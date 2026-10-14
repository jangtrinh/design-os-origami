# Use DESIGN:OS Origami with a local AI host

Start with [local setup](local-setup.md), install one host package, then run the
[verification workflow](verification.md). The canonical
[es-origami-cad skill](../../skills/es-origami-cad/SKILL.md) drives the same engine
through CLI entrypoints or the shared local stdio MCP server.

| Host | Package/setup | Qualification boundary |
| --- | --- | --- |
| [Claude Code](claude-code.md) | Local plugin + project MCP snippet | Requires fresh host smoke receipt |
| [Codex CLI](codex-cli.md) | Local marketplace plugin + stdio registration | Codex CLI only; no ChatGPT web connector |
| [Gemini CLI](gemini-cli.md) | Local extension + resolved MCP snippet | Installation/discovery observed; execution blocked by Gemini sign-in on the test machine; support unqualified |
| [Grok Build CLI](grok-build.md) | Local staged plugin with stdio config | Official Grok Build binary required |
| [Claude Desktop](claude-desktop.md) | Manual local MCP configuration | Owner-manual GUI discovery/acceptance |
| [Cursor](cursor.md) | Manual local MCP configuration | Owner-manual GUI discovery/acceptance |

Packages are generated, regular-file copies. No hosted server, remote MCP,
tunnel, app-store submission or consumer/API connector is included. The local
CAD runtime is offline; an AI host may still use its own network/model service.
Installation does not establish execution, artifact display or host support.

See [printer limits](../printer-profile.md), [preview limits](../fold-preview.md)
and [attribution](../../skills/es-origami-cad/ATTRIBUTION.md).
