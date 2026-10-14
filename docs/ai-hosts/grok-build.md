# Grok Build CLI: resolved local plugin

Prerequisites: [local setup](local-setup.md), the official Grok Build CLI,
authentication, writable artifact workspace and prepared browser cache.
Verify the binary's `--version` and `plugin --help`: another executable named
`grok` is not sufficient. Syntax follows the [official Grok Build plugin guide](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/09-plugins.md).
Local Grok Build smoke remains pending an actual supported runtime receipt.

## Install

Back up affected Grok Build settings/plugin state privately. Generate a fresh
machine-local staging package outside the committed portable bundle:

```sh
python3 scripts/sync_host_bundles.py --stage-host grok-build \
  --output-dir /absolute/new-local-plugin --workspace "$HOME/OrigamiRuns" \
  --browser-cache "$HOME/.cache/origami-cad-browser"
grok plugin validate /absolute/new-local-plugin
grok plugin install /absolute/new-local-plugin --trust
grok plugin list --json
```

The staged `.mcp.json` points to the original checkout/interpreter, with argv
escaped as JSON. The directory must not exist before generation. Do not commit
or publish it: it contains local absolute paths. `--trust` acknowledges the
reviewed plugin installation; preserve normal runtime permissions/hooks.
Restart (or reload the Plugins tab), inspect `/mcps`, and invoke
`/design-os-origami:es-origami-cad` where qualified names are shown.

## Smoke

Run [verification](verification.md) in the actual Grok Build session; retain
real tool execution and opened artifact/sheet evidence. No Grok consumer app,
Grok API remote connector or hosted MCP is supplied by this package.

## Update, removal and rollback

Update the checkout, pass contract/bundle checks, generate a new staged package
with resolved paths, validate it and reinstall from that path. Restart and smoke.
Use the host's actual supported syntax; current official management commands:

```sh
grok plugin update design-os-origami
grok plugin uninstall design-os-origami --confirm
```

Remove only this setup's server/marketplace entries if registered separately.
Preserve CAD runs and backups; retire old local staging only after verified
activation. Rollback uses the preserved checkout, old staged package and private
settings backup, then reinstall and fresh smoke. Never infer rollback from a
successful uninstall alone.

Limits: manifest compatibility is distinct from installation, execution and
artifact display. Official binary/authentication and complete smoke are required
before host support is claimed. Physical fit/recipient import remain unverified.
