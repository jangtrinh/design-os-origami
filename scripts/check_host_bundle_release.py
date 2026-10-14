"""Run local mechanical release checks and both offline example workflows.

This is a local gate, not a hosted CI, host compatibility, physical or publication verdict.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser-cache', type=Path, required=True)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.evidence_dir.absolute()
    if output.exists() or output.is_symlink():
        parser.error('Evidence directory must be new')
    output.mkdir(parents=True)
    checks = []
    product_environment = os.environ.copy()
    product_environment['PYTHONPATH'] = os.pathsep.join([str(ROOT / 'src'), str(ROOT / 'tests')])
    product_environment['PYTHONDONTWRITEBYTECODE'] = '1'
    product_environment['ORIGAMI_BROWSER_CACHE'] = str(args.browser_cache.absolute())
    def run(label, command, cwd=ROOT):
        result = subprocess.run(command, cwd=cwd, env=product_environment, capture_output=True, text=True)
        (output / (label + '.log')).write_text(result.stdout + result.stderr)
        checks.append({'label': label, 'command': command, 'exit': result.returncode})
        print(label + ': exit ' + str(result.returncode), flush=True)
        return result.returncode == 0
    success = run('contract', [sys.executable, '-B', 'scripts/skill_contract.py', '--check'])
    success = run('sync', [sys.executable, '-B', 'scripts/sync_host_bundles.py', '--check']) and success
    # Explicit source import without needing a package install or ambient PYTHONPATH.
    tests = "import sys,unittest;sys.path[:0]=['src','tests'];r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover('tests'));sys.exit(not r.wasSuccessful())"
    success = run('tests', [sys.executable, '-B', '-c', tests]) and success
    skill = ROOT / 'skills/es-origami-cad'
    for slug in ('tuck-box-printer', 'hex-petal-presentation'):
        target = output / slug
        built = run(slug + '-build', [sys.executable, '-B', str(skill / 'build.py'), '--repo-root', str(ROOT), '--spec', str(skill / 'examples' / (slug + '.json')), '--output-dir', str(target)])
        checked = built and run(slug + '-validate', [sys.executable, '-B', str(skill / 'validate.py'), '--repo-root', str(ROOT), '--output-dir', str(target)])
        looked = checked and run(slug + '-look', [sys.executable, '-B', str(skill / 'look.py'), '--repo-root', str(ROOT), '--output-dir', str(target), '--browser-cache', str(args.browser_cache.absolute()), '--sheet', str(target / 'evidence/look-sheet.png')])
        success = looked and success
    receipt = {'schema_version': 1, 'ok': success, 'scope': 'local mechanical checks; human sheet inspection and actual host/CI qualification are separate', 'checks': checks}
    (output / 'release-checks.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
