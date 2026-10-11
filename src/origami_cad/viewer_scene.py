"""Inline Three r128 renderer; source XY geometry and parent-relative hinges."""

VIEWER_SCENE = r'''
function createFoldScene(model, viewport) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#FFFFFF');
  const camera = new THREE.OrthographicCamera();
  camera.up.set(0, 0, 1);
  const renderer = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.domElement.setAttribute('role', 'img');
  renderer.domElement.setAttribute('aria-label', 'Dieline-derived rigid fold preview');
  viewport.appendChild(renderer.domElement);
  const meshes = new Map();
  const front = new THREE.MeshBasicMaterial({color: '#F4F4F6', side: THREE.FrontSide});
  const back = new THREE.MeshBasicMaterial({color: '#EEF0F4', side: THREE.BackSide});
  const line = new THREE.LineBasicMaterial({color: '#898992'});
  const points = ring => ring.map(p => new THREE.Vector2(p[0], p[1]));
  for (const face of model.faces) {
    const shape = new THREE.Shape(points(face.vertices));
    for (const hole of face.holes || []) shape.holes.push(new THREE.Path(points(hole)));
    const geometry = new THREE.ShapeGeometry(shape);
    const group = new THREE.Group();
    group.matrixAutoUpdate = false;
    group.add(new THREE.Mesh(geometry, front), new THREE.Mesh(geometry, back));
    // Ring outlines retain holes and avoid exposing triangulation diagonals.
    for (const ring of [face.vertices, ...(face.holes || [])]) {
      const vertices = [...ring, ring[0]].map(p => new THREE.Vector3(p[0], p[1], 0));
      group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(vertices), line));
    }
    meshes.set(face.id, group);
    scene.add(group);
  }
  function matrices(t) {
    const result = new Map([[model.root, new THREE.Matrix4()]]);
    for (const hinge of model.hinges) {
      const a = hinge.axis[0], b = hinge.axis[1];
      const axis = new THREE.Vector3(b[0]-a[0], b[1]-a[1], 0).normalize();
      const rotation = new THREE.Matrix4().makeTranslation(a[0], a[1], 0)
        .multiply(new THREE.Matrix4().makeRotationAxis(axis, t*hinge.angle_deg*Math.PI/180))
        .multiply(new THREE.Matrix4().makeTranslation(-a[0], -a[1], 0));
      result.set(hinge.child, result.get(hinge.parent).clone().multiply(rotation));
    }
    return result;
  }
  const bounds = new THREE.Box3();
  const target = new THREE.Sphere(), displayedCenter = new THREE.Vector3();
  const startCenter = new THREE.Vector3(), direction = new THREE.Vector3(1, -1, 1.3).normalize();
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let displayedRadius = 0, startRadius = 0, startedAt = 0, frame = null;
  function render() {
    const width = Math.max(1, viewport.clientWidth), height = Math.max(1, viewport.clientHeight);
    // The current sphere plus center offset encloses every vertex even during
    // easing or a large slider jump. Safety expansion is immediate; zoom-in eases.
    const radius = Math.max(displayedRadius, target.radius + target.center.distanceTo(displayedCenter), 1e-7);
    const aspect = width/height, halfHeight = radius*1.05*Math.max(1, 1/aspect);
    camera.position.copy(displayedCenter).addScaledVector(direction, 3*radius);
    camera.near = radius/1000; camera.far = 6*radius;
    camera.lookAt(displayedCenter); camera.updateMatrixWorld(true);
    camera.left = -halfHeight*aspect; camera.right = halfHeight*aspect;
    camera.top = halfHeight; camera.bottom = -halfHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height, false);
    renderer.render(scene, camera);
  }
  function settleCamera() {
    if (frame !== null) cancelAnimationFrame(frame);
    frame = null; displayedCenter.copy(target.center); displayedRadius = target.radius;
    render();
  }
  function easeCamera(now) {
    frame = null;
    const progress = Math.min(1, Math.max(0, (now-startedAt)/180));
    const eased = 1-Math.pow(1-progress, 3);
    displayedCenter.lerpVectors(startCenter, target.center, eased);
    displayedRadius = startRadius+(target.radius-startRadius)*eased;
    render();
    if (progress < 1) frame = requestAnimationFrame(easeCamera);
  }
  function setFold(t) {
    const transforms = matrices(t);
    for (const [id, matrix] of transforms) meshes.get(id).matrix.copy(matrix);
    bounds.makeEmpty();
    for (const face of model.faces) {
      for (const ring of [face.vertices, ...(face.holes || [])]) for (const p of ring)
        bounds.expandByPoint(new THREE.Vector3(p[0], p[1], 0).applyMatrix4(transforms.get(face.id)));
    }
    bounds.getBoundingSphere(target);
    if (!displayedRadius || motion.matches) { settleCamera(); return; }
    startCenter.copy(displayedCenter); startRadius = displayedRadius; startedAt = performance.now();
    render();
    if (frame === null) frame = requestAnimationFrame(easeCamera);
  }
  function motionState() { if (motion.matches) settleCamera(); }
  motion.addEventListener('change', motionState);
  setFold(0);
  const observer = new ResizeObserver(render);
  observer.observe(viewport);
  return {setFold, matrices, renderer, bounds, stop: () => {
    observer.disconnect(); if (frame !== null) cancelAnimationFrame(frame);
    motion.removeEventListener('change', motionState);
  }};
}
'''
