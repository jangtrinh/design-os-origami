"""Missing essentials and unresolved public references must reject before output."""

import unittest

from public_snapshot_fixture import PublicSnapshotFixture, snapshot


class TestPublicSnapshotClosure(PublicSnapshotFixture):
    def publish(self, name, data):
        self.write(name, data)
        self.write_manifest()
        self.git("add", ".")

    def test_manifest_cannot_omit_mandatory_content(self):
        names = ("README.md", "LICENSE", "pyproject.toml", ".gitignore", "docs/index.html",
                 "docs/robots.txt", "docs/sitemap.xml", "docs/llms.txt", "src/origami_cad/cli.py")
        for name in names:
            with self.subTest(name=name):
                path = self.source / name
                data = path.read_bytes()
                path.unlink()
                self.write_manifest()
                self.git("add", "-u")
                self.reject()
                path.write_bytes(data)
                self.write_manifest()
                self.git("add", ".")

    def test_dangling_html_href_and_src_are_rejected(self):
        for attribute in ("href", "src"):
            with self.subTest(attribute=attribute):
                self.publish("docs/index.html", ('<a ' + attribute + '="missing.svg">asset</a>').encode())
                self.reject()

    def test_dangling_readme_markdown_and_html_are_rejected(self):
        for body in (b"[guide](docs/missing.md)", b"![image](docs/missing.png)",
                     b'<img src="docs/missing.png">', b"[guide][doc]\n\n[doc]: docs/missing.md"):
            with self.subTest(body=body):
                self.publish("README.md", body)
                self.reject()

    def test_link_to_omitted_internal_path_is_rejected(self):
        self.publish("docs/index.html", b'<a href="../plans/internal.md">private</a>')
        self.write("plans/internal.md", b"private")
        self.reject()

    def test_nested_html_and_encoded_escape_are_rejected(self):
        for url in ("../../../outside.txt", "%2e%2e/%2e%2e/%2e%2e/outside.txt"):
            with self.subTest(url=url):
                self.publish("docs/demo/example.html", ('<img src="' + url + '">').encode())
                self.reject()

    def test_missing_fragment_is_rejected(self):
        self.publish("docs/index.html", b'<a href="#absent">missing section</a>')
        self.reject()

    def test_manifest_duplicate_and_escape_are_rejected(self):
        manifest = self.source / "scripts/public_manifest.txt"
        valid = manifest.read_bytes()
        for extra in (b"docs/sample.txt\n", b"../outside.txt\n"):
            with self.subTest(extra=extra):
                manifest.write_bytes(valid + extra)
                self.reject()
        manifest.write_bytes(valid)

    def test_link_resolution_accepts_queries_fragments_and_root_paths(self):
        self.publish("docs/guide.html", b'<h2 id="section">Section</h2>')
        self.publish("docs/index.html", b'<a href="guide.html?view=1#section">guide</a>'
                     b'<img src="/assets/image.svg"><a href="https://example.com/absent">remote</a>')
        self.publish("docs/assets/image.svg", b"<svg/>")
        self.publish("README.md", b"[guide](docs/guide.html#section)\n![image](docs/assets/image.svg)\n"
                     b"[reference][doc]\n\n[doc]: docs/guide.html\n")
        result = snapshot.build_snapshot(self.source, self.output)
        self.assertEqual(result["scanner"], "PASS")


if __name__ == "__main__":
    unittest.main()
