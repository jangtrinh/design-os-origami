---
name: es-origami-cad
description: "Use when generating parametric packaging dielines, preparing printer exchange files, validating exports, or inspecting source-derived fold previews."
metadata:
  author: DESIGN:OS
  qualification: experimental-unqualified
---

# DESIGN:OS Origami CAD

One workflow: Concept → Build → Check → Hand over → Adjust.
Use an existing product checkout as `--repo-root`; installed skill copies contain
entrypoints and guidance, not the engine. Python ≥3.10; runtime uses stdlib.

## 1. Concept

Read [concepts.md](concepts.md) and choose one buildable request. The executable
[contract.md](contract.md) owns family choices, parameters, defaults and outputs.
Read the numbered [rules.md](rules.md) before editing inputs. Caliper and dimensions
are explicit; material qualification is separate from geometry generation.

| Need | Choose | Limit |
| --- | --- | --- |
| Carton blank or cutter display | Presentation | SVG/R12 DXF/viewer; no recipient approval |
| Printer exchange | Presentation + printer | PDF/R2000 DXF; recipient import still required |
| Local mathematical research | Presentation-only research types | No printer/physical acceptance |
| Preview of unsupported motion | Permit unavailable | Preserve 2D and honest status |

When NOT to use: production release without physical fold/fit and recipient
approval, food-contact or load certification, or an unimplemented catalogue idea
represented as an existing generator. No hosted service or remote connector.

## 2. Build

Start from [tuck-box-printer.json](examples/tuck-box-printer.json) or
[hex-petal-presentation.json](examples/hex-petal-presentation.json). Use a fresh
output directory; change only declarative inputs, never executable commands.

```sh
python3 skills/es-origami-cad/build.py --repo-root . \
  --spec skills/es-origami-cad/examples/tuck-box-printer.json \
  --output-dir /absolute/new-run
```

[build.py](build.py) prints the completed output path. It delegates to the product,
records source/contract/artifact hashes and refuses an existing destination.
Read the receipt; a failed build is not a deliverable.

## 3. Check

Run [validate.py](validate.py) against that run. Read [look.md](look.md), then run
[look.py](look.py) with an explicitly prepared browser cache.

```sh
python3 skills/es-origami-cad/validate.py --repo-root . --output-dir /absolute/new-run
python3 skills/es-origami-cad/look.py --repo-root . --output-dir /absolute/new-run \
  --browser-cache /absolute/user-cache --sheet /absolute/new-run/evidence/look-sheet.png
```

Validate/look: exit 0 = checked, 1 = rejected, 2 = could not run. Validate is
offline; look blocks external requests except the pinned cached Three.js asset.
Neither downloads dependencies nor installs into the skill. Inspect the sheet.
Machine checks do not grade visual clarity or physical assembly.

## 4. Hand over

Use these fields, preserving failures and missing checks:

```text
OUTPUT: <absolute run directory and artifact paths>
BUILD: <command, exit, source and contract hashes>
VALIDATE: <exit and actual diagnostics or ok>
LOOK: <exit, sheet path, numbered observations>
PHYSICAL_FOLD_FIT: NOT VERIFIED.
RECIPIENT_IMPORT: NOT VERIFIED.
LIMITS: <preview availability, checks not run, material assumptions>
```

Without a browser use exactly:
`LOOK: NOT RUN — browser runtime or pinned cache is unavailable.`
Do not say “should work”. Sampled continuity does not prove continuous motion,
collision avoidance, physical fit, or compliance with a recipient's tooling.
The current allowance is a heuristic (0.45t at 90°), not π(R + Kt)/2;
packaging this engine does not resolve that known formula conflict.

## 5. Adjust

Edit the concept/spec, build into another new directory, rerun checks, inspect
fresh evidence. Keep the previous run for comparison. Do not hand-edit generated
outputs, the [contract](contract.md), or host bundle copies.

| What goes wrong | Do this instead |
| --- | --- |
| `input` | Use applicable finite positive inputs; rules 2 and concepts |
| `contract` / `artifact-receipt` | Rebuild from matching checkout; rules 1, 4 |
| `svg-layers` / `dxf-layers` | Regenerate separated layer exports; rules 5, 8 |
| `printer-spots` / `printer-exchange` | Restore distinct spots/units; rules 9, 10 |
| `preview-status` | Preserve source-derived unavailable state; rule 11 |
| Missing browser | Record NOT RUN; look.md without-browser clause |

## Knowledge routing

| Reference | Read when |
| --- | --- |
| [Origami mathematics](references/origami-mathematics.md) | Local vertex conditions and limits |
| [Thickness mechanics](references/packaging-thickness-mechanics.md) | Caliper, allowance and layer semantics |
| [Creative catalogue](references/creative-catalog-taxonomy.md) | Selecting an implemented family versus a concept |
| [Kinematic folding](references/kinematic-folding-3d.md) | Source-derived hinges and preview qualification |
| [Attribution](ATTRIBUTION.md) | Source provenance and permission boundaries |
