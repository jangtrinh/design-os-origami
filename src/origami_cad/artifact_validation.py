"""Offline named checks: contract, input, files, receipt, layers, folds, topology,
DXF, printer spots/exchange, preview, catalogue and hashes. No taste verdicts.
"""
import json
from pathlib import Path
import re
import tempfile
import xml.etree.ElementTree as ET

from origami_cad.artifact_workflow import normalize_spec, strict_json, blanks_for_spec, expected_names
from origami_cad.cli_contract import SKILL, contract_current, digest, source_hash
from origami_cad.dieline_export import export_svg, export_dxf
from origami_cad.printer_profile_export import export_printer_pdf, export_printer_dxf
from origami_cad.preview_model import build_preview_model
from origami_cad.preview_recording import preview_records_match, continuity_records_match
from origami_cad.artifact_topology import violations

DIAGNOSTICS = {
    'contract': 'regenerate contract.md from the current product source',
    'input': 'use a bounded valid request with applicable finite dimensions',
    'artifact-files': 'restore the complete manifest-listed regular files inside the run',
    'artifact-receipt': 'restore a complete source-bound artifact.json receipt',
    'svg-layers': 'restore CUT and CREASE separation and all four layer colors',
    'fold-metadata': 'restore source mountain/valley data-fold attributes',
    'topology': 'restore the valid source contour, slit attachments and fold segments',
    'dxf-layers': 'restore the source presentation DXF layers and coordinates',
    'printer-spots': 'use five distinct valid spot names',
    'printer-exchange': 'regenerate source-scaled spot PDF and mm/y-up DXF with recorded bleed',
    'preview-status': 'preserve the source-derived unavailable state and qualified model',
    'catalog-consistency': 'regenerate catalogue artifacts using their recorded inputs',
    'artifact-hashes': 'restore artifact bytes matching the receipt hashes',
}
MAX_ARTIFACT = 16 * 1024 * 1024


def safe_file(root, name):
    """No symlinks, traversal or absolute manifest paths, including ancestors."""
    path = Path(name)
    if not isinstance(name, str) or path.is_absolute() or path.as_posix() != name or '..' in path.parts or not path.parts:
        raise ValueError('Unsafe artifact path')
    target = root / path
    if root.is_symlink() or any(p.is_symlink() for p in [target, *target.parents] if p == root or root in p.parents):
        raise ValueError('Linked artifact path')
    if not target.is_file() or target.stat().st_size > MAX_ARTIFACT:
        raise ValueError('Missing or oversized artifact')
    return target


def svg_structure(text):
    tree = ET.fromstring(text)
    groups = {g.get('id'): g for g in tree.iter() if g.tag.rsplit('}', 1)[-1] == 'g'}
    return tree, groups


def validate(repo, output):
    repo, root = Path(repo).resolve(), Path(output).absolute()
    failures = set()
    def result():
        return [key + ': ' + value for key, value in DIAGNOSTICS.items() if key in failures]
    if not contract_current(repo):
        failures.add('contract')
        return result()
    try:
        receipt = strict_json(safe_file(root, 'artifact.json').read_bytes())
        required = {'schema_version', 'spec', 'source_hash', 'contract_hash', 'files', 'profiles', 'blanks'}
        if not isinstance(receipt, dict) or set(receipt) != required or receipt['schema_version'] != 1:
            raise ValueError('Incomplete receipt')
    except (OSError, ValueError, TypeError):
        failures.add('artifact-receipt')
        return result()
    try:
        spec = normalize_spec(receipt['spec'])
        if spec != receipt['spec']:
            raise ValueError('Request is not normalized')
    except (ValueError, TypeError, OverflowError):
        # Spot failure is distinct from generic dimensions/unknown parameters.
        try:
            from origami_cad.printer_profile_export import resolve_spots
            resolve_spots(receipt['spec'].get('printer', {}).get('spots', {}))
        except (ValueError, TypeError, AttributeError):
            failures.add('printer-spots')
        if not failures:
            failures.add('input')
        return result()
    try:
        blanks = blanks_for_spec(spec)
    except (ValueError, TypeError, OverflowError, ZeroDivisionError):
        failures.add('input')
        return result()
    expected = expected_names(spec, blanks)
    if (not isinstance(receipt['files'], dict) or set(receipt['files']) != set(expected) or
            any(not isinstance(v, str) or not re.fullmatch('[0-9a-f]{64}', v) for v in receipt['files'].values())):
        failures.add('artifact-files')
        return result()
    files = {}
    for name in expected:
        try:
            files[name] = safe_file(root, name).read_bytes()
        except (ValueError, OSError):
            failures.add('artifact-files')
    if failures:
        return result()
    if (receipt['source_hash'] != source_hash(repo) or
            receipt['contract_hash'] != digest((repo / SKILL / 'contract.md').read_bytes()) or
            receipt['profiles'] != spec['profiles']):
        failures.add('artifact-receipt')
        return result()
    models = [build_preview_model(cp) for cp in blanks]
    recorded = receipt['blanks']
    if (not isinstance(recorded, list) or len(recorded) != len(blanks) or
            any(not isinstance(row, dict) or set(row) != {'name', 'bounding_box', 'thickness_mm', 'preview'} or
                row['name'] != cp.name or row['bounding_box'] != list(cp.bounding_box()) or
                row['thickness_mm'] != cp.thickness_mm for row, cp in zip(recorded, blanks))):
        failures.add('artifact-receipt')
        return result()
    if any(not preview_records_match(row['preview'], model, cp)
           for row, model, cp in zip(recorded, models, blanks)):
        failures.add('preview-status')
    if spec['preview_requirement'] == 'available' and any(not m['available'] for m in models):
        failures.add('preview-status')
    with tempfile.TemporaryDirectory() as tmp:
        temp = Path(tmp)
        for cp, model in zip(blanks, models):
            if spec['type'] not in ['miura-ori', 'deer-base'] and any(violations(cp).values()):
                failures.add('topology')
            if 'presentation' in spec['profiles']:
                expected_svg = export_svg(cp, temp / 'expected.svg')
                try:
                    svg_failures_before = set(failures)
                    tree, groups = svg_structure(files[cp.name + '.svg'])
                    reference, reference_groups = svg_structure(expected_svg)
                    layer_ok = True
                    for name in ['CUT', 'CREASE', 'PERFORATE', 'GLUE']:
                        if name not in groups or groups[name].attrib != reference_groups[name].attrib:
                            layer_ok = False
                    styles = lambda t: [n.text for n in t.iter() if n.tag.endswith('style')]
                    if styles(tree) != styles(reference):
                        layer_ok = False
                    if not layer_ok:
                        failures.add('svg-layers')
                    else:
                        for name in ['CUT', 'CREASE', 'PERFORATE', 'GLUE']:
                            actual_lines, source_lines = list(groups[name]), list(reference_groups[name])
                            if len(actual_lines) != len(source_lines):
                                failures.add('topology')
                                continue
                            for actual, source in zip(actual_lines, source_lines):
                                if actual.get('data-fold') != source.get('data-fold'):
                                    failures.add('fold-metadata')
                                attrs = lambda n: {k: v for k, v in n.attrib.items() if k != 'data-fold'}
                                if actual.tag != source.tag or attrs(actual) != attrs(source):
                                    failures.add('topology')
                        if tree.attrib != reference.attrib:
                            failures.add('topology')
                    if failures == svg_failures_before and ET.tostring(tree) != ET.tostring(reference):
                        failures.add('topology')  # Includes unknown sibling geometry and duplicate groups.
                except (ET.ParseError, ValueError):
                    failures.add('svg-layers')
                if files[cp.name + '.dxf'] != export_dxf(cp, temp / 'expected.dxf').encode():
                    failures.add('dxf-layers')
                try:
                    html = files[cp.name + '_viewer.html'].decode()
                    actual = strict_json(re.search(r'<script[^>]*id="fold-model"[^>]*>(.*?)</script>', html, re.S).group(1))
                    if not preview_records_match(actual, model, cp):
                        failures.add('preview-status')
                    # Compare every renderer byte; only the already checked JSON
                    # diagnostics may differ between platform math libraries.
                    from origami_cad.viewer_html import generate_viewer_html
                    generate_viewer_html(cp, temp / 'expected.html')
                    reference_html = (temp / 'expected.html').read_text()
                    pattern = r'(<script[^>]*id="fold-model"[^>]*>)(.*?)(</script>)'
                    reference_payload = re.search(pattern, reference_html, re.S).group(2)
                    normalized_html = re.sub(pattern, lambda m: m.group(1) + reference_payload + m.group(3), html, flags=re.S)
                    if normalized_html != reference_html:
                        failures.add('preview-status')
                except (AttributeError, ValueError, UnicodeError):
                    failures.add('preview-status')
            if 'printer' in spec['profiles']:
                settings = spec['printer']
                try:
                    pdf = export_printer_pdf(cp, temp / 'expected.pdf', settings['bleed_mm'], settings['spots'])
                    dxf = export_printer_dxf(cp, temp / 'printer.dxf', settings['bleed_mm'], settings['spots']).encode()
                    if files[cp.name + '_printer.pdf'] != pdf or files[cp.name + '_printer.dxf'] != dxf:
                        failures.add('printer-exchange')
                except ValueError:
                    failures.add('printer-exchange')
    # Semantic failures take precedence over the incidental stale artifact hash.
    if not failures and any(digest(data) != receipt['files'][name] for name, data in files.items()):
        failures.add('artifact-hashes')
    return result()


def validate_catalog(repo, catalog):
    """Regenerate recorded catalogue inputs, never unrelated custom-run defaults."""
    try:
        for entry in strict_json(Path(catalog).read_bytes()):
            if 'run' in entry:
                failures = validate(repo, Path(catalog).parent / entry['run'])
            else:
                spec = normalize_spec(entry['inputs'])
                candidates = blanks_for_spec(spec)
                cp = next(c for c in candidates if c.name == entry['source_name'])
                model = build_preview_model(cp)
                failures = (entry['preview_available'] != model['available'] or
                            entry['caliper_mm'] != cp.thickness_mm or not
                            continuity_records_match(entry['continuity'], model.get('continuity'), model, cp))
                with tempfile.TemporaryDirectory() as tmp:
                    folder = Path(tmp)
                    parent = Path(catalog).parent.parent
                    actual = {k: safe_file(parent, name).read_bytes() for k, name in entry['files'].items()}
                    expected = {'svg': export_svg(cp, folder / 'blank.svg').encode(),
                                'pdf': export_printer_pdf(cp, folder / 'blank.pdf', spec['printer']['bleed_mm'], spec['printer']['spots']),
                                'dxf': export_printer_dxf(cp, folder / 'blank.dxf', spec['printer']['bleed_mm'], spec['printer']['spots']).encode()}
                    failures = failures or actual != expected
            if failures:
                return ['catalog-consistency: ' + DIAGNOSTICS['catalog-consistency']]
        return []
    except (OSError, ValueError, TypeError, KeyError, StopIteration):
        return ['catalog-consistency: ' + DIAGNOSTICS['catalog-consistency']]
