"""Minimal, standard-library RSS/Atom parsing for public SPUTNIK sources."""
from __future__ import annotations
import hashlib
import re
import xml.etree.ElementTree as ET
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
    child = _direct(node, {"link"})
    if child is None:
        return ""
    return str(child.attrib.get("href") or "").strip() or "".join(child.itertext()).strip()


def _descendant(node, names):
    for child in node.iter():
        if child is node or _name(child.tag) not in names:
            continue
        value = "".join(child.itertext()).strip()
        if value:
            return value
    return ""


def _safe_public_url(value, base_url):
    """Resolve a feed link only when it is a safe absolute HTTP(S) URL."""
    raw = str(value or "").strip()
    if not raw or "\\" in raw or any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in raw):
        return ""
    try:
        candidate = urljoin(base_url, raw)
        parsed = urlsplit(candidate)
        # Reject non-web schemes, missing hosts, and user-info URLs that can
        # disguise the actual destination in a Telegram/source citation.
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            return ""
        if parsed.username is not None or parsed.password is not None:
            return ""
    except (TypeError, ValueError):
        return ""
    return candidate


def parse_public_feed(raw, base_url):
    """Return individual RSS 2.0 or Atom entries with source metadata."""
    safe_base_url = _safe_public_url(base_url, base_url)
    if not safe_base_url:
        raise ValueError("URL del feed pubblico non valida: è richiesto HTTP/HTTPS")
    base_url = safe_base_url
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
        if raw_link:
            link = _safe_public_url(raw_link, base_url)
            # Do not turn a malicious or malformed item link into apparently
            # trustworthy public evidence by silently substituting the feed URL.
            if not link:
                continue
        else:
            link = base_url
        published = _text(entry, {"pubdate", "published", "updated", "date"})
        identity = _text(entry, {"guid", "id"}) or link or hashlib.sha256(
            (title + "|" + published + "|" + body).encode("utf-8")
        ).hexdigest()
        original = _descendant(entry, {"originalurl", "original_url", "truthoriginalurl"})
        if original:
            original = _safe_public_url(original, base_url)
        result.append({
            "id": identity[:500], "title": title[:300], "text": body[:6000],
            "published": published[:100], "url": link[:1000],
            "primary_url": original[:1000], "feed_url": base_url[:1000],
            "item_index": str(index),
        })
    return result
