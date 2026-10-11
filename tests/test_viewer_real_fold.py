"""Viewer contracts exercised with actual generated crease patterns."""
import json
import re
import tempfile
import unittest
from pathlib import Path

from origami_cad.fold_faces import build_fold_model
from origami_cad.packaging import generate_tuck_box, generate_miura_ori_sleeve
from origami_cad.figurative import generate_deer_bird_base
from origami_cad.geometry import OrigamiCreasePattern
from origami_cad.viewer_html import generate_viewer_html


def html_for(cp):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'nested' / 'viewer.html'
        html = generate_viewer_html(cp, str(path))
        assert path.read_text() == html
        return html


def model_from(html):
    match = re.search(r'<script id="fold-model" type="application/json">(.*?)</script>', html, re.S)
    if not match:
        raise AssertionError('Missing actual fold JSON')
    return json.loads(match.group(1))


class TestViewerRealFold(unittest.TestCase):
    def test_real_polygons_and_signed_hinges_round_trip(self):
        cp = generate_tuck_box()
        self.assertEqual(model_from(html_for(cp)), build_fold_model(cp))

    def test_dimensions_change_with_actual_source(self):
        small, large = generate_tuck_box(), generate_tuck_box(width=160, depth=90, height=200)
        self.assertNotEqual(model_from(html_for(small))['faces'], model_from(html_for(large))['faces'])
        for cp in (small, large):
            x0, y0, x1, y1 = cp.bounding_box()
            self.assertIn(f'Blank {x1-x0:g} × {y1-y0:g} mm', html_for(cp))

    def test_reference_theme_replaces_dark_mockup(self):
        html = html_for(generate_tuck_box())
        self.assertIn('--paper: #FFFFFF', html)
        self.assertIn('--ink: #232327', html)
        self.assertNotRegex(html, r'\b(?:const|let|var)\s+[WDH]\s*=')
        for old in ('#090d13', '#0d1117', 'mockup', 'telemetry', 'wireframe'):
            self.assertNotIn(old, html)

    def test_unsupported_patterns_and_bad_graph_remain_unavailable(self):
        for cp in (generate_miura_ori_sleeve(), generate_deer_bird_base(200), OrigamiCreasePattern('Bad')):
            html = html_for(cp)
            model = model_from(html)
            self.assertFalse(model['available'])
            self.assertEqual(model['faces'], [])
            self.assertEqual(model['status'], '3D fold preview not available for this pattern')
            self.assertIn(model['status'], html)
            self.assertIn('aria-disabled="true"', html)

    def test_name_is_html_escaped_and_cannot_end_a_script(self):
        cp = generate_tuck_box()
        cp.name = '</script><img src=x onerror="attack()"> & unsafe'
        html = html_for(cp)
        self.assertNotIn(cp.name, html)
        self.assertIn('&lt;/script&gt;', html)
        self.assertEqual(model_from(html), build_fold_model(cp))

    def test_model_metadata_json_cannot_inject_markup(self):
        cp = generate_tuck_box()
        cp.creases[0].label = '</script><script>attack()</script>'
        html = html_for(cp)
        self.assertEqual(model_from(html), build_fold_model(cp))
        self.assertNotIn('<script>attack()', html)

    def test_long_name_stays_complete_on_page_with_readable_tab_title(self):
        cp = generate_tuck_box()
        cp.name = 'Source-defined packaging model ' * 10
        html = html_for(cp)
        self.assertIn(f'<h1>{cp.name}</h1>', html)
        self.assertLess(len(re.search(r'<title>(.*?)</title>', html).group(1)), 100)

    def test_custom_controls_have_keyboard_and_motion_contract(self):
        html = html_for(generate_tuck_box())
        self.assertIn('role="slider"', html)
        self.assertIn('aria-valuenow="0"', html)
        self.assertNotIn('type="range"', html)
        for key in ('ArrowLeft', 'ArrowRight', 'Home', 'End', 'prefers-reduced-motion', 'pointerdown'):
            self.assertIn(key, html)
        self.assertIn('>Play</button>', html)
        self.assertIn('>Reset</button>', html)

    def test_preserves_source_and_technical_layer_colors(self):
        cp = generate_tuck_box()
        before = [(c.p1, c.p2, c.crease_type, c.target_angle_deg) for c in cp.creases]
        html = html_for(cp)
        self.assertEqual(before, [(c.p1, c.p2, c.crease_type, c.target_angle_deg) for c in cp.creases])
        self.assertIn('#FF0000', html)
        self.assertIn('#00FF00', html)

    def test_meaningful_fold_edges_have_contrasting_display_backing(self):
        from html.parser import HTMLParser
        class Lines(HTMLParser):
            def __init__(self):
                super().__init__(); self.rows = []
            def handle_starttag(self, tag, attrs):
                if tag == 'line': self.rows.append(dict(attrs))
        parsed = Lines(); html = html_for(generate_tuck_box()); parsed.feed(html)
        green = [row for row in parsed.rows if row.get('stroke') == '#00FF00']
        backing = [row for row in parsed.rows if row.get('data-presentation') == 'contrast']
        self.assertEqual(len(backing), len(green))
        self.assertTrue(backing)
        for color, outline in zip(green, backing):
            for key in ('x1', 'x2', 'y1', 'y2', 'stroke-dasharray'):
                self.assertEqual(color[key], outline[key])
            self.assertGreater(float(outline['stroke-width']), 0.9)
        def luminance(hex_color):
            channels = [int(hex_color[i:i+2], 16)/255 for i in (1, 3, 5)]
            linear = [c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in channels]
            return sum(c*w for c, w in zip(linear, (.2126, .7152, .0722)))
        def contrast(a, b):
            values = sorted((luminance(a), luminance(b)))
            return (values[1]+.05)/(values[0]+.05)
        for outline in backing:
            self.assertGreaterEqual(contrast(outline['stroke'], '#FFFFFF'), 3)
            self.assertGreaterEqual(contrast(outline['stroke'], '#00FF00'), 3)
        front, back, edge = re.findall(r"color: '(#[0-9A-F]{6})'", html)
        for background in ('#FFFFFF', front, back):
            self.assertGreaterEqual(contrast(edge, background), 3)


if __name__ == '__main__':
    unittest.main()
