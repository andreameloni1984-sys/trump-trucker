"""Small, defensive RSS/Atom parser for public SPUTNIK sources.

The parser keeps item-level provenance and refuses DTD/entity declarations so
untrusted feed XML cannot expand entities inside the collector.
"""
from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urljoin

MAX_FEED_BYTES = 2_000_000
_UNSAFE_XML = re.compile(br"<!\s*(?:DOCTYPE|ENTITY)\b", re.IGNORECASE)


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        value = " ".join(data.split()).strip()
        if value:
            self.parts.append(value)


def clean_public_text(value):
    parser = _Text()
    parser.feed(str(value or ""))
    return " ".join(parser.parts).strip()


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
    links = [child for child in list(node) if _name(child.tag) == "link"]
    if not links:
        return ""
    # Atom feeds may list self/enclosure links before the article permalink.
    links.sort(key=lambda child: (
        str(child.attrib.get("rel") or "alternate").lower() not in {"alternate", ""},
        not bool(str(child.attrib.get("href") or "").strip()),
    ))
    child = links[0]
    return str(child.attrib.get("href") or "").strip() or "".join(child.itertext()).strip()


def _descendant(node, names):
    for child in node.iter():
        if child is node or _name(child.tag) not in names:
            continue
        value = "".join(child.itertext()).strip()
        if value:
            return value
    return ""


def parse_public_feed(raw, base_url):
    """Return RSS 2.0 or Atom entries with stable IDs and original source URLs."""
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if not isinstance(raw, (bytes, bytearray)):
        raise ValueError("Contenuto feed non valido")
    if len(raw) > MAX_FEED_BYTES:
        raise ValueError("Feed pubblico oltre il limite di dimensione")
    if _UNSAFE_XML.search(bytes(raw)):
        raise ValueError("Dichiarazioni DTD/ENTITY non consentite nei feed pubblici")
    try:
        root = ET.fromstring(raw)
    except (ET.ParseError, TypeError, ValueError) as exc:
        raise ValueError("Fonte pubblica priva di RSS/Atom XML valido") from exc

    entries = [node for node in root.iter() if _name(node.tag) in {"item", "entry"}]
    result = []
    for index, entry in enumerate(entries):
        title = clean_public_text(_text(entry, {"title"}))
        body = clean_public_text(_text(entry, {"encoded", "description", "summary", "content"}))
        if not title and not body:
            continue
        link = _link(entry)
        link = urljoin(base_url, link) if link else base_url
        published = _text(entry, {"pubdate", "published", "updated", "date"})
        identity = _text(entry, {"guid", "id"}) or link or hashlib.sha256(
            (title + "|" + published + "|" + body).encode("utf-8")
        ).hexdigest()
        original = _descendant(entry, {"originalurl", "original_url", "truthoriginalurl"})
        if original:
            original = urljoin(base_url, original)
        result.append({
            "id": identity[:500],
            "title": title[:300],
            "text": body[:6000],
            "published": published[:100],
            "url": link[:1000],
            "primary_url": original[:1000],
            "feed_url": base_url[:1000],
            "item_index": str(index),
        })
    return result
