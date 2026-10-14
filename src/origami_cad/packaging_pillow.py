"""Curved-end tube geometry with hinges clipped to the sampled cuts."""
import math
from origami_cad.packaging_constraints import validate_glue_flap
from origami_cad.fold_graph import EPS as GEOMETRY_EPS
from origami_cad.geometry import OrigamiCreasePattern, Point2D, CreaseType


def generate_pillow_box(
    width: float = 90.0,
    depth: float = 40.0,
    height: float = 110.0,
    thickness: float = 0.5,
    glue_flap_width: float = 12.0,
) -> OrigamiCreasePattern:
    """
    Generates a Pillow Box dieline: one-piece tube with a glue flap whose top and bottom
    edges are curved (arc-approximated) so the ends bow inward and lock without adhesive.
    """
    cp = OrigamiCreasePattern(name=f"PillowBox_{int(width)}x{int(depth)}x{int(height)}", thickness_mm=thickness)
    c_allow = cp.calculate_score_allowance(90.0)
    w, d, h = width + c_allow, depth + c_allow, height
    validate_glue_flap(glue_flap_width, d)

    # Panels along X: Glue -> Front (W) -> Side (D) -> Back (W) -> Side (D)
    xs = [0.0, glue_flap_width]
    for span in (w, d, w, d):
        xs.append(xs[-1] + span)
    bow = min(d * 0.35, 12.0)  # inward bow depth of the curved end edges
    segs = 12

    def end_inset(x):
        # Intersect the vertical hinge with the actual piecewise-linear CUT,
        # not the smooth parabola between sampled vertices.
        t = (x - xs[1]) / (xs[-1] - xs[1])
        k = min(int(t * segs), segs - 1)
        a, b = k / segs, (k + 1) / segs
        fraction = (t - a) / (b - a)
        return bow * ((1 - fraction) * 4 * a * (1 - a) + fraction * 4 * b * (1 - b))

    # Vertical creases terminate on the curved cut boundary.
    for i, x in enumerate(xs[1:-1]):
        inset = end_inset(x)
        cp.add_crease(Point2D(x, inset), Point2D(x, h - inset), CreaseType.CREASE, 90.0, f"Hinge_{i}")

    # Mirror the receiving side's sampled CUT profile onto the glue flap. A
    # rectangular flap overhangs that curved wall even when its width fits.
    total = xs[-1] - xs[1]
    knot_precision = GEOMETRY_EPS * max(1.0, math.hypot(total / segs, bow))
    sample_xs = [xs[1] + k * total / segs for k in range(1, segs)]

    # Build top and bottom curves across the 4 body panels:
    # Front (xs[1]..xs[2]) and Back (xs[3]..xs[4]) carry outward-arching pillow
    # end-closure flaps with straight score hinges; Side panels (xs[2]..xs[3] and
    # xs[4]..xs[5]) keep the exact sampled inward curve for glue-flap containment.
    flap_bow = max(d * 0.45, 8.0)
    flap_segs = 6
    for panel_idx in range(4):
        xa, xb = xs[panel_idx + 1], xs[panel_idx + 2]
        ya_top, yb_top = end_inset(xa), end_inset(xb)
        ya_bot, yb_bot = h - ya_top, h - yb_top
        if panel_idx in (0, 2):
            for end_name, ya, yb, out_sign in (("Top", ya_top, yb_top, -1.0),
                                               ("Bottom", ya_bot, yb_bot, 1.0)):
                cp.add_crease(Point2D(xa, ya), Point2D(xb, yb),
                              CreaseType.CREASE, 90.0, f"PillowEndHinge_{end_name}_{panel_idx}")
                prev_pt = Point2D(xa, ya)
                for k in range(1, flap_segs + 1):
                    u = k / flap_segs
                    px = (1.0 - u) * xa + u * xb
                    py = (1.0 - u) * ya + u * yb + out_sign * flap_bow * 4.0 * u * (1.0 - u)
                    cur_pt = Point2D(px, py)
                    cp.add_crease(prev_pt, cur_pt, CreaseType.CUT, 0.0, "CurvedEnd")
                    prev_pt = cur_pt
        else:
            panel_xs = [xa, *[x for x in sample_xs if xa + knot_precision < x < xb - knot_precision], xb]
            top_pts = [Point2D(x, end_inset(x)) for x in panel_xs]
            bot_pts = [Point2D(p.x, h - p.y) for p in top_pts]
            for chain in (top_pts, bot_pts):
                for p1, p2 in zip(chain, chain[1:]):
                    cp.add_crease(p1, p2, CreaseType.CUT, 0.0, "CurvedEnd")

    distances = sorted({0.0, glue_flap_width, *(
        xs[-1] - (xs[1] + k * total / segs) for k in range(1, segs)  # endpoints are already explicit; do not subtract them
        if 0 < xs[-1] - (xs[1] + k * total / segs) < glue_flap_width)})
    # Bound the material edge to the preceding exact curve knot if the last
    # interval cannot be resolved at the unchanged relative intersection precision.
    if len(distances) > 2 and distances[-1] - distances[-2] <= knot_precision:
        distances.pop()
    top = [Point2D(xs[1] - distance, end_inset(xs[-1] - distance)) for distance in distances]
    bottom = [Point2D(p.x, h - p.y) for p in top]
    for label, chain in (("GlueFlapTop", top), ("GlueFlapBottom", bottom)):
        for a, b in zip(chain, chain[1:]):
            cp.add_crease(a, b, CreaseType.CUT, 0.0, label)
    cp.add_crease(top[-1], bottom[-1], CreaseType.CUT, 0.0, "GlueOuterCut")
    cp.add_crease(top[-1], bottom[-1], CreaseType.GLUE, 0.0, "GlueEdge")
    cp.add_crease(Point2D(xs[-1], 0.0), Point2D(xs[-1], h), CreaseType.CUT, 0.0)

    cp.add_facet("PillowFront", [Point2D(xs[1], 0), Point2D(xs[2], 0), Point2D(xs[2], h), Point2D(xs[1], h)])
    return cp
