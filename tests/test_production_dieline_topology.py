"""Shared packaging gate, including planted failures for each invariant."""
import copy
import inspect
import unittest

from origami_cad import packaging
from origami_cad.geometry import OrigamiCreasePattern, Point2D, CreaseType
from dieline_topology import violations

MODELS = {
    "tuck-box": packaging.generate_tuck_box,
    "zero-glue-tray": packaging.generate_zero_glue_tray,
    "crash-lock-box": packaging.generate_crash_lock_box,
    "gable-box": packaging.generate_gable_handle_box,
    "diamond-box": packaging.generate_diamond_faceted_box,
    "pillow-box": packaging.generate_pillow_box,
    "hex-petal": packaging.generate_hexagonal_petal_box,
}
VARIANTS = {
    "tuck-box": {"width": 90, "depth": 60, "height": 130, "thickness": 0.6},
    "zero-glue-tray": {"width": 120, "depth": 95, "wall_height": 32, "thickness": 0.6},
    "crash-lock-box": {"width": 150, "depth": 40, "height": 200, "thickness": 0.6},
    "gable-box": {"width": 180, "depth": 95, "height": 140, "gable_height": 60,
                  "handle_height": 50, "thickness": 0.6},
    "diamond-box": {"width": 70, "height": 100, "facets": 5, "thickness": 0.6},
    "pillow-box": {"width": 105, "depth": 45, "height": 135, "thickness": 0.6},
    "hex-petal": {"radius": 48, "height": 65, "thickness": 0.6},
}


def rectangle():
    cp = OrigamiCreasePattern("TopologyControl")
    pts = [Point2D(0, 0), Point2D(20, 0), Point2D(20, 20), Point2D(0, 20)]
    for a, b in zip(pts, pts[1:] + pts[:1]):
        cp.add_crease(a, b, CreaseType.CUT)
    cp.add_crease(Point2D(0, 10), Point2D(20, 10), CreaseType.CREASE)
    return cp


class TopologyControls(unittest.TestCase):
    def test_clean_rectangle_and_contacts_pass(self):
        cp = rectangle()
        cp.add_crease(Point2D(10, 0), Point2D(10, 10), CreaseType.VALLEY)
        self.assertTrue(all(not rows for rows in violations(cp).values()))

    def test_each_planted_defect_is_rejected(self):
        for check in ["cut_closed", "fold_on_cut", "fold_outside", "cut_overlap", "fold_overlap", "fold_free"]:
            cp = rectangle()
            if check == "cut_closed":
                cp.creases.pop(0)
            elif check == "fold_on_cut":
                cp.add_crease(Point2D(5, 0), Point2D(15, 0), CreaseType.CREASE)
            elif check == "fold_outside":
                cp.add_crease(Point2D(-1, 10), Point2D(0, 10), CreaseType.CREASE)
            elif check == "cut_overlap":
                cp.add_crease(Point2D(15, 0), Point2D(5, 0), CreaseType.CUT)
            elif check == "fold_overlap":
                cp.add_crease(Point2D(15, 10), Point2D(5, 10), CreaseType.VALLEY)
            else:
                cp.add_crease(Point2D(5, 5), Point2D(10, 5), CreaseType.CREASE)
            with self.subTest(check=check):
                self.assertTrue(violations(cp)[check])

    def test_cut_junction_is_seen_inside_segment(self):
        cp = rectangle()
        cp.add_crease(Point2D(10, 0), Point2D(10, 5), CreaseType.CUT)
        self.assertTrue(violations(cp)["cut_closed"])

    def test_exact_duplicates_fail_for_cut_and_fold(self):
        for index, check in [(0, "cut_overlap"), (-1, "fold_overlap")]:
            cp = rectangle()
            cp.creases.append(copy.deepcopy(cp.creases[index]))
            self.assertTrue(violations(cp)[check])

    def test_hole_is_outside_material_and_slits_need_specific_declarations(self):
        cp = rectangle()
        hole = [Point2D(4, 2), Point2D(8, 2), Point2D(8, 6), Point2D(4, 6)]
        for a, b in zip(hole, hole[1:] + hole[:1]):
            cp.add_crease(a, b, CreaseType.CUT)
        cp.add_crease(Point2D(6, 4), Point2D(6, 6), CreaseType.CREASE)
        self.assertTrue(violations(cp)["fold_outside"])
        cp = rectangle()
        cp.add_crease(Point2D(10, 0), Point2D(10, 10), CreaseType.CUT, label="NamedSlit")
        self.assertTrue(violations(cp)["cut_closed"])
        cp.cut_slits = {"NamedSlit": "Separates adjacent closure flaps; endpoints meet boundary and hinge."}
        self.assertTrue(all(not rows for rows in violations(cp).values()))
        cp.cut_slits["MissingSlit"] = "Must be found, not silently exempted."
        self.assertTrue(violations(cp)["cut_closed"])


class ProductionTopology(unittest.TestCase):
    def check_model(self, name):
        for kwargs in [{}, VARIANTS[name], {"thickness": 0.0}]:
            with self.subTest(model=name, kwargs=kwargs):
                errors = {k: v for k, v in violations(MODELS[name](**kwargs)).items() if v}
                self.assertEqual(errors, {})

    def test_registry_covers_every_packaging_generator(self):
        generators = {f for n, f in inspect.getmembers(packaging, inspect.isfunction)
                      if n.startswith("generate_") and n != "generate_miura_ori_sleeve"}
        from origami_cad.product_registry import PRODUCTS
        self.assertEqual(generators, {getattr(packaging, function) for _, _, function in PRODUCTS})

    def test_tuck_box(self): self.check_model("tuck-box")
    def test_zero_glue_tray(self): self.check_model("zero-glue-tray")
    def test_crash_lock_box(self): self.check_model("crash-lock-box")
    def test_gable_box(self): self.check_model("gable-box")
    def test_diamond_box(self): self.check_model("diamond-box")
    def test_pillow_box(self): self.check_model("pillow-box")
    def test_hex_petal(self): self.check_model("hex-petal")


if __name__ == "__main__":
    unittest.main(verbosity=2)
