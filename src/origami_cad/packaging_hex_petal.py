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

        # Asymmetric blooming petal flap (swept outer curve + locking nose)
        tx = edge_dx / edge_len
        ty = edge_dy / edge_len
        petal_h = side * 0.82
        shoulder_l = Point2D(w1.x + tx * (side * 0.12) + nx * (petal_h * 0.55),
                             w1.y + ty * (side * 0.12) + ny * (petal_h * 0.55))
        apex = Point2D((w1.x + w2.x) / 2.0 + tx * (side * 0.14) + nx * petal_h,
                       (w1.y + w2.y) / 2.0 + ty * (side * 0.14) + ny * petal_h)
        shoulder_r = Point2D(w2.x - tx * (side * 0.06) + nx * (petal_h * 0.62),
                             w2.y - ty * (side * 0.06) + ny * (petal_h * 0.62))

        # Outer cut lines for sculpted blooming petal
        cp.add_crease(w1, shoulder_l, CreaseType.CUT, 0.0)
        cp.add_crease(shoulder_l, apex, CreaseType.CUT, 0.0)
        cp.add_crease(apex, shoulder_r, CreaseType.CUT, 0.0)
        cp.add_crease(shoulder_r, w2, CreaseType.CUT, 0.0)

        # Outer side wall cuts (Wall 0 carries a 60-degree side glue tab that bonds inside Wall 5)
        if i == 0:
            glue_w = min(12.0, side * 0.35, height * 0.3)
            taper = glue_w * 0.6
            cp.add_crease(p1, w1, CreaseType.CREASE, 60.0, "HexGlueHinge")
            g1 = Point2D(p1.x - tx * glue_w + nx * taper, p1.y - ty * glue_w + ny * taper)
            g2 = Point2D(w1.x - tx * glue_w - nx * taper, w1.y - ty * glue_w - ny * taper)
            cp.add_crease(p1, g1, CreaseType.CUT, 0.0, "HexGlueCut")
            cp.add_crease(g1, g2, CreaseType.CUT, 0.0, "HexGlueCut")
            cp.add_crease(g2, w1, CreaseType.CUT, 0.0, "HexGlueCut")
            g_mid1 = Point2D((p1.x + g1.x) / 2.0 + nx * taper, (p1.y + g1.y) / 2.0 + ny * taper)
            g_mid2 = Point2D((w1.x + g2.x) / 2.0 - nx * taper, (w1.y + g2.y) / 2.0 - ny * taper)
            cp.add_crease(g_mid1, g_mid2, CreaseType.GLUE, 0.0, "HexGlueLine")
        else:
            cp.add_crease(p1, w1, CreaseType.CUT, 0.0)
        cp.add_crease(p2, w2, CreaseType.CUT, 0.0)

    # Base facet
    cp.add_facet("HexBase", base_pts, fold_angle_deg=0.0)
    return cp
