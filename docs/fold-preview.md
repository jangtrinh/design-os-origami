# Dieline-derived fold preview

The standalone HTML viewer uses the actual CUT and fold segments of a generated crease pattern. Extraction copies the source, validates raw segments, splits intersections, and walks the planar graph. Bounded material faces retain die-cut holes; their area totals match the blank. Declared cut slits separate material but never act as hinges. Stored approximate facets do not supply the mesh.

The largest material face stays in its original coordinate frame. A fold-adjacent spanning tree rotates each child subtree around its source hinge in its parent frame. Before exposing this motion, the preview checks both endpoint copies of every non-tree fold and every shared uncut face boundary at 25%, 50%, 75% and 100%; the maximum permitted separation is 0.5 mm. Tree hinges are also checked, and declared CUT slits are excluded because they separate material. Shared boundaries are reconstructed from face geometry, so missing non-tree metadata cannot remove the continuity obligation.

The product registry exposes eleven carton products as twelve separately exported blanks.
The original four-sample source schedule remains the baseline gate. When that schedule
fails, the public preview tries coordinated motion with at least 101 samples including
0%, 50% and 100%, the same 0.5 mm seam tolerance, source endpoint targets (except
geometrically proven rigid-cluster locks) and a full free-edge loop through the root body.
Sparse sampling cannot bypass this qualification; partial wall/flap/glue motion is rejected.

The default crash-lock, zero-glue tray and diamond-faceted box sources qualify with
rigidly joined diagonal or gusset faces kept flat (`locked-seams`). This is a
source-derived tube/closure preview, not verification of automatic locking, collision
avoidance or physical assembly. Qualification uses source geometry, not a product-name
whitelist. Miura/deer and failed extraction keep the generic unavailable state.

Original dieline coordinates are millimetres in XY, with z=0 at 0% progress. +Z is the printed/front side, and -Z is the unprinted inside. Hinge axes follow the parent boundary with its interior on the left. Generic CREASE and VALLEY use positive right-hand rotation toward the inside; MOUNTAIN uses the opposite sign. Source target-angle magnitude is preserved; crease type supplies direction, including historical negative VALLEY targets. At 100%, each active tree hinge reaches its source target; proven rigid-cluster hinges remain at zero in coordinated previews.

The tuck and gable bodies close into rectangular cross-sections within the specified 0.5 mm tolerance in default and variant tests. Sampled seam continuity does not prove continuous-time or global physical foldability. Rigid face intersections, glue joins, material thickness, bending mechanics, grain and physical assembly need separate evidence. This is a qualified spanning-tree visualization, with no collision solver or manufacturing qualification.

The viewer has a light two-pane layout, stacked below 768px, and keyboard/pointer fold controls with explicit Play/Pause and Reset. Reduced motion keeps manual slider operation and disables playback. The camera fits the current folded-state bounding sphere, easing center and inward zoom over 180 ms. Immediate safety expansion encloses the current geometry during playback and large manual jumps; reduced motion settles immediately. There is no idle orbit. At 100%, measured tuck/gable bounding rectangles exceed 50% of the 3D pane. The browser tab abbreviates unusually long names; the page heading keeps the complete source name.

Three.js is the sole external JavaScript dependency, pinned to the existing cdnjs r128 URL. JavaScript, CDN or WebGL failure preserves the 2D dieline and an honest status. No runtime fetch sends the crease-pattern data to a service.

Inspect the [model switcher](demo/index.html), the
[generated catalogue](assets/catalog.json) and the [public overview](index.html#preview).
The catalogue records each example’s sampled continuity result. Local checks do
not establish assistive-technology, physical-sample, recipient or owner acceptance.

Recorded model parity uses [the diagnostic comparison policy](../src/origami_cad/preview_recording.py).
Saved diagnostics retain their original precision. Comparison permits an absolute
0.000001 mm difference in reported gaps/displacements: the decimal precision below
one hundred-thousandth of the 0.5 mm seam tolerance, or 1/500000 of that gate.
Reported solver angles permit 0.000001 degrees; rendered hinge angles stay exact.
Availability, every validity flag, thresholds, sample schedules, topology and
source coordinates remain exact. A diagnostic difference cannot cross the seam,
zero-motion or endpoint-deviation threshold. Derived face areas permit only 16
floating-point ULPs, rather than the diagnostic tolerance.

Representative worst-seam identity and nearest-contact/loop witness selection
can change among numerical ties. Their identity/path is excluded from recorded
parity; saved raw witnesses remain available for inspection. Measurements, source
edges, contact flags and gate decisions still compare. This comparison neither
qualifies motion nor changes the full-precision source gates. It does not prove
physical closure or witness equivalence beyond the compared diagnostics.

Before permitting a tied identity, the saved witness is verified against source
geometry: a sampled shared-seam endpoint with the reported gap; an actual new
free CUT edge contacting the referenced face with the same full/adjacent flags;
or its real hinge-tree path closing through the root. Fabricated face IDs,
endpoints, sample positions and loop paths fail. Unavailable previews use the
source extraction solely to verify their recorded rejected-candidate witnesses;
this never makes the preview available.
The preview implementation is in
[`viewer_html.py`](https://github.com/jangtrinh/design-os-origami/blob/main/src/origami_cad/viewer_html.py).
Repository links target the planned public name; publication and remote
availability are not verified.
