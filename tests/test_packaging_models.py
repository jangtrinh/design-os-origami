"""Smoke + geometry tests for every packaging model generator."""

import tempfile
import unittest
from pathlib import Path

from origami_cad.dieline_export import export_dxf, export_svg
from origami_cad.geometry import CreaseType
from origami_cad.packaging import (
    generate_crash_lock_box,
    generate_diamond_faceted_box,
    generate_gable_handle_box,
    generate_hexagonal_petal_box,
    generate_miura_ori_sleeve,
    generate_pillow_box,
    generate_tuck_box,
    generate_zero_glue_tray,
)
from origami_cad.viewer_html import generate_viewer_html

MODELS = {
    "tuck-box": generate_tuck_box,
    "miura-ori": generate_miura_ori_sleeve,
    "hex-petal": generate_hexagonal_petal_box,
    "diamond-box": generate_diamond_faceted_box,
    "zero-glue-tray": generate_zero_glue_tray,
    "gable-box": generate_gable_handle_box,
    "pillow-box": generate_pillow_box,
    "crash-lock-box": generate_crash_lock_box,
}


class TestPackagingModels(unittest.TestCase):
    def test_every_model_generates_and_exports(self):
        for name, gen in MODELS.items():
            with self.subTest(model=name), tempfile.TemporaryDirectory() as tmp:
                cp = gen()
                self.assertGreater(len(cp.creases), 4)
                min_x, min_y, max_x, max_y = cp.bounding_box()
                self.assertGreater(max_x - min_x, 0)
                self.assertGreater(max_y - min_y, 0)
                svg = export_svg(cp, str(Path(tmp) / "a.svg"))
                dxf = export_dxf(cp, str(Path(tmp) / "a.dxf"))
                html = generate_viewer_html(cp, str(Path(tmp) / "a.html"))
                self.assertIn('id="CUT"', svg)
                self.assertIn("AC1009", dxf)
                self.assertGreater(len(html), 1000)

    def test_new_models_have_cut_and_fold_lines(self):
        for gen in (generate_pillow_box, generate_crash_lock_box):
            cp = gen()
            types = {c.crease_type for c in cp.creases}
            self.assertIn(CreaseType.CUT, types)
            self.assertIn(CreaseType.CREASE, types)

    def test_pillow_box_scales_with_dimensions(self):
        small = generate_pillow_box(width=60, depth=30, height=80).bounding_box()
        big = generate_pillow_box(width=120, depth=60, height=80).bounding_box()
        self.assertGreater(big[2] - big[0], small[2] - small[0])

    def test_crash_lock_diagonals_within_flap(self):
        cp = generate_crash_lock_box(width=80, depth=60, height=100)
        _, _, _, max_y = cp.bounding_box()
        for c in cp.creases:
            if c.label == "LockDiag":
                self.assertLessEqual(max(c.p1.y, c.p2.y), max_y + 1e-6)
                self.assertAlmostEqual(abs(c.p2.x - c.p1.x), abs(c.p2.y - c.p1.y), places=6)

    def test_crash_lock_glue_flap_is_outlined(self):
        labels = {c.label for c in generate_crash_lock_box().creases}
        self.assertIn("GlueFlapTop", labels)
        self.assertIn("GlueFlapBottom", labels)


if __name__ == "__main__":
    unittest.main()
