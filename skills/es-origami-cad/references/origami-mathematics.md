# Origami Mathematics & Flat-Foldability Theorems

Comprehensive mathematical foundation for computational origami and crease pattern design.

Draft reference: legacy claims below have no verified source capture in this
package. Local single-vertex conditions have assumptions and do not certify
global foldability, rigid motion, collision avoidance, or carton assembly.

## 1. The 7 Huzita-Justin-Hatori Axioms

Every fold in mathematical origami corresponds to an operation placing points/lines onto other points/lines:

| Axiom | Input | Operation | Algebraic Degree |
| :--- | :--- | :--- | :--- |
| **O1** | Points $p_1, p_2$ | Fold line passing through $p_1$ and $p_2$ | Linear ($d=1$) |
| **O2** | Points $p_1, p_2$ | Fold placing $p_1$ onto $p_2$ (Perpendicular bisector) | Linear ($d=1$) |
| **O3** | Lines $l_1, l_2$ | Fold placing $l_1$ onto $l_2$ (Angle bisector) | Quadratic ($d=2$) |
| **O4** | Point $p_1$, line $l_1$ | Fold perpendicular to $l_1$ passing through $p_1$ | Linear ($d=1$) |
| **O5** | Points $p_1, p_2$, line $l_1$ | Fold line passing through $p_2$ placing $p_1$ onto $l_1$ | Quadratic ($d=2$) |
| **O6** | Points $p_1, p_2$, lines $l_1, l_2$ | Fold line placing $p_1$ onto $l_1$ and $p_2$ onto $l_2$ | **Cubic ($d=3$)** |
| **O7** | Point $p_1$, lines $l_1, l_2$ | Fold line placing $p_1$ onto $l_1$ perpendicular to $l_2$ | Quadratic ($d=2$) |

*Note: Axiom O6 allows solving general cubic equations, enabling angle trisection and doubling the cube.*

---

## 2. Local Flat-Foldability Conditions

### Kawasaki's Theorem
For a flat-foldable interior vertex of degree $2n$ with consecutive sector angles $\theta_1, \theta_2, \dots, \theta_{2n}$:
$$\sum_{k=1}^n \theta_{2k-1} = \sum_{k=1}^n \theta_{2k} = 180^\circ$$

**Validation Algorithm**:
```python
def check_kawasaki(sector_angles_deg: list[float], tolerance: float = 0.5) -> bool:
    if len(sector_angles_deg) % 2 != 0:
        return False  # Maekawa violation: odd degree cannot fold flat
    odd_sum = sum(sector_angles_deg[0::2])
    even_sum = sum(sector_angles_deg[1::2])
    return abs(odd_sum - 180.0) <= tolerance and abs(even_sum - 180.0) <= tolerance
```

### Maekawa's Theorem
At any flat-foldable interior vertex with $M$ mountain folds and $V$ valley folds:
$$M - V = \pm 2$$
- Implication: All flat-foldable interior vertices must have an even number of creases ($\ge 4$).
- An interior vertex with degree 3 or 5 is mathematically impossible to fold flat without crumpling.

---

## 3. Decision Matrix: Fold Pattern Selection

| Pattern Type | Degree of Freedom | Flat Foldable? | Primary Packaging Use |
| :--- | :--- | :--- | :--- |
| **Miura-ori** | 1-DOF rigid | Yes | Shock-absorbing sleeves, expandable bottle wrappers |
| **Yoshimura Pattern** | Multi-DOF buckling | No (Cylindrical) | Crush zones, cylindrical cosmetic tube cartons |
| **Waterbomb Base** | 1-DOF radial | Yes | Pop-up gift closures, collapsible candy boxes |
| **Flasher / Twist** | 1-DOF rotational | Yes | Luxury polygonal perfume boxes, spiral opening lids |

---

## 4. Failure Modes & Anti-Patterns

1. **Parity Violation**: Designing 4-crease vertices with angles $90^\circ, 90^\circ, 85^\circ, 95^\circ$. Odd sum = $175^\circ \ne 180^\circ$. Sheet will buckle out-of-plane.
2. **Self-Intersection in Multi-Layer Folds**: Failing to check layer ordering matrix. Local flat-foldability does not guarantee global non-collision.
3. **Overconstrained Facets**: Rigid origami requires facets to remain planar. If a quadrilateral is non-developable, it must be triangulated with a diagonal crease.
