"""Run the checkout's offline look service using an explicitly prepared cache."""
import argparse
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--repo-root', required=True)
    args, _ = parser.parse_known_args()
    root = Path(args.repo_root).resolve()
    if not (root / 'src/origami_cad/look_harness.py').is_file():
        print('LOOK: NOT RUN — checkout capture runtime unavailable', file=sys.stderr)
        return 2
    sys.path.insert(0, str(root / 'src'))
    from origami_cad.look_harness import main as capture_main
    return capture_main()


if __name__ == '__main__':
    sys.exit(main())
