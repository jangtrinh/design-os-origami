"""No rigid preview may tear a shared uncut material seam."""
import copy
import unittest
from origami_cad import packaging
from origami_cad.fold_faces import build_fold_model
from test_fold_kinematics import assert_closed_tube
from test_production_dieline_topology import MODELS, VARIANTS


class FoldContinuity(unittest.TestCase):
    def test_incompatible_models_fail_closed_without_name_classification(self):
        for generate in (packaging.generate_crash_lock_box,
                         packaging.generate_zero_glue_tray,
                         packaging.generate_diamond_faceted_box):
            cp = generate(); cp.name = 'Unclassified material'
            model = build_fold_model(cp)
            with self.subTest(generate=generate.__name__):
                self.assertFalse(model['available'])
                self.assertEqual(model['faces'], [])
                self.assertIn('coordinated or non-rigid folding', model['status'])
                from test_viewer_real_fold import html_for, model_from
                html = html_for(cp)
                self.assertEqual(model_from(html), model)
                self.assertIn(model['status'], html)
                self.assertIn('aria-disabled="true"', html)
                self.assertIn('<line ', html)

    def test_all_models_variants_match_actual_seam_qualification(self):
        from origami_cad.fold_faces import _extract_fold_model
        from origami_cad.fold_continuity import continuity_report
        for name, generate in MODELS.items():
            for kwargs in ({}, VARIANTS[name], {'thickness': 0}):
                with self.subTest(name=name, kwargs=kwargs):
                    cp = generate(**kwargs); original = copy.deepcopy(cp.__dict__)
                    report = continuity_report(_extract_fold_model(cp))
                    model = build_fold_model(cp)
                    self.assertEqual(model['available'], report['valid'])
                    self.assertEqual(model['continuity'], report)
                    self.assertEqual(report['samples'], [.25, .5, .75, 1.0])
                    self.assertEqual(report['tolerance_mm'], .5)
                    self.assertGreater(report['checked_edges'], 0)
                    self.assertEqual(cp.__dict__, original)

    def test_tuck_and_gable_keep_seams_and_rectangular_body_closure(self):
        for generate in (packaging.generate_tuck_box, packaging.generate_gable_handle_box):
            for kwargs in ({}, {'width': 137, 'depth': 43, 'height': 89, 'thickness': .9}):
                cp = generate(**kwargs); model = build_fold_model(cp)
                self.assertTrue(model['available'], model['status'])
                self.assertLessEqual(model['continuity']['max_gap_mm'], .5)
                assert_closed_tube(self, cp, model)

    def test_shared_boundaries_catch_missing_non_tree_fold_metadata(self):
        from origami_cad.fold_faces import _extract_fold_model
        from origami_cad.fold_continuity import continuity_report
        model = _extract_fold_model(packaging.generate_zero_glue_tray())
        model['non_tree_folds'] = []
        report = continuity_report(model)
        self.assertFalse(report['valid'])
        self.assertAlmostEqual(report['max_gap_mm'], 42.426406871, places=6)

    def test_cut_slits_do_not_become_uncut_seam_constraints(self):
        from origami_cad.fold_faces import _extract_fold_model
        from origami_cad.fold_continuity import continuity_report
        model = _extract_fold_model(packaging.generate_gable_handle_box())
        self.assertTrue(continuity_report(model)['valid'])
        # Removing CUT identity treats the real roof/gusset slits as material.
        model['cut_edges'] = []
        self.assertFalse(continuity_report(model)['valid'])


if __name__ == '__main__':
    unittest.main()
