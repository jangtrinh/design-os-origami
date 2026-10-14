# Mechanical rules and their homes

Every numbered rule has an enforcing home. Checks print `<check>: <what to fix>`;
see [validate.py](validate.py). Eye-only decisions are numbered in [look.md](look.md).

## 1. Bind the executable contract
Statement: use the contract generated from this checkout, not an edited copy.
Keep it (API): build/validate resolve `--repo-root`; source and contract hashes bind the run.
Rejected when: `contract` finds stale, changed or mismatched contract bytes.

## 2. Use a bounded declarative input
Statement: supply applicable finite positive dimensions/caliper, known keys and profiles.
Keep it (API): build reads the normalized JSON schema; maximum 200 lines and 64 KiB.
Rejected when: `input` finds an invalid/ignored parameter, schema or incompatible output request.

## 3. Deliver every requested file
Statement: requested profiles produce a complete artifact set with confined relative paths.
Keep it (API): build creates a fresh staged run; validator follows its declared artifacts.
Rejected when: `artifact-files` finds missing, linked or escaping paths or incomplete outputs.

## 4. Preserve the run receipt
Statement: the receipt records actual normalized inputs, outputs and provenance.
Keep it (API): build writes `artifact.json`; never hand-edit it after export.
Rejected when: `artifact-receipt` finds malformed, inconsistent or incomplete receipt structure.

## 5. Keep presentation SVG layers separate
Statement: CUT red #FF0000, CREASE green #00FF00, PERFORATE blue #0000FF, GLUE magenta #FF00FF.
Keep it (API): use the product SVG exporter and inspect groups for actual emitted line types.
Rejected when: `svg-layers` finds missing/misassigned required layers or colors.

## 6. Preserve actual mountain/valley metadata
Statement: actual M/V SVG segments retain `data-fold`; generic CREASE has no invented direction.
Keep it (API): exporter consumes the source crease type. Presentation DXF collapses M/V to CREASE.
Rejected when: `fold-metadata` finds missing or wrong direction on source M/V segments.

## 7. Preserve geometric topology
Statement: the blank must retain the product's exterior/material/slit topology checks.
Keep it (API): reuse product geometry validation; one contour need not be one SVG path.
Rejected when: `topology` detects an invalid exterior, disconnected material or invalid slit attachment.

## 8. Keep presentation DXF layer semantics
Statement: layer assignments preserve CUT/CREASE/PERFORATE/GLUE; M/V identity is not encoded.
Keep it (API): use the R12 exporter rather than inferring geometry from an image.
Rejected when: `dxf-layers` finds wrong or absent applicable layer separation.

## 9. Keep printer spots distinct
Statement: five valid distinct spot names represent CutContour, CreaseLine, Perforation, Bleed, GlueArea.
Keep it (API): printer settings use contract defaults or validated recipient overrides.
Rejected when: `printer-spots` finds invalid, reused or incorrectly mapped spot names.

## 10. Preserve printer exchange metadata
Statement: PDF/R2000 DXF retain units, orientation, scale, bleed and their required resources.
Keep it (API): generate both profiles from identical resolved inputs; preserve each blank's files.
Rejected when: `printer-exchange` finds wrong units/orientation/resources/scale/bleed metadata.

## 11. Preserve honest preview availability
Statement: source-derived qualification determines available versus unavailable preview.
Keep it (API): require `available` only when the sampled gate passes; otherwise permit unavailable.
Rejected when: `preview-status` contradicts qualification or exposes fabricated fallback geometry.

## 12. Compare catalogue inputs correctly
Statement: only checked-in catalogue examples compare against their actual recorded inputs.
Keep it (API): regenerate matching catalogue inputs; custom dimensions are not catalogue defaults.
Rejected when: `catalog-consistency` finds a checked-in entry inconsistent with matching regeneration.

## 13. Bind artifact bytes
Statement: all manifest-listed generated artifacts match their receipt hashes.
Keep it (API): rebuild after any change; capture evidence separately from immutable generated outputs.
Rejected when: `artifact-hashes` finds changed bytes or a mismatched hash.

## 14. Inspect and report the limits
Statement: machine success does not qualify taste, physical assembly or recipient import.
Keep it (API): inspect look items L1–L3; report the exact handover fields in [SKILL.md](SKILL.md).
Rejected when: human look items L1–L3 show unclear, clipped or mismatched output; no automated taste score.

When NOT to use: these checks are not a material qualification, food-contact
approval, printer RIP/CAD import receipt or proof of collision-free continuous motion.
The mandated π(R + Kt)/2 and current default 0.45t heuristic differ; no claim of
formula compliance is permitted. Geometry correction belongs to a separate scope.
