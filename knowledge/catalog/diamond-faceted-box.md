---
id: diamond-faceted-box
title: "Diamond-Faceted Polyhedral Packaging: Kinematics, Parametric Dielines & Caliper Relief"
domain: "packaging-engineering"
description: "Engineering specification for polyhedral, triangulated, and diamond-faceted origami packaging, non-orthogonal dihedral score allowances, multi-crease vertex relief geometry, and luxury carton CAD."
when: ["designing faceted packaging", "generating diamond box dielines", "polyhedral folding cartons", "luxury perfume carton CAD", "vertex relief calculation"]
trust_tier: "draft"
version: "1.0.0"
quarantine:
  is_external_untrusted: false
---

# Diamond-Faceted Polyhedral Packaging: Kinematics, Parametric Dielines & Caliper Relief

## Draft Provenance Notice

This document is draft guidance, withheld from verified engineering authority.
No captured source bytes substantiate the former provenance or source licence
claims; those unsupported claims have been removed. Citations are references,
not verification or permission to reproduce third-party material.
Material constants, mathematical claims, and production applicability require
independent sourced review and relevant physical or recipient acceptance.

## Purpose
Specifies the mathematical kinematics, parametric 2D dieline layouts, fiber bending deductions, and multi-crease relief geometry required to engineer polyhedral diamond-faceted folding cartons from single-sheet paperboard without facet buckling or corner tearing.

## When to Use / When NOT
### ALLOWED (When to Use)
- Engineering secondary luxury packaging for perfume flacons, cosmetics jars, fine jewelry, and high-end confectionery.
- Generating parametric CAD dielines (DXF, SVG, CF2) with triangulated, hexagonal, or octagonal bipyramidal faceted geometry.
- Computing thickness compensation for acute non-orthogonal dihedral fold angles ($\psi \in [30^\circ, 150^\circ]$).
- Dimensioning laser relief micro-apertures at high-degree vertex nodes ($\ge 6$ convergent crease lines).

### NOT ALLOWED (When NOT to Use)
- High-speed automatic machine-erected RSC shipping cartons (FEFCO 0201) running on 600 box/min packing lines.
- Heavy corrugated board exceeding E-flute caliper ($t > 1.6\text{mm}$) where facet triangulation induces severe delamination.
- Vacuum-formed plastic blister packaging.

## Core Knowledge Content
<!-- ease:source status="unverified" -->

### 1. Geometric Topology & Facet Kinematics
A diamond-faceted carton derives its structural envelope from an antiprismatic or bipyramidal polyhedral band consisting of $2n$ alternating triangular facets.

```
       Apex Vertex V_top
           /  |  \
          /   |   \   (Upper Facet Triangles)
         /    |    \
       V1 ────V2────V3 (Equatorial Belt Vertices)
        \    /  \   /
         \  /    \ /  (Lower Facet Triangles)
          \/──────\/
       Base Vertex V_base
```

For an $n$-sided polygonal base of inradius $R_b$, carton height $H$, and equatorial expansion factor $k_{\text{eq}} > 1.0$:
- **Equatorial Radius**: $R_{\text{eq}} = k_{\text{eq}} \cdot R_b$
- **Facet Dihedral Angle $\psi$**: The internal angle between adjacent triangular facets $F_1, F_2$ sharing edge $e_{12}$:
  $$\cos \psi = \vec{n}_1 \cdot \vec{n}_2$$
  where $\vec{n}_1, \vec{n}_2$ are unit normal vectors of the triangular facets.
- **Folding Rotation**: Folding angle $\rho = \pi - \psi$. For diamond facets, $\psi$ typically ranges between $70^\circ$ and $125^\circ$.

### 2. Parametric 2D Dieline Geometry
The unfolded planar net consists of:
1. **Base Polygon**: Regular $n$-gon ($n = 6$ hexagonal, $n = 8$ octagonal).
2. **Lower Triangular Facets**: $n$ isosceles triangles base-hinged to the base polygon edges.
3. **Upper Inverted Facets**: $n$ alternating triangular facets completing the equatorial diamond belt.
4. **Closure Flaps / Collar**: Top tuck flaps or interlocking apex star tabs.

The 2D planar coordinates for facet vertices are mapped using isometric development:
$$L_{\text{edge}} = \sqrt{\Delta r^2 + \left(\frac{H}{2}\right)^2 + \left(2 R_{\text{eq}} \sin \frac{\pi}{n}\right)^2}$$

### 3. Non-Orthogonal Caliper Allowance Formula
In standard right-angle folding cartons ($90^\circ$), score deduction is $\Delta L_{90^\circ} = 0.5 t$. However, in diamond-faceted cartons, dihedral angles $\psi$ are non-orthogonal ($\psi \ne 90^\circ$).

The generalized dihedral score allowance $\Delta L(\psi)$ for paperboard with caliper $t$ and neutral bending factor $K \approx 0.42$ is:
$$\Delta L(\psi) = K \cdot t \cdot \left(\frac{180^\circ - \psi}{90^\circ}\right)$$

For acute dihedral folds where $\psi < 60^\circ$ (e.g., sharp diamond peaks):
$$\Delta L_{\text{acute}}(\psi) = t \cdot \tan\left(\frac{180^\circ - \psi}{2}\right)$$

*Design Rule*: Increase the nominal distance between parallel score lines by $\sum \Delta L(\psi)$ to prevent panel crowning and outward bulging.

### 4. Multi-Crease Vertex Relief Geometry
In diamond-faceted nets, interior vertices frequently gather 6 or 8 convergent crease lines (e.g., where upper triangles, lower triangles, and equatorial valley creases intersect).
- Under compression, overlapping fibers form an un-creased solid lump of thickness $N \cdot t$, creating hydraulic bursting pressures in the die-cut rule.
- **Relief Aperture**: At every vertex where $\ge 5$ creases meet, incorporate a circular or diamond relief cutout:
  $$d_{\text{relief}} \ge 1.5 t + 0.5\text{mm}$$
- For laser-cut die boards, relief holes must have radius $r \ge 0.8\text{mm}$ to prevent laser burn-out and charred corners.

```
       Crease M1 \       / Crease M2
                  \     /
       Crease V1 ───( O )─── Crease V2   (O = Relief Hole d >= 1.5t + 0.5mm)
                  /     \
       Crease M3 /       \ Crease M4
```

### 5. Board Specification & Tooling Parameters
- **Recommended Substrates**: Solid Bleached Sulfate (SBS) or Folding Boxboard (FBB) with caliper $t \in [0.35\text{mm}, 0.55\text{mm}]$ (280–420 gsm). High tearing strength and double-clay coating on face.
- **Grain Direction**: Dieline must be oriented such that the primary vertical load-bearing facet creases run parallel ($\pm 15^\circ$) to the board machine grain direction.
- **Creasing Matrix Rule**:
  - Creasing rule thickness: $w_r = 0.71\text{mm}$ (2-pt rule).
  - Matrix channel width: $w_c = 1.3 t + w_r$.
  - Matrix channel depth: $d_c = t$.

### 6. Assembly & Pre-Breaks
Faceted cartons cannot be erected directly from rigid board without pre-breaking scores:
1. **Pre-Break Pass**: Fold all score lines $120^\circ$ inward, then release to flat state. This ruptures internal fiber bond matrix along the crease without tearing outer clay coating.
2. **Pop-In Inversion**: Apply light inward thumb pressure at equatorial vertices to invert valley creases while holding mountain perimeter edges.
3. **Sequential Rim Lock**: Engage the top tuck or star-aperture tabs in sequential rotational order ($1 \to 2 \to \dots \to n$).

## Failure Modes (Mandatory)
1. **Multi-Crease Vertex Crowding & Fiber Bursting**: Omitting relief cutouts at 6-crease intersections; creates a localized fiber stack of $6t$, rupturing the exterior clay coating and puncturing adjacent facets during erection.
2. **Springback & Dimensional Bulging in Unconstrained Facets**: Under-calculating dihedral score deduction on acute diagonal creases ($\psi < 70^\circ$); causes planar facets to bow outward into irregular cylindrical curves instead of crisp planar polygons.
3. **Scoring Rule Asymmetry Causing Torsional Warping**: Applying unequal matrix widths or creasing depths across symmetric diagonal pairs; causes the 3D carton to twist helically along its longitudinal axis upon closing.
4. **Inadequate Taper on Interlocking Facet Tabs**: Designing facet closure tabs with parallel $90^\circ$ edges instead of $15^\circ-20^\circ$ lead-in tapers; results in edge-on-edge binding, paper scuffing, and failure to close on the packaging assembly line.
5. **Grain Direction Splitting on Acute Folds**: Placing acute diamond mountain folds perpendicular to board grain direction; stretches outer tensile fibers beyond ultimate elongation limit ($< 3\%$), leading to white split lines on dark printed surfaces.
