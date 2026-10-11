"""Planar arrangement of source CUT and fold segments, without source mutation."""
import math
from collections import defaultdict

EPS = 1e-7
FOLDS = {'CREASE', 'VALLEY', 'MOUNTAIN'}


def area(ring):
    return sum(a[0]*b[1] - b[0]*a[1]
               for a, b in zip(ring, ring[1:] + ring[:1])) / 2


def contains(point, ring):
    x, y = point
    result = False
    for a, b in zip(ring, ring[1:] + ring[:1]):
        if (a[1] > y) != (b[1] > y):
            if x < a[0] + (y-a[1])*(b[0]-a[0])/(b[1]-a[1]):
                result = not result
    return result


def on_segment(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    length = math.hypot(dx, dy)
    return (length > EPS and abs(dx*(p[1]-a[1])-dy*(p[0]-a[0])) <= EPS*length
            and -EPS*length <= (p[0]-a[0])*dx+(p[1]-a[1])*dy <= length*length+EPS*length)


def validated_segments(lines):
    """Validate raw segments before any splitter can silently discard them."""
    segments = []
    for c in lines:
        a, b = (c.p1.x, c.p1.y), (c.p2.x, c.p2.y)
        if not all(math.isfinite(v) for v in (*a, *b, c.target_angle_deg)):
            raise ValueError('Nonfinite fold geometry')
        if math.dist(a, b) <= EPS:
            raise ValueError('Zero-length segment')
        segments.append((a, b, c))
    return segments


def arrangement(lines):
    """Split X/T contacts, including CUT contacts ignored by the source splitter."""
    vertices, edges = [], {}

    def node(p):
        for i, v in enumerate(vertices):
            if math.dist(p, v) <= EPS:
                return i
        vertices.append(p)
        return len(vertices)-1

    segments = validated_segments(lines)
    for a, b, c in segments:
        points = [a, b]
        dx, dy = b[0]-a[0], b[1]-a[1]
        for e, f, _ in segments:
            points.extend(p for p in (e, f) if on_segment(p, a, b))
            ex, ey = f[0]-e[0], f[1]-e[1]
            den = dx*ey-dy*ex
            if abs(den) <= 1e-12:
                continue
            wx, wy = e[0]-a[0], e[1]-a[1]
            t, u = (wx*ey-wy*ex)/den, (wx*dy-wy*dx)/den
            if -EPS <= t <= 1+EPS and -EPS <= u <= 1+EPS:
                points.append((a[0]+max(0, min(1, t))*dx, a[1]+max(0, min(1, t))*dy))
        nodes = sorted(set(node(p) for p in points), key=lambda i: math.dist(a, vertices[i]))
        for i, j in zip(nodes, nodes[1:]):
            key = tuple(sorted((i, j)))
            if key in edges:
                raise ValueError('Overlapping planar segments')
            edges[key] = c
    return vertices, edges


def rings(vertices, edges):
    """Walk directed half-edges with the bounded face on the left."""
    neighbors = defaultdict(list)
    for a, b in edges:
        neighbors[a].append(b)
        neighbors[b].append(a)
    for a in neighbors:
        neighbors[a].sort(key=lambda b: math.atan2(vertices[b][1]-vertices[a][1],
                                                   vertices[b][0]-vertices[a][0]))
    remaining = {(a, b) for a, b in edges} | {(b, a) for a, b in edges}
    result = []
    while remaining:
        start = min(remaining)
        walk, current = [], start
        while current in remaining:
            remaining.remove(current)
            walk.append(current)
            a, b = current
            fan = neighbors[b]
            current = (b, fan[(fan.index(a)-1) % len(fan)])
        if current != start:
            raise ValueError('Invalid planar walk')
        result.append(walk)
    return result


def left_sample(walk, vertices):
    a, b = (vertices[i] for i in walk[0])
    dx, dy = b[0]-a[0], b[1]-a[1]
    length = math.hypot(dx, dy)
    offset = min(length * 1e-5, 1e-5)
    return ((a[0]+b[0])/2-dy/length*offset, (a[1]+b[1])/2+dx/length*offset)


def simple_ring(walk, vertices):
    """Remove backtracking bridges; they enclose no material and are not hinges."""
    ids = [a for a, _ in walk]
    changed = True
    while changed and len(ids) > 2:
        changed = False
        for i in range(len(ids)):
            if ids[i-1] == ids[(i+1) % len(ids)]:
                ids = [v for j, v in enumerate(ids) if j not in {i, (i+1) % len(ids)}]
                changed = True
                break
    return [list(vertices[i]) for i in ids]
