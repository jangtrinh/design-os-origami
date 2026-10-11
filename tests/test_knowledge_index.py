"""Knowledge catalogue digests must bind to the current published bytes."""

import hashlib
import json
from pathlib import Path
import unittest


class TestKnowledgeIndex(unittest.TestCase):
    def test_every_index_hash_matches_its_file(self):
        root = Path(__file__).resolve().parents[1] / "knowledge"
        entries = json.loads((root / "index.json").read_text())
        self.assertTrue(entries)
        self.assertEqual(len({row["id"] for row in entries}), len(entries))
        self.assertEqual(len({row["path"] for row in entries}), len(entries))
        for row in entries:
            with self.subTest(entry=row["id"]):
                path = (root / row["path"]).resolve()
                self.assertIn(root.resolve(), path.parents)
                self.assertEqual(row["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
