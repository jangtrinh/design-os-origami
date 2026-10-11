"""Qualify rigid preview motion against every shared uncut material seam."""
import math
from collections import defaultdict
from origami_cad.fold_kinematics import fold_matrices


def _edge_key(axis):
    return tuple(sorted(tuple(round(v, 7) for v in point) for point in axis))


def _seams(model):
    # Reconstruct shared boundaries as well as declared folds: deleting unused
    # fold metadata must not silently remove the material continuity obligation.
    boundaries = defaultdict(set)
    for face in model['faces']:
        for ring in [face['vertices'], *face.get('holes', [])]:
            for a, b in zip(ring, ring[1:] + ring[:1]):
                boundaries[_edge_key([a, b])].add(face['id'])
    cuts = {_edge_key(axis) for axis in model.get('cut_edges', [])}
    seams = set()
    for axis, owners in boundaries.items():
        if axis not in cuts:
            ids = sorted(owners)
            for i, a in enumerate(ids):
                for b in ids[i+1:]:
                    seams.add((a, b, axis))
    for fold in model['hinges'] + model['non_tree_folds']:
        a, b = sorted((fold['parent'], fold['child']))
        if a != b:
            seams.add((a, b, _edge_key(fold['axis'])))
    return sorted(seams)


def continuity_report(model):
    """Check both endpoint copies at the required four progress samples.

    Passing is bounded continuity evidence, not collision or physical closure.
    CUT slits separate material and are deliberately not continuity constraints.
    """
    samples = [.25, .5, .75, 1.0]
    seams = _seams(model)
    maximum, worst = 0.0, None
    for t in samples:
        matrices = fold_matrices(model, t)
        for a, b, axis in seams:
            for point in axis:
                copies = [[sum(matrices[fid][i][j]*v for j, v in
                               enumerate([*point, 0, 1])) for i in range(3)]
                          for fid in (a, b)]
                gap = math.dist(*copies)
                if not math.isfinite(gap):
                    raise ValueError('Nonfinite seam displacement')
                if gap > maximum:
                    maximum = gap
                    worst = dict(progress=t, faces=[a, b], endpoint=list(point))
    return dict(valid=model['available'] and maximum <= .5, tolerance_mm=.5,
                samples=samples, checked_edges=len(seams), max_gap_mm=maximum,
                worst=worst)
