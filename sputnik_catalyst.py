"""SPUTNIK catalyst-to-market mapping.

Maps documented public-policy themes to instruments/sectors worth monitoring.
It deliberately produces WATCH candidates, not trade directions. No company
or private relationship is inferred from a policy event.
"""
from __future__ import annotations
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

DOMAIN_INSTRUMENTS = {
    "ENERGY": [
        ("WTI", "Crude oil / energy"),
        ("BRENT", "Brent crude / energy"),
    ],
    "METALS": [
        ("GOLD", "Gold / metals"),
        ("SILVER", "Silver / metals"),
    ],
    "AGRICULTURE": [
        ("CORN", "Corn / agriculture"),
        ("WHEAT", "Wheat / agriculture"),
        ("SUGAR", "Sugar / agriculture"),
        ("COCOA", "Cocoa / agriculture"),
        ("COFFEE", "Coffee / agriculture"),
    ],
    "DEFENSE": [
        ("US_DEFENSE", "US defense sector"),
    ],
    "AI_TECH": [
        ("NASDAQ100", "US technology / AI"),
        ("SEMICONDUCTORS", "Semiconductors"),
    ],
    "SPACE": [
        ("US_AEROSPACE", "US aerospace / space"),
    ],
    "CRYPTO": [
        ("BTCUSD", "Bitcoin"),
    ],
    "MEDIA": [
        ("MEDIA", "US media sector"),
    ],
    "REAL_ESTATE": [
        ("US_REIT", "US real estate / REIT"),
    ],
    # These are watch candidates only: headline direction must be confirmed by
    # live price/volume before GAGARIN can consider an entry.
    "TRADE_POLICY": [
        ("NASDAQ100", "US technology / growth equities"),
        ("GOLD", "Gold / defensive asset"),
        ("USD", "US dollar"),
    ],
    "RATES_MACRO": [
        ("GOLD", "Gold / metals"),
        ("NASDAQ100", "US technology / growth equities"),
        ("USD", "US dollar"),
    ],
}

PRIMARY_SOURCES = {"WHITE_HOUSE", "OGE", "SEC"}


def catalyst_watchlist(findings: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    """Return deduplicated WATCH candidates from documented public findings."""
    if limit <= 0:
        return []

    merged: dict[str, dict[str, Any]] = {}
    for finding in findings:
        source = str(finding.get("source") or "UNKNOWN")
        domains = finding.get("domains") or []
        event_id = str(finding.get("event_id") or "")
        evidence = str(finding.get("evidence") or "")
        for domain in domains:
            domain = str(domain).upper()
            for instrument, description in DOMAIN_INSTRUMENTS.get(domain, []):
                key = instrument
                row = merged.setdefault(key, {
                    "instrument": instrument,
                    "description": description,
                    "status": "WATCH",
                    "sources": set(),
                    "events": set(),
                    "domains": set(),
                    "primary_source": False,
                    "evidence": [],
                })
                row["sources"].add(source)
                if event_id:
                    row["events"].add(event_id)
                row["domains"].add(domain)
                row["primary_source"] |= source in PRIMARY_SOURCES
                row["evidence"].append(evidence or "PUBLIC_SOURCE_TEXT")

    result = []
    for row in merged.values():
        source_count = len(row["sources"])
        event_count = len(row["events"])
        score = min(100, 40 + (20 if row["primary_source"] else 0) + min(20, source_count * 10) + min(20, event_count * 5))
        result.append({
            "instrument": row["instrument"],
            "description": row["description"],
            "status": row["status"],
            "score": score,
            "sources": sorted(row["sources"]),
            "events": len(row["events"]),
            "domains": sorted(row["domains"]),
            "primary_source": row["primary_source"],
            "reason": "Catalizzatore pubblico da verificare; nessuna direzione BUY/SELL inferita.",
        })
    result.sort(key=lambda x: (-x["score"], x["instrument"]))
    return result[:limit]


# Conservative headline-to-direction rules. These produce a *news bias* only;
# they never certify an entry without independent price/volume confirmation.
_DIRECTION_RULES = [
    {
        "id": "energy_supply_tightening",
        "domains": {"ENERGY"},
        "patterns": [r"\b(supply disruption|supply disrupted|production cut|cuts production|output cut|oil embargo|energy sanctions|pipeline attack|shipping disruption|strait of hormuz)\b"],
        "bias": {"WTI": "LONG_BIAS", "BRENT": "LONG_BIAS"},
        "reason": "possible tightening of energy supply",
    },
    {
        "id": "iran_diplomatic_deescalation",
        "domains": {"ENERGY"},
        "patterns": [r"\b(iran.*(agreement|deal|ceasefire)|((agreement|deal|ceasefire).*)iran|diplomatic breakthrough.*iran|de-escalation.*iran|deescalation.*iran|sanctions eased.*iran|sanctions lifted.*iran)\b"],
        "bias": {"WTI": "SHORT_BIAS", "BRENT": "SHORT_BIAS"},
        "reason": "credible Iran diplomatic de-escalation may reduce the geopolitical oil risk premium; supply-escalation risk remains the invalidation scenario",
    },
    {
        "id": "energy_supply_easing",
        "domains": {"ENERGY"},
        "patterns": [r"\b(production increase|raises output|output increase|supply restored|ceasefire.*oil|sanctions lifted.*oil|production boost)\b"],
        "bias": {"WTI": "SHORT_BIAS", "BRENT": "SHORT_BIAS"},
        "reason": "possible easing of energy supply constraints",
    },
    {
        "id": "trade_escalation",
        "domains": {"TRADE_POLICY"},
        "patterns": [r"\b(new tariffs|tariff increase|raises tariffs|tariffs on|trade war|trade restrictions|export ban|sanctions imposed|sanctions expanded)\b"],
        "bias": {"NASDAQ100": "SHORT_BIAS", "GOLD": "LONG_BIAS"},
        "reason": "trade escalation may pressure growth assets and support defensive demand",
    },
    {
        "id": "trade_deescalation",
        "domains": {"TRADE_POLICY"},
        "patterns": [r"\b(tariffs reduced|tariffs lifted|tariff rollback|trade deal|trade agreement|sanctions lifted|sanctions eased|ceasefire agreement)\b"],
        "bias": {"NASDAQ100": "LONG_BIAS", "GOLD": "SHORT_BIAS"},
        "reason": "trade de-escalation may support risk appetite and reduce defensive demand",
    },
    {
        "id": "hawkish_rates",
        "domains": {"RATES_MACRO"},
        "patterns": [r"\b(rate hike|raises interest rates|higher for longer|hawkish|inflation hotter than expected|inflation accelerates)\b"],
        "bias": {"USD": "LONG_BIAS", "GOLD": "SHORT_BIAS", "NASDAQ100": "SHORT_BIAS"},
        "reason": "higher expected rates may support USD and pressure duration-sensitive assets",
    },
    {
        "id": "dovish_rates",
        "domains": {"RATES_MACRO"},
        "patterns": [r"\b(rate cut|cuts interest rates|dovish|rate cuts expected|inflation cools|inflation lower than expected)\b"],
        "bias": {"USD": "SHORT_BIAS", "GOLD": "LONG_BIAS", "NASDAQ100": "LONG_BIAS"},
        "reason": "lower expected rates may weaken USD and support duration-sensitive assets",
    },
]


_NEGATED_IRAN_DEESCALATION_PATTERNS = (
    r"\b(?:no|not|never|failed to reach|reject(?:s|ed)?|collapse[ds]?)\b.{0,60}\b(?:agreement|deal|ceasefire|de-escalation|deescalation)\b",
    r"\b(?:agreement|deal|ceasefire)\b.{0,40}\b(?:not reached|rejected|failed|collapsed|off)\b",
    r"\bsanctions\b.{0,40}\b(?:not lifted|not eased|remain(?:s)? in place|will remain)\b",
)


def _is_negated_iran_deescalation(text: str) -> bool:
    """Abstain when an Iran deal/ceasefire/sanctions easing is explicitly denied."""
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in _NEGATED_IRAN_DEESCALATION_PATTERNS)

_NEGATION_BEFORE_MATCH = re.compile(
    r"\b(?:no|not|never|failed to|fails to|reject(?:s|ed)?|den(?:y|ies|ied)|ruled out|without)\b[^.!?;]{0,60}$",
    re.IGNORECASE,
)
_NEGATION_AFTER_MATCH = re.compile(
    r"^\s*(?:(?:was|were|is|are|has been|have been|had been|will be)\s+)?"
    r"(?:not\s+(?:reached|announced|approved|implemented|expected|planned|lifted|eased|restored|increased|cut|confirmed)|"
    r"rejected|denied|ruled out|failed|collapsed|off)\b",
    re.IGNORECASE,
)


def _is_explicitly_negated_rule_match(text: str, patterns: list[str]) -> bool:
    """Return True when a matched catalyst is explicitly denied in its sentence.

    This is a conservative keyword guard, not full natural-language understanding.
    Ambiguous cases should abstain rather than produce a directional hypothesis.
    """
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            left_boundary = max(
                text.rfind(".", 0, match.start()),
                text.rfind("!", 0, match.start()),
                text.rfind("?", 0, match.start()),
                text.rfind(";", 0, match.start()),
            ) + 1
            right_candidates = [
                position for position in (
                    text.find(".", match.end()),
                    text.find("!", match.end()),
                    text.find("?", match.end()),
                    text.find(";", match.end()),
                ) if position >= 0
            ]
            right_boundary = min(right_candidates) if right_candidates else len(text)
            before = text[left_boundary:match.start()]
            after = text[match.end():right_boundary]
            if _NEGATION_BEFORE_MATCH.search(before) or _NEGATION_AFTER_MATCH.search(after):
                return True
    return False



def _parse_aware_publication_time(value: Any) -> datetime | None:
    """Parse ISO-8601 or RFC-822 publication times only when timezone-aware."""
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        try:
            parsed = parsedate_to_datetime(text)
        except (TypeError, ValueError, OverflowError):
            return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def directional_news_candidates(findings: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    """Map explicit, recognized public-news language to cautious directional biases.

    Only dated individual items with a URL and event ID qualify. Biases are
    hypotheses, not trade signals; unrecognized or ambiguous headlines abstain.
    """
    if limit <= 0:
        return []
    candidates: dict[tuple[str, str], dict[str, Any]] = {}
    conflicted: set[tuple[str, str]] = set()
    for finding in findings:
        if (
            finding.get("evidence") != "PUBLIC_RSS_ITEM"
            or not finding.get("event_id")
            or not finding.get("url")
            or not finding.get("published")
        ):
            continue
        now_utc = datetime.now(timezone.utc)
        published_at = _parse_aware_publication_time(finding.get("published"))
        if published_at is None or published_at > now_utc:
            continue
        # If observation time is provided, it must be explicit, timezone-aware,
        # no earlier than publication, and not in the future. Older records
        # without available_at remain compatible but are less auditable.
        available_raw = finding.get("available_at")
        if available_raw is not None:
            available_at = _parse_aware_publication_time(available_raw)
            if available_at is None or available_at < published_at or available_at > now_utc:
                continue
        text = " ".join(str(finding.get(k) or "") for k in ("title", "text"))
        text = " ".join(text.lower().split())
        negated_iran_deescalation = _is_negated_iran_deescalation(text)
        domains = {str(x).upper() for x in finding.get("domains") or []}
        for rule in _DIRECTION_RULES:
            if not domains.intersection(rule["domains"]):
                continue
            # Keyword overlap is not enough: a rejected/failed deal must not
            # become the opposite (SHORT) hypothesis of a successful de-escalation.
            if rule["id"] == "iran_diplomatic_deescalation" and negated_iran_deescalation:
                continue
            if not any(re.search(pattern, text, re.IGNORECASE) for pattern in rule["patterns"]):
                continue
            # A negated headline must not be inverted into the opposite bias
            # (e.g. "no production cut" must not imply LONG oil).
            if _is_explicitly_negated_rule_match(text, rule["patterns"]):
                continue
            for instrument, bias in rule["bias"].items():
                key = (str(finding["event_id"]), instrument)
                if key in conflicted:
                    continue
                candidate = {
                    "event_id": str(finding["event_id"]),
                    "title": str(finding.get("title") or "")[:240],
                    "source": str(finding.get("source") or "N/D"),
                    "published": str(finding.get("published") or ""),
                    # Canonical UTC timestamp supports correct ordering across
                    # RFC-822/ISO inputs and differing source timezone offsets.
                    "published_at_utc": published_at.isoformat().replace("+00:00", "Z"),
                    "url": str(finding.get("url") or ""),
                    "instrument": instrument,
                    "bias": bias,
                    "rule": rule["id"],
                    "reason": rule["reason"],
                    "status": "BIAS_ONLY_NEEDS_PRICE_VOLUME_CONFIRMATION",
                }
                if available_raw is not None:
                    candidate["available_at_utc"] = available_at.isoformat().replace("+00:00", "Z")
                previous = candidates.get(key)
                if previous is not None and previous["bias"] != bias:
                    # Mixed/contradictory catalysts must not be resolved by
                    # rule iteration order. Abstain for this event/instrument.
                    candidates.pop(key, None)
                    conflicted.add(key)
                    continue
                if previous is None:
                    candidates[key] = candidate
    # Sort normalized UTC instants, not raw strings whose lexical order
    # changes with timezone offsets or mixed RFC-822/ISO formats.
    result = sorted(
        candidates.values(),
        key=lambda x: _parse_aware_publication_time(x["published_at_utc"]),
        reverse=True,
    )
    return result[:limit]
