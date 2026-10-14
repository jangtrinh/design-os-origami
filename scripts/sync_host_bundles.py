"""Generate exact portable host bundles, or inspect drift without writes."""
import argparse
import json
import os
from pathlib import Path
import sys

from host_config import server_config, expected_manifests, product_version

SKILL = Path('skills/es-origami-cad')
HOSTS = ('claude-code', 'codex', 'gemini', 'grok-build')
ROOTS = tuple(map(Path, ('bundles', '.claude-plugin', '.agents/plugins', '.grok-plugin')))
REQUIRED = ('SKILL.md', 'rules.md', 'concepts.md', 'look.md', 'ATTRIBUTION.md',
            'contract.md', 'build.py', 'validate.py', 'look.py')


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf-8')


def inventory(root, roots):
    found = {}
    if root.is_symlink():
        raise ValueError("bundle-links: replace linked output root")
    for managed in roots:
        start = root / managed
        for path in (start, *start.parents):
            if path == root.parent:
                break
            if path.is_symlink():
                raise ValueError('bundle-links: replace linked path with a regular copy')
        if not start.exists():
            continue
        if not start.is_dir():
            raise ValueError('bundle-path: generated roots must be directories')
        for base, dirs, files in os.walk(start, followlinks=False):
            for name in sorted(dirs + files):
                path = Path(base) / name
                if path.is_symlink():
                    raise ValueError('bundle-links: replace linked path with a regular copy')
                if not path.is_file() and not path.is_dir():
                    raise ValueError("bundle-path: only regular files and directories are allowed")
                rel = path.relative_to(root)
                found[rel] = path.read_bytes() if path.is_file() else None
    return found


def skill_files(root):
    files = inventory(root, (SKILL,))
    missing = [name for name in REQUIRED if SKILL / name not in files]
    if missing:
        raise ValueError('bundle-source: missing canonical files: ' + ', '.join(missing))
    result = {}
    for path, data in files.items():
        if data is None:
            continue
        if path.suffix not in {'.md', '.py', '.json'}:
            raise ValueError('bundle-source: unexpected canonical file: ' + path.as_posix())
        result[path.relative_to(SKILL)] = data
    return result


def expected_files(root):
    expected = expected_manifests(root, product_version(root))
    for host in HOSTS:
        expected.update({Path("bundles") / host / SKILL / path: data
                         for path, data in skill_files(root).items()})
    return expected


def drift(root, expected, roots=ROOTS):
    actual = inventory(root, roots)
    issues = ['missing: ' + p.as_posix() for p in expected.keys() - actual.keys()]
    issues += ['extra: ' + p.as_posix() for p in actual.keys() - expected.keys()
               if actual[p] is not None or not any(p in q.parents for q in expected)]
    issues += ['changed: ' + p.as_posix() for p in expected.keys() & actual.keys()
               if expected[p] != actual[p]]
    return sorted(issues)


def write_files(root, expected, fresh=False):
    if fresh and (root.exists() or root.is_symlink()):
        raise ValueError('bundle-output: choose a new output directory')
    # Inspect everything before touching anything; never traverse a linked target.
    roots = (Path('.'),) if fresh else ROOTS
    actual = inventory(root, roots)
    if any(path in actual and actual[path] is None for path in expected):
        raise ValueError("bundle-path: file destination is an existing directory")
    for path, data in actual.items():
        if data is not None and path not in expected:
            (root / path).unlink()
    for path, data in sorted(expected.items()):
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    for path, data in sorted(actual.items(), key=lambda item: len(item[0].parts), reverse=True):
        if data is None and path not in {Path('.')}:
            target = root / path
            if target.is_dir() and not any(target.iterdir()):
                target.rmdir()


def stage(root, host, output, workspace, interpreter, browser_cache=None):
    if host not in HOSTS:
        raise ValueError('bundle-host: choose a portable skill host')
    prefix = Path('bundles') / host
    files = {path.relative_to(prefix): data for path, data in expected_files(root).items()
             if prefix in path.parents}
    server = server_config(root, workspace, interpreter, browser_cache)
    filename = '.mcp.json'
    if host == 'gemini':
        manifest = json.loads(files[Path('gemini-extension.json')])
        manifest['mcpServers'] = {'origami-cad': server}
        files[Path('gemini-extension.json')] = json_bytes(manifest)
    else:
        if host == 'codex':
            filename = 'mcp.json'
            server = {'type': 'stdio', **server}
        config = {'mcpServers': {'origami-cad': server}}
        if host == 'codex':
            config['$schema'] = 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json'
        files[Path(filename)] = json_bytes(config)
    write_files(output, files, fresh=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--output-skill', type=Path, help='Generate a fresh canonical skill mirror')
    parser.add_argument('--stage-host', choices=HOSTS)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--workspace', type=Path)
    parser.add_argument('--browser-cache', type=Path)
    parser.add_argument('--python-executable', type=Path, default=Path(sys.executable))
    args = parser.parse_args(argv)
    try:
        root = args.repo_root.resolve()
        if args.stage_host:
            if args.check or args.output_skill or not args.output_dir or not args.workspace:
                raise ValueError('bundle-options: staging requires output-dir and workspace only')
            stage(root, args.stage_host, args.output_dir.absolute(), args.workspace, args.python_executable, args.browser_cache)
        elif args.output_skill:
            expected = skill_files(root)
            if args.check:
                issues = drift(args.output_skill.absolute(), expected, roots=(Path('.'),))
                if issues:
                    print('\n'.join(issues), file=sys.stderr)
                    return 1
            else:
                write_files(args.output_skill.absolute(), expected, fresh=True)
        else:
            if args.output_dir or args.workspace or args.browser_cache:
                raise ValueError('bundle-options: output-dir/workspace require stage-host')
            expected = expected_files(root)
            if args.check:
                issues = drift(root, expected)
                if issues:
                    print('\n'.join(issues), file=sys.stderr)
                    return 1
            else:
                write_files(root, expected)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print('ok: host bundles' if not args.output_skill else 'ok: canonical skill mirror')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
