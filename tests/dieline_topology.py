"""Independent, stdlib-only segment topology checks in source millimetres."""
from collections import defaultdict
from itertools import combinations

from origami_cad.geometry import Point2D, CreaseType
from test_production_geometry import overlap_length, FOLDS

EPS = 1e-7


def on_segment(p, line):
    if line.length <= EPS:
        return p.distance_to(line.p1) <= EPS
    dx, dy = line.p2.x - line.p1.x, line.p2.y - line.p1.y
    px, py = p.x - line.p1.x, p.y - line.p1.y
    return (abs(dx * py - dy * px) / line.length <= EPS and
            -EPS * line.length <= px * dx + py * dy <= line.length ** 2 + EPS * line.length)


def crossing(a, b):
    dx, dy = a.p2.x - a.p1.x, a.p2.y - a.p1.y
    ex, ey = b.p2.x - b.p1.x, b.p2.y - b.p1.y
    den = dx * ey - dy * ex
    if abs(den) <= 1e-12:
        return None
    wx, wy = b.p1.x - a.p1.x, b.p1.y - a.p1.y
    t, u = (wx * ey - wy * ex) / den, (wx * dy - wy * dx) / den
    if -EPS <= t <= 1 + EPS and -EPS <= u <= 1 + EPS:
        return Point2D(a.p1.x + t * dx, a.p1.y + t * dy)
    return None


def segment_graph(cuts):
    """Split at X/T junctions; never close gaps or round to SVG precision."""
    graph, vertices = defaultdict(list), []

    def key(p):
        for i, v in enumerate(vertices):
            if p.distance_to(v) <= EPS:
                return i
        vertices.append(p)
        return len(vertices) - 1

    for c in cuts:
        if c.length <= EPS:
            continue
        points = [c.p1, c.p2]
        for other in cuts:
            points.extend(p for p in (other.p1, other.p2) if on_segment(p, c))
            p = crossing(c, other)
            if p is not None:
                points.append(p)
        nodes = sorted(set(key(p) for p in points), key=lambda i: c.p1.distance_to(vertices[i]))
        for a, b in zip(nodes, nodes[1:]):
            graph[a].append(b)
            graph[b].append(a)
    return graph, vertices


def cycle_rank(cuts):
    """Bounded faces E-V+C; an added face severs a piece from the material."""
    graph, _ = segment_graph(cuts)
    unseen, components = set(graph), 0
    while unseen:
        components += 1
        stack = [unseen.pop()]
        while stack:
            for node in graph[stack.pop()]:
                if node in unseen:
                    unseen.remove(node)
                    stack.append(node)
    return sum(map(len, graph.values())) // 2 - len(graph) + components


def cut_loops(cuts):
    if any(c.length <= EPS for c in cuts):
        return [], ["zero-length CUT"]
    graph, vertices = segment_graph(cuts)
    bad = [(vertices[v], len(edges)) for v, edges in graph.items() if len(edges) != 2]
    if not graph or bad:
        return [], bad or ["empty CUT outline"]
    loops, unseen = [], set(graph)
    while unseen:
        start = next(iter(unseen))
        loop, previous, current = [], None, start
        while True:
            loop.append(vertices[current])
            unseen.discard(current)
            nxt = next(v for v in graph[current] if v != previous)
            previous, current = current, nxt
            if current == start:
                break
        if len(loop) < 3:
            return [], ["degenerate CUT loop"]
        loops.append(loop)
    return loops, []


def inside(p, loops, cuts):
    if any(on_segment(p, c) for c in cuts):
        return True
    # Even/odd over all closed loops accounts for internal die-cut holes.
    result = False
    for loop in loops:
        for a, b in zip(loop, loop[1:] + loop[:1]):
            if (a.y > p.y) != (b.y > p.y):
                x = a.x + (p.y - a.y) * (b.x - a.x) / (b.y - a.y)
                if p.x < x:
                    result = not result
    return result


def violations(cp):
    cuts = [c for c in cp.creases if c.crease_type == CreaseType.CUT]
    folds = [c for c in cp.creases if c.crease_type in FOLDS]
    declarations = getattr(cp, "cut_slits", {})
    errors = []
    for label, reason in declarations.items():
        if not label or not reason or sum(c.label == label for c in cuts) != 1:
            errors.append((label, "slit declaration must justify exactly one named CUT"))
    outline = [c for c in cuts if c.label not in declarations]
    loops, degree_errors = cut_loops(outline)
    if declarations and cycle_rank(cuts) > cycle_rank(outline):
        errors.append(("declared slits", "sever the blank: added CUT face disconnects material"))
    for c in cuts:
        if c.label in declarations:
            if not any(on_segment(p, edge) for p in (c.p1, c.p2) for edge in outline):
                errors.append((c.label, "slit must reach the closed outline"))
            for p in (c.p1, c.p2):
                if not (inside(p, loops, outline) and
                        any(on_segment(p, edge) for edge in outline + folds)):
                    errors.append((c.label, "slit endpoint must meet outline or fold inside blank"))
    return {
        "cut_closed": degree_errors + errors,
        "fold_on_cut": [(c.label, f.label) for c in cuts for f in folds
                        if overlap_length(c, f, EPS) > 0],
        "fold_outside": [(f.label, p) for f in folds for p in (f.p1, f.p2)
                         if not loops or not inside(p, loops, outline)],
        "cut_overlap": [(a.label, b.label) for a, b in combinations(cuts, 2)
                        if overlap_length(a, b, EPS) > 0],
        "fold_overlap": [(a.label, b.label) for a, b in combinations(folds, 2)
                         if overlap_length(a, b, EPS) > 0],
        "fold_free": [(f.label, p) for f in folds for p in (f.p1, f.p2)
                      if not any(on_segment(p, c) for c in cuts) and
                      not any(on_segment(p, o) for o in folds if o is not f)],
    }
