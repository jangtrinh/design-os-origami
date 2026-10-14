"""Release gate includes both examples and real tests; failures fail closed."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('release_gate', ROOT / 'scripts/check_host_bundle_release.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class HostBundleRelease(unittest.TestCase):
    def test_both_examples_and_unittest_are_required(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'proof'
            def completed(command, **kwargs):
                return subprocess.CompletedProcess(command, 0, 'ok\n', '')
            with patch.object(sys, 'argv', ['check', '--browser-cache', temp, '--evidence-dir', str(target)]), patch.object(gate.subprocess, 'run', side_effect=completed):
                self.assertEqual(gate.main(), 0)
            receipt = json.loads((target / 'release-checks.json').read_text())
            labels = {r['label'] for r in receipt['checks']}
            self.assertIn('tests', labels)
            for slug in ('tuck-box-printer', 'hex-petal-presentation'):
                for stage in ('build', 'validate', 'look'):
                    self.assertIn(slug + '-' + stage, labels)

    def test_failed_example_look_blocks_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'proof'
            def fail_look(command, **kwargs):
                failed = any(str(arg).endswith('look.py') for arg in command)
                return subprocess.CompletedProcess(command, int(failed), '', 'look: unavailable\n' if failed else '')
            with patch.object(sys, 'argv', ['check', '--browser-cache', temp, '--evidence-dir', str(target)]), patch.object(gate.subprocess, 'run', side_effect=fail_look):
                self.assertEqual(gate.main(), 1)
            self.assertFalse(json.loads((target / 'release-checks.json').read_text())['ok'])
