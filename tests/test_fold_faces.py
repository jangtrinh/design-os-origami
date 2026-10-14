"""Source-led planar face and topology checks, independent of stored facets."""
import copy
import inspect
import json
import unittest

from origami_cad import packaging
from origami_cad.geometry import CreaseType, Point2D
from origami_cad.fold_faces import build_fold_model, _extract_fold_model
from dieline_topology import cut_loops, on_segment
from origami_cad.printer_paths import signed_area
from test_production_dieline_topology import MODELS, VARIANTS, rectangle


def blank_area(cp):
    cuts = [c for c in cp.creases if c.crease_type == CreaseType.CUT
            and c.label not in getattr(cp, 'cut_slits', {})]
    loops, errors = cut_loops(cuts)
    if errors:
        raise AssertionError(errors)
    areas = sorted((abs(signed_area(r)) for r in loops), reverse=True)
    return areas[0] - sum(areas[1:])


class FoldFaces(unittest.TestCase):
    def test_all_generators_defaults_variants_area_tree_and_immutability(self):
        counts = {'tuck-box': 13, 'zero-glue-tray': 17, 'crash-lock-box': 17,
                  'gable-box': 21, 'diamond-box': 21, 'pillow-box': 9, 'hex-petal': 14}
        generators = {f for n, f in inspect.getmembers(packaging, inspect.isfunction)
                      if n.startswith('generate_') and n != 'generate_miura_ori_sleeve'}
        from origami_cad.product_registry import PRODUCTS
        self.assertEqual(generators, {getattr(packaging, function) for _, _, function in PRODUCTS})
        for name, generate in MODELS.items():
            for kwargs in ({}, VARIANTS[name], {'thickness': 0}):
                with self.subTest(name=name, kwargs=kwargs):
                    cp = generate(**kwargs)
                    original = copy.deepcopy(cp.__dict__)
                    cp.facets = []  # Stored approximations cannot supply the faces.
                    facets_free = copy.deepcopy(cp.__dict__)
                    # Pure extraction remains checked even when motion is unsuitable.
                    model = _extract_fold_model(cp)
                    self.assertTrue(model['available'], model['status'])
                    self.assertEqual(cp.__dict__, facets_free)
                    self.assertAlmostEqual(sum(f['area_mm2'] for f in model['faces']),
                                           blank_area(cp), places=5)
                    if not kwargs:
                        self.assertEqual(len(model['faces']), counts[name])
                    self.assertEqual(json.loads(json.dumps(model)), model)
                    seen = {model['root']}
                    for hinge in model['hinges']:
                        self.assertIn(hinge['parent'], seen)
                        self.assertNotIn(hinge['child'], seen)
                        seen.add(hinge['child'])
                    self.assertEqual(seen, {f['id'] for f in model['faces']})
                    self.assertEqual(len(model['hinges']), len(model['faces']) - 1)
                    root = next(f for f in model['faces'] if f['id'] == model['root'])
                    self.assertEqual(root['area_mm2'], max(f['area_mm2'] for f in model['faces']))
                    for hinge in model['hinges'] + model['non_tree_folds']:
                        source = [c for c in cp.creases if c.crease_type == hinge['crease_type']
                                  and all(on_segment(Point2D(*p), c) for p in hinge['axis'])]
                        self.assertTrue(source)
                        self.assertTrue(any(abs(hinge['angle_deg']) == abs(c.target_angle_deg)
                                            for c in source))
                    self.assertEqual(original['creases'], cp.creases)

    def test_gable_holes_excluded_and_crash_slits_are_not_hinges(self):
        model = build_fold_model(packaging.generate_gable_handle_box())
        self.assertEqual(sum(len(f.get('holes', [])) for f in model['faces']), 2)
        self.assertAlmostEqual(sum(abs(signed_area([Point2D(*p) for p in r]))
                                   for f in model['faces'] for r in f.get('holes', [])), 2420)
        cp = packaging.generate_crash_lock_box()
        model = _extract_fold_model(cp)
        slits = [c for c in cp.creases if c.label in cp.cut_slits]
        for hinge in model['hinges']:
            a, b = [Point2D(*p) for p in hinge['axis']]
            self.assertFalse(any({a, b} == {c.p1, c.p2} for c in slits))

    def test_cut_intersections_and_hole_in_generic_pattern(self):
        cp = rectangle()  # Fold endpoints meet interiors of CUT edges.
        hole = [Point2D(3, 2), Point2D(7, 2), Point2D(7, 6), Point2D(3, 6)]
        for a, b in zip(hole, hole[1:] + hole[:1]):
            cp.add_crease(a, b, CreaseType.CUT)
        model = build_fold_model(cp)
        self.assertTrue(model['available'])
        self.assertEqual(len(model['faces']), 2)
        self.assertEqual(sum(f['area_mm2'] for f in model['faces']), 384)
        self.assertEqual(sum(len(f.get('holes', [])) for f in model['faces']), 1)

    def test_missing_cut_disconnected_fold_and_unsupported_fail_explicitly(self):
        for mutate in ('cut', 'disconnected', 'overlap', 'nonfinite', 'miura', 'deer'):
            cp = rectangle()
            if mutate == 'cut':
                cp.creases.pop(0)
            elif mutate == 'disconnected':
                cp.creases.pop()
                cp.add_crease(Point2D(10, 0), Point2D(10, 20), CreaseType.CUT)
                cp.cut_slits = {'': 'splits material'}
            elif mutate == 'overlap':
                cp.creases.append(copy.deepcopy(cp.creases[-1]))
            elif mutate == 'nonfinite':
                cp.creases[0].p1 = Point2D(float('nan'), 0)
            else:
                cp.name = 'MiuraOri_6x4' if mutate == 'miura' else 'DeerBirdBase'
            with self.subTest(mutate=mutate):
                model = build_fold_model(cp)
                self.assertEqual(model, {'available': False,
                    'status': '3D fold preview not available for this pattern',
                    'faces': [], 'root': None, 'hinges': [], 'non_tree_folds': []})

    def test_fold_outside_material_cannot_be_silently_dropped(self):
        cp = rectangle()
        cp.add_crease(Point2D(-5, 5), Point2D(25, 5), CreaseType.CREASE)
        self.assertFalse(build_fold_model(cp)['available'])

    def test_raw_degenerate_score_is_rejected_before_source_splitter_drops_it(self):
        cp = rectangle()
        cp.add_crease(Point2D(5, 5), Point2D(5, 5), CreaseType.CREASE)
        self.assertFalse(build_fold_model(cp)['available'])

    def test_non_tree_fold_edges_are_not_animated_hinges(self):
        model = _extract_fold_model(packaging.generate_diamond_faceted_box())
        self.assertTrue(model['non_tree_folds'])
        axes = {frozenset(map(tuple, h['axis'])) for h in model['hinges']}
        for fold in model['non_tree_folds']:
            self.assertNotIn(frozenset(map(tuple, fold['axis'])), axes)


if __name__ == '__main__':
    unittest.main()
