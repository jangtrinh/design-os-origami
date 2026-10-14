"""Two-piece sleeve and four-wall glued tray; one blank per crease pattern."""
from origami_cad.packaging_constraints import validate_glue_flap
from origami_cad.geometry import OrigamiCreasePattern, Point2D, CreaseType
from origami_cad.packaging_rectangular_blank import (
    add_cut_chain, build_four_wall_tray, tray_dimensions, validate_box_arguments)


def generate_sleeve_tray(
    width: float = 120.0,
    depth: float = 80.0,
    height: float = 35.0,
    thickness: float = 0.5,
    fit_clearance: float = 1.0,
    glue_flap_width: float = 15.0,
):
    """Return (sleeve, tray): a wrapping band and the four-wall tray it slides over.

    width/depth/height are the tray's inside dimensions in mm. The sleeve's inside cross
    section is the tray's outside cross section plus fit_clearance on every side.
    """
    validate_box_arguments(width, depth, height, thickness, fit_clearance)
    stem = f"{int(width)}x{int(depth)}x{int(height)}"
    return (generate_sleeve_blank(width, depth, height, thickness, fit_clearance, glue_flap_width, stem),
            generate_tray_blank(width, depth, height, thickness, stem))


def generate_sleeve_blank(width, depth, height, thickness, fit_clearance, glue_flap_width, stem):
    cp = OrigamiCreasePattern(name=f"TwoPieceSleeve_{stem}", thickness_mm=thickness)
    allowance = cp.calculate_score_allowance(90.0)
    panel_w = width + 2 * thickness + 2 * fit_clearance + allowance   # over the tray's outside width
    panel_h = height + thickness + 2 * fit_clearance + allowance      # over the tray's outside height
    validate_glue_flap(glue_flap_width, panel_h)
    band = depth + 2 * thickness                                      # sleeve length = tray outside depth
    xs = [0.0, glue_flap_width]
    for span in (panel_w, panel_h, panel_w, panel_h):
        xs.append(xs[-1] + span)
    for x, name in zip(xs[1:5], ("GlueTop", "TopSide", "SideBottom", "BottomSide")):
        cp.add_crease(Point2D(x, 0), Point2D(x, band), CreaseType.CREASE, 90.0, f"SleeveHinge_{name}")
    # V thumb notch in the top panel's leading edge for pushing the tray out. A V keeps the
    # closed outline; outward bleed may bridge a notch narrower than its offset.
    notch_depth = min(12.0, band * 0.25)
    notch_width = min(30.0, panel_w * 0.4)
    mid = (xs[1] + xs[2]) / 2.0
    cp.add_crease(Point2D(xs[1], 0), Point2D(mid - notch_width / 2.0, 0), CreaseType.CUT, 0.0, "OutlineTop_0")
    cp.add_crease(Point2D(mid - notch_width / 2.0, 0), Point2D(mid, notch_depth), CreaseType.CUT, 0.0, "ThumbNotch")
    cp.add_crease(Point2D(mid, notch_depth), Point2D(mid + notch_width / 2.0, 0), CreaseType.CUT, 0.0, "ThumbNotch")
    cp.add_crease(Point2D(mid + notch_width / 2.0, 0), Point2D(xs[5], 0), CreaseType.CUT, 0.0, "OutlineTop_1")
    add_cut_chain(cp, [Point2D(xs[5], 0), Point2D(xs[5], band), Point2D(xs[1], band)], "OutlineRightBottom_")
    taper = min(5.0, band / 4.0)
    add_cut_chain(cp, [Point2D(xs[1], band), Point2D(0, band - taper), Point2D(0, taper), Point2D(xs[1], 0)],
                  "GlueFlapEdge_")
    cp.add_crease(Point2D(xs[1] / 2.0, taper), Point2D(xs[1] / 2.0, band - taper), CreaseType.GLUE, 0.0, "SleeveGlue")
    cp.add_facet("SleeveTop", [Point2D(xs[1], 0), Point2D(xs[2], 0), Point2D(xs[2], band), Point2D(xs[1], band)])
    return cp


def generate_tray_blank(width, depth, height, thickness, stem):
    cp = OrigamiCreasePattern(name=f"TwoPieceTray_{stem}", thickness_mm=thickness)
    dims = tray_dimensions(cp, width, depth, height)
    left, right = build_four_wall_tray(cp, dims)
    add_cut_chain(cp, [left, right], "OutlineBack_")
    return cp
