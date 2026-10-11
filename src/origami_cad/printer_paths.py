"""Connected source-mm paths and parallel-edge bleed construction."""
import math
from collections import defaultdict
from origami_cad.geometry import Point2D, CreaseType

EPS = 1e-7
FOLDS = {CreaseType.CREASE, CreaseType.MOUNTAIN, CreaseType.VALLEY}


def connected_paths(lines):
    """Follow degree-two chains; branches become separate connected polylines."""
    vertices, graph, edges = [], defaultdict(list), []

    def node(p):
        for i, v in enumerate(vertices):
            if p.distance_to(v) <= EPS:
                return i
        vertices.append(p)
        return len(vertices)-1

    for line in lines:
        if line.length <= EPS:
            raise ValueError('Printer paths cannot contain zero-length segments')
        a, b = node(line.p1), node(line.p2)
        i = len(edges)
        edges.append((a, b))
        graph[a].append(i)
        graph[b].append(i)
    unused, paths = set(range(len(edges))), []

    def walk(start, edge):
        points, current = [vertices[start]], start
        while edge in unused:
            unused.remove(edge)
            a, b = edges[edge]
            current = b if current == a else a
            points.append(vertices[current])
            if current == start:
                return points[:-1], True
            available = [e for e in graph[current] if e in unused]
            if len(graph[current]) != 2 or not available:
                break
            edge = available[0]
        return points, False

    for start in graph:
        if len(graph[start]) != 2:
            for edge in graph[start]:
                if edge in unused:
                    paths.append(walk(start, edge))
    while unused:
        edge = min(unused)
        paths.append(walk(edges[edge][0], edge))
    return paths


def printer_paths(cp):
    declarations = getattr(cp, 'cut_slits', {})
    cuts = [c for c in cp.creases if c.crease_type == CreaseType.CUT]
    outline = connected_paths([c for c in cuts if c.label not in declarations])
    if not outline or any(not closed or len(points) < 3 for points, closed in outline):
        raise ValueError('Printer profile requires closed CUT contours')
    return {
        'cut': outline + connected_paths([c for c in cuts if c.label in declarations]),
        'crease': connected_paths([c for c in cp.creases if c.crease_type in FOLDS]),
        'perforation': connected_paths([c for c in cp.creases if c.crease_type == CreaseType.PERFORATE]),
        'glue': connected_paths([c for c in cp.creases if c.crease_type == CreaseType.GLUE]),
    }


def signed_area(points):
    return sum(a.x*b.y-b.x*a.y for a, b in zip(points, points[1:]+points[:1]))/2


def bleed_outline(points, distance):
    """Miter join of outward parallel edges; offset internal holes separately never."""
    if not math.isfinite(distance) or distance < 0:
        raise ValueError('Bleed must be a finite nonnegative distance in mm')
    area = signed_area(points)
    if abs(area) <= EPS:
        raise ValueError('Degenerate CUT contour')
    from origami_cad.printer_bleed import outward_envelope
    return outward_envelope(points, distance)


def with_bleed(cp, distance):
    if any(not math.isfinite(v) for c in cp.creases for p in (c.p1,c.p2) for v in (p.x,p.y)):
        raise ValueError("Nonfinite printer coordinates")
    paths = printer_paths(cp)
    # Largest closed contour is exterior for the current single-blank generators.
    outer = max((pts for pts, closed in paths['cut'] if closed), key=lambda pts: abs(signed_area(pts)))
    paths['bleed'] = [(bleed_outline(outer, distance), True)]
    return paths
