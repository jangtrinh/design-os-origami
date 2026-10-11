# Printer exchange profile

The printer profile exports named manufacturing paths as vector spot-colour
PDF and R2000 DXF for printer/die-maker exchange.
Recipient RIP/CAD acceptance, material suitability and physical assembly need
recipient qualification; local tests and renders establish narrower evidence.

Use printer mode when handing off manufacturing paths. For example, request the
recipient's bleed and cut spot name explicitly:

```sh
PYTHONPATH=src python3 -m origami_cad.cli generate \
  --type tuck-box --width 80 --depth 50 --height 120 --thickness 0.5 \
  --profile printer --bleed-mm 5 --spot-cut DieCut --output-dir ./output
```

[CLI `main`](https://github.com/jangtrinh/design-os-origami/blob/main/src/origami_cad/cli.py) owns filenames, supported generators,
parameter defaults and every override; `generate --help` discovers them.
Omitting the profile retains the presentation path. Preserve an earlier delivery
under a separate output directory before regenerating files.

The printer profile uses five unique spot colours, 1 pt PDF vector strokes,
100% scale, and millimetre/y-up DXF. Print or import at 100%; fit-to-page changes
manufacturing dimensions. Default bleed is 3 mm; select the recipient's material
allowance explicitly. The source's inconsistent corrugated inch/mm pairing was
not turned into an automatic rule.

The five default spot names are `CutContour`, `CreaseLine`, `Perforation`,
`Bleed` and `GlueArea`. The PDF includes a five-spot legend below the
bleed-inclusive blank; legend samples use every spot even when a line type has
no manufacturing path in that blank. Printer DXF declares millimetres and uses
y-up coordinates. Presentation DXF remains a separate R12 export with an
unspecified recipient unit/orientation profile and no mountain/valley identity.

[PDF/DXF exporters](https://github.com/jangtrinh/design-os-origami/blob/main/src/origami_cad/printer_profile_export.py) own the API,
spot-name restrictions, PDF page/legend placement and DXF units.
[R2000 database writer](https://github.com/jangtrinh/design-os-origami/blob/main/src/origami_cad/printer_r2000.py) owns handles,
space/layout ownership and table/object structure. Dedicated line-type spots
avoid special all/none or process-colour semantics; explicitly
empty CLI overrides must reach validation rather than silently use defaults.
[Connected paths](https://github.com/jangtrinh/design-os-origami/blob/main/src/origami_cad/printer_paths.py) own the closed CUT contour
requirement and slit handling. [Bleed envelope](https://github.com/jangtrinh/design-os-origami/blob/main/src/origami_cad/printer_bleed.py)
owns the outward construction for one exterior blank; holes/slits are not
separately offset. Wide allowances can close narrow notches. The blank and its
clearance must remain covered: removing crossing loops by area alone failed that
requirement. Arithmetic overflow must be rejected before writing invalid files.

[Executable profile contracts](https://github.com/jangtrinh/design-os-origami/blob/main/tests/test_printer_profile.py) own geometry,
byte structure, scale, compatibility and negative controls. The
[real tuck-box printer PDF](assets/models/tuck-box.pdf) and
[printer DXF](assets/models/tuck-box.dxf) show the generated paths. Return to the
[public overview](index.html#printer). Repository links target the planned public
name; publication and remote availability are not verified.
