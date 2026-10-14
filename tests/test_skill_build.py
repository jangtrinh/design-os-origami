"""Declarative input and no-partial-success workflow boundaries."""
import math
from pathlib import Path
import threading
from unittest.mock import patch

from origami_cad.artifact_workflow import build, normalize_spec, read_spec
from origami_cad.artifact_validation import validate
from skill_fixture import SkillFixture, TUCK


class SkillBuild(SkillFixture):
    def test_real_printer_and_presentation_same_request(self):
        receipt = self.build_tuck()
        self.assertEqual(len(receipt['files']), 5)
        self.assertEqual(validate(self.repo, self.output), [])
        self.assertEqual(set(receipt['profiles']), {'presentation', 'printer'})

    def test_two_piece_product_never_combines_nets(self):
        receipt = build(self.repo, {'schema_version': 1, 'type': 'sleeve-tray'}, self.output)
        self.assertEqual(len(receipt['blanks']), 2)
        self.assertEqual(len(receipt['files']), 6)
        self.assertEqual(validate(self.repo, self.output), [])

    def test_custom_input_not_compared_to_catalog_defaults(self):
        receipt = build(self.repo, TUCK | {'parameters': {'width': 100, 'depth': 65, 'height': 150}}, self.output)
        self.assertEqual(receipt['spec']['parameters']['width'], 100)
        self.assertEqual(validate(self.repo, self.output), [])

    def test_unknown_ignored_incompatible_nonfinite_and_boolean_rejected(self):
        cases = [TUCK | {'extra': 1}, TUCK | {'parameters': {'radius': 10}},
                 TUCK | {'profiles': ['bogus']}, TUCK | {'profiles': ['printer']},
                 TUCK | {'parameters': {'thickness': 0}}, TUCK | {'parameters': {'width': True}},
                 TUCK | {'parameters': {'height': math.inf}}, TUCK | {'schema_version': True},
                 {'schema_version': 1, 'type': 'hex-petal', 'parameters': {'width': 3}},
                 {'schema_version': 1, 'type': 'miura-ori', 'parameters': {'thickness': 0.5}}]
        for spec in cases:
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                normalize_spec(spec)

    def test_size_lines_duplicate_keys_and_nonfinite_json_rejected(self):
        path = self.base / 'spec.json'
        for data in [' ' * 65537, '\n' * 201, '{"type":"tuck-box","type":"hex-petal"}', '{"number":NaN}']:
            path.write_text(data)
            with self.subTest(data=data[:30]), self.assertRaises(ValueError):
                read_spec(path)

    def test_repeated_run_and_existing_empty_directory_rejected(self):
        self.build_tuck()
        before = (self.output / 'artifact.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'must be new'):
            build(self.repo, TUCK, self.output)
        self.assertEqual((self.output / 'artifact.json').read_bytes(), before)
        empty = self.base / 'empty'
        empty.mkdir()
        with self.assertRaisesRegex(ValueError, 'must be new'):
            build(self.repo, TUCK, empty)

    def test_failed_export_leaves_no_run_or_stage(self):
        with patch('origami_cad.artifact_workflow.export_printer_pdf', side_effect=ValueError('export failed')):
            with self.assertRaisesRegex(ValueError, 'export failed'):
                build(self.repo, TUCK, self.output)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.base.glob('.run-*')), [])

    def test_cancelled_build_does_not_publish(self):
        event = threading.Event()
        event.set()
        with self.assertRaisesRegex(ValueError, 'cancelled'):
            build(self.repo, TUCK, self.output, event)
        self.assertFalse(self.output.exists())
