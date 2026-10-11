---
colors:
  paper: "#FFFFFF"
  ink: "#232327"
  secondary: "#6F6F78"
  hairline: "#A4A4AC"
  canvas: "#F4F4F6"
  viewer-border: "#E0E0E4"
  viewer-line: "#898992"
  viewer-back: "#EEF0F4"
  exported-svg-canvas: "#FFFFFF"
typography:
  fonts:
    - ui-sans-serif
    - system-ui
    - -apple-system
    - Segoe UI
    - sans-serif
    - ui-monospace
    - SFMono-Regular
    - Consolas
    - monospace
  body: 16px
  minimum-body: 14px
  minimum-label: 12px
rounded:
  card: 12px
  inset-card-edge: 11px
  viewer-control: 6px
  viewer-square-thumb: 50%
spacing:
  scale: [4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 96]
---

# Public site design

Authority: accepted product brief and viewer reference tokens, then es-designer
floors. This is a static Persuade surface; the standalone viewer is an Operate
surface. The page inherits the light viewer’s paper, ink and secondary colours;
the brief selects the hairline colour. Exported SVG canvases use white and technical layer colours, with the complete
blank uncropped and no baked title or legend text.

## One blank, multiple outputs

The hero pairs the source-specific proposition “7 blanks. 4 previews.” with two
real images: the full flat source SVG and the actual source-derived 100% fold
capture. Between them, a four-row continuity register displays the real tuck
gate from catalog.json: 25/50/75/100%, 12 shared edges, 0.5mm gap tolerance.
The unavailable three catalogue defaults are part of this tool’s identity. The title and every image have a clear 32px separation at all breakpoints.
The owner explicitly selected separation over the earlier default interlock.
The actual source-generated forms, technical paths and moving hinge panels
provide the subject-specific visual identity. The images remain separate,
uncropped and unmodified. They share the tuck geometry; the catalogue names
its dimensions without implying physical qualification.

The scroll changes composition: source net / measured gate / preview, facts register, sequential
pipeline, catalogue cards, printer sheet and spot register, embedded viewer,
comparison table, semantic FAQ, quickstart and explicit limits. The redundant
large tuck blank and five-image fold strip have been removed; the catalogue
and interactive viewer already expose those artifacts. Catalogue cards are the
only repeated card grid.

Gate interpretation: the seven semantic gallery entries contain real images,
headings and downloads, despite a primitive-shape advisory. Literal-CSS type
inspection omits the resolved 128px clamp heading. Uppercase SVG/PDF/DXF labels
are file-format actions rather than ornamental section kickers. Rendered probes
and actual image/text structure govern these documented advisories.

## Type and interaction

System sans for prose and headings; monospace for commands, paths and measured
dimensions. Body 16px; supporting prose 14px; labels 12px minimum. Display type
uses a 14.25vh desktop scale bounded at 72–128px, with a 44–60px narrow-screen
override. Reading containers are bounded at 58ch, including captions, FAQ rows,
printer copy, card copy and safety lists; rendered line length is measured
separately because the font’s zero glyph is wider than its average character. Heading
tracking never exceeds -0.04em. All link groups, navigation and FAQ summaries
have at least 44px target height. Running-text links retain the inline exception.

Each interactive element has a visible keyboard focus ring and hover/active
feedback. Hover rules run only under `@media (hover: hover)`. FAQ uses native semantic details/summary as explicitly required by the
brief. The landing page has no script file or runtime library; JSON-LD is metadata.
Inline image-error handlers preserve the failed source URL and prefix the
existing alternative text with “Image unavailable”. No replacement artwork is
presented as evidence. The actual
viewer is embedded directly and has a standalone entrypoint.

## Generated demo tokens

The generated demo inherits `viewer_style.py`: border #E0E0E4, line #898992,
back #EEF0F4, 12px card, 11px inset media edge, 6px controls and a 50% radius on
a square 14px slider thumb. These are deliberate source tokens, not overrides
of the landing page’s hairline. No detector rules are ignored.

## Layout and motion

Cards and large media use the brief’s 12px radius; an edge child inset by the
1px card border uses 11px, following the same arc. There is no stacked border and
shadow. No decorative animation or scroll conductor is needed for this static
story. Reduced motion is respected; the viewer owns its motion controls.

The 1024px and 767px layout breakpoints reduce columns and stack the hero copy, navigation,
printer and FAQ layouts. The comparison remains a horizontal table inside a
focusable scroll region with a visible scroll instruction. Code wraps within
its surface. The iframe’s 817px and 480px height breakpoints allow its own
stacked panels and wrapped camera controls to remain visible without nested
vertical scrolling at the measured widths. These source rules are a design intention; viewport and sibling
probes, focus/hover evidence, UI/slop/a11y gates and screenshots establish the
rendered result separately.

Source of content values: [generated catalogue](assets/catalog.json),
[printer profile](printer-profile.md), [fold contract](fold-preview.md), and
[public overview](index.html). Preserve source/copy parity when updating either
the site or the repository README.

The measured four-sample register and dashed seam rules recur through pipeline,
printer spot rows and viewer caption. They use the existing hairline token; bright
technical path colours remain confined to generated CAD output. The redundant
printer raster was removed from the hero and appears once in its printer section.
