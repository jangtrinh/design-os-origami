"""Regression controls for independent review's R2000 false-green findings."""
import unittest
from unittest.mock import patch
from printer_dxf_structure import dump, one, records, tags, validate
import test_printer_r2000
from origami_cad.printer_r2000 import r2000_document


class R2000ReviewControls(unittest.TestCase):
    def test_wrong_typed_and_dangling_references_refuse(self):
        case = test_printer_r2000.PrinterR2000()
        case.setUp()
        self.addCleanup(case.doCleanups)
        original = case.baseline()
        model = next(r for r in records(original[original.index((0, 'TABLE')):])
                     if r[0] == (0, 'BLOCK_RECORD') and (2, '*Model_Space') in r)
        target = one(model, 5)
        for fault, reason in [('layout', 'Layout references'),
                              ('dimstyle', 'DIMSTYLE text style'),
                              ('dangling', 'Dangling handle reference')]:
            with self.subTest(fault=fault):
                pairs = original[:]
                if fault == 'layout':
                    start = pairs.index((0, 'LAYOUT'))
                    index = next(i for i in range(start+1, len(pairs)) if pairs[i][0] == 330)
                    pairs[index] = (330, target)
                elif fault == 'dimstyle':
                    start = pairs.index((0, 'DIMSTYLE'))
                    index = next(i for i in range(start+1, len(pairs)) if pairs[i][0] == 340)
                    pairs[index] = (340, target)
                else:
                    pairs.insert(pairs.index((0, 'LWPOLYLINE'))+2, (331, 'FFFFFF'))
                with self.assertRaisesRegex(AssertionError, reason):
                    validate(dump(pairs), case.names)

    def test_geometry_contract_detects_truncated_crease(self):
        def truncate(paths, names):
            pairs = tags(r2000_document(paths, names))
            for i, pair in enumerate(pairs):
                if pair != (0, 'LWPOLYLINE'):
                    continue
                end = next(j for j in range(i+1, len(pairs)) if pairs[j][0] == 0)
                if (8, names['crease']) not in pairs[i:end]:
                    continue
                count = next(j for j in range(i+1, end) if pairs[j][0] == 90)
                x = max(j for j in range(i+1, end) if pairs[j][0] == 10)
                del pairs[x:x+2]
                pairs[count] = (90, str(int(pairs[count][1])-1))
                return dump(pairs)
            raise AssertionError('Mutation never reached a crease')
        case = test_printer_r2000.PrinterR2000('test_complete_database_all_real_models_and_overrides')
        result = unittest.TestResult()
        with patch('origami_cad.printer_r2000.r2000_document', truncate):
            case.run(result)
        self.assertFalse(result.errors, result.errors)
        self.assertFalse(result.wasSuccessful(), 'Truncated crease escaped geometry contract')
        self.assertTrue(all('Source vertex count' in failure for _, failure in result.failures),
                        result.failures)
