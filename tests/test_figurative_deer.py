import math
import unittest

from origami_cad.figurative import generate_deer_bird_base
from origami_cad.geometry import CreaseType, Point2D


class TestDeerBirdBase(unittest.TestCase):
    def test_all_interior_vertices_flat_foldable(self):
        s = 200.0
        cp = generate_deer_bird_base(s)
        fold = (CreaseType.MOUNTAIN, CreaseType.VALLEY, CreaseType.CREASE)
        verts = {(round(p.x, 4), round(p.y, 4)) for c in cp.creases if c.crease_type in fold for p in (c.p1, c.p2)}
        checked = 0
        for x, y in verts:
            if min(x, y, s - x, s - y) < 1e-6:
                continue  # boundary vertex
            ok, msg = cp.validate_kawasaki_at_vertex(Point2D(x, y))
            self.assertTrue(ok, f"({x},{y}): {msg}")
            checked += 1
        self.assertGreaterEqual(checked, 9)

    def test_maekawa_at_every_interior_vertex(self):
        s = 200.0
        cp = generate_deer_bird_base(s)
        inc = {}
        for c in cp.creases:
            if c.crease_type in (CreaseType.MOUNTAIN, CreaseType.VALLEY):
                for p in (c.p1, c.p2):
                    inc.setdefault((round(p.x, 4), round(p.y, 4)), []).append(c.crease_type)
        for (x, y), types in inc.items():
            if min(x, y, s - x, s - y) < 1e-6:
                continue
            m = types.count(CreaseType.MOUNTAIN)
            v = types.count(CreaseType.VALLEY)
            self.assertEqual(abs(m - v), 2, f"({x},{y}) M={m} V={v}")

    def test_big_little_big_at_every_interior_vertex(self):
        """Regression: an earlier M/V assignment passed Maekawa but violated BLB at the 22.5 degree nodes."""
        import math
        s = 200.0
        cp = generate_deer_bird_base(s)
        inc = {}
        for c in cp.creases:
            if c.crease_type in (CreaseType.MOUNTAIN, CreaseType.VALLEY):
                for p, q in ((c.p1, c.p2), (c.p2, c.p1)):
                    inc.setdefault((round(p.x, 4), round(p.y, 4)), []).append(
                        (math.degrees(math.atan2(q.y - p.y, q.x - p.x)) % 360.0, c.crease_type))
        for (x, y), ring in inc.items():
            if min(x, y, s - x, s - y) < 1e-6:
                continue
            ring.sort(key=lambda t: t[0])
            n = len(ring)
            sec = [(ring[(i + 1) % n][0] - ring[i][0]) % 360.0 for i in range(n)]
            for i in range(n):
                if sec[i] < sec[i - 1] - 1e-6 and sec[i] < sec[(i + 1) % n] - 1e-6:
                    self.assertNotEqual(ring[i][1], ring[(i + 1) % n][1], f"BLB at ({x},{y})")

    def test_deer_base_has_no_unsplit_crossings(self):
        """Splitting at intersections must not change the fold-crease census of the generated pattern."""
        cp = generate_deer_bird_base(200.0)
        before = sum(1 for c in cp.creases if c.crease_type != CreaseType.CUT)
        cp.split_at_intersections()
        after = sum(1 for c in cp.creases if c.crease_type != CreaseType.CUT)
        self.assertEqual(before, after)
        self.assertEqual(before, 32)

    def test_solver_splits_unsplit_crossings_before_assigning(self):
        """Without the split, the unsplit X would be two creases and the centre vertex would never be constrained."""
        from origami_cad.geometry import OrigamiCreasePattern
        from origami_cad.figurative import _assign_maekawa_mountain_valley
        cp = OrigamiCreasePattern("X")
        # 4 creases through (10,10) given as 2 unsplit lines, plus 45 degree lines so the centre has degree 8
        for a, b in [((0, 10), (20, 10)), ((10, 0), (10, 20)), ((0, 0), (20, 20)), ((0, 20), (20, 0))]:
            cp.add_crease(Point2D(*a), Point2D(*b), CreaseType.CREASE)
        _assign_maekawa_mountain_valley(cp, 20.0)
        folds = [c for c in cp.creases if c.crease_type in (CreaseType.MOUNTAIN, CreaseType.VALLEY)]
        self.assertEqual(len(folds), 8)
        m = sum(1 for c in folds if c.crease_type == CreaseType.MOUNTAIN)
        self.assertEqual(abs(m - (len(folds) - m)), 2)


if __name__ == "__main__":
    unittest.main()
