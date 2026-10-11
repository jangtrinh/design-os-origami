"""Interior vertices of degree < 4 must not be reported flat-foldable unless trivially so."""

import unittest

from origami_cad.geometry import CreaseType, OrigamiCreasePattern, Point2D


def _star(cp, center, angles_deg, r=10.0, kind=CreaseType.VALLEY):
    import math
    for a in angles_deg:
        rad = math.radians(a)
        cp.add_crease(center, Point2D(center.x + r * math.cos(rad), center.y + r * math.sin(rad)), kind)


class TestLowDegreeVertices(unittest.TestCase):
    def test_interior_degree_three_is_rejected(self):
        cp = OrigamiCreasePattern("Deg3")
        c = Point2D(0.0, 0.0)
        _star(cp, c, [0, 120, 240])
        ok, msg = cp.validate_kawasaki_at_vertex(c)
        self.assertFalse(ok, msg)

    def test_interior_dead_end_crease_is_rejected(self):
        cp = OrigamiCreasePattern("Deg1")
        c = Point2D(0.0, 0.0)
        _star(cp, c, [0])
        ok, msg = cp.validate_kawasaki_at_vertex(c)
        self.assertFalse(ok, msg)

    def test_interior_straight_line_is_accepted(self):
        cp = OrigamiCreasePattern("Deg2Straight")
        c = Point2D(0.0, 0.0)
        _star(cp, c, [0, 180])
        ok, msg = cp.validate_kawasaki_at_vertex(c)
        self.assertTrue(ok, msg)

    def test_interior_kinked_line_is_rejected(self):
        cp = OrigamiCreasePattern("Deg2Kink")
        c = Point2D(0.0, 0.0)
        _star(cp, c, [0, 120])
        ok, msg = cp.validate_kawasaki_at_vertex(c)
        self.assertFalse(ok, msg)

    def test_boundary_degree_three_stays_accepted(self):
        cp = OrigamiCreasePattern("BoundaryDeg3")
        c = Point2D(0.0, 0.0)
        # sheet edge along x axis (cut), three fold creases fanning into the sheet
        cp.add_crease(Point2D(-10.0, 0.0), Point2D(10.0, 0.0), CreaseType.CUT)
        _star(cp, c, [45, 90, 135])
        ok, msg = cp.validate_kawasaki_at_vertex(c)
        self.assertTrue(ok, msg)

    def test_degree_two_respects_tolerance_argument(self):
        cp = OrigamiCreasePattern("Deg2Tol")
        c = Point2D(0.0, 0.0)
        _star(cp, c, [0, 179.75])
        self.assertTrue(cp.validate_kawasaki_at_vertex(c, tolerance_deg=0.5)[0])
        self.assertFalse(cp.validate_kawasaki_at_vertex(c, tolerance_deg=0.1)[0])
        cp2 = OrigamiCreasePattern("Deg2TolWide")
        _star(cp2, c, [0, 179.0])
        self.assertTrue(cp2.validate_kawasaki_at_vertex(c, tolerance_deg=2.0)[0])
        self.assertFalse(cp2.validate_kawasaki_at_vertex(c, tolerance_deg=0.5)[0])

    def test_empty_interior_vertex_is_accepted(self):
        cp = OrigamiCreasePattern("Empty")
        self.assertTrue(cp.validate_kawasaki_at_vertex(Point2D(5.0, 5.0))[0])

    def test_through_crease_equals_split_crease(self):
        """A crease passing through the vertex must count as two rays, same as two split creases."""
        c = Point2D(0.0, 0.0)
        split = OrigamiCreasePattern("Split")
        split.add_crease(Point2D(-10.0, 0.0), c, CreaseType.VALLEY)
        split.add_crease(c, Point2D(10.0, 0.0), CreaseType.VALLEY)
        through = OrigamiCreasePattern("Through")
        through.add_crease(Point2D(-10.0, 0.0), Point2D(10.0, 0.0), CreaseType.VALLEY)
        self.assertTrue(split.validate_kawasaki_at_vertex(c)[0])
        self.assertTrue(through.validate_kawasaki_at_vertex(c)[0])

    def test_through_crease_plus_rays_matches_split_for_degree_four(self):
        import math
        c = Point2D(0.0, 0.0)
        results = []
        for through in (False, True):
            cp = OrigamiCreasePattern("T%s" % through)
            if through:
                cp.add_crease(Point2D(-10.0, 0.0), Point2D(10.0, 0.0), CreaseType.VALLEY)
            else:
                cp.add_crease(Point2D(-10.0, 0.0), c, CreaseType.VALLEY)
                cp.add_crease(c, Point2D(10.0, 0.0), CreaseType.VALLEY)
            for a in (60.0, 300.0):
                r = math.radians(a)
                cp.add_crease(c, Point2D(10.0 * math.cos(r), 10.0 * math.sin(r)), CreaseType.VALLEY)
            results.append(cp.validate_kawasaki_at_vertex(c))
        self.assertEqual(results[0][0], results[1][0])
        self.assertTrue(results[1][0], results[1][1])


if __name__ == "__main__":
    unittest.main()
