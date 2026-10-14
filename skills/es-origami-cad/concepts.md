# One buildable packaging concept

| Request field | Record before building | Do not substitute |
| --- | --- | --- |
| Family | Implemented type in [contract](contract.md) | An application idea from the taxonomy |
| Dimensions | Applicable millimetre parameters | Screen pixels or unrelated family defaults |
| Caliper | Explicit `thickness` in mm | A generic material name as measured caliper |
| Outputs | `presentation`, optionally `printer` | A preview screenshot as cutter geometry |
| Recipient | Requested spot names, bleed, units and approval limits | Local display colors as their tooling contract |
| Preview | `available` or `allow-unavailable` | Fabricated geometry for unsupported motion |

## Known-good starting requests

Use [tuck-box-printer.json](examples/tuck-box-printer.json) for both profiles and
[hex-petal-presentation.json](examples/hex-petal-presentation.json) for presentation.
Resolved defaults and parameter applicability come from the generated contract.
Research miura/deer requests are presentation-only; printer rejects a research
pattern as a closed-carton request.
These are genuine generator inputs, not a physical sample or certified design.

Right: `{"width":80,"depth":50,"height":120,"thickness":0.5}` for tuck-box.
Wrong: add `radius` to tuck-box merely because another family accepts it; `input`
rejects unsupported/ignored parameters. Never insert shell commands into JSON.

Input is limited to 200 lines and 64 KiB. This bounds declarative requests and
review cost, not the size of generated geometry. Reject non-finite numbers,
unknown keys, non-positive dimensions/caliper and incompatible profiles.

## Weak concepts to resolve

| Weak request | Resolve | When NOT to use the shortcut |
| --- | --- | --- |
| “A luxury box” | Pick one family and dimensions | When opening/closing requirements differ |
| “Exactly like this photo” | Distinguish style from implemented topology | When the image hides hinges or locks |
| “Printer-ready” | Record recipient import and sample approval | When no recipient requirements exist |
| “Guaranteed flat-foldable” | Scope the mathematical condition | For a volumetric carton or global motion |
| “Zero-glue food box” | Separate closure from food-contact qualification | For certified food-contact claims |

Select one concept. Changing family is a new request/run. Do not carry incompatible
parameters forward; preserve the old run, regenerate, validate and inspect.
