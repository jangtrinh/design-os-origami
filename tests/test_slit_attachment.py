"""Owner-approved geometry and cut attachment regressions."""
import unittest
from origami_cad.packaging import generate_gable_handle_box
from origami_cad.geometry import Point2D, CreaseType
from test_production_dieline_topology import rectangle
from dieline_topology import violations


class SlitAttachment(unittest.TestCase):
    def test_declared_severing_slit_fails(self):
        cp = rectangle()
        cp.add_crease(Point2D(10, 0), Point2D(10, 20), CreaseType.CUT, label='Sever')
        cp.cut_slits = {'Sever': 'Alleged separation slit that actually cuts the blank in two.'}
        self.assertTrue(violations(cp)['cut_closed'])

    def test_two_attached_slits_that_join_and_sever_fail(self):
        cp = rectangle()
        cp.add_crease(Point2D(10, 0), Point2D(10, 10), CreaseType.CUT, label='Top')
        cp.add_crease(Point2D(10, 20), Point2D(10, 10), CreaseType.CUT, label='Bottom')
        cp.cut_slits = {'Top': 'top slit', 'Bottom': 'bottom slit'}
        self.assertTrue(violations(cp)['cut_closed'])
