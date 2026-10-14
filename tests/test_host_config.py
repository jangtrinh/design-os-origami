"""Resolved snippets preserve argv and never write host configuration."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import host_config


class TestHostConfig(unittest.TestCase):
    def test_json_and_toml_preserve_spaces_unicode_and_quotes(self):
        with tempfile.TemporaryDirectory(prefix='origami résumé ') as temp:
            root = Path(temp) / 'checkout "quoted" 日本語 😀'
            (root / 'scripts').mkdir(parents=True)
            (root / 'scripts/run_mcp.py').write_text('')
            workspace = Path(temp) / 'output thư mục'
            for host in host_config.HOSTS:
                rendered = host_config.render(host, root, workspace, sys.executable)
                if host == 'codex':
                    self.assertIn('[mcp_servers.origami-cad]', rendered)
                    try:
                        import tomllib
                    except ImportError:
                        pass
                    else:
                        self.assertIn('origami-cad', tomllib.loads(rendered)['mcp_servers'])
                    args = json.loads(next(line[7:] for line in rendered.splitlines()
                                           if line.startswith('args = ')))
                else:
                    server = json.loads(rendered)['mcpServers']['origami-cad']
                    self.assertEqual(server['command'], str(Path(sys.executable).resolve()))
                    args = server['args']
                self.assertEqual(args, ['-B', str(root.resolve() / 'scripts/run_mcp.py'),
                                        '--workspace', str(workspace.resolve())])
                self.assertFalse(workspace.exists())

    def test_cache_option_is_resolved_without_creating_it(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "scripts").mkdir()
            (root / "scripts/run_mcp.py").write_text("")
            cache = root / "cache with spaces"
            server = host_config.server_config(root, root / "out", sys.executable, cache)
            self.assertEqual(server["args"][-2:], ["--browser-cache", str(cache.resolve())])
            self.assertFalse(cache.exists())

    def test_missing_launcher_or_interpreter_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                host_config.render('cursor', Path(temp), Path(temp) / 'out', sys.executable)

    def test_cli_outputs_parseable_json_and_no_writes(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, '-B', str(root / 'scripts/host_config.py'),
                                     '--host', 'cursor', '--repo-root', str(root),
                                     '--workspace', str(Path(temp) / 'absent')], capture_output=True, text=True)
            # Launcher is supplied by the root integration worker.
            if not (root / 'scripts/run_mcp.py').exists():
                self.assertEqual(result.returncode, 2)
            else:
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('mcpServers', json.loads(result.stdout))
            self.assertFalse((Path(temp) / 'absent').exists())
