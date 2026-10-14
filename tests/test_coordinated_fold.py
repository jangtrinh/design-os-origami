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


class CoordinatedFold(unittest.TestCase):
    def test_dense_samples_and_old_gate_are_not_weakened(self):
        self.assertEqual(len(DENSE_SAMPLES), 101)
        for required in (0.0, .5, 1.0):
            self.assertIn(required, DENSE_SAMPLES)
        model = build_fold_model(packaging.generate_tuck_box())
        report = continuity_report(model)
        self.assertEqual(report['samples'], [.25, .5, .75, 1.0])
        self.assertEqual(report['tolerance_mm'], .5)
        dense = continuity_report(model, DENSE_SAMPLES)
        self.assertEqual(dense['samples'], DENSE_SAMPLES)
        self.assertEqual(dense['tolerance_mm'], .5)
        for generate in CYCLIC.values():
            self.assertFalse(build_fold_model(generate())['available'])

    def test_baseline_models_keep_identical_faces_and_hinges(self):
        for generate in BASELINE:
            cp = generate(); before = copy.deepcopy(cp.__dict__)
            base, model = build_fold_model(cp), build_coordinated_fold_model(cp)
            self.assertTrue(model['available'])
            for key in ('faces', 'root', 'hinges', 'non_tree_folds', 'cut_edges'):
                self.assertEqual(model[key], base[key])
            self.assertEqual(model['coordination']['candidate'], 'source')
            self.assertEqual(model['continuity']['samples'], DENSE_SAMPLES)
            self.assertLessEqual(model['continuity']['max_gap_mm'], .5)
            self.assertEqual(cp.__dict__, before)
            self.assertEqual(json.loads(json.dumps(model)), model)

    def test_crash_lock_qualifies_with_locked_diagonals_dense_and_closed(self):
        # A flap whose two 45-degree diagonals meet at one apex fuses the outer face to
        # the central triangle (two shared seams), so those diagonals are locked flat.
        # When width/2 exceeds depth the diagonals end on the flap edge and stay free.
        for kwargs in ({}, VARIANTS['crash-lock-box'], {'thickness': 0}):
            with self.subTest(kwargs=kwargs):
                cp = packaging.generate_crash_lock_box(**kwargs)
                before = copy.deepcopy(cp.__dict__)
                allowance = cp.calculate_score_allowance(90.0)
                w, d = kwargs.get('width', 80.0)+allowance, kwargs.get('depth', 60.0)+allowance
                expected_locks = 2 + 2*(w/2 <= d)
                extracted = _extract_fold_model(cp)
                model = build_coordinated_fold_model(cp)
                self.assertTrue(model['available'], model['status'])
                self.assertEqual(model['faces'], extracted['faces'])
                self.assertEqual(model['coordination']['candidate'], 'locked-seams')
                locks = model['coordination']['locked']
                self.assertEqual(len(locks), expected_locks)
                fused = {frozenset(lock['faces']) for lock in locks}
                for hinge, source in zip(model['hinges'], extracted['hinges']):
                    self.assertEqual(hinge['axis'], source['axis'])
                    if frozenset((hinge['parent'], hinge['child'])) in fused:
                        self.assertEqual(hinge['crease_type'], 'VALLEY')
                        self.assertEqual(hinge['angle_deg'], 0.0)
                    else:
                        self.assertEqual(hinge['angle_deg'], source['angle_deg'])
                self.assertEqual(sum(1 for h in model['hinges'] if h['angle_deg'] == 0.0), expected_locks)
                self.assertEqual(model['continuity']['samples'], DENSE_SAMPLES)
                self.assertLessEqual(model['continuity']['max_gap_mm'], 1e-9)
                self.assertTrue(model['coordination']['closure']['valid'])
                self.assertGreaterEqual(len(model['coordination']['closure']['contacts']), 1)
                assert_closed_body(self, cp, model)
                self.assertEqual(cp.__dict__, before)
                self.assertEqual(json.loads(json.dumps(model)), model)
                self.assertEqual(model['coordination']['schedule_deg'], schedule_of(model))

    def test_rigid_locks_come_from_doubly_shared_seams_only(self):
        expected = {
            packaging.generate_crash_lock_box: 4,
            packaging.generate_zero_glue_tray: 4,
            packaging.generate_diamond_faceted_box: 8,
        }
        for generate, count in expected.items():
            locks = rigid_locks(_extract_fold_model(generate()))
            self.assertEqual(len(locks), count)
            for lock in locks:
                self.assertEqual(len(lock['axes']), 2)
        self.assertEqual(rigid_locks(_extract_fold_model(packaging.generate_tuck_box())), [])

    def test_tray_and_diamond_stay_honestly_unavailable_with_evidence(self):
        for name in ('zero-glue-tray', 'diamond-box'):
            for kwargs in ({}, VARIANTS[name], {'thickness': 0}):
                with self.subTest(name=name, kwargs=kwargs):
                    cp = CYCLIC[name](**kwargs); before = copy.deepcopy(cp.__dict__)
                    model = build_coordinated_fold_model(cp)
                    self.assertTrue(model['available'], model['status'])
                    self.assertEqual(model['coordination']['candidate'], 'locked-seams')
                    self.assertEqual(model['continuity']['samples'], DENSE_SAMPLES)
                    self.assertLessEqual(model['continuity']['max_gap_mm'], 1e-9)
                    self.assertTrue(model['coordination']['closure']['valid'])
                    self.assertTrue(model['coordination']['endpoint']['valid'])
                    self.assertTrue(model['coordination']['loop']['valid'])
                    source = model['coordination']['candidates'][0]
                    self.assertEqual(source['name'], 'source')
                    self.assertFalse(source['continuity']['valid'])
                    self.assertGreater(source['continuity']['max_gap_mm'], 20)
                    self.assertEqual(cp.__dict__, before)
                    self.assertEqual(json.loads(json.dumps(model)), model)
        # An unslit degree-3 corner tray remains overconstrained and must stay honestly unavailable.
        unslit = self._unslit_tray()
        refused = build_coordinated_fold_model(unslit)
        self.assertFalse(refused['available'])
        self.assertIsNone(refused['coordination']['candidate'])
        names = [c['name'] for c in refused['coordination']['candidates']]
        self.assertEqual(names[0], 'source')
        self.assertIn('least-squares', names)
        for candidate in refused['coordination']['candidates']:
            self.assertFalse(candidate['valid'])
            self.assertTrue(candidate['rejected'])

    @staticmethod
    def _unslit_tray():
        from origami_cad.geometry import CreaseType, Point2D
        cp = packaging.generate_zero_glue_tray()
        cp.cut_slits = {}
        cp.creases = [c for c in cp.creases
                      if not c.label.startswith(('CornerSlit_', 'CornerHinge_', 'CornerGusset'))]
        for cx, cy, sx, sy in ((70.0, 70.0, -1, -1), (170.0, 70.0, 1, -1),
                               (170.0, 140.0, 1, 1), (70.0, 140.0, -1, 1)):
            cp.add_crease(Point2D(cx, cy), Point2D(cx + sx * 30.0, cy + sy * 30.0),
                          CreaseType.VALLEY, -90.0, "CornerGusset")
        return cp

    def test_tray_sampled_corner_schedules_above_ten_degrees_fail(self):
        # When corner relief slits and tab hinges are absent, each corner vertex has degree
        # three (two base hinges and one gusset diagonal), so folding walls tears the corner.
        model = _extract_fold_model(self._unslit_tray())
        walls = [i for i, h in enumerate(model['hinges']) if h['parent'] == model['root']]
        self.assertEqual(len(walls), 4)
        worst_pass = 0.0
        for alpha in range(10, 181, 10):
            for beta in range(-180, 181, 10):
                schedule = [0.0]*len(model['hinges'])
                for k, index in enumerate(walls):
                    schedule[index] = float(alpha if k % 2 == 0 else beta)
                report = continuity_report(apply_schedule(model, schedule), [1.0])
                self.assertFalse(report['valid'], (alpha, beta, report['max_gap_mm']))
                worst_pass = max(worst_pass, report['max_gap_mm'])
        self.assertGreater(worst_pass, 40)

    def test_diamond_straight_line_branches_are_continuous_but_do_not_close(self):
        model = _extract_fold_model(packaging.generate_diamond_faceted_box())
        # Folding only two vertical panel hinges (forming an open U-channel) is
        # continuous across all seams but never closes a container loop.
        open_strip = [
            h['angle_deg'] if (h['crease_type'] == 'CREASE'
                               and h['axis'][0][0] == h['axis'][1][0]
                               and h['axis'][0][0] in {60.0, 120.0}) else 0.0
            for h in model['hinges']
        ]
        result = qualify(model, open_strip)
        self.assertTrue(result['continuity']['valid'])
        self.assertFalse(result['closure']['valid'])
        self.assertFalse(result['valid'])
        mixed = qualify(model, schedule_of(model))
        self.assertFalse(mixed['continuity']['valid'])
        self.assertGreater(mixed['continuity']['max_gap_mm'], 40)


if __name__ == '__main__':
    unittest.main()
