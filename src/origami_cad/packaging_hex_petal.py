"""Hexagonal petal geometry with outward wall normals."""
import math
from origami_cad.geometry import OrigamiCreasePattern, Point2D, CreaseType


def generate_hexagonal_petal_box(
    radius: float = 40.0,
    height: float = 55.0,
    thickness: float = 0.4,
) -> OrigamiCreasePattern:
    """
    Generates a creative Origami Hexagonal Blooming Petal Box (Cosmetic/Gift luxury packaging).
    Features a central regular hexagon base, 6 folding wall panels, and 6 interlocking
    origami petal tabs that spiral close at the top without glue.
    """
    cp = OrigamiCreasePattern(name=f"OrigamiHexPetal_R{int(radius)}_H{int(height)}", thickness_mm=thickness)
    side = radius  # regular hexagon side length equals radius

    # Center at (150, 150)
    cx, cy = 150.0, 150.0

    # Calculate 6 base vertices
    base_pts = []
    for i in range(6):
        ang = math.radians(60 * i - 30)
        base_pts.append(Point2D(cx + radius * math.cos(ang), cy + radius * math.sin(ang)))

    # 1. Base creases around central hexagon (Crease lines)
    for i in range(6):
        p1 = base_pts[i]
        p2 = base_pts[(i + 1) % 6]
        cp.add_crease(p1, p2, CreaseType.CREASE, 90.0, f"BaseHinge_{i}")

    # 2. For each edge, build wall panel extending outward
    for i in range(6):
        p1 = base_pts[i]
        p2 = base_pts[(i + 1) % 6]

        # Normal vector pointing outward
        edge_dx = p2.x - p1.x
        edge_dy = p2.y - p1.y
        edge_len = math.hypot(edge_dx, edge_dy)
        # The base vertices wind counterclockwise: the right normal is outward.
        nx = edge_dy / edge_len
        ny = -edge_dx / edge_len

        # Wall outer corners
        w1 = Point2D(p1.x + nx * height, p1.y + ny * height)
        w2 = Point2D(p2.x + nx * height, p2.y + ny * height)

        # Crease at wall top to petal flap
        cp.add_crease(w1, w2, CreaseType.CREASE, 90.0, f"PetalHinge_{i}")

        # Petal apex (interlocking triangular flap)
        petal_h = side * 0.7
        mid_x = (w1.x + w2.x) / 2.0 + nx * petal_h
        mid_y = (w1.y + w2.y) / 2.0 + ny * petal_h
        apex = Point2D(mid_x, mid_y)

        # Outer cut lines for petal
        cp.add_crease(w1, apex, CreaseType.CUT, 0.0)
        cp.add_crease(apex, w2, CreaseType.CUT, 0.0)

        # Outer side wall cuts
        cp.add_crease(p1, w1, CreaseType.CUT, 0.0)
        cp.add_crease(p2, w2, CreaseType.CUT, 0.0)

    # Base facet
    cp.add_facet("HexBase", base_pts, fold_angle_deg=0.0)
    return cp
