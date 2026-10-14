"""Handled roof and gusset carton geometry."""
import math
from origami_cad.packaging_constraints import validate_glue_flap
from origami_cad.geometry import OrigamiCreasePattern, Point2D, CreaseType


def generate_gable_handle_box(
    width: float = 160.0,
    depth: float = 110.0,
    height: float = 110.0,
    gable_height: float = 55.0,
    handle_height: float = 45.0,
    thickness: float = 0.5,
) -> OrigamiCreasePattern:
    """
    Generates an Industrial Gable-Top Food Box with Integrated Carry Handle (FEFCO 0217 / Gable Box).
    Features 4 body panels, 2 inward triangular folding side gussets, pitched front/back roof panels,
    integrated ergonomic carry handles with die-cut finger slots, and interlocking bottom flaps.
    """
    cp = OrigamiCreasePattern(name=f"GableHandleBox_{int(width)}x{int(depth)}x{int(height)}", thickness_mm=thickness)

    # Thickness score allowance
    c_allow = cp.calculate_score_allowance(90.0)
    w = width + c_allow
    d = depth + c_allow
    h = height
    hg = max(gable_height, (d / 2.0) / math.sin(math.radians(45.0)))
    hh = handle_height
    glue_w = 15.0
    validate_glue_flap(glue_w, w)

    # Panel progression along X: Glue Tab -> Left Side (D) -> Front (W) -> Right Side (D) -> Back (W)
    x0 = 0.0
    x_glue = x0 + glue_w
    x_left = x_glue + d
    x_front = x_left + w
    x_right = x_front + d
    x_back = x_right + w

    # Vertical baselines Y
    y_handle_top = -(hg + hh)
    y_roof_top = -hg
    y_body_top = 0.0
    y_body_bottom = h
    bottom_flap_h = d * 0.65
    y_bottom_flaps = h + bottom_flap_h

    cp.cut_slits = {label: "Separates gusset and roof from body-top hinge to gusset shoulder."
                    for label in ("GussetFrontSlit", "FrontRightSlit", "RightBackSlit")}
    # The bare right body edge connects roof and bottom outlines.
    cp.add_crease(Point2D(x_back, y_body_top), Point2D(x_back, y_body_bottom),
                  CreaseType.CUT, 0.0, "BodyRightCut")

    # 1. Main Vertical Body Creases (Green)
    cp.add_crease(Point2D(x_glue, y_body_top), Point2D(x_glue, y_body_bottom), CreaseType.CREASE, 90.0, "Crease_Glue")
    cp.add_crease(Point2D(x_left, y_body_top), Point2D(x_left, y_body_bottom), CreaseType.CREASE, 90.0, "Crease_LeftFront")
    cp.add_crease(Point2D(x_front, y_body_top), Point2D(x_front, y_body_bottom), CreaseType.CREASE, 90.0, "Crease_FrontRight")
    cp.add_crease(Point2D(x_right, y_body_top), Point2D(x_right, y_body_bottom), CreaseType.CREASE, 90.0, "Crease_RightBack")

    # 2. Main Horizontal Creases (Top & Bottom of main body)
    for px1, px2 in ((x_glue, x_left), (x_left, x_front), (x_front, x_right), (x_right, x_back)):
        cp.add_crease(Point2D(px1, y_body_top), Point2D(px2, y_body_top), CreaseType.CREASE, 45.0, "Crease_BodyTop")
    cp.add_crease(Point2D(x_glue, y_body_bottom), Point2D(x_back, y_body_bottom), CreaseType.CREASE, 90.0, "Crease_BodyBottom")

    # 3. Left Side Triangular Inward Gusset (x_glue to x_left)
    x_mid_l = (x_glue + x_left) / 2.0
    cp.add_crease(Point2D(x_mid_l, y_body_top), Point2D(x_mid_l, y_roof_top), CreaseType.VALLEY, -90.0, "Gusset_Left_Center")
    cp.add_crease(Point2D(x_glue, y_body_top), Point2D(x_mid_l, y_roof_top), CreaseType.CREASE, 45.0, "Gusset_Left_Diag1")
    cp.add_crease(Point2D(x_left, y_body_top), Point2D(x_mid_l, y_roof_top), CreaseType.CREASE, 45.0, "Gusset_Left_Diag2")
    # Left gusset top cuts
    cp.add_crease(Point2D(x_glue, y_roof_top + 10.0), Point2D(x_mid_l, y_roof_top), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_mid_l, y_roof_top), Point2D(x_left, y_roof_top + 10.0), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_glue, y_roof_top + 10.0), Point2D(x_glue, y_body_top), CreaseType.CUT, 0.0)

    # 4. Right Side Triangular Inward Gusset (x_front to x_right)
    x_mid_r = (x_front + x_right) / 2.0
    cp.add_crease(Point2D(x_mid_r, y_body_top), Point2D(x_mid_r, y_roof_top), CreaseType.VALLEY, -90.0, "Gusset_Right_Center")
    cp.add_crease(Point2D(x_front, y_body_top), Point2D(x_mid_r, y_roof_top), CreaseType.CREASE, 45.0, "Gusset_Right_Diag1")
    cp.add_crease(Point2D(x_right, y_body_top), Point2D(x_mid_r, y_roof_top), CreaseType.CREASE, 45.0, "Gusset_Right_Diag2")
    # Right gusset top cuts
    cp.add_crease(Point2D(x_front, y_roof_top + 10.0), Point2D(x_mid_r, y_roof_top), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_mid_r, y_roof_top), Point2D(x_right, y_roof_top + 10.0), CreaseType.CUT, 0.0)

    # 5. Front Roof & Carry Handle (x_left to x_front)
    # Roof to handle hinge crease (counter-folds -45 deg to stand vertical at the ridge)
    cp.add_crease(Point2D(x_left, y_roof_top), Point2D(x_front, y_roof_top), CreaseType.MOUNTAIN, 45.0, "Front_RoofHandle_Hinge")
    # Front handle outer perimeter with rounded shoulders and locking ear
    ear_w = 12.0
    cp.add_crease(Point2D(x_left, y_body_top), Point2D(x_left, y_roof_top + 10.0), CreaseType.CUT, 0.0, "GussetFrontSlit")
    cp.add_crease(Point2D(x_left, y_roof_top + 10.0), Point2D(x_left, y_roof_top), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_left, y_roof_top), Point2D(x_left - ear_w, y_roof_top - hh * 0.4), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_left - ear_w, y_roof_top - hh * 0.4), Point2D(x_left + 15.0, y_handle_top), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_left + 15.0, y_handle_top), Point2D(x_front - 15.0, y_handle_top), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_front - 15.0, y_handle_top), Point2D(x_front + ear_w, y_roof_top - hh * 0.4), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_front + ear_w, y_roof_top - hh * 0.4), Point2D(x_front, y_roof_top), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_front, y_body_top), Point2D(x_front, y_roof_top + 10.0), CreaseType.CUT, 0.0, "FrontRightSlit")
    cp.add_crease(Point2D(x_front, y_roof_top + 10.0), Point2D(x_front, y_roof_top), CreaseType.CUT, 0.0)

    # Front Handle Die-Cut Slot (Oval finger cutout)
    slot_w = 65.0
    slot_h = 22.0
    slot_cx = (x_left + x_front) / 2.0
    slot_cy = y_roof_top - hh * 0.5
    s_x1, s_x2 = slot_cx - slot_w / 2.0, slot_cx + slot_w / 2.0
    s_y1, s_y2 = slot_cy - slot_h / 2.0, slot_cy + slot_h / 2.0
    # Slot boundary cuts
    cp.add_crease(Point2D(s_x1 + 10, s_y1), Point2D(s_x2 - 10, s_y1), CreaseType.CUT, 0.0, "HandleSlot_Top")
    cp.add_crease(Point2D(s_x2 - 10, s_y1), Point2D(s_x2, slot_cy), CreaseType.CUT, 0.0, "HandleSlot_R1")
    cp.add_crease(Point2D(s_x2, slot_cy), Point2D(s_x2 - 10, s_y2), CreaseType.CUT, 0.0, "HandleSlot_R2")
    cp.add_crease(Point2D(s_x2 - 10, s_y2), Point2D(s_x1 + 10, s_y2), CreaseType.CUT, 0.0, "HandleSlot_Bottom")
    cp.add_crease(Point2D(s_x1 + 10, s_y2), Point2D(s_x1, slot_cy), CreaseType.CUT, 0.0, "HandleSlot_L1")
    cp.add_crease(Point2D(s_x1, slot_cy), Point2D(s_x1 + 10, s_y1), CreaseType.CUT, 0.0, "HandleSlot_L2")

    # 6. Back Roof & Carry Handle (x_right to x_back)
    cp.add_crease(Point2D(x_right, y_roof_top), Point2D(x_back, y_roof_top), CreaseType.MOUNTAIN, 45.0, "Back_RoofHandle_Hinge")
    cp.add_crease(Point2D(x_right, y_body_top), Point2D(x_right, y_roof_top + 10.0), CreaseType.CUT, 0.0, "RightBackSlit")
    cp.add_crease(Point2D(x_right, y_roof_top + 10.0), Point2D(x_right, y_roof_top), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_right, y_roof_top), Point2D(x_right - ear_w, y_roof_top - hh * 0.4), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_right - ear_w, y_roof_top - hh * 0.4), Point2D(x_right + 15.0, y_handle_top), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_right + 15.0, y_handle_top), Point2D(x_back - 15.0, y_handle_top), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_back - 15.0, y_handle_top), Point2D(x_back + ear_w, y_roof_top - hh * 0.4), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_back + ear_w, y_roof_top - hh * 0.4), Point2D(x_back, y_roof_top), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x_back, y_roof_top), Point2D(x_back, y_body_top), CreaseType.CUT, 0.0)

    # Back Handle Die-Cut Slot
    b_slot_cx = (x_right + x_back) / 2.0
    bs_x1, bs_x2 = b_slot_cx - slot_w / 2.0, b_slot_cx + slot_w / 2.0
    cp.add_crease(Point2D(bs_x1 + 10, s_y1), Point2D(bs_x2 - 10, s_y1), CreaseType.CUT, 0.0, "BackSlot_Top")
    cp.add_crease(Point2D(bs_x2 - 10, s_y1), Point2D(bs_x2, slot_cy), CreaseType.CUT, 0.0, "BackSlot_R1")
    cp.add_crease(Point2D(bs_x2, slot_cy), Point2D(bs_x2 - 10, s_y2), CreaseType.CUT, 0.0, "BackSlot_R2")
    cp.add_crease(Point2D(bs_x2 - 10, s_y2), Point2D(bs_x1 + 10, s_y2), CreaseType.CUT, 0.0, "BackSlot_Bottom")
    cp.add_crease(Point2D(bs_x1 + 10, s_y2), Point2D(bs_x1, slot_cy), CreaseType.CUT, 0.0, "BackSlot_L1")
    cp.add_crease(Point2D(bs_x1, slot_cy), Point2D(bs_x1 + 10, s_y1), CreaseType.CUT, 0.0, "BackSlot_L2")

    # 7. Glue Tab on Left (Side Seam)
    cp.add_crease(Point2D(x_glue, y_body_top), Point2D(x0 + 4.0, y_body_top + 5.0), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x0 + 4.0, y_body_top + 5.0), Point2D(x0, y_body_top + 10.0), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x0, y_body_top + 10.0), Point2D(x0, y_body_bottom - 10.0), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x0, y_body_bottom - 10.0), Point2D(x0 + 4.0, y_body_bottom - 5.0), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(x0 + 4.0, y_body_bottom - 5.0), Point2D(x_glue, y_body_bottom), CreaseType.CUT, 0.0)

    # Glue Line Annotation (Magenta)
    cp.add_crease(Point2D(x0 + 3.0, y_body_top + 15.0), Point2D(x_glue - 3.0, y_body_top + 15.0), CreaseType.GLUE, 0.0)
    cp.add_crease(Point2D(x0 + 3.0, y_body_bottom - 15.0), Point2D(x_glue - 3.0, y_body_bottom - 15.0), CreaseType.GLUE, 0.0)

    # 8. Bottom Closure (Automatic 1-2-3 Snap Lock Style Flaps)
    # Left & Right dust flaps (trapezoidal)
    for px1, px2 in [(x_glue, x_left), (x_front, x_right)]:
        cp.add_crease(Point2D(px1, y_body_bottom), Point2D(px1 + 8.0, y_body_bottom + bottom_flap_h * 0.8), CreaseType.CUT, 0.0)
        cp.add_crease(Point2D(px1 + 8.0, y_body_bottom + bottom_flap_h * 0.8), Point2D(px2 - 8.0, y_body_bottom + bottom_flap_h * 0.8), CreaseType.CUT, 0.0)
        cp.add_crease(Point2D(px2 - 8.0, y_body_bottom + bottom_flap_h * 0.8), Point2D(px2, y_body_bottom), CreaseType.CUT, 0.0)

    # Front & Back bottom lock flaps (interlocking with 45 degree notch)
    for px1, px2 in [(x_left, x_front), (x_right, x_back)]:
        mid_x = (px1 + px2) / 2.0
        cp.add_crease(Point2D(px1, y_body_bottom), Point2D(px1 + 5.0, y_bottom_flaps), CreaseType.CUT, 0.0)
        cp.add_crease(Point2D(px1 + 5.0, y_bottom_flaps), Point2D(mid_x - 10.0, y_bottom_flaps), CreaseType.CUT, 0.0)
        # Lock notch
        cp.add_crease(Point2D(mid_x - 10.0, y_bottom_flaps), Point2D(mid_x, y_bottom_flaps - 15.0), CreaseType.CUT, 0.0)
        cp.add_crease(Point2D(mid_x, y_bottom_flaps - 15.0), Point2D(mid_x + 10.0, y_bottom_flaps), CreaseType.CUT, 0.0)
        cp.add_crease(Point2D(mid_x + 10.0, y_bottom_flaps), Point2D(px2 - 5.0, y_bottom_flaps), CreaseType.CUT, 0.0)
        cp.add_crease(Point2D(px2 - 5.0, y_bottom_flaps), Point2D(px2, y_body_bottom), CreaseType.CUT, 0.0)

    # Base Facet
    cp.add_facet("FrontBody", [Point2D(x_left, y_body_top), Point2D(x_front, y_body_top), Point2D(x_front, y_body_bottom), Point2D(x_left, y_body_bottom)], fold_angle_deg=0.0)
    return cp
