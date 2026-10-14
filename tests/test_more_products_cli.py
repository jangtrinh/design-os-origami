"""Every new product exports the actual source blanks through both CLI profiles."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class TestMoreProductsCLI(unittest.TestCase):
    def test_new_types_export_one_file_per_blank(self):
        from origami_cad.product_registry import product_blanks
        for slug in ('fefco-0201', 'fefco-0427', 'sleeve-tray', 'food-box'):
            with self.subTest(slug=slug), tempfile.TemporaryDirectory() as directory:
                expected = product_blanks(slug, width=180, depth=125, height=65, thickness=.6)
                for profile, suffixes in (('presentation', ('.svg', '.dxf', '_viewer.html')),
                                           ('printer', ('_printer.pdf', '_printer.dxf'))):
                    result = subprocess.run([sys.executable, '-B', '-m', 'origami_cad.cli', 'generate',
                        '--type',slug,'--width','180','--depth','125','--height','65','--thickness','.6',
                        '--profile',profile,'--output-dir',directory],text=True,capture_output=True,
                        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
                    self.assertEqual(result.returncode,0,result.stderr)
                    for cp in expected:
                        for suffix in suffixes:
                            self.assertTrue((Path(directory)/(cp.name+suffix)).is_file())
                self.assertEqual(len(list(Path(directory).iterdir())),len(expected)*5)

    def test_sleeve_rejects_nonfinite_glue_flap_width(self):
        from origami_cad.packaging_sleeve_tray import generate_sleeve_tray
        for value in (float('inf'), float('nan'), '15'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                generate_sleeve_tray(glue_flap_width=value)

    def test_two_piece_names_and_registered_counts(self):
        from origami_cad.product_registry import PRODUCTS, catalog_blanks, product_blanks
        self.assertEqual(len(PRODUCTS),11)
        entries=catalog_blanks()
        self.assertEqual(len(entries),12)
        self.assertEqual(len({e['slug'] for e in entries}),12)
        self.assertEqual([e['part'] for e in entries if e['product']=='sleeve-tray'],['sleeve','tray'])
        self.assertEqual(len(product_blanks('sleeve-tray')),2)


if __name__ == '__main__':
    unittest.main()
