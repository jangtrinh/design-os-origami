import unittest

from origami_cad.geometry import CreaseType, OrigamiCreasePattern, Point2D


def _fold_count(cp):
    return sum(1 for c in cp.creases if c.crease_type != CreaseType.CUT)


class TestSplitAtIntersections(unittest.TestCase):
    def test_x_crossing_is_split_into_four_rays(self):
        cp = OrigamiCreasePattern("X")
        cp.add_crease(Point2D(-10, 0), Point2D(10, 0), CreaseType.VALLEY)
        cp.add_crease(Point2D(0, -10), Point2D(0, 10), CreaseType.MOUNTAIN)
        cp.split_at_intersections()
        self.assertEqual(_fold_count(cp), 4)
        self.assertEqual(sorted(c.crease_type.value for c in cp.creases), ["MOUNTAIN"] * 2 + ["VALLEY"] * 2)

    def test_t_junction_splits_only_the_through_crease(self):
        cp = OrigamiCreasePattern("T")
        cp.add_crease(Point2D(-10, 0), Point2D(10, 0), CreaseType.VALLEY)
        cp.add_crease(Point2D(0, 0), Point2D(0, 10), CreaseType.MOUNTAIN)
        cp.split_at_intersections()
        self.assertEqual(_fold_count(cp), 3)

    def test_already_split_pattern_is_unchanged(self):
        cp = OrigamiCreasePattern("Split")
        for a, b in [((-10, 0), (0, 0)), ((0, 0), (10, 0)), ((0, -10), (0, 0)), ((0, 0), (0, 10))]:
            cp.add_crease(Point2D(*a), Point2D(*b), CreaseType.VALLEY)
        cp.split_at_intersections()
        self.assertEqual(_fold_count(cp), 4)

    def test_verdict_is_identical_for_unsplit_and_split_input(self):
        center = Point2D(0, 0)
        unsplit = OrigamiCreasePattern("U")
        unsplit.add_crease(Point2D(-10, 0), Point2D(10, 0), CreaseType.VALLEY)
        unsplit.add_crease(Point2D(0, -10), Point2D(0, 10), CreaseType.VALLEY)
        unsplit.split_at_intersections()
        explicit = OrigamiCreasePattern("E")
        for a, b in [((-10, 0), (0, 0)), ((0, 0), (10, 0)), ((0, -10), (0, 0)), ((0, 0), (0, 10))]:
            explicit.add_crease(Point2D(*a), Point2D(*b), CreaseType.VALLEY)
        self.assertEqual(unsplit.validate_kawasaki_at_vertex(center)[0], explicit.validate_kawasaki_at_vertex(center)[0])

    def test_parallel_and_disjoint_creases_are_untouched(self):
        cp = OrigamiCreasePattern("P")
        cp.add_crease(Point2D(0, 0), Point2D(10, 0), CreaseType.VALLEY)
        cp.add_crease(Point2D(0, 5), Point2D(10, 5), CreaseType.VALLEY)
        cp.split_at_intersections()
        self.assertEqual(_fold_count(cp), 2)

    def test_overlapping_collinear_folds_raise(self):
        cp = OrigamiCreasePattern("Overlap")
        cp.add_crease(Point2D(0, 0), Point2D(10, 0), CreaseType.VALLEY)
        cp.add_crease(Point2D(5, 0), Point2D(15, 0), CreaseType.VALLEY)
        with self.assertRaises(ValueError):
            cp.split_at_intersections()

    def test_end_to_end_collinear_neighbours_are_allowed(self):
        cp = OrigamiCreasePattern("Neighbours")
        cp.add_crease(Point2D(0, 0), Point2D(10, 0), CreaseType.VALLEY)
        cp.add_crease(Point2D(10, 0), Point2D(20, 0), CreaseType.VALLEY)
        cp.split_at_intersections()
        self.assertEqual(_fold_count(cp), 2)

    def test_glue_and_perforate_are_not_split_or_changed(self):
        cp = OrigamiCreasePattern("Layers")
        cp.add_crease(Point2D(-10, 0), Point2D(10, 0), CreaseType.VALLEY)
        cp.add_crease(Point2D(0, -10), Point2D(0, 10), CreaseType.GLUE)
        cp.add_crease(Point2D(-5, -5), Point2D(5, 5), CreaseType.PERFORATE)
        cp.split_at_intersections()
        types = sorted(c.crease_type.value for c in cp.creases)
        self.assertEqual(types, ["GLUE", "PERFORATE", "VALLEY"])

    def test_metadata_is_preserved_on_pieces(self):
        cp = OrigamiCreasePattern("Meta")
        cp.add_crease(Point2D(-10, 0), Point2D(10, 0), CreaseType.VALLEY, -180.0, "Hinge")
        cp.add_crease(Point2D(0, -10), Point2D(0, 10), CreaseType.MOUNTAIN, 180.0, "Axis")
        cp.split_at_intersections()
        for c in cp.creases:
            self.assertIn(c.label, ("Hinge", "Axis"))
            self.assertEqual(abs(c.target_angle_deg), 180.0)

    def test_three_creases_through_one_point(self):
        cp = OrigamiCreasePattern("Triple")
        cp.add_crease(Point2D(-10, 0), Point2D(10, 0), CreaseType.VALLEY)
        cp.add_crease(Point2D(0, -10), Point2D(0, 10), CreaseType.VALLEY)
        cp.add_crease(Point2D(-10, -10), Point2D(10, 10), CreaseType.VALLEY)
        cp.split_at_intersections()
        self.assertEqual(_fold_count(cp), 6)


if __name__ == "__main__":
    unittest.main()
