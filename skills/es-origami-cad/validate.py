"""Named checks: contract/input/artifact-files/artifact-receipt/svg-layers/
fold-metadata/topology/dxf-layers/printer-spots/printer-exchange/preview-status/
catalog-consistency/artifact-hashes. Offline, stdlib only; exit 0 ok/1 reject/2 unavailable.
"""
import argparse
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--catalog', type=Path, help='Optional index of recorded runs; never compare custom inputs to defaults')
    args = parser.parse_args()
    sys.path.insert(0, str(args.repo_root.resolve() / 'src'))
    try:
        from origami_cad.artifact_validation import validate, validate_catalog
        failures = validate(args.repo_root, args.output_dir)
        if not failures and args.catalog:
            failures = validate_catalog(args.repo_root, args.catalog)
    except (OSError, ImportError) as error:
        print('runtime: could not run: ' + str(error), file=sys.stderr)
        return 2
    if failures:
        print('\n'.join(failures))
        return 1
    print('ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
