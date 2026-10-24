"""Minimal, standard-library RSS/Atom parsing for public SPUTNIK sources."""
from __future__ import annotations
import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

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


def parse_publication_datetime(value):
    """Parse ISO-8601/RFC-2822 publication dates and normalize them to UTC."""
    raw = str(value or "").strip()
    if not raw:
        return None
    iso_value = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(iso_value)
    except (TypeError, ValueError):
        try:
            parsed = parsedate_to_datetime(raw)
        except (TypeError, ValueError, OverflowError):
            return None
    if parsed is None:
        return None
    # A timestamp without an explicit zone is treated as UTC, never as the
    # runner's local timezone, so freshness decisions remain deterministic.
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _has_valid_publication_date(value):
    return parse_publication_datetime(value) is not None


def publication_is_recent(value, now=None, max_age_hours=72, future_skew_minutes=10):
    """Return False for unparseable, stale, or implausibly future-dated items."""
    published_at = parse_publication_datetime(value)
    if published_at is None:
        return False
    try:
        age_limit = float(max_age_hours)
        future_limit = float(future_skew_minutes)
    except (TypeError, ValueError, OverflowError):
        return False
    if not 1 <= age_limit <= 24 * 30 or not 0 <= future_limit <= 60:
        return False
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    current = current.astimezone(timezone.utc)
    age = current - published_at
    return timedelta(minutes=-future_limit) <= age <= timedelta(hours=age_limit)


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


_TRACKING_QUERY_KEYS = {
    "fbclid", "gclid", "dclid", "mc_cid", "mc_eid", "ref_src",
    "igshid", "vero_id", "oly_anon_id", "oly_enc_id",
}


def canonical_public_item_url(value):
    """Normalize an individual public-item URL for cross-feed deduplication."""
    parsed = urlsplit(str(value or "").strip())
    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"} or not parsed.hostname:
        return ""
    if parsed.username is not None or parsed.password is not None:
        return ""
    try:
        port = parsed.port
    except ValueError:
        return ""
    host = parsed.hostname.lower()
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/":
        path = path.rstrip("/")
    query = [
        (key, val)
        for key, val in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in _TRACKING_QUERY_KEYS
    ]
    return urlunsplit((scheme, host, path, urlencode(sorted(query)), ""))


def public_item_identity(item):
    """Return an identity independent of which feed carried the same item."""
    primary = canonical_public_item_url(item.get("primary_url"))
    if primary:
        return "url:" + primary
    permalink = canonical_public_item_url(item.get("url"))
    if permalink:
        return "url:" + permalink
    title = " ".join(str(item.get("title") or "").split()).casefold()
    published = " ".join(str(item.get("published") or "").split())
    if title and published:
        return "metadata:" + hashlib.sha256((title + "|" + published).encode("utf-8")).hexdigest()
    return ""



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
