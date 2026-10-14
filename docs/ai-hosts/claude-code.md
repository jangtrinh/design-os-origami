# Claude Code: local plugin and stdio MCP

Prerequisites: [local setup](local-setup.md), installed/authenticated Claude Code,
a writable artifact workspace, and a prepared browser cache for look.
Manifest/commands checked against Claude Code 2.1.296 and its
[official reference](https://code.claude.com/docs/en/plugins-reference).

## Install

Run from the product checkout. Back up affected plugin/settings state privately
before registration; preserve unrelated marketplaces and server entries.

```sh
claude plugin validate bundles/claude-code --strict
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin marketplace add ./
claude plugin install design-os-origami@design-os-origami-local
python3 scripts/host_config.py --host claude-code --workspace "$HOME/OrigamiRuns" \
  --browser-cache "$HOME/.cache/origami-cad-browser"
```

Merge the printed `origami-cad` entry into the consuming project's `.mcp.json`.
Restart, inspect `/mcp`, and invoke `/design-os-origami:es-origami-cad` (or select
the installed skill in the host UI). Supply the original checkout as repo-root.
The portable bundle intentionally contains no personal absolute paths.

## Smoke

Run [verification](verification.md) in the fresh session, including real artifact
creation, negative input, validation, look and display. Capture actual host state.
A strict manifest pass establishes schema acceptance only.

## Update, removal and rollback

Update the preserved clone, rerun contract/bundle checks, then:

```sh
claude plugin marketplace update design-os-origami-local
claude plugin update design-os-origami@design-os-origami-local
```

Restart and rerun smoke. To remove:

```sh
claude plugin uninstall design-os-origami@design-os-origami-local
claude plugin marketplace remove design-os-origami-local
```

Remove only the added MCP server entry or restore its private backup after
checking for unrelated subsequent changes. Roll back to the preserved checkout
revision, restore affected settings, reinstall and smoke; keep all CAD runs.

Limits: local Claude Code integration only. No claude.ai connector, hosted
service, physical acceptance or recipient approval is established by installation.
