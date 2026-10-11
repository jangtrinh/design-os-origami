"""Faceted strip geometry preserving the specified mountain/valley network."""
from origami_cad.geometry import OrigamiCreasePattern, Point2D, CreaseType


def generate_diamond_faceted_box(
    width: float = 60.0,
    height: float = 80.0,
    facets: int = 4,
    thickness: float = 0.45,
) -> OrigamiCreasePattern:
    """
    Generates a Diamond-Faceted Origami Box (Luxury jewelry & perfume packaging).
    Employs triangular facet triangulation with alternating mountain/valley diagonal
    creases that create a gem-faceted 3D profile when folded.
    """
    cp = OrigamiCreasePattern(name=f"OrigamiDiamond_{int(width)}x{int(height)}", thickness_mm=thickness)
    h_half = height / 2.0
    panel_w = width

    # 4 side panels along X
    for i in range(facets):
        x1 = i * panel_w
        x2 = (i + 1) * panel_w
        mid_x = (x1 + x2) / 2.0

        # Boundary cuts top & bottom
        cp.add_crease(Point2D(x1, 0), Point2D(x2, 0), CreaseType.CUT, 0.0)
        cp.add_crease(Point2D(x1, height), Point2D(x2, height), CreaseType.CUT, 0.0)

        # Vertical crease between panels
        # The first boundary is the free outer edge, not a panel hinge.
        cp.add_crease(Point2D(x1, 0), Point2D(x1, height),
                      CreaseType.CUT if i == 0 else CreaseType.CREASE, 0.0 if i == 0 else 90.0)

        # Diamond creases: X-pattern in center of panel
        # Mid-level vertices
        v_top = Point2D(mid_x, 0)
        v_mid_left = Point2D(x1, h_half)
        v_mid_right = Point2D(x2, h_half)
        v_bottom = Point2D(mid_x, height)
        v_center = Point2D(mid_x, h_half)

        # Diagonals forming diamond facet
        cp.add_crease(v_top, v_center, CreaseType.MOUNTAIN, 45.0)
        cp.add_crease(v_bottom, v_center, CreaseType.MOUNTAIN, 45.0)
        cp.add_crease(v_mid_left, v_center, CreaseType.VALLEY, -45.0)
        cp.add_crease(v_mid_right, v_center, CreaseType.VALLEY, -45.0)

        # The two valley half-scores already cover the midline. A generic
        # score here would duplicate them and prescribe a conflicting angle.

    # Right edge cut
    total_w = facets * panel_w
    cp.add_crease(Point2D(total_w, 0), Point2D(total_w, height), CreaseType.CUT, 0.0)

    # Base facet
    cp.add_facet("BaseFacet", [Point2D(0, 0), Point2D(panel_w, 0), Point2D(panel_w, height), Point2D(0, height)])
    return cp
