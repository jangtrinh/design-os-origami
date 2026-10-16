"""Offline look rejects damaged provenance before running a cached browser."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

from origami_cad.look_harness import LookError, prepare_job, run_look
from origami_cad.product_registry import product_blanks
from origami_cad.preview_model import build_preview_model
from origami_cad.dieline_export import export_svg
from origami_cad.viewer_html import generate_viewer_html

ROOT = Path(__file__).resolve().parents[1]


class SkillLookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='origami look ü ')
        self.addCleanup(self.tmp.cleanup)
        self.output = Path(self.tmp.name) / 'run'
        self.output.mkdir()
        self.cache = Path(self.tmp.name) / 'cache'
        self.cache.mkdir()
        self.sheet = self.output / 'evidence' / 'look-sheet.png'
        self.create_run()

    def create_run(self, product='tuck-box'):
        parameters = {'width': 50.0} if product == 'diamond-box' else {}
        try:
            from origami_cad.artifact_workflow import build, normalize_spec, blanks_for_spec
        except ModuleNotFoundError:
            pass
        else:
            spec = normalize_spec(dict(schema_version=1, type=product, parameters=parameters))
            shutil.rmtree(self.output)
            self.manifest = build(ROOT, spec, self.output)
            self.cp = blanks_for_spec(spec)[0]
            return
        self.cp = product_blanks(product, **parameters)[0]
        export_svg(self.cp, str(self.output / (self.cp.name + '.svg')))
        generate_viewer_html(self.cp, str(self.output / (self.cp.name + '_viewer.html')))
        model = build_preview_model(self.cp)
        self.manifest = dict(schema_version=1, spec=dict(schema_version=1, type=product, parameters=parameters,
                             profiles=['presentation'], preview_requirement='allow-unavailable'),
                             source_hash='a' * 64, contract_hash='b' * 64,
                             files={}, profiles=['presentation'],
                             blanks=[dict(name=self.cp.name, preview=dict(
                                 available=model['available'], status=model['status'],
                                 continuity=model.get('continuity')))])
        self.refresh()

    def refresh(self):
        self.manifest['files'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in self.output.iterdir() if p.suffix in {'.svg', '.html', '.dxf', '.pdf'}}
        (self.output / 'artifact.json').write_text(json.dumps(self.manifest))

    def job(self):
        return prepare_job(ROOT, self.output, self.sheet)

    def browser_capture(self, cache=None):
        job = self.job()
        job['browser_cache'] = str(cache or os.environ['ORIGAMI_BROWSER_CACHE'])
        return subprocess.run([shutil.which('node'), str(ROOT / 'scripts/capture-viewer.cjs')],
            input=json.dumps(job), capture_output=True, text=True, timeout=90)

    def assert_error(self, text, callback=None):
        with self.assertRaisesRegex(LookError, text) as raised:
            (callback or self.job)()
        self.assertEqual(raised.exception.code, 1)

    @unittest.skipUnless(os.environ.get('ORIGAMI_BROWSER_CACHE'), 'explicit browser cache required')
    def test_inflight_cancellation_removes_unpublished_evidence(self):
        event = threading.Event()
        timer = threading.Timer(0.8, event.set)
        timer.start()
        try:
            with self.assertRaisesRegex(LookError, 'cancelled'):
                run_look(ROOT, self.output, os.environ['ORIGAMI_BROWSER_CACHE'], self.sheet, cancel=event)
            self.assertFalse(self.sheet.exists())
            self.assertFalse(self.sheet.with_suffix('.json').exists())
        finally:
            timer.cancel()

    def test_real_source_job_is_portable(self):
        job = self.job()
        self.assertEqual(job['blanks'][0]['name'], self.cp.name)
        self.assertEqual(job['blanks'][0]['model'], build_preview_model(self.cp))

    def test_corrupt_manifest_is_machine_failure(self):
        (self.output / 'artifact.json').write_text('{')
        self.assert_error('artifact')

    def test_changed_viewer_hash_is_rejected(self):
        (self.output / (self.cp.name + '_viewer.html')).write_text('broken')
        self.assert_error('hash')

    def test_missing_svg_is_rejected(self):
        (self.output / (self.cp.name + '.svg')).unlink()
        self.assert_error('file')

    def test_traversal_is_rejected(self):
        self.manifest['files']['../outside.html'] = 'a' * 64
        (self.output / 'artifact.json').write_text(json.dumps(self.manifest))
        self.assert_error('path')

    def test_symlink_is_rejected(self):
        svg = self.output / (self.cp.name + '.svg')
        destination = self.output.parent / 'outside.svg'
        svg.rename(destination)
        svg.symlink_to(destination)
        self.assert_error('path')

    def test_tampered_model_even_with_updated_file_hash_is_rejected(self):
        viewer = self.output / (self.cp.name + '_viewer.html')
        viewer.write_text(viewer.read_text().replace('"tolerance_mm": 0.5', '"tolerance_mm": 5'))
        self.refresh()
        self.assert_error('L7')

    def test_forged_preview_receipt_is_rejected(self):
        self.manifest['blanks'][0]['preview']['available'] = False
        self.refresh()
        self.assert_error('L7')

    def test_available_requirement_rejects_unavailable(self):
        self.create_run('miura-ori')
        self.manifest['spec']['preview_requirement'] = 'available'
        self.refresh()
        self.assert_error('available')

    def test_unavailable_is_honest_source_state(self):
        self.create_run('miura-ori')
        self.assertFalse(self.job()['blanks'][0]['model']['available'])

    def test_existing_sheet_is_never_overwritten(self):
        self.sheet.parent.mkdir()
        self.sheet.write_bytes(b'owner evidence')
        self.assert_error('exists')
        self.assertEqual(self.sheet.read_bytes(), b'owner evidence')

    def test_missing_cache_has_dependency_exit_two(self):
        with self.assertRaises(LookError) as raised:
            run_look(ROOT, self.output, self.cache, self.sheet)
        self.assertEqual(raised.exception.code, 2)
        self.assertFalse(self.sheet.exists())

    def test_cli_missing_cache_exit_two(self):
        result = subprocess.run([sys.executable, '-B',
            str(ROOT / 'skills/es-origami-cad/look.py'), '--repo-root', str(ROOT),
            '--output-dir', str(self.output), '--browser-cache', str(self.cache),
            '--sheet', str(self.sheet)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('NOT RUN', result.stderr)

    def test_corrupt_cached_three_has_dependency_exit_two(self):
        package = self.cache / 'node_modules' / 'playwright'
        package.mkdir(parents=True)
        (self.cache / 'three-r128.min.js').write_bytes(b'corrupted cached library')
        result = self.browser_capture(self.cache)
        self.assertEqual(result.returncode, 2)
        self.assertIn('checksum', result.stderr)
        self.assertFalse(self.sheet.exists())

    def test_missing_cached_three_has_dependency_exit_two(self):
        (self.cache / 'node_modules' / 'playwright').mkdir(parents=True)
        result = self.browser_capture(self.cache)
        self.assertEqual(result.returncode, 2)
        self.assertIn('Three', result.stderr)
        self.assertFalse(self.sheet.exists())

    @unittest.skipUnless(os.environ.get('ORIGAMI_BROWSER_CACHE'), 'explicit cached browser not supplied')
    def test_external_request_is_rejected_by_actual_browser(self):
        viewer = self.output / (self.cp.name + '_viewer.html')
        viewer.write_text(viewer.read_text().replace('</body>',
            '<img src="https://example.invalid/forbidden.png"></body>'))
        self.refresh()
        result = self.browser_capture()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('L8', result.stderr)
        self.assertFalse(self.sheet.exists())

    @unittest.skipUnless(os.environ.get('ORIGAMI_BROWSER_CACHE'), 'explicit cached browser not supplied')
    def test_disabled_slider_is_rejected_by_actual_browser(self):
        viewer = self.output / (self.cp.name + '_viewer.html')
        viewer.write_text(viewer.read_text().replace('</body>',
            '<script>window.addEventListener("load",()=>document.querySelector("#fold-slider").setAttribute("aria-disabled","true"))</script></body>'))
        self.refresh()
        result = self.browser_capture()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('L4', result.stderr)
        self.assertFalse(self.sheet.exists())

    @unittest.skipUnless(os.environ.get('ORIGAMI_BROWSER_CACHE'), 'explicit cached browser not supplied')
    def test_actual_browser_preserves_unavailable(self):
        self.create_run('miura-ori')
        captured = self.browser_capture()
        self.assertEqual(captured.returncode, 0, captured.stderr)
        result = json.loads(captured.stdout)
        self.assertTrue(result['ok'])
        self.assertEqual(result['blanks'][0]['checks']['L9'], 'PASS')

    @unittest.skipUnless(os.environ.get('ORIGAMI_BROWSER_CACHE'), 'explicit cached browser not supplied')
    def test_real_offline_browser(self):
        captured = self.browser_capture()
        self.assertEqual(captured.returncode, 0, captured.stderr)
        result = json.loads(captured.stdout)
        self.assertTrue(result['ok'])
        self.assertEqual(self.sheet.read_bytes()[:8], b'\x89PNG\r\n\x1a\n')
        self.assertEqual([f['progress'] for f in result['blanks'][0]['frames']], [25, 50, 75, 100])


if __name__ == '__main__':
    unittest.main()
