"""Strict declarative request -> complete, source-bound, atomically published run."""
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import tempfile

from origami_cad.cli import create_parser, generate_blanks
from origami_cad.cli_contract import SKILL, contract_current, digest, model_parameters, source_hash
from origami_cad.dieline_export import export_svg, export_dxf
from origami_cad.viewer_html import generate_viewer_html
from origami_cad.printer_profile_export import export_printer_pdf, export_printer_dxf, resolve_spots
from origami_cad.preview_model import build_preview_model

MAX_INPUT = 65536


def strict_json(data):
    # Bound nesting before the platform JSON parser: Python releases have
    # different recursion limits, independently of the transport byte limit.
    text = data.decode('utf-8') if isinstance(data, bytes) else data
    depth, quoted, escaped = 0, False, False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '[{':
            depth += 1
            if depth > 64:
                raise ValueError('JSON nesting exceeds64 levels')
        elif char in ']}':
            depth -= 1
    def pairs(values):
        out = {}
        for key, value in values:
            if key in out:
                raise ValueError('Duplicate JSON key')
            out[key] = value
        return out
    def invalid(value):
        raise ValueError('Non-finite JSON number')
    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError('Non-finite JSON number')
        return number
    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid, parse_float=finite_float)
    except RecursionError as error:
        raise ValueError('JSON parser nesting limit exceeded') from error


def read_spec(path):
    data = Path(path).read_bytes()
    if len(data) > MAX_INPUT or len(data.splitlines()) > 200:
        raise ValueError('Input exceeds 64 KiB or 200 lines')
    return normalize_spec(strict_json(data))


def keys(value, allowed, label):
    if not isinstance(value, dict) or set(value) - set(allowed):
        raise ValueError('Unknown or invalid ' + label)


def number(value, label, zero=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0 or (value == 0 and not zero):
        raise ValueError(label + ' must be finite and ' + ('non-negative' if zero else 'positive'))
    return float(value)


def normalize_spec(spec):
    keys(spec, ['schema_version', 'type', 'parameters', 'profiles', 'printer', 'preview_requirement'], 'request keys')
    if spec.get('schema_version') != 1 or isinstance(spec.get('schema_version'), bool):
        raise ValueError('schema_version must be 1')
    models = model_parameters()
    slug = spec.get('type')
    if not isinstance(slug, str) or slug not in models:
        raise ValueError('Unsupported model type')
    parameters = spec.get('parameters', {})
    keys(parameters, models[slug], 'model parameters (ignored parameters forbidden)')
    parameters = models[slug] | {k: number(v, k) for k, v in parameters.items()}
    profiles = spec.get('profiles', ['presentation'])
    if not isinstance(profiles, list) or not profiles or len(profiles) != len(set(str(p) for p in profiles)) or any(p not in ['presentation', 'printer'] for p in profiles):
        raise ValueError('Unsupported profile combination')
    if slug in ['miura-ori', 'deer-base'] and 'printer' in profiles:
        raise ValueError('Printer profile requires a closed carton blank; research patterns are presentation-only')
    preview = spec.get('preview_requirement', 'allow-unavailable')
    if preview not in ['available', 'allow-unavailable'] or (preview == 'available' and 'presentation' not in profiles):
        raise ValueError('Invalid preview_requirement/profile combination')
    printer = spec.get('printer', {})
    keys(printer, ['bleed_mm', 'spots'], 'printer keys')
    if printer and 'printer' not in profiles:
        raise ValueError('Printer settings require printer profile')
    resolved = {}
    if 'printer' in profiles:
        spots = printer.get('spots', {})
        keys(spots, resolve_spots(), 'spot keys')
        resolved = {'bleed_mm': number(printer.get('bleed_mm', 3), 'bleed_mm', zero=True), 'spots': resolve_spots(spots)}
    out = dict(schema_version=1, type=slug, parameters=parameters,
               profiles=[p for p in ['presentation', 'printer'] if p in profiles],
               preview_requirement=preview, printer=resolved)
    if len(json.dumps(out, allow_nan=False).encode()) > MAX_INPUT:
        raise ValueError('Input exceeds 64 KiB')
    return out


def blanks_for_spec(spec):
    args = create_parser().parse_args(['generate', '--type', spec['type']])
    for key, value in spec['parameters'].items():
        setattr(args, key, value)
    return generate_blanks(args)


def expected_names(spec, blanks):
    out = []
    for cp in blanks:
        if 'presentation' in spec['profiles']:
            out += [cp.name + '.svg', cp.name + '.dxf', cp.name + '_viewer.html']
        if 'printer' in spec['profiles']:
            out += [cp.name + '_printer.pdf', cp.name + '_printer.dxf']
    return out


def cancelled(event):
    if event is not None and event.is_set():
        raise ValueError('Operation cancelled; retry requires a new run ID')


def build(repo, spec, output, cancel=None):
    repo, output = Path(repo).resolve(), Path(output).absolute()
    spec = normalize_spec(spec)
    if not contract_current(repo):
        raise ValueError('contract: regenerate contract.md from the current product source')
    if output.exists() or output.is_symlink():
        raise ValueError('Output destination must be new')
    blanks = blanks_for_spec(spec)
    from origami_cad.artifact_topology import violations
    for cp in blanks:
        if spec['type'] not in ['deer-base', 'miura-ori'] and any(violations(cp).values()):
            raise ValueError('topology: source blank fails existing product topology checks')
    models = [build_preview_model(cp) for cp in blanks]
    if spec['preview_requirement'] == 'available' and any(not m['available'] for m in models):
        raise ValueError('preview-status: requested available preview failed source qualification')
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.' + output.name + '-', dir=output.parent))
    try:
        for cp in blanks:
            cancelled(cancel)
            if 'presentation' in spec['profiles']:
                export_svg(cp, stage / (cp.name + '.svg'))
                export_dxf(cp, stage / (cp.name + '.dxf'))
                generate_viewer_html(cp, stage / (cp.name + '_viewer.html'))
            if 'printer' in spec['profiles']:
                config = spec['printer']
                export_printer_pdf(cp, stage / (cp.name + '_printer.pdf'), config['bleed_mm'], config['spots'])
                export_printer_dxf(cp, stage / (cp.name + '_printer.dxf'), config['bleed_mm'], config['spots'])
        receipt = dict(schema_version=1, spec=spec, source_hash=source_hash(repo),
                       contract_hash=digest((repo / SKILL / 'contract.md').read_bytes()),
                       files={name: digest((stage / name).read_bytes()) for name in expected_names(spec, blanks)},
                       profiles=spec['profiles'],
                       blanks=[dict(name=cp.name, bounding_box=list(cp.bounding_box()),
                                    thickness_mm=cp.thickness_mm, preview=model) for cp, model in zip(blanks, models)])
        (stage / 'artifact.json').write_text(json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False) + '\n')
        cancelled(cancel)
        if not contract_current(repo):
            raise ValueError('contract: runtime source changed during build; restart and regenerate contract')
        # Exclusive no-clobber claim; the complete receipt is published last.
        # Readers reject a run without that commit marker during file publication.
        output.mkdir()
        try:
            for name in expected_names(spec, blanks):
                os.replace(stage / name, output / name)
            os.replace(stage / 'artifact.json', output / 'artifact.json')
        except BaseException:
            shutil.rmtree(output)
            raise
        return receipt
    finally:
        shutil.rmtree(stage)
