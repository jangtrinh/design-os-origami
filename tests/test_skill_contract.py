"""Contract drift cannot be hidden by recalculating an edited header."""
from origami_cad.cli_contract import SKILL, contract_current, render_contract, model_parameters
from skill_fixture import SkillFixture, ROOT
import shutil
import subprocess
import sys


class SkillContract(SkillFixture):
    def test_checked_in_contract_is_current(self):
        self.assertTrue(contract_current(ROOT))

    def test_actual_script_staleness_and_tamper_controls(self):
        scripts = self.repo / 'scripts'
        scripts.mkdir()
        script = scripts / 'skill_contract.py'
        shutil.copy2(ROOT / 'scripts/skill_contract.py', script)
        command = [sys.executable, '-B', str(script), '--check']
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        contract = self.repo / SKILL / 'contract.md'
        original = contract.read_bytes()
        contract.write_bytes(original + b'edited\n')
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
        contract.write_bytes(original)
        source = self.repo / 'src/origami_cad/packaging.py'
        source.write_bytes(source.read_bytes() + b'\n# source drift\n')
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)

    def test_generated_bytes_are_deterministic_and_source_bound(self):
        self.assertEqual(render_contract(self.repo), render_contract(self.repo))
        before = render_contract(self.repo)
        source = self.repo / 'src/origami_cad/packaging.py'
        source.write_bytes(source.read_bytes() + b'\n# drift\n')
        self.assertNotEqual(render_contract(self.repo), before)
        self.assertFalse(contract_current(self.repo))

    def test_tampered_body_and_self_rehashed_header_are_rejected(self):
        from origami_cad.cli_contract import digest
        path = self.repo / SKILL / 'contract.md'
        data = path.read_bytes().replace(b'0.45*t', b'9.99*t')
        data = ('<!-- sha256: ' + digest(data) + ' -->\n').encode() + data.split(b'\n', 1)[1]
        path.write_bytes(data)
        self.assertFalse(contract_current(self.repo))

    def test_regenerated_contract_for_different_runtime_is_rejected(self):
        path = self.repo / 'src/origami_cad/packaging.py'
        path.write_bytes(path.read_bytes() + b'\n# different runtime\n')
        (self.repo / SKILL / 'contract.md').write_bytes(render_contract(self.repo))
        self.assertFalse(contract_current(self.repo))

    def test_actual_cli_defaults_and_applicability(self):
        metadata = model_parameters()
        self.assertEqual(metadata['diamond-box']['width'], 50)
        self.assertEqual(metadata['hex-petal']['thickness'], 0.5)
        self.assertNotIn('width', metadata['hex-petal'])
        self.assertNotIn('depth', metadata['diamond-box'])
        self.assertEqual(metadata['miura-ori'], {})
