# Dieline-derived fold preview

The standalone HTML viewer uses the actual CUT and fold segments of a generated crease pattern. Extraction copies the source, validates raw segments, splits intersections, and walks the planar graph. Bounded material faces retain die-cut holes; their area totals match the blank. Declared cut slits separate material but never act as hinges. Stored approximate facets do not supply the mesh.

The largest material face stays in its original coordinate frame. A fold-adjacent spanning tree rotates each child subtree around its source hinge in its parent frame. Before exposing this motion, the preview checks both endpoint copies of every non-tree fold and every shared uncut face boundary at 25%, 50%, 75% and 100%; the maximum permitted separation is 0.5 mm. Tree hinges are also checked, and declared CUT slits are excluded because they separate material. Shared boundaries are reconstructed from face geometry, so missing non-tree metadata cannot remove the continuity obligation.

All seven packaging generators are covered by default and parameter-variant tests. The default crash-lock, zero-glue tray and diamond candidates fail continuity and preserve their 2D drawing with `3D fold preview not available: this pattern needs coordinated or non-rigid folding`. Their public model has no renderable faces or hinges, and its diagnostic continuity report records the failure. Qualification depends on actual geometry and motion. Miura and deer patterns, or failed extraction, retain the original generic unavailable status. Passing models keep non-tree folds in the serialized data without animating them as additional constraints.

Original dieline coordinates are millimetres in XY, with z=0 at 0% progress. +Z is the printed/front side, and -Z is the unprinted inside. Hinge axes follow the parent boundary with its interior on the left. Generic CREASE and VALLEY use positive right-hand rotation toward the inside; MOUNTAIN uses the opposite sign. Source target-angle magnitude is preserved; crease type supplies direction, including historical negative VALLEY targets. At 100%, each tree hinge has reached its own target magnitude.

The tuck and gable bodies close into rectangular cross-sections within the specified 0.5 mm tolerance in default and variant tests. Sampled seam continuity does not prove continuous-time or global physical foldability. Rigid face intersections, glue joins, material thickness, bending mechanics, grain and physical assembly need separate evidence. This is a qualified spanning-tree visualization, with no collision solver or manufacturing qualification.

The viewer has a light two-pane layout, stacked below 768px, and keyboard/pointer fold controls with explicit Play/Pause and Reset. Reduced motion keeps manual slider operation and disables playback. The camera fits the current folded-state bounding sphere, easing center and inward zoom over 180 ms. Immediate safety expansion encloses the current geometry during playback and large manual jumps; reduced motion settles immediately. There is no idle orbit. At 100%, measured tuck/gable bounding rectangles exceed 50% of the 3D pane. The browser tab abbreviates unusually long names; the page heading keeps the complete source name.

Three.js is the sole external JavaScript dependency, pinned to the existing cdnjs r128 URL. JavaScript, CDN or WebGL failure preserves the 2D dieline and an honest status. No runtime fetch sends the crease-pattern data to a service.

Inspect the [standalone tuck-box viewer](demo/tuck-box.html), the
[generated catalogue](assets/catalog.json) and the [public overview](index.html#preview).
The catalogue records each example’s sampled continuity result. Local checks do
not establish assistive-technology, physical-sample, recipient or owner acceptance.
The preview implementation is in
[`viewer_html.py`](https://github.com/jangtrinh/design-os-origami/blob/main/src/origami_cad/viewer_html.py).
Repository links target the planned public name; publication and remote
availability are not verified.
