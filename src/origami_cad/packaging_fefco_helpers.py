"""Piece-based blank assembly shared by the FEFCO style generators.

A style is described as named material pieces (simple polygons that never overlap
in area) plus the score lines two pieces share. Assembly derives every CUT from the
piece boundaries: a boundary portion covered by a score is a fold, a portion shared
by two pieces without a score is a knife slit (declared on the pattern), and the
rest is the die outline. The derived outline therefore always closes, slots and
lock holes come from notches in the piece polygons, and every slit is declared.
"""
import math
from typing import Dict, Iterable, List, Sequence, Tuple

from origami_cad.geometry import CreaseType, OrigamiCreasePattern, Point2D

Point = Tuple[float, float]
EPS = 1e-9


def validate_box_inputs(width: float, depth: float, height: float, thickness: float) -> None:
    """Reject non-numeric, non-finite or non-positive sizes; caliper may be zero, never negative."""
    for name, value in (("width", width), ("depth", depth), ("height", height)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number in mm")
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be a finite positive size in mm")
    if isinstance(thickness, bool) or not isinstance(thickness, (int, float)):
        raise TypeError("thickness must be a number in mm")
    if not math.isfinite(thickness) or thickness < 0:
        raise ValueError("thickness must be a finite caliper >= 0 mm")


def rect(x0: float, y0: float, x1: float, y1: float) -> List[Point]:
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def mirror_y(polygon: Sequence[Point], axis_sum: float) -> List[Point]:
    """Reflect a polygon across the horizontal line y = axis_sum / 2."""
    return [(x, axis_sum - y) for x, y in polygon]


def _collinear_interval(a: Point, b: Point, c: Point, d: Point):
    """Parameter interval of segment cd along ab when both lie on one line, else None."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    length2 = dx * dx + dy * dy
    scale = max(math.sqrt(length2), 1.0)
    for p in (c, d):
        if abs(dx * (p[1] - a[1]) - dy * (p[0] - a[0])) > EPS * scale:
            return None
    t = sorted(((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length2 for p in (c, d))
    lo, hi = max(0.0, t[0]), min(1.0, t[1])
    if (hi - lo) * math.sqrt(length2) <= 1e-7:
        return None
    return lo, hi


def _merge(intervals: Iterable[Tuple[float, float]]) -> List[Tuple[float, float]]:
    merged: List[Tuple[float, float]] = []
    for lo, hi in sorted(intervals):
        if merged and lo <= merged[-1][1] + EPS:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    return merged


def _complement(intervals: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    gaps, cursor = [], 0.0
    for lo, hi in intervals:
        if lo - cursor > EPS:
            gaps.append((cursor, lo))
        cursor = max(cursor, hi)
    if 1.0 - cursor > EPS:
        gaps.append((cursor, 1.0))
    return gaps


def _point_at(a: Point, b: Point, t: float) -> Point:
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))


def _same_line(a: Point, b: Point, c: Point, d: Point) -> bool:
    dx, dy = b[0] - a[0], b[1] - a[1]
    scale = max(math.hypot(dx, dy), 1.0)
    return all(abs(dx * (p[1] - a[1]) - dy * (p[0] - a[0])) <= EPS * scale for p in (c, d))


def _merge_collinear_segments(segments: List[Tuple[Point, Point, str]]) -> List[Tuple[Point, Point, str]]:
    """Join touching collinear slit pieces so one knife line stays one declared slit."""
    remaining = list(segments)
    merged: List[Tuple[Point, Point, str]] = []
    while remaining:
        a, b, label = remaining.pop(0)
        changed = True
        while changed:
            changed = False
            for other in list(remaining):
                c, d, _ = other
                if not _same_line(a, b, c, d):
                    continue
                dx, dy = b[0] - a[0], b[1] - a[1]
                ts = [((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)
                      for p in (c, d)]
                if max(ts) < -EPS or min(ts) > 1 + EPS:
                    continue
                lo, hi = min(0.0, *ts), max(1.0, *ts)
                a, b = _point_at(a, b, lo), _point_at(a, b, hi)
                remaining.remove(other)
                changed = True
        merged.append((a, b, label))
    return merged


def assemble_blank(cp: OrigamiCreasePattern, pieces: Dict[str, Sequence[Point]],
                   hinges: Sequence[Tuple[str, Point, Point]], slit_reason: str) -> None:
    """Add outline CUTs, declared slits and 90-degree score hinges derived from pieces."""
    names = list(pieces)
    edges = [(name, pieces[name][i], pieces[name][(i + 1) % len(pieces[name])])
             for name in names for i in range(len(pieces[name]))]
    for label, p, q in hinges:
        owners = {name for name, a, b in edges if _collinear_interval(a, b, p, q) is not None}
        if len(owners) != 2:
            raise ValueError(f"hinge {label!r} must be shared by exactly two pieces, found {sorted(owners)}")
        cp.add_crease(Point2D(*p), Point2D(*q), CreaseType.CREASE, 90.0, label)
    slits: List[Tuple[Point, Point, str]] = []
    for index, (name, a, b) in enumerate(edges):
        covered = [iv for _, p, q in hinges if (iv := _collinear_interval(a, b, p, q)) is not None]
        shared = []
        for other_index, (other, c, d) in enumerate(edges):
            if other == name:
                continue
            interval = _collinear_interval(a, b, c, d)
            if interval is None:
                continue
            shared.append(interval)
            if names.index(name) < names.index(other):
                # Only the shared portion that no score covers is a knife slit.
                for lo, hi in _complement(_merge(covered)):
                    s_lo, s_hi = max(lo, interval[0]), min(hi, interval[1])
                    if s_hi - s_lo > EPS:
                        slits.append((_point_at(a, b, s_lo), _point_at(a, b, s_hi),
                                      f"Slit_{name}_{other}"))
        for lo, hi in _complement(_merge(covered + shared)):
            cp.add_crease(Point2D(*_point_at(a, b, lo)), Point2D(*_point_at(a, b, hi)),
                          CreaseType.CUT, 0.0, f"Outline_{name}")
    declared = {}
    for a, b, label in _merge_collinear_segments(slits):
        while label in declared:
            label += "_"
        declared[label] = slit_reason
        cp.add_crease(Point2D(*a), Point2D(*b), CreaseType.CUT, 0.0, label)
    cp.cut_slits = declared
    for name in names:
        cp.add_facet(name, [Point2D(*p) for p in pieces[name]])
