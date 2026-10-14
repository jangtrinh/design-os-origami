"""Start the clone-local bounded stdio MCP server; Python stdlib only."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from origami_cad.mcp_server import main

if __name__ == '__main__':
    raise SystemExit(main(ROOT))
