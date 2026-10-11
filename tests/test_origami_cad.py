"""Unit tests for Origami CAD & Packaging Engineering."""

import unittest
from pathlib import Path
import tempfile

from origami_cad.geometry import OrigamiCreasePattern, Point2D, CreaseType
from origami_cad.packaging import generate_tuck_box, generate_miura_ori_sleeve
from origami_cad.dieline_export import export_svg, export_dxf
from origami_cad.viewer_html import generate_viewer_html


class TestOrigamiCAD(unittest.TestCase):

    def test_score_allowance(self):
        cp = OrigamiCreasePattern("TestBox", thickness_mm=0.6)
        allowance = cp.calculate_score_allowance(90.0, k_factor=0.45)
        self.assertAlmostEqual(allowance, 0.27, places=2)

    def test_kawasaki_theorem_verification(self):
        cp = OrigamiCreasePattern("KawasakiTest")
        center = Point2D(50.0, 50.0)

        # 4 creases with sector angles: 60°, 110°, 120°, 70°
        # Alternating sum: (60 + 120) = 180°, (110 + 70) = 180° (Satisfies Kawasaki)
        # Angles: 0°, 60°, 170°, 290°
        import math
        r = 50.0
        for ang_deg in [0.0, 60.0, 170.0, 290.0]:
            rad = math.radians(ang_deg)
            target = Point2D(center.x + r * math.cos(rad), center.y + r * math.sin(rad))
            cp.add_crease(center, target, CreaseType.CREASE)

        passed, msg = cp.validate_kawasaki_at_vertex(center)
        self.assertTrue(passed, f"Expected Kawasaki condition to pass: {msg}")

    def test_tuck_box_generation_and_export(self):
        cp = generate_tuck_box(width=80.0, depth=50.0, height=120.0, thickness=0.5)
        self.assertGreater(len(cp.creases), 15)
        self.assertGreater(len(cp.facets), 4)

        with tempfile.TemporaryDirectory() as tmp_dir:
            svg_path = Path(tmp_dir) / "test_box.svg"
            dxf_path = Path(tmp_dir) / "test_box.dxf"
            html_path = Path(tmp_dir) / "test_viewer.html"

            svg_str = export_svg(cp, str(svg_path))
            dxf_str = export_dxf(cp, str(dxf_path))
            html_str = generate_viewer_html(cp, str(html_path))

            self.assertTrue(svg_path.exists())
            self.assertTrue(dxf_path.exists())
            self.assertTrue(html_path.exists())

            # Verify CAD layers in SVG
            self.assertIn('id="CUT"', svg_str)
            self.assertIn('id="CREASE"', svg_str)
            self.assertIn('id="GLUE"', svg_str)

            # Verify DXF R12 Header and Layers
            self.assertIn("AC1009", dxf_str)
            self.assertIn("CUT", dxf_str)
            self.assertIn("CREASE", dxf_str)

    def test_miura_ori_generation(self):
        cp = generate_miura_ori_sleeve(cell_w=20.0, cell_h=15.0, rows=3, cols=4)
        self.assertGreater(len(cp.creases), 20)
        min_x, min_y, max_x, max_y = cp.bounding_box()
        self.assertGreater(max_x, min_x)
        self.assertGreater(max_y, min_y)


if __name__ == "__main__":
    unittest.main()
