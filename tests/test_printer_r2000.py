"""Public printer DXF regression and mutation-sensitive database contracts."""
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

from origami_cad.printer_profile_export import export_printer_dxf, resolve_spots
from origami_cad.printer_paths import with_bleed
from printer_dxf_structure import dump, one, tags, validate, values
from test_production_dieline_topology import MODELS


class PrinterR2000(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.cp = MODELS['tuck-box']()
        self.names = resolve_spots()

    def export(self, cp=None, names=None, bleed=3):
        target = self.root/'printer.dxf'
        text = export_printer_dxf(cp or self.cp, target, bleed, names)
        self.assertEqual(target.read_text(encoding='ascii'), text)
        return text

    def baseline(self):
        text = self.export()
        validate(text, self.names)  # Every corruption starts from a valid public artifact.
        return tags(text)

    def test_complete_database_all_real_models_and_overrides(self):
        overrides = {'cut': 'Knife Blue', 'glue': 'Adhesive'}
        names = resolve_spots(overrides)
        for model, factory in MODELS.items():
            for bleed in [0, 3, 8]:
                with self.subTest(model=model, bleed=bleed):
                    cp = factory()
                    _, _, exported = validate(self.export(cp, overrides, bleed), names)
                    expected = [(names[k], pts, closed) for k in names
                                for pts, closed in with_bleed(cp, bleed)[k]]
                    self.assertEqual(len(exported), len(expected))
                    for entity, (layer, pts, closed) in zip(exported, expected):
                        self.assertEqual(one(entity, 8), layer)
                        self.assertEqual(one(entity, 70), str(int(closed)))
                        coords = list(zip(map(float, values(entity, 10)),
                                          map(float, values(entity, 20))))
                        self.assertEqual(len(coords), len(pts), 'Source vertex count')
                        for (x, y), point in zip(coords, pts):
                            self.assertAlmostEqual(x, point.x, places=7)
                            self.assertAlmostEqual(y, -point.y, places=7)
                    cuts = [e for e in exported if one(e, 8) == names['cut']]
                    self.assertTrue(any(one(e, 70) == '1' for e in cuts))

    def test_duplicate_handle_rejected(self):
        pairs = self.baseline()
        start = pairs.index((0, 'LWPOLYLINE'))
        end = pairs.index((0, 'ENDSEC'), start)
        indices = [i for i in range(start, end) if pairs[i][0] == 5]
        pairs[indices[1]] = pairs[indices[0]]
        with self.assertRaisesRegex(AssertionError, 'Duplicate/zero handles'):
            validate(dump(pairs), self.names)

    def test_dangling_owner_rejected(self):
        pairs = self.baseline()
        i = pairs.index((0, 'LWPOLYLINE'))
        owner = next(j for j in range(i+1, len(pairs)) if pairs[j][0] == 330)
        pairs[owner] = (330, 'FFFFFF')
        with self.assertRaisesRegex(AssertionError, 'Polyline owner'):
            validate(dump(pairs), self.names)

    def test_missing_required_records_rejected(self):
        original = self.baseline()
        for kind, name in [('LTYPE', 'CONTINUOUS'), ('LAYER', '0'),
                           ('STYLE', 'STANDARD'), ('APPID', 'ACAD'),
                           ('DIMSTYLE', 'STANDARD'), ('BLOCK_RECORD', '*Paper_Space')]:
            with self.subTest(kind=kind):
                pairs = original[:]
                start = next(i for i in range(len(pairs)) if pairs[i] == (0, kind)
                             and (2, name) in pairs[i:next((j for j in range(i+1, len(pairs))
                                                          if pairs[j][0] == 0), len(pairs))])
                end = next(j for j in range(start+1, len(pairs)) if pairs[j][0] == 0)
                del pairs[start:end]
                with self.assertRaisesRegex(AssertionError, f'Required {kind} records'):
                    validate(dump(pairs), self.names)

    def test_missing_subclasses_and_boundaries_rejected(self):
        original = self.baseline()
        for marker in [(100, 'AcDbSymbolTable'), (100, 'AcDbPolyline'),
                       (100, 'AcDbDictionary'), (100, 'AcDbLayout'),
                       (0, 'ENDTAB'), (0, 'ENDSEC'), (0, 'EOF')]:
            with self.subTest(marker=marker):
                pairs = original[:]
                pairs.remove(marker)
                with self.assertRaises((AssertionError, ValueError)):
                    validate(dump(pairs), self.names)

    def test_low_handseed_rejected(self):
        pairs = self.baseline()
        i = pairs.index((9, '$HANDSEED'))+1
        pairs[i] = (5, '1')
        with self.assertRaisesRegex(AssertionError, 'Low HANDSEED'):
            validate(dump(pairs), self.names)

    def test_wrong_layout_relation_rejected(self):
        pairs = self.baseline()
        start = pairs.index((0, 'BLOCK_RECORD'))
        i = next(i for i in range(start, len(pairs)) if pairs[i][0] == 340)
        pairs[i] = (340, '0')
        with self.assertRaisesRegex(AssertionError, 'Reciprocal layout pointer'):
            validate(dump(pairs), self.names)

    def test_open_cut_and_wrong_vertex_count_rejected(self):
        original = self.baseline()
        start = original.index((0, 'LWPOLYLINE'))
        end = next(i for i in range(start+1, len(original)) if original[i][0] == 0)
        for code, value, reason in [(70, '0', 'Missing closed CUT contour'),
                                    (90, '1', 'Vertex count')]:
            with self.subTest(code=code):
                pairs = original[:]
                i = next(i for i in range(start, end) if pairs[i][0] == code)
                pairs[i] = (code, value)
                with self.assertRaisesRegex(AssertionError, reason):
                    validate(dump(pairs), self.names)

    @unittest.skipUnless(importlib.util.find_spec('ezdxf'),
                         'ezdxf not importable; optional recover/audit NOT RUN (no install)')
    def test_optional_ezdxf_recover_audit(self):
        from ezdxf import recover
        for factory in MODELS.values():
            text = self.export(factory())
            validate(text, self.names)
            doc, recovery = recover.read(io.BytesIO(text.encode('ascii')))
            self.assertFalse(recovery.errors)
            self.assertFalse(recovery.fixes, 'Recovery must not repair malformed output')
            audit = doc.audit()
            self.assertFalse(audit.errors)
            self.assertFalse(audit.fixes)


if __name__ == '__main__':
    unittest.main()
