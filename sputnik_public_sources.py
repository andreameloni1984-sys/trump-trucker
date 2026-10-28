"""Minimal, standard-library RSS/Atom parsing for public SPUTNIK sources."""
from __future__ import annotations
import hashlib
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urljoin

class _Text(HTMLParser):
    # RSS/Atom descriptions may embed HTML. Script/style and inert markup are
    # not public prose and must never become catalyst evidence.
    _SUPPRESSED_TAGS = frozenset({"script", "style", "noscript", "template"})

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self._suppressed_tags = []

    def handle_starttag(self, tag, attrs):
        tag = str(tag).lower()
        if tag in self._SUPPRESSED_TAGS:
            self._suppressed_tags.append(tag)

    def handle_endtag(self, tag):
        tag = str(tag).lower()
        if tag in self._SUPPRESSED_TAGS:
            for index in range(len(self._suppressed_tags) - 1, -1, -1):
                if self._suppressed_tags[index] == tag:
                    del self._suppressed_tags[index:]
                    break

    def handle_data(self, data):
        if self._suppressed_tags:
            return
        value = " ".join(data.split()).strip()
        if value:
            self.parts.append(value)

def clean_public_text(value):
    parser = _Text()
    parser.feed(str(value or ""))
    joined = " ".join(parser.parts).strip()
    # HTMLParser splits punctuation into separate data nodes; rejoin it.
    return re.sub(r"\s+([.,!?;:])", r"\1", joined)

def _name(tag):
    return str(tag).rsplit("}", 1)[-1].split(":")[-1].lower()

def _direct(node, names):
    for child in list(node):
        if _name(child.tag) in names:
            return child
    return None

def _text(node, names):
    child = _direct(node, names)
    return "".join(child.itertext()).strip() if child is not None else ""

def _link(node):
    """Choose an individual entry's alternate link, not Atom self/enclosure links."""
    candidates = []
    for child in list(node):
        if _name(child.tag) != "link":
            continue
        rel = str(child.attrib.get("rel") or "").strip().lower()
        if rel not in {"", "alternate"}:
            continue
        value = str(child.attrib.get("href") or "").strip() or "".join(child.itertext()).strip()
        if value:
            # Atom defaults a missing rel to "alternate"; explicit alternate links
            # are preferred when a feed also contains a link with no rel.
            priority = 0 if rel == "alternate" else 1
            candidates.append((priority, value))
    return min(candidates, key=lambda row: row[0])[1] if candidates else ""

def _descendant(node, names):
    for child in node.iter():
        if child is node or _name(child.tag) not in names:
            continue
        value = "".join(child.itertext()).strip()
        if value:
            return value
    return ""

def parse_public_feed(raw, base_url):
    """Return individual RSS 2.0 or Atom entries with source metadata."""
    try:
        root = ET.fromstring(raw)
    except (ET.ParseError, TypeError, ValueError) as exc:
        raise ValueError("Fonte pubblica priva di RSS/Atom XML valido") from exc
    if _name(root.tag) not in {"rss", "rdf", "feed"}:
        raise ValueError("Fonte pubblica priva di RSS/Atom XML valido")
    entries = [n for n in root.iter() if _name(n.tag) in {"item", "entry"}]
    result = []
    for index, entry in enumerate(entries):
        title = clean_public_text(_text(entry, {"title"}))
        body = clean_public_text(_text(entry, {"encoded", "description", "summary", "content"}))
        if not title and not body:
            continue
        raw_link = _link(entry)
        published = _text(entry, {"pubdate", "published", "updated", "date"})
        original = _descendant(entry, {"originalurl", "original_url", "truthoriginalurl"})
        if original:
            original = urljoin(base_url, original)
        # Never substitute the feed URL for an individual post permalink.
        # If the archive omits its own link but exposes the original public post,
        # that original URL is still a valid item-level destination.
        if raw_link:
            link = urljoin(base_url, raw_link)
        elif original:
            link = original
        else:
            continue
        identity = _text(entry, {"guid", "id"}) or link or hashlib.sha256(
            (title + "|" + published + "|" + body).encode("utf-8")
        ).hexdigest()
        result.append({
            "id": identity[:500], "title": title[:300], "text": body[:6000],
            "published": published[:100], "url": link[:1000],
            "primary_url": original[:1000], "feed_url": base_url[:1000],
            "item_index": str(index),
        })
    return result
