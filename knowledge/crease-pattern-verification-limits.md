---
id: "crease-pattern-verification-limits"
title: "Local Flat-Fold Checks and What They Cannot Prove"
domain: "architecture"
description: "Kawasaki, Maekawa and Big-Little-Big as necessary local conditions, the NP-hardness of global flat foldability, and a concrete defect these checks caught in this repo."
when:
  - "Validating a crease pattern"
  - "Assigning mountain/valley"
  - "Deciding what to report as not verified"
source:
  uri: "https://arxiv.org/pdf/1601.02727"
  modality: "pdf"
  sha256: "8df368e004e1b5eccce3de6d10e285c3b001d70d02c47f2bf7cfe68128485e4f"
  captured_at: "2026-10-08T08:35:16Z"
quarantine: false
version: "1.1.0"
---

## Purpose
Defines the local vertex checks the generator runs and states, as hard limits, what passing them does not establish.

## When to Use / When NOT
- **ALLOWED**: linting vertex degree, Kawasaki sums, Maekawa counts and Big-Little-Big parity.
- **NOT ALLOWED**: declaring a pattern foldable, or die-cut ready, because local checks pass.

## Core Knowledge Content
1. FACT: Big-Little-Big Lemma (Lemma 3.1 in Hull, arXiv:1601.02727, which cites Demaine and O'Rourke 2007): for a flat vertex fold with a valid M/V assignment, if $\alpha_{i-1}>\alpha_i<\alpha_{i+1}$ then the creases bounding $\alpha_i$ have opposite M/V. <!-- ease:source https://arxiv.org/pdf/1601.02727 --> Hull's paper is a survey that states the lemma; it is not the discoverer (an earlier draft credited "Hull, 2016").
2. Kawasaki (alternating angle sum is 0, so odd sectors sum to 180 degrees) and Maekawa ($|M-V|=2$) are standard necessary local conditions at an interior vertex of even degree. Not re-checked against a source in this pass; both are implemented and tested in src/origami_cad/geometry.py and the tests directory.
3. FACT: ORIPA's documentation states that Kawasaki + Maekawa + big-little-big together are not sufficient to check foldability. <!-- ease:source https://raw.githubusercontent.com/oripa/oripa/master/documents/algorithms.md -->
4. FACT (secondary): global flat foldability is NP-hard (Bern and Hayes, SODA 1996, pp. 175-183), reported for both assigned and unassigned patterns by surveys such as arXiv:1307.1065. A later paper reports errors in parts of the original gadget proof, while later work still treats the hardness as established. Bern and Hayes' paper itself was not fetched.
5. FACT (this repo, reproduced 2026-10-08): the deer bird-base M/V assignment passed Maekawa at every interior vertex yet violated Big-Little-Big at the 22.5 degree node (100, 41.42). Adding the BLB constraint to the solver fixed it; test_big_little_big_at_every_interior_vertex guards it.

## Failure Modes (Mandatory)
- Maekawa-only assignment: can hide BLB violations; run BLB during M/V solving.
- False local confidence: local pass says nothing about layer ordering, global self-intersection, continuous folding or thickness; report all of these as NOT verified.
- Layer ordering needs a real facet partition; the deer generator has a single facet (other packaging generators define several), so no layer analysis is possible for it.
- FACT (fixed 2026-10-08): validate_kawasaki_at_vertex used to return True for any vertex with fewer than 4 fold creases, including an interior degree-3 vertex. It now rejects interior degrees 1 and 3 and kinked degree 2, accepts straight degree 2, counts a crease passing through the vertex as two rays, and exempts only vertices touching a CUT segment. Known limits: a CUT boundary vertex of degree >= 4 is still checked with the interior rules, and boundary detection uses a fixed 1e-4 coordinate tolerance.
- Physical behaviour (thickness, collisions, appearance) is NOT verified by any check here. Mathematical certificates for idealized foldability exist but are not implemented.
