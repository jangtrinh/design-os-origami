# Local clone, cache and configuration

Python ≥3.10 runs the product and MCP adapter using stdlib. Install/authenticate
your chosen host independently. Keep the checkout; bundles carry skill files,
not another engine. Commands below run from the checkout root.

```sh
git clone https://github.com/jangtrinh/design-os-origami.git
cd design-os-origami
python3 scripts/skill_contract.py --check
python3 scripts/sync_host_bundles.py --check
python3 -B scripts/run_mcp.py --help
```

Repository publication and remote availability require separate confirmation.
Use a new writable run directory beneath your selected artifact workspace.

```sh
ORIGAMI_REPO="$(pwd -P)"
ORIGAMI_WORKSPACE="$HOME/OrigamiRuns"
python3 scripts/host_config.py --host claude-desktop \
  --repo-root "$ORIGAMI_REPO" --workspace "$ORIGAMI_WORKSPACE" \
  --browser-cache "$HOME/.cache/origami-cad-browser"
```

The renderer prints JSON (`mcpServers.origami-cad`) or, with `--host codex`,
TOML (`mcp_servers.origami-cad`). Paths are absolute, resolved and escaped;
`command` is an interpreter and `args` an argv array, never a shell command.
Use `--python-executable /absolute/python` to choose another existing runtime.
It creates no workspace, settings file or host registration. Review its output,
back up the consuming settings file privately, and merge only this server entry.
The committed Desktop/Cursor templates contain explanatory placeholders and are
not installable configuration; use the renderer instead.

## Browser preparation

[look.md](../../skills/es-origami-cad/look.md) specifies the fixed sheet and checks.
The public [capture harness](../../scripts/capture-viewer.cjs) implements the
README fold capture procedure; `look.py --help` describes invocation. Keep Playwright/browser/pinned Three.js in a user
cache. Provisioning is separate and explicit. Build/validate do not need a browser.
Look neither installs nor downloads; absent runtime/cache returns cannot-run (2).
The viewer's pinned CDN request is fulfilled from verified cache during look.
A missing look sheet means visual acceptance remains pending.

Explicit setup on macOS/Linux (Node22+, npm and curl required):

```sh
ORIGAMI_BROWSER_CACHE="$HOME/.cache/origami-cad-browser"
mkdir -p "$ORIGAMI_BROWSER_CACHE"
npm install --prefix "$ORIGAMI_BROWSER_CACHE" --no-save --package-lock=false playwright@1.62.1
node "$ORIGAMI_BROWSER_CACHE/node_modules/playwright/cli.js" install chromium
node -e 'const fs=require("fs"),p=require(process.argv[1]+"/node_modules/playwright");fs.writeFileSync(process.argv[1]+"/browser.json",JSON.stringify({executable_path:p.chromium.executablePath()}))' "$ORIGAMI_BROWSER_CACHE"
curl -fsSL https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js -o "$ORIGAMI_BROWSER_CACHE/three-r128.min.js"
python3 -c 'import hashlib,pathlib,sys;assert hashlib.sha256((pathlib.Path(sys.argv[1])/"three-r128.min.js").read_bytes()).hexdigest()=="9274bbcec8d96168626c732b5d31c775aa8cfb7eaa0599bec0c175908a2c1ce2"' "$ORIGAMI_BROWSER_CACHE"
```

These commands explicitly use network during dependency setup; capture itself
stays offline. On Linux, provision Chromium system libraries using Playwright's
documented `install --with-deps chromium` command. Windows runtime/browser
installation is not qualified here; use native absolute paths and test it.

CI pins Python3.14. Recorded preview parity uses the
[documented diagnostic precision](../fold-preview.md) across Python/platform
roundoff; geometry and availability are checked separately and remain strict.
Keep build, validation and capture on the same Python runtime. Broader host,
Windows and physical qualification still require their own evidence.

## Updates and rollback

Before pulling, preserve the prior checkout revision and back up relevant host
settings/cache privately. After an update run contract and bundle `--check`,
reinstall/refresh only this plugin, restart the host, then rerun verification.
Do not overwrite unrelated configuration or copy hand-edited bundled skills.
Rollback uses the preserved checkout revision and settings backup, then repeats
installation and smoke. Do not remove generated CAD runs as part of uninstall.

## Limits

Physical fold/fit, continuous-time collision avoidance and recipient RIP/CAD
import remain NOT VERIFIED. Current default 0.45t allowance at 90° differs from
π(R + Kt)/2; packaging does not resolve this formula conflict. No global settings
change is performed by this repository's snippet or sync generator.
