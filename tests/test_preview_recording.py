"""Recorded diagnostics permit roundoff; motion and gate decisions remain exact."""
import copy
import unittest

from origami_cad.packaging import generate_tuck_box
from origami_cad.preview_model import build_preview_model


class TestPreviewRecording(unittest.TestCase):
    def setUp(self):
        self.model = build_preview_model(generate_tuck_box())

    def test_recorded_diagnostic_relative_roundoff_matches(self):
        from origami_cad.preview_recording import preview_record, preview_records_match
        recorded = copy.deepcopy(self.model)
        recorded['continuity']['max_gap_mm'] *= 1 + 1e-9
        self.assertTrue(preview_records_match(recorded, self.model))

    def test_changed_availability_gate_and_geometry_do_not_match(self):
        from origami_cad.preview_recording import preview_record, preview_records_match
        for change in (
                lambda m: m.update(available=False),
                lambda m: m['continuity'].update(valid=False),
                lambda m: m['continuity'].update(tolerance_mm=0.6),
                lambda m: m['continuity'].update(max_gap_mm=0.51),
                lambda m: m['faces'][0]['vertices'][0].__setitem__(0, 0.01),
                lambda m: m['hinges'][0].update(angle_deg=89.999999999),
                lambda m: m['faces'][0].update(area_mm2=m['faces'][0]['area_mm2'] + 0.001)):
            recorded = copy.deepcopy(self.model)
            change(recorded)
            self.assertFalse(preview_records_match(recorded, self.model))

    def test_recording_never_mutates_or_requalifies_motion(self):
        from origami_cad.preview_recording import preview_record
        before = copy.deepcopy(self.model)
        recorded = preview_record(self.model)
        self.assertEqual(self.model, before)
        self.assertEqual(recorded['available'], self.model['available'])
        self.assertEqual(recorded['hinges'], self.model['hinges'])
        self.assertEqual([f['vertices'] for f in recorded['faces']],
                         [f['vertices'] for f in self.model['faces']])
        self.model['available'] = False
        self.model['continuity'].update(valid=False, max_gap_mm=0.500000000001)
        recorded = preview_record(self.model)
        self.assertFalse(recorded['available'])
        self.assertFalse(recorded['continuity']['valid'])
        self.assertGreater(self.model['continuity']['max_gap_mm'], 0.5)

    def test_unknown_fields_and_nonfinite_diagnostics_do_not_match(self):
        from origami_cad.preview_recording import preview_record, preview_records_match
        for change in (lambda m: m.update(unknown=True),
                       lambda m: m['continuity'].update(max_gap_mm=float('nan')),
                       lambda m: m['continuity'].update(max_gap_mm=float('inf'))):
            recorded = copy.deepcopy(self.model)
            change(recorded)
            self.assertFalse(preview_records_match(recorded, self.model))

    def test_diagnostic_comparison_cannot_cross_gate_threshold(self):
        from origami_cad.preview_recording import preview_records_match
        self.model['continuity']['max_gap_mm'] = 0.5 - 1e-10
        recorded = copy.deepcopy(self.model)
        recorded['continuity']['max_gap_mm'] = 0.5 + 1e-10
        self.assertFalse(preview_records_match(recorded, self.model))

    def test_malformed_or_nonfinite_witness_is_rejected(self):
        from origami_cad.preview_recording import preview_records_match
        for witness in ({'progress': 0.5, 'faces': [0, 1], 'endpoint': [float('nan'), 0.0]},
                        {'unknown': True}):
            recorded = copy.deepcopy(self.model)
            recorded['continuity']['worst'] = witness
            self.assertFalse(preview_records_match(recorded, self.model))

    def test_fabricated_seam_contact_and_loop_witnesses_are_rejected(self):
        from origami_cad.packaging import generate_crash_lock_box
        from origami_cad.preview_recording import preview_records_match
        model = build_preview_model(generate_crash_lock_box())
        for change in (
                lambda m: m['continuity']['worst'].update(faces=[999999, 999998], endpoint=[0.0, 0.0]),
                lambda m: m['coordination']['closure']['contacts'][0].update(other=999999),
                lambda m: m['coordination']['loop']['loops'][0].update(
                    other=999999, path=[999999] * 4)):
            recorded = copy.deepcopy(model)
            change(recorded)
            self.assertFalse(preview_records_match(recorded, model))
