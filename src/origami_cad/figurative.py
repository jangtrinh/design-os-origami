"""Figurative (non-packaging) origami crease patterns built on flat-foldable bases."""

import math
from origami_cad.geometry import OrigamiCreasePattern, Point2D, CreaseType


def generate_deer_bird_base(size: float = 200.0, thickness: float = 0.1) -> OrigamiCreasePattern:
    """
    Square-sheet bird-base crease pattern used as the skeleton of the origami deer:
    4 long flaps become the legs/neck/tail by later reverse folds (head, antlers and
    hooves are step-folds, not part of this flat pattern). Every interior vertex
    satisfies Kawasaki/Maekawa (verified in tests).
    """
    cp = OrigamiCreasePattern(name=f"DeerBirdBase_{int(size)}", thickness_mm=thickness)
    s, m = size, size / 2.0
    a = m * math.tan(math.radians(22.5))
    P = Point2D

    def seg(p, q, kind, ang, label):
        cp.add_crease(p, q, kind, ang, label)

    # Sheet outline
    corners = [P(0, 0), P(s, 0), P(s, s), P(0, s)]
    for i in range(4):
        seg(corners[i], corners[(i + 1) % 4], CreaseType.CUT, 0.0, "Sheet")

    # Midlines (valley), split at the 22.5° nodes
    for x_fixed in (True, False):
        pts = [0.0, a, m, s - a, s]
        for u, v in zip(pts, pts[1:]):
            p, q = (P(m, u), P(m, v)) if x_fixed else (P(u, m), P(v, m))
            seg(p, q, CreaseType.VALLEY, -180.0, "Midline")

    # Diagonals (mountain), split at (a, a) nodes
    for flip in (False, True):
        pts = [0.0, a, m, s - a, s]
        for u, v in zip(pts, pts[1:]):
            p, q = (P(u, u), P(v, v)) if not flip else (P(u, s - u), P(v, s - v))
            seg(p, q, CreaseType.MOUNTAIN, 180.0, "Diagonal")

    # Per corner: two 22.5° kite lines and the two short petal lines to the (a,a) node
    for cx, cy, sx, sy in [(0, 0, 1, 1), (s, 0, -1, 1), (s, s, -1, -1), (0, s, 1, -1)]:
        c = P(cx, cy)
        n1, n2 = P(m, cy + sy * a), P(cx + sx * a, m)
        node = P(cx + sx * a, cy + sy * a)
        seg(c, n1, CreaseType.VALLEY, -180.0, "KiteFold")
        seg(c, n2, CreaseType.VALLEY, -180.0, "KiteFold")
        seg(node, n1, CreaseType.MOUNTAIN, 180.0, "PetalFold")
        seg(node, n2, CreaseType.MOUNTAIN, 180.0, "PetalFold")

    _assign_maekawa_mountain_valley(cp, s)
    cp.add_facet("DeerSheet", corners)
    return cp


def _assign_maekawa_mountain_valley(cp: OrigamiCreasePattern, size: float) -> None:
    """
    Backtracking M/V assignment so every interior vertex has |M - V| = 2 (Maekawa) and
    satisfies Big-Little-Big: a sector strictly smaller than both neighbours must be
    bounded by creases of opposite type. Local conditions only; global foldability and
    layer ordering are NOT verified.
    """
    cp.split_at_intersections()  # endpoint incidence below is complete only on a split pattern
    fold_types = (CreaseType.MOUNTAIN, CreaseType.VALLEY, CreaseType.CREASE)
    fold_ids = [i for i, c in enumerate(cp.creases) if c.crease_type in fold_types]
    at_vertex = {}
    for i in fold_ids:
        for p in (cp.creases[i].p1, cp.creases[i].p2):
            at_vertex.setdefault((round(p.x, 4), round(p.y, 4)), []).append(i)
    interior_keys = [k for k in at_vertex if min(k[0], k[1], size - k[0], size - k[1]) > 1e-6]
    interior = [at_vertex[k] for k in interior_keys]
    differ = _big_little_big_pairs(cp, at_vertex, interior_keys)
    sign = {}

    def feasible() -> bool:
        for e1, e2 in differ:
            if e1 in sign and e2 in sign and sign[e1] == sign[e2]:
                return False
        for edges in interior:
            known = [sign[e] for e in edges if e in sign]
            if abs(sum(known)) - (len(edges) - len(known)) > 2:
                return False
            if len(known) == len(edges) and abs(sum(known)) != 2:
                return False
        return True

    def solve(k: int) -> bool:
        if k == len(fold_ids):
            return True
        for val in (1, -1):
            sign[fold_ids[k]] = val
            if feasible() and solve(k + 1):
                return True
            del sign[fold_ids[k]]
        return False

    if not solve(0):
        raise ValueError("no Maekawa-consistent mountain/valley assignment")
    for i, val in sign.items():
        c = cp.creases[i]
        c.crease_type = CreaseType.MOUNTAIN if val > 0 else CreaseType.VALLEY
        c.target_angle_deg = 180.0 if val > 0 else -180.0


def _big_little_big_pairs(cp, at_vertex, keys):
    """Crease-index pairs that must differ in M/V (Big-Little-Big) at the given vertices."""
    pairs = []
    for key in keys:
        ring = []
        for i in at_vertex[key]:
            c = cp.creases[i]
            other = c.p2 if (round(c.p1.x, 4), round(c.p1.y, 4)) == key else c.p1
            ring.append((math.degrees(math.atan2(other.y - key[1], other.x - key[0])) % 360.0, i))
        ring.sort()
        n = len(ring)
        sectors = [(ring[(k + 1) % n][0] - ring[k][0]) % 360.0 for k in range(n)]
        for k in range(n):
            if sectors[k] < sectors[k - 1] - 1e-6 and sectors[k] < sectors[(k + 1) % n] - 1e-6:
                pairs.append((ring[k][1], ring[(k + 1) % n][1]))
    return pairs
