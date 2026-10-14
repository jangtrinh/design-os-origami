"""Sleeve+tray two-piece and hinged-lid food box: semantics, topology, printer, fold."""
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

FOLDS = {CreaseType.CREASE, CreaseType.MOUNTAIN, CreaseType.VALLEY}
VARIANTS = [{}, {"width": 30, "depth": 200, "height": 12, "thickness": 0.6},  # narrow, deep, low
            {"width": 400, "depth": 24, "height": 90, "thickness": 1.5},      # wide, shallow, tall
            {"width": 60, "depth": 60, "height": 60, "thickness": 0.0},       # cube, zero caliper
            {"width": 9, "depth": 7, "height": 4, "thickness": 0.3}]          # tiny
INVALID = [{"width": 0}, {"depth": -5}, {"height": float("nan")}, {"width": float("inf")},
           {"thickness": -0.1}, {"fit_clearance": -1}, {"height": 0.5, "thickness": 0.5},
           {"width": 0.5, "thickness": 0.5}]
COUNTS = {"sleeve": 5, "tray": 9, "food-box": 13}


def by_label(cp, label):
    found = [c for c in cp.creases if c.label == label]
    assert len(found) == 1, (label, len(found))
    return found[0]


def models(**kwargs):
    sleeve_options = dict(kwargs)
    if kwargs.get("height", 35) < 15:
        sleeve_options["glue_flap_width"] = 5.0  # explicit compatible seam for short-wall fixtures
    sleeve, tray = generate_sleeve_tray(**sleeve_options)
    return {"sleeve": sleeve, "tray": tray, "food-box": generate_food_box(**kwargs)}


def across(model, crease, parent):
    """The face on the far side of a hinge from its known parent face."""
    ends = {(round(p.x, 6), round(p.y, 6)) for p in (crease.p1, crease.p2)}
    return next(f for f in model["faces"] if f["id"] != parent
                and ends <= {(round(x, 6), round(y, 6)) for x, y in f["vertices"]})


def distance(p, a, b):
    dx, dy = b.x - a.x, b.y - a.y
    t = max(0, min(1, ((p.x - a.x) * dx + (p.y - a.y) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p.x - a.x - t * dx, p.y - a.y - t * dy)


class ApiContract(unittest.TestCase):
    def test_sleeve_tray_returns_two_distinctly_named_blanks(self):
        result = generate_sleeve_tray()
        self.assertIsInstance(result, tuple)
        self.assertEqual([cp.name for cp in result], ["TwoPieceSleeve_120x80x35", "TwoPieceTray_120x80x35"])
        self.assertEqual(generate_food_box().name, "FoodBoxHingedLid_160x120x70")

    def test_invalid_arguments_are_rejected(self):
        for kwargs in INVALID:
            for generator in (generate_sleeve_tray, generate_food_box):
                with self.subTest(generator=generator.__name__, kwargs=kwargs), self.assertRaises(ValueError):
                    generator(**kwargs)


class Semantics(unittest.TestCase):
    def test_sleeve_band_uses_formula_allowance_and_fit_clearance(self):
        sleeve, tray = generate_sleeve_tray(width=120, depth=80, height=35, thickness=0.5, fit_clearance=1.0)
        c = sleeve.calculate_score_allowance(90.0)
        self.assertAlmostEqual(c, 0.225)
        hinges = [by_label(sleeve, "SleeveHinge_" + n) for n in ("GlueTop", "TopSide", "SideBottom", "BottomSide")]
        xs = [h.p1.x for h in hinges]
        panel_w, panel_h = 120 + 2 * 0.5 + 2 * 1.0 + c, 35 + 0.5 + 2 * 1.0 + c
        self.assertAlmostEqual(xs[1] - xs[0], panel_w)
        self.assertAlmostEqual(xs[2] - xs[1], panel_h)
        self.assertAlmostEqual(xs[3] - xs[2], panel_w)
        ys = [c.p1.y for c in sleeve.creases]
        self.assertAlmostEqual(max(ys) - min(ys), 80 + 2 * 0.5)
        self.assertTrue(all(h.crease_type == CreaseType.CREASE and h.target_angle_deg == 90 for h in hinges))
        labels = {c.label for c in sleeve.creases}
        self.assertTrue({"SleeveGlue", "ThumbNotch"} <= labels)
        # Tray outer cross-section fits inside the sleeve with the stated clearance per side.
        self.assertAlmostEqual(panel_w - (by_label(tray, "FloorHinge_Back").length + 2 * 0.5), 2 * 1.0)

    def test_tray_walls_attach_to_floor_with_corner_tabs_and_declared_slits(self):
        _, tray = generate_sleeve_tray()
        c = tray.calculate_score_allowance(90.0)
        for side, length in (("Back", 120 + c), ("Right", 80 + c), ("Front", 120 + c), ("Left", 80 + c)):
            hinge = by_label(tray, f"FloorHinge_{side}")
            self.assertAlmostEqual(hinge.length, length)
            self.assertEqual((hinge.crease_type, hinge.target_angle_deg), (CreaseType.CREASE, 90.0))
        for corner in ("LeftBack", "LeftFront", "RightBack", "RightFront"):
            hinge, slit = by_label(tray, f"TabHinge_{corner}"), by_label(tray, f"TabSlit_{corner}")
            self.assertAlmostEqual(hinge.length, 35.0)       # tab hinge spans the wall height
            self.assertEqual(slit.crease_type, CreaseType.CUT)
            self.assertIn(f"TabSlit_{corner}", tray.cut_slits)
            self.assertLess(slit.length, 35.0)                # relief keeps the tab below the wall top
        self.assertEqual(len(tray.cut_slits), 4)

    def test_food_box_lid_is_hinged_on_back_wall_with_side_flaps_and_tuck(self):
        cp = generate_food_box(width=160, depth=120, height=70, thickness=0.5, fit_clearance=1.0)
        c = cp.calculate_score_allowance(90.0)
        back, lid, tuck = by_label(cp, "FloorHinge_Back"), by_label(cp, "LidHinge"), by_label(cp, "TuckHinge")
        self.assertAlmostEqual(lid.p1.y, back.p1.y - 70)                 # on the back wall's top edge
        self.assertAlmostEqual(lid.length, (160 + c) - 2 * (0.5 + 1.0))  # inset so flaps go inside
        self.assertAlmostEqual(lid.p1.y - tuck.p1.y, 120 + c)            # lid spans the formula depth
        for side in ("Left", "Right"):
            self.assertAlmostEqual(by_label(cp, f"LidFlapHinge_{side}").length, 120 + c)
            self.assertIn(f"LidFlapSlit_{side}", cp.cut_slits)
        self.assertEqual(len(cp.cut_slits), 6)
        self.assertEqual(sum(c.crease_type in FOLDS for c in cp.creases), 12)
        self.assertEqual(sum(c.label.startswith("TuckFlap") for c in cp.creases), 3)


class Topology(unittest.TestCase):
    def test_every_blank_passes_independent_topology_gate(self):
        for kwargs in VARIANTS:
            for name, cp in models(**kwargs).items():
                with self.subTest(blank=name, kwargs=kwargs):
                    self.assertEqual({k: v for k, v in violations(cp).items() if v}, {})

    def test_planted_defects_are_still_caught_on_new_blanks(self):
        for name, cp in models().items():
            with self.subTest(blank=name):
                cp.creases.remove(next(c for c in cp.creases if c.crease_type == CreaseType.CUT
                                       and c.label not in getattr(cp, "cut_slits", {})))
                self.assertTrue(violations(cp)["cut_closed"])


class Printer(unittest.TestCase):
    def test_pdf_dxf_and_bleed_contracts_for_each_blank(self):
        with tempfile.TemporaryDirectory() as tmp:
            for kwargs in VARIANTS[:3]:
                for name, cp in models(**kwargs).items():
                    with self.subTest(blank=name, kwargs=kwargs):
                        pdf = export_printer_pdf(cp, Path(tmp) / f"{cp.name}.pdf")
                        objects(pdf)
                        self.assertEqual(len(set(re.findall(rb"/Separation /([^ ]+)", pdf))), 5)
                        _, entities = dxf_entities(export_printer_dxf(cp, Path(tmp) / f"{cp.name}.dxf"))
                        self.assertTrue(any(("8", "CutContour") in e and ("70", "1") in e for e in entities))
                        closed = [pts for pts, is_closed in printer_paths(cp)["cut"] if is_closed]
                        self.assertEqual(len(closed), 1)  # one outline; slits are open paths
                        for amount in (0, 3, 8, 20):
                            bleed = bleed_outline(closed[0], amount)
                            edges = [SimpleNamespace(p1=a, p2=b) for a, b in zip(bleed, bleed[1:] + bleed[:1])]
                            for i, a in enumerate(edges):
                                for j, b in enumerate(edges[i + 2:], i + 2):
                                    if not (i == 0 and j == len(edges) - 1):
                                        self.assertIsNone(crossing(a, b), (name, amount))
                            for p in closed[0]:
                                clearance = min(distance(p, a, b) for a, b in zip(bleed, bleed[1:] + bleed[:1]))
                                self.assertGreaterEqual(clearance, amount - 0.01)

    def test_collinear_notch_bleed_forms_a_simple_envelope(self):
        # Regression: overlapping parallel strips once produced an ambiguous graph.
        # A closed notch is correct when the union is simple and preserves clearance.
        sleeve, _ = generate_sleeve_tray(width=9, depth=7, height=4, thickness=0.3, glue_flap_width=5)
        outer = next(pts for pts, closed in printer_paths(sleeve)["cut"] if closed)
        for amount in (8, 20):
            bleed = bleed_outline(outer, amount)
            self.assertGreaterEqual(len(bleed), 4)
            self.assertEqual(len(bleed), len({(p.x, p.y) for p in bleed}))
            edges = [SimpleNamespace(p1=a, p2=b) for a, b in zip(bleed, bleed[1:] + bleed[:1])]
            for i, a in enumerate(edges):
                for j, b in enumerate(edges[i + 2:], i + 2):
                    if not (i == 0 and j == len(edges) - 1):
                        self.assertIsNone(crossing(a, b), (amount, i, j))
            for p in outer:
                clearance = min(distance(p, a, b) for a, b in zip(bleed, bleed[1:] + bleed[:1]))
                self.assertGreaterEqual(clearance, amount - 0.01)





if __name__ == "__main__":
    unittest.main(verbosity=2)
