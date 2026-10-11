"""Public snapshot controls, with planted leaks and exact manifest assertions."""

import hashlib
from pathlib import Path
import unittest

from public_snapshot_fixture import PublicSnapshotFixture, SCRIPT, snapshot


class TestPublicSnapshot(PublicSnapshotFixture):
    def test_exact_allowlist_and_byte_hashes(self):
        expected = {p.relative_to(self.source).as_posix(): p.read_bytes()
                    for p in self.source.rglob("*") if p.is_file() and ".git" not in p.relative_to(self.source).parts}
        for name in ("plans/report.md", ".brv/node.md", "AGENTS.md", "CONTEXT.md", "HANDOFF.md",
                     "assets/model.svg", ".orca-state", "src/__pycache__/a.pyc", "tests/a.pyc",
                     "docs/evidence/probe.txt", "docs/proofs/probe.txt", "private-scripts/helper.py"):
            self.write(name, snapshot.PATH_SIGNATURES[0].encode())
        result = snapshot.build_snapshot(self.source, self.output)
        actual = {p.relative_to(self.output).as_posix(): p.read_bytes()
                  for p in self.output.rglob("*") if p.is_file()}
        self.assertEqual(actual, expected)
        self.assertEqual(result["scanner"], "PASS")
        self.assertEqual(result["scanned_files"], len(expected))
        self.assertEqual(result["leaks"], [])
        self.assertEqual([r["path"] for r in result["files"]], sorted(expected))
        for row in result["files"]:
            self.assertEqual(row["sha256"], hashlib.sha256(expected[row["path"]]).hexdigest())

    def test_every_forbidden_signature_in_text_and_binary(self):
        for signature in snapshot.PATH_SIGNATURES + snapshot.NAME_SIGNATURES:
            for wrapper in (lambda s: s, lambda s: b"\x00\xff" + s.upper() + b"\x00"):
                with self.subTest(signature=signature, binary=wrapper):
                    self.write("docs/sample.txt", wrapper(signature.encode()))
                    self.reject()
        self.write("docs/sample.txt", b"safe")

    def test_forbidden_filename_is_rejected(self):
        self.write("src/" + snapshot.NAME_SIGNATURES[0] + ".txt", b"safe")
        self.reject()

    def test_underscore_delimited_internal_names_are_rejected(self):
        for signature in snapshot.NAME_SIGNATURES[:4]:
            with self.subTest(signature=signature):
                self.write("docs/sample.txt", ("file_" + signature + "_report").encode())
                self.reject()

    def test_solver_is_not_a_person_name(self):
        self.assertEqual(snapshot.scan_bytes(b"solve solver resolution solar"), [])
        self.assertEqual(snapshot.scan_bytes(("hello " + snapshot.NAME_SIGNATURES[0] + "!").encode()),
                         [snapshot.NAME_SIGNATURES[0]])

    def test_missing_required_input_is_rejected(self):
        (self.source / "LICENSE").unlink()
        self.reject()

    def test_symlink_file_and_directory_are_rejected(self):
        for name in ("docs/linked.txt", "src/linked-dir"):
            with self.subTest(name=name):
                link = self.source / name
                link.symlink_to(self.base)
                self.reject()
                link.unlink()

    def test_linked_root_and_public_script_are_rejected(self):
        for name in ("README.md", "scripts/" + snapshot.PUBLIC_SCRIPTS[0]):
            with self.subTest(name=name):
                path = self.source / name
                data = path.read_bytes()
                path.unlink()
                path.symlink_to(self.base)
                self.reject()
                path.unlink()
                path.write_bytes(data)

    def test_existing_output_is_preserved(self):
        self.output.mkdir()
        sentinel = self.output / "keep.txt"
        sentinel.write_bytes(b"keep")
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.build_snapshot(self.source, self.output)
        self.assertEqual(sentinel.read_bytes(), b"keep")

    def test_output_inside_source_is_rejected(self):
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.build_snapshot(self.source, self.source / "out")
        self.assertFalse((self.source / "out").exists())

    def test_linked_output_parent_is_rejected(self):
        link = self.base / "alias"
        link.symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.build_snapshot(self.source, link / "public")
        self.assertFalse(self.output.exists())

    def test_scanner_and_test_source_are_not_exempt(self):
        self.assertEqual(snapshot.scan_bytes(SCRIPT.read_bytes()), [])
        self.assertEqual(snapshot.scan_bytes(Path(__file__).read_bytes()), [])
        self.write("scripts/" + snapshot.PUBLIC_SCRIPTS[0], snapshot.NAME_SIGNATURES[1].encode())
        self.reject()
        self.write("scripts/" + snapshot.PUBLIC_SCRIPTS[0], b"safe")
        self.write("tests/sample.txt", snapshot.NAME_SIGNATURES[1].encode())
        self.reject()


    def test_untracked_note_is_rejected(self):
        self.write("docs/unexpected-note.txt", b"innocuous private planning note")
        self.reject()

    def test_tracked_file_outside_manifest_is_rejected(self):
        self.write("docs/unexpected-note.txt", b"innocuous body")
        self.git("add", "docs/unexpected-note.txt")
        self.reject()

    def test_manifest_cannot_admit_an_untracked_file(self):
        self.write("docs/new-public.txt", b"safe content")
        self.write_manifest()
        self.reject()

    def test_credential_filename_is_rejected_even_if_manifested(self):
        for name in (".env.production", "private.pem", "private.key", "id_rsa.backup",
                     "access" + "token.txt", "service" + "secret.txt"):
            with self.subTest(name=name):
                path = self.write("docs/" + name, b"safe body")
                self.output = self.base / ("public-" + name)
                self.write_manifest()
                self.git("add", "-f", "docs/" + name, "scripts/public_manifest.txt")
                self.reject()
                path.unlink()
                self.git("add", "-u")
                self.write_manifest()

    def test_credential_strings_in_text_and_binary_are_rejected(self):
        values = ("-----BEGIN " + "PRIVATE KEY-----",
                  "AK" + "IA" + "A" * 16,
                  "gh" + "p_" + "A" * 36,
                  "github_" + "pat_" + "A" * 60,
                  "sk" + "-proj-" + "A" * 40,
                  "xox" + "b-" + "1" * 30,
                  "AI" + "za" + "A" * 35,
                  "api_" + "key = " + "A" * 24)
        for value in values:
            for prefix in (b"", b"\x00\xff"):
                with self.subTest(kind=value[:5], binary=bool(prefix)):
                    self.write("docs/sample.txt", prefix + value.encode())
                    self.output = self.base / ("public-" + str(values.index(value)) + str(len(prefix)))
                    self.reject()

if __name__ == "__main__":
    unittest.main()
