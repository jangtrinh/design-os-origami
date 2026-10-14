"""Real generated fixtures in isolated temporary repositories."""
from pathlib import Path
import shutil
import tempfile
import unittest

from origami_cad.artifact_workflow import build
from origami_cad.cli_contract import SKILL, render_contract

ROOT = Path(__file__).resolve().parents[1]
TUCK = {'schema_version': 1, 'type': 'tuck-box', 'profiles': ['presentation', 'printer'], 'preview_requirement': 'available'}


class SkillFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / 'checkout'
        shutil.copytree(ROOT / 'src', self.repo / 'src', ignore=shutil.ignore_patterns('__pycache__'))
        (self.repo / SKILL).mkdir(parents=True)
        (self.repo / SKILL / 'contract.md').write_bytes(render_contract(self.repo))
        self.output = self.base / 'run'

    def build_tuck(self):
        self.receipt = build(self.repo, TUCK, self.output)
        self.name = self.receipt['blanks'][0]['name']
        return self.receipt
