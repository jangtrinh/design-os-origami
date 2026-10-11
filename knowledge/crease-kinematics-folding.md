---
id: crease-kinematics-folding
title: "Crease Kinematics & 3D Folding Simulation"
domain: "origami-kinematics"
description: "Kinematic joint models, panel rotation matrices, dihedral angle evolution, and Three.js 3D paper folding visualization."
when: ["simulating 3D folding", "computing panel rotation matrices", "threejs visualization", "origami kinematics"]
trust_tier: "draft"
version: "1.0.0"
quarantine:
  is_external_untrusted: false
---

# Crease Kinematics & 3D Folding Simulation

## Draft Provenance Notice

This document is draft guidance, withheld from verified engineering authority.
No captured source bytes substantiate the former provenance or source licence
claims; those unsupported claims have been removed. Citations are references,
not verification or permission to reproduce third-party material.
Material constants, mathematical claims, and production applicability require
independent sourced review and relevant physical or recipient acceptance.

## Purpose
Specifies the mathematical kinematics and transformation algorithms used to simulate the continuous 3D folding of planar crease patterns into finished packaging cartons or origami structures.

## When to Use / When NOT
### ALLOWED (When to Use)
- Calculating 3D vertex positions as panels rotate around crease hinge axes by angle $\theta(t)$.
- Generating WebGL/Three.js interactive folding animations from 2D dielines.
- Detecting panel collisions and verifying assembly sequence order.

### NOT ALLOWED (When NOT to Use)
- Flexible cloth simulation with crumpling and wrinkle physics (use mass-spring or position-based dynamics).
- Plastic yield modeling under extreme compressive crushing.

## Core Knowledge Content
<!-- ease:source status="unverified" -->

### 1. Dual Graph Kinematic Tree
A crease pattern is modeled as an undirected dual graph $G = (F, E_{\text{crease}})$:
- Vertices in dual graph represent planar rigid facets $F_i$.
- Edges represent crease hinges $e_{ij} = (p_{\text{start}}, p_{\text{end}})$.
- Choose one facet $F_{\text{base}}$ as the rooted anchor in the $XY$ ground plane ($Z = 0$).
- Construct a spanning tree rooted at $F_{\text{base}}$.

### 2. Rodrigues' Rotation Formula around Crease Vector
For a crease hinge directed along unit vector $\hat{\mathbf{u}} = \frac{\mathbf{p}_2 - \mathbf{p}_1}{\|\mathbf{p}_2 - \mathbf{p}_1\|}$:
Any vertex $\mathbf{v}$ on child facet $F_{\text{child}}$ rotating by dihedral fold angle $\rho$ around line through $\mathbf{p}_1$ transforms as:
$$\mathbf{v}' = \mathbf{p}_1 + \mathbf{R}(\hat{\mathbf{u}}, \rho) \cdot (\mathbf{v} - \mathbf{p}_1)$$
where Rodrigues' rotation matrix $\mathbf{R}(\hat{\mathbf{u}}, \rho)$ is:
$$\mathbf{R}(\hat{\mathbf{u}}, \rho) = \mathbf{I} + (\sin \rho) \mathbf{K} + (1 - \cos \rho) \mathbf{K}^2$$
and $\mathbf{K}$ is the skew-symmetric cross-product matrix:
$$\mathbf{K} = \begin{bmatrix} 0 & -u_z & u_y \\ u_z & 0 & -u_x \\ -u_y & u_x & 0 \end{bmatrix}$$

### 3. Dihedral Folding Trajectory
A packaging carton erects through continuous parametric time $\tau \in [0, 1]$:
$$\rho_{ij}(\tau) = \rho_{ij}^{\text{target}} \cdot f(\tau)$$
where $f(\tau) = \frac{1 - \cos(\pi \tau)}{2}$ provides smooth S-curve easing without velocity discontinuity at endpoints.

## Failure Modes (Mandatory)
1. **Unrooted Kinematic Cycle**: Applying uncoordinated rotational transformations around a closed loop of creases; causes cumulative drift and tearing of closed origami loops.
2. **Axis Inversion Sign Error**: Neglecting the directional orientation of hinge vector $\hat{\mathbf{u}}$; inverts mountain into valley, causing cartons to fold inside-out.
3. **Rigid Facet Bending**: Enforcing rigid planar constraints on non-developable quadrilaterals without diagonal triangulation; leads to mathematically impossible constraints and numerical blowup.
