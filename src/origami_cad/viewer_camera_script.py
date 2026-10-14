"""Source-independent camera navigation; no face or fold geometry mutation."""

VIEWER_CAMERA_SCRIPT = r'''
// Camera-only navigation for the public generated demo.
let viewZoom = 1, yaw = -Math.PI/4, pitch = Math.atan(1.3/Math.sqrt(2));
const viewPan = new THREE.Vector3();
function changeView(action) {
  const step = Math.max(target.radius, 1)*0.12;
  if (action === 'left') yaw -= 0.15;
  if (action === 'right') yaw += 0.15;
  if (action === 'up') pitch = Math.min(1.5, pitch+0.15);
  if (action === 'down') pitch = Math.max(-1.5, pitch-0.15);
  if (action === 'pan-left') viewPan.x -= step;
  if (action === 'pan-right') viewPan.x += step;
  if (action === 'pan-up') viewPan.z += step;
  if (action === 'pan-down') viewPan.z -= step;
  if (action === 'in') viewZoom = Math.min(4, viewZoom*1.15);
  if (action === 'out') viewZoom = Math.max(0.5, viewZoom/1.15);
  if (action === 'reset') {
    yaw = -Math.PI/4; pitch = Math.atan(1.3/Math.sqrt(2)); viewZoom = 1; viewPan.set(0,0,0);
  }
  direction.set(Math.cos(pitch)*Math.cos(yaw), Math.cos(pitch)*Math.sin(yaw), Math.sin(pitch));
  render();
}
document.querySelectorAll('[data-view]').forEach(button => {
  button.disabled = false;
  button.addEventListener('click', () => changeView(button.dataset.view));
});
let drag = null;
renderer.domElement.addEventListener('pointerdown', event => {
  if (event.pointerType !== 'mouse') return;
  drag = {x:event.clientX, y:event.clientY};
  renderer.domElement.setPointerCapture(event.pointerId);
});
renderer.domElement.addEventListener('pointermove', event => {
  if (!drag) return;
  const dx = event.clientX-drag.x, dy = event.clientY-drag.y;
  drag = {x:event.clientX, y:event.clientY};
  if (event.shiftKey) {
    viewPan.x -= dx*target.radius/200; viewPan.z += dy*target.radius/200;
  } else {
    yaw -= dx/150; pitch = Math.max(-1.5, Math.min(1.5, pitch+dy/150));
  }
  changeView('drag');
});
renderer.domElement.addEventListener('pointerup', () => { drag = null; });
renderer.domElement.addEventListener('pointercancel', () => { drag = null; });
renderer.domElement.addEventListener('wheel', event => {
  // Require explicit focus before intercepting page scroll.
  if (document.activeElement !== renderer.domElement) return;
  event.preventDefault(); changeView(event.deltaY < 0 ? 'in' : 'out');
}, {passive:false});
renderer.domElement.tabIndex = 0;
renderer.domElement.setAttribute('aria-label', 'Folded model. Use camera buttons below to rotate, pan or zoom.');

'''
