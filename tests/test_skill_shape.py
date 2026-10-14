"""Mechanical tool-product shape and public reference closure."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/es-origami-cad'
sys.path.insert(0, str(ROOT / 'scripts'))
from public_snapshot_links import markdown_links, validate_closure
from public_snapshot_policy import SnapshotError

CHECKS = ('contract', 'input', 'artifact-files', 'artifact-receipt', 'svg-layers',
          'fold-metadata', 'topology', 'dxf-layers', 'printer-spots', 'printer-exchange',
          'preview-status', 'catalog-consistency', 'artifact-hashes')


class TestSkillShape(unittest.TestCase):
    def test_router_frontmatter_identity_and_line_limit(self):
        text = (SKILL / 'SKILL.md').read_text()
        self.assertLessEqual(len(text.splitlines()), 120)
        self.assertTrue(text.startswith('---\n'))
        frontmatter = text.split('---', 2)[1]
        self.assertRegex(frontmatter, r'(?m)^name: es-origami-cad$')
        description = re.search(r'(?m)^description: "(.*)"$', frontmatter)[1]
        self.assertTrue(description.startswith('Use when '))
        self.assertLessEqual(len(description), 200)
        self.assertIn('experimental-unqualified', frontmatter)

    def test_router_links_every_canonical_file(self):
        links = set(markdown_links((SKILL / 'SKILL.md').read_text()))
        required = {path.relative_to(SKILL).as_posix() for path in SKILL.rglob('*')
                    if path.is_file() and path.name != 'SKILL.md' and '__pycache__' not in path.parts}
        self.assertTrue(required.issubset(links), sorted(required - links))
        self.assertEqual(sorted(link for link in links if not (SKILL / link).is_file()), [])
        for link in sorted(links):
            self.assertFalse((SKILL / link).is_symlink(), link)

    def test_rules_have_rejection_homes_and_look_numbering(self):
        rules = (SKILL / 'rules.md').read_text()
        sections = re.split(r'(?m)^## \d+\. ', rules)[1:]
        self.assertEqual(len(sections), 14)
        for section in sections:
            for marker in ('Statement:', 'Keep it (API):', 'Rejected when:'):
                self.assertIn(marker, section)
        for name in CHECKS:
            self.assertIn('`' + name + '`', rules)
        look = (SKILL / 'look.md').read_text()
        for number in range(1, 10):
            self.assertIn('| L' + str(number) + ' |', look)
        self.assertIn('Without a browser', look)
        self.assertIn('PHYSICAL_FOLD_FIT: NOT VERIFIED.', look)

    def test_examples_are_complete_declarative_json(self):
        examples = sorted((SKILL / 'examples').glob('*.json'))
        self.assertGreaterEqual(len(examples), 2)
        for path in examples:
            data = path.read_bytes()
            self.assertLessEqual(len(data), 65536)
            self.assertLessEqual(len(data.splitlines()), 200)
            spec = json.loads(data)
            self.assertEqual(set(spec), {'schema_version', 'type', 'parameters', 'profiles',
                                         'printer', 'preview_requirement'})
            self.assertEqual(spec['schema_version'], 1)
            self.assertEqual(spec['preview_requirement'], 'available')

    def test_references_include_correct_wrong_choices_and_limits(self):
        for path in (SKILL / 'references').glob('*.md'):
            text = path.read_text()
            self.assertLess(len(text.splitlines()), 300)
            for required in ('Right:', 'Wrong:', 'When NOT to use', 'diagnostics'):
                self.assertIn(required.casefold(), text.casefold(), str(path))
        attribution = (SKILL / 'ATTRIBUTION.md').read_text()
        self.assertIn('Copyright (c) 2026 Lucas Marques', attribution)
        self.assertIn('Permission is hereby granted', attribution)

    def test_snapshot_hidden_roots_allow_only_exact_public_files(self):
        from public_snapshot_fixture import PublicSnapshotFixture, snapshot
        fixture = PublicSnapshotFixture()
        fixture.setUp()
        try:
            for name in ('\x2eagents/private.txt', '.github/private.txt', '.grok-plugin/private.txt'):
                path = fixture.write(name, b'public text')
                fixture.write_manifest()
                fixture.git('add', '.')
                with self.assertRaises(snapshot.SnapshotError):
                    snapshot.collect(fixture.source)
                path.unlink()
                fixture.write_manifest()
                fixture.git('add', '-u')
            for name in ('.agents/plugins/marketplace.json', '.claude-plugin/marketplace.json',
                         '.grok-plugin/marketplace.json', '.github/workflows/ci.yml'):
                fixture.write(name, b'{}')
            fixture.write_manifest()
            fixture.git('add', '.')
            selected = snapshot.collect(fixture.source)
            self.assertIn(Path('.github/workflows/ci.yml'), selected)
            self.assertIn(Path('.agents/plugins/marketplace.json'), selected)
        finally:
            fixture.doCleanups()

    def test_new_public_markdown_and_manifest_paths_close(self):
        def payload(extra):
            mandatory = {'README.md', 'LICENSE', 'pyproject.toml', '.gitignore', 'docs/index.html',
                         'docs/robots.txt', 'docs/sitemap.xml', 'docs/llms.txt', 'src/origami_cad/cli.py'}
            return [(Path(name), data) for name, data in
                    {**{name: b'plain' for name in mandatory}, **extra}.items()]
        for name in ('docs/ai-hosts/guide.md', 'skills/es-origami-cad/rules.md',
                     'bundles/gemini/GEMINI.md'):
            with self.assertRaises(SnapshotError):
                validate_closure(payload({name: b'[missing](absent.md)'}))
        marketplace = '.agents/plugins/marketplace.json'
        body = json.dumps({'plugins': [{'source': {'source': 'local', 'path': './bundles/codex'}}]}).encode()
        with self.assertRaises(SnapshotError):
            validate_closure(payload({marketplace: body}))
        self.assertGreater(validate_closure(payload({marketplace: body,
                           'bundles/codex/plugin.json': b'{"name":"example"}'})), 0)
