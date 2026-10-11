"""Tests for Creative Origami Packaging Catalog generators."""

import unittest
from pathlib import Path
import tempfile

from origami_cad.packaging import (
    generate_hexagonal_petal_box,
    generate_diamond_faceted_box,
    generate_zero_glue_tray,
)
from origami_cad.dieline_export import export_svg, export_dxf
from origami_cad.geometry import CreaseType


class TestCreativeCatalog(unittest.TestCase):

    def test_hexagonal_petal_box(self):
        cp = generate_hexagonal_petal_box(radius=45.0, height=60.0, thickness=0.4)
        self.assertEqual(len(cp.facets), 1)
        self.assertGreater(len(cp.creases), 18)

        # Check that CUT and CREASE lines are segregated
        cuts = [c for c in cp.creases if c.crease_type == CreaseType.CUT]
        creases = [c for c in cp.creases if c.crease_type == CreaseType.CREASE]
        self.assertGreater(len(cuts), 6)
        self.assertGreater(len(creases), 6)

    def test_diamond_faceted_box(self):
        cp = generate_diamond_faceted_box(width=50.0, height=80.0, facets=4, thickness=0.45)
        self.assertGreater(len(cp.creases), 15)

        # Mountain and valley folds
        mountains = [c for c in cp.creases if c.crease_type == CreaseType.MOUNTAIN]
        valleys = [c for c in cp.creases if c.crease_type == CreaseType.VALLEY]
        self.assertGreater(len(mountains), 0)
        self.assertGreater(len(valleys), 0)

    def test_zero_glue_tray(self):
        cp = generate_zero_glue_tray(width=100.0, depth=70.0, wall_height=30.0, thickness=0.5)
        self.assertGreater(len(cp.creases), 16)

        # Gusset valley folds present
        gussets = [c for c in cp.creases if c.label == "CornerGusset"]
        self.assertEqual(len(gussets), 4)

        with tempfile.TemporaryDirectory() as tmp_dir:
            svg_p = Path(tmp_dir) / "tray.svg"
            dxf_p = Path(tmp_dir) / "tray.dxf"
            export_svg(cp, str(svg_p))
            export_dxf(cp, str(dxf_p))
            self.assertTrue(svg_p.exists())
            self.assertTrue(dxf_p.exists())

    def test_gable_handle_box(self):
        from origami_cad.packaging import generate_gable_handle_box
        cp = generate_gable_handle_box(width=160.0, depth=110.0, height=110.0, thickness=0.5)
        self.assertGreater(len(cp.creases), 25)

        # Check handle slots present
        slots = [c for c in cp.creases if "Slot" in c.label]
        self.assertGreater(len(slots), 6)

        # Check triangular gusset creases present
        gussets = [c for c in cp.creases if "Gusset" in c.label]
        self.assertGreater(len(gussets), 4)


if __name__ == "__main__":
    unittest.main()
