"""Owner-approved geometry and cut attachment regressions."""
import unittest
from origami_cad.packaging import generate_gable_handle_box
from origami_cad.geometry import Point2D, CreaseType
from test_production_dieline_topology import rectangle
from dieline_topology import violations


class Followups(unittest.TestCase):
    def test_gable_dust_flaps_on_flap_side_for_all_proportions(self):
        for height, depth in [(300, 60), (110, 110), (30, 100)]:
            cp = generate_gable_handle_box(height=height, depth=depth)
            # Four sloped dust-flap sides originate at body-bottom hinges.
            dust = [c for c in cp.creases if c.crease_type == CreaseType.CUT
                    and abs(c.p1.y-height) < 1e-8 and abs(c.p2.x-c.p1.x-8) < 1e-8]
            self.assertEqual(len(dust), 2)
            for c in dust:
                self.assertAlmostEqual(c.p2.y-height, (depth+cp.calculate_score_allowance(90))*0.65*0.8)
                self.assertGreater(c.p2.y, height)
            self.assertFalse(any(violations(cp).values()))
