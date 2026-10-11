"""End-to-end gate for a figurative crease pattern: local vertex checks plus the flap-count claim.

Usage: PYTHONPATH=src python3 scripts/e2e_figurative_gate.py [claimed_flaps]
Exit code 1 when any gate fails. Local checks are necessary conditions only; layer ordering,
global foldability and physical behaviour are always reported as NOT VERIFIED.
"""

import math
import sys

from origami_cad.figurative import generate_deer_bird_base
from origami_cad.geometry import CreaseType, Point2D

FOLD = (CreaseType.MOUNTAIN, CreaseType.VALLEY, CreaseType.CREASE)


def interior_vertices(cp, size):
    seen = {}
    for c in cp.creases:
        if c.crease_type in FOLD:
            for p in (c.p1, c.p2):
                seen[(round(p.x, 4), round(p.y, 4))] = p
    return [p for (x, y), p in seen.items() if min(x, y, size - x, size - y) > 1e-6]


def maekawa_and_blb(cp, vertex):
    rays = []
    for c in cp.creases:
        if c.crease_type not in (CreaseType.MOUNTAIN, CreaseType.VALLEY):
            continue
        for a, b in ((c.p1, c.p2), (c.p2, c.p1)):
            if a.distance_to(vertex) < 1e-4:
                rays.append((math.degrees(a.angle_to(b)) % 360.0, c.crease_type))
    rays.sort(key=lambda t: t[0])
    n = len(rays)
    m = sum(1 for _, t in rays if t == CreaseType.MOUNTAIN)
    maekawa = abs(m - (n - m)) == 2
    sectors = [(rays[(i + 1) % n][0] - rays[i][0]) % 360.0 for i in range(n)]
    blb = all(
        rays[i][1] != rays[(i + 1) % n][1]
        for i in range(n)
        if sectors[i] < sectors[i - 1] - 1e-6 and sectors[i] < sectors[(i + 1) % n] - 1e-6
    )
    return maekawa, blb


def main():
    try:
        expected = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    except ValueError:
        print("usage: e2e_figurative_gate.py [claimed_flaps:int]")
        sys.exit(2)
    size = 200.0
    cp = generate_deer_bird_base(size)
    cp.split_at_intersections()  # idempotent here; makes the gate safe for unsplit input
    rows, ok_all = [], True
    verts = interior_vertices(cp, size)
    kaw = [cp.validate_kawasaki_at_vertex(v)[0] for v in verts]
    mk = [maekawa_and_blb(cp, v) for v in verts]
    checks = [
        ("interior vertices enumerated (>0)", len(verts) > 0, f"{len(verts)}"),
        ("Kawasaki + degree rules at every interior vertex", all(kaw), f"{sum(kaw)}/{len(kaw)}"),
        ("Maekawa at every interior vertex", all(m for m, _ in mk), f"{sum(m for m, _ in mk)}/{len(mk)}"),
        ("Big-Little-Big at every interior vertex", all(b for _, b in mk), f"{sum(b for _, b in mk)}/{len(mk)}"),
    ]
    unassigned = sum(1 for c in cp.creases if c.crease_type == CreaseType.CREASE)
    checks.insert(1, ("every fold crease has a mountain/valley assignment", unassigned == 0, f"{unassigned} unassigned"))
    # No flap-realization checker or certificate mechanism exists yet, so a flap-count claim cannot pass.
    checks.append((f"flap-realization certificate for {expected} flaps", False,
                   "NOT VERIFIED: no certificate mechanism; tip counting by labels or corners is not evidence"))
    for name, ok, detail in checks:
        rows.append(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
        ok_all &= ok
    print("\n".join(rows))
    print("NOT VERIFIED: layer ordering, global foldability, collision-free collapse, thickness, deer appearance")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
