"""Coordinated rigid schedules: dense seam continuity, endpoint closure, honest refusal."""
import copy
import json
import math
import unittest
from origami_cad import packaging
from origami_cad.fold_continuity import continuity_report
from origami_cad.fold_coordinated import (DENSE_SAMPLES, apply_schedule,
                                          build_coordinated_fold_model, closure_report,
                                          qualify, rigid_locks)
from origami_cad.fold_faces import _extract_fold_model, build_fold_model
from origami_cad.fold_kinematics import fold_vertices
from test_production_dieline_topology import VARIANTS

CYCLIC = {'crash-lock-box': packaging.generate_crash_lock_box,
          'zero-glue-tray': packaging.generate_zero_glue_tray,
          'diamond-box': packaging.generate_diamond_faceted_box}
BASELINE = (packaging.generate_tuck_box, packaging.generate_gable_handle_box,
            packaging.generate_pillow_box, packaging.generate_hexagonal_petal_box)


def schedule_of(model):
    return [h['angle_deg'] for h in model['hinges']]


def assert_closed_body(test, cp, model):
    """Four body panels (y in {0, h}) meet at right angles in a closed loop at 100%."""
    h = next(c.length for c in cp.creases if c.label == 'Hinge_0')
    folded = fold_vertices(model, 1)
    body = sorted((f for f in model['faces'] if len(f['vertices']) == 4
                   and {p[1] for p in f['vertices']} == {0, h} and min(p[0] for p in f['vertices']) > 0
                   and f['area_mm2'] > 1600), key=lambda f: min(p[0] for p in f['vertices']))
    test.assertEqual(len(body), 4)
    edges = []
    for f in body:
        pts = [p for p, s in zip(folded[f['id']], f['vertices']) if s[1] == 0]
        pts.sort(key=lambda p: next(s[0] for s, d in zip(f['vertices'], folded[f['id']]) if d is p))
        edges.append(pts)
    for i in range(4):
        test.assertLess(math.dist(edges[i][1], edges[(i+1) % 4][0]), .5)
        a = [edges[i][1][j]-edges[i][0][j] for j in (0, 2)]
        b = [edges[(i+1) % 4][1][j]-edges[(i+1) % 4][0][j] for j in (0, 2)]
        test.assertAlmostEqual(sum(x*y for x, y in zip(a, b)), 0, places=5)


class CoordinatedAdversarial(unittest.TestCase):
    def test_seam_perturbations_are_caught_densely(self):
        cp = packaging.generate_crash_lock_box()
        model = build_coordinated_fold_model(cp)
        extracted = _extract_fold_model(cp)
        schedule = schedule_of(model)
        locked = next(i for i, h in enumerate(model['hinges']) if h['angle_deg'] == 0.0)
        for angle in (5.0, -5.0, 90.0):
            perturbed = list(schedule); perturbed[locked] = angle
            result = qualify(extracted, perturbed)
            self.assertFalse(result['continuity']['valid'])
            self.assertFalse(result['valid'])
        damaged = copy.deepcopy(extracted)
        damaged['hinges'][0]['axis'][0][0] += 1.0
        self.assertFalse(qualify(damaged, schedule)['continuity']['valid'])
        # An early-progress tear is visible to the dense check even if 25/50/75/100 pass.
        late = copy.deepcopy(extracted)
        self.assertTrue(continuity_report(apply_schedule(late, schedule), DENSE_SAMPLES)['valid'])

    def test_fake_zero_motion_and_flat_endpoints_are_rejected(self):
        extracted = _extract_fold_model(packaging.generate_crash_lock_box())
        zero = qualify(extracted, [0.0]*len(extracted['hinges']))
        self.assertTrue(zero['continuity']['valid'])
        self.assertFalse(zero['closure']['valid'])
        self.assertIn('zero', zero['closure']['reason'])
        tiny = qualify(extracted, [1e-3]*len(extracted['hinges']))
        self.assertTrue(tiny['continuity']['valid'])
        self.assertFalse(tiny['closure']['valid'])
        self.assertTrue(tiny['closure']['flat_endpoint'])
        # Small wall angles slip under the seam tolerance but never close the tray.
        tray = _extract_fold_model(packaging.generate_zero_glue_tray())
        exploit = [3.0 if h['parent'] == tray['root'] else 0.0 for h in tray['hinges']]
        result = qualify(tray, exploit)
        self.assertTrue(result['continuity']['valid'])
        self.assertFalse(result['closure']['valid'])
        self.assertEqual(result['closure']['contacts'], [])

    def test_malformed_schedules_are_rejected(self):
        model = _extract_fold_model(packaging.generate_crash_lock_box())
        n = len(model['hinges'])
        for bad in ([90.0]*(n-1), [90.0]*(n+1), [float('nan')]*n, [float('inf')]*n,
                    ['90']*n, [True]*n, None, 90.0, {}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                apply_schedule(model, bad)
        with self.assertRaises(ValueError):
            qualify(model, [90.0]*(n-1))

    def test_closure_contacts_need_new_coincidence_not_preexisting_slits(self):
        model = build_fold_model(packaging.generate_tuck_box())
        report = closure_report(model)
        self.assertTrue(report['valid'])
        flat = closure_report(apply_schedule(model, [0.0]*len(model['hinges'])))
        self.assertEqual(flat['contacts'], [])
        self.assertFalse(flat['valid'])

    def test_unsupported_patterns_remain_generic_unavailable(self):
        model = build_coordinated_fold_model(packaging.generate_miura_ori_sleeve())
        self.assertFalse(model['available'])
        self.assertEqual(model['status'], '3D fold preview not available for this pattern')
        self.assertEqual(model['coordination']['candidates'], [])


if __name__ == '__main__':
    unittest.main()
