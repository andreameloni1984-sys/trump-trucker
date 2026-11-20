"""Verified public news and conservative US equity catalyst rules."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import timedelta
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
    except (OSError, ValueError) as exc:
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


def collect_news(feeds=FEEDS):
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
    ({"issuer", "press"}, "guidance-up", "", "LONG",
     r"\b(?:raises|raised|increases|increased)\b.{0,55}\b(?:revenue|earnings|eps|sales)\s+(?:guidance|outlook|forecast)\b",
     "La società ha alzato le previsioni finanziarie, aumentando le aspettative sui risultati."),
    ({"issuer", "press"}, "guidance-down", "", "SHORT",
     r"\b(?:cuts|cut|lowers|lowered|reduces|reduced)\b.{0,55}\b(?:revenue|earnings|eps|sales)\s+(?:guidance|outlook|forecast)\b",
     "La società ha abbassato le previsioni finanziarie, riducendo le aspettative sui risultati."),
    ({"fda"}, "fda-approval", "LLY", "LONG",
     r"\bfda approves\b.{0,120}\b(?:zepbound|mounjaro|kisunla)\b",
     "L’approvazione FDA amplia le possibilità commerciali negli USA per un farmaco di Eli Lilly."),
)

# Only these explicitly identified US issuers can be mapped from press headlines.
ISSUERS = {"AAPL": r"\bapple\b", "MSFT": r"\bmicrosoft\b",
           "NVDA": r"\bnvidia\b", "LLY": r"\beli lilly\b"}
UNCERTAIN = re.compile(
    r"\b(?:could|might|would|may|consider\w*|propos\w*|threaten\w*|rumou?r\w*|"
    r"expected to|plans? to|unlikely|denies|not|never|previously|reportedly|already priced in)\b|\?"
)


def catalyst(item):
    title = item["title"].lower()
    # FOMC titles are often simply “Federal Reserve issues FOMC statement”.
    use_body = item["kind"] in {"fed", "truth"}
    text = " ".join((item["text"] if use_body and item["text"] else title).lower().split())
    if UNCERTAIN.search(title):
        return None
    matches = []
    for kinds, rule, ticker, direction, pattern, reason in RULES:
        if item["kind"] not in kinds:
            continue
        match = re.search(pattern, text)
        if not match or UNCERTAIN.search(text[max(0, match.start() - 90):match.end()]):
            continue
        symbol = ticker or item["issuer"]
        if not symbol:
            named = [symbol for symbol, name in ISSUERS.items()
                     if re.match(name + r"(?: inc\.?| corp\.?)?\s*$", title[:match.start()].strip())]
            if len(named) != 1:
                continue
            symbol = named[0]
        matches.append({"rule": rule, "ticker": symbol, "direction": direction,
                        "reason": reason, "fact": match.group()})
    return matches[0] if len(matches) == 1 else None


def eligible_news(items, now):
    for item in sorted(items, key=lambda item: item["published"]):
        age = now - _parse_public_item_timestamp(item["published"])
        if timedelta(0) <= age <= timedelta(hours=24):
            yield item
