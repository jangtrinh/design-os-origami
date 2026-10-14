"""Bundle generation fails closed on byte/path drift, links and staging conflicts."""
from pathlib import Path
import json
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import sync_host_bundles as sync


class TestHostBundleSync(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='origami thư mục ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'checkout with spaces'
        self.root.mkdir()
        source = Path(__file__).resolve().parents[1]
        shutil.copytree(source / 'skills/es-origami-cad', self.root / sync.SKILL)
        for name in sync.REQUIRED:
            path = self.root / sync.SKILL / name
            if not path.exists():
                path.write_text('integration fixture\n')
        shutil.copyfile(source / 'pyproject.toml', self.root / 'pyproject.toml')
        (self.root / 'scripts').mkdir()
        (self.root / 'scripts/run_mcp.py').write_text('')
        self.expected = sync.expected_files(self.root)
        sync.write_files(self.root, self.expected)

    def test_exact_byte_copies_and_version_from_metadata(self):
        self.assertEqual(sync.drift(self.root, self.expected), [])
        for host in sync.HOSTS:
            for path in (self.root / sync.SKILL).rglob('*'):
                if path.is_file():
                    rel = path.relative_to(self.root / sync.SKILL)
                    self.assertEqual(path.read_bytes(), (self.root / 'bundles' / host /
                                                         sync.SKILL / rel).read_bytes())
        metadata = self.root / 'pyproject.toml'
        metadata.write_text(metadata.read_text().replace('version = "0.1.0"', 'version = "0.2.7"'))
        updated = sync.expected_files(self.root)
        self.assertTrue(sync.drift(self.root, updated))
        plugin = json.loads(updated[Path('bundles/codex/plugin.json')])
        self.assertEqual(plugin['version'], '0.2.7')

    def test_changed_missing_extra_manifest_and_links_each_detected(self):
        path = self.root / 'bundles/codex/skills/es-origami-cad/SKILL.md'
        original = path.read_bytes()
        path.write_bytes(original + b'changed')
        self.assertIn('changed: bundles/codex/skills/es-origami-cad/SKILL.md', sync.drift(self.root, self.expected))
        path.unlink()
        self.assertIn('missing: bundles/codex/skills/es-origami-cad/SKILL.md', sync.drift(self.root, self.expected))
        path.write_bytes(original)
        extra = self.root / 'bundles/codex/extra.txt'
        extra.write_text('unexpected')
        self.assertIn('extra: bundles/codex/extra.txt', sync.drift(self.root, self.expected))
        extra.unlink()
        manifest = self.root / '.agents/plugins/marketplace.json'
        manifest.write_text('{}')
        self.assertIn('changed: .agents/plugins/marketplace.json', sync.drift(self.root, self.expected))
        manifest.write_bytes(self.expected[Path('.agents/plugins/marketplace.json')])
        path.unlink()
        path.symlink_to(self.root / sync.SKILL / 'SKILL.md')
        with self.assertRaises(ValueError):
            sync.drift(self.root, self.expected)
        with self.assertRaises(ValueError):
            sync.write_files(self.root, self.expected)

    def test_linked_source_directory_rejected(self):
        target = self.root / sync.SKILL / 'linked'
        target.symlink_to(self.root / 'scripts', target_is_directory=True)
        with self.assertRaises(ValueError):
            sync.expected_files(self.root)

    def test_staging_json_and_mirror_are_exact_and_refuse_overwrite(self):
        stage = Path(self.temp.name) / 'local staging 日本語'
        sync.stage(self.root, 'grok-build', stage, stage.parent / 'runs', sys.executable)
        config = json.loads((stage / '.mcp.json').read_text())
        self.assertEqual(config['mcpServers']['origami-cad']['args'][1],
                         str(self.root.resolve() / 'scripts/run_mcp.py'))
        self.assertFalse((stage.parent / 'runs').exists())
        with self.assertRaises(ValueError):
            sync.stage(self.root, 'grok-build', stage, stage.parent / 'runs', sys.executable)
        mirror = Path(self.temp.name) / 'generated mirror'
        skill = sync.skill_files(self.root)
        sync.write_files(mirror, skill, fresh=True)
        self.assertEqual(sync.drift(mirror, skill, roots=(Path('.'),)), [])

    def test_extra_hidden_file_and_linked_bundle_parent_rejected(self):
        hidden = self.root / 'bundles/codex/.unexpected'
        hidden.write_text('unexpected')
        self.assertTrue(any('extra:' in line for line in sync.drift(self.root, self.expected)))
        hidden.unlink()
        target = self.root / 'bundles/codex'
        shutil.rmtree(target)
        target.symlink_to(self.root / 'scripts', target_is_directory=True)
        with self.assertRaises(ValueError):
            sync.drift(self.root, self.expected)
