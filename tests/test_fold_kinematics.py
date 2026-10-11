"""Fold transforms tested against source points and analytic rotations."""
import copy
import math
import unittest
from origami_cad import packaging
from origami_cad.fold_faces import build_fold_model, _extract_fold_model
from origami_cad.fold_kinematics import fold_vertices
from origami_cad.geometry import CreaseType, Point2D
from test_production_dieline_topology import MODELS, rectangle


def assert_closed_tube(test, cp, model):
    folded = fold_vertices(model, 1)
    h = next(c.length for c in cp.creases if c.label.endswith('_LeftFront'))
    body = [f for f in model['faces'] if len(f['vertices']) >= 4
            and {p[1] for p in f['vertices']} == {0, h}]
    test.assertEqual(len(body), 4)
    edges = []
    for f in sorted(body, key=lambda f: min(p[0] for p in f['vertices'])):
        limits = {min(p[0] for p in f['vertices']), max(p[0] for p in f['vertices'])}
        test.assertAlmostEqual(f['area_mm2'], (max(limits)-min(limits))*h)
        # Gable top-edge contacts retain collinear vertices; take rectangle corners.
        edge = [p for p, src in zip(folded[f['id']], f['vertices'])
                if src[1] == 0 and src[0] in limits]
        test.assertEqual(len(edge), 2)
        edge.sort(key=lambda p: next(src[0] for src, dest in
                  zip(f['vertices'], folded[f['id']]) if dest is p))
        edges.append(edge)
        test.assertLess(max(abs(p[1]) for p in edge), .000001)
    for i in range(4):
        test.assertLess(math.dist(edges[i][1], edges[(i+1) % 4][0]), .5)
        a = [edges[i][1][j] - edges[i][0][j] for j in (0, 2)]
        b = [edges[(i+1) % 4][1][j] - edges[(i+1) % 4][0][j] for j in (0, 2)]
        test.assertAlmostEqual(sum(x*y for x, y in zip(a, b)), 0, places=5)


class FoldKinematics(unittest.TestCase):
    def test_flat_source_identity_and_root_stays_fixed(self):
        for generate in MODELS.values():
            model = _extract_fold_model(generate())
            before = copy.deepcopy(model)
            flat, folded = fold_vertices(model, 0), fold_vertices(model, .5)
            for f in model['faces']:
                self.assertEqual(flat[f['id']], [p + [0.0] for p in f['vertices']])
            root = next(f for f in model['faces'] if f['id'] == model['root'])
            self.assertEqual(folded[root['id']], [p + [0.0] for p in root['vertices']])
            self.assertEqual(model, before)

    def test_tuck_tube_closes_defaults_and_variants(self):
        for kwargs in ({}, {'width': 137, 'depth': 43, 'height': 89, 'thickness': .9},
                       {'width': 45, 'depth': 80, 'height': 155, 'thickness': 0}):
            cp = packaging.generate_tuck_box(**kwargs)
            assert_closed_tube(self, cp, build_fold_model(cp))

    def test_sign_target_and_axis_reverse_invariance(self):
        for kind in (CreaseType.CREASE, CreaseType.VALLEY, CreaseType.MOUNTAIN):
            for reverse in (False, True):
                cp = rectangle()
                cp.creases[-1].crease_type = kind
                cp.creases[-1].target_angle_deg = -37
                if reverse:
                    cp.creases[-1].p1, cp.creases[-1].p2 = cp.creases[-1].p2, cp.creases[-1].p1
                model = build_fold_model(cp)
                hinge = model['hinges'][0]
                self.assertEqual(hinge['angle_deg'], -37 if kind == CreaseType.MOUNTAIN else 37)
                z = [p[2] for p in fold_vertices(model, 1)[hinge['child']]]
                self.assertAlmostEqual(max(map(abs, z)), 10 * math.sin(math.radians(37)))
                self.assertGreater(max(z), 0) if kind == CreaseType.MOUNTAIN else self.assertLess(min(z), 0)

    def test_subtree_parent_frame_preserves_hinge_and_lengths(self):
        model = build_fold_model(packaging.generate_tuck_box())
        folded = fold_vertices(model, .53)
        for face in model['faces']:
            src, dst = face['vertices'], folded[face['id']]
            for i in range(len(src)):
                self.assertAlmostEqual(math.dist(src[i], src[i-1]), math.dist(dst[i], dst[i-1]))
        for hinge in model['hinges']:
            for endpoint in hinge['axis']:
                matches = []
                for fid in (hinge['parent'], hinge['child']):
                    face = next(f for f in model['faces'] if f['id'] == fid)
                    matches.append(folded[fid][face['vertices'].index(endpoint)])
                self.assertLess(math.dist(*matches), 1e-7)

    def test_oblique_axis_is_rigid_and_has_no_box_coordinate_assumption(self):
        from origami_cad.fold_kinematics import rotation_about_axis
        axis = [[-7, 3], [5, 19]]  # Unit axis (0.6, 0.8, 0).
        matrix = rotation_about_axis(axis, 90)
        point = [-15, 9, 0, 1]  # Left of axis, 10 mm perpendicular distance.
        transformed = [sum(row[j]*point[j] for j in range(4)) for row in matrix[:3]]
        for got, expected in zip(transformed, [-7, 3, 10]):
            self.assertAlmostEqual(got, expected)
        for p in axis:
            transformed = [sum(row[j]*v for j, v in enumerate([*p, 0, 1]))
                           for row in matrix[:3]]
            for got, expected in zip(transformed, [*p, 0]):
                self.assertAlmostEqual(got, expected)

    def test_progress_rejects_invalid_values_and_unavailable_is_empty(self):
        model = build_fold_model(packaging.generate_tuck_box())
        for t in (-.01, 1.01, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                fold_vertices(model, t)
        self.assertEqual(fold_vertices(build_fold_model(packaging.generate_miura_ori_sleeve()), .5), {})

    def test_mutation_controls_sign_axis_face_and_order(self):
        cp = packaging.generate_tuck_box()
        model = build_fold_model(cp)
        for attack in ('sign', 'axis', 'face', 'order'):
            damaged = copy.deepcopy(model)
            if attack == 'sign':
                for hinge in damaged['hinges']:
                    hinge['angle_deg'] *= -1
                # Closure alone permits outward folding, so test inside sign separately.
                bad = fold_vertices(damaged, .5)
                first = next(h for h in damaged['hinges'] if h['parent'] == damaged['root'])
                with self.assertRaises(AssertionError):
                    self.assertLess(min(p[2] for p in bad[first['child']]), -1e-7)
            elif attack == 'axis':
                damaged['hinges'][0]['axis'][0][0] += 10
                with self.assertRaises((AssertionError, ValueError)):
                    assert_closed_tube(self, cp, damaged)
            elif attack == 'face':
                damaged['faces'].pop()
                with self.assertRaises(ValueError):
                    fold_vertices(damaged, .5)
            else:
                damaged['hinges'].reverse()
                with self.assertRaises(ValueError):
                    fold_vertices(damaged, .5)


if __name__ == '__main__':
    unittest.main()
