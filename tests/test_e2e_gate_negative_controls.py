import importlib.util
import math
import unittest
from pathlib import Path

from origami_cad.geometry import CreaseType, OrigamiCreasePattern, Point2D

_spec = importlib.util.spec_from_file_location(
    "e2e_gate", Path(__file__).resolve().parents[1] / "scripts" / "e2e_figurative_gate.py")
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


def _vertex(angles_types):
    cp = OrigamiCreasePattern("neg")
    c = Point2D(0.0, 0.0)
    for a, t in angles_types:
        r = math.radians(a)
        cp.add_crease(c, Point2D(10 * math.cos(r), 10 * math.sin(r)), t)
    return cp, c


V, M = CreaseType.VALLEY, CreaseType.MOUNTAIN


class TestGateNegativeControls(unittest.TestCase):
    def test_four_valleys_fail_maekawa(self):
        cp, c = _vertex([(0, V), (90, V), (180, V), (270, V)])
        maekawa, _ = gate.maekawa_and_blb(cp, c)
        self.assertFalse(maekawa)

    def test_equal_sign_around_smallest_sector_fails_blb_but_passes_maekawa(self):
        # sectors 45, 90, 135, 90 (Kawasaki ok); creases bounding the 45 sector have equal sign
        cp, c = _vertex([(0, M), (45, M), (135, M), (270, V)])
        maekawa, blb = gate.maekawa_and_blb(cp, c)
        self.assertTrue(maekawa)
        self.assertFalse(blb)

    def test_opposite_sign_around_smallest_sector_passes_blb(self):
        cp, c = _vertex([(0, M), (45, V), (135, M), (270, M)])
        maekawa, blb = gate.maekawa_and_blb(cp, c)
        self.assertTrue(maekawa)
        self.assertTrue(blb)


if __name__ == "__main__":
    unittest.main()
