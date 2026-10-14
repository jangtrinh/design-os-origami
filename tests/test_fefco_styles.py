"""FEFCO 0201 and 0427 style generators: structure, gates, folds, rejections."""
import copy
import math
import re
import tempfile
import unittest
from pathlib import Path

from origami_cad.dieline_export import export_svg
from origami_cad.fold_faces import build_fold_model
from origami_cad.fold_graph import contains
from origami_cad.fold_kinematics import fold_matrices, fold_vertices
from origami_cad.geometry import CreaseType, Point2D
from origami_cad.packaging_fefco_0201 import generate_fefco_0201
from origami_cad.packaging_fefco_0427 import generate_fefco_0427
from origami_cad.printer_bleed import outward_envelope
from origami_cad.printer_paths import signed_area
from origami_cad.printer_profile_export import DEFAULT_SPOTS, export_printer_dxf, export_printer_pdf
from dieline_topology import cut_loops, violations
from printer_dxf_structure import validate

FOLDS = {CreaseType.CREASE, CreaseType.MOUNTAIN, CreaseType.VALLEY}
VARIANTS = {
    "fefco-0201": [{}, {"width": 320, "depth": 90, "height": 45, "thickness": 1.2},
                   {"width": 180, "depth": 60, "height": 250, "thickness": 0.3},
                   {"thickness": 0.0}],
    "fefco-0427": [{}, {"width": 330, "depth": 110, "height": 90, "thickness": 1.2},
                   {"width": 70, "depth": 220, "height": 25, "thickness": 0.3},
                   {"thickness": 0.0}],
}
GENERATORS = {"fefco-0201": generate_fefco_0201, "fefco-0427": generate_fefco_0427}


def folds(cp):
    return [c for c in cp.creases if c.crease_type in FOLDS]


def cuts(cp):
    return [c for c in cp.creases if c.crease_type == CreaseType.CUT]


def vertical(c, x, y0, y1):
    return (abs(c.p1.x - x) < 1e-9 and abs(c.p2.x - x) < 1e-9
            and {round(c.p1.y, 6), round(c.p2.y, 6)} == {round(y0, 6), round(y1, 6)})


def horizontal(c, y, x0, x1):
    return (abs(c.p1.y - y) < 1e-9 and abs(c.p2.y - y) < 1e-9
            and {round(c.p1.x, 6), round(c.p2.x, 6)} == {round(x0, 6), round(x1, 6)})


def folded_extents(cp):
    model = build_fold_model(cp)
    points = [p for pts in fold_vertices(model, 1.0).values() for p in pts]
    return sorted(max(p[i] for p in points) - min(p[i] for p in points) for i in range(3))


class Fefco0201Structure(unittest.TestCase):
    def test_four_walls_eight_flaps_and_manufacturers_joint(self):
        cp = generate_fefco_0201()
        allowance = cp.calculate_score_allowance(90.0)
        self.assertAlmostEqual(allowance, 0.45 * 0.5)
        length, breadth, height = 200 + allowance, 150 + allowance, 120.0
        joint = cp.joint_flap_width
        xs = [joint]
        for span in (length, breadth, length, breadth):  # FEFCO 0201: L B L B
            xs.append(xs[-1] + span)
        panel_hinges = [c for c in folds(cp) if any(vertical(c, x, 0, height) for x in xs[:4])]
        self.assertEqual(len(panel_hinges), 4, "joint hinge plus three wall hinges")
        self.assertTrue(all(c.crease_type == CreaseType.CREASE and c.target_angle_deg == 90
                            for c in panel_hinges))
        flap_depth = breadth / 2  # all flaps half the breadth, Fibre Box Association / FEFCO 0201
        slot = cp.slot_width
        for y in (0.0, height):
            hinges = [c for c in folds(cp) if abs(c.p1.y - y) < 1e-9 and abs(c.p2.y - y) < 1e-9]
            self.assertEqual(sorted((min(c.p1.x, c.p2.x), max(c.p1.x, c.p2.x)) for c in hinges),
                             [(xs[i] + slot / 2, xs[i + 1] - slot / 2) for i in range(4)])
        top = min(c.p1.y for c in cuts(cp))
        bottom = max(c.p1.y for c in cuts(cp))
        self.assertAlmostEqual(top, -flap_depth)
        self.assertAlmostEqual(bottom, height + flap_depth)
        # Slot floors run along the body scores: a half width on each side of every wall
        # score (six full slots) plus a half slot at each end of the glued corner.
        for y in (0.0, height):
            floors = sorted((min(c.p1.x, c.p2.x), max(c.p1.x, c.p2.x)) for c in cuts(cp)
                            if abs(c.p1.y - y) < 1e-9 and abs(c.p2.y - y) < 1e-9)
            expected = sorted([(xs[i], xs[i] + slot / 2) for i in range(4)]
                              + [(xs[i + 1] - slot / 2, xs[i + 1]) for i in range(4)])
            self.assertEqual([(round(a, 6), round(b, 6)) for a, b in floors],
                             [(round(a, 6), round(b, 6)) for a, b in expected])
        glue = [c for c in cp.creases if c.crease_type == CreaseType.GLUE]
        self.assertTrue(glue and all(0 < c.p1.x < joint and 0 < c.p2.x < joint for c in glue))
        self.assertEqual(getattr(cp, "cut_slits", {}), {})
        self.assertEqual(cp.name, "FEFCO0201_200x150x120")
        self.assertEqual(cp.fefco_style, "0201")

    def test_panels_follow_formula_allowance(self):
        thick = generate_fefco_0201(thickness=1.2)
        thin = generate_fefco_0201(thickness=0.0)
        delta = thick.calculate_score_allowance(90.0) - thin.calculate_score_allowance(90.0)
        self.assertAlmostEqual(delta, 0.45 * 1.2)
        self.assertAlmostEqual(thick.bounding_box()[2] - thin.bounding_box()[2], 4 * delta)


class Fefco0427Structure(unittest.TestCase):
    def test_roll_ends_tuck_front_dust_flaps_and_no_glue(self):
        cp = generate_fefco_0427()
        allowance = cp.calculate_score_allowance(90.0)
        length, breadth, height = 200 + allowance, 150 + allowance, 60.0
        strip = cp.roll_strip_width
        self.assertAlmostEqual(strip, 2 * 0.5 + cp.roll_clearance)
        x_base = height
        x_back = x_base + breadth
        x_lid = x_back + height
        x_tuck = x_lid + breadth
        # Four wall/lid/tuck hinges along the length edges of the base.
        for x in (x_base, x_back, x_lid, x_tuck):
            self.assertEqual(sum(vertical(c, x, 0, length) for c in folds(cp)), 1, x)
        # Roll ends: two parallel creases per end separated by the roll strip, both ends.
        for y in (-height, -height - strip, length + height, length + height + strip):
            self.assertEqual(sum(horizontal(c, y, x_base, x_back) for c in folds(cp)), 1, y)
        # Tuck front is the last column and has no attached flaps.
        self.assertAlmostEqual(cp.bounding_box()[2], x_tuck + cp.tuck_depth)
        self.assertFalse(any(c.p1.x > x_tuck + 1e-9 and c.p2.x > x_tuck + 1e-9 for c in folds(cp)))
        # Dust flaps on front and back walls, lid side flaps on the lid, each on both ends.
        for x0, x1 in ((0, x_base), (x_back, x_lid), (x_lid, x_tuck)):
            for y in (0.0, length):
                self.assertEqual(sum(horizontal(c, y, x0, x1) for c in folds(cp)), 1, (x0, y))
        self.assertEqual([c for c in cp.creases if c.crease_type == CreaseType.GLUE], [])
        # Flap separations are declared knife slits reaching the body corner lines.
        self.assertEqual(len(cp.cut_slits), 6)
        self.assertTrue(all(sum(c.label == label for c in cuts(cp)) == 1 for label in cp.cut_slits))
        # Two lock slots sit in the base beside the end scores as closed inner cut loops.
        outline = [c for c in cuts(cp) if c.label not in cp.cut_slits]
        loops, errors = cut_loops(outline)
        self.assertEqual(errors, [])
        self.assertEqual(len(loops), 3)
        self.assertEqual(cp.name, "FEFCO0427_200x150x60")
        self.assertEqual(cp.fefco_style, "0427")

    def test_thickness_drives_roll_strip_and_slot_depth(self):
        thick, thin = generate_fefco_0427(thickness=1.2), generate_fefco_0427(thickness=0.0)
        self.assertAlmostEqual(thick.roll_strip_width - thin.roll_strip_width, 2.4)
        self.assertGreater(thin.roll_strip_width, 0)
        self.assertAlmostEqual(thick.lock_slot_height - thin.lock_slot_height, 2.4)


class FefcoGates(unittest.TestCase):
    def test_topology_gate_fold_preview_and_closure_for_defaults_and_variants(self):
        for name, generate in GENERATORS.items():
            for kwargs in VARIANTS[name]:
                with self.subTest(model=name, kwargs=kwargs):
                    cp = generate(**kwargs)
                    self.assertEqual({k: v for k, v in violations(cp).items() if v}, {})
                    model = build_fold_model(cp)
                    self.assertTrue(model["available"], model["status"])
                    self.assertTrue(model["continuity"]["valid"])
                    self.assertLessEqual(model["continuity"]["max_gap_mm"], 1e-6)
                    allowance = cp.calculate_score_allowance(90.0)
                    width = kwargs.get("width", 200) + allowance
                    depth = kwargs.get("depth", 150) + allowance
                    height = kwargs.get("height", 120 if name == "fefco-0201" else 60)
                    if name == "fefco-0427":
                        self.assert_lock_tabs_pass_through_slots(cp)
                        height += cp.lock_tab_depth  # rigid tabs protrude below the base
                    expected = sorted([width, depth, height])
                    for actual, target in zip(folded_extents(cp), expected):
                        self.assertAlmostEqual(actual, target, delta=0.5)

    def assert_lock_tabs_pass_through_slots(self, cp):
        """Rigid tabs end one tab depth below the base plane, inside the slot footprint."""
        model = build_fold_model(cp)
        base = next(f["id"] for f in model["faces"]
                    if contains((cp.bounding_box()[2] / 3, 1.0), f["vertices"]))
        matrices = fold_matrices(model, 1.0)
        moved = fold_vertices(model, 1.0)
        base_z = moved[base][0][2]
        lid_z = moved[model["root"]][0][2] if model["root"] != base else None
        outward = -1 if lid_z is None or lid_z > base_z else 1
        tips = [p for pts in moved.values() for p in pts
                if abs(p[2] - (base_z + outward * cp.lock_tab_depth)) < 1e-6]
        self.assertEqual(len(tips), 4)
        slots = [[c for c in cp.creases if c.label == label] for label in ("LockSlot_Top", "LockSlot_Bottom")]
        for tip in tips:
            inside = []
            for slot in slots:
                corners = [[sum(matrices[base][i][j] * v for j, v in enumerate([c.p1.x, c.p1.y, 0, 1]))
                            for i in range(3)] for c in slot]
                xs = sorted(c[0] for c in corners)
                ys = sorted(c[1] for c in corners)
                inside.append(xs[0] + 1e-6 < tip[0] < xs[-1] - 1e-6 and ys[0] + 1e-6 < tip[1] < ys[-1] - 1e-6)
            self.assertEqual(sum(inside), 1, (tip, inside))

    def test_face_counts_are_the_source_pieces(self):
        self.assertEqual(len(build_fold_model(generate_fefco_0201())["faces"]), 13)
        self.assertEqual(len(build_fold_model(generate_fefco_0427())["faces"]), 17)

    def test_planted_defects_are_still_caught_on_these_blanks(self):
        cp = generate_fefco_0427()
        undeclared = copy.deepcopy(cp)
        undeclared.cut_slits = {}
        self.assertTrue(violations(undeclared)["cut_closed"])
        self.assertFalse(build_fold_model(undeclared)["available"])
        opened = copy.deepcopy(generate_fefco_0201())
        opened.creases.remove(next(c for c in opened.creases if c.crease_type == CreaseType.CUT))
        self.assertTrue(violations(opened)["cut_closed"])
        glued = copy.deepcopy(generate_fefco_0201())
        edge = next(c for c in glued.creases if c.crease_type == CreaseType.CUT)
        glued.add_crease(edge.p1, Point2D((edge.p1.x + edge.p2.x) / 2, (edge.p1.y + edge.p2.y) / 2),
                         CreaseType.CREASE)
        self.assertTrue(violations(glued)["fold_on_cut"])

    def test_printer_profile_and_presentation_exports(self):
        for name, generate in GENERATORS.items():
            with self.subTest(model=name), tempfile.TemporaryDirectory() as tmp:
                cp = generate()
                root = Path(tmp)
                pdf = export_printer_pdf(cp, root / "p.pdf")
                self.assertTrue(pdf.startswith(b"%PDF-1.4"))
                self.assertEqual(set(re.findall(rb"/Separation /([^ ]+)", pdf)),
                                 {n.encode() for n in DEFAULT_SPOTS.values()})
                dxf = export_printer_dxf(cp, root / "p.dxf")
                validate(dxf, DEFAULT_SPOTS)
                svg = export_svg(cp, str(root / "p.svg"))
                self.assertIn('id="CUT"', svg)
                self.assertEqual(svg.count("<line"), len(cp.creases))

    def test_bleed_envelope_fills_notches_narrower_than_the_bleed(self):
        """A slot narrower than the bleed is bridged; wider slots keep their offset walls."""
        def notched(width):
            half = width / 2
            return [Point2D(0, 0), Point2D(40 - half, 0), Point2D(40 - half, 30), Point2D(40 + half, 30),
                    Point2D(40 + half, 0), Point2D(80, 0), Point2D(80, 60), Point2D(0, 60)]
        for width, bleed in ((2.0, 3.0), (2.0, 2.1), (0.5, 3.0), (7.0, 3.0), (6.0, 3.0)):
            with self.subTest(width=width, bleed=bleed):
                loop = outward_envelope(notched(width), bleed)
                self.assertGreater(abs(signed_area(loop)), 80 * 60)
                for p in notched(width):
                    self.assertTrue(min(p.distance_to(q) for q in loop) >= bleed - 1e-6
                                    or any(abs(p.x - q.x) < 1e-9 or abs(p.y - q.y) < 1e-9 for q in loop))
                xs = [q.x for q in loop]
                self.assertAlmostEqual(min(xs), -bleed)
                self.assertAlmostEqual(max(xs), 80 + bleed)
                self.assertAlmostEqual(min(q.y for q in loop), -bleed)
                bridged = not any(abs(q.y - (30 - bleed)) < 1e-9 for q in loop)
                self.assertEqual(bridged, width <= 2 * bleed, loop)
        # Original orientation and untouched convex contour: unchanged envelope.
        square = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)]
        loop = outward_envelope(square, 1.0)
        self.assertAlmostEqual(abs(signed_area(loop)), 144)
        self.assertEqual({(min(q.x for q in loop), max(q.x for q in loop)),
                          (min(q.y for q in loop), max(q.y for q in loop))}, {(-1, 11)})

    def test_rejects_invalid_dimensions_and_thickness(self):
        for generate in GENERATORS.values():
            for kwargs in ({"width": 0}, {"depth": -5}, {"height": float("nan")},
                           {"width": float("inf")}, {"thickness": -0.1},
                           {"thickness": float("nan")}, {"width": "200"}):
                with self.subTest(generate=generate.__name__, kwargs=kwargs):
                    with self.assertRaises((ValueError, TypeError)):
                        generate(**kwargs)
        with self.assertRaisesRegex(ValueError, "slot"):
            generate_fefco_0201(depth=4, slot_width=5)
        with self.assertRaisesRegex(ValueError, "joint"):
            generate_fefco_0201(joint_flap_width=0)
        with self.assertRaisesRegex(ValueError, "longer"):
            generate_fefco_0201(width=100, depth=150)
        with self.assertRaisesRegex(ValueError, "height"):
            generate_fefco_0427(height=1.0, thickness=0.5)
        with self.assertRaisesRegex(ValueError, "depth"):
            generate_fefco_0427(depth=1.5)

    def test_names_are_unique_and_source_is_not_mutated_by_preview(self):
        a, b = generate_fefco_0201(), generate_fefco_0427()
        self.assertNotEqual(a.name, b.name)
        for cp in (a, b):
            before = copy.deepcopy(cp.creases)
            build_fold_model(cp)
            self.assertEqual(cp.creases, before)
            self.assertTrue(all(math.isfinite(v) for c in cp.creases
                                for v in (c.p1.x, c.p1.y, c.p2.x, c.p2.y)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
