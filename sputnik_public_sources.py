"""Minimal, standard-library RSS/Atom parsing for public SPUTNIK sources."""
from __future__ import annotations
import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

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
    """Prefer an Atom alternate/permalink over self, enclosure or feed links."""
    links = [child for child in list(node) if _name(child.tag) == "link"]
    for child in links:
        rel = str(child.attrib.get("rel") or "alternate").strip().lower()
        href = str(child.attrib.get("href") or "").strip()
        if href and rel in {"alternate", ""}:
            return href
    for child in links:
        value = str(child.attrib.get("href") or "").strip() or "".join(child.itertext()).strip()
        if value:
            return value
    return ""


def _has_valid_publication_date(value):
    raw = str(value or "").strip()
    if not raw:
        return False
    iso_value = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        datetime.fromisoformat(iso_value)
        return True
    except (TypeError, ValueError):
        pass
    try:
        return parsedate_to_datetime(raw) is not None
    except (TypeError, ValueError, OverflowError):
        return False


def _is_individual_permalink(link, base_url):
    if not link:
        return False
    resolved = urljoin(base_url, link)
    parsed = urlsplit(resolved)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return False
    # A source homepage or feed endpoint is not an individual article/post.
    if not parsed.path or parsed.path.rstrip("/") == "":
        return False
    base = urlsplit(base_url)
    normalized_link = (parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/"), parsed.query)
    normalized_base = (base.scheme.lower(), base.netloc.lower(), base.path.rstrip("/"), base.query)
    return normalized_link != normalized_base

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
        raw_link = _link(entry)
        published = _text(entry, {"pubdate", "published", "updated", "date"})
        # Only keep a candidate that can be independently checked: title,
        # parseable publication date and a permalink to an individual item.
        if not title or not raw_link or not _has_valid_publication_date(published):
            continue
        link = urljoin(base_url, raw_link)
        if not _is_individual_permalink(link, base_url):
            continue
        identity = _text(entry, {"guid", "id"}) or link or hashlib.sha256(
            (title + "|" + published + "|" + body).encode("utf-8")
        ).hexdigest()
        original = _descendant(entry, {"originalurl", "original_url", "truthoriginalurl"})
        if original:
            original = urljoin(base_url, original)
        result.append({
            "id": identity[:500], "title": title[:300], "text": body[:6000],
            "published": published[:100], "url": link[:1000],
            "primary_url": original[:1000], "feed_url": base_url[:1000],
            "item_index": str(index),
        })
    return result
