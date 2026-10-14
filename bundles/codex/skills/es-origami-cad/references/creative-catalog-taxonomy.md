# Creative catalogue: ideas versus generators

The legacy taxonomy contains 305 application ideas across five structural
families. They are not 305 independently validated CAD models. Executable types,
parameters and defaults are owned by [contract.md](../contract.md).

| Concept family | Legacy idea count | Implemented starting point | Trade-off |
| --- | --- | --- | --- |
| Blooming petal/flower closures | 65 | hex-petal | No arbitrary polygon/petal generator implied |
| Polyhedral/diamond facets | 62 | diamond-box | Retain honest unavailable preview where gated |
| Twist/spiral closures | 58 | Research concept | No implemented twist carton implied |
| Zero-glue interlocks | 64 | zero-glue-tray | Closure idea does not establish physical locking |
| Kinetic tessellations | 56 | miura-ori research CLI | No cushioning/load certification |

## Select a buildable concept

Right: select `hex-petal` and explicit radius/height/caliper from the contract,
then build [the presentation example](../examples/hex-petal-presentation.json).
Wrong: translate “octagonal rose box” into `--type octagonal-rose` when that
choice is absent from the executable contract.

```json
{"type":"hex-petal","parameters":{"radius":45,"height":60,"thickness":0.5}}
```

This fragment explains family selection; use the complete example's schema,
profiles and preview requirement when building. Application ideas may require
new topology research rather than a relabelled existing net.

## Additional carton choices

Tuck, gable, pillow, crash-lock, FEFCO 0201/0427, sleeve-tray and food-box are
source-derived generator choices, alongside hex-petal, diamond and zero-glue
tray. The contract owns the current list; this narrative is not a registry.
Sleeve-tray delivers separately named sleeve and tray blanks; do not merge
parts or imply sheet nesting/assembly acceptance. Research types stay separate.

| Need | Decision | When NOT to use |
| --- | --- | --- |
| Known family with new dimensions | Parameterize a registered generator | When new hinge/lock topology is required |
| New aesthetic/application | Record concept, inspect generator limits | Never invent supported flags |
| Two-piece assembly | Preserve each named blank and outputs | Not a combined mesh or nested sheet |
| Catalogue reproduction | Use its recorded inputs before comparison | Not unrelated custom dimensions |

## Common pitfalls and diagnostics

| Failure | Action | Home |
| --- | --- | --- |
| Unknown family/ignored parameter | Use contract choices and applicability | `input` |
| Missing second blank | Deliver each requested named artifact | `artifact-files` |
| Catalogue mismatch | Regenerate the actual recorded inputs | `catalog-consistency` |
| Unavailable preview | Preserve its explicit status and 2D exports | `preview-status` |

When NOT to use: a concept entry as proof of fit, load capacity, food-contact
compliance, global foldability, recipient approval or available 3D motion.
