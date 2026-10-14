"""Rollover tray geometry."""
from origami_cad.geometry import OrigamiCreasePattern, Point2D, CreaseType


def generate_zero_glue_tray(
    width: float = 100.0,
    depth: float = 70.0,
    wall_height: float = 30.0,
    thickness: float = 0.5,
) -> OrigamiCreasePattern:
    """
    Generates a single-sheet Zero-Glue Interlocking Origami Tray (Masu box style).
    Double-folded rollover walls with 45-degree corner gussets that lock securely
    without any adhesive, ideal for sustainable luxury packaging.
    """
    cp = OrigamiCreasePattern(name=f"ZeroGlueTray_{int(width)}x{int(depth)}x{int(wall_height)}", thickness_mm=thickness)
    h = wall_height

    # Center base panel: width x depth
    # Center origin at (h * 2 + 10, h * 2 + 10)
    ox = 2 * h + 10.0
    oy = 2 * h + 10.0

    bx1, by1 = ox, oy
    bx2, by2 = ox + width, oy + depth

    # 1. Base rectangle creases
    cp.add_crease(Point2D(bx1, by1), Point2D(bx2, by1), CreaseType.CREASE, 90.0, "Base_Top")
    cp.add_crease(Point2D(bx2, by1), Point2D(bx2, by2), CreaseType.CREASE, 90.0, "Base_Right")
    cp.add_crease(Point2D(bx2, by2), Point2D(bx1, by2), CreaseType.CREASE, 90.0, "Base_Bottom")
    cp.add_crease(Point2D(bx1, by2), Point2D(bx1, by1), CreaseType.CREASE, 90.0, "Base_Left")

    # 2. Outer rollover walls (first wall + 180-degree rollover inner wall)
    # Top wall
    cp.add_crease(Point2D(bx1, by1 - h), Point2D(bx2, by1 - h), CreaseType.CREASE, 180.0, "TopWall_Rollover")
    cp.add_crease(Point2D(bx1, by1 - 2*h), Point2D(bx2, by1 - 2*h), CreaseType.CUT, 0.0, "TopWall_Edge")

    # Bottom wall
    cp.add_crease(Point2D(bx1, by2 + h), Point2D(bx2, by2 + h), CreaseType.CREASE, 180.0, "BottomWall_Rollover")
    cp.add_crease(Point2D(bx1, by2 + 2*h), Point2D(bx2, by2 + 2*h), CreaseType.CUT, 0.0, "BottomWall_Edge")

    # Left wall
    cp.add_crease(Point2D(bx1 - h, by1), Point2D(bx1 - h, by2), CreaseType.CREASE, 180.0, "LeftWall_Rollover")
    cp.add_crease(Point2D(bx1 - 2*h, by1), Point2D(bx1 - 2*h, by2), CreaseType.CUT, 0.0, "LeftWall_Edge")

    # Right wall
    cp.add_crease(Point2D(bx2 + h, by1), Point2D(bx2 + h, by2), CreaseType.CREASE, 180.0, "RightWall_Rollover")
    cp.add_crease(Point2D(bx2 + 2*h, by1), Point2D(bx2 + 2*h, by2), CreaseType.CUT, 0.0, "RightWall_Edge")

    cp.cut_slits = {f"CornerSlit_{i}": "Separates corner locking gusset tab from top/bottom wall so tab folds inside rollover wall."
                    for i in range(4)}

    # Close each rollover strip at both ends and attach 45-degree corner gussets to Left/Right walls.
    corners = [(bx1, by1, -1, -1), (bx2, by1, 1, -1), (bx2, by2, 1, 1), (bx1, by2, -1, 1)]
    for i, (cx, cy, sx, sy) in enumerate(corners):
        cp.add_crease(Point2D(cx, cy + sy * h), Point2D(cx, cy + sy * 2 * h),
                      CreaseType.CUT, 0.0, "RolloverSide")
        cp.add_crease(Point2D(cx + sx * h, cy), Point2D(cx + sx * h, cy + sy * h),
                      CreaseType.CUT, 0.0, "CornerCut")
        cp.add_crease(Point2D(cx + sx * h, cy), Point2D(cx + sx * 2 * h, cy),
                      CreaseType.CUT, 0.0, "RolloverSide")
        cp.add_crease(Point2D(cx, cy + sy * h), Point2D(cx + sx * h, cy + sy * h),
                      CreaseType.CUT, 0.0, "CornerCut")
        # Relief slit along horizontal top/bottom wall edge; 90-deg hinge along Left/Right wall edge
        cp.add_crease(Point2D(cx, cy), Point2D(cx, cy + sy * h),
                      CreaseType.CUT, 0.0, f"CornerSlit_{i}")
        cp.add_crease(Point2D(cx, cy), Point2D(cx + sx * h, cy),
                      CreaseType.CREASE, 90.0, f"CornerHinge_{i}")
        # 45-degree corner gusset creases meeting at the corner square center
        p_c = Point2D(cx, cy)
        p_mid = Point2D(cx + sx * h * 0.5, cy + sy * h * 0.5)
        cp.add_crease(p_c, p_mid, CreaseType.VALLEY, -90.0, "CornerGusset")
        cp.add_crease(Point2D(cx + sx * h, cy), p_mid, CreaseType.MOUNTAIN, 90.0, "CornerGussetLock")

    # Base facet
    cp.add_facet("TrayBase", [Point2D(bx1, by1), Point2D(bx2, by1), Point2D(bx2, by2), Point2D(bx1, by2)], fold_angle_deg=0.0)
    return cp
