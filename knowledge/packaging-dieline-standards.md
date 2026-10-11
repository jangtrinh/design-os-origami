---
id: packaging-dieline-standards
title: "Packaging Dieline Standards & Physical Thickness Compensation"
domain: "packaging-engineering"
description: "CAD conventions for packaging dielines, knife cut/crease layer assignments, paperboard caliper deduction, and folding carton styles."
when: ["generating dielines", "calculating bend allowances", "exporting DXF/SVG for laser die cutting", "packaging carton engineering"]
trust_tier: "draft"
version: "1.0.0"
quarantine:
  is_external_untrusted: false
---

# Packaging Dieline Standards & Physical Thickness Compensation

## Draft Provenance Notice

This document is draft guidance, withheld from verified engineering authority.
No captured source bytes substantiate the former provenance or source licence
claims; those unsupported claims have been removed. Citations are references,
not verification or permission to reproduce third-party material.
Material constants, mathematical claims, and production applicability require
independent sourced review and relevant physical or recipient acceptance.

## Purpose
Establishes the technical CAD standards for packaging dielines, layer separation (cut, crease, perforate, glue), and mathematical thickness compensation formulas required to manufacture folding cartons without dimensional distortion.

## When to Use / When NOT
### ALLOWED (When to Use)
- Producing 2D CAD files (DXF/SVG) for laser die-board cutting and sample plotters (Zünd, Kongsberg).
- Dimensioning folding cartons (FEFCO 0201/0427, ECMA A20/A55 tuck-end boxes).
- Applying score allowances based on board caliper $t$ (0.3mm to 3.0mm corrugated flutes).

### NOT ALLOWED (When NOT to Use)
- Thermoforming plastic blisters or injection-molded containers.
- Metal sheet stamping with heavy thinning strains ($> 10\%$).

## Core Knowledge Content
<!-- ease:source status="unverified" -->

### 1. CAD Layer & Color Conventions
Packaging dielines must use explicit color and layer segregation to drive CNC cutting and creasing heads:
- **CUT**: Layer name `CUT`, RGB `#FF0000` (Red), solid stroke $1.0\text{pt}$. Through-cut cutting rule knife.
- **CREASE**: Layer name `CREASE`, RGB `#00FF00` (Green), dashed stroke (`dasharray: 4,4`). Creasing matrix rule.
- **PERFORATE**: Layer name `PERFORATE`, RGB `#0000FF` (Blue), dotted stroke (`dasharray: 2,2`). Alternating cut/skip rule for tear tabs.
- **GLUE**: Layer name `GLUE`, RGB `#FF00FF` (Magenta), hatch/cross-hatch fill. Hot-melt or PVA adhesive application zone.
- **DIMENSIONS**: Layer name `DIMENSIONS`, RGB `#7F7F7F` (Grey), thin technical annotation lines with metric (mm) measurements.

### 2. Paperboard Thickness & Score Allowance Formula
Paperboard has a non-zero caliper (thickness $t$). Folding along a crease compresses the inside fibers and stretches the outside fibers.
The neutral bending line sits at distance $K \cdot t$ from the inside surface ($K \approx 0.40 - 0.45$ for folding boxboard / SBS).

For a $90^\circ$ fold:
$$\Delta L_{90^\circ} = \frac{1}{2} t$$

For a $180^\circ$ rollover fold (such as dust flaps and glue tabs):
$$\Delta L_{180^\circ} = 1.0 t \text{ to } 1.5 t$$

When calculating outer panel dimensions $L_{\text{outer}}$ from inner clear cavity dimensions $L_{\text{inner}}$:
$$L_{\text{panel}} = L_{\text{inner}} + \sum \Delta L_{\text{creases}}$$

### 3. Dust Flap & Tuck Tab Geometry
- **Tuck Flap Taper**: Edge cut angled at $3^\circ \text{ to } 5^\circ$ to prevent binding against dust flaps upon insertion.
- **Friction Lock Notch**: Small $0.8\text{mm} - 1.2\text{mm}$ curved detent tabs providing tactile retention click without glue.
- **Grain Direction Alignment**: Main carton body score lines should run parallel to the board grain direction to maximize compressive stack strength and minimize cracking along the fold.

## Failure Modes (Mandatory)
1. **Zero-Thickness Interference**: Calculating panel dimensions with $t=0$; results in box panels bulging outward, tuck flaps refusing to close, or the carton popping open under internal stress.
2. **Layer Color Collision**: Outputting all cut and crease lines on a single black CAD layer; causes laser die cutters to cut through crease lines, severing box panels completely.
3. **Flap Binding**: Failing to add $3^\circ-5^\circ$ taper angles to dust flaps and tuck tabs; causes corners to catch and tear upon high-speed automatic machine erection.
