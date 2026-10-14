"""Coordinated rigid schedules for cyclic fold graphs: dense seams plus endpoint guards."""
import copy
import math
from origami_cad.fold_closure import (closure_report, clusters, endpoint_report,
                                      loop_closure, rigid_locks)
from origami_cad.fold_continuity import TOLERANCE_MM, _seams, continuity_report
from origami_cad.fold_faces import _extract_fold_model, _unavailable, build_fold_model
from origami_cad.fold_kinematics import least_squares_schedule

__all__ = ['DENSE_SAMPLES', 'apply_schedule', 'build_coordinated_fold_model',
           'closure_report', 'qualify', 'rigid_locks']
DENSE_SAMPLES = [i/100 for i in range(101)]
UNAVAILABLE_COORDINATED = ('3D fold preview not available: no qualified coordinated rigid '
                           'motion keeps every seam joined and closes the blank')


def apply_schedule(model, schedule):
    """Copy the model with one target angle per tree hinge; angle(t) = t * angle_deg."""
    if isinstance(schedule, bool) or not isinstance(schedule, (list, tuple)) \
            or len(schedule) != len(model['hinges']) or any(
                isinstance(a, bool) or not isinstance(a, (int, float)) or not math.isfinite(a)
                for a in schedule):
        raise ValueError('Malformed fold schedule: one finite angle per tree hinge')
    scheduled = copy.deepcopy(model)
    for hinge, angle in zip(scheduled['hinges'], schedule):
        hinge['angle_deg'] = float(angle)
    return scheduled


def dense_samples(samples=None):
    """Requested samples never replace the required 101; they are added to them."""
    if samples is None:
        return list(DENSE_SAMPLES)
    if isinstance(samples, (str, bytes)) or not isinstance(samples, (list, tuple, set)):
        raise ValueError('Progress samples must be a list of numbers within [0, 1]')
    extra = list(samples)
    if not extra or any(isinstance(t, bool) or not isinstance(t, (int, float))
                        or not math.isfinite(t) or not 0 <= t <= 1 for t in extra):
        raise ValueError('Progress samples must be a non-empty list within [0, 1]')
    return sorted(set(DENSE_SAMPLES) | {float(t) for t in extra})


def qualify(model, schedule, samples=None):
    """Dense seam continuity, source endpoint targets, free-edge contact and root loop."""
    candidate = apply_schedule(model, schedule)
    continuity = continuity_report(candidate, dense_samples(samples))
    endpoint = endpoint_report(model, schedule)
    closure = closure_report(candidate)
    loop = loop_closure(model, schedule, closure['contacts'])
    valid = continuity['valid'] and endpoint['valid'] and closure['valid'] and loop['valid']
    return dict(valid=valid, continuity=continuity, endpoint=endpoint, closure=closure,
                loop=loop, schedule_deg=[float(a) for a in schedule], model=candidate)


def _rejection(result):
    continuity = result['continuity']
    if not continuity['valid']:
        return 'seam gap %.3f mm exceeds %.1f mm at progress %s' % (
            continuity['max_gap_mm'], TOLERANCE_MM, continuity['worst']['progress'])
    for key in ('endpoint', 'closure', 'loop'):
        if not result[key]['valid']:
            return result[key]['reason']
    return ''


def _summary(name, result):
    return dict(name=name, valid=result['valid'], schedule_deg=result['schedule_deg'],
                continuity=result['continuity'], endpoint=result['endpoint'],
                closure=result['closure'], loop=result['loop'], rejected=_rejection(result))


def build_coordinated_fold_model(cp, samples=None):
    """Baseline rigid tree when it already qualifies; otherwise coordinated candidates.

    Hinge angle_deg carries the schedule, so renderers keep angle(t) = t * angle_deg
    with the unchanged parent-relative transform rule. Availability needs 101-sample
    seam continuity, source target angles (only proven rigid-cluster hinges at zero),
    a new free-edge contact and a loop through the root body. Zero, flat or relaxed
    motion is never a rescue.
    """
    samples, base = dense_samples(samples), build_fold_model(cp)
    coordination = dict(kind='rigid-schedule', candidate=None, schedule_deg=[], locked=[],
                        endpoint=None, closure=None, loop=None, candidates=[])
    if base['available']:
        schedule = [h['angle_deg'] for h in base['hinges']]
        return dict(base, continuity=continuity_report(base, samples), coordination=dict(
            coordination, candidate='source', schedule_deg=schedule,
            endpoint=endpoint_report(base, schedule), closure=closure_report(base),
            loop=loop_closure(base, schedule)))
    extracted = _extract_fold_model(cp)
    if not extracted['available']:
        return dict(extracted, coordination=coordination)
    cluster, locks = clusters(extracted)
    source = [h['angle_deg'] for h in extracted['hinges']]
    locked = [0.0 if cluster[h['parent']] == cluster[h['child']] else a
              for h, a in zip(extracted['hinges'], source)]
    free = [i for i, (a, b) in enumerate(zip(source, locked)) if a == b]
    candidates = [('source', lambda: source)] + \
        ([('locked-seams', lambda: locked)] if locked != source else []) + \
        ([('least-squares', lambda: least_squares_schedule(
            extracted, _seams(extracted), locked, free))] if free else [])
    results, tried = [], []
    for name, make in candidates:
        schedule = make()
        if schedule in tried:
            continue
        tried.append(schedule)
        result = qualify(extracted, schedule, samples)
        results.append(_summary(name, result))
        if result['valid']:
            return dict(result['model'], status='', continuity=result['continuity'],
                        coordination=dict(coordination, candidate=name, locked=locks,
                                          schedule_deg=result['schedule_deg'],
                                          endpoint=result['endpoint'], closure=result['closure'],
                                          loop=result['loop'], candidates=results))
    model = _unavailable(UNAVAILABLE_COORDINATED)
    model['continuity'] = results[0]['continuity']
    model['coordination'] = dict(coordination, locked=locks, candidates=results)
    return model
