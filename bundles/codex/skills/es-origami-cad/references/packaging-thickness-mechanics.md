# Caliper, allowance and export semantics

Material constants and tooling recommendations require measured evidence.
This package supplies experimental geometry, not a qualified material recipe.
See [rules.md](../rules.md) and [contract.md](../contract.md) for executable homes.

## Known formula conflict

The project mandate is `C = π(R + Kt)/2` at 90°. The current executable
`OrigamiCreasePattern.calculate_score_allowance` is an angle-scaled heuristic,
with default 0.45t at 90°. These are not equivalent. For R=0, K=0.45,
the mandated expression yields about 0.707t, not 0.45t or 0.50t.
Do not silently replace the geometry formula in a packaging/host-bundle task.
Do not report compliance or use uncalibrated K values as a production recipe.

Right: record explicit caliper and the actual executable allowance in the run.
Wrong: change K until a convenient dimensional check passes, or infer caliper
from grammage alone. Grain, tooling, moisture and material behavior need samples.

```python
# Right: delegate to the owning engine and preserve explicit inputs.
allowance_mm = cp.calculate_score_allowance(thickness_mm)
# Wrong: allowance_mm = 0.5 * thickness_mm  # a second, unbound engine rule
```

## Export decision matrix

| Output | Semantics | When NOT to use |
| --- | --- | --- |
| SVG presentation | Source lines/layers with M/V `data-fold` where applicable | Not recipient-approved machine setup |
| R12 presentation DXF | CUT/CREASE/PERFORATE/GLUE; M/V collapsed into CREASE | Not a way to recover M/V assignments |
| Printer PDF | Five distinct named spot colorants, vector strokes/legend/bleed | Not recipient RIP acceptance |
| R2000 printer DXF | Millimetres, y-up orientation, printer layer/spot mapping | Not proof of CAD/plotter import |

| Presentation layer | Exact local color | Meaning |
| --- | --- | --- |
| CUT | #FF0000 | Cut knife |
| CREASE | #00FF00 | Score/fold |
| PERFORATE | #0000FF | Perforated line |
| GLUE | #FF00FF | Adhesive area |

Only required/applicable emitted groups are checked. A closed geometric CUT
contour can consist of multiple SVG segments; never require one `<path>`.
Printer defaults are CutContour, CreaseLine, Perforation, Bleed, GlueArea.
Validated recipient overrides are permitted; presentation colors do not define
a recipient's spot names, stroke widths or cutting tools.

## Common pitfalls and diagnostics

| Symptom | Evidence/action | Check home |
| --- | --- | --- |
| Fold line becomes a cut | Restore separate layer assignment | `svg-layers`, `dxf-layers` |
| Spots alias each other | Use five distinct valid recipient names | `printer-spots` |
| Scale/orientation/bleed wrong | Regenerate and inspect exchange metadata | `printer-exchange` |
| Caliper missing or invalid | Supply finite positive `thickness` | `input` |
| Flap fit/load/grain uncertain | Cut and fold a measured material sample | PHYSICAL_FOLD_FIT: NOT VERIFIED |

When NOT to use: food-contact, strength, moisture, grain, springback or automated
folder-gluer claims without material and recipient qualification. No fixed grain
clearance or score-depth percentage is established by this reference.
