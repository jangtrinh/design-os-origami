import tempfile
import unittest
from pathlib import Path

from origami_cad.figurative import generate_deer_bird_base
from origami_cad.packaging import generate_gable_handle_box, generate_tuck_box
from origami_cad.viewer_html import generate_viewer_html


def _html(cp):
    with tempfile.TemporaryDirectory() as tmp:
        return generate_viewer_html(cp, str(Path(tmp) / "v.html"))


class TestViewerHonesty(unittest.TestCase):
    def test_no_hardcoded_verified_badge_or_fixed_kawasaki_sum(self):
        for cp in (generate_deer_bird_base(200.0), generate_tuck_box(), generate_gable_handle_box()):
            html = _html(cp)
            self.assertNotIn("UKMC.v1 Verified", html)
            self.assertNotIn("180.00° / 180.00°", html)

    def test_reports_interior_and_boundary_separately(self):
        # The redesign removes telemetry; unsupported deer must never imply certification.
        from test_viewer_real_fold import model_from
        html = _html(generate_deer_bird_base(200.0))
        model = model_from(html)
        self.assertFalse(model['available'])
        self.assertEqual(model['faces'], [])
        self.assertEqual(model['status'], '3D fold preview not available for this pattern')

    def test_failing_pattern_is_reported_as_failing(self):
        from origami_cad.geometry import CreaseType, OrigamiCreasePattern, Point2D
        cp = OrigamiCreasePattern("Bad")
        c = Point2D(0, 0)
        for x, y in [(10, 0), (-5, 8), (-5, -8)]:  # interior degree 3 cannot fold flat
            cp.add_crease(c, Point2D(x, y), CreaseType.VALLEY)
        from test_viewer_real_fold import model_from
        html = _html(cp)
        self.assertFalse(model_from(html)['available'])
        self.assertIn('3D fold preview not available for this pattern', html)

    def test_3d_preview_disclosure_for_every_model(self):
        from origami_cad.fold_faces import build_fold_model
        from test_viewer_real_fold import model_from
        self.assertFalse(model_from(_html(generate_deer_bird_base(200.0)))['available'])
        cp = generate_gable_handle_box()
        self.assertEqual(model_from(_html(cp)), build_fold_model(cp))
        self.assertNotIn('mockup', _html(cp))

    def test_no_uncomputed_standard_claims(self):
        html = _html(generate_deer_bird_base(200.0))
        self.assertNotIn("ISO/ECMA", html)


if __name__ == "__main__":
    unittest.main()
