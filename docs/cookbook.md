# `design-os-origami` Prompt & CLI Cookbook

Copy-paste recipes for **DESIGN:OS Origami CAD** (`skills/es-origami-cad/SKILL.md`).

---

## 1. Generate & Scaffold

> "Generate a reverse-tuck end carton (120x80x45mm, 0.45mm paperboard) with print bleed, spot-color PDF/DXF dielines, and 3D fold preview."

## 2. Audit & Verify

> "Validate this packaging output directory across all 13 mechanical checks (topology, Kawasaki/Maekawa, DXF layers, and printer spots)."

## 3. Export & Automate

> "Render a 9-panel visual inspection contact sheet for our sleeve-and-tray packaging spec and verify zero panel collisions."

---

## 4. CLI & Diagnostic Commands

```bash
# Run deterministic offline self-check
python3 scripts/self_check.py

# Run primary domain verification / workflow
PYTHONPATH=src python3 -B -m unittest discover -s tests -v

# Run primary CLI command
python3 -B scripts/skill_contract.py --check && python3 -B scripts/sync_host_bundles.py --check
```
