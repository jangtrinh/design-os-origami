"""Resolve public HTML/Markdown file references against captured snapshot bytes."""

from html.parser import HTMLParser
import json
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


def manifest_links(name, data):
    """Check local package sources and declared component paths; not MCP argv."""
    try:
        manifest = json.loads(data)
    except (ValueError, UnicodeError) as exc:
        raise SnapshotError(f"Malformed public manifest: {name}") from exc
    if not isinstance(manifest, dict):
        raise SnapshotError(f"Public manifest must be an object: {name}")
    if name.endswith('/marketplace.json'):
        links = []
        for entry in manifest.get('plugins', []):
            source = entry.get('source')
            if isinstance(source, dict):
                if source.get('source', source.get('type')) != 'local':
                    raise SnapshotError(f"Public marketplace source must be local: {name}")
                source = source.get('path')
            if not isinstance(source, str) or not source.startswith('./'):
                raise SnapshotError(f"Public marketplace path must start with ./ in {name}")
            links.append(source)
        return links
    links = []
    for field in ('skills', 'commands', 'agents', 'mcpServers', 'hooks', 'contextFileName'):
        value = manifest.get(field)
        if isinstance(value, str):
            links.append(value)
        elif isinstance(value, list):
            links.extend(item for item in value if isinstance(item, str))
    overlay = manifest.get('extensions', {}).get('com.openai', {})
    for field in ('apps', 'hooks', 'onboardingSkill'):
        if isinstance(overlay.get(field), str):
            links.append(overlay[field])
    return links


def validate_closure(payloads):
    """Validate the same bytes that will be copied, before staging any output."""
    files = {path.as_posix(): data for path, data in payloads}
    missing = set(MANDATORY) - files.keys()
    if missing:
        raise SnapshotError("Mandatory files missing: " + str(sorted(missing)))
    pages = {name: References(data.decode("utf-8")) for name, data in files.items()
             if name.startswith("docs/") and name.endswith(".html")}
    sources = {name: page.links for name, page in pages.items()}
    sources.update({name: markdown_links(data.decode("utf-8"))
                    for name, data in files.items() if name.endswith(".md")})
    for name, data in files.items():
        if name.endswith("/marketplace.json") or name.endswith("/plugin.json") or name.endswith("/gemini-extension.json"):
            sources[name] = manifest_links(name, data)
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
            elif name.endswith("/marketplace.json") and path:
                target = posixpath.normpath(path)
            elif (name.endswith(("/.claude-plugin/plugin.json", "/.codex-plugin/plugin.json", "/.factory-plugin/plugin.json")) or name in {".claude-plugin/plugin.json", ".codex-plugin/plugin.json", ".factory-plugin/plugin.json"}) and path:
                target = posixpath.normpath(str(PurePosixPath(name).parent.parent / path))
            elif path:
                target = posixpath.normpath(str(PurePosixPath(name).parent / path))
            else:
                target = name
            if target.endswith("/") or target == "docs" or target + "/index.html" in files:
                target = target.rstrip("/") + "/index.html"
            if target not in files and any(candidate.startswith(target.rstrip("/") + "/")
                                            for candidate in files):
                checked += 1
                continue
            if target not in files:
                raise SnapshotError(f"Unresolved local reference: {name} -> {link}")
            fragment = unquote(url.fragment)
            if fragment and target in pages and fragment not in pages[target].ids:
                raise SnapshotError(f"Missing local fragment: {name} -> {link}")
            checked += 1
    return checked
