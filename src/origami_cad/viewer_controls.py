"""Accessible fold progress, explicit playback and fail-closed runtime states."""

VIEWER_CONTROLS = r'''
(() => {
  const model = JSON.parse(document.getElementById('fold-model').textContent);
  const viewport = document.getElementById('three-viewport');
  const slider = document.getElementById('fold-slider');
  const percent = document.getElementById('fold-percent');
  const play = document.getElementById('play-btn');
  const reset = document.getElementById('reset-btn');
  const status = document.getElementById('fold-status');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let scene, value = 0, playing = false, frame = null, previous = null, failed = false;
  function pause() {
    playing = false; previous = null;
    if (frame !== null) cancelAnimationFrame(frame);
    frame = null; play.textContent = 'Play'; play.setAttribute('aria-pressed', 'false');
  }
  function fail(message) {
    failed = true;
    if (scene) scene.stop();
    pause(); slider.setAttribute('aria-disabled', 'true'); slider.tabIndex = -1;
    play.disabled = true; reset.disabled = true;
    viewport.setAttribute('aria-busy', 'false');
    status.setAttribute('aria-live', 'assertive'); status.textContent = message;
  }
  function setValue(next) {
    if (slider.getAttribute('aria-disabled') === 'true') return;
    value = Math.max(0, Math.min(100, next));
    slider.style.setProperty('--progress', `${value}%`);
    slider.setAttribute('aria-valuenow', String(Math.round(value)));
    slider.setAttribute('aria-valuetext', `${Math.round(value)} percent`);
    percent.textContent = `${Math.round(value)}%`;
    try { scene.setFold(value/100); }
    catch (error) { fail('3D fold preview failed. Reload to retry; the 2D dieline remains available.'); }
  }
  if (!model.available) { fail(model.status); return; }
  if (typeof THREE === 'undefined') {
    fail('3D library could not load. Check your connection and reload; the 2D dieline remains available.');
    return;
  }
  try { scene = createFoldScene(model, viewport); }
  catch (error) {
    viewport.replaceChildren();
    fail('WebGL fold preview unavailable. Enable WebGL and reload; the 2D dieline remains available.');
    return;
  }
  slider.setAttribute('aria-disabled', 'false'); slider.tabIndex = 0;
  reset.disabled = false; viewport.setAttribute('aria-busy', 'false');
  function motionState() {
    if (failed) return;
    if (motion.matches) pause();
    play.disabled = motion.matches;
    status.textContent = motion.matches ? 'Reduced motion: use the fold slider.' : '';
  }
  motion.addEventListener('change', motionState); motionState();
  scene.renderer.domElement.addEventListener('webglcontextlost', event => {
    event.preventDefault();
    fail('WebGL connection lost. Reload to retry; the 2D dieline remains available.');
  });
  slider.addEventListener('keydown', event => {
    const values = {ArrowLeft: value-1, ArrowDown: value-1, ArrowRight: value+1,
      ArrowUp: value+1, Home: 0, End: 100};
    if (Object.prototype.hasOwnProperty.call(values, event.key)) {
      event.preventDefault(); pause(); setValue(values[event.key]);
    }
  });
  function pointerValue(event) {
    const track = slider.querySelector('.slider-track').getBoundingClientRect();
    setValue((event.clientX-track.left)/track.width*100);
  }
  slider.addEventListener('pointerdown', event => {
    if (slider.getAttribute('aria-disabled') === 'true' || event.button !== 0) return;
    event.preventDefault(); pause(); slider.focus();
    slider.setPointerCapture(event.pointerId); pointerValue(event);
  });
  slider.addEventListener('pointermove', event => {
    if (slider.hasPointerCapture(event.pointerId)) pointerValue(event);
  });
  slider.addEventListener('pointerup', event => {
    if (slider.hasPointerCapture(event.pointerId)) slider.releasePointerCapture(event.pointerId);
  });
  function tick(timestamp) {
    frame = null;
    if (!playing || motion.matches) { pause(); return; }
    if (previous !== null) setValue(value+(timestamp-previous)/60);
    previous = timestamp;
    if (value >= 100) pause();
    if (playing) frame = requestAnimationFrame(tick);
  }
  play.addEventListener('click', () => {
    if (playing) { pause(); return; }
    if (motion.matches || play.disabled) return;
    if (value >= 100) setValue(0);
    playing = true; previous = null;
    play.textContent = 'Pause'; play.setAttribute('aria-pressed', 'true');
    frame = requestAnimationFrame(tick);
  });
  reset.addEventListener('click', () => { pause(); setValue(0); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
  window.addEventListener('pagehide', pause);
})();
'''
