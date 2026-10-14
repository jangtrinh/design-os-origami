"""Local stdio launcher. No network transport or authentication service."""
import argparse
from pathlib import Path
import sys

from origami_cad.mcp_protocol import Protocol
from origami_cad.mcp_tools import ToolService


def main(repo):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True, type=Path)
    parser.add_argument('--browser-cache', type=Path)
    args = parser.parse_args()
    try:
        Protocol(ToolService(repo, args.workspace, args.browser_cache), sys.stdout).serve(sys.stdin.buffer)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    return 0
