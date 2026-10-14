# Two-piece sleeve/tray and hinged-lid food box

Two generators add three blanks built from one shared four-wall tray helper.
Inside dimensions in mm; every blank is a single closed CUT contour with
declared slits, formula score allowances, and a tree of hinges that the
existing rigid fold model qualifies without any fold-machinery change.

## API and blank names

```py
from origami_cad.packaging_sleeve_tray import generate_sleeve_tray
from origami_cad.packaging_food_box import generate_food_box

sleeve, tray = generate_sleeve_tray(width=120, depth=80, height=35, thickness=0.5)
box = generate_food_box(width=160, depth=120, height=70, thickness=0.5)
```

| Generator | Returns | `cp.name` (defaults) | Faces | Hinges |
|---|---|---|---|---|
| `generate_sleeve_tray` | `tuple[CP, CP]` | `TwoPieceSleeve_120x80x35`, `TwoPieceTray_120x80x35` | 5, 9 | 4, 8 |
| `generate_food_box` | `CP` | `FoodBoxHingedLid_160x120x70` | 13 | 12 |

Two-blank representation: **one crease pattern per blank, one file per blank**.
The product function returns the two blanks as a tuple with distinct names;
the caller writes `<name>.svg`, `<name>_printer.pdf` and so on per blank, so
nothing in the exporters or the fold model has to learn about multi-blank
sheets. A one-sheet nesting layout is not provided.

Optional keyword arguments: `fit_clearance` (default 1.0 mm per side, sleeve
and lid flaps) and, for the sleeve, `glue_flap_width` (15 mm). Non-finite or
non-positive sizes, negative caliper or clearance, and sizes that leave no
room for corner tabs or the lid inset raise `ValueError`. `glue_flap_width` must
not exceed the receiving sleeve side span `height + t + 2·fit + c`; short sleeves
need an explicitly smaller flap, e.g. height 5 mm with glue_flap_width 5 mm.

## Sleeve

Wrapping band Top / Side / Bottom / Side with a tapered glue flap and a
`SleeveGlue` annotation. Panel spans are the tray's **outside** cross section
plus clearance and the 90 degree score allowance:
`panel_w = width + 2t + 2·fit + c`, `panel_h = height + t + 2·fit + c`,
band length `depth + 2t`. A V thumb notch (`ThumbNotch`, ≤ 30 × 12 mm) in the
top panel's leading edge lets the tray be pushed out.

## Tray (shared helper `packaging_rectangular_blank.py`)

Floor `width + c` by `depth + c` at the origin, four walls of `height`, and
four corner glue tabs hinged on the end (left/right) walls that fold inside the
back/front walls. Tab width `min(height − (1 mm + t), floor_w/2 − t)` keeps the
two tabs on one long wall from overlapping and keeps each tab below the wall
top; the far corner is chamfered. Each tab is separated from the long wall by a
declared `TabSlit_*` running from the outline to the floor corner hinge.

## Food box

The tray above plus a lid hinged on the back wall's top edge (`LidHinge`),
inset by `t + fit` per side so its side flaps (`LidFlapHinge_Left/Right`,
depth `min(0.6·height, 25)`) hang inside the end walls, and a chamfered front
tuck (`TuckHinge`) that folds inside the front wall. The back wall's top-edge
stubs under the flaps are declared `LidFlapSlit_*`. Lid depth equals the floor
depth `depth + c` (same zero-thickness convention as the tuck box lid).

## Verification and limits

`tests/test_two_piece_food_styles.py` and `tests/test_two_piece_food_fold.py` run the independent topology gate,
printer PDF/DXF export, bleed offsets at 0/3/8/20 mm, fold availability with
face counts, and folded-state checks at 100 % (tabs in the long-wall planes,
lid at wall-top height, tuck in the front-wall plane, flaps inside the end
walls) for defaults, asymmetric and extreme variants, and caliper 0.

Known limits, stated rather than hidden:

- Fold passing means tree continuity, not collision or thickness simulation.
- The outward bleed envelope splits collinear overlapping edge strips. Narrow thumb
  notches may close in the outward union when the bleed is larger than the notch;
  the regression test checks a simple closed contour and the requested clearance,
  including the 9 mm sleeve with 20 mm bleed. Ambiguous or open graphs still raise.
- Source references do not specify these sleeve-fit, tab or lid-flap dimensions; clearance 1 mm, tab relief
  1 mm + t, and flap depth `min(0.6·height, 25)` are design choices exposed or
  documented here, not cited standards.
- CLI `--type sleeve-tray` writes one file per named sleeve/tray blank.
  CLI `--type food-box` writes the hinged food-box blank; both support the printer profile.
