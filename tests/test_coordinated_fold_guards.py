"""Guards against sparse sampling and incidental-contact false positives."""
import copy
import unittest
from origami_cad import packaging
from origami_cad.fold_closure import endpoint_report, loop_closure
from origami_cad.fold_continuity import GATE_SAMPLES, continuity_report
from origami_cad.fold_coordinated import (DENSE_SAMPLES, build_coordinated_fold_model,
                                          qualify, rigid_locks)
from origami_cad.fold_faces import _extract_fold_model, build_fold_model
from test_production_dieline_topology import VARIANTS

SPARSE = ([0.0], [0.0, 1.0], [1.0], list(GATE_SAMPLES), [0.0, .5, 1.0], [.37])


def crash(**kwargs):
    cp = packaging.generate_crash_lock_box(**kwargs)
    return cp, _extract_fold_model(cp), build_coordinated_fold_model(cp)


def locked_indices(extracted):
    fused = {frozenset(lock['faces']) for lock in rigid_locks(extracted)}
    return {i for i, h in enumerate(extracted['hinges'])
            if frozenset((h['parent'], h['child'])) in fused}


class SparseSampling(unittest.TestCase):
    def test_requested_subset_never_replaces_dense_qualification(self):
        cp = packaging.generate_crash_lock_box()
        for samples in SPARSE:
            with self.subTest(samples=samples):
                model = build_coordinated_fold_model(cp, samples=samples)
                self.assertEqual(model['coordination']['candidate'], 'locked-seams')
                self.assertTrue(set(DENSE_SAMPLES) <= set(model['continuity']['samples']))
                self.assertTrue(set(samples) <= set(model['continuity']['samples']))
                source = model['coordination']['candidates'][0]
                self.assertEqual(source['name'], 'source')
                self.assertFalse(source['valid'])
                self.assertGreater(source['continuity']['max_gap_mm'], 50)
                self.assertTrue(set(DENSE_SAMPLES) <= set(source['continuity']['samples']))

    def test_qualify_unions_required_samples_and_rejects_empty_or_bad(self):
        _, extracted, model = crash()
        source = [h['angle_deg'] for h in extracted['hinges']]
        for samples in SPARSE:
            result = qualify(extracted, source, samples)
            self.assertFalse(result['continuity']['valid'])
            self.assertFalse(result['valid'])
        for bad in ([], [1.5], [float('nan')], ['0'], 0.5):
            with self.subTest(bad=bad), self.assertRaises((ValueError, TypeError)):
                qualify(extracted, source, bad)
        with self.assertRaises(ValueError):
            build_coordinated_fold_model(packaging.generate_crash_lock_box(), samples=[])

    def test_legacy_four_sample_gate_and_tray_diamond_unchanged(self):
        for generate in (packaging.generate_zero_glue_tray, packaging.generate_diamond_faceted_box):
            cp = generate()
            self.assertEqual(continuity_report(build_fold_model(cp))['samples'], [.25, .5, .75, 1.0])
            for samples in SPARSE:
                model = build_coordinated_fold_model(cp, samples=samples)
                self.assertTrue(model['available'])
                self.assertEqual(model['coordination']['candidate'], 'locked-seams')
                self.assertTrue(set(DENSE_SAMPLES) <= set(model['continuity']['samples']))


class EndpointConfiguration(unittest.TestCase):
    def test_only_proven_rigid_cluster_hinges_may_be_zero(self):
        _, extracted, model = crash()
        locked = locked_indices(extracted)
        self.assertEqual(len(locked), 4)
        schedule = model['coordination']['schedule_deg']
        for i, hinge in enumerate(extracted['hinges']):
            with self.subTest(hinge=i, faces=(hinge['parent'], hinge['child'])):
                probe = list(schedule); probe[i] = 0.0
                result = qualify(extracted, probe)
                if i in locked:
                    self.assertEqual(probe, schedule)
                    self.assertTrue(result['valid'])
                else:
                    self.assertFalse(result['valid'])
                    self.assertFalse(result['endpoint']['valid'])
                    self.assertEqual([d['hinge'] for d in result['endpoint']['deviations']], [i])

    def test_opening_body_walls_top_bottom_glue_or_flaps_fails(self):
        cp, extracted, model = crash()
        schedule = model['coordination']['schedule_deg']
        root = extracted['root']
        groups = {'body': [i for i, h in enumerate(extracted['hinges'])
                           if h['parent'] == root and h['axis'][0][0] == h['axis'][1][0]],
                  'top': [i for i, h in enumerate(extracted['hinges'])
                          if h['axis'][0][1] == 0 and h['axis'][1][1] == 0 and h['angle_deg']],
                  'bottom': [i for i, h in enumerate(extracted['hinges'])
                             if h['axis'][0][1] == h['axis'][1][1] != 0 and h['angle_deg']],
                  'glue': [i for i, h in enumerate(extracted['hinges'])
                           if h['axis'][0][0] == h['axis'][1][0] == 15.0]}
        self.assertEqual(len(groups['body']), 2)
        self.assertEqual(len(groups['top']), 4)
        self.assertEqual(len(groups['bottom']), 4)
        self.assertEqual(len(groups['glue']), 1)
        for name, indices in groups.items():
            with self.subTest(group=name):
                probe = list(schedule)
                for i in indices:
                    probe[i] = 0.0
                result = qualify(extracted, probe)
                self.assertFalse(result['valid'])
                self.assertFalse(result['endpoint']['valid'])
                self.assertEqual(sorted(d['hinge'] for d in result['endpoint']['deviations']), indices)
        # The container loop joins two body panels (Back free edge onto the Left/glue
        # hinge line); opening either body wall removes every body-to-body loop even
        # though flap contacts through the root may remain.
        h = next(c.length for c in cp.creases if c.label == 'Hinge_0')
        body = {f['id'] for f in extracted['faces'] if len(f['vertices']) == 4
                and {q[1] for q in f['vertices']} == {0, h} and f['area_mm2'] > 1600
                and min(q[0] for q in f['vertices']) > 0}
        self.assertEqual(len(body), 4)
        closed = loop_closure(extracted, schedule)['loops']
        self.assertTrue(any({l['face'], l['other']} <= body for l in closed))
        for i in groups['body']:
            body_open = list(schedule); body_open[i] = 0.0
            opened = loop_closure(extracted, body_open)['loops']
            self.assertFalse(any({l['face'], l['other']} <= body for l in opened), i)

    def test_non_source_magnitudes_signs_and_scaled_motion_fail(self):
        _, extracted, model = crash()
        schedule = model['coordination']['schedule_deg']
        first = next(i for i, a in enumerate(schedule) if a)
        for angle in (45.0, 135.0, -90.0, 89.999, 90.001):
            probe = list(schedule); probe[first] = angle
            result = qualify(extracted, probe)
            self.assertFalse(result['endpoint']['valid'], angle)
            self.assertFalse(result['valid'], angle)
        for scale in (.01, .5, .99, 1.01):
            result = qualify(extracted, [a*scale for a in schedule])
            self.assertFalse(result['valid'], scale)
            self.assertFalse(result['endpoint']['valid'], scale)
        tiny = qualify(extracted, [a*.001 for a in schedule])
        self.assertTrue(tiny['closure']['flat_endpoint'])
        self.assertFalse(tiny['valid'])

    def test_endpoint_report_lists_locked_hinges_and_source_targets(self):
        _, extracted, model = crash()
        report = endpoint_report(extracted, model['coordination']['schedule_deg'])
        self.assertTrue(report['valid'])
        self.assertEqual(sorted(report['locked']), sorted(locked_indices(extracted)))
        self.assertEqual(report['deviations'], [])
        self.assertEqual(report['source_deg'], [h['angle_deg'] for h in extracted['hinges']])


class BodyLoopClosure(unittest.TestCase):
    def test_crash_candidate_closes_a_root_loop_with_full_edge_coincidence(self):
        for kwargs in ({}, VARIANTS['crash-lock-box'], {'thickness': 0}):
            with self.subTest(kwargs=kwargs):
                cp, extracted, model = crash(**kwargs)
                self.assertTrue(model['available'])
                loop = model['coordination']['loop']
                self.assertTrue(loop['valid'])
                self.assertGreaterEqual(len(loop['loops']), 1)
                for item in loop['loops']:
                    self.assertGreaterEqual(len(item['path']), 4)
                    self.assertIn(extracted['root'], item['path'])
                    self.assertTrue(item['full'])
                self.assertGreater(model['coordination']['closure']['max_vertex_move_mm'], 100)
                self.assertGreaterEqual(sum(1 for a in model['coordination']['schedule_deg'] if a), 12)

    def test_open_strips_and_flat_trays_have_no_root_loop(self):
        diamond = _extract_fold_model(packaging.generate_diamond_faceted_box())
        open_strip = [
            h['angle_deg'] if (h['crease_type'] == 'CREASE'
                               and h['axis'][0][0] == h['axis'][1][0]
                               and h['axis'][0][0] in {60.0, 120.0}) else 0.0
            for h in diamond['hinges']
        ]
        self.assertEqual(loop_closure(diamond, open_strip)['loops'], [])
        tray = _extract_fold_model(packaging.generate_zero_glue_tray())
        rollovers = [90.0 if (h['parent'] != tray['root'] and abs(h['angle_deg']) == 180.0) else 0.0
                     for h in tray['hinges']]
        self.assertEqual(loop_closure(tray, rollovers)['loops'], [])

    def test_least_squares_relaxations_are_evidence_not_rescue(self):
        from origami_cad.geometry import CreaseType, Point2D
        unslit = packaging.generate_zero_glue_tray()
        unslit.cut_slits = {}
        unslit.creases = [c for c in unslit.creases
                          if not c.label.startswith(('CornerSlit_', 'CornerHinge_', 'CornerGusset'))]
        for cx, cy, sx, sy in ((70.0, 70.0, -1, -1), (170.0, 70.0, 1, -1),
                               (170.0, 140.0, 1, 1), (70.0, 140.0, -1, 1)):
            unslit.add_crease(Point2D(cx, cy), Point2D(cx + sx * 30.0, cy + sy * 30.0),
                              CreaseType.VALLEY, -90.0, "CornerGusset")
        model = build_coordinated_fold_model(unslit)
        relaxed = next(c for c in model['coordination']['candidates'] if c['name'] == 'least-squares')
        self.assertFalse(relaxed['valid'])
        self.assertFalse(relaxed['endpoint']['valid'])
        self.assertTrue(relaxed['rejected'])

    def test_baseline_models_keep_source_candidate_and_root_loops(self):
        for generate in (packaging.generate_tuck_box, packaging.generate_gable_handle_box,
                         packaging.generate_pillow_box, packaging.generate_hexagonal_petal_box):
            cp = generate(); before = copy.deepcopy(cp.__dict__)
            model = build_coordinated_fold_model(cp)
            self.assertEqual(model['coordination']['candidate'], 'source')
            self.assertEqual(model['faces'], build_fold_model(cp)['faces'])
            self.assertTrue(model['coordination']['endpoint']['valid'])
            self.assertEqual(cp.__dict__, before)


if __name__ == '__main__':
    unittest.main()
