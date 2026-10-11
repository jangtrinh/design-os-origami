"""Build a scanned, history-free public file snapshot with stdlib validation and tracked Git membership.

Usage: python3 scripts/build_public_snapshot.py --output-dir /tmp/public-snapshot
The destination must not exist. No repository or publication is created.
"""

import argparse
import hashlib
import json
from pathlib import Path
import tempfile


from public_snapshot_policy import (collect, scan_bytes, SnapshotError,
                                    ROOT_FILES, TREES, PUBLIC_SCRIPTS,
                                    PATH_SIGNATURES, NAME_SIGNATURES)
from public_snapshot_links import validate_closure


def build_snapshot(source, output):
    source = Path(source).resolve(strict=True)
    output = Path(output).absolute()
    resolved = output.resolve()
    if output.exists() or output.is_symlink():
        raise SnapshotError("Destination must not exist")
    if resolved == source or source in resolved.parents:
        raise SnapshotError("Destination must be outside the source tree")
    if not output.parent.is_dir() or output.parent.resolve() != output.parent:
        raise SnapshotError("Destination parent must exist without symlink components")
    selected = collect(source)
    payloads, rows, leaks = [], [], []
    for rel in selected:
        data = (source / rel).read_bytes()
        matches = scan_bytes(rel.as_posix().encode()) + scan_bytes(data)
        if matches:
            leaks.append({"file": rel.as_posix(), "signatures": sorted(set(matches))})
        payloads.append((rel, data))
        rows.append({"path": rel.as_posix(), "bytes": len(data),
                     "sha256": hashlib.sha256(data).hexdigest()})
    if leaks:
        raise SnapshotError("Public scan rejected selected files: " + json.dumps(leaks, sort_keys=True))
    checked_links = validate_closure(payloads)
    with tempfile.TemporaryDirectory(prefix="public-build-", dir=output.parent) as tmp:
        staging = Path(tmp) / "snapshot"
        staging.mkdir()
        for rel, data in payloads:
            dest = staging / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        # Refuse a destination that appeared during validation/copying.
        if output.exists() or output.is_symlink():
            raise SnapshotError("Destination appeared during the build")
        staging.rename(output)
    return {"scanner": "PASS", "scanned_files": len(rows), "leaks": [], "files": rows,
            "publication": "NOT RUN", "history": "none", "local_references": checked_links}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build_snapshot(args.source_root, args.output_dir)
    except (SnapshotError, OSError) as exc:
        parser.exit(1, f"Snapshot rejected: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
