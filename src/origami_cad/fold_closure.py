"""Endpoint guards for coordinated candidates: rigid locks, source targets, root loops."""
import math
from origami_cad.fold_continuity import TOLERANCE_MM, _edge_key, _seams
from origami_cad.fold_kinematics import fold_matrices, transform_point

LOCK_REASON = 'faces share two seams on distinct lines; any nonzero hinge angle tears one'


def _segment_distance(p, a, b):
    ab = [b[i]-a[i] for i in range(3)]
    length2 = sum(v*v for v in ab)
    u = 0.0 if length2 <= 1e-14 else max(0.0, min(1.0, sum((p[i]-a[i])*ab[i]
                                                           for i in range(3))/length2))
    return math.dist(p, [a[i]+u*ab[i] for i in range(3)])


def _line_of(axis):
    """Collinear split pieces share one line signature; distinct lines lock faces."""
    (ax, ay), (bx, by) = axis
    dx, dy = bx-ax, by-ay
    length = math.hypot(dx, dy)
    dx, dy = dx/length, dy/length
    if dx < -1e-9 or (abs(dx) <= 1e-9 and dy < 0):
        dx, dy = -dx, -dy
    return (round(dx, 7), round(dy, 7), round(ax*dy-ay*dx, 5))


def clusters(model):
    """Union faces joined by two seams on distinct lines until stable; return map, locks."""
    parent = {f['id']: f['id'] for f in model['faces']}

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    seams, locks, merged = _seams(model), [], True
    while merged:
        merged, shared = False, {}
        for a, b, axis in seams:
            ra, rb = find(a), find(b)
            if ra != rb:
                shared.setdefault((min(ra, rb), max(ra, rb)), {})[_line_of(axis)] = (axis, a, b)
        for (ra, rb), lines in sorted(shared.items()):
            if len(lines) >= 2:
                parent[rb] = ra
                locks.append(dict(faces=sorted({f for _, a, b in lines.values() for f in (a, b)}),
                                  axes=[[list(p) for p in axis] for axis, _, _ in lines.values()],
                                  reason=LOCK_REASON))
                merged = True
                break
    return {f: find(f) for f in parent}, locks


def rigid_locks(model):
    """Face pairs rigidly joined by two shared seams on distinct lines, propagated."""
    return clusters(model)[1]


def endpoint_report(model, schedule):
    """Every hinge must end at its source target; only proven rigid-cluster hinges end at 0."""
    cluster, _ = clusters(model)
    source, locked, deviations = [], [], []
    for i, (hinge, angle) in enumerate(zip(model['hinges'], schedule)):
        expected = hinge['angle_deg']
        if cluster[hinge['parent']] == cluster[hinge['child']]:
            locked.append(i)
            expected = 0.0
        source.append(hinge['angle_deg'])
        if abs(float(angle)-expected) > 1e-9:
            deviations.append(dict(hinge=i, faces=[hinge['parent'], hinge['child']],
                                   expected_deg=expected, actual_deg=float(angle)))
    reason = '' if not deviations else (
        '%d hinge angles deviate from source targets or proven locks' % len(deviations))
    return dict(valid=not deviations, locked=locked, source_deg=source,
                deviations=deviations, reason=reason)


def closure_report(model, t=1.0):
    """New coincidences of free CUT edges with other faces' edges at progress t.

    Nontrivial motion evidence only: not collision, glue, thickness or physical fit.
    """
    cuts = {_edge_key(axis) for axis in model.get('cut_edges', [])}
    flat, end = fold_matrices(model, 0.0), fold_matrices(model, t)
    edges = {f['id']: [(a, b) for ring in [f['vertices'], *f.get('holes', [])]
                       for a, b in zip(ring, ring[1:]+ring[:1])] for f in model['faces']}

    def placed(matrices):
        return {fid: [(transform_point(matrices[fid], a), transform_point(matrices[fid], b))
                      for a, b in edges[fid]] for fid in edges}
    moved, rest = placed(end), placed(flat)

    def nearest(fid, p, q, where):
        return min((max(_segment_distance(p, a, b), _segment_distance(q, a, b)), other, (a, b))
                   for other in where if other != fid for a, b in where[other])
    adjacent = {frozenset((a, b)) for a, b, _ in _seams(model)}
    contacts = []
    for fid in edges:
        for k, (a, b) in enumerate(edges[fid]):
            if _edge_key([a, b]) not in cuts:
                continue
            p, q = moved[fid][k]
            gap, other, (c, d) = nearest(fid, p, q, moved)
            if gap <= TOLERANCE_MM and nearest(fid, *rest[fid][k], rest)[0] > TOLERANCE_MM:
                full = max(_segment_distance(c, p, q), _segment_distance(d, p, q)) <= TOLERANCE_MM
                contacts.append(dict(face=fid, other=other, edge=[list(a), list(b)], gap_mm=gap,
                                     full=full, adjacent=frozenset((fid, other)) in adjacent))
    max_move = max((math.dist(p, q) for fid in edges for (p, _), (q, _) in
                    zip(rest[fid], moved[fid])), default=0.0)
    flat_endpoint = all(abs(p[2]) <= TOLERANCE_MM for fid in edges for p, _ in moved[fid])
    angle = max((abs(h['angle_deg']) for h in model['hinges']), default=0.0)
    reason = ('zero motion' if angle <= 1e-9 else 'flat endpoint' if flat_endpoint
              else 'no new free-edge contact' if not contacts else '')
    return dict(valid=not reason, contacts=contacts, flat_endpoint=flat_endpoint,
                max_abs_angle_deg=angle, max_vertex_move_mm=max_move,
                tolerance_mm=TOLERANCE_MM, progress=t, reason=reason)


def loop_closure(model, schedule, contacts=None):
    """A full free-edge coincidence between non-adjacent faces whose tree path crosses the root.

    One incidental touch between neighbouring flaps is not container closure; the loop
    must run through the root body with at least three hinges.
    """
    scheduled = dict(model, hinges=[dict(h, angle_deg=float(a))
                                    for h, a in zip(model['hinges'], schedule)])
    if contacts is None:
        contacts = closure_report(scheduled)['contacts']
    parent = {h['child']: h['parent'] for h in model['hinges']}

    def ancestry(fid):
        path = [fid]
        while path[-1] in parent:
            path.append(parent[path[-1]])
        return path
    loops = []
    for contact in contacts:
        if not contact['full'] or contact['adjacent']:
            continue
        up, down = ancestry(contact['face']), ancestry(contact['other'])
        common = next(f for f in up if f in down)
        path = up[:up.index(common)+1] + list(reversed(down[:down.index(common)]))
        if common == model['root'] and len(path) >= 4:
            loops.append(dict(face=contact['face'], other=contact['other'], path=path,
                              full=True, gap_mm=contact['gap_mm']))
    reason = '' if loops else 'no full free-edge coincidence closes a loop through the root body'
    return dict(valid=bool(loops), loops=loops, reason=reason)
