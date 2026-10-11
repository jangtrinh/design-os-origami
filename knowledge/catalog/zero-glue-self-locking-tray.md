---
id: zero-glue-self-locking-tray
title: "Zero-Glue Self-Locking Tray & Cartons: Mono-Material Origami Engineering"
domain: "packaging-engineering"
description: "Engineering specification for single-sheet zero-glue self-locking origami trays, double-wall rollover hollow-wall construction, Walker/Simplex mechanical locks, and caliper clearance math."
when: ["designing zero-glue trays", "engineering self-locking packaging", "calculating rollover score clearances", "eco-minimalist packaging", "Walker lock dielines"]
trust_tier: "draft"
version: "1.0.0"
quarantine:
  is_external_untrusted: false
---

# Zero-Glue Self-Locking Tray & Cartons: Mono-Material Origami Engineering

## Draft Provenance Notice

This document is draft guidance, withheld from verified engineering authority.
No captured source bytes substantiate the former provenance or source licence
claims; those unsupported claims have been removed. Citations are references,
not verification or permission to reproduce third-party material.
Material constants, mathematical claims, and production applicability require
independent sourced review and relevant physical or recipient acceptance.

## Purpose
Establishes the structural design rules, parametric CAD dieline layouts, fiber caliper deduction math, and mechanical retention detent standards for single-sheet, 100% glue-free folding trays and cartons. Enables high-speed manual or semi-automated erection of rigid, eco-compliant packaging without chemical adhesives.

## When to Use / When NOT
### ALLOWED (When to Use)
- Engineering single-sheet mono-material paperboard cartons and display trays that require zero hot-melt or PVA glues.
- Meeting circular packaging regulations (EU PPWR 2025/2030, plastic-free and adhesive-free recyclability mandates).
- Designing double-wall rollover presentation trays (Simplex tray, Walker lock, roll-end hollow wall) for cosmetics, luxury gifts, bakery, and e-commerce inserts.
- Dimensioning CNC knife and crease paths for sample plotters (Zünd, Kongsberg) and high-volume steel rule cutting dies.

### NOT ALLOWED (When NOT to Use)
- Direct containment of liquids, oils, or loose powders without an internal certified barrier liner or pouch.
- High-speed automated side-seam folding carton lines requiring pre-glued crash-bottom blanks running at $> 60,000\text{ units/hour}$.
- Heavy industrial shipping containers exceeding 25 kg load capacity without exterior strapping or tape closure.

## Core Knowledge Content
<!-- ease:source status="unverified" -->

### 1. Structural Typology & Kinematic Net
The double-wall self-locking tray (Walker lock / Simplex tray variant) is engineered from a single rectangular net divided into a base panel, two single-wall side panels with corner gusset flaps, and two double-wall rollover end panels with locking foot tabs:

```
        ┌─────────────┬───────────────────────────┬─────────────┐
        │  Gusset G1  │   Inner End Wall (Roll)   │  Gusset G2  │
        ├─────────────┼───────────────────────────┼─────────────┤
        │  Side Flap  │   Outer End Wall          │  Side Flap  │
        ├─────────────┼───────────────────────────┼─────────────┤
        │             │                           │             │
        │  Side Wall  │   BASE PANEL (L x W)      │  Side Wall  │
        │             │   [Slot 1]        [Slot 2]│             │
        ├─────────────┼───────────────────────────┼─────────────┤
        │  Side Flap  │   Outer End Wall          │  Side Flap  │
        ├─────────────┼───────────────────────────┼─────────────┤
        │  Gusset G3  │   Inner End Wall (Roll)   │  Gusset G4  │
        │             │   [Foot Tab 1] [Foot Tab 2]│             │
        └─────────────┴───────────────────────────┴─────────────┘
```

The tray achieves structural rigidity through:
1. **$90^\circ$ Upward Fold**: Side walls fold upright along base score lines.
2. **Inward Corner Web Fold**: Corner gussets fold $90^\circ$ against the inside faces of the end walls.
3. **$180^\circ$ Rollover**: End walls fold up $90^\circ$ and then roll over $180^\circ$ across double score lines, enveloping the corner gussets.
4. **Mechanical Lock Seating**: Die-cut foot tabs on the inner end walls snap into precision die-cut slots in the base panel.

### 2. Thickness Deduction & Rollover Clearance Math
Paperboard caliper $t$ dictates exact score line positioning to prevent panel crowding and wall bowing.

For a tray of clear internal cavity dimensions $L \times W \times H$ using board of caliper $t$:

#### A. Rollover Score Spacing
The top edge of the rollover end wall comprises two parallel crease lines spaced by $\delta_{\text{roll}}$:
$$\delta_{\text{roll}} = 1.5 t \text{ to } 2.0 t$$
*Rationale*: Provides sufficient neutral axis clearance for the board to complete a full $180^\circ$ fold without rupturing surface fibers.

#### B. Inner Wall Height Deduction
The inner rollover panel must seat flush against the base floor without bottoming out prematurely:
$$H_{\text{inner}} = H - (1.5 t + c_{\text{floor}})$$
where $c_{\text{floor}} = 0.3\text{mm} - 0.5\text{mm}$ is the vertical clearance allowance.

#### C. Base Slot Geometry & Placement
- **Slot Width**: $W_{\text{slot}} = t + 0.3\text{mm}$ (provides clean tab entry without loose play).
- **Slot Length**: $L_{\text{slot}} = W_{\text{tab}} + 1.0\text{mm}$.
- **Slot Distance from Base Score**:
  $$D_{\text{slot}} = t_{\text{effective}} = 2.0 t$$
  (compensates for the combined thickness of the outer wall and folded corner gusset).
- **Lead-In Chamfers**: The locking tab edges must have $15^\circ - 20^\circ$ entry tapers to guide self-centering into the slot during rapid assembly.

### 3. Corner Gusset Stack-Up & Web Geometry
When corner gussets fold $90^\circ$ behind the rollover wall, the localized corner stack-up reaches 3 material plies ($3t$):
- Outer wall ($1t$)
- Folded corner web ($2t$)
- Inner rollover wall ($1t$)
Total joint thickness $= 4t$.

To accommodate this stack without tearing:
1. **Corner Relief Radius**: Laser-cut a circular stress relief hole ($r \ge 1.0\text{mm}$) or a $45^\circ$ diamond notch at the intersection of the base scores.
2. **Gusset Bisector Crease Angle**:
   $$\theta_{\text{bisector}} = \arctan\left(\frac{H_{\text{side}}}{H_{\text{end}}}\right)$$
   For equal wall heights ($H_{\text{side}} = H_{\text{end}} = H$), $\theta_{\text{bisector}} = 45.0^\circ$.
3. **Crease Step Offset**: Step the gusset fold line outward by $1.0 t$ relative to the base score line to prevent corner bunching.

```
       Base Edge Score ──────────────────┐
                                         │  <- Offset 1.0t
       Gusset Bisector (45°) \          ( O ) Relief Hole (r >= 1.0mm)
                              \          │
       Side Wall Score ──────────────────┘
```

### 4. Mechanical Retention Detents (Walker Lock)
To guarantee zero-glue retention under vibration and transit drop testing:
- **Retention Barb Notch**: Cut a $0.8\text{mm} - 1.2\text{mm}$ deep hook notch into each side of the locking tab.
- **Undercut Angle**: $75^\circ - 80^\circ$ barb undercut angle prevents tab back-out once seated below the base panel.
- **Locking Tactile Feedback**: Proper dimensioning produces a distinct audible and tactile "snap" when the tab passes the slot edge and springs outward under board elasticity.
- **Pull-Out Resistance**: A properly designed Walker lock withstands $> 25\text{ N}$ of vertical extraction force per tab without adhesive.

### 5. Board Grain Direction Alignment
- **Grain Orientation Rule**: The board machine grain direction must run **parallel** to the tray length $L$ (perpendicular to the rollover end-wall creases).
- **Impact on Performance**:
  - Rollover folds transverse to grain fold cleanly without cracking and exert maximum spring-tension against the locking slots.
  - Longitudinal base stiffness resists center sagging under product weight.

### 6. Substrate Specification & Tooling Guidelines
- **Substrates**: Virgin Kraft Board, Solid Bleached Sulfate (SBS), or Folding Boxboard (FBB) 300–450 gsm ($t = 0.40 - 0.65\text{mm}$); or E-flute corrugated ($t = 1.4 - 1.6\text{mm}$) for heavy shippers.
- **Die Rule Assignment**:
  - Through-cut rule: 2-pt ($0.71\text{mm}$) cutting knife, RGB `#FF0000`.
  - Rollover crease: 2-pt creasing rule with polyurethane creasing matrix, RGB `#00FF00`.
  - Base slot: CNC laser-cut slot with rounded radius ends ($r \ge 0.5\text{mm}$) to prevent tear initiation.

## Failure Modes (Mandatory)
1. **Rollover Spring-Back & Slot Disengagement**: Omitting retention barbs or under-sizing base slots ($W_{\text{slot}} < t$); causes inner walls to spring upward out of the slots, completely collapsing the tray structure.
2. **Corner Web Gusset Fiber Rupture**: Omitting relief cutouts ($r \ge 1.0\text{mm}$) at the 4-crease corner intersection; creates extreme hydraulic shear forces during rollover, tearing the outer paperboard surface open at the corners.
3. **Friction Lock Tab Buckling during Insertion**: Designing locking tabs with aspect ratios exceeding $L/W > 3$ without center stiffening creases; causes the tab to crumple and bend backwards rather than penetrating the base slot.
4. **Flute / Grain Direction Mismatch causing Wall Bowing**: Running the paperboard grain parallel to rollover creases; causes uneven score folding, severe exterior surface cracking, and inward bowing of the side walls.
5. **Slot Width Under-sizing / Board Caliper Jamming**: Designing the slot width to match nominal paper thickness ($W_{\text{slot}} = t$) without manufacturing tolerance ($+0.3\text{mm}$); variations in board humidity and coating thickness prevent tabs from entering, stalling packaging assembly lines.
