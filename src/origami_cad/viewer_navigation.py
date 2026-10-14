"""Apply the existing published camera controls to any source-generated viewer."""
from origami_cad.viewer_camera_script import VIEWER_CAMERA_SCRIPT


def with_navigation(page):
    page = page.replace("function render() {", VIEWER_CAMERA_SCRIPT + "\n  function render() {")
    page = page.replace("const aspect = width/height, halfHeight = radius*1.05*Math.max(1, 1/aspect);",
                        "const aspect = width/height, halfHeight = radius*1.05*Math.max(1, 1/aspect)/viewZoom;")
    page = page.replace("camera.position.copy(displayedCenter).addScaledVector(direction, 3*radius);",
                        "const viewCenter = displayedCenter.clone().add(viewPan);\n    camera.position.copy(viewCenter).addScaledVector(direction, 3*radius);")
    page = page.replace("camera.lookAt(displayedCenter);", "camera.lookAt(viewCenter);")
    buttons = ''.join(f'<button type="button" data-view="{action}" disabled>{label}</button>' for action,label in
                      [("left","Rotate left"),("right","Rotate right"),("up","Rotate up"),("down","Rotate down"),
                       ("pan-left","Pan left"),("pan-right","Pan right"),("pan-up","Pan up"),("pan-down","Pan down"),
                       ("in","Zoom in"),("out","Zoom out"),("reset","Reset view")])
    page = page.replace('<p id="fold-status"', '<p class="dimensions">Drag to rotate; Shift-drag to pan; scroll to zoom. Keyboard view buttons are below.</p>'
                        '<nav class="view-controls" aria-label="Camera controls">'+buttons+'</nav><p id="fold-status"')
    style = 'body{font-size:14px}h2,.controls,button{font-size:12px}.dimensions{max-width:60ch}.view-controls{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}.view-controls button{min-height:44px;padding:8px 16px}header>a{display:inline-flex;align-items:center;min-height:44px;color:var(--ink)}header>a:focus-visible,#three-viewport canvas:focus-visible{outline:2px solid var(--ink);outline-offset:3px}#three-viewport canvas{touch-action:pan-y;cursor:grab}'
    page = page.replace('</style>', style+'</style>')
    page = page.replace('<header><h1>', '<header><a href="index.html">Choose another blank</a><h1>')
    page = page.replace('function fail(message) {', "function fail(message) {\n    document.querySelectorAll('[data-view]').forEach(button => { button.disabled = true; });\n    const canvas = viewport.querySelector('canvas');\n    if (canvas) { canvas.tabIndex = -1; canvas.style.pointerEvents = 'none'; }")
    resize = """<script>
if (window.parent !== window) {
  const notify = () => parent.postMessage({type:'origami-viewer-height',height:document.documentElement.scrollHeight}, '*');
  new ResizeObserver(notify).observe(document.body); addEventListener('load',notify);
}
</script>"""
    return '\n'.join(line.rstrip() for line in page.replace('</body>', resize+'</body>').splitlines())+'\n'
