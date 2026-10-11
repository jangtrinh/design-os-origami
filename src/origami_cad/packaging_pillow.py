"""Curved-end tube geometry with hinges clipped to the sampled cuts."""
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
    cp.add_crease(Point2D(xs[0], 0.0), Point2D(xs[0], h), CreaseType.GLUE, 0.0, "GlueEdge")

    # Curved top/bottom cut edges (sagitta bow) across the full strip
    for edge_y, sign in ((0.0, 1.0), (h, -1.0)):
        prev = None
        for k in range(segs + 1):
            t = k / segs
            x = xs[1] + t * (xs[-1] - xs[1])
            y = edge_y + sign * bow * 4 * t * (1 - t)
            pt = Point2D(x, y)
            if prev:
                cp.add_crease(prev, pt, CreaseType.CUT, 0.0, "CurvedEnd")
            prev = pt
    # Glue flap outline (tapered) and outer right edge
    cp.add_crease(Point2D(xs[0], 0.0), Point2D(xs[0], h), CreaseType.CUT, 0.0, "GlueOuterCut")
    cp.add_crease(Point2D(xs[0], 0.0), Point2D(xs[1], 0.0), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(xs[0], h), Point2D(xs[1], h), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(xs[-1], 0.0), Point2D(xs[-1], h), CreaseType.CUT, 0.0)

    cp.add_facet("PillowFront", [Point2D(xs[1], 0), Point2D(xs[2], 0), Point2D(xs[2], h), Point2D(xs[1], h)])
    return cp
