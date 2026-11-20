"""Verified public news and conservative US equity catalyst rules."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import timedelta
from functools import lru_cache
from http.client import HTTPException
import json
import os
import re
from urllib.parse import urlsplit, urlunsplit

from sputnik_public_sources import parse_public_feed
from trump_tracker import _parse_public_item_timestamp, fetch_public_feed


@dataclass(frozen=True)
class Feed:
    name: str
    url: str
    publisher: str
    kind: str
    ticker: str = ""


FEEDS = (
    Feed("Casa Bianca – azioni", "https://www.whitehouse.gov/presidential-actions/feed/",
         "www.whitehouse.gov", "policy"),
    Feed("Casa Bianca – comunicati", "https://www.whitehouse.gov/briefings-statements/feed/",
         "www.whitehouse.gov", "policy"),
    Feed("Donald Trump / Truth Social", "https://www.trumpstruth.org/feed",
         "truthsocial.com", "truth"),
    Feed("Federal Reserve", "https://www.federalreserve.gov/feeds/press_all.xml",
         "www.federalreserve.gov", "fed"),
    Feed("Congresso / GovInfo", "https://www.govinfo.gov/rss/bills.xml",
         "www.govinfo.gov", "bills"),
    Feed("Leggi federali / GovInfo", "https://www.govinfo.gov/rss/plaw.xml",
         "www.govinfo.gov", "policy"),
    Feed("FDA", "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml",
         "www.fda.gov", "fda"),
    Feed("SEC", "https://www.sec.gov/news/pressreleases.rss", "www.sec.gov", "agency"),
    Feed("MarketWatch / Dow Jones", "https://feeds.content.dowjones.io/public/rss/mw_topstories",
         "www.marketwatch.com", "press"),
    Feed("GlobeNewswire / comunicati societari",
         "https://www.globenewswire.com/RssFeed/subjectcode/01-01/feedTitle/"
         "GlobeNewswire%20-%20Earnings%20Releases%20and%20Operating%20Results",
         "www.globenewswire.com", "wire"),
    Feed("PR Newswire / comunicati societari",
         "https://www.prnewswire.com/rss/financial-services-latest-news/"
         "financial-services-latest-news-list.rss",
         "www.prnewswire.com", "wire"),
    Feed("Microsoft Source", "https://news.microsoft.com/source/feed/",
         "news.microsoft.com", "issuer", "MSFT"),
    Feed("NVIDIA Blog", "https://blogs.nvidia.com/feed/",
         "blogs.nvidia.com", "issuer", "NVDA"),
    Feed("Eli Lilly Investor Relations", "https://investor.lilly.com/rss/news-releases.xml",
         "investor.lilly.com", "issuer", "LLY"),
)


def original_url(feed, row):
    value = row["primary_url"] if feed.kind == "truth" else row["url"]
    if any(ord(ch) < 33 for ch in value):
        return None
    try:
        parts = urlsplit(value)
        if (parts.scheme not in {"http", "https"} or parts.hostname != feed.publisher
                or parts.username or parts.password or parts.port is not None
                or not parts.path.strip("/")
                or parts.path.rstrip("/") == urlsplit(feed.url).path.rstrip("/")):
            return None
    except ValueError:
        return None
    if feed.kind == "truth" and not re.fullmatch(r"/@realDonaldTrump/\d+", parts.path):
        return None
    return urlunsplit(("https", parts.hostname, parts.path.rstrip("/"), "", ""))


def read_feed(feed):
    try:
        rows = parse_public_feed(fetch_public_feed(feed.url, timeout=10), feed.url)
    except (OSError, HTTPException, ValueError) as exc:
        print(f"SPUTNIK USA: {feed.name} indisponibile ({type(exc).__name__}).")
        return []
    items = []
    for row in rows:
        url = original_url(feed, row)
        stamp = _parse_public_item_timestamp(row["publication_time"])
        if url and stamp and row["title"]:
            items.append({"source": feed.name, "kind": feed.kind, "url": url,
                          "published": stamp.isoformat(), "title": row["title"],
                          "text": row["text"], "issuer": feed.ticker})
    print(f"SPUTNIK USA: {feed.name}, {len(items)} elementi con URL e pubblicazione.")
    return items


def configured_feeds():
    url = os.getenv("SPUTNIK_REUTERS_FEED_URL", "").strip()
    if not url:
        return FEEDS
    try:
        parts = urlsplit(url)
        valid = (parts.scheme == "https"
                 and parts.hostname in {"reuters.com", "www.reuters.com", "feeds.reuters.com"}
                 and parts.path.strip("/") and not parts.username and not parts.password
                 and parts.port in (None, 443) and not parts.fragment
                 and not any(ord(char) < 33 for char in url))
    except ValueError:
        valid = False
    if not valid:
        print("SPUTNIK USA: URL del feed Reuters non valido.")
        return FEEDS
    return (*FEEDS, Feed("Reuters", url, "www.reuters.com", "press"))


def collect_news(feeds=None):
    if feeds is None:
        feeds = configured_feeds()
    with ThreadPoolExecutor(max_workers=8) as pool:
        return [item for batch in pool.map(read_feed, feeds) for item in batch]


# Match completed actions with an explicit scope. Direction is a hypothesis
# about the economic channel, and still needs independent price confirmation.
TARIFF = r"(?:tariffs?|import duties|duty)"
TARIFF_SCOPE = r"(?:chinese|china|imports|all countries|trading partners)"
RULES = (
    ({"fed", "press"}, "fed-cut", "QQQ", "LONG",
     r"(?:committee decided to lower the target range for the federal funds rate|fed (?:cuts|cut|lowers) (?:interest rates|the federal funds rate))",
     "Tassi ufficiali più bassi possono ridurre il tasso di sconto dei titoli growth."),
    ({"fed", "press"}, "fed-hike", "QQQ", "SHORT",
     r"(?:committee decided to raise the target range for the federal funds rate|fed (?:raises|hikes) (?:interest rates|the federal funds rate))",
     "Tassi ufficiali più alti possono comprimere le valutazioni dei titoli growth."),
    ({"policy", "truth", "press"}, "tariffs-up", "SPY", "SHORT",
     rf"(?:impos(?:es|ed|ing)|rais(?:es|ed|ing)|increas(?:es|ed|ing)|implement(?:s|ed|ing))\b.{{0,70}}\b{TARIFF}\b.{{0,70}}\b{TARIFF_SCOPE}\b",
     "Dazi più alti sulle importazioni aumentano i costi per le aziende esposte e possono ridurre i margini."),
    ({"policy", "truth", "press"}, "tariffs-down", "SPY", "LONG",
     rf"(?:suspends?|suspended|suspending|removes?|removed|removing|reduces?|reduced|reducing)\b.{{0,70}}\b{TARIFF}\b.{{0,70}}\b{TARIFF_SCOPE}\b",
     "Dazi più bassi sulle importazioni possono ridurre costi e pressione sui margini."),
    ({"issuer", "press", "wire"}, "guidance-up", "", "LONG",
     r"\b(?:raises|raised|increases|increased)\b.{0,55}?\b(?:revenue|earnings|eps|sales)\s+(?:guidance|outlook|forecast)\b",
     "La società ha alzato le previsioni finanziarie, aumentando le aspettative sui risultati."),
    ({"issuer", "press", "wire"}, "guidance-down", "", "SHORT",
     r"\b(?:cuts|cut|lowers|lowered|reduces|reduced)\b.{0,55}?\b(?:revenue|earnings|eps|sales)\s+(?:guidance|outlook|forecast)\b",
     "La società ha abbassato le previsioni finanziarie, riducendo le aspettative sui risultati."),
    ({"fda"}, "fda-approval", "LLY", "LONG",
     r"\bfda approves\b.{0,120}\b(?:zepbound|mounjaro|kisunla)\b",
     "L’approvazione FDA amplia le possibilità commerciali negli USA per un farmaco di Eli Lilly."),
)

# Named issuers in the initial universe. Other issuers require an exchange-qualified symbol.
ISSUERS = {"AAPL": r"\bapple\b", "MSFT": r"\bmicrosoft\b",
           "NVDA": r"\bnvidia\b", "LLY": r"\beli lilly\b"}
LISTED_SYMBOL = re.compile(
    r"\((?:NASDAQ|NYSE(?: American| Arca)?|CBOE)\s*:\s*([A-Z][A-Z0-9.-]{0,9})\)",
    re.IGNORECASE,
)
UNCERTAIN = re.compile(
    r"\b(?:could|might|would|may|consider\w*|propos\w*|threaten\w*|rumou?r\w*|"
    r"expected to|plans? to|will|unlikely|den(?:ies|ied)|not|never|previously|reportedly|"
    r"already priced in)\b|n['’]t\b|\?"
)


def _issuer_name(value):
    return re.sub(r"(?: (?:inc|corp|corporation|company|co|ltd|limited|plc))+$", "", _normalized(value))


@lru_cache(maxsize=1)
def _sec_issuers():
    """Resolve names only after a guidance headline needs a ticker."""
    try:
        rows = json.loads(fetch_public_feed("https://www.sec.gov/files/company_tickers.json", timeout=10))
        names = {}
        for row in rows.values():
            names.setdefault(_issuer_name(row["title"]), set()).add(row["ticker"].upper())
        return names
    except (OSError, HTTPException, ValueError, KeyError, TypeError, AttributeError):
        print("SPUTNIK USA: anagrafica emittenti SEC indisponibile.")
        return {}


def catalyst(item):
    title = item["title"].lower()
    # FOMC titles are often simply “Federal Reserve issues FOMC statement”.
    use_body = item["kind"] in {"fed", "truth"}
    text = " ".join((item["text"] if use_body and item["text"] else title).lower().split())
    if UNCERTAIN.search(title):
        return None
    matches = []
    guidance_directions = set()
    for kinds, rule, ticker, direction, pattern, reason in RULES:
        if item["kind"] not in kinds:
            continue
        match = re.search(pattern, text)
        if not match or UNCERTAIN.search(text[max(0, match.start() - 90):match.end()]):
            continue
        if rule.startswith("guidance-"):
            guidance_directions.add(direction)
        symbol = ticker or item["issuer"]
        if not symbol:
            named = [symbol for symbol, name in ISSUERS.items()
                     if re.match(name + r"(?: inc\.?| corp\.?)?\s*$", title[:match.start()].strip())]
            subject = item["title"][:match.start()].strip()
            listing = LISTED_SYMBOL.search(subject)
            if listing and listing.end() == len(subject) and subject[:listing.start()].strip():
                explicit_symbol = listing.group(1).upper()
                if named and named != [explicit_symbol]:
                    continue
                symbol = explicit_symbol
            elif len(named) == 1:
                symbol = named[0]
            else:
                named_symbols = _sec_issuers().get(_issuer_name(subject), ())
                if len(named_symbols) != 1:
                    continue
                symbol = next(iter(named_symbols))
        bias = {"rule": rule, "ticker": symbol, "direction": direction,
                "reason": reason, "fact": match.group(),
                "uncertainty": "alta" if rule.startswith(("fed-", "tariffs-")) else "media"}
        if rule.startswith("fed-"):
            bias["rate_change"] = _rate_change(text[match.end():match.end() + 70])
        matches.append(bias)
    return matches[0] if len(matches) == 1 and len(guidance_directions) <= 1 else None


def eligible_news(items, now):
    for item in sorted(items, key=lambda item: item["published"]):
        age = now - _parse_public_item_timestamp(item["published"])
        if timedelta(0) <= age <= timedelta(hours=24):
            yield item


def _normalized(text):
    return " ".join(re.findall(r"\w+(?:[./]\d+)?", text.casefold()))


def _rate_change(text):
    points = re.search(r"\b(\d+)\s*(?:basis points?|bps)\b", text, re.IGNORECASE)
    if points:
        return int(points.group(1))
    percentage = re.search(
        r"\b(\d+(?:\.\d+|/\d+)?)\s+percentage points?\b", text, re.IGNORECASE
    )
    if percentage:
        value = percentage.group(1).split("/")
        if len(value) == 2 and int(value[1]) == 0:
            return None
        return round(float(value[0]) * 100 / (int(value[1]) if len(value) == 2 else 1))
    if re.search(r"\b(?:half|a half) (?:a |of a )?(?:percentage )?point\b", text, re.IGNORECASE):
        return 50
    if re.search(r"\b(?:quarter|a quarter) (?:of a )?(?:percentage )?point\b", text, re.IGNORECASE):
        return 25
    return None


def same_event(first, second):
    """Compare evidence of a shared event, without treating time alone as identity."""
    a, b = first["bias"], second["bias"]
    if (a["rule"], a["ticker"]) != (b["rule"], b["ticker"]):
        return False
    if first["url"] == second["url"]:
        return True
    # Two original publications can describe distinct actions with the same headline.
    if not {"press", "wire"}.intersection((first["kind"], second["kind"])):
        return False
    elapsed = abs(_parse_public_item_timestamp(first["published"])
                  - _parse_public_item_timestamp(second["published"]))
    if elapsed > timedelta(hours=2):
        return False
    if a["rule"].startswith("fed-"):
        magnitude = a.get("rate_change")
        if magnitude is not None and b.get("rate_change") is not None:
            return magnitude == b["rate_change"]
    return _normalized(first["title"]) == _normalized(second["title"])
