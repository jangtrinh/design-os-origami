"""Build a real, complete artifact set from a bounded declarative specification."""
import argparse
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', required=True, type=Path)
    parser.add_argument('--spec', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repo_root.resolve() / 'src'))
    try:
        from origami_cad.artifact_workflow import read_spec, build
        build(args.repo_root, read_spec(args.spec), args.output_dir)
    except (OSError, ImportError) as error:
        print('build: could not run: ' + str(error), file=sys.stderr)
        return 2
    except (ValueError, TypeError, OverflowError) as error:
        print('build: ' + str(error), file=sys.stderr)
        return 1
    print(args.output_dir.absolute())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
