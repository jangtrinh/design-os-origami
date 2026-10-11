"""Independent segment checks for tuck hinges and their preserved cut exterior."""

import copy
from collections import defaultdict
import unittest

from origami_cad.geometry import CreaseLine, CreaseType, Point2D
from origami_cad.packaging import generate_tuck_box

FOLDS = {CreaseType.CREASE, CreaseType.MOUNTAIN, CreaseType.VALLEY}


def overlap_length(a, b, tolerance=1e-8):
    """Measure positive collinear overlap; crossings and shared points are not overlap."""
    if a.length <= tolerance or b.length <= tolerance:
        return 0.0
    ux = (a.p2.x - a.p1.x) / a.length
    uy = (a.p2.y - a.p1.y) / a.length
    projections = []
    for point in (b.p1, b.p2):
        dx, dy = point.x - a.p1.x, point.y - a.p1.y
        if abs(ux * dy - uy * dx) > tolerance:
            return 0.0
        projections.append(ux * dx + uy * dy)
    lo, hi = sorted(projections)
    length = min(a.length, hi) - max(0.0, lo)
    return length if length > tolerance else 0.0


def cut_fold_overlaps(cp):
    return [(cut, fold, overlap_length(cut, fold))
            for cut in cp.creases if cut.crease_type == CreaseType.CUT
            for fold in cp.creases if fold.crease_type in FOLDS
            if overlap_length(cut, fold) > 0.0]


class TestProductionGeometry(unittest.TestCase):
    def assert_cut_outline_is_closed(self, cp):
        graph = defaultdict(list)
        for cut in cp.creases:
            if cut.crease_type != CreaseType.CUT:
                continue
            self.assertGreater(cut.length, 1e-8)
            a = (round(cut.p1.x, 9), round(cut.p1.y, 9))
            b = (round(cut.p2.x, 9), round(cut.p2.y, 9))
            graph[a].append(b)
            graph[b].append(a)
        self.assertTrue(graph, "CUT outline must not be empty")
        self.assertTrue(all(len(edges) == 2 for edges in graph.values()),
                        "Every CUT vertex must have degree 2")
        seen, pending = set(), [next(iter(graph))]
        while pending:
            vertex = pending.pop()
            if vertex not in seen:
                seen.add(vertex)
                pending.extend(graph[vertex])
        self.assertEqual(len(seen), len(graph), "CUT must have one component")

    def test_tuck_cut_and_fold_do_not_overlap(self):
        # Positive control: a reversed partial fold lies inside an actual CUT.
        planted = generate_tuck_box()
        cut = next(c for c in planted.creases if c.crease_type == CreaseType.CUT)
        middle = Point2D((cut.p1.x + cut.p2.x) / 2, (cut.p1.y + cut.p2.y) / 2)
        planted.add_crease(cut.p2, middle, CreaseType.CREASE, label="PlantedOverlap")
        controls = [row for row in cut_fold_overlaps(planted) if row[1].label == "PlantedOverlap"]
        self.assertEqual(len(controls), 1)
        self.assertAlmostEqual(controls[0][2], cut.length / 2)
        for dimensions in ({}, {"width": 160, "depth": 110, "height": 110},
                           {"width": 32, "depth": 20, "height": 50, "thickness": 1.2}):
            with self.subTest(dimensions=dimensions):
                overlaps = cut_fold_overlaps(generate_tuck_box(**dimensions))
                self.assertEqual(overlaps, [],
                                 f"CUT/fold overlap totals {sum(row[2] for row in overlaps):.3f} mm")

    def test_overlap_detector_ignores_contacts_and_crossings(self):
        a = CreaseLine(Point2D(0, 0), Point2D(10, 0), CreaseType.CUT)
        for p1, p2 in [(Point2D(10, 0), Point2D(20, 0)),
                       (Point2D(5, -5), Point2D(5, 5)),
                       (Point2D(0, 1), Point2D(10, 1))]:
            with self.subTest(p1=p1, p2=p2):
                self.assertEqual(overlap_length(a, CreaseLine(p1, p2, CreaseType.CREASE)), 0)

    def test_tuck_cut_outline_is_closed(self):
        for dimensions in ({}, {"width": 160, "depth": 110, "height": 110},
                           {"width": 32, "depth": 20, "height": 50, "thickness": 1.2}):
            with self.subTest(dimensions=dimensions):
                self.assert_cut_outline_is_closed(generate_tuck_box(**dimensions))

    def test_tuck_body_hinges_cover_attached_flaps(self):
        cp = generate_tuck_box()
        allowance = cp.calculate_score_allowance(90)
        xs = [15.0]
        for dimension in (50.0, 80.0, 50.0, 80.0):
            xs.append(xs[-1] + dimension + allowance)
        for y, attached in ((0.0, (0, 1, 2)), (120.0, (0, 2, 3))):
            with self.subTest(y=y):
                hinges = [c for c in cp.creases if "Body" in c.label and c.p1.y == y]
                self.assertEqual([(c.p1.x, c.p2.x) for c in hinges],
                                 [(xs[i], xs[i + 1]) for i in attached])
                self.assertTrue(all(c.crease_type == CreaseType.CREASE and
                                    c.target_angle_deg == 90 and c.p2.y == y for c in hinges))

    def test_cut_outline_detector_rejects_open_or_disconnected_cuts(self):
        cp = generate_tuck_box()
        open_cp = copy.deepcopy(cp)
        open_cp.creases.remove(next(c for c in open_cp.creases if c.crease_type == CreaseType.CUT))
        with self.assertRaisesRegex(AssertionError, "degree 2"):
            self.assert_cut_outline_is_closed(open_cp)
        disconnected = copy.deepcopy(cp)
        square = [Point2D(1000, 1000), Point2D(1010, 1000),
                  Point2D(1010, 1010), Point2D(1000, 1010)]
        for a, b in zip(square, square[1:] + square[:1]):
            disconnected.add_crease(a, b, CreaseType.CUT)
        with self.assertRaisesRegex(AssertionError, "one component"):
            self.assert_cut_outline_is_closed(disconnected)


if __name__ == "__main__":
    unittest.main()
