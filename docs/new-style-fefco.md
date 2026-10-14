# FEFCO 0201 and 0427 style generators

Two parametric blanks follow the FEFCO/ESBO International Fibreboard Case Code.
The code describes construction styles; every dimension here is parametric and
internal (`width` = L, `depth` = B, `height` = H, millimetres), as the code's
"Case dimensions" section defines L x B x H. Neither generator is a production
qualification: slot widths, clearances and tab sizes are converter choices that
the docstrings label as such, and physical erection is not verified locally.

## Sources

| Ref | Source | Used for |
| --- | --- | --- |
| S-FEFCO | FEFCO/ESBO "International fibreboard case code" PDF, fefco.org `files/FEFCO_ESBO_codes_of_designs.pdf`, SHA-256 `dd1278686cdef038b944a420869349a7b57074d6491f760ba39fcc5143e89e43` | p.6 internal L x B x H, "layouts ... viewed from the inside", manufacturer's joint glued/stitched/taped; p.7 02 slotted-type and 04 folder-type group definitions; p.26 style 0201 drawing; p.44 style 0427 drawing |
| S-FBA | Fibre Box Association, "Box Styles Basics" (2014), iopp.org, SHA-256 `fd1f4d3fc5a9d0dc8b6027eeb251c0525a068fc459c789e75fba824b69bf1779` | 0201: all flaps the same length, outer flaps one-half the container width; 0427: single die-cut piece, unbroken bottom, several layers in the end panels, locking cover |

The two primary-source PDFs above are the style references. Diagram pages were rendered and read, not inferred.

## `generate_fefco_0201(width=200, depth=150, height=120, thickness=0.5)`

Regular slotted container (FEFCO 0201, slotted-type box, M/A erection).

- Panels in the code's drawn order: manufacturer's joint flap, L, B, L, B. The joint
  flap extends the first L panel, is chamfered at both ends and carries a magenta
  `GLUE` centreline (`ManufacturersJoint_Glue`); stitched or taped joints use the
  same flap.
- Eight closing flaps, four top and four bottom, each B/2 deep on every panel
  (S-FBA), so the outer flaps meet at the centre and the inner flaps leave the usual
  gap.
- Slots between adjacent flaps are centred on the wall scores and run from the flap
  edge to the body score. Default `slot_width` is 2 x caliper + 1 mm; the glued
  corner gets a half slot on each side so the assembled corner has a full slot.
  This width is an engineering default, not a FEFCO figure. Pass `slot_width`
  explicitly for a converter's slotting knife.
- Score allowance from `calculate_score_allowance(90)` (0.45 x caliper) is added to
  the L and B panel widths; H is used as given, matching the existing generators.
- Rejections: non-finite or non-positive sizes, negative caliper, `width < depth`
  (L is the longer side at the opening by definition), slot wider than a panel,
  non-finite/non-positive joint flap, or joint wider than the receiving B panel
  (including its score allowance).

Every blank is a closed outline with no declared slits; the topology gate reports
no violations for defaults, asymmetric variants and zero caliper, and the
dieline-derived fold preview is available: 13 material faces, 12 tree hinges, and at
100 % the folded extents equal L+allowance, B+allowance and H.

## `generate_fefco_0427(width=200, depth=150, height=60, thickness=0.5)`

Roll-end tray with locking cover (FEFCO 0427, folder-type, manual erection); the
e-commerce "roll end tuck front" mailer. No glue geometry is emitted.

- Columns across the blank, as drawn on S-FEFCO p.44: front wall (H), base (B), back
  wall (H), cover (B), tuck front. L runs along the walls, so it is the vertical
  dimension of the blank exactly as the code draws it.
- Roll ends on both B edges of the base: outer end wall (H), roll strip between two
  scores, inner end wall (H) ending in a centred locking tab. The strip is
  2 x caliper + `roll_clearance` (default 1 mm) so the inner wall rolls over the two
  dust flaps; with zero caliper only the clearance remains.
- Dust flaps on the front and back walls, each B/2 minus clearance deep so the two
  meet at the centre of the end; cover side flaps (chamfered) and the tuck front are
  H minus the roll strip deep so they clear the rolled ends.
- Lock slots are closed holes in the base, one roll strip inboard of each end score,
  sized tab width + 2 x clearance by the strip depth. The FEFCO sketch draws the slot on
  the score; this generator places it where the rigid inner wall actually lands once
  caliper is accounted for, and the tests prove the folded tabs end inside the slot
  footprint one tab depth below the base plane.
- Six knife slits separate the dust flaps and cover side flaps from the end columns.
  They are declared on `cp.cut_slits`, run from the body score to the blank edge, and
  the gate confirms they do not sever the blank.
- Rejections: non-finite or non-positive sizes, negative caliper, H not exceeding the
  roll strip, B too small for dust flaps and the lock slot, non-positive clearance or
  tab depth. Width plus score allowance must exceed three roll-strip widths by
  the resolvable gap `1e-7 × max(1, roll_strip)` mm: the two lock slots need a
  positive gap beyond the unchanged segment-intersection precision.

The topology gate reports no violations for defaults, asymmetric variants and zero
caliper. The fold preview is available: 17 material faces, 16 tree hinges, sampled
seam gap 0 mm, and at 100 % the folded extents equal B+allowance, L+allowance and
H + tab depth (the rigid tabs protrude through the base plane by their depth).

## Shared assembly helper

`packaging_fefco_helpers.assemble_blank` builds both blanks from named material
pieces plus their shared scores. Boundary portions covered by a score become
`CREASE` hinges, portions shared by two pieces without a score become declared knife
slits, and everything else becomes the die outline. Slots are notches and lock slots
are explicit hole loops, so the outline closes by construction and the assembly
raises if a score is not shared by exactly two pieces.

## Exports and names

Both generators return a plain `OrigamiCreasePattern`; existing SVG, legacy DXF,
viewer and printer exporters work unchanged. Pattern names are
`FEFCO0201_{W}x{D}x{H}` and `FEFCO0427_{W}x{D}x{H}`. CLI types `fefco-0201` and `fefco-0427` export each blank in presentation or
printer mode; each also has a model-switcher entry and separate source downloads.

Bleed note: `printer_bleed.outward_envelope` used to raise `Ambiguous bleed boundary`
when a concave notch of the outer contour was narrower than the bleed distance, which
the default 0201 slot (2 mm at 0.5 mm caliper) triggers at the default 3 mm bleed.
The envelope now also splits collinear overlapping edge strips at each other's
endpoints, so such a notch is bridged by the bleed exactly as the union of strips
implies; wider notches keep their offset walls, tolerances are unchanged, and the
seven existing models' default printer PDF/DXF bytes are identical before and after.
