"""Compare saved reports without turning platform roundoff into a geometry gate.

This projection is for recorded parity only; never use it to qualify motion.
The 0.000001 mm diagnostic precision is 1/500000 of the 0.5 mm seam gate.
Angle diagnostics use the same decimal precision in degrees. Source/rendered
angles, vertices, samples, thresholds and every decision remain exact.
"""
import copy
import math

from origami_cad.fold_continuity import TOLERANCE_MM
from origami_cad.preview_witnesses import witnesses_valid

DIAGNOSTIC_PRECISION = 10 ** math.floor(math.log10(TOLERANCE_MM / 100000))
DIAGNOSTIC_FIELDS = {'max_gap_mm', 'gap_mm', 'max_vertex_move_mm',
                     'max_abs_angle_deg', 'actual_deg', 'schedule_deg'}


def _report(report, kind):
    if not isinstance(report, dict):
        return report
    report = copy.deepcopy(report)
    # These are representative witnesses selected by raw floating-point min/max.
    # Gate decisions, measurements, source edges and flags are still compared.
    if kind == 'continuity':
        if 'worst' in report:
            worst = report['worst']
            if worst is not None and (not isinstance(worst, dict) or
                    set(worst) != {'progress', 'faces', 'endpoint'} or
                    not isinstance(worst['faces'], list) or len(worst['faces']) != 2 or
                    any(type(fid) is not int or fid < 0 for fid in worst['faces']) or
                    not isinstance(worst['endpoint'], list) or len(worst['endpoint']) != 2 or
                    any(type(n) not in (float, int) for n in worst['endpoint']) or
                    type(worst['progress']) not in (float, int) or not 0 <= worst['progress'] <= 1):
                raise ValueError('Malformed seam witness')
            report['worst'] = None
    elif kind == 'closure':
        for contact in report.get('contacts', []):
            if type(contact.get('other')) is not int or contact['other'] < 0:
                raise ValueError('Malformed contact witness')
            contact['other'] = None
    elif kind == 'loop':
        for loop in report.get('loops', []):
            if (type(loop.get('other')) is not int or loop['other'] < 0 or
                    not isinstance(loop.get('path'), list) or len(loop['path']) < 4 or
                    any(type(fid) is not int or fid < 0 for fid in loop['path'])):
                raise ValueError('Malformed loop witness')
            loop['other'] = None
            loop['path'] = []
    return report


def preview_record(model):
    """Comparison projection, not a new serialized schema or runtime model."""
    result = copy.deepcopy(model)
    if 'continuity' in result:
        result['continuity'] = _report(result['continuity'], 'continuity')
    coordination = result.get('coordination')
    if isinstance(coordination, dict):
        for summary in [coordination, *coordination.get('candidates', [])]:
            for kind in ('continuity', 'closure', 'loop'):
                if kind in summary:
                    summary[kind] = _report(summary[kind], kind)
    return result


def _finite(value):
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_finite(v) for v in value.values())
    if isinstance(value, list):
        return all(_finite(v) for v in value)
    return True


def _matches(recorded, expected, path=()):
    if type(recorded) is not type(expected):
        return False
    if isinstance(expected, dict):
        if {'actual_deg', 'expected_deg'} <= expected.keys() and expected.keys() == recorded.keys():
            if ((abs(recorded['actual_deg'] - recorded['expected_deg']) > 1e-9) !=
                    (abs(expected['actual_deg'] - expected['expected_deg']) > 1e-9)):
                return False
        return recorded.keys() == expected.keys() and all(
            _matches(recorded[key], value, path + (key,)) for key, value in expected.items())
    if isinstance(expected, list):
        return len(recorded) == len(expected) and all(
            _matches(a, b, path + (i,)) for i, (a, b) in enumerate(zip(recorded, expected)))
    if isinstance(expected, float):
        if not math.isfinite(recorded) or not math.isfinite(expected):
            return False
        # Areas are derived geometry metadata: allow only a small number of
        # floating-point ULPs, not the diagnostic tolerance or a relative slack.
        if path[-1:] == ('area_mm2',):
            return abs(recorded - expected) <= 16 * max(math.ulp(recorded), math.ulp(expected))
        diagnostic = path and path[0] in {'continuity', 'coordination'}
        if diagnostic and any(key in DIAGNOSTIC_FIELDS for key in path):
            if path[-1] in {'max_gap_mm', 'gap_mm'} and (
                    (recorded <= TOLERANCE_MM) != (expected <= TOLERANCE_MM)):
                return False
            if path[-1] == 'max_abs_angle_deg' and ((recorded <= 1e-9) != (expected <= 1e-9)):
                return False
            return abs(recorded - expected) <= DIAGNOSTIC_PRECISION
    return recorded == expected


def preview_records_match(recorded, regenerated, cp=None):
    """Strict motion/decisions, bounded diagnostic comparison; no gate evaluation."""
    try:
        return (_finite(recorded) and _finite(regenerated) and
                witnesses_valid(recorded, regenerated, cp, DIAGNOSTIC_PRECISION) and
                _matches(preview_record(recorded), preview_record(regenerated)))
    except (AttributeError, KeyError, TypeError, ValueError, IndexError):
        return False


def continuity_records_match(recorded, regenerated, model=None, cp=None):
    source = dict(model or {}, continuity=regenerated)
    return preview_records_match(dict(source, continuity=recorded), source, cp)
