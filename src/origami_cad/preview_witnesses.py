"""Verify saved representative witnesses against the unmodified source geometry."""
import math

from origami_cad.fold_closure import _segment_distance, loop_closure
from origami_cad.fold_continuity import TOLERANCE_MM, _edge_key, _seams
from origami_cad.fold_coordinated import apply_schedule
from origami_cad.fold_faces import _extract_fold_model
from origami_cad.fold_kinematics import fold_matrices, transform_point


def _continuity(report, model, precision):
    if not isinstance(report, dict) or 'worst' not in report:
        return True
    worst = report['worst']
    if worst is None:
        return report['max_gap_mm'] == 0
    a, b = worst['faces']
    point = tuple(worst['endpoint'])
    if (worst['progress'] not in report['samples'] or not any(
            (a, b) == (x, y) and point in axis for x, y, axis in _seams(model))):
        return False
    matrices = fold_matrices(model, worst['progress'])
    gap = math.dist(transform_point(matrices[a], point), transform_point(matrices[b], point))
    return abs(gap - report['max_gap_mm']) <= precision


def _placed_edges(model, progress):
    matrices = fold_matrices(model, progress)
    source = {face['id']: [(a, b) for ring in [face['vertices'], *face.get('holes', [])]
                          for a, b in zip(ring, ring[1:] + ring[:1])]
              for face in model['faces']}
    placed = {fid: [(transform_point(matrices[fid], a), transform_point(matrices[fid], b))
                    for a, b in edges] for fid, edges in source.items()}
    return source, placed


def _gap(p, q, edge):
    return max(_segment_distance(p, *edge), _segment_distance(q, *edge))


def _contacts(report, model, precision):
    if not isinstance(report, dict) or not report.get('contacts'):
        return True
    source, moved = _placed_edges(model, report['progress'])
    _, rest = _placed_edges(model, 0.0)
    cuts = {_edge_key(axis) for axis in model['cut_edges']}
    adjacent = {frozenset((a, b)) for a, b, _ in _seams(model)}
    for contact in report['contacts']:
        fid, other = contact['face'], contact['other']
        if fid not in source or other not in source or fid == other:
            return False
        axis = _edge_key(contact['edge'])
        if axis not in cuts:
            return False
        indices = [i for i, edge in enumerate(source[fid]) if _edge_key(edge) == axis]
        if not indices:
            return False
        i = indices[0]
        p, q = moved[fid][i]
        nearest = min(_gap(p, q, edge) for face in moved if face != fid for edge in moved[face])
        before = min(_gap(*rest[fid][i], edge) for face in rest if face != fid for edge in rest[face])
        if (nearest > TOLERANCE_MM or before <= TOLERANCE_MM or
                abs(nearest - contact['gap_mm']) > precision or
                contact['adjacent'] != (frozenset((fid, other)) in adjacent)):
            return False
        # A different nearest target is permitted only when it is actually tied
        # geometrically and has the same full-edge qualification, without slack
        # at the 0.5 mm contact threshold.
        matches = [edge for edge in moved[other] if _gap(p, q, edge) <= TOLERANCE_MM and
                   abs(_gap(p, q, edge) - contact['gap_mm']) <= precision and
                   (max(_segment_distance(edge[0], p, q), _segment_distance(edge[1], p, q))
                    <= TOLERANCE_MM) == contact['full']]
        if not matches:
            return False
    return True


def _loops(report, closure, model, precision):
    if not isinstance(report, dict) or not report.get('loops'):
        return True
    contacts = closure['contacts']
    angles = [hinge['angle_deg'] for hinge in model['hinges']]
    for loop in report['loops']:
        candidates = [c for c in contacts if c['face'] == loop['face'] and
                      c['other'] == loop['other'] and c['full'] and not c['adjacent'] and
                      abs(c['gap_mm'] - loop['gap_mm']) <= precision]
        if not candidates:
            return False
        proven = loop_closure(model, angles, candidates)['loops']
        if not any(loop['path'] == p['path'] and loop['full'] == p['full'] for p in proven):
            return False
    return True


def witnesses_valid(recorded, regenerated, cp, precision):
    """Validate witnesses before ignoring which member of a numerical tie won."""
    geometry = regenerated
    if not geometry.get('faces') and cp is not None:
        geometry = _extract_fold_model(cp)
    if not _continuity(recorded.get('continuity'), geometry, precision):
        return False
    coordination = recorded.get('coordination')
    if not isinstance(coordination, dict):
        return True
    for summary in [coordination, *coordination.get('candidates', [])]:
        if not any(isinstance(summary.get(key), dict) for key in ('continuity', 'closure', 'loop')):
            continue
        scheduled = apply_schedule(geometry, summary['schedule_deg'])
        if (not _continuity(summary.get('continuity'), scheduled, precision) or
                not _contacts(summary.get('closure'), scheduled, precision) or
                not _loops(summary.get('loop'), summary.get('closure'), scheduled, precision)):
            return False
    return True
