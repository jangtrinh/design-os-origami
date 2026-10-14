"""Generate/check the canonical source-bound tool contract."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from origami_cad.cli_contract import SKILL, render_contract


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    expected = render_contract(ROOT)
    path = ROOT / SKILL / 'contract.md'
    if args.check:
        if path.is_symlink() or not path.is_file() or path.read_bytes() != expected:
            print('contract: regenerate contract.md from the current product source', file=sys.stderr)
            return 1
        print('ok: contract')
    else:
        path.write_bytes(expected)
        print(path.relative_to(ROOT))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
