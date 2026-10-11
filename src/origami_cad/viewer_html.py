"""Self-contained light viewer of actual dielines and their rigid hinge tree."""
import html
import json
from pathlib import Path

from origami_cad.geometry import OrigamiCreasePattern
from origami_cad.fold_faces import build_fold_model
from origami_cad.viewer_style import VIEWER_STYLE
from origami_cad.viewer_scene import VIEWER_SCENE
from origami_cad.viewer_controls import VIEWER_CONTROLS


def _dieline(cp):
    """Presentation only: preserve original source coordinates and CAD layers."""
    x0, y0, x1, y1 = cp.bounding_box()
    margin = max(x1-x0, y1-y0, 1) * 0.05
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
             f'aria-label="2D dieline" viewBox="{x0-margin:.17g} {y0-margin:.17g} '
             f'{x1-x0+2*margin:.17g} {y1-y0+2*margin:.17g}">']
    colors = {'CUT': '#FF0000', 'CREASE': '#00FF00', 'MOUNTAIN': '#00FF00',
              'VALLEY': '#00FF00', 'PERFORATE': '#0000FF', 'GLUE': '#FF00FF'}
    for crease in cp.creases:
        kind = crease.crease_type.value
        dashed = '' if kind == 'CUT' else ' stroke-dasharray="4 3"'
        if kind in {'CREASE', 'MOUNTAIN', 'VALLEY'}:
            # Display backing makes essential folds legible; CAD color stays on top.
            parts.append(f'<line x1="{crease.p1.x:.17g}" y1="{crease.p1.y:.17g}" '
                         f'x2="{crease.p2.x:.17g}" y2="{crease.p2.y:.17g}" '
                         f'stroke="#6F6F78" stroke-width="2.4" data-presentation="contrast" '
                         f'aria-hidden="true" vector-effect="non-scaling-stroke"{dashed}/>')
        parts.append(f'<line x1="{crease.p1.x:.17g}" y1="{crease.p1.y:.17g}" '
                     f'x2="{crease.p2.x:.17g}" y2="{crease.p2.y:.17g}" '
                     f'stroke="{colors[kind]}" data-fold="{kind.lower()}" '
                     f'vector-effect="non-scaling-stroke"{dashed}/>')
    return '\n'.join(parts + ['</svg>'])


def _script_json(value):
    """JSON raw text cannot terminate its script element or inject HTML."""
    encoded = json.dumps(value, ensure_ascii=True, allow_nan=False)
    for char, replacement in (('<', '\\u003c'), ('>', '\\u003e'), ('&', '\\u0026')):
        encoded = encoded.replace(char, replacement)
    return encoded


def generate_viewer_html(cp: OrigamiCreasePattern, output_path: str) -> str:
    """Write and return HTML; geometry and signed angles come only from the CP."""
    model = build_fold_model(cp)
    name = html.escape(cp.name, quote=True)
    title_name = html.escape(cp.name if len(cp.name) <= 80 else cp.name[:77] + '…', quote=True)
    x0, y0, x1, y1 = cp.bounding_box()
    dimensions = f'Blank {x1-x0:g} × {y1-y0:g} mm · Caliper {cp.thickness_mm:g} mm'
    status = html.escape(model['status'] or 'Loading 3D fold preview…')
    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title_name} · Fold preview</title>
  <style>{VIEWER_STYLE}</style>
</head>
<body>
<main>
  <header><h1>{name}</h1><p class="dimensions">{dimensions}</p></header>
  <div class="panes">
    <section class="pane" aria-labelledby="dieline-title">
      <h2 id="dieline-title">2D dieline</h2>
      <div class="cad-canvas">{_dieline(cp)}</div>
    </section>
    <section class="pane" aria-labelledby="fold-title">
      <h2 id="fold-title">3D fold preview</h2>
      <div id="three-viewport" role="group" aria-label="3D fold preview" aria-busy="true"></div>
    </section>
  </div>
  <div class="controls" aria-label="Fold controls">
    <span id="fold-label">Fold</span>
    <div id="fold-slider" role="slider" tabindex="-1" aria-labelledby="fold-label"
      aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" aria-valuetext="0 percent"
      aria-disabled="true"><span class="slider-track"><span class="slider-fill"></span>
      <span class="slider-thumb"></span></span></div>
    <output id="fold-percent" aria-hidden="true">0%</output>
    <button id="play-btn" type="button" disabled>Play</button>
    <button id="reset-btn" type="button" disabled>Reset</button>
  </div>
  <p id="fold-status" role="status" aria-live="polite">{status}</p>
  <noscript><p>3D fold preview needs JavaScript. The 2D dieline remains available.</p></noscript>
</main>
<script id="fold-model" type="application/json">{_script_json(model)}</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>{VIEWER_SCENE}\n{VIEWER_CONTROLS}</script>
</body>
</html>'''
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page, encoding='utf-8')
    return page
