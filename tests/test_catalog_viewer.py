"""The switcher must publish actual model viewers with safe deep links."""
import json
from pathlib import Path
import re
import tempfile
import unittest

from origami_cad.packaging import generate_tuck_box, generate_gable_handle_box


class TestCatalogViewer(unittest.TestCase):
    def test_each_entry_gets_its_actual_geometry_and_deep_link(self):
        from origami_cad.catalog_viewer import generate_catalog_viewer
        entries = [{'slug': 'tuck-box', 'label': 'Tuck box', 'cp': generate_tuck_box()},
                   {'slug': 'gable-box', 'label': 'Gable box', 'cp': generate_gable_handle_box()}]
        with tempfile.TemporaryDirectory() as directory:
            page = generate_catalog_viewer(entries, directory)
            self.assertIn('aria-label="Choose a blank"', page)
            self.assertIn('index.html?model=gable-box', page)
            self.assertIn("Unknown blank", page)
            for entry in entries:
                text = (Path(directory)/(entry['slug']+'.html')).read_text()
                model = json.loads(re.search(r'<script id="fold-model" type="application/json">(.*?)</script>', text, re.S).group(1))
                from origami_cad.preview_model import build_preview_model
                self.assertEqual(model, build_preview_model(entry['cp']))
                self.assertIn(entry['cp'].name, text)
                self.assertIn('data-view="reset"', text)
            self.assertTrue((Path(directory)/'index.html').is_file())

    def test_malformed_slug_and_duplicate_are_rejected_before_write(self):
        from origami_cad.catalog_viewer import generate_catalog_viewer
        entry = {'slug': 'tuck-box', 'label': 'Tuck box', 'cp': generate_tuck_box()}
        with tempfile.TemporaryDirectory() as directory:
            for entries in ([entry, entry], [dict(entry, slug='../escape')], []):
                with self.subTest(entries=len(entries)), self.assertRaises(ValueError):
                    generate_catalog_viewer(entries, directory)
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
