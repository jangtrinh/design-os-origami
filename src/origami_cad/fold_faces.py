"""Extract actual material faces and a preview hinge tree from a copied dieline."""
import copy
from collections import deque
from origami_cad.fold_graph import (EPS, FOLDS, area, arrangement, contains,
                                    left_sample, rings, simple_ring, validated_segments)
from origami_cad.fold_continuity import continuity_report

UNAVAILABLE = '3D fold preview not available for this pattern'


def _unavailable(status=UNAVAILABLE):
    return dict(available=False, status=status, faces=[], root=None,
                hinges=[], non_tree_folds=[])


def _cut_rings(cp):
    declarations = getattr(cp, 'cut_slits', {})
    cuts = [c for c in cp.creases if c.crease_type == 'CUT' and c.label not in declarations]
    vertices, edges = arrangement(cuts)
    degrees = {i: 0 for edge in edges for i in edge}
    for a, b in edges:
        degrees[a] += 1
        degrees[b] += 1
    if not degrees or any(n != 2 for n in degrees.values()):
        raise ValueError('Open or branching CUT contour')
    loops = [simple_ring(w, vertices) for w in rings(vertices, edges)]
    return [r for r in loops if area(r) > EPS]


def _material_faces(vertices, edges, loops):
    faces, owners, hole_walks = [], {}, []
    for walk in rings(vertices, edges):
        ring = simple_ring(walk, vertices)
        signed = area(ring)
        sample = left_sample(walk, vertices)
        if abs(signed) <= EPS or sum(contains(sample, r) for r in loops) % 2 != 1:
            continue
        if signed < 0:
            hole_walks.append((walk, ring, sample))
            continue
        fid = len(faces)
        faces.append(dict(id=fid, vertices=ring, area_mm2=signed))
        owners.update({edge: fid for edge in walk})
    for walk, ring, sample in hole_walks:
        candidates = [f for f in faces if contains(sample, f['vertices'])]
        if not candidates:
            raise ValueError('Hole without enclosing material')
        face = min(candidates, key=lambda f: f['area_mm2'])
        face.setdefault('holes', []).append(ring)
        face['area_mm2'] += area(ring)
        owners.update({edge: face['id'] for edge in walk})
    return faces, owners


def _hinge(a, b, c, vertices, owners):
    return dict(parent=owners.get((a, b)), child=owners.get((b, a)),
                axis=[list(vertices[a]), list(vertices[b])],
                angle_deg=abs(c.target_angle_deg) * (-1 if c.crease_type == 'MOUNTAIN' else 1),
                crease_type=c.crease_type.value)


def _tree(faces, vertices, edges, owners):
    root = max(faces, key=lambda f: f['area_mm2'])['id']
    adjacent = {f['id']: [] for f in faces}
    folds = []
    for (a, b), c in edges.items():
        if c.crease_type not in FOLDS:
            continue
        index = len(folds)
        forward = _hinge(a, b, c, vertices, owners)
        folds.append(forward)
        parent, child = forward['parent'], forward['child']
        if parent is None or child is None:
            raise ValueError('Fold edge outside material or on CUT boundary')
        if parent is not None and child is not None and parent != child:
            adjacent[parent].append((index, forward))
            adjacent[child].append((index, _hinge(b, a, c, vertices, owners)))
    seen, used, queue, hinges = {root}, set(), deque([root]), []
    while queue:
        for index, hinge in adjacent[queue.popleft()]:
            child = hinge['child']
            if child not in seen:
                seen.add(child)
                used.add(index)
                hinges.append(hinge)
                queue.append(child)
    if len(seen) != len(faces):
        raise ValueError('Material faces are not fold-connected')
    return root, hinges, [f for i, f in enumerate(folds) if i not in used]


def _extract_fold_model(cp):
    """Unqualified extraction candidate; callers must validate seam continuity.

    +Z is printed/front. Axis follows the parent's CCW boundary (interior left).
    CREASE/VALLEY use positive RH magnitude toward -Z, MOUNTAIN the opposite.
    Source target signs are historical direction hints; type owns direction here.
    """
    if any(token in cp.name.lower() for token in ('miura', 'deer')):
        return _unavailable()
    try:
        copied = copy.deepcopy(cp)
        validated_segments(c for c in copied.creases if c.crease_type in FOLDS | {'CUT'})
        copied.split_at_intersections()
        loops = _cut_rings(copied)
        lines = [c for c in copied.creases if c.crease_type in FOLDS | {'CUT'}]
        vertices, edges = arrangement(lines)
        faces, owners = _material_faces(vertices, edges, loops)
        if not faces:
            raise ValueError('No material faces')
        # Even/odd containment handles holes, including nested material islands.
        blank = sum(area(r) * (-1 if sum(contains(r[0], other) for other in loops
                                        if other is not r) % 2 else 1) for r in loops)
        if abs(sum(f['area_mm2'] for f in faces) - blank) > max(1e-5, blank*1e-9):
            raise ValueError('Incomplete material coverage')
        root, hinges, unused = _tree(faces, vertices, edges, owners)
        return dict(available=True, status='', faces=faces, root=root,
                    hinges=hinges, non_tree_folds=unused,
                    cut_edges=[[list(vertices[a]), list(vertices[b])]
                               for (a, b), c in edges.items() if c.crease_type == 'CUT'])
    except (ValueError, OverflowError, ArithmeticError):
        return _unavailable()


def build_fold_model(cp):
    """JSON-safe preview, available only when sampled uncut seams stay joined."""
    model = _extract_fold_model(cp)
    if model['available']:
        try:
            report = continuity_report(model)
        except (ValueError, ArithmeticError):
            return _unavailable()
        if not report['valid']:
            model = _unavailable('3D fold preview not available: this pattern '
                                 'needs coordinated or non-rigid folding')
        model['continuity'] = report
    return model
