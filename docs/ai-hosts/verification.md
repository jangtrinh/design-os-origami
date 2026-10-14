# Host smoke and evidence

Run after [local setup](local-setup.md) and the selected host guide. A manifest
validation or successful installation is not a completed host smoke.

1. Restart into a fresh host session; confirm `es-origami-cad` or the
   `origami-workflow` prompt and the local server/tools are visible.
2. Ask the host to execute the request below in a new run directory. Preserve its
   actual tool/command calls, direct exits and artifact paths.
3. Supply a deliberate invalid dimension (for example width −1) in a separate
   request. Confirm named rejection and no successful-looking partial run.
4. Open the actual artifact and saved look sheet; capture the host result and
   evidence. Inspect human look items L1–L3; record machine L4–L9 separately.
5. Record host version/OS, source revision/hashes, bundle digest, commands, exits,
   actual discovery/execution/display results and every NOT RUN/NOT VERIFIED leg.

Request:

> Use es-origami-cad, or the origami-workflow prompt, to build the canonical
> tuck-box printer example in a new run directory. Validate it, capture the look
> sheet using the prepared user cache, and report artifact paths and verification
> limits. Use the original checkout as repo-root.

Expected requested delivery: presentation SVG/R12 DXF/viewer, printer PDF/R2000
DXF, artifact receipt and look sheet. `origami_describe`, `origami_build`,
`origami_validate`, `origami_look`, `origami_read_artifact` and the workflow prompt
are the bounded MCP surface. Use bounded artifact-read when a host cannot display
local file links; discovering a tool is not proof it executed.

Keep detailed receipts and settings backups private. Publish only sanitized
summaries; do not expose personal paths, credentials or host state. Record failed,
blocked and owner-manual legs explicitly. Host UI/sign-in acceptance is separate
from protocol unit tests, local CLI generation and screenshots of other hosts.

The [release checker](../../scripts/check_host_bundle_release.py) and
[canonical skill tests](../../tests/test_skill_shape.py) provide deterministic
product gates. Their success cannot replace these actual host observations.
Physical fit and recipient import remain NOT VERIFIED.
