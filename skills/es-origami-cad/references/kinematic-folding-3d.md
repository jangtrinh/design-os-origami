# 3D Kinematic Folding Simulation & WebGL Rendering

Mathematical formulation and Three.js implementation guidelines for real-time origami folding simulation.

Draft guidance: the equations and example architecture below are not evidence
that the repository viewer solves a generated net. The viewer is illustrative;
rigid closure, collision detection, and physical assembly remain unqualified.

## 1. Rodrigues' Rotation Formula around Hinge Vectors

Given two rigid facets $F_A$ and $F_B$ joined along a crease line with unit axis $\hat{\mathbf{u}} = \frac{\mathbf{p}_2 - \mathbf{p}_1}{\|\mathbf{p}_2 - \mathbf{p}_1\|}$:

For any vertex $\mathbf{v} \in F_B$, rotating by fold angle $\rho$ around hinge passing through $\mathbf{p}_1$:
$$\mathbf{v}' = \mathbf{p}_1 + (\mathbf{v} - \mathbf{p}_1) \cos \rho + (\hat{\mathbf{u}} \times (\mathbf{v} - \mathbf{p}_1)) \sin \rho + \hat{\mathbf{u}} (\hat{\mathbf{u}} \cdot (\mathbf{v} - \mathbf{p}_1)) (1 - \cos \rho)$$

In matrix form:
$$\mathbf{R}(\hat{\mathbf{u}}, \rho) = \mathbf{I} + (\sin \rho) \mathbf{K} + (1 - \cos \rho) \mathbf{K}^2$$
where $\mathbf{K}$ is the skew-symmetric cross-product matrix:
$$\mathbf{K} = \begin{bmatrix} 0 & -u_z & u_y \\ u_z & 0 & -u_x \\ -u_y & u_x & 0 \end{bmatrix}$$

---

## 2. Dual-Graph Kinematic Tree

To avoid cyclic dependency errors:
1. **Choose Base Panel**: Select the primary ground panel (e.g., `FrontPanel` or `BaseHexagon`) anchored at $Z = 0$.
2. **Build Spanning Tree**: Construct a directed tree where each node is a facet and each edge is a revolute joint.
3. **Compound Transformations**:
   $$\mathbf{T}_{\text{child}} = \mathbf{T}_{\text{parent}} \cdot \mathbf{T}_{\text{hinge}}(\rho)$$

---

## 3. Three.js Dual-Pane Architecture

An illustrative packaging interface can use a synchronized dual-pane layout:
- **Left Pane (2D CAD Canvas)**: Raw SVG dieline displaying laser die CUT (Red), CREASE (Green dashed), and GLUE (Magenta) lines.
- **Right Pane (3D WebGL Viewport)**: Three.js scene containing `THREE.Group` hierarchical joints driven by a fold progress variable $\tau \in [0, 1]$.

### Hinge Group Construction Pattern
```javascript
// Anchor group
const baseMesh = createPanelMesh(w, h);
scene.add(baseMesh);

// Hinge joint attached to edge of base panel
const hingeGroup = new THREE.Group();
hingeGroup.position.set(-w / 2, 0, 0); // Position on fold line
baseMesh.add(hingeGroup);

// Child panel attached to hinge
const childMesh = createPanelMesh(d, h);
childMesh.position.set(-d / 2, 0, 0);
hingeGroup.add(childMesh);

// Animate fold:
function updateFold(angleDeg) {
  hingeGroup.rotation.y = THREE.MathUtils.degToRad(angleDeg);
}
```

---

## 4. Failure Modes & Anti-Patterns

1. **Inverted Hinge Vector**: If the direction vector $\hat{\mathbf{u}}$ is reversed ($\mathbf{p}_1 \to \mathbf{p}_2$ vs $\mathbf{p}_2 \to \mathbf{p}_1$), positive rotation produces an outward fold instead of an inward fold, turning the carton inside-out.
2. **Unanchored Floating Mesh**: Failing to anchor one face as the stationary world base causes the entire 3D model to rotate and drift unpredictably during fold animation.
3. **Double-Sided Face Z-Fighting**: Placing inner and outer liner meshes at identical coordinates $Z = 0$ results in severe visual flicker; offset overlapping panels by caliper $t$ along the facet normal.
