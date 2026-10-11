"""Mathematical origami geometry, theorems, and fold structures."""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import List, Tuple, Dict, Optional


class CreaseType(str, Enum):
    CUT = "CUT"              # Red #FF0000
    MOUNTAIN = "MOUNTAIN"    # Green #00FF00
    VALLEY = "VALLEY"        # Green #00FF00 dashed/dotted
    CREASE = "CREASE"        # Generic score line
    PERFORATE = "PERFORATE"  # Blue #0000FF
    GLUE = "GLUE"            # Magenta #FF00FF


@dataclass(frozen=True)
class Point2D:
    x: float
    y: float

    def distance_to(self, other: "Point2D") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def angle_to(self, other: "Point2D") -> float:
        """Angle in radians [-pi, pi] from self to other."""
        return math.atan2(other.y - self.y, other.x - self.x)


@dataclass
class Point3D:
    x: float
    y: float
    z: float = 0.0

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)


@dataclass
class CreaseLine:
    p1: Point2D
    p2: Point2D
    crease_type: CreaseType
    target_angle_deg: float = 90.0  # target folding angle (0 = flat, 90 = right angle, 180 = flat folded)
    label: str = ""

    @property
    def length(self) -> float:
        return self.p1.distance_to(self.p2)


@dataclass
class Facet2D:
    name: str
    vertices: List[Point2D]
    hinge_crease_index: Optional[int] = None  # index of parent crease line
    fold_angle_deg: float = 0.0               # target angle relative to base


class OrigamiCreasePattern:
    """Represents a 2D crease pattern with packaging and origami validation."""

    def __init__(self, name: str, thickness_mm: float = 0.5):
        self.name = name
        self.thickness_mm = thickness_mm
        self.creases: List[CreaseLine] = []
        self.facets: List[Facet2D] = []

    def add_crease(self, p1: Point2D, p2: Point2D, crease_type: CreaseType, target_angle_deg: float = 90.0, label: str = "") -> int:
        idx = len(self.creases)
        self.creases.append(CreaseLine(p1, p2, crease_type, target_angle_deg, label))
        return idx

    def add_facet(self, name: str, vertices: List[Point2D], hinge_crease_index: Optional[int] = None, fold_angle_deg: float = 0.0):
        self.facets.append(Facet2D(name, vertices, hinge_crease_index, fold_angle_deg))

    def calculate_score_allowance(self, angle_deg: float = 90.0, k_factor: float = 0.45) -> float:
        """Calculate paperboard thickness bend allowance."""
        # For 90 degree fold: Delta L = 0.5 * thickness
        return (angle_deg / 180.0) * (k_factor * 2.0 * self.thickness_mm)

    def validate_kawasaki_at_vertex(self, vertex: Point2D, tolerance_deg: float = 0.5) -> Tuple[bool, str]:
        """
        Validates Kawasaki's theorem at a single vertex:
        Sum of alternating sector angles must equal 180 degrees.
        """
        # Find all incident creases
        incident = []
        for c in self.creases:
            if c.crease_type in (CreaseType.MOUNTAIN, CreaseType.VALLEY, CreaseType.CREASE):
                if c.p1.distance_to(vertex) < 1e-4:
                    incident.append(c.p1.angle_to(c.p2))
                elif c.p2.distance_to(vertex) < 1e-4:
                    incident.append(c.p2.angle_to(c.p1))
                elif self._point_strictly_inside_segment(vertex, c):
                    # crease passes through the vertex: it contributes two opposite rays
                    incident.append(vertex.angle_to(c.p1))
                    incident.append(vertex.angle_to(c.p2))

        if self._is_on_cut_boundary(vertex):
            if len(incident) < 4:
                return True, f"Boundary vertex with degree {len(incident)} (no interior Kawasaki condition)"
        elif len(incident) < 4:
            return self._validate_low_degree_interior_vertex(incident, tolerance_deg)

        if len(incident) % 2 != 0:
            return False, f"Maekawa violation: degree {len(incident)} is odd; cannot fold flat"

        # Sort angles in counter-clockwise order [0, 2*pi)
        angles_sorted = sorted([(a % (2 * math.pi)) for a in incident])
        n = len(angles_sorted)
        sectors = []
        for i in range(n):
            next_idx = (i + 1) % n
            diff = angles_sorted[next_idx] - angles_sorted[i]
            if diff < 0:
                diff += 2 * math.pi
            sectors.append(math.degrees(diff))

        # Check alternating sum
        odd_sum = sum(sectors[i] for i in range(0, n, 2))
        even_sum = sum(sectors[i] for i in range(1, n, 2))

        if abs(odd_sum - 180.0) <= tolerance_deg and abs(even_sum - 180.0) <= tolerance_deg:
            return True, f"Kawasaki PASSED: odd sum = {odd_sum:.2f}°, even sum = {even_sum:.2f}°"
        else:
            return False, f"Kawasaki FAILED: odd sum = {odd_sum:.2f}°, even sum = {even_sum:.2f}° (target 180°)"

    @staticmethod
    def _point_strictly_inside_segment(point: Point2D, c: "CreaseLine", tol: float = 1e-4) -> bool:
        """True when point lies on the crease segment away from both endpoints."""
        if c.length < tol:
            return False
        t = ((point.x - c.p1.x) * (c.p2.x - c.p1.x) + (point.y - c.p1.y) * (c.p2.y - c.p1.y)) / (c.length ** 2)
        if t <= 0.0 or t >= 1.0:
            return False
        foot = Point2D(c.p1.x + t * (c.p2.x - c.p1.x), c.p1.y + t * (c.p2.y - c.p1.y))
        return foot.distance_to(point) < tol

    def _is_on_cut_boundary(self, vertex: Point2D, tol: float = 1e-4) -> bool:
        """True when the vertex touches a CUT segment (sheet edge or slit), so it is not interior paper."""
        for c in self.creases:
            if c.crease_type != CreaseType.CUT or c.length < tol:
                continue
            t = ((vertex.x - c.p1.x) * (c.p2.x - c.p1.x) + (vertex.y - c.p1.y) * (c.p2.y - c.p1.y)) / (c.length ** 2)
            t = max(0.0, min(1.0, t))
            nearest = Point2D(c.p1.x + t * (c.p2.x - c.p1.x), c.p1.y + t * (c.p2.y - c.p1.y))
            if nearest.distance_to(vertex) < tol:
                return True
        return False

    @staticmethod
    def _validate_low_degree_interior_vertex(angles_rad: List[float], tolerance_deg: float = 0.5) -> Tuple[bool, str]:
        """Interior vertices of degree 0-3: only an empty vertex or a straight line (degree 2, 180 deg apart) can fold flat."""
        degree = len(angles_rad)
        if degree == 0:
            return True, "Empty vertex"
        if degree == 2:
            gap = abs((angles_rad[0] - angles_rad[1]) % (2 * math.pi) - math.pi)
            if math.degrees(gap) <= tolerance_deg:
                return True, "Interior degree 2: straight crease line"
            return False, "Interior degree 2 with a kink: cannot fold flat"
        return False, f"Interior vertex of degree {degree} cannot fold flat (Maekawa needs even degree >= 4)"

    @staticmethod
    def _reject_overlapping_collinear(folds: List["CreaseLine"], tol: float) -> None:
        for i, a in enumerate(folds):
            d = (a.p2.x - a.p1.x, a.p2.y - a.p1.y)
            for b in folds[i + 1:]:
                e = (b.p2.x - b.p1.x, b.p2.y - b.p1.y)
                if abs(d[0] * e[1] - d[1] * e[0]) > 1e-9 * max(a.length * b.length, 1.0):
                    continue
                w = (b.p1.x - a.p1.x, b.p1.y - a.p1.y)
                if abs(d[0] * w[1] - d[1] * w[0]) > tol * max(a.length, 1.0):
                    continue  # parallel but not on the same line
                u0 = (w[0] * d[0] + w[1] * d[1]) / (a.length ** 2)
                u1 = u0 + (e[0] * d[0] + e[1] * d[1]) / (a.length ** 2)
                lo, hi = min(u0, u1), max(u0, u1)
                if min(hi, 1.0) - max(lo, 0.0) > tol / max(a.length, tol):
                    raise ValueError("overlapping collinear fold creases: %r and %r" % (a.label, b.label))

    def split_at_intersections(self, tol: float = 1e-6) -> None:
        """
        Splits every fold crease (non-CUT) at each point where another fold crease crosses it or
        ends on it (X and T junctions), so vertex incidence by endpoints is complete.
        CUT, GLUE and PERFORATE creases are left untouched (and a fold crossing them is not split).
        Type, angle and label are kept on every piece. Pieces shorter than tol are dropped.
        Side effect: self.creases is rebuilt with non-fold creases first, so crease indices returned
        earlier by add_crease and Facet2D.hinge_crease_index are NOT remapped.
        Raises ValueError when two fold creases overlap along a common line.
        """
        fold_types = (CreaseType.MOUNTAIN, CreaseType.VALLEY, CreaseType.CREASE)
        folds = [c for c in self.creases if c.crease_type in fold_types]
        others = [c for c in self.creases if c.crease_type not in fold_types]
        self._reject_overlapping_collinear(folds, tol)

        def cut_points(c: "CreaseLine") -> List[float]:
            ts = []
            d = (c.p2.x - c.p1.x, c.p2.y - c.p1.y)
            for o in folds:
                if o is c:
                    continue
                e = (o.p2.x - o.p1.x, o.p2.y - o.p1.y)
                den = d[0] * e[1] - d[1] * e[0]
                if abs(den) < 1e-12:
                    continue  # parallel or collinear: no single crossing point
                w = (o.p1.x - c.p1.x, o.p1.y - c.p1.y)
                t = (w[0] * e[1] - w[1] * e[0]) / den
                u = (w[0] * d[1] - w[1] * d[0]) / den
                eps_t, eps_u = tol / max(c.length, tol), tol / max(o.length, tol)
                if -eps_u <= u <= 1 + eps_u and eps_t < t < 1 - eps_t:
                    ts.append(t)
            return sorted(ts)

        pieces: List["CreaseLine"] = []
        for c in folds:
            ts = [0.0] + cut_points(c) + [1.0]
            dedup = [ts[0]]
            for t in ts[1:]:
                if (t - dedup[-1]) * c.length > tol:
                    dedup.append(t)
            if dedup[-1] != 1.0:
                dedup[-1] = 1.0
            for a, b in zip(dedup, dedup[1:]):
                p1 = Point2D(c.p1.x + a * (c.p2.x - c.p1.x), c.p1.y + a * (c.p2.y - c.p1.y))
                p2 = Point2D(c.p1.x + b * (c.p2.x - c.p1.x), c.p1.y + b * (c.p2.y - c.p1.y))
                pieces.append(CreaseLine(p1, p2, c.crease_type, c.target_angle_deg, c.label))
        self.creases = others + pieces

    def bounding_box(self) -> Tuple[float, float, float, float]:
        """Returns (min_x, min_y, max_x, max_y)."""
        xs = []
        ys = []
        for c in self.creases:
            xs.extend([c.p1.x, c.p2.x])
            ys.extend([c.p1.y, c.p2.y])
        for f in self.facets:
            for v in f.vertices:
                xs.append(v.x)
                ys.append(v.y)
        if not xs:
            return (0.0, 0.0, 0.0, 0.0)
        return (min(xs), min(ys), max(xs), max(ys))
