"""Print resolved local stdio configuration; never mutate host settings."""
import argparse
import json
import re
from pathlib import Path
import sys

HOSTS = ('claude-code', 'codex', 'gemini', 'grok-build', 'claude-desktop', 'cursor')


def server_config(repo_root, workspace, python_executable=None, browser_cache=None):
    root = Path(repo_root).expanduser().resolve()
    output = Path(workspace).expanduser().resolve()
    interpreter = Path(python_executable or sys.executable).expanduser().resolve()
    launcher = root / 'scripts/run_mcp.py'
    if not launcher.is_file() or launcher.is_symlink():
        raise ValueError('host-config: supply a checkout containing scripts/run_mcp.py')
    if not interpreter.is_file():
        raise ValueError('host-config: supply an existing Python executable')
    if output.exists() and not output.is_dir():
        raise ValueError('host-config: workspace must be a directory path')
    if any(ord(char) < 32 for path in (root, output, interpreter) for char in str(path)):
        raise ValueError('host-config: remove control characters from paths')
    args = ['-B', str(launcher), '--workspace', str(output)]
    if browser_cache is not None:
        cache = Path(browser_cache).expanduser().resolve()
        if any(ord(char) < 32 for char in str(cache)):
            raise ValueError('host-config: remove control characters from cache path')
        args += ['--browser-cache', str(cache)]
    return {'command': str(interpreter), 'args': args}


def render(host, repo_root, workspace, python_executable=None, browser_cache=None):
    if host not in HOSTS:
        raise ValueError('host-config: choose a supported local host')
    server = server_config(repo_root, workspace, python_executable, browser_cache)
    if host == 'codex':
        # JSON strings/arrays here are valid TOML basic strings/arrays.
        return ('[mcp_servers.origami-cad]\ncommand = ' + json.dumps(server['command'], ensure_ascii=False) +
                '\nargs = ' + json.dumps(server['args'], ensure_ascii=False) + '\n')
    return json.dumps({'mcpServers': {'origami-cad': server}}, indent=2, ensure_ascii=False) + '\n'


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def product_version(root):
    # Python 3.10 has no tomllib. Read only the product's simple [project] version.
    text = (root / 'pyproject.toml').read_text(encoding='utf-8')
    section = re.search(r'(?ms)^\[project\]\s*\n(.*?)(?=^\[|\Z)', text)
    versions = re.findall(r'(?m)^version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+(?:[-+][\w.-]+)?)"\s*$',
                          section.group(1) if section else '')
    if len(versions) != 1:
        raise ValueError('bundle-version: provide one static project version in pyproject.toml')
    return versions[0]


def expected_manifests(root, version):
    """Generate manifest bytes only; source paths follow each host specification."""
    identity = {'name': 'design-os-origami', 'version': version,
                'description': 'Local parametric packaging dielines and validation.',
                'author': {'name': 'DESIGN:OS'}, 'license': 'LicenseRef-PolyForm-Shield-1.0.0'}
    expected = {}
    for host in ("claude-code", "codex", "gemini", "grok-build"):
        base = Path('bundles') / host
        if host == 'gemini':
            manifest = {key: identity[key] for key in ('name', 'version', 'description')}
            manifest['contextFileName'] = 'GEMINI.md'
            expected[base / 'gemini-extension.json'] = json_bytes(manifest)
            expected[base / 'GEMINI.md'] = (b'# DESIGN:OS Origami\n\n'
                b'Load [es-origami-cad](skills/es-origami-cad/SKILL.md).\n'
                b'Use the original product checkout as --repo-root; this bundle carries no engine.\n'
                b'Installation and MCP setup: https://jangtrinh.github.io/design-os-origami/ai-hosts/gemini-cli.md\n')
        else:
            manifest = dict(identity)
            path = '.claude-plugin/plugin.json' if host == 'claude-code' else 'plugin.json'
            if host == 'codex':
                manifest['$schema'] = 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
            expected[base / path] = json_bytes(manifest)
    name = 'design-os-origami-local'
    plugin = 'design-os-origami'
    for folder, host in (('.claude-plugin', 'claude-code'), ('.grok-plugin', 'grok-build')):
        source = './bundles/' + host
        if host == 'grok-build':
            source = {'type': 'local', 'path': source}
        marketplace = {
            'name': name, 'owner': {'name': 'DESIGN:OS'},
            'plugins': [{'name': plugin, 'source': source}]}
        if host == 'claude-code':
            marketplace['description'] = 'Local packaging CAD workflow, validation and fold evidence.'
        expected[Path(folder) / 'marketplace.json'] = json_bytes(marketplace)
    expected[Path('.agents/plugins/marketplace.json')] = json_bytes({
        'name': name, 'interface': {'displayName': 'DESIGN:OS Origami Local'},
        'plugins': [{'name': plugin, 'source': {'source': 'local', 'path': './bundles/codex'},
                     'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'},
                     'category': 'Productivity'}]})
    template = {'mcpServers': {'origami-cad': {'command': '<absolute-python-executable>',
                'args': ['-B', '<absolute-checkout>/scripts/run_mcp.py',
                         '--workspace', '<absolute-artifact-workspace>']}}}
    for host, filename in (('claude-desktop', 'claude-desktop-config.template.json'),
                           ('cursor', 'mcp.template.json')):
        expected[Path('bundles') / host / filename] = json_bytes(template)
    return expected



def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', choices=HOSTS, required=True)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--browser-cache', type=Path)
    parser.add_argument('--python-executable', type=Path, default=Path(sys.executable))
    args = parser.parse_args(argv)
    try:
        sys.stdout.write(render(args.host, args.repo_root, args.workspace, args.python_executable, args.browser_cache))
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
