# 7 blanks. 4 previews.

**DESIGN:OS Origami** · Python ≥3.10 · [MIT](LICENSE)

DESIGN:OS Origami generates parametric carton dielines, printer exchange files and source-derived folding previews from Python.

![The generated tuck blank at 100% fold progress in the actual WebGL preview](docs/assets/tuck-fold-100.png)

One generated tuck blank. 100% fold progress. A rigid-panel visualization does not certify physical assembly.

Source: `TuckBox_80x50x120` · blank 275.9 × 250.45 mm · caliper 0.5 mm.

Fold gate: 4 / 4 samples pass (25%, 50%, 75%, 100%). Twelve shared edges stay within a 0.5 mm gap tolerance. Three catalogue defaults retain 2D with no qualified preview. [Measured catalogue](docs/assets/catalog.json).

## Choose the workflow for the job

| Task | Drawing / separate inspection | DESIGN:OS Origami |
| --- | --- | --- |
| Geometry changes | Edit a drawing and inspect each changed path. | Regenerate from dimensions and caliper; inspect the result. |
| Printer handoff | Specify the recipient’s layers, spots and scale. | Start from an explicit five-spot PDF and mm/y-up printer DXF; still qualify the recipient. |
| Fold inspection | Fold a sample or use a separate simulation workflow. | Inspect source-derived rigid-panel motion when the continuity gate permits it. |
| Physical qualification | Check material, fit and manufacturing behaviour. | The same physical checks remain necessary; the preview does not replace them. |

Use a recipient-qualified CAD/prepress workflow for accepted manufacturing exchange. Use a physical sample to establish fold/fit. These generated files and previews do not establish either outcome.

## One blank, multiple outputs

- Generate seven parametric carton dielines as SVG and presentation DXF.
- Export a printer profile with five named spots, 1 pt PDF strokes, a legend and 3 mm default bleed.
- Inspect source-derived rigid-panel motion when the sampled continuity gate permits a 3D preview.

The topology tests check a single CUT contour, connectivity and slit attachment. These structural checks do not establish physical foldability.

## Quickstart from a checkout

From the repository checkout, with Python ≥3.10. The first command uses presentation mode; the second adds the printer profile.

```sh
PYTHONPATH=src python3 -m origami_cad.cli generate --type tuck-box --output-dir output
PYTHONPATH=src python3 -m origami_cad.cli generate --type tuck-box --profile printer --output-dir output
find output -maxdepth 1 -type f | sort
```

The sorted file list for this tuck-box run:

```text
output/TuckBox_80x50x120.dxf
output/TuckBox_80x50x120.svg
output/TuckBox_80x50x120_printer.dxf
output/TuckBox_80x50x120_printer.pdf
output/TuckBox_80x50x120_viewer.html
```

### First safe use

1. Generate the presentation files and inspect the full SVG blank. Keep each earlier delivery in a separate output directory before regenerating.
2. Generate the printer profile and inspect its PDF legend, spot names, bleed and dimensions at 100% scale.
3. Open the generated viewer, inspect available fold motion, then qualify RIP/CAD import and physical fold/fit with the recipient before manufacturing.

## Seven cartons. Every blank visible.

Individual source-generated examples, with full SVGs and separate printer PDF/DXF downloads. Dimensions below describe the shown blank, not the finished carton.

| Carton / CLI type | Shown blank / caliper | 3D preview | Source SVG | Printer PDF / DXF |
| --- | --- | --- | --- | --- |
| Tuck box / `tuck-box` | 275.9 × 250.45 mm / 0.5 mm | 3D preview available | [SVG](docs/assets/models/tuck-box.svg) | [PDF](docs/assets/models/tuck-box.pdf) / [DXF](docs/assets/models/tuck-box.dxf) |
| Hexagonal petal box / `hex-petal` | 235.3 × 203.8 mm / 0.4 mm | 3D preview available | [SVG](docs/assets/models/hex-petal.svg) | [PDF](docs/assets/models/hex-petal.pdf) / [DXF](docs/assets/models/hex-petal.dxf) |
| Diamond faceted box / `diamond-box` | 240.0 × 80.0 mm / 0.45 mm | 3D preview unavailable | [SVG](docs/assets/models/diamond-box.svg) | [PDF](docs/assets/models/diamond-box.pdf) / [DXF](docs/assets/models/diamond-box.dxf) |
| Zero-glue tray / `zero-glue-tray` | 220.0 × 190.0 mm / 0.5 mm | 3D preview unavailable | [SVG](docs/assets/models/zero-glue-tray.svg) | [PDF](docs/assets/models/zero-glue-tray.pdf) / [DXF](docs/assets/models/zero-glue-tray.dxf) |
| Gable handle box / `gable-box` | 567.9 × 281.6 mm / 0.5 mm | 3D preview available | [SVG](docs/assets/models/gable-box.svg) | [PDF](docs/assets/models/gable-box.pdf) / [DXF](docs/assets/models/gable-box.dxf) |
| Pillow box / `pillow-box` | 272.9 × 110.0 mm / 0.5 mm | 3D preview available | [SVG](docs/assets/models/pillow-box.svg) | [PDF](docs/assets/models/pillow-box.pdf) / [DXF](docs/assets/models/pillow-box.dxf) |
| Crash-lock box / `crash-lock-box` | 295.9 × 196.4 mm / 0.5 mm | 3D preview unavailable | [SVG](docs/assets/models/crash-lock-box.svg) | [PDF](docs/assets/models/crash-lock-box.pdf) / [DXF](docs/assets/models/crash-lock-box.dxf) |

### Tuck box

![Tuck box full source dieline with CUT, CREASE and GLUE paths](docs/assets/models/tuck-box.svg)

Blank 275.9 × 250.45 mm · caliper 0.5 mm. 3D preview available.

### Hexagonal petal box

![Hexagonal petal box full source dieline with CUT, CREASE and GLUE paths](docs/assets/models/hex-petal.svg)

Blank 235.3 × 203.8 mm · caliper 0.4 mm. 3D preview available.

### Diamond faceted box

![Diamond faceted box full source dieline with CUT, CREASE and GLUE paths](docs/assets/models/diamond-box.svg)

Blank 240.0 × 80.0 mm · caliper 0.45 mm. 3D preview unavailable.

### Zero-glue tray

![Zero-glue tray full source dieline with CUT, CREASE and GLUE paths](docs/assets/models/zero-glue-tray.svg)

Blank 220.0 × 190.0 mm · caliper 0.5 mm. 3D preview unavailable.

### Gable handle box

![Gable handle box full source dieline with CUT, CREASE and GLUE paths](docs/assets/models/gable-box.svg)

Blank 567.9 × 281.6 mm · caliper 0.5 mm. 3D preview available.

### Pillow box

![Pillow box full source dieline with CUT, CREASE and GLUE paths](docs/assets/models/pillow-box.svg)

Blank 272.9 × 110.0 mm · caliper 0.5 mm. 3D preview available.

### Crash-lock box

![Crash-lock box full source dieline with CUT, CREASE and GLUE paths](docs/assets/models/crash-lock-box.svg)

Blank 295.9 × 196.4 mm · caliper 0.5 mm. 3D preview unavailable.

These catalogue examples record their own dimensions and caliper in [catalog.json](docs/assets/catalog.json); they are not a promise that every parameter combination folds. Miura-ori and deer-base are separate research patterns, outside this carton catalogue.

## A handoff with named paths

Export a printer profile with five named spots, 1 pt PDF strokes, a legend and 3 mm default bleed.

![Actual tuck-box printer PDF raster, including the complete bleed envelope and five-spot legend](docs/assets/tuck-printer.png)

Actual PDF raster · default 3 mm bleed · five spot resources. Print or import at 100% scale.

| Default spot name | Purpose |
| --- | --- |
| `CutContour` | Cut contour |
| `CreaseLine` | Crease paths |
| `Perforation` | Perforation paths |
| `Bleed` | Exterior allowance |
| `GlueArea` | Glue paths |

Printer DXF is R2000 with millimetre units and y-up coordinates. Presentation DXF is the separate R12 drawing export; its recipient unit/orientation profile is unspecified and it loses mountain/valley direction.

The legend uses all five spots even when a particular blank has no paths of a given type. Agree the names, bleed and import settings with the recipient. [Download printer PDF](docs/assets/models/tuck-box.pdf) · [Download printer DXF](docs/assets/models/tuck-box.dxf).

## From flat paths to moving panels

Inspect source-derived rigid-panel motion when the sampled continuity gate permits a 3D preview.

[Open the standalone tuck-box viewer](docs/demo/tuck-box.html). Rotate, pan and zoom the actual generated viewer; use its fold controls to inspect progress. The 2D drawing remains available if JavaScript, the Three.js r128 CDN or WebGL is unavailable.

## What is NOT verified

- Recipient RIP/CAD import and prepress acceptance are not verified.
- Physical fold/fit, material, grain, tooling and manufacturing tolerances are not verified.
- Crash-lock box, zero-glue tray and diamond faceted box have no qualified 3D preview.
- Continuity is sampled at 25%, 50%, 75% and 100% with a 0.5 mm tolerance; continuous-time motion and collision avoidance are not verified.

Score allowances are uncalibrated heuristics. Knowledge documents have mixed provenance; structural lint does not establish their engineering claims.

## Before you cut or fold

<details>
<summary>What does DESIGN:OS Origami generate?</summary>

It generates seven parametric carton styles as SVG and presentation DXF, a standalone viewer, and a separate printer profile with spot-colour PDF and R2000 DXF. Miura-ori and deer-base are separate research patterns.

</details>

<details>
<summary>Which cartons have a 3D fold preview?</summary>

The shown tuck box, hexagonal petal box, gable handle box and pillow box pass the sampled continuity gate. Diamond faceted box, zero-glue tray and crash-lock box retain their 2D dielines with no 3D fold preview. Availability depends on the generated geometry.

</details>

<details>
<summary>What is in the printer profile?</summary>

The defaults are CutContour, CreaseLine, Perforation, Bleed and GlueArea, with 1 pt PDF strokes, a five-spot legend and 3 mm bleed. Printer DXF is R2000 with millimetre units and y-up coordinates. Recipient RIP/CAD import is not verified.

</details>

<details>
<summary>How do I run it?</summary>

Use Python 3.10 or newer from a checkout and run the Quickstart commands. Presentation mode writes SVG, DXF and viewer HTML; printer mode writes a separate PDF and DXF.

</details>

<details>
<summary>Does the preview prove the carton will fold and fit?</summary>

No. Continuity is checked at 25%, 50%, 75% and 100% fold progress with a 0.5 mm tolerance. The preview does not prove continuous-time motion, collision avoidance, material behaviour, glue closure or physical fold/fit.

</details>

<details>
<summary>What are the license and browser requirements?</summary>

Original repository work is MIT licensed; third-party references retain their own rights. The static landing page has no analytics, cookies or widgets. The embedded viewer requires JavaScript, WebGL and the pinned Three.js r128 CDN; its 2D dieline remains available when 3D cannot load.

</details>

## Read the contracts

- [Printer profile: spots, bleed, scale and exchange limits](docs/printer-profile.md)
- [Fold preview: extraction, continuity and motion limits](docs/fold-preview.md)
- [CLI choices, parameters and filenames](src/origami_cad/cli.py)

The public display name is DESIGN:OS Origami. Package metadata remains `design-os-origami-cad`. [GitHub](https://github.com/jangtrinh/design-os-origami) · [Website](https://jangtrinh.github.io/design-os-origami/). Publication and remote availability are not verified.
