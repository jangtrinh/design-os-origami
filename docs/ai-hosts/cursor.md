# Cursor: manual local MCP setup

Prerequisites: [local setup](local-setup.md), installed/authenticated Cursor,
local Python, artifact workspace and prepared browser cache. GUI acceptance is
owner-manual. Configuration locations follow the [official MCP guide](https://cursor.com/docs/mcp).

## Install and invoke

Back up the existing selected settings file privately. From the checkout:

```sh
python3 scripts/host_config.py --host cursor --workspace "$HOME/OrigamiRuns" \
  --browser-cache "$HOME/.cache/origami-cad-browser"
```

Merge only `mcpServers.origami-cad` into the consuming project's `.cursor/mcp.json`
or your chosen user MCP configuration. Absolute resolved command/argv point to
the original clone. Preserve unrelated entries. Restart/refresh MCP in Cursor,
confirm tools, then use the `origami-workflow` prompt or canonical skill guidance
with those tools. No VS Code extension or second engine is installed.

## Smoke

Run [verification](verification.md) in Cursor; inspect actual tool calls and
opened generated artifact/look sheet. If local links cannot display, use the
bounded artifact-read tool. Report GUI discovery/execution/display as pending
owner-manual until captured; unit tests are separate evidence.

## Update, removal and rollback

Preserve checkout/settings backups, update the clone, pass contract/bundle
checks, and regenerate the snippet if paths changed. Refresh/restart and smoke.
Remove only the `origami-cad` server entry to uninstall; keep generated CAD runs.
Rollback: preserved checkout and private settings backup, restore the affected
entry while preserving subsequent unrelated edits, restart and repeat smoke.

Limits: local MCP only; no Cursor extension, hosted server, consumer connector,
physical fold/fit certification or recipient import acceptance. Installation
and tool discovery alone do not establish a complete workflow.
