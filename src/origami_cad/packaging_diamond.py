"""Faceted strip geometry preserving the specified mountain/valley network."""
import math
from origami_cad.geometry import OrigamiCreasePattern, Point2D, CreaseType


def generate_diamond_faceted_box(
    width: float = 60.0,
    height: float = 80.0,
    facets: int = 4,
    thickness: float = 0.45,
) -> OrigamiCreasePattern:
    """
    Generates a Diamond-Faceted Origami Box (Luxury jewelry & perfume packaging).
    Employs diagonal diamond facet triangulation with alternating mountain/valley
    creases, top/bottom pyramid closure flaps, and a side seam glue tab.
    """
    cp = OrigamiCreasePattern(name=f"OrigamiDiamond_{int(width)}x{int(height)}", thickness_mm=thickness)
    h_half = height / 2.0
    panel_w = width
    turn_angle = 360.0 / facets
    flap_h = (panel_w / 2.0) / math.tan(math.pi / facets)
    glue_w = min(12.0, panel_w * 0.3)
    taper = min(8.0, height * 0.15)

    # Left side glue flap at x in [-glue_w, 0]
    cp.add_crease(Point2D(0.0, 0.0), Point2D(0.0, height), CreaseType.CREASE, turn_angle, "GlueHinge")
    cp.add_crease(Point2D(0.0, 0.0), Point2D(-glue_w, taper), CreaseType.CUT, 0.0, "GlueFlapTop")
    cp.add_crease(Point2D(-glue_w, taper), Point2D(-glue_w, height - taper), CreaseType.CUT, 0.0, "GlueOuterCut")
    cp.add_crease(Point2D(-glue_w, height - taper), Point2D(0.0, height), CreaseType.CUT, 0.0, "GlueFlapBottom")
    cp.add_crease(Point2D(-glue_w * 0.5, taper + 4.0), Point2D(-glue_w * 0.5, height - taper - 4.0),
                  CreaseType.GLUE, 0.0, "GlueLine")

    # Side panels along X with true diagonal diamond facets and top/bottom closure flaps
    for i in range(facets):
        x1 = i * panel_w
        x2 = (i + 1) * panel_w
        mid_x = (x1 + x2) / 2.0

        # Top and bottom closure flap hinges + triangular pyramid closure flaps
        cp.add_crease(Point2D(x1, 0.0), Point2D(x2, 0.0), CreaseType.CREASE, 90.0, f"TopFlapHinge_{i}")
        cp.add_crease(Point2D(x1, 0.0), Point2D(mid_x, -flap_h), CreaseType.CUT, 0.0, "TopFlapCut")
        cp.add_crease(Point2D(mid_x, -flap_h), Point2D(x2, 0.0), CreaseType.CUT, 0.0, "TopFlapCut")

        cp.add_crease(Point2D(x1, height), Point2D(x2, height), CreaseType.CREASE, 90.0, f"BottomFlapHinge_{i}")
        cp.add_crease(Point2D(x1, height), Point2D(mid_x, height + flap_h), CreaseType.CUT, 0.0, "BottomFlapCut")
        cp.add_crease(Point2D(mid_x, height + flap_h), Point2D(x2, height), CreaseType.CUT, 0.0, "BottomFlapCut")

        # Vertical crease between panels
        if i > 0:
            cp.add_crease(Point2D(x1, 0.0), Point2D(x1, height), CreaseType.CREASE, turn_angle, f"Hinge_{i - 1}")

        # True oblique diamond facet inside each panel
        v_top = Point2D(mid_x, height * 0.18)
        v_mid_left = Point2D(x1, h_half)
        v_mid_right = Point2D(x2, h_half)
        v_bottom = Point2D(mid_x, height * 0.82)

        cp.add_crease(v_mid_left, v_top, CreaseType.MOUNTAIN, 45.0, "DiamondDiag")
        cp.add_crease(v_top, v_mid_right, CreaseType.MOUNTAIN, 45.0, "DiamondDiag")
        cp.add_crease(v_mid_left, v_bottom, CreaseType.VALLEY, -45.0, "DiamondDiag")
        cp.add_crease(v_bottom, v_mid_right, CreaseType.VALLEY, -45.0, "DiamondDiag")

    # Right edge cut
    total_w = facets * panel_w
    cp.add_crease(Point2D(total_w, 0.0), Point2D(total_w, height), CreaseType.CUT, 0.0)

    # Base facet
    cp.add_facet("BaseFacet", [Point2D(0.0, 0.0), Point2D(panel_w, 0.0),
                               Point2D(panel_w, height), Point2D(0.0, height)])
    return cp
