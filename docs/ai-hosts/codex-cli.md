# Codex CLI: local marketplace and stdio MCP

Prerequisites: [local setup](local-setup.md), installed/authenticated Codex CLI,
a writable artifact workspace and prepared browser cache. This guide covers
Codex CLI, not ChatGPT web, hosted apps or consumer connectors. Interface checked
with Codex CLI 0.162.1 and [OpenAI's plugin reference](https://developers.openai.com/plugins/build/plugins).

## Install

Back up affected Codex settings/plugin state privately. Run from the checkout:

```sh
codex plugin marketplace add .
codex plugin add design-os-origami@design-os-origami-local
python3 scripts/host_config.py --host codex --workspace "$HOME/OrigamiRuns" \
  --browser-cache "$HOME/.cache/origami-cad-browser"
```

Merge the printed `[mcp_servers.origami-cad]` stanza into the chosen Codex config
scope, preserving unrelated entries. Alternatively register the same resolved
interpreter/argv with `codex mcp add origami-cad -- ...`; copy real values from the
renderer, not explanatory placeholders. Do not register both forms.
Restart Codex, inspect `/mcp`, select `$es-origami-cad` and give the original
checkout as repo-root. The root `plugin.json` uses the portable Agent Plugins
schema and fixed `skills/` layout. Marketplace source paths are relative to the
marketplace root, not `.agents/plugins/`.

## Smoke

Run [verification](verification.md) through this actual Codex session. Inspect
output artifacts/look sheet and retain commands/exits. Package discovery and
CLI installation alone do not establish MCP execution or display support.

## Update, removal and rollback

Update the clone and rerun contract/bundle checks. Local packages need reinstall
to refresh the cached copy:

```sh
codex plugin remove design-os-origami@design-os-origami-local
codex plugin add design-os-origami@design-os-origami-local
```

`codex plugin marketplace upgrade` refreshes Git marketplace snapshots; it is
not a substitute for local reinstall. Restart and smoke. To remove this setup:

```sh
codex plugin remove design-os-origami@design-os-origami-local
codex plugin marketplace remove design-os-origami-local
codex mcp remove origami-cad
```

If registration was merged into another config scope, remove only that stanza
there instead. Rollback: preserved checkout revision, private config backup,
reinstall and fresh smoke; preserve subsequent unrelated settings and CAD runs.

Limits: host version/account capabilities can differ. Local CLI/MCP acceptance
is not ChatGPT web support, physical fold/fit or recipient import acceptance.
