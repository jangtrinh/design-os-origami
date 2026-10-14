# Claude Desktop: manual local MCP setup

Prerequisites: [local setup](local-setup.md), installed Claude Desktop, required
sign-in, local Python, workspace/cache. This is local MCP configuration, not a
Desktop plugin archive. GUI discovery/execution/display is owner-manual.
See the [official local-server guide](https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers).

## Install and invoke

Back up the existing settings file privately, then print resolved configuration:

```sh
python3 scripts/host_config.py --host claude-desktop --workspace "$HOME/OrigamiRuns" \
  --browser-cache "$HOME/.cache/origami-cad-browser"
```

Merge only `mcpServers.origami-cad` into `claude_desktop_config.json`:
on macOS it is under `~/Library/Application Support/Claude/`; on Windows under
`%APPDATA%\Claude\`. Use absolute interpreter/check-out/workspace paths. Preserve
unrelated entries; the printed snippet and committed template do not mutate them.
Restart Desktop, confirm the local server/tools, then load `origami-workflow`.
Desktop does not implicitly load a CLI plugin's skill directory.

## Smoke

Run [verification](verification.md) in the GUI. Confirm actual calls and open
artifacts/look sheet; use bounded artifact-read if local links cannot display.
Record owner-manual/pending until these observations exist. Protocol tests or
another CLI host's receipt cannot close this GUI leg.

## Update, removal and rollback

Preserve checkout/settings backups before updating. Rerun contract/bundle
checks; regenerate the snippet if the checkout/interpreter/workspace moved.
Restart and smoke. Remove only `origami-cad` from the config and restart to
uninstall this setup. For rollback, restore the previous checkout and relevant
settings entry from the private backup, preserving later unrelated changes;
restart and repeat smoke. Generated CAD runs are retained.

Limits: no `.mcpb`, bundled interpreter, claude.ai remote connector, hosted
service, certified physical assembly or recipient RIP/CAD acceptance.
