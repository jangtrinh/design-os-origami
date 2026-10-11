"""Dedicated spot names must not invoke PDF all/none/process semantics."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from origami_cad.packaging import generate_tuck_box
from origami_cad.printer_profile_export import export_printer_pdf, export_printer_dxf, DEFAULT_SPOTS

RESERVED = ['None', 'All', 'Cyan', 'Magenta', 'Yellow', 'Black']
INVALID = ['', ' ', '\t\n', 'Ink/Other', 'Ink#ZZ', '(Ink)', 'Ink\x00', 'Ink☃']


class PrinterColorants(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.cp = generate_tuck_box()

    def test_export_rejects_reserved_and_invalid_colorants(self):
        for kind in DEFAULT_SPOTS:
            for index,name in enumerate(RESERVED + [n.lower() for n in RESERVED] + INVALID):
                for export in [export_printer_pdf, export_printer_dxf]:
                    target = self.root/f'{kind}-{index}-{export.__name__}.out'
                    with self.subTest(kind=kind,name=name,export=export.__name__):
                        with self.assertRaises(ValueError):
                            export(self.cp,target,spot_names={kind:name})
                        self.assertFalse(target.exists(),'Invalid names must refuse before writing')

    def test_cli_rejects_reserved_invalid_and_duplicate_names(self):
        base = [sys.executable,'-m','origami_cad.cli','generate','--profile','printer']
        cases = [([f'--spot-{kind}',name],'reserved') for kind in DEFAULT_SPOTS for name in RESERVED]
        cases += [(['--spot-cut',name],'Spot') for name in INVALID if '\x00' not in name]
        cases += [(['--spot-cut','CreaseLine'],'unique')]
        for index,(args,message) in enumerate(cases):
            case = self.root/f'case-{index}'
            with self.subTest(args=args):
                result = subprocess.run(base+['--output-dir',str(case)]+args,capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0)
                self.assertIn(message,result.stderr)
                self.assertFalse(list(case.iterdir()),'Refusal must not create output files')

    def test_shared_validation_precedes_both_exporters(self):
        for index,invalid in enumerate([{'cut':'None'},{'cut':'All'},{'cut':'CreaseLine'},
                        {'cut':'creaseline'},{'cut':' '},{'cut':'Name/'},{'cut':'Name#GG'}]):
            for export in [export_printer_pdf,export_printer_dxf]:
                with self.subTest(invalid=invalid,export=export.__name__):
                    with self.assertRaises(ValueError):
                        export(self.cp,self.root/f'bad-{index}-{export.__name__}',spot_names=invalid)
                    self.assertFalse((self.root/f'bad-{index}-{export.__name__}').exists())
