"""Reference tokens and restrained responsive viewer presentation."""

VIEWER_STYLE = r'''
:root {
  --paper: #FFFFFF; --ink: #232327; --secondary: #6F6F78;
  --surface: #F4F4F6; --border: #E0E0E4; --line: #898992;
  --back: #EEF0F4; font-size: 16px;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--paper); color: var(--ink);
  font: 13px/1.5 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 1120px; margin: 0 auto; padding: 32px 20px 60px; }
header { margin-bottom: 24px; }
h1 { margin: 0 0 8px; font-size: 20px; font-weight: 600; line-height: 1.3;
  overflow-wrap: anywhere; }
.dimensions { margin: 0; color: var(--secondary); }
.panes { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 20px; }
.pane { min-width: 0; border: 1px solid var(--border); border-radius: 12px;
  overflow: hidden; background: var(--paper); }
h2 { margin: 0; padding: 12px 16px; font: 600 11px/1.5 ui-monospace, monospace;
  border-radius: 11px 11px 0 0; }
.cad-canvas, #three-viewport { width: 100%; aspect-ratio: 1 / 1; min-width: 0; }
.cad-canvas, #three-viewport { border-radius: 0 0 11px 11px; overflow: hidden; }
.cad-canvas { padding: 16px; display: flex; align-items: center; justify-content: center; }
.cad-canvas svg { width: 100%; height: 100%; fill: none; stroke-width: 0.9; }
#three-viewport canvas { display: block; width: 100%; height: 100%; border-radius: inherit; }
.controls { display: flex; align-items: center; gap: 12px; margin-top: 20px;
  font: 11px/1.5 ui-monospace, monospace; }
#fold-slider { --progress: 0%; flex: 1; min-width: 44px; height: 44px;
  display: flex; align-items: center; cursor: pointer; touch-action: none;
  padding: 0 8px; border-radius: 6px; }
.slider-track { display: block; position: relative; height: 1px; width: 100%;
  background: var(--line); }
.slider-fill { display: block; height: 1px; width: var(--progress); background: var(--ink); }
.slider-thumb { position: absolute; left: var(--progress); top: 0; width: 14px; height: 14px;
  border-radius: 50%; border: 1px solid var(--ink); background: var(--paper);
  transform: translate(-50%, -50%); }
#fold-percent { min-width: 4ch; text-align: right; font-variant-numeric: tabular-nums; }
button { min-height: 44px; min-width: 44px; padding: 6px 12px; border-radius: 6px;
  border: 1px solid var(--border); background: var(--surface); color: var(--ink);
  font: 11px/1.5 ui-monospace, monospace; cursor: pointer; }
button:active:enabled, button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
button:disabled { color: var(--secondary); cursor: default; }
#fold-slider[aria-disabled="true"] { opacity: 0.6; cursor: default; }
@media (hover: hover) {
  button:hover:enabled { background: var(--back); border-color: var(--line); }
  #fold-slider:hover:not([aria-disabled="true"]) .slider-thumb { background: var(--surface); }
}
button:focus-visible, #fold-slider:focus-visible { outline: 2px solid var(--ink); outline-offset: 3px; }
#fold-status { margin: 12px 0 0; color: var(--secondary); }
#fold-status:empty { display: none; }
::selection { background: var(--ink); color: var(--paper); }
@media (max-width: 767px) {
  .panes { grid-template-columns: minmax(0, 1fr); }
  .controls { gap: 8px; }
}
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto; } }
'''
