"""Source-derived folded endpoint checks for the two-piece and food blanks."""
import math
import re
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from origami_cad.fold_faces import build_fold_model
from origami_cad.fold_kinematics import fold_vertices
from origami_cad.geometry import CreaseType
from origami_cad.packaging_food_box import generate_food_box
from origami_cad.packaging_sleeve_tray import generate_sleeve_tray
from origami_cad.printer_paths import bleed_outline, printer_paths
from origami_cad.printer_profile_export import export_printer_dxf, export_printer_pdf
from dieline_topology import crossing, violations
from test_printer_profile import dxf_entities, objects

from test_two_piece_food_styles import models, by_label, across, COUNTS, VARIANTS


class FoldAvailability(unittest.TestCase):
    def test_tree_hinged_blanks_qualify_with_expected_face_counts(self):
        for kwargs in VARIANTS:
            for name, cp in models(**kwargs).items():
                with self.subTest(blank=name, kwargs=kwargs):
                    model = build_fold_model(cp)
                    self.assertTrue(model["available"], model["status"])
                    self.assertEqual((len(model["faces"]), len(model["hinges"]), model["non_tree_folds"]),
                                     (COUNTS[name], COUNTS[name] - 1, []))
                    self.assertTrue(model["continuity"]["valid"])
                    self.assertGreater(model["continuity"]["checked_edges"], 0)
                    self.assertTrue(all(abs(p[2]) < 1e-9 for pts in fold_vertices(model, 0.0).values() for p in pts))
                    self.assertTrue(any(abs(p[2]) > 1 for pts in fold_vertices(model, 0.5).values() for p in pts))

    def test_folded_tray_tabs_lie_inside_the_long_walls(self):
        _, tray = generate_sleeve_tray()
        model, c = build_fold_model(tray), tray.calculate_score_allowance(90.0)
        floor_w, floor_d, h = 120 + c, 80 + c, 35.0
        folded = fold_vertices(model, 1.0)
        planes = {0.0: 0, floor_d: 0}
        for corner in ("LeftBack", "LeftFront", "RightBack", "RightFront"):
            end_wall = across(model, by_label(tray, "FloorHinge_" + corner.replace("Back", "").replace("Front", "")), model["root"])
            pts = folded[across(model, by_label(tray, f"TabHinge_{corner}"), end_wall["id"])["id"]]
            ys = {round(p[1], 6) for p in pts}
            self.assertEqual(len(ys), 1)                      # tab lies flat in one wall plane
            plane = next(k for k in planes if abs(k - next(iter(ys))) < 1e-6)
            planes[plane] += 1
            self.assertTrue(all(-1e-6 <= p[0] <= floor_w + 1e-6 and -h - 1e-6 <= p[2] <= 1e-6 for p in pts))
        self.assertEqual(planes, {0.0: 2, floor_d: 2})

    def test_folded_food_box_closes_lid_over_floor_and_tucks_front(self):
        cp = generate_food_box()
        model, c = build_fold_model(cp), cp.calculate_score_allowance(90.0)
        floor_w, floor_d, h = 160 + c, 120 + c, 70.0
        folded = fold_vertices(model, 1.0)
        back = across(model, by_label(cp, "FloorHinge_Back"), model["root"])
        lid = across(model, by_label(cp, "LidHinge"), back["id"])
        self.assertTrue(all(abs(p[2] + h) < 1e-6 and -1e-6 <= p[1] <= floor_d + 1e-6 for p in folded[lid["id"]]))
        tuck = across(model, by_label(cp, "TuckHinge"), lid["id"])
        for x, y, z in folded[tuck["id"]]:
            self.assertAlmostEqual(y, floor_d, places=6)      # tuck reaches the front wall plane
            self.assertTrue(-h - 1e-6 <= z <= 1e-6 and 0 < x < floor_w)
        for side in ("Left", "Right"):
            flap = across(model, by_label(cp, f"LidFlapHinge_{side}"), lid["id"])
            xs = {round(p[0], 6) for p in folded[flap["id"]]}
            self.assertEqual(len(xs), 1)
            self.assertTrue(0 < next(iter(xs)) < floor_w)     # flap hangs inside the end wall
            self.assertTrue(all(-h - 1e-6 <= p[2] <= 1e-6 for p in folded[flap["id"]]))


if __name__ == "__main__":
    unittest.main()
