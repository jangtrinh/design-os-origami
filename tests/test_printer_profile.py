"""Printer profile contracts checked directly in PDF/DXF bytes and coordinates."""
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from test_production_dieline_topology import MODELS
from origami_cad.geometry import Point2D, CreaseType
from origami_cad.printer_profile_export import export_printer_pdf, export_printer_dxf, DEFAULT_SPOTS
from origami_cad.printer_paths import printer_paths, bleed_outline, signed_area

PT = 72 / 25.4


def objects(pdf):
    start = int(re.search(rb'startxref\n(\d+)\n', pdf).group(1))
    assert pdf[start:start+4] == b'xref'
    entries = pdf[start:].splitlines()
    count = int(entries[1].split()[1])
    offsets = [int(line[:10]) for line in entries[3:count+2]]
    out = []
    for i, offset in enumerate(offsets, 1):
        assert pdf[offset:].startswith(f'{i} 0 obj\n'.encode())
        end = pdf.index(b'endobj', offset)
        out.append(pdf[offset:end])
    return out


def dxf_entities(text):
    lines = text.splitlines()
    pairs = list(zip(lines[::2], lines[1::2]))
    entities, current = [], None
    for code, value in pairs:
        if code == '0':
            if current is not None: entities.append(current)
            current = [] if value == 'LWPOLYLINE' else None
        elif current is not None:
            current.append((code, value))
    return pairs, entities


class PrinterProfile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.cp = MODELS['tuck-box']()

    def test_pdf_valid_xref_spots_scale_stroke_and_legend(self):
        pdf = export_printer_pdf(self.cp, self.root/'printer.pdf')
        self.assertEqual(pdf, (self.root/'printer.pdf').read_bytes())
        self.assertTrue(pdf.startswith(b'%PDF-1.4'))
        objs = objects(pdf)
        self.assertEqual(len(re.findall(rb'/Separation /([^ ]+)',pdf)),5)
        self.assertEqual(set(re.findall(rb'/Separation /([^ ]+)',pdf)),{n.encode() for n in DEFAULT_SPOTS.values()})
        content = next(o for o in objs if b'\nstream\n' in o)
        stream = content.split(b'\nstream\n',1)[1].split(b'endstream',1)[0]
        self.assertEqual(int(re.search(rb'/Length (\d+)',content).group(1)),len(stream))
        self.assertEqual(re.findall(rb'([\d.]+) w\b',stream),[b'1'])
        self.assertNotIn(b' cm',stream)  # Unit CTM keeps1 w exactly1pt.
        coordinates = [(float(x),float(y)) for x,y in re.findall(rb'([\d.]+) ([\d.]+) [ml]\b',stream)]
        cuts = printer_paths(self.cp)['cut'][0][0]
        for (x1,y1),(x2,y2),p,q in zip(coordinates,coordinates[1:],cuts,cuts[1:]):
            self.assertAlmostEqual(x2-x1,(q.x-p.x)*PT,places=6)
            self.assertAlmostEqual(y2-y1,-(q.y-p.y)*PT,places=6)
        self.assertNotIn(b'/Image',pdf)
        self.assertNotIn(b' rg',stream)
        # Source paths precede legend; text must lie below every die point.
        die_bottom = min(y for _,y in coordinates[:-10])
        text_y = [float(y) for y in re.findall(rb'1 0 0 1 [\d.]+ ([\d.]+) Tm',stream)]
        self.assertEqual(len(text_y),5)
        self.assertLess(max(text_y),die_bottom)
        self.assertIn(b'h\nS',stream)

    def test_bleed_edges_are_parallel_outward_offsets(self):
        paths = printer_paths(self.cp)
        outer = max((pts for pts,closed in paths['cut'] if closed),key=lambda pts:abs(sum(a.x*b.y-b.x*a.y for a,b in zip(pts,pts[1:]+pts[:1]))))
        for distance in [0,3,8]:
            bleed = bleed_outline(outer,distance)
            for p,q in zip(bleed,bleed[1:]+bleed[:1]):
                matches=[]
                for a,b in zip(outer,outer[1:]+outer[:1]):
                    dx,dy=b.x-a.x,b.y-a.y
                    values=[(dx*(v.y-a.y)-dy*(v.x-a.x))/math.hypot(dx,dy) for v in [p,q]]
                    if all(abs(v + math.copysign(distance, signed_area(outer))) < 0.01 for v in values):
                        matches.append(values)
                self.assertTrue(matches,'Every surviving bleed edge lies on a parallel offset CUT edge')

    def test_bleed_contains_original_blank(self):
        def inside(p, polygon):
            hit = False
            for a,b in zip(polygon,polygon[1:]+polygon[:1]):
                dx,dy=b.x-a.x,b.y-a.y
                cross=dx*(p.y-a.y)-dy*(p.x-a.x)
                if abs(cross)<1e-6 and min(a.x,b.x)-1e-6<=p.x<=max(a.x,b.x)+1e-6 and min(a.y,b.y)-1e-6<=p.y<=max(a.y,b.y)+1e-6:return True
                if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:hit=not hit
            return hit
        for name,fn in MODELS.items():
            outer=max((p for p,c in printer_paths(fn())['cut'] if c),key=lambda p:abs(signed_area(p)))
            for distance in [0,3,8,20]:
                bleed=bleed_outline(outer,distance)
                for a,b in zip(outer,outer[1:]+outer[:1]):
                    for p in [a,Point2D((a.x+b.x)/2,(a.y+b.y)/2)]:
                        with self.subTest(model=name,bleed=distance,point=p):self.assertTrue(inside(p,bleed))

    def test_bleed_clearance_at_original_cut_vertices(self):
        def distance(p,a,b):
            dx,dy=b.x-a.x,b.y-a.y
            t=max(0,min(1,((p.x-a.x)*dx+(p.y-a.y)*dy)/(dx*dx+dy*dy)))
            return math.hypot(p.x-a.x-t*dx,p.y-a.y-t*dy)
        for name,fn in MODELS.items():
            outer=max((p for p,c in printer_paths(fn())['cut'] if c),key=lambda p:abs(signed_area(p)))
            for amount in [3,8,20]:
                bleed=bleed_outline(outer,amount)
                for p in outer:
                    clearance=min(distance(p,a,b) for a,b in zip(bleed,bleed[1:]+bleed[:1]))
                    with self.subTest(model=name,bleed=amount):self.assertGreaterEqual(clearance,amount-0.01)

    def test_bleed_has_no_self_crossings(self):
        from dieline_topology import crossing
        from types import SimpleNamespace
        for name,fn in MODELS.items():
            for distance in [0,3,8]:
                paths=printer_paths(fn())
                outer=max((pts for pts,closed in paths['cut'] if closed),key=lambda pts:abs(sum(a.x*b.y-b.x*a.y for a,b in zip(pts,pts[1:]+pts[:1]))))
                pts=bleed_outline(outer,distance)
                edges=[SimpleNamespace(p1=a,p2=b) for a,b in zip(pts,pts[1:]+pts[:1])]
                for i,a in enumerate(edges):
                    for j,b in enumerate(edges[i+2:],i+2):
                        if i==0 and j==len(edges)-1:continue
                        with self.subTest(model=name,bleed=distance,pair=(i,j)):
                            self.assertIsNone(crossing(a,b))

    def test_dxf_units_mirror_and_closed_cut(self):
        text=export_printer_dxf(self.cp,self.root/'printer.dxf')
        pairs,entities=dxf_entities(text)
        self.assertIn(('1','AC1015'),pairs)
        self.assertIn(('9','$INSUNITS'),pairs)
        self.assertIn(('70','4'),pairs)
        self.assertIn(('9','$MEASUREMENT'),pairs)
        self.assertIn(('70','1'),pairs)
        closed=[e for e in entities if ('8','CutContour') in e and ('70','1') in e]
        self.assertTrue(closed)
        exported={(round(float(x),6),round(float(y),6)) for e in entities if ('8','CutContour') in e
                  for x,y in zip([v for k,v in e if k=='10'],[v for k,v in e if k=='20'])}
        source={(round(p.x,6),round(-p.y,6)) for c in self.cp.creases if c.crease_type==CreaseType.CUT for p in [c.p1,c.p2]}
        self.assertEqual(exported,source)

    def test_every_packaging_model_exports(self):
        for name,f in MODELS.items():
            with self.subTest(model=name):
                cp=f()
                objects(export_printer_pdf(cp,self.root/(name+'.pdf')))
                _,entities=dxf_entities(export_printer_dxf(cp,self.root/(name+'.dxf')))
                self.assertTrue(any(('8','CutContour') in e and ('70','1') in e for e in entities))

    def test_spot_overrides_validation_and_parameters(self):
        custom={'cut':'Knife Blue'}
        pdf=export_printer_pdf(self.cp,self.root/'custom.pdf',bleed_mm=8,spot_names=custom)
        self.assertIn(b'/Separation /Knife#20Blue',pdf)
        self.assertIn('Knife Blue',export_printer_dxf(self.cp,self.root/'custom.dxf',spot_names=custom))
        for invalid in [-1,float('nan'),float('inf'),1e308]:
            for exporter in [export_printer_pdf,export_printer_dxf]:
                with self.assertRaises(ValueError): exporter(self.cp,self.root/'bad.out',bleed_mm=invalid)
        for bad in [{'cut':'CreaseLine'},{'cut':'bad\n0'},{'unknown':'Ink'}]:
            with self.assertRaises(ValueError): export_printer_pdf(self.cp,self.root/'bad.pdf',spot_names=bad)

    def test_cli_additive_and_default_unchanged(self):
        base=[sys.executable,'-m','origami_cad.cli','generate','--output-dir',str(self.root)]
        result=subprocess.run(base+['--profile','printer','--spot-cut','Knife','--bleed-mm','8'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(len(list(self.root.glob('*_printer.pdf'))),1)
        self.assertEqual(len(list(self.root.glob('*_printer.dxf'))),1)
        self.assertFalse(list(self.root.glob('*.svg')))
        self.assertEqual(subprocess.run(base,capture_output=True).returncode,0)
        self.assertEqual(len(list(self.root.glob('*.svg'))),1)
        self.assertEqual(len(list(self.root.glob('*_viewer.html'))),1)
