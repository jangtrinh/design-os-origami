"""Runtime metadata and public setup copy must match the stdlib-only implementation."""

from pathlib import Path
import re
import unittest


class TestStdlibRuntime(unittest.TestCase):
    def test_no_unused_dependency_or_public_claim(self):
        root = Path(__file__).resolve().parents[1]
        metadata = (root / "pyproject.toml").read_text()
        dependencies = re.search(r"(?ms)^dependencies\s*=\s*\[(.*?)\]", metadata)
        self.assertIsNotNone(dependencies)
        self.assertEqual(dependencies.group(1).strip(), "")
        for name in ("README.md", "docs/index.html", "docs/llms.txt"):
            with self.subTest(file=name):
                self.assertNotIn("pydantic", (root / name).read_text().casefold())

    def test_grep_finds_no_pydantic_import_in_runtime_tests_or_scripts(self):
        root = Path(__file__).resolve().parents[1]
        pattern = re.compile(r"(?m)^\s*(?:from\s+pydantic(?:\.|\s)|import\s+pydantic(?:\s|,|$))")
        checked = 0
        for directory in ("src", "tests", "scripts"):
            for path in (root / directory).rglob("*.py"):
                with self.subTest(file=path.relative_to(root)):
                    self.assertIsNone(pattern.search(path.read_text()))
                    checked += 1
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main()
