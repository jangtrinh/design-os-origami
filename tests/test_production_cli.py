"""Real CLI regressions for explicit dimension ownership and omitted defaults."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from origami_cad.dieline_export import export_dxf, export_svg
from origami_cad.figurative import generate_deer_bird_base
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

ROOT = Path(__file__).resolve().parents[1]
MODELS = {
    "tuck-box": (generate_tuck_box, {}),
    "miura-ori": (generate_miura_ori_sleeve, {}),
    "hex-petal": (generate_hexagonal_petal_box, {"thickness": 0.5}),
    "diamond-box": (generate_diamond_faceted_box, {"width": 50.0, "thickness": 0.5}),
    "zero-glue-tray": (generate_zero_glue_tray, {}),
    "gable-box": (generate_gable_handle_box, {}),
    "pillow-box": (generate_pillow_box, {"height": 110.0}),
    "crash-lock-box": (generate_crash_lock_box, {}),
    "deer-base": (generate_deer_bird_base, {}),
}


class TestProductionCLI(unittest.TestCase):
    def assert_cli_geometry(self, model, cp, *flags):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, PYTHONPATH=str(ROOT / "src"),
                       PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run(
                [sys.executable, "-m", "origami_cad.cli", "generate",
                 "--type", model, "--output-dir", tmp, *flags],
                cwd=ROOT, env=env, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"Generated Origami CAD Model: {cp.name}\n", result.stdout)
            root = Path(tmp)
            self.assertEqual((root / f"{cp.name}.svg").read_text(),
                             export_svg(cp, str(root / "expected.svg")))
            self.assertEqual((root / f"{cp.name}.dxf").read_text(),
                             export_dxf(cp, str(root / "expected.dxf")))
            self.assertTrue((root / f"{cp.name}_viewer.html").is_file())

    def test_explicit_tuck_dimensions_are_preserved(self):
        cases = [
            ({"width": 160.0}, ["--width", "160"]),
            ({"depth": 110.0}, ["--depth", "110"]),
            ({"height": 110.0}, ["--height", "110"]),
            ({"width": 160.0, "depth": 110.0, "height": 110.0},
             ["--width", "160", "--depth", "110", "--height", "110"]),
        ]
        for dimensions, flags in cases:
            with self.subTest(dimensions=dimensions):
                self.assert_cli_geometry("tuck-box", generate_tuck_box(**dimensions), *flags)

    def test_tray_height_is_preserved(self):
        for height in (41.25, 110.0):
            with self.subTest(height=height):
                self.assert_cli_geometry(
                    "zero-glue-tray", generate_zero_glue_tray(wall_height=height),
                    "--height", str(height),
                )

    def test_explicit_model_dimensions_are_preserved(self):
        cases = [
            ("hex-petal", {"height": 110.0}, ["--height", "110"]),
            ("diamond-box", {"width": 160.0, "height": 110.0},
             ["--width", "160", "--height", "110"]),
            ("zero-glue-tray", {"width": 160.0, "depth": 110.0},
             ["--width", "160", "--depth", "110"]),
            ("pillow-box", {"width": 160.0, "depth": 110.0, "height": 110.0},
             ["--width", "160", "--depth", "110"]),
            ("crash-lock-box", {"width": 160.0, "depth": 110.0, "height": 110.0},
             ["--width", "160", "--depth", "110", "--height", "110"]),
            ("deer-base", {"size": 160.0}, ["--width", "160"]),
        ]
        for model, dimensions, flags in cases:
            with self.subTest(model=model):
                generator, defaults = MODELS[model]
                self.assert_cli_geometry(model, generator(**{**defaults, **dimensions}), *flags)

    def test_omitted_dimensions_keep_model_defaults(self):
        for model, (generator, dimensions) in MODELS.items():
            with self.subTest(model=model):
                self.assert_cli_geometry(model, generator(**dimensions))


if __name__ == "__main__":
    unittest.main()
