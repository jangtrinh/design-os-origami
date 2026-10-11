"""Disposable tracked checkout shared by snapshot contract tests."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_public_snapshot.py"
SPEC = importlib.util.spec_from_file_location("public_snapshot", SCRIPT)
snapshot = importlib.util.module_from_spec(SPEC)
sys.path.insert(0, str(SCRIPT.parent))
SPEC.loader.exec_module(snapshot)
sys.path.pop(0)


class PublicSnapshotFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.source = self.base / "source"
        self.source.mkdir()
        self.output = self.base / "public"
        self.probes = 0
        for name in snapshot.ROOT_FILES:
            self.write(name, b"public root\n")
        for name in snapshot.TREES:
            self.write(name + "/sample.txt", b"safe public body\n")
        for name in snapshot.PUBLIC_SCRIPTS:
            self.write("scripts/" + name, b"safe script\n")
        for name in ("docs/index.html", "docs/robots.txt", "docs/sitemap.xml",
                     "docs/llms.txt", "src/origami_cad/cli.py"):
            self.write(name, b"public body\n")
        self.git("init", "--quiet")
        self.write_manifest()
        self.git("add", ".")

    def write(self, name, data):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.source), *args],
                              check=True, capture_output=True, text=True).stdout

    def write_manifest(self):
        names = {p.relative_to(self.source).as_posix() for p in self.source.rglob("*")
                 if p.is_file() and ".git" not in p.relative_to(self.source).parts}
        names.add("scripts/public_manifest.txt")
        self.write("scripts/public_manifest.txt", ("\n".join(sorted(names)) + "\n").encode())

    def reject(self):
        self.probes += 1
        self.output = self.base / ("rejected-" + str(self.probes))
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.build_snapshot(self.source, self.output)
        self.assertFalse(self.output.exists())
