"""Exact tracked-file selection and leak checks for the public snapshot."""

from fnmatch import fnmatchcase
import os
from pathlib import Path
import re
import subprocess

TREES = ("src", "tests", "docs", "knowledge", "skills")
ROOT_FILES = ("README.md", "LICENSE", "pyproject.toml", ".gitignore")
PUBLIC_SCRIPTS = ("build_public_snapshot.py", "e2e_figurative_gate.py",
                  "public_snapshot_policy.py", "public_snapshot_links.py", "public_manifest.txt")
MANIFEST = Path("scripts/public_manifest.txt")
EXCLUDED = {"plans", ".brv", "AGENTS.md", "CONTEXT.md", "HANDOFF.md", "__pycache__"}
# Fragment assembly lets the policy and its tests undergo the same raw-byte scan.
PATH_SIGNATURES = ("/Us" + "ers/", "/private/" + "tmp", "orca/" + "workspaces")
NAME_SIGNATURES = ("So" + "l", "As" + "tra", "Co" + "dex worker", "Hai" + "ku",
                   "gpt" + "-6", "Claude" + " handoff")
PATTERNS = tuple((s, re.compile(re.escape(s.encode()), re.I)) for s in PATH_SIGNATURES)
PATTERNS += tuple((s, re.compile(rb"(?<![A-Za-z0-9])" + re.escape(s.encode()) +
                                rb"(?![A-Za-z0-9])", re.I)) for s in NAME_SIGNATURES[:4])
PATTERNS += tuple((s, re.compile(re.escape(s.encode()), re.I)) for s in NAME_SIGNATURES[4:])
CREDENTIAL_NAMES = (".env*", "*.pem", "*.key", "id_rsa*", "*token*", "*secret*")
CREDENTIAL_PATTERNS = tuple((label, re.compile(pattern)) for label, pattern in (
    ("private-key", rb"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----"),
    ("cloud-access-key", rb"(?:AKIA|ASIA)[A-Z0-9]{16}"),
    ("source-access-key", rb"gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,}"),
    ("service-access-key", rb"sk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
    ("messaging-access-key", rb"xox[baprs]-[A-Za-z0-9-]{20,}"),
    ("cloud-api-key", rb"AIza[A-Za-z0-9_-]{35}"),
    ("credential-assignment", rb"(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)"
     rb"[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9_+/=-]{12,}"),
))


class SnapshotError(ValueError):
    """An unsafe or incomplete snapshot was rejected before writing output."""


def excluded(path):
    return any(part in EXCLUDED or part.startswith(".orca") or
               "evidence" in part.casefold() or part.casefold() in {"proof", "proofs"}
               for part in path.parts) or path.suffix.casefold() in {".pyc", ".pyo"}


def credential_name(path):
    return any(fnmatchcase(part.casefold(), pattern)
               for part in path.parts for pattern in CREDENTIAL_NAMES)


def scan_bytes(data):
    """Scan text and binary identically; report signature labels, never values."""
    return [label for label, pattern in PATTERNS + CREDENTIAL_PATTERNS if pattern.search(data)]


def tracked_paths(source):
    """Git membership is checked independently of the reviewed manifest."""
    try:
        top = subprocess.check_output(["git", "-C", str(source), "rev-parse", "--show-toplevel"],
                                      stderr=subprocess.DEVNULL)
        if Path(os.fsdecode(top).strip()).resolve() != source:
            raise SnapshotError("Source must be the tracked checkout root")
        data = subprocess.check_output(["git", "-C", str(source), "ls-files", "-z"],
                                       stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SnapshotError("Source must be a tracked Git checkout") from exc
    return {Path(os.fsdecode(name)) for name in data.split(b"\0") if name}


def public_path(path):
    return (path in map(Path, ROOT_FILES) or path.parts[0] in TREES or
            path.as_posix() in {"scripts/" + name for name in PUBLIC_SCRIPTS})


def collect(source):
    """Inventory detects unknown files; only manifest entries are ever copied."""
    manifest = source / MANIFEST
    if manifest.is_symlink() or not manifest.is_file():
        raise SnapshotError("Required regular manifest missing or linked")
    names = manifest.read_text(encoding="utf-8").splitlines()
    if not names or names != sorted(set(names)):
        raise SnapshotError("Manifest must contain sorted unique paths")
    selected = {Path(name) for name in names}
    for name, path in zip(names, (Path(name) for name in names)):
        if (path.is_absolute() or path.as_posix() != name or ".." in path.parts or
                not public_path(path) or excluded(path) or credential_name(path)):
            raise SnapshotError(f"Unsafe manifest path: {name}")
    if MANIFEST not in selected or not set(map(Path, ROOT_FILES)).issubset(selected):
        raise SnapshotError("Manifest omits required root files or itself")
    tracked = tracked_paths(source)
    if selected - tracked:
        raise SnapshotError("Untracked manifest files: " + str(sorted(map(str, selected - tracked))))
    seen = set()
    for path in source.iterdir():
        if credential_name(Path(path.name)):
            raise SnapshotError("Credential-like root filename")
    for name in (*TREES, "scripts"):
        root = source / name
        if root.is_symlink() or not root.is_dir():
            raise SnapshotError(f"Required directory missing or linked: {name}")
        for base, dirs, files in os.walk(root, followlinks=False):
            relbase = Path(base).relative_to(source)
            kept = []
            for child in sorted(dirs):
                rel = relbase / child
                if excluded(rel):
                    continue
                if (source / rel).is_symlink() or credential_name(rel):
                    raise SnapshotError(f"Unsafe directory: {rel.as_posix()}")
                kept.append(child)
            dirs[:] = kept
            for child in sorted(files):
                rel = relbase / child
                if excluded(rel):
                    continue
                if credential_name(rel):
                    raise SnapshotError("Credential-like filename")
                if rel not in tracked:
                    raise SnapshotError(f"Untracked public-area file: {rel.as_posix()}")
                if rel not in selected:
                    raise SnapshotError(f"Unexpected public-area file: {rel.as_posix()}")
                seen.add(rel)
    seen.update(map(Path, ROOT_FILES))
    if seen != selected:
        raise SnapshotError("Missing manifested files: " + str(sorted(map(str, selected - seen))))
    for rel in selected:
        path = source / rel
        if any(parent.is_symlink() for parent in [path, *path.parents] if parent != source.parent):
            raise SnapshotError(f"Linked selected path: {rel.as_posix()}")
        if not path.is_file():
            raise SnapshotError(f"Required regular file missing: {rel.as_posix()}")
    return sorted(selected, key=lambda p: p.as_posix())
