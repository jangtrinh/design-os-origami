"""Four-wall glued food tray with a hinged lid, inside side flaps and a front tuck."""
from origami_cad.geometry import OrigamiCreasePattern, Point2D, CreaseType
from origami_cad.packaging_rectangular_blank import (
    add_cut_chain, build_four_wall_tray, tray_dimensions, validate_box_arguments)


def generate_food_box(
    width: float = 160.0,
    depth: float = 120.0,
    height: float = 70.0,
    thickness: float = 0.5,
    fit_clearance: float = 1.0,
) -> OrigamiCreasePattern:
    """Cake/food box: tray with corner glue tabs plus a lid hinged on the back wall.

    The lid is inset by caliper + fit_clearance per side so its side flaps hang inside the
    end walls; the front tuck flap folds inside the front wall. Inside dimensions in mm.
    """
    validate_box_arguments(width, depth, height, thickness, fit_clearance)
    cp = OrigamiCreasePattern(name=f"FoodBoxHingedLid_{int(width)}x{int(depth)}x{int(height)}",
                              thickness_mm=thickness)
    dims = tray_dimensions(cp, width, depth, height)
    w, d, h = dims["floor_w"], dims["floor_d"], dims["height"]
    inset = thickness + fit_clearance
    lid_w = w - 2 * inset
    if lid_w <= 0:
        raise ValueError(f"width {width} mm is too small for a lid inset of {inset} mm per side")
    flap = min(0.6 * height, 25.0)                 # lid side flaps and front tuck depth
    shoulder = min(flap, lid_w / 4.0)              # tuck flap chamfer
    flap_chamfer = 0.3 * min(flap, d)
    y_top, y_lid = -h, -h - d                      # back wall top edge; lid front edge
    build_four_wall_tray(cp, dims)
    cp.add_crease(Point2D(inset, y_top), Point2D(w - inset, y_top), CreaseType.CREASE, 90.0, "LidHinge")
    cp.add_crease(Point2D(inset, y_top), Point2D(inset, y_lid), CreaseType.CREASE, 90.0, "LidFlapHinge_Left")
    cp.add_crease(Point2D(w - inset, y_top), Point2D(w - inset, y_lid), CreaseType.CREASE, 90.0, "LidFlapHinge_Right")
    cp.add_crease(Point2D(inset, y_lid), Point2D(w - inset, y_lid), CreaseType.CREASE, 90.0, "TuckHinge")
    cp.cut_slits.update({
        f"LidFlapSlit_{side}": "Separates the lid side flap from the back wall's top edge inside "
                               "the lid inset; runs from the outline to the lid hinge corner."
        for side in ("Left", "Right")})
    for side, x_wall, direction in (("Left", 0.0, 1.0), ("Right", w, -1.0)):
        x_hinge = x_wall + direction * inset       # lid flap hinge
        x_outer = x_hinge - direction * flap       # lid flap outer edge
        # The back wall's top stub under the flap is a slit; any part beyond the wall is outline.
        split = x_wall if (x_outer - x_wall) * direction < 0 else x_outer
        if abs(split - x_wall) > 1e-9:
            cp.add_crease(Point2D(x_wall, y_top), Point2D(split, y_top), CreaseType.CUT, 0.0, f"LidStub_{side}")
        cp.add_crease(Point2D(split, y_top), Point2D(x_hinge, y_top), CreaseType.CUT, 0.0, f"LidFlapSlit_{side}")
        if abs(x_outer - split) > 1e-9:
            cp.add_crease(Point2D(split, y_top), Point2D(x_outer, y_top), CreaseType.CUT, 0.0, f"LidFlapBottom_{side}")
        add_cut_chain(cp, [Point2D(x_outer, y_top), Point2D(x_outer, y_lid + flap_chamfer),
                           Point2D(x_outer + direction * flap_chamfer, y_lid), Point2D(x_hinge, y_lid)],
                      f"LidFlapEdge_{side}_")
    add_cut_chain(cp, [Point2D(inset, y_lid), Point2D(inset + shoulder, y_lid - flap),
                       Point2D(w - inset - shoulder, y_lid - flap), Point2D(w - inset, y_lid)], "TuckFlap_")
    cp.add_facet("Lid", [Point2D(inset, y_top), Point2D(w - inset, y_top),
                         Point2D(w - inset, y_lid), Point2D(inset, y_lid)])
    return cp
