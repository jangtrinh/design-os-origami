---
id: "tree-theory-uniaxial-bases"
title: "Tree Theory and Uniaxial Bases for Figurative Origami"
domain: "architecture"
description: "Tree-graph to circle-packing view of origami design as used by TreeMaker, with corrected paper-area geometry and explicit evidence labels."
when:
  - "Designing figurative origami crease patterns"
  - "Tree graph to circle packing layout"
  - "Uniaxial base flap computation"
source:
  uri: "https://www.langorigami.com/wp-content/uploads/2015/09/TreeMkr40.pdf"
  modality: "pdf"
  sha256: "3ba7b010fecb05163e7b70b044c3079641093176652d5535c0efaf1dcf85be56"
  captured_at: "2026-10-08T08:35:16Z"
quarantine: false
version: "1.1.0"
---

## Purpose
Gives the tree/circle-packing frame for turning a stick-figure animal into a flat-foldable base, and says which statements are sourced and which are our own derivation.

## When to Use / When NOT
- **ALLOWED**: choosing flap counts and relative lengths before drawing any crease.
- **ALLOWED**: sanity-checking a hand-designed base against tip-distance constraints.
- **NOT ALLOWED**: claiming a pattern folds because the packing is feasible; packing is a design input, not a foldability proof (see crease-pattern-verification-limits).
- **NOT ALLOWED**: curved-crease or tessellation work with no terminal flaps.

## Core Knowledge Content
Evidence labels: FACT = in the cited source; INFERENCE = our reading or derivation; UNVERIFIED = not found in any source fetched.

1. FACT: In TreeMaker, terminal nodes of a stick-figure tree each get a circle; "Optimize Scale" moves terminal nodes on the square to make the whole tree as large as possible, and edges that cannot be made longer are shown as tight. <!-- ease:source https://www.langorigami.com/wp-content/uploads/2015/09/TreeMkr40.pdf --> Anchors for follow-up: manual p.116 and section 6.3 (scale optimization); this is TreeMaker 4.0 documentation (file TreeMkr40.pdf), not 5.x.
2. INFERENCE (standard tree-distance condition, formula not quoted from the manual): with scale $\lambda$ and tree distance $d_T(i,j)$ (sum of edge lengths on the path), tip positions $p_i$ on the sheet satisfy $\|p_i-p_j\|\ge \lambda\,d_T(i,j)$ for every pair of leaves; for a star tree this reduces to disjoint disks $\|p_i-p_j\|\ge r_i+r_j$.
3. INFERENCE: internal edges (torso, neck) enter the pairwise distance through $d_T$; a fore leg and a hind leg are separated by the torso edge, so their required distance includes it; the inequality only gives lower bounds, not a layout. The exact "river" construction is UNVERIFIED here; do not implement from this file alone.
4. FACT (geometry): a flap of reach $r$ pinned at a sheet corner can use at most a quarter disk of paper ($\tfrac14\pi r^2$), on an edge a half disk ($\tfrac12\pi r^2$), in the interior a full disk ($\pi r^2$). Long flaps are therefore cheaper at corners and edges. (An earlier draft stated $0.5\pi r^2$ for corners and $\pi r^2$ for edges; that was wrong.)

## Failure Modes (Mandatory)
- Distance below $\lambda d_T$: the packing is infeasible at that scale; reduce $\lambda$ or change the tree.
- Long flap placed in the interior: consumes a full disk; move it to a corner or edge.
- Treating a feasible packing as a foldable crease pattern: it still needs M/V assignment and layer checks.
- Reading depth: Lang's 1996 algorithm paper, Theorem 2 and the universal-molecule construction (printed pp.100-103) are NOT VERIFIED in this note; consult the original source before implementing the algorithm.
- Implementing rivers from this file: UNVERIFIED; read the TreeMaker manual sections on edge optimization and the universal molecule first.
