# 12 blanks. 12 with 3D.

### DESIGN:OS Origami CAD (`design-os-origami`)

**Parametric packaging dielines, Kawasaki/Maekawa foldability verification, spot-color print PDFs/DXFs, and source-derived 3D fold previews.**

Generate production-ready tuck boxes, mailers, sleeves, trays, and origami crease patterns with zero third-party Python dependencies and a 13-check mechanical validation gate.

<p align="center">
  <img src="docs/images/cover.png" alt="DESIGN:OS Origami CAD — 2:1 Axonometric Technical Architecture" width="840">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-202020?style=flat-square&labelColor=202020&color=444444" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/Claude_Code_%C2%B7_Codex_%C2%B7_Gemini_%C2%B7_Antigravity-skill-202020?style=flat-square&labelColor=202020&color=444444" alt="Compatible agents">
  <a href="commands/doctor.md"><img src="https://img.shields.io/badge/diagnostics-%2Fdoctor-202020?style=flat-square&labelColor=202020&color=444444" alt="Doctor command"></a>
  <a href="https://jangtrinh.github.io/design-os-origami/"><img src="https://img.shields.io/badge/live_docs-GitHub_Pages-202020?style=flat-square&labelColor=202020&color=444444" alt="Live GitHub Pages"></a>
  <a href="https://buymeacoffee.com/jangtrinh"><img src="https://img.shields.io/badge/Buy_Me_a_Coffee-FFDD00?style=flat-square&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me a Coffee"></a>
</p>

<p align="center">
  <a href="#quickstart">Quickstart</a> · <a href="#what-it-makes">What it makes</a> · <a href="#installation">Install</a> · <a href="#how-it-works">How it works</a> · <a href="#commands--diagnostics">Commands</a> · <a href="#quality-bar--limitations">Limits</a>
</p>

---

## Why this exists

Asking a general LLM to draw a packaging dieline produces disconnected SVG lines that cannot fold in 3D, lack paperboard caliper allowances, and fail commercial die-cutting separation checks. **`design-os-origami`** is a pure-Python stdlib parametric CAD engine with topological graph verification, spot-color PDF/DXF generation, and source-derived 3D fold kinematics.

| Dimension | Generic AI / Manual Workflow | DESIGN:OS Origami CAD (`DESIGN:OS`) |
| :--- | :--- | :--- |
| **Fold Topology** | Hallucinated SVG rectangles with unattached flaps | Mathematically verified planar face graph + Kawasaki/Maekawa flat-foldability checks |
| **Printer Exchange** | RGB screen drawings rejected by pre-press RIPs | True `/Separation` spot-color PDF (`CUT`, `CREASE_VALLEY`, `CREASE_MOUNTAIN`, `BLEED`) + R2000 DXF |
| **3D Fold Preview** | Fake decorative mockups disconnected from the dieline | Exact polygon faces and signed hinge angles derived directly from the 2D crease pattern |
| **Runtime Footprint** | Heavy CAD binaries or cloud subscriptions | 100% Python standard library runtime (`dependencies = []`) |
| **Privacy & Telemetry** | Opaque cloud telemetry or unverified third-party APIs | **Zero telemetry** — 100% local execution ([`PRIVACY.md`](PRIVACY.md) audited) |

---

## Quickstart

### 1. Install the plugin or CLI

**In Claude Code:**

```text
/plugin marketplace add jangtrinh/design-os-origami
/plugin install design-os-origami@design-os-origami
```

**Or from your terminal (Codex, Gemini CLI, Antigravity, OpenCode, or standalone CLI):**

```bash
git clone https://github.com/jangtrinh/design-os-origami.git
cd design-os-origami
PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

### 2. Ask in plain English

Open your project in your AI coding agent and describe what you need:

> "Generate a reverse-tuck end carton (120x80x45mm, 0.45mm paperboard) with print bleed, spot-color PDF/DXF dielines, and 3D fold preview."

> "Validate this packaging output directory across all 13 mechanical checks (topology, Kawasaki/Maekawa, DXF layers, and printer spots)."

> "Render a 9-panel visual inspection contact sheet for our sleeve-and-tray packaging spec and verify zero panel collisions."

### 3. Verify your setup

```bash
python3 scripts/self_check.py
```

---

## What it makes

Every deliverable produced by `design-os-origami` is backed by a deterministic verification gate rather than freehand AI guesswork.

<p align="center">
  <img src="docs/images/cover.png" alt="DESIGN:OS Origami CAD Output Specimen" width="840"><br>
  <sub>Prompt: <code>"Generate a reverse-tuck end carton (120x80x45mm, 0.45mm paperboard) with print bleed, spot-color PDF/DXF dielines, and 3D fold preview."</code></sub>
</p>

| Deliverable / Mode | Best for | Output Format | Verification Gate |
| :--- | :--- | :--- | :--- |
| **Production Dieline Suite** | Generating cutter-ready vector files with caliper & bleed allowances | `SVG + Spot-Color PDF + AutoCAD DXF + FOLD JSON` | `13-check validate.py gate PASS` |
| **Interactive 3D Fold Viewer** | Inspecting flat-to-folded hinge progression in the browser | `Self-contained HTML + fold-model JSON` | `preview_records_match parity check` |
| **9-Panel Visual Evidence Sheet** | Headless Chromium inspection sheet (`L1`–`L9`) for human pre-press review | `evidence/look-sheet.png + receipt.json` | `look.py 9-checkpoint verifier` |

---

## Installation

Choose the setup that matches your AI coding agent. Every option installs the same canonical skill (`skills/es-origami-cad/SKILL.md`) and `/doctor` diagnostic suite.

### Claude Code

Run these two commands inside Claude Code:

```text
/plugin marketplace add jangtrinh/design-os-origami
/plugin install design-os-origami@design-os-origami
```

### OpenAI Codex

Install to your personal Codex skills directory:

```bash
git clone https://github.com/jangtrinh/design-os-origami.git /tmp/design-os-origami
mkdir -p ~/.codex/skills/es-origami-cad ~/.codex/prompts
cp -R /tmp/design-os-origami/skills/es-origami-cad/* ~/.codex/skills/es-origami-cad/
cp /tmp/design-os-origami/prompts/doctor.md ~/.codex/prompts/es-origami-cad-doctor.md
rm -rf /tmp/design-os-origami
```

### Gemini CLI & Google Antigravity

```bash
git clone https://github.com/jangtrinh/design-os-origami.git /tmp/design-os-origami
mkdir -p ~/.gemini/skills/es-origami-cad
cp -R /tmp/design-os-origami/skills/es-origami-cad/* ~/.gemini/skills/es-origami-cad/
rm -rf /tmp/design-os-origami
```

### OpenCode, Cursor, Windsurf & Other Agent Harnesses

```bash
git clone https://github.com/jangtrinh/design-os-origami.git /tmp/design-os-origami
mkdir -p ~/.agents/skills/es-origami-cad
cp -R /tmp/design-os-origami/skills/es-origami-cad/* ~/.agents/skills/es-origami-cad/
rm -rf /tmp/design-os-origami
```

<details>
<summary>Verify or uninstall</summary>

**Verify installation:**

```bash
python3 scripts/self_check.py
```

Or run `/doctor` inside Claude Code / Codex to inspect installed skill paths, plugin manifests, and gate health.

**Uninstall:**

```bash
rm -rf ~/.claude/skills/es-origami-cad ~/.codex/skills/es-origami-cad ~/.gemini/skills/es-origami-cad ~/.agents/skills/es-origami-cad
```

</details>

---

## Usage & Prompt Cookbook

Once installed, `skills/es-origami-cad/SKILL.md` activates automatically when your prompt matches its domain triggers. Browse [`docs/cookbook.md`](docs/cookbook.md) for copy-paste prompt recipes.

**Generate & Scaffold**

```text
"Generate a reverse-tuck end carton (120x80x45mm, 0.45mm paperboard) with print bleed, spot-color PDF/DXF dielines, and 3D fold preview."
```

**Audit & Verify**

```text
"Validate this packaging output directory across all 13 mechanical checks (topology, Kawasaki/Maekawa, DXF layers, and printer spots)."
```

**Export & Automate**

```text
"Render a 9-panel visual inspection contact sheet for our sleeve-and-tray packaging spec and verify zero panel collisions."
```

---

## Commands & Diagnostics

| Command | Environment | What it does |
| :--- | :--- | :--- |
| `/doctor` | Claude Code / Codex | Read-only diagnostic check of installed skill paths, plugin manifests, and runtime prerequisites |
| `python3 scripts/self_check.py` | Terminal / CI | Deterministic offline verification of manifests, skill contracts, and governance files |
| `python3 -B scripts/skill_contract.py --check && python3 -B scripts/sync_host_bundles.py --check` | Terminal / CI | Verify canonical skill contract and portable host bundle synchronization across Claude Code, Codex, and Gemini |

---

## How it works

1. **Intent Routing** — Your AI agent matches your request against `skills/es-origami-cad/SKILL.md` frontmatter triggers.
2. **Progressive Context Loading** — Only the entry-point `SKILL.md` router loads initially; detailed recipes and scripts load on demand.
3. **Deterministic Execution** — Domain scripts and contracts execute locally with reproducible inputs and outputs.
4. **Gate Verification** — `scripts/self_check.py` and domain verifiers (`PYTHONPATH=src python3 -B -m unittest discover -s tests -v`) validate the artifact before completion.
5. **Zero-Telemetry Delivery** — Verified files are written directly to your workspace with zero external network calls.

```text
User Prompt / CLI Invocation
            │
            ▼
┌───────────────────────────────────────────────┐
│ skills/es-origami-cad/SKILL.md
│ Progressive disclosure router & hard rules    │
└───────────┬───────────────────────────────────┘
            │ loads on demand
            ▼
┌───────────────────────────────────────────────┐
│ python3 -B scripts/skill_contract.py --check && python3 -B scripts/sync_host_bundles.py --check
│ Deterministic build & contract enforcement    │
└───────────┬───────────────────────────────────┘
            │ verifies
            ▼
┌───────────────────────────────────────────────┐
│ python3 scripts/self_check.py + /doctor       │
│ Zero-telemetry local verification gate        │
└───────────────────────────────────────────────┘
```

### What loads when

`design-os-origami` uses progressive context disclosure so your agent's context window stays fast and focused:

| File | Loaded when |
| :--- | :--- |
| `skills/es-origami-cad/SKILL.md` | Always (~100–150 lines) — routing rules, triggers, and execution workflow |
| `docs/cookbook.md` | When selecting multi-step prompt recipes or domain patterns |
| `commands/doctor.md` / `prompts/doctor.md` | Only when running `/doctor` diagnostics |
| `llms.txt` | When indexed by AI answer engines, RAG pipelines, or repo crawlers |

---

## File structure

```text
design-os-origami/
├── .claude-plugin/
│   ├── plugin.json                 # Claude Code plugin manifest
│   └── marketplace.json            # Claude Code marketplace catalog
├── .codex-plugin/
│   └── plugin.json                 # OpenAI Codex plugin & interface manifest
├── .agents/
│   └── plugins/marketplace.json    # Cross-agent local plugin registry
├── .factory-plugin/
│   ├── plugin.json                 # Factory / Droid plugin manifest
│   └── marketplace.json            # Factory marketplace metadata
├── skills/
│   └── es-origami-cad/
│       └── SKILL.md                # Canonical agent skill entrypoint
├── commands/
│   └── doctor.md                   # /doctor diagnostic slash command
├── prompts/
│   └── doctor.md                   # Codex diagnostic prompt mirror
├── scripts/
│   └── self_check.py               # Deterministic repository & skill self-check
├── docs/
│   ├── cookbook.md                 # Copy-paste prompt recipes by job
│   └── llms.txt                    # GEO / LLM discovery index
├── PRIVACY.md                      # Zero-telemetry & local-first privacy commitment
├── SECURITY.md                     # Vulnerability disclosure & security policy
├── CONTRIBUTING.md                 # Contribution workflow & verification rules
├── CODE_OF_CONDUCT.md              # Contributor Covenant code of conduct
├── CHANGELOG.md                    # Release history
├── llms.txt                        # Root LLM indexing manifest
├── LICENSE                         # MIT License
└── README.md
```

---

## Quality bar & Limitations

### It's working if...

- `python3 scripts/self_check.py` prints `ok: design-os-origami self-check passed (es-origami-cad)` and exits `0`.
- `PYTHONPATH=src python3 -B -m unittest discover -s tests -v` passes with zero contract or test regressions.
- Your AI coding agent loads `skills/es-origami-cad/SKILL.md` automatically when given any prompt from [`docs/cookbook.md`](docs/cookbook.md).
- Network traffic during execution remains zero (guaranteed by [`PRIVACY.md`](PRIVACY.md)).

### When not to use

- Curved thermoformed plastic blisters, blow-molded bottles, or injection-molded enclosures (use `design-os-3d-blender`).
- Substituting for physical sample cutting on your target paperboard stock (`PHYSICAL_FOLD_FIT` always requires a real physical sample).
- Freeform artistic illustration unrelated to foldable sheet geometry.

---

## DESIGN:OS Ecosystem

`design-os-origami` is one of the 13 open-source engines in the **`DESIGN:OS`** ecosystem:

| Engine | Live Docs | Repository | Layer |
| :--- | :--- | :--- | :--- |
| **DESIGN:OS CLI** | [jangtrinh.github.io/design-os](https://jangtrinh.github.io/design-os/) | [`jangtrinh/design-os`](https://github.com/jangtrinh/design-os) | `cli` |
| **Knowledge Builder** | [jangtrinh.github.io/design-os-knowledge-builder](https://jangtrinh.github.io/design-os-knowledge-builder/) | [`jangtrinh/design-os-knowledge-builder`](https://github.com/jangtrinh/design-os-knowledge-builder) | `compiler` |
| **Figma Plugin & CLI** | [jangtrinh.github.io/design-os-figma-plugin](https://jangtrinh.github.io/design-os-figma-plugin/) | [`jangtrinh/design-os-figma-plugin`](https://github.com/jangtrinh/design-os-figma-plugin) | `plugin` |
| **SVG Animation Engine** | [jangtrinh.github.io/design-os-svg-animation](https://jangtrinh.github.io/design-os-svg-animation/) | [`jangtrinh/design-os-svg-animation`](https://github.com/jangtrinh/design-os-svg-animation) | `engine` |
| **3D Blender Agent** | [jangtrinh.github.io/design-os-3d-blender](https://jangtrinh.github.io/design-os-3d-blender/) | [`jangtrinh/design-os-3d-blender`](https://github.com/jangtrinh/design-os-3d-blender) | `3d / cad` |
| **OPAH ONE Drone** | [jangtrinh.github.io/design-os-drone-showcase](https://jangtrinh.github.io/design-os-drone-showcase/) | [`jangtrinh/design-os-drone-showcase`](https://github.com/jangtrinh/design-os-drone-showcase) | `hardware` |
| **GitHub Pages Engine** | [jangtrinh.github.io/design-os-github-page](https://jangtrinh.github.io/design-os-github-page/) | [`jangtrinh/design-os-github-page`](https://github.com/jangtrinh/design-os-github-page) | `pages` |
| **Apple Design OS** | [jangtrinh.github.io/design-os-apple](https://jangtrinh.github.io/design-os-apple/) | [`jangtrinh/design-os-apple`](https://github.com/jangtrinh/design-os-apple) | `swiftui` |
| **Agent Teacher** | [jangtrinh.github.io/design-os-pedagogy](https://jangtrinh.github.io/design-os-pedagogy/) | [`jangtrinh/design-os-pedagogy`](https://github.com/jangtrinh/design-os-pedagogy) | `pedagogy` |
| **Origami CAD** | [jangtrinh.github.io/design-os-origami](https://jangtrinh.github.io/design-os-origami/) | [`jangtrinh/design-os-origami`](https://github.com/jangtrinh/design-os-origami) | `packaging` |
| **Voice UX Architecture** | [jangtrinh.github.io/design-os-voice-ux](https://jangtrinh.github.io/design-os-voice-ux/) | [`jangtrinh/design-os-voice-ux`](https://github.com/jangtrinh/design-os-voice-ux) | `voice-ai` |
| **Code2Flow** | [jangtrinh.github.io/design-os-code2flow](https://jangtrinh.github.io/design-os-code2flow/) | [`jangtrinh/design-os-code2flow`](https://github.com/jangtrinh/design-os-code2flow) | `ast / audit` |
| **Generative UI** | [jangtrinh.github.io/design-os-generative-ui](https://jangtrinh.github.io/design-os-generative-ui/) | [`jangtrinh/design-os-generative-ui`](https://github.com/jangtrinh/design-os-generative-ui) | `runtime` |

---

## Contributing, Governance & License

- **Contributing**: See [`CONTRIBUTING.md`](CONTRIBUTING.md) for pull request guidelines and verification gates (`python3 scripts/self_check.py`).
- **Code of Conduct**: Governed by [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
- **Security & Privacy**: Zero telemetry — see [`SECURITY.md`](SECURITY.md) and [`PRIVACY.md`](PRIVACY.md).
- **Changelog & LLM Index**: Track releases in [`CHANGELOG.md`](CHANGELOG.md) and machine-readable index in [`llms.txt`](llms.txt).
- **License**: [MIT](LICENSE) © [Jang Trinh](https://github.com/jangtrinh).

---

If `design-os-origami` saves you time, a star on GitHub helps other engineers and AI agents find it.

<p align="left">
  <a href="https://buymeacoffee.com/jangtrinh">
    <img src="https://img.shields.io/badge/Buy_Me_a_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me a Coffee">
  </a>
</p>
