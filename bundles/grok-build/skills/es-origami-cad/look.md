# Fixed visual inspection

Run [look.py](look.py) only after [validate.py](validate.py). Supply a prepared
user cache; the harness never installs or downloads dependencies. It reuses the
product's public capture path and the actual generated viewer HTML.

Fixed sheet: full SVG blank, then 25%, 50%, 75%, 100% fold-progress shots at a
1440px desktop viewport. Each shot labels the model, progress and availability.
Responsive checks: SKIPPED (owner default). Do not claim physical simulation.

| Item | Check | Home |
| --- | --- | --- |
| L1 | Complete blank visible, line types distinguishable | Human eyes |
| L2 | Material, seams, overlap, clipping and labels intelligible | Human eyes |
| L3 | Displayed family matches requested concept | Receipt + human eyes |
| L4 | Slider reaches all fixed requested percentages | DOM assertion |
| L5 | Source model is unchanged during controls | Parsed model/hash assertion |
| L6 | Qualified preview has present, nonblank canvas | Browser measurement |
| L7 | Sampled continuity matches source data | Product geometry checks |
| L8 | No unexpected console/resource failure or external request | Browser assertions |
| L9 | Unavailable preview retains 2D SVG and honest status | Browser assertion |

Right: open the saved sheet and inspect L1–L3, alongside measured L4–L9 output.
Wrong: call a zero exit “looks good”, or treat a visible rectangle as nonblank 3D.

| Symptom | Action | When NOT to use a shortcut |
| --- | --- | --- |
| Machine item fails | Preserve failure receipt; regenerate or repair its cause | Never waive it with a model judgment |
| Preview unavailable | Check 2D/status and report unavailable | Never invent a substitute mesh |
| Fine details unreadable | Inspect original captures/zoom | Never grade tiny sheet thumbnails alone |
| Missing cache/browser | Return cannot-run (2), record NOT RUN | Never install during look |

Only the exact pinned Three.js r128 CDN request is served from the
checksum-verified cache during capture. All other external requests are rejected.
The receipt records dependency hashes and interception. The generated viewer
itself retains its CDN URL; local capture does not establish network portability.

## Without a browser

Use exactly:

```text
LOOK: NOT RUN — browser runtime or pinned cache is unavailable.
PHYSICAL_FOLD_FIT: NOT VERIFIED.
RECIPIENT_IMPORT: NOT VERIFIED.
```

A missing look runtime does not satisfy the visual gate. Do not substitute unit
tests, textual self-report, an old screenshot or an unrelated build's capture.
