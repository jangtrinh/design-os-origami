# Packaging Paperboard Thickness & Score Mechanics

Engineering rules for calculating bend allowances, score deductions, grain orientation, and laser die-board layer standards.

Draft guidance: material ranges, K factors, grain rules, relief clearances, and
tooling numbers below lack supporting measured source evidence. The formulas
are retained for review; the pi-based expression and approximate 0.5t rule are
not equivalent to the code's default 0.45t allowance. Do not use these values as
a production recipe. Layer colors are local display conventions; recipient
spot inks, stroke widths, tools, and import requirements need owner decisions.

## 1. Neutral Axis & Score Allowance Formula

When paperboard of caliper (thickness) $t$ is creased and folded to angle $\alpha$, the inner surface undergoes compression while the outer surface undergoes tension. The neutral line sits at distance $K \cdot t$ from the inner face.

### Bending Formula
$$\Delta L = \frac{\alpha}{180^\circ} \cdot \pi \cdot (R + K \cdot t)$$
For sharp $90^\circ$ die creases where inside bend radius $R \approx 0$ and $K \approx 0.40 - 0.45$:
$$\Delta L_{90^\circ} \approx \frac{1}{2} t = 0.50 \cdot t$$

For $180^\circ$ rollover folds (double-wall trays, dust flaps, glue tabs):
$$\Delta L_{180^\circ} \approx 1.0 \cdot t \text{ to } 1.5 \cdot t$$

---

## 2. Decision Matrix: Paperboard Selection by Application

| Board Grade | Grammage ($\text{g/m}^2$) | Caliper ($t$) | Bending Stiffness | Best Suited For |
| :--- | :--- | :--- | :--- | :--- |
| **SBS (Solid Bleached Sulfate)** | $250 - 450$ | $0.35 - 0.60\text{ mm}$ | High | Luxury cosmetics, pharmaceuticals, perfume |
| **FBB (Folding Boxboard)** | $200 - 400$ | $0.40 - 0.75\text{ mm}$ | Very High | Confectionery, dry foods, retail consumer goods |
| **Micro-flute (F/N Flute)** | $300 - 500$ | $0.75 - 1.00\text{ mm}$ | High rigidity | Small electronics, premium e-commerce |
| **E-Flute Corrugated** | $350 - 600$ | $1.20 - 1.60\text{ mm}$ | Impact resistant | Mailer boxes (FEFCO 0427), subscription boxes |
| **B-Flute Corrugated** | $450 - 800$ | $2.80 - 3.20\text{ mm}$ | Heavy duty | Master shippers (FEFCO 0201), industrial freight |

---

## 3. CNC Laser Die-Board Layer Standard

Packaging prepress requires absolute color and layer separation for automated sample plotters (Zünd, Kongsberg, ESKO):

| Layer Name | Stroke Color | Hex Code | Dash Pattern | Tool Type |
| :--- | :--- | :--- | :--- | :--- |
| **CUT** | Red | `#FF0000` / `#FF3344` | Solid | 2pt / 3pt Cutting Knife Rule |
| **CREASE** | Green | `#00FF00` / `#00E676` | Dashed (`4, 3`) | Creasing Rule + Phenolic Matrix |
| **PERFORATE** | Blue | `#0000FF` / `#2979FF` | Dotted (`2, 2`) | Perf Rule (e.g. 3mm cut / 3mm skip) |
| **GLUE** | Magenta | `#FF00FF` / `#E040FB` | Hatch / Solid | PVA or Hot-Melt Adhesive Area |
| **DIMENSION** | Grey | `#7F7F7F` | Thin Solid | Technical Annotation (Not Cut) |

---

## 4. Grain Direction Invariant

Paper fibers align predominantly in the machine direction (MD):
- **Rule**: Main body score lines MUST run parallel to the grain direction to minimize fold cracking.
- **Cross-grain scores**: If a crease must run perpendicular to grain, increase score width by $+0.2\text{mm}$ to prevent carton cracking on high-speed folder-gluers.

---

## 5. Failure Modes & Anti-Patterns

1. **Zero-Clearance Dust Flaps**: Designing dust flaps with square $90^\circ$ ends causes them to collide with top tuck tabs; always apply a $3^\circ - 5^\circ$ lead-in taper.
2. **Rollover Pinching**: Folding a double-wall tray without adding an extra $1.0\cdot t$ gap on the inner wall causes the outer wall to bow and crack.
3. **Over-Creasing**: Using excessive creasing depth on recycled board (WLC) breaks outer liner fibers; inspect score indentation depth to maintain $\ge 60\%$ remaining fiber tensile strength.
