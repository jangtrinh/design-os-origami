"""Parametric packaging dieline generators combining origami crease patterns with industrial packaging standards."""

import math
from origami_cad.packaging_hex_petal import generate_hexagonal_petal_box
from origami_cad.packaging_pillow import generate_pillow_box
from origami_cad.packaging_diamond import generate_diamond_faceted_box
from origami_cad.packaging_gable import generate_gable_handle_box
from origami_cad.packaging_crash_lock import generate_crash_lock_box
from origami_cad.packaging_tray import generate_zero_glue_tray
from typing import List, Tuple
from origami_cad.geometry import OrigamiCreasePattern, Point2D, CreaseType


def generate_tuck_box(
    width: float = 80.0,
    depth: float = 50.0,
    height: float = 120.0,
    thickness: float = 0.5,
    glue_flap_width: float = 15.0,
    tuck_flap_height: float = 15.0,
) -> OrigamiCreasePattern:
    """
    Generates a standard ECMA A20.20 style Straight/Reverse Tuck Folding Carton
    with thickness score allowances and tapered dust flaps.
    """
    cp = OrigamiCreasePattern(name=f"TuckBox_{int(width)}x{int(depth)}x{int(height)}", thickness_mm=thickness)

    # Thickness score allowance
    c_allow = cp.calculate_score_allowance(90.0)

    # Effective panel dimensions
    w = width + c_allow
    d = depth + c_allow
    h = height

    # Horizontal panel progression along X:
    # Glue Flap -> Left Side (D) -> Front (W) -> Right Side (D) -> Back (W)
    x0 = 0.0
    x_glue = x0 + glue_flap_width
    x_left = x_glue + d
    x_front = x_left + w
    x_right = x_front + d
    x_back = x_right + w

    # Vertical baseline Y coordinates:
    # y_top_tuck = -d - tuck_flap_height
    # y_top_lid = -d
    # y_body_top = 0
    # y_body_bottom = h
    # y_bottom_lid = h + d
    # y_bottom_tuck = h + d + tuck_flap_height

    y_top_tuck = -d - tuck_flap_height
    y_top_lid = -d
    y_top = 0.0
    y_bottom = h
    y_bottom_lid = h + d
    y_bottom_tuck = h + d + tuck_flap_height

    # 1. Main Vertical Body Creases (Green)
    # Between Glue & Left Side
    cp.add_crease(Point2D(x_glue, y_top), Point2D(x_glue, y_bottom), CreaseType.CREASE, 90.0, "Hinge_Glue")
    # Between Left Side & Front
    cp.add_crease(Point2D(x_left, y_top), Point2D(x_left, y_bottom), CreaseType.CREASE, 90.0, "Hinge_LeftFront")
    # Between Front & Right Side
    cp.add_crease(Point2D(x_front, y_top), Point2D(x_front, y_bottom), CreaseType.CREASE, 90.0, "Hinge_FrontRight")
    # Between Right Side & Back
    cp.add_crease(Point2D(x_right, y_top), Point2D(x_right, y_bottom), CreaseType.CREASE, 90.0, "Hinge_RightBack")

    # 2. Main Horizontal Creases (Green)
    # Only attached dust flaps and lids have hinges; bare body edges are CUT.
    for a, b in ((x_glue, x_left), (x_left, x_front), (x_front, x_right)):
        cp.add_crease(Point2D(a, y_top), Point2D(b, y_top), CreaseType.CREASE, 90.0, "Hinge_TopBody")
    for a, b in ((x_glue, x_left), (x_front, x_right), (x_right, x_back)):
        cp.add_crease(Point2D(a, y_bottom), Point2D(b, y_bottom), CreaseType.CREASE, 90.0, "Hinge_BottomBody")

    # Top Tuck Lid Hinge (Top of Front Panel)
    cp.add_crease(Point2D(x_left, y_top_lid), Point2D(x_front, y_top_lid), CreaseType.CREASE, 90.0, "Hinge_TopTuckFlap")
    # Bottom Tuck Lid Hinge (Bottom of Back Panel)
    cp.add_crease(Point2D(x_right, y_bottom_lid), Point2D(x_back, y_bottom_lid), CreaseType.CREASE, 90.0, "Hinge_BottomTuckFlap")

    # 3. Outer Cut Outlines (Red)
    # Glue Flap Cut outline (with 15 degree chamfer at ends)
    cp.add_crease(Point2D(x_glue, y_top), Point2D(x0 + 4.0, y_top + 4.0), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x0 + 4.0, y_top + 4.0), Point2D(x0, y_top + 8.0), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x0, y_top + 8.0), Point2D(x0, y_bottom - 8.0), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x0, y_bottom - 8.0), Point2D(x0 + 4.0, y_bottom - 4.0), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x0 + 4.0, y_bottom - 4.0), Point2D(x_glue, y_bottom), CreaseType.CUT, 0.0)

    # Top Dust Flap 1 (on Left Panel: x_glue to x_left)
    # Tapered cut: 3 degrees inward
    cp.add_crease(Point2D(x_glue, y_top), Point2D(x_glue + 3.0, y_top - d * 0.8), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_glue + 3.0, y_top - d * 0.8), Point2D(x_left - 3.0, y_top - d * 0.8), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_left - 3.0, y_top - d * 0.8), Point2D(x_left, y_top), CreaseType.CUT, 0.0)

    # Top Tuck Lid & Tab (on Front Panel: x_left to x_front)
    cp.add_crease(Point2D(x_left, y_top), Point2D(x_left, y_top_lid), CreaseType.CUT, 0.0)
    # Tuck tab sides tapered with corner radius approximation
    cp.add_crease(Point2D(x_left, y_top_lid), Point2D(x_left + 4.0, y_top_tuck), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_left + 4.0, y_top_tuck), Point2D(x_front - 4.0, y_top_tuck), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_front - 4.0, y_top_tuck), Point2D(x_front, y_top_lid), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_front, y_top_lid), Point2D(x_front, y_top), CreaseType.CUT, 0.0)

    # Top Dust Flap 2 (on Right Panel: x_front to x_right)
    cp.add_crease(Point2D(x_front, y_top), Point2D(x_front + 3.0, y_top - d * 0.8), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_front + 3.0, y_top - d * 0.8), Point2D(x_right - 3.0, y_top - d * 0.8), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_right - 3.0, y_top - d * 0.8), Point2D(x_right, y_top), CreaseType.CUT, 0.0)

    # Top Back Panel Cut (on Back Panel: x_right to x_back)
    cp.add_crease(Point2D(x_right, y_top), Point2D(x_back, y_top), CreaseType.CUT, 0.0)
    # Outer Right Cut Edge
    cp.add_crease(Point2D(x_back, y_top), Point2D(x_back, y_bottom), CreaseType.CUT, 0.0)

    # Bottom Dust Flap 1 (on Left Panel: x_glue to x_left)
    cp.add_crease(Point2D(x_glue, y_bottom), Point2D(x_glue + 3.0, y_bottom + d * 0.8), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_glue + 3.0, y_bottom + d * 0.8), Point2D(x_left - 3.0, y_bottom + d * 0.8), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_left - 3.0, y_bottom + d * 0.8), Point2D(x_left, y_bottom), CreaseType.CUT, 0.0)

    # Bottom Front Cut (on Front Panel: x_left to x_front)
    cp.add_crease(Point2D(x_left, y_bottom), Point2D(x_front, y_bottom), CreaseType.CUT, 0.0)

    # Bottom Dust Flap 2 (on Right Panel: x_front to x_right)
    cp.add_crease(Point2D(x_front, y_bottom), Point2D(x_front + 3.0, y_bottom + d * 0.8), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_front + 3.0, y_bottom + d * 0.8), Point2D(x_right - 3.0, y_bottom + d * 0.8), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_right - 3.0, y_bottom + d * 0.8), Point2D(x_right, y_bottom), CreaseType.CUT, 0.0)

    # Bottom Tuck Lid & Tab (on Back Panel: x_right to x_back)
    cp.add_crease(Point2D(x_right, y_bottom), Point2D(x_right, y_bottom_lid), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_right, y_bottom_lid), Point2D(x_right + 4.0, y_bottom_tuck), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_right + 4.0, y_bottom_tuck), Point2D(x_back - 4.0, y_bottom_tuck), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_back - 4.0, y_bottom_tuck), Point2D(x_back, y_bottom_lid), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_back, y_bottom_lid), Point2D(x_back, y_bottom), CreaseType.CUT, 0.0)

    # Glue Area Annotation (Magenta)
    cp.add_crease(Point2D(x0 + 2.0, y_top + 10.0), Point2D(x_glue - 2.0, y_top + 10.0), CreaseType.GLUE, 0.0, "GLUE_LINE")
    cp.add_crease(Point2D(x0 + 2.0, y_bottom - 10.0), Point2D(x_glue - 2.0, y_bottom - 10.0), CreaseType.GLUE, 0.0, "GLUE_LINE")

    # Define Facets for 3D simulation
    # Base Facet: Front Panel (Anchor at Z=0)
    cp.add_facet("FrontPanel", [
        Point2D(x_left, y_top),
        Point2D(x_front, y_top),
        Point2D(x_front, y_bottom),
        Point2D(x_left, y_bottom)
    ], fold_angle_deg=0.0)

    # Left Panel
    cp.add_facet("LeftPanel", [
        Point2D(x_glue, y_top),
        Point2D(x_left, y_top),
        Point2D(x_left, y_bottom),
        Point2D(x_glue, y_bottom)
    ], fold_angle_deg=90.0)

    # Right Panel
    cp.add_facet("RightPanel", [
        Point2D(x_front, y_top),
        Point2D(x_right, y_top),
        Point2D(x_right, y_bottom),
        Point2D(x_front, y_bottom)
    ], fold_angle_deg=90.0)

    # Back Panel
    cp.add_facet("BackPanel", [
        Point2D(x_right, y_top),
        Point2D(x_back, y_top),
        Point2D(x_back, y_bottom),
        Point2D(x_right, y_bottom)
    ], fold_angle_deg=180.0)

    # Top Lid
    cp.add_facet("TopLid", [
        Point2D(x_left, y_top_lid),
        Point2D(x_front, y_top_lid),
        Point2D(x_front, y_top),
        Point2D(x_left, y_top)
    ], fold_angle_deg=90.0)

    # Bottom Lid
    cp.add_facet("BottomLid", [
        Point2D(x_right, y_bottom),
        Point2D(x_back, y_bottom),
        Point2D(x_back, y_bottom_lid),
        Point2D(x_right, y_bottom_lid)
    ], fold_angle_deg=90.0)

    return cp


def generate_miura_ori_sleeve(
    cell_w: float = 30.0,
    cell_h: float = 20.0,
    rows: int = 4,
    cols: int = 6,
    skew_angle_deg: float = 75.0,
) -> OrigamiCreasePattern:
    """
    Generates a rigid origami Miura-ori tessellation crease pattern.
    Miura-ori is flat-foldable with 1-DOF rigid panel kinematics,
    ideal for shock-absorbing packaging sleeves.
    """
    cp = OrigamiCreasePattern(name=f"MiuraOri_{cols}x{rows}", thickness_mm=0.3)
    rad = math.radians(skew_angle_deg)
    dx = cell_h * (1.0 / math.tan(rad))

    for r in range(rows + 1):
        for c in range(cols + 1):
            offset_x = dx if (r % 2 == 1 and c % 2 == 1) else 0.0
            x = c * cell_w + offset_x
            y = r * cell_h

            # Horizontal zig-zag creases
            if c < cols:
                next_offset = dx if (r % 2 == 1 and (c + 1) % 2 == 1) else 0.0
                nx = (c + 1) * cell_w + next_offset
                c_type = CreaseType.MOUNTAIN if (r % 2 == 0) else CreaseType.VALLEY
                cp.add_crease(Point2D(x, y), Point2D(nx, y), c_type, 60.0)

            # Vertical zig-zag creases
            if r < rows:
                next_r_offset = dx if ((r + 1) % 2 == 1 and c % 2 == 1) else 0.0
                ny = (r + 1) * cell_h
                nx2 = c * cell_w + next_r_offset
                c_type = CreaseType.VALLEY if ((r + c) % 2 == 0) else CreaseType.MOUNTAIN
                cp.add_crease(Point2D(x, y), Point2D(nx2, ny), c_type, 60.0)

    return cp
