"""Shared four-wall tray blank: floor, walls, corner glue tabs and declared slits."""
import math
from origami_cad.geometry import OrigamiCreasePattern, Point2D, CreaseType

TAB_RELIEF_MM = 1.0  # tab top edge sits this far (plus caliper) below the wall top


def validate_box_arguments(width, depth, height, thickness, fit_clearance):
    """Reject non-finite or non-positive dimensions before any geometry is built."""
    for name, value in (("width", width), ("depth", depth), ("height", height)):
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be a finite positive length in mm, got {value!r}")
    for name, value in (("thickness", thickness), ("fit_clearance", fit_clearance)):
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f"{name} must be a finite non-negative length in mm, got {value!r}")


def add_cut_chain(cp, points, label_prefix=""):
    """Add consecutive CUT segments between points; labels are prefix + index."""
    for i, (a, b) in enumerate(zip(points, points[1:])):
        cp.add_crease(a, b, CreaseType.CUT, 0.0, f"{label_prefix}{i}" if label_prefix else "")


def tray_dimensions(cp, width, depth, height):
    """Floor spans carry the 90 degree score allowance; tabs stay below the wall top."""
    allowance = cp.calculate_score_allowance(90.0)
    floor_w, floor_d = width + allowance, depth + allowance
    relief = TAB_RELIEF_MM + cp.thickness_mm
    tab = min(height - relief, floor_w / 2.0 - cp.thickness_mm)
    if tab <= 0:
        raise ValueError("height and width must leave room for corner glue tabs "
                         f"(height {height} mm, width {width} mm, caliper {cp.thickness_mm} mm)")
    chamfer = 0.3 * min(tab, height)
    return dict(floor_w=floor_w, floor_d=floor_d, height=height, tab=tab, chamfer=chamfer)


def build_four_wall_tray(cp, dims):
    """Floor at the origin, four walls, four end-wall corner tabs folding inside the long walls.

    Emits every outline edge except the back wall's top edge and returns that edge's
    endpoints (left, right) so the caller either closes it as CUT or hangs a lid on it.
    """
    w, d, h, t, c = dims["floor_w"], dims["floor_d"], dims["height"], dims["tab"], dims["chamfer"]
    # Floor hinges: walls fold toward the unprinted side.
    cp.add_crease(Point2D(0, 0), Point2D(w, 0), CreaseType.CREASE, 90.0, "FloorHinge_Back")
    cp.add_crease(Point2D(w, 0), Point2D(w, d), CreaseType.CREASE, 90.0, "FloorHinge_Right")
    cp.add_crease(Point2D(w, d), Point2D(0, d), CreaseType.CREASE, 90.0, "FloorHinge_Front")
    cp.add_crease(Point2D(0, d), Point2D(0, 0), CreaseType.CREASE, 90.0, "FloorHinge_Left")
    # Corner tabs hinge on the end (left/right) walls and fold inside the back/front walls.
    for corner, (x_wall, x_out, y_edge, y_tab) in {
        "LeftBack": (0, -h, 0, -t), "LeftFront": (0, -h, d, d + t),
        "RightBack": (w, w + h, 0, -t), "RightFront": (w, w + h, d, d + t),
    }.items():
        cp.add_crease(Point2D(x_out, y_edge), Point2D(x_wall, y_edge), CreaseType.CREASE, 90.0, f"TabHinge_{corner}")
        cp.add_crease(Point2D(x_wall, y_tab), Point2D(x_wall, y_edge), CreaseType.CUT, 0.0, f"TabSlit_{corner}")
    cp.cut_slits = {f"TabSlit_{corner}": "Separates the corner glue tab from the adjacent long wall; "
                    "runs from the tab outline to the floor corner hinge."
                    for corner in ("LeftBack", "LeftFront", "RightBack", "RightFront")}
    # Outline: right side (back wall right edge -> right tabs -> front wall), bottom, left side.
    right = [Point2D(w, -h), Point2D(w, -t), Point2D(w + h - c, -t), Point2D(w + h, -t + c),
             Point2D(w + h, d + t - c), Point2D(w + h - c, d + t), Point2D(w, d + t), Point2D(w, d + h)]
    add_cut_chain(cp, right, "OutlineRight_")
    add_cut_chain(cp, [Point2D(w, d + h), Point2D(0, d + h)], "OutlineFront_")
    left = [Point2D(0, d + h), Point2D(0, d + t), Point2D(-h + c, d + t), Point2D(-h, d + t - c),
            Point2D(-h, -t + c), Point2D(-h + c, -t), Point2D(0, -t), Point2D(0, -h)]
    add_cut_chain(cp, left, "OutlineLeft_")
    cp.add_facet("Floor", [Point2D(0, 0), Point2D(w, 0), Point2D(w, d), Point2D(0, d)])
    return Point2D(0, -h), Point2D(w, -h)  # back wall top edge, left to right
