---
name: es-origami-cad
description: "Origami mathematics, crease patterns & parametric CAD dielines for packaging engineering. Covers FEFCO/ECMA, caliper deductions, 3D kinematics, and 305+ creative packaging catalog."
metadata:
  author: DESIGN:OS
  version: "1.0.0"
  qualification: experimental-unqualified
---

# Origami CAD & Packaging Engineering (`es-origami-cad`)

Experimental guidance for mathematical origami crease patterns, parametric packaging dielines (2D DXF/SVG), and illustrative folding previews.

## Evidence and Qualification Limits

Knowledge documents have mixed provenance and uncalibrated material constants.
Unsupported source claims have been removed; treat design rules as draft guidance. The catalog contains application ideas, not independently
validated CAD models. Source lint and local geometry tests do not establish
physical fit, global foldability, printer/plotter acceptance, or prepress approval.
The viewer derives real rigid-panel fold motion from the generated net when
the sampled continuity gate passes. Unsupported patterns retain their 2D
dielines and explicitly report 3D preview unavailable. The preview does not
certify physical assembly, continuous-time motion or collision avoidance.

SVG preserves M/V direction as `data-fold` metadata; DXF collapses it into
`CREASE`. Do not infer a manufacturing profile from the display styling.

## When to Activate

- Designing packaging boxes, folding cartons, or origami gift containers
- Generating laser die-cutter dielines (CUT, CREASE, PERFORATE, GLUE layers)
- Calculating paperboard thickness score allowances ($\Delta L = 0.5 \cdot t$)
- Evaluating flat-foldability with Kawasaki's and Maekawa's theorems
- Building 3D folding animations in WebGL / Three.js

## Philosophy & Core Principles

1. **Geometry Over Magic**: Kawasaki ($\sum (-1)^i \theta_i = 0$) and Maekawa ($|M - V| = 2$) constrain interior single-vertex flat folds under their assumptions. Boundary vertices and cartons that fold to a volume need different checks; local conditions do not prove global folding or collision avoidance.
2. **Caliper Reality**: Paper has non-zero thickness $t$. Panel dimensions must include bend allowances; zero-thickness CAD will tear or jam upon assembly.
3. **Retrieval-Augmented CAD (RA-CAD)**: Use the catalog as concept guidance and the implemented generators as experimental geometry. Catalog entries do not certify a corresponding validated net.
4. **Layer Separation**: Local conventions are CUT (Red), CREASE (Green dashed), PERFORATE (Blue), GLUE (Magenta). Display colors and dash patterns are not a recipient-approved machine or prepress contract.

## Pattern Selection Decision Matrix

| Packaging Archetype | Primary Industry | Origami Topology | Key Mechanism | Glue Required? |
| :--- | :--- | :--- | :--- | :--- |
| **Straight/Reverse Tuck** | Pharma, Tech, Retail | ECMA A20 / A55 | $3^\circ$ tapered tuck tab | Yes (Side seam) |
| **Hexagonal Petal Box** | Cosmetics, Luxury Gifts | Blooming Petal | Interlocking flower crown | Optional (Base only) |
| **Diamond Faceted Box** | Jewelry, Perfume | Polyhedral / Yoshimura | Diagonal buckle facets | Yes (Side seam) |
| **Zero-Glue Masu Tray** | Gourmet Food, Eco Retail | Rollover Wall Gusset | $45^\circ$ self-locking corners | **No (100% Zero-Glue)** |
| **Miura-Ori Sleeve** | Wine, Fragile Electronics | Rigid Tessellation | 1-DOF shock absorber | No (Continuous sleeve) |

## Caliper & Score Allowance Table

Legacy illustrative values below are uncalibrated, not a material/tooling recipe.
The executable allowance is owned by `OrigamiCreasePattern.calculate_score_allowance`;
its default is 0.45t at 90°, which differs from the approximate 0.5t guidance.

| Material Type | Caliper ($t$) | $90^\circ$ Fold Allowance ($\Delta L$) | Neutral Axis $K$ | Typical Style |
| :--- | :--- | :--- | :--- | :--- |
| **Solid Bleached Sulfate (SBS)** | $0.35 - 0.50\text{ mm}$ | $+0.18 - 0.25\text{ mm}$ | $0.45$ | Cosmetics, Medicine |
| **Folding Boxboard (FBB)** | $0.50 - 0.70\text{ mm}$ | $+0.25 - 0.35\text{ mm}$ | $0.42$ | Retail Food, Hardware |
| **E-Flute Corrugated** | $1.20 - 1.60\text{ mm}$ | $+0.60 - 0.80\text{ mm}$ | $0.40$ | E-commerce Mailer (FEFCO 0427) |
| **B-Flute Corrugated** | $2.80 - 3.20\text{ mm}$ | $+1.40 - 1.60\text{ mm}$ | $0.38$ | Shipping Box (FEFCO 0201) |

## Right vs Wrong Code Examples

### 1. Panel Dimension Calculation
```python
# ❌ WRONG: Zero-thickness assumption (carton will bulge and tuck tab will tear)
outer_width = inner_width
outer_depth = inner_depth

# ✅ RIGHT: Explicit score allowance per 90-degree fold
c_allow = (90.0 / 180.0) * (k_factor * 2.0 * thickness_mm)  # approx 0.5 * t
outer_width = inner_width + c_allow
outer_depth = inner_depth + c_allow
```

### 2. Interior Vertex Flat-Foldability
```python
# ❌ WRONG: Arbitrary 3-crease interior junction
cp.add_crease(v, p1, CreaseType.CREASE)
cp.add_crease(v, p2, CreaseType.CREASE)
cp.add_crease(v, p3, CreaseType.CREASE)  # Violates Maekawa: degree 3 cannot fold flat!

# ✅ RIGHT: Even-degree vertex satisfying Kawasaki alternating angle sum
# Angles: 60°, 110°, 120°, 70° -> (60+120=180°) and (110+70=180°)
for ang in [0.0, 60.0, 170.0, 290.0]:
    cp.add_crease(v, point_at_angle(v, ang, r), CreaseType.CREASE)
```

## Quickstart CLI Commands

```bash
# Generate Standard Tuck Box (ECMA A20)
python3 -m origami_cad.cli generate --type tuck-box --width 80 --depth 50 --height 120 --thickness 0.5

# Generate Luxury Hexagonal Petal Flower Box
python3 -m origami_cad.cli generate --type hex-petal --radius 45 --height 60 --thickness 0.4

# Generate Eco Zero-Glue Interlocking Tray
python3 -m origami_cad.cli generate --type zero-glue-tray --width 100 --depth 70 --thickness 0.5

# Run Geometric Unit Tests
PYTHONPATH=src python3 -m unittest discover tests
```

## Failure Modes & Common Pitfalls

1. **Flap Jamming**: Omission of $3^\circ-5^\circ$ taper angle on dust flaps and tuck tabs causes corners to catch upon insertion.
2. **Layer Bleed**: Combining CUT and CREASE lines into a single DXF layer causes CNC laser cutters to slice through fold hinges.
3. **Rigid Loop Tearing**: Simulating 3D folding across closed kinematic loops without unrooted trees introduces cumulative rotational drift.

## References Index

- [Origami Mathematics](references/origami-mathematics.md): Huzita axioms, Kawasaki condition, Maekawa theorem.
- [Thickness Mechanics](references/packaging-thickness-mechanics.md): Caliper deductions, grain orientation, laser die rules.
- [Creative Catalog Taxonomy](references/creative-catalog-taxonomy.md): illustrative application concepts across packaging families.
- [3D Kinematic Folding](references/kinematic-folding-3d.md): Rodrigues' rotation formula and Three.js dual-pane simulation.
