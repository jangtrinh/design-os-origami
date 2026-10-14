# Gemini CLI: generated local extension

Installation and discovery were observed with Gemini CLI 0.63.0. Execution was
blocked by Gemini sign-in on the test machine; support remains unqualified.

Prerequisites: [local setup](local-setup.md), installed/authenticated Gemini CLI,
writable artifact workspace and prepared browser cache. Interface checked with
Gemini CLI 0.63.0 and its [official extension reference](https://geminicli.com/docs/extensions/reference/).

## Install

Back up affected extension/settings state privately. From the checkout:

```sh
gemini extensions validate ./bundles/gemini
gemini extensions install ./bundles/gemini
gemini extensions list
python3 scripts/host_config.py --host gemini --workspace "$HOME/OrigamiRuns" \
  --browser-cache "$HOME/.cache/origami-cad-browser"
```

Merge only the printed server into your chosen `.gemini/settings.json` scope.
Restart; confirm extension context, canonical skill and MCP tools are discovered.
Invoke `es-origami-cad` and supply the original checkout as repo-root. `GEMINI.md`
links the bundled canonical instructions; it has no second engineering workflow.

If an older standalone global skill exists, back it up first. Generate a new
mirror at a separate path, compare it, then activate it using your host's skill
installation mechanism; retire the old copy only after discovery/smoke succeeds:

```sh
python3 scripts/sync_host_bundles.py --output-skill /absolute/new-skill-mirror
python3 scripts/sync_host_bundles.py --output-skill /absolute/new-skill-mirror --check
```

The generator refuses existing destinations. Never hand-copy or hand-edit the
canonical bundle, replace an old mirror without a backup, or assume an historical
nonstandard global skill path is an installed host's current discovery path.

## Smoke

Run [verification](verification.md), including negative input and actual saved
look sheet. A listed extension or loaded context alone is not execution evidence.

## Update, removal and rollback

After updating the checkout and passing contract/bundle checks, reinstall the
local extension to refresh its copied files:

```sh
gemini extensions uninstall design-os-origami
gemini extensions install ./bundles/gemini
```

Restart and smoke. To remove, uninstall only `design-os-origami` and remove only
the added server entry. Restore any prior standalone skill from its private
backup if migrated. Rollback: preserve old checkout revision, extension/settings
backup, reinstall from that revision, then rerun smoke. Keep generated CAD runs.

Limits: local extension/CLI only; no hosted Gemini service integration. Browser
cache availability, physical fit and recipient import require separate evidence.
