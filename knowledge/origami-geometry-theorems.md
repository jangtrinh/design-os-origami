---
id: origami-geometry-theorems
title: "Origami Geometry & Flat-Foldability Theorems"
domain: "origami-engineering"
description: "Mathematical foundations of crease patterns, flat-foldability, Huzita-Hatori axioms, and vertex fold conditions for CAD paper engineering."
when: ["designing folding patterns", "verifying crease patterns", "evaluating flat-foldability", "checking vertex angles"]
trust_tier: "draft"
version: "1.0.0"
quarantine:
  is_external_untrusted: false
---

# Origami Geometry & Flat-Foldability Theorems

## Draft Provenance Notice

This document is draft guidance, withheld from verified engineering authority.
No captured source bytes substantiate the former provenance or source licence
claims; those unsupported claims have been removed. Citations are references,
not verification or permission to reproduce third-party material.
Material constants, mathematical claims, and production applicability require
independent sourced review and relevant physical or recipient acceptance.

## Purpose
Provides the rigorous mathematical rules governing single-sheet paper folding, flat-foldability criteria, and geometric theorems required for computational origami CAD and packaging engineering.

## When to Use / When NOT
### ALLOWED (When to Use)
- Verifying whether a 2D crease pattern can fold flat without paper stretching or tearing.
- Validating interior vertices in packaging dielines and folding cartons.
- Designing self-collapsing origami tessellations (Miura-ori, Yoshimura, Waterbomb) for protective packaging inserts.

### NOT ALLOWED (When NOT to Use)
- Calculating 3D plastic deformation or deep drawing of ductile metals (use continuum FEA).
- Designing curved organic paper sculptures without crease discretization.

## Core Knowledge Content
<!-- ease:source status="unverified" -->

### 1. The Huzita-Justin-Hatori Axioms
Computational origami constructs fold lines using 7 fundamental geometric operations:
1. **O1**: Given two points $p_1, p_2$, fold the unique line through both.
2. **O2**: Given two points $p_1, p_2$, fold the perpendicular bisector placing $p_1$ onto $p_2$.
3. **O3**: Given two lines $l_1, l_2$, fold the angle bisector placing $l_1$ onto $l_2$.
4. **O4**: Given a point $p_1$ and line $l_1$, fold a perpendicular to $l_1$ through $p_1$.
5. **O5**: Given points $p_1, p_2$ and line $l_1$, fold a line placing $p_1$ onto $l_1$ passing through $p_2$.
6. **O6**: Given points $p_1, p_2$ and lines $l_1, l_2$, fold a line placing $p_1$ onto $l_1$ and $p_2$ onto $l_2$ (solves cubic equations).
7. **O7**: Given a point $p_1$ and lines $l_1, l_2$, fold a line placing $p_1$ onto $l_1$ perpendicular to $l_2$.

### 2. Local Flat-Foldability Conditions
For an interior vertex $v$ with incident crease angles $\theta_1, \theta_2, \dots, \theta_{2n}$:

#### Kawasaki's Theorem
A single-vertex crease pattern with even degree folds flat if and only if the alternating sum of angles equals zero:
$$\sum_{i=1}^{2n} (-1)^i \theta_i = 0 \iff \sum_{k=1}^{n} \theta_{2k-1} = \sum_{k=1}^{n} \theta_{2k} = 180^\circ$$

#### Maekawa-Justin Theorem
At any flat-foldable interior vertex, the difference between the number of mountain folds ($M$) and valley folds ($V$) is always $\pm 2$:
$$|M - V| = 2$$
*Corollary*: The degree of any interior flat-foldable vertex must be an even integer $\ge 4$. Degree 2 vertices are trivial (collinear lines).

### 3. Rigid Origami & Kinematics
Rigid origami treats the facets as rigid polygons connected along creases by revolute hinges.
Each crease $e_{ij}$ between facet $F_i$ and facet $F_j$ has a fold angle $\rho_{ij} \in [-\pi, \pi]$:
- $\rho_{ij} = 0$: Unfolded flat sheet.
- $\rho_{ij} > 0$: Valley fold.
- $\rho_{ij} < 0$: Mountain fold.
- $|\rho_{ij}| = \pi$: Completely folded flat state.

## Failure Modes (Mandatory)
1. **Odd Degree Vertex Failure**: Designing an interior vertex with 3 or 5 incident crease lines; violates Maekawa's theorem and cannot fold flat without paper tearing or crumpling.
2. **Kawasaki Angle Parity Violation**: Sector angles around a 4-vertex summing to $170^\circ$ and $190^\circ$; results in mechanical jamming and panel warping during fold collapse.
3. **Facet Self-Intersection**: Assuming local flat-foldability implies global flat-foldability without testing global layer ordering; causes overlapping panels to penetrate each other in 3D.
