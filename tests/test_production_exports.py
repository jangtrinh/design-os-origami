"""SVG semantic preservation and unchanged legacy geometry/DXF bytes."""

import hashlib
from pathlib import Path
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET

from origami_cad.dieline_export import export_dxf, export_svg
from origami_cad.geometry import CreaseType, OrigamiCreasePattern, Point2D

NS = {"svg": "http://www.w3.org/2000/svg"}


def export_pattern():
    cp = OrigamiCreasePattern("ExportPreservation", thickness_mm=0.5)
    for row, kind in enumerate(CreaseType):
        cp.add_crease(Point2D(-5, row * 10), Point2D(25, row * 10), kind)
    return cp


class TestProductionExports(unittest.TestCase):
    def svg(self, cp):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dieline.svg"
            content = export_svg(cp, str(path))
            self.assertEqual(path.read_text(), content)
            return content

    def test_default_svg_is_light_and_has_no_baked_text(self):
        cp = export_pattern()
        cp.name = '<untrusted & name>'
        root = ET.fromstring(self.svg(cp))
        self.assertEqual(root.get('style'), 'background:#FFFFFF;')
        self.assertEqual(root.findall('.//svg:text', NS), [])
        style = root.find('.//svg:style', NS).text
        for kind, colour in [('cut', '#FF0000'), ('crease', '#00FF00'),
                             ('perf', '#0000FF'), ('glue', '#FF00FF')]:
            self.assertRegex(style, r'\.' + kind + r'\s*\{\s*stroke:\s*' + colour)
        self.assertEqual(root.get('viewBox'), '0 0 60.00 80.00')
        self.assertEqual(len(root.findall('.//svg:line', NS)), len(cp.creases))

    def test_svg_preserves_perforation(self):
        cp = export_pattern()
        cp.add_crease(Point2D(20, 52), Point2D(-2, 52), CreaseType.PERFORATE)
        root = ET.fromstring(self.svg(cp))
        group = root.find(".//svg:g[@id='PERFORATE']", NS)
        self.assertIsNotNone(group, "PERFORATE group is missing")
        self.assertEqual(group.attrib["class"], "perf")
        lines = group.findall("svg:line", NS)
        self.assertEqual([line.attrib for line in lines], [
            {"x1": "15.00", "y1": "55.00", "x2": "45.00", "y2": "55.00"},
            {"x1": "40.00", "y1": "67.00", "x2": "18.00", "y2": "67.00"},
        ])
        self.assertEqual(len(root.findall(".//svg:line", NS)), len(cp.creases))

    def test_svg_preserves_fold_direction(self):
        root = ET.fromstring(self.svg(export_pattern()))
        lines = root.findall(".//svg:g[@id='CREASE']/svg:line", NS)
        self.assertEqual(len(lines), 3)
        self.assertEqual([line.get("data-fold") for line in lines],
                         [None, "mountain", "valley"])
        self.assertEqual([line.get("y1") for line in lines], ["45.00", "25.00", "35.00"])
        for group in ("CUT", "GLUE", "PERFORATE"):
            self.assertTrue(all(line.get("data-fold") is None for line in
                                root.findall(f".//svg:g[@id='{group}']/svg:line", NS)))

    def test_existing_geometry_bytes_are_preserved(self):
        svg = self.svg(export_pattern())
        blocks = [re.search(r'    <g id="' + name + r'".*?</g>', svg, re.S).group()
                  for name in ("CUT", "CREASE", "GLUE")]
        content = re.sub(r' data-fold="(?:mountain|valley)"', "", "\n".join(blocks))
        # Recorded before the exporter change; the digest covers exact group/line bytes.
        self.assertEqual(hashlib.sha256(content.encode()).hexdigest(),
                         "8049667e517f85881f68a10c3e998e436e3a45858a7221059a25393e318bdb2e")

    def test_dxf_bytes_and_layer_conventions_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dieline.dxf"
            content = export_dxf(export_pattern(), str(path))
            self.assertEqual(path.read_text(), content)
            self.assertEqual(hashlib.sha256(content.encode()).hexdigest(),
                             "217616de10b39ea702bd117f4a36de88fb2b4a8e0673ce422568fd8a395c642d")


if __name__ == "__main__":
    unittest.main()
