"""Resolve public HTML/Markdown file references against captured snapshot bytes."""

from html.parser import HTMLParser
from pathlib import PurePosixPath
import posixpath
import re
from urllib.parse import unquote, urlsplit

from public_snapshot_policy import SnapshotError

MANDATORY = ("README.md", "LICENSE", "pyproject.toml", ".gitignore", "docs/index.html",
             "docs/robots.txt", "docs/sitemap.xml", "docs/llms.txt", "src/origami_cad/cli.py")


class References(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == "base":
            raise SnapshotError("Public HTML must not override its local URL base")
        for name, value in attrs:
            if name in {"href", "src"} and value is not None:
                self.links.append(value)
            if name == "id" and value:
                self.ids.add(value)

    handle_startendtag = handle_starttag


def markdown_links(text):
    # Code examples are not rendered links. Inline HTML is parsed separately.
    text = re.sub(r"(?ms)^ *(`{3,}|~{3,})[^\n]*\n.*?^ *\1[^\n]*(?:\n|$)", "", text)
    text = re.sub(r"(`+).*?\1", "", text)
    targets = re.findall(r"!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)", text)
    targets += re.findall(r"(?m)^ {0,3}\[[^\]\n]+\]:\s*(<[^>]+>|\S+)", text)
    return [target.strip("<>") for target in targets] + References(text).links


def validate_closure(payloads):
    """Validate the same bytes that will be copied, before staging any output."""
    files = {path.as_posix(): data for path, data in payloads}
    missing = set(MANDATORY) - files.keys()
    if missing:
        raise SnapshotError("Mandatory files missing: " + str(sorted(missing)))
    pages = {name: References(data.decode("utf-8")) for name, data in files.items()
             if name.startswith("docs/") and name.endswith(".html")}
    sources = {name: page.links for name, page in pages.items()}
    sources["README.md"] = markdown_links(files["README.md"].decode("utf-8"))
    checked = 0
    for name, links in sources.items():
        for link in links:
            try:
                url = urlsplit(link)
            except ValueError as exc:
                raise SnapshotError(f"Malformed reference in {name}") from exc
            if url.scheme in {"http", "https", "mailto", "tel", "data"} or url.netloc:
                continue
            if url.scheme or "\\" in url.path:
                raise SnapshotError(f"Unsupported local reference in {name}")
            path = unquote(url.path)
            if path.startswith("/"):
                target = posixpath.normpath("docs/" + path.lstrip("/"))
            elif path:
                target = posixpath.normpath(str(PurePosixPath(name).parent / path))
            else:
                target = name
            if target.endswith("/") or target == "docs" or target + "/index.html" in files:
                target = target.rstrip("/") + "/index.html"
            if target not in files:
                raise SnapshotError(f"Unresolved local reference: {name} -> {link}")
            fragment = unquote(url.fragment)
            if fragment and target in pages and fragment not in pages[target].ids:
                raise SnapshotError(f"Missing local fragment: {name} -> {link}")
            checked += 1
    return checked
