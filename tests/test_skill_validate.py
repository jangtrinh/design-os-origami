"""Each primary defect produces exactly one stable actionable diagnostic."""
import json
import subprocess
import sys

from origami_cad.artifact_validation import validate, validate_catalog, DIAGNOSTICS
from origami_cad.cli_contract import SKILL
from skill_fixture import SkillFixture, ROOT


class SkillValidate(SkillFixture):
    def setUp(self):
        super().setUp()
        self.build_tuck()

    def reject(self, check):
        diagnostic = check + ': ' + DIAGNOSTICS[check]
        self.assertEqual(validate(self.repo, self.output), [diagnostic])
        result = subprocess.run([sys.executable, '-B', str(ROOT / SKILL / 'validate.py'),
                                 '--repo-root', str(self.repo), '--output-dir', str(self.output)],
                                capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (1, diagnostic + '\n', ''))

    def mutate_receipt(self, function):
        path = self.output / 'artifact.json'
        data = json.loads(path.read_text())
        function(data)
        path.write_text(json.dumps(data))

    def mutate_file(self, suffix, old, new):
        path = self.output / (self.name + suffix)
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1))

    def test_good_accepts_and_cli_prints_ok(self):
        self.assertEqual(validate(self.repo, self.output), [])
        result = subprocess.run([sys.executable, '-B', str(ROOT / SKILL / 'validate.py'), '--repo-root', str(self.repo), '--output-dir', str(self.output)], capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout), (0, 'ok\n'), result.stderr)

    def test_contract(self):
        path = self.repo / SKILL / 'contract.md'
        path.write_bytes(path.read_bytes() + b'edited')
        self.reject('contract')

    def test_input(self):
        self.mutate_receipt(lambda d: d['spec']['parameters'].update(width=0))
        self.reject('input')

    def test_artifact_files(self):
        (self.output / (self.name + '.svg')).unlink()
        self.reject('artifact-files')

    def test_artifact_receipt(self):
        self.mutate_receipt(lambda d: d.update(source_hash='0' * 64))
        self.reject('artifact-receipt')

    def test_svg_layers(self):
        self.mutate_file('.svg', 'id="CUT"', 'id="CREASE_WRONG"')
        self.reject('svg-layers')

    def test_fold_metadata(self):
        # A real mountain/valley source is required for this check.
        from origami_cad.artifact_workflow import build
        target = self.base / 'gable'
        receipt = build(self.repo, {'schema_version': 1, 'type': 'gable-box'}, target)
        self.output = target
        self.name = receipt['blanks'][0]['name']
        self.mutate_file('.svg', 'data-fold="valley"', 'data-fold="mountain"')
        self.reject('fold-metadata')

    def test_topology(self):
        self.mutate_file('.svg', 'x1="15.00"', 'x1="25.00"')
        self.reject('topology')

    def test_rehashed_extra_svg_geometry_cannot_bypass_topology(self):
        from origami_cad.cli_contract import digest
        path = self.output / (self.name + '.svg')
        path.write_text(path.read_text().replace('</svg>', '<path class="cut" d="M 0 0 L 10 0"/></svg>'))
        self.mutate_receipt(lambda d: d['files'].update({path.name: digest(path.read_bytes())}))
        self.reject('topology')

    def test_rehashed_duplicate_layer_cannot_hide_extra_geometry(self):
        from origami_cad.cli_contract import digest
        path = self.output / (self.name + '.svg')
        path.write_text(path.read_text().replace('<g id="DIELINE_LAYER">', '<g id="CUT"><path d="M0 0L10 0"/></g><g id="DIELINE_LAYER">'))
        self.mutate_receipt(lambda d: d['files'].update({path.name: digest(path.read_bytes())}))
        self.reject('topology')

    def test_dxf_layers(self):
        self.mutate_file('.dxf', '\nCUT\n', '\nBadKnife\n')
        self.reject('dxf-layers')

    def test_printer_spots(self):
        self.mutate_receipt(lambda d: d['spec']['printer']['spots'].update(cut='CreaseLine'))
        self.reject('printer-spots')

    def test_printer_exchange(self):
        path = self.output / (self.name + '_printer.pdf')
        path.write_bytes(path.read_bytes().replace(b'1 w', b'2 w', 1))
        self.reject('printer-exchange')

    def test_preview_status(self):
        self.mutate_file('_viewer.html', '"available": true', '"available": false')
        self.reject('preview-status')

    def test_recorded_receipt_and_viewer_diagnostic_roundoff_passes(self):
        import re
        from origami_cad.cli_contract import digest
        self.mutate_receipt(lambda d: d['blanks'][0]['preview']['continuity'].update(
            max_gap_mm=d['blanks'][0]['preview']['continuity']['max_gap_mm'] * (1 + 1e-9)))
        path = self.output / (self.name + '_viewer.html')
        text = path.read_text()
        pattern = r'(<script id="fold-model" type="application/json">)(.*?)(</script>)'
        model = json.loads(re.search(pattern, text, re.S).group(2))
        model['continuity']['max_gap_mm'] *= 1 + 1e-9
        path.write_text(re.sub(pattern, lambda m: m.group(1) + json.dumps(model) + m.group(3), text, flags=re.S))
        self.mutate_receipt(lambda d: d['files'].update({path.name: digest(path.read_bytes())}))
        self.assertEqual(validate(self.repo, self.output), [])
        result = subprocess.run([sys.executable, '-B', str(ROOT / SKILL / 'validate.py'),
                                 '--repo-root', str(self.repo), '--output-dir', str(self.output)],
                                capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, 'ok\n', ''))
        from origami_cad.look_harness import prepare_job
        job = prepare_job(self.repo, self.output, self.base / 'look.png')
        self.assertEqual(job['blanks'][0]['model'], model)
        model['faces'][0]['vertices'][0][0] += 0.01
        path.write_text(re.sub(pattern, lambda m: m.group(1) + json.dumps(model) + m.group(3), text, flags=re.S))
        self.mutate_receipt(lambda d: d['files'].update({path.name: digest(path.read_bytes())}))
        self.reject('preview-status')

    def test_artifact_hashes(self):
        self.mutate_receipt(lambda d: d['files'].update({self.name + '.svg': '0' * 64}))
        self.reject('artifact-hashes')

    def test_catalog_consistency(self):
        catalog = self.base / 'catalog.json'
        catalog.write_text(json.dumps([{'run': 'run'}]))
        self.assertEqual(validate_catalog(self.repo, catalog), [])
        self.mutate_file('.svg', 'id="CUT"', 'id="BAD"')
        self.assertEqual(validate_catalog(self.repo, catalog), ['catalog-consistency: ' + DIAGNOSTICS['catalog-consistency']])
        from origami_cad.artifact_workflow import build
        from skill_fixture import TUCK
        good = self.base / 'good'
        build(self.repo, TUCK, good)
        result = subprocess.run([sys.executable, '-B', str(ROOT / SKILL / 'validate.py'),
                                 '--repo-root', str(self.repo), '--output-dir', str(good),
                                 '--catalog', str(catalog)], capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout, result.stderr),
                         (1, 'catalog-consistency: ' + DIAGNOSTICS['catalog-consistency'] + '\n', ''))

    def test_public_catalog_recorded_inputs_pass_and_changed_asset_fails(self):
        import shutil
        rows = json.loads((ROOT / 'docs/assets/catalog.json').read_text())[:1]
        docs = self.base / 'docs'
        (docs / 'assets').mkdir(parents=True)
        for filename in rows[0]['files'].values():
            target = docs / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / 'docs' / filename, target)
        catalog = docs / 'assets/catalog.json'
        catalog.write_text(json.dumps(rows))
        self.assertEqual(validate_catalog(self.repo, catalog), [])
        target = docs / rows[0]['files']['svg']
        target.write_text(target.read_text().replace('id="CUT"', 'id="BAD"'))
        self.assertEqual(validate_catalog(self.repo, catalog), ['catalog-consistency: ' + DIAGNOSTICS['catalog-consistency']])

    def test_public_catalog_diagnostic_roundoff_passes_availability_change_fails(self):
        import shutil
        rows = json.loads((ROOT / 'docs/assets/catalog.json').read_text())[:1]
        docs = self.base / 'docs'
        (docs / 'assets').mkdir(parents=True)
        for filename in rows[0]['files'].values():
            target = docs / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / 'docs' / filename, target)
        catalog = docs / 'assets/catalog.json'
        rows[0]['continuity']['max_gap_mm'] *= 1 + 1e-9
        catalog.write_text(json.dumps(rows))
        self.assertEqual(validate_catalog(self.repo, catalog), [])
        rows[0]['preview_available'] = not rows[0]['preview_available']
        catalog.write_text(json.dumps(rows))
        self.assertEqual(validate_catalog(self.repo, catalog),
                         ['catalog-consistency: ' + DIAGNOSTICS['catalog-consistency']])

    def test_manifest_escape_symlink_and_missing_prerequisite_suppress_cascades(self):
        path = self.output / (self.name + '.svg')
        outside = self.base / 'outside.svg'
        path.rename(outside)
        path.symlink_to(outside)
        self.reject('artifact-files')
        (self.output / 'artifact.json').unlink()
        self.reject('artifact-receipt')

    def test_cannot_run_exit2_and_help(self):
        command = [sys.executable, '-B', str(ROOT / SKILL / 'validate.py')]
        self.assertEqual(subprocess.run(command + ['--help'], capture_output=True).returncode, 0)
        result = subprocess.run(command + ['--repo-root', str(self.base / 'missing'), '--output-dir', str(self.output)], capture_output=True)
        # Imports are resolved only from selected checkout; current working directory is not a runtime fallback.
        # The running process PYTHONPATH may be inherited by caller, so explicitly clear it.
        import os
        result = subprocess.run(command + ['--repo-root', str(self.base / 'missing'), '--output-dir', str(self.output)], capture_output=True, env=os.environ | {'PYTHONPATH': ''})
        self.assertEqual(result.returncode, 2)
