"""Public counts, source-derived assets and the switcher must agree on actual blanks."""
import hashlib
import json
from pathlib import Path
import re
import unittest


class TestPublicProducts(unittest.TestCase):
    def test_catalog_and_switcher_bind_to_each_actual_source_blank(self):
        from origami_cad.product_registry import catalog_blanks
        from origami_cad.preview_model import build_preview_model
        from origami_cad.preview_recording import preview_records_match
        root=Path(__file__).resolve().parents[1]
        rows=json.loads((root/'docs/assets/catalog.json').read_text())
        expected=catalog_blanks()
        self.assertEqual({r['slug'] for r in rows},{e['slug'] for e in expected})
        index=(root/'docs/demo/index.html').read_text()
        choices=json.loads(re.search(r'<script id="blank-choices" type="application/json">(.*?)</script>',index,re.S).group(1))
        self.assertEqual({r['slug'] for r in choices},{r['slug'] for r in rows})
        for entry in expected:
            row=next(r for r in rows if r['slug']==entry['slug']);cp=entry['cp']
            model=build_preview_model(cp)
            self.assertEqual(row['source_name'],cp.name)
            self.assertEqual(row['preview_available'],model['available'])
            choice=next(r for r in choices if r['slug']==entry['slug'])
            self.assertEqual(choice['available'],model['available'])
            text=(root/'docs/demo'/choice['file']).read_text()
            actual=json.loads(re.search(r'<script id="fold-model" type="application/json">(.*?)</script>',text,re.S).group(1))
            self.assertTrue(preview_records_match(actual,model,cp), entry['slug'])
            for filename in row['files'].values():self.assertTrue((root/'docs'/filename).is_file())

    def test_public_headline_counts_and_source_manifest(self):
        root=Path(__file__).resolve().parents[1]
        rows=json.loads((root/'docs/assets/catalog.json').read_text())
        heading=f"{len(rows)} blanks. {sum(r['preview_available'] for r in rows)} with 3D."
        self.assertTrue((root/'README.md').read_text().startswith('# '+heading+'\n'))
        site=(root/'docs/index.html').read_text()
        h1=re.search(r'<h1 id="proposition">(.*?)</h1>',site,re.S).group(1)
        self.assertEqual(re.sub(r'<[^>]+>','',h1),heading)
        expected={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((root/'src/origami_cad').glob('*.py'))}
        self.assertEqual(json.loads((root/'docs/assets/source-manifest.json').read_text()),expected)


if __name__ == '__main__':
    unittest.main()
