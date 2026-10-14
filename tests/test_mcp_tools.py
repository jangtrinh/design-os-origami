"""Tools create real artifacts and refuse traversal, overwrites and unlisted reads."""
import json
from pathlib import Path

from origami_cad.mcp_tools import ToolService
from origami_cad.cli_contract import SKILL
from skill_fixture import SkillFixture, TUCK


class McpTools(SkillFixture):
    def setUp(self):
        super().setUp()
        (self.repo / SKILL / 'SKILL.md').write_text('Canonical workflow')
        self.service = ToolService(self.repo, self.base / 'workspace')

    def test_describe_build_validate_and_artifact_access(self):
        self.assertIn('contract', self.service.call('origami_describe', {}))
        built = self.service.call('origami_build', {'run_id': 'tuck', 'spec': TUCK})
        self.assertEqual(len(built['artifacts']), 5)
        self.assertTrue(self.service.call('origami_validate', {'run_id': 'tuck'})['ok'])
        artifact = self.service.call('origami_read_artifact', {'run_id': 'tuck', 'filename': built['artifacts'][0]['filename']})
        self.assertIn('sha256', artifact)
        receipt = self.service.call('origami_read_artifact', {'run_id': 'tuck', 'filename': 'artifact.json'})
        self.assertEqual(json.loads(receipt['data'])['schema_version'], 1)

    def test_long_lived_service_rejects_changed_source_even_with_new_contract(self):
        from origami_cad.cli_contract import render_contract
        source = self.repo / 'src/origami_cad/geometry.py'
        source.write_bytes(source.read_bytes() + b'\n# changed after server initialization\n')
        (self.repo / SKILL / 'contract.md').write_bytes(render_contract(self.repo))
        with self.assertRaisesRegex(ValueError, 'Runtime source or contract changed'):
            self.service.call('origami_describe', {})

    def test_repeat_build_invalid_dimension_and_unknown_arguments(self):
        self.service.call('origami_build', {'run_id': 'once', 'spec': TUCK})
        for arguments in [{'run_id': 'once', 'spec': TUCK},
                          {'run_id': 'bad', 'spec': TUCK | {'parameters': {'width': 0}}},
                          {'run_id': 'new', 'spec': TUCK, 'command': 'anything'}]:
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                self.service.call('origami_build', arguments)

    def test_run_id_traversal_absolute_unicode_and_symlink_escape(self):
        for name in ['../outside', '/absolute', '.', '', 'a/b', 'x' * 65, 'é', True]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.service.run_path(name)
        outside = self.base / 'outside'
        outside.mkdir()
        (self.service.workspace / 'linked').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.service.call('origami_build', {'run_id': 'linked', 'spec': TUCK})

    def test_unlisted_files_and_stale_hash_are_rejected(self):
        built = self.service.call('origami_build', {'run_id': 'tuck', 'spec': TUCK})
        for filename in ['../outside', '/absolute', 'private.txt']:
            with self.subTest(filename=filename), self.assertRaises(ValueError):
                self.service.call('origami_read_artifact', {'run_id': 'tuck', 'filename': filename})
        name = built['artifacts'][0]['filename']
        (self.service.workspace / 'tuck' / name).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            self.service.call('origami_read_artifact', {'run_id': 'tuck', 'filename': name})

    def test_read_size_bound_and_symlinked_manifest_artifact(self):
        built = self.service.call('origami_build', {'run_id': 'tuck', 'spec': TUCK})
        name = built['artifacts'][0]['filename']
        path = self.service.workspace / 'tuck' / name
        path.write_bytes(b'x' * (1024 * 1024 + 1))
        with self.assertRaisesRegex(ValueError, 'exceeds'):
            self.service.call('origami_read_artifact', {'run_id': 'tuck', 'filename': name})
        path.unlink()
        path.symlink_to(self.repo / SKILL / 'contract.md')
        with self.assertRaisesRegex(ValueError, 'Linked'):
            self.service.call('origami_read_artifact', {'run_id': 'tuck', 'filename': name})

    def test_no_browser_is_explicit_not_success(self):
        self.service.call('origami_build', {'run_id': 'tuck', 'spec': TUCK})
        with self.assertRaisesRegex(ValueError, 'LOOK: NOT RUN'):
            self.service.call('origami_look', {'run_id': 'tuck'})

    def test_look_rejects_symlinked_evidence_before_browser_writes(self):
        self.service.browser_cache = self.base / 'configured-cache'
        self.service.call('origami_build', {'run_id': 'tuck', 'spec': TUCK})
        outside = self.base / 'outside'
        outside.mkdir()
        (self.service.workspace / 'tuck/evidence').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Evidence destination escapes'):
            self.service.call('origami_look', {'run_id': 'tuck'})
        self.assertEqual(list(outside.iterdir()), [])

    def test_look_rejects_index_symlink_before_capture(self):
        from unittest.mock import patch
        self.service.browser_cache = self.base / 'configured-cache'
        self.service.call('origami_build', {'run_id': 'tuck', 'spec': TUCK})
        folder = self.service.workspace / 'tuck/evidence'
        folder.mkdir()
        sentinel = self.base / 'private-sentinel'
        sentinel.write_bytes(b'preserve me')
        (folder / 'artifact-index.json').symlink_to(sentinel)
        with patch('origami_cad.look_harness.capture_look', return_value={'ok': True}) as capture:
            with self.assertRaisesRegex(ValueError, 'Evidence index must be new'):
                self.service.call('origami_look', {'run_id': 'tuck'})
            capture.assert_not_called()
        self.assertEqual(sentinel.read_bytes(), b'preserve me')
