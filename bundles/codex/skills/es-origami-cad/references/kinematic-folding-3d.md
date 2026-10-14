# Source-derived folding preview

The viewer extracts panels and hinges from generated crease geometry. Qualified
nets display rigid-panel motion after the product's sampled continuity gate.
Unsupported nets retain 2D and explicitly unavailable 3D; no decorative fallback
mesh is evidence of a fold. Physical assembly and collisions remain unqualified.

## Hinge mathematics

For unit hinge axis u through p, rotate vertex v by angle ρ:

`v' = p + (v-p)cosρ + [u × (v-p)]sinρ + u[u·(v-p)](1-cosρ)`.

A child's transform composes with its parent's transform. The rooted spanning
tree does not eliminate constraints on the remaining hinges; loop closure needs
its own source-derived checks. An axis reversal also reverses positive rotation.

Right: transform a child around its source hinge in its parent coordinate frame.
Wrong: rotate every panel independently around an arbitrary world-space center.

```text
right: T_child = T_parent × T_source_hinge(rotation)
wrong: T_child = decorative_animation(requested_family_label)
```

## Preview qualification decisions

| State | Display | When NOT to infer more |
| --- | --- | --- |
| Source extraction + sampled continuity pass | Real source-derived panels/hinges | Not physical fit, collision freedom or continuous-time proof |
| Coordinated motion passes endpoint/loop constraints | Qualified sampled coordinated candidate | Not all arbitrary custom dimensions |
| Unsupported extraction/motion | SVG + explicit unavailable status | Never synthesize a substitute mesh |
| Browser/cache unavailable | LOOK NOT RUN | Unit tests or an old screenshot do not replace a capture |

Baseline seam tolerance and samples are the owning engine's contract, not a
host-specific constant to loosen. Coordinated candidates additionally check
original endpoints and loop closure. Preserve rejected candidates and status.

## Common pitfalls and diagnostics

| Symptom | Evidence/action | Home |
| --- | --- | --- |
| Wrong M/V direction | Compare actual source segments with SVG metadata | `fold-metadata` |
| Floating or torn panels | Inspect source hinge graph and sampled continuity | `preview-status`, look L7 |
| Canvas rectangle with no model | Measure pixels and source-model stability | Look L5, L6 |
| Console/network failures | Keep error receipt and reject unexpected requests | Look L8 |
| “Available” on unsupported net | Restore honest unavailable state and SVG | `preview-status`, look L9 |

The generated HTML uses pinned Three.js r128. Offline look intercepts only that
exact request with checksum-verified cache bytes; every other external request
fails. No download occurs during look. [look.md](../look.md) owns fixed shots and
[ATTRIBUTION.md](../ATTRIBUTION.md) records renderer provenance.

When NOT to use: certifying mechanical locking, thickness-aware contact,
continuous collision avoidance, multi-sheet assembly, or recipient import.
