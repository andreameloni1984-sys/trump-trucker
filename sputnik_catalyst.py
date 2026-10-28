"""SPUTNIK catalyst-to-market mapping.

Maps public policy and macro themes to the agreed operational watch universe.
All outputs are hypotheses or WATCH candidates only; this module never places
orders or treats a news headline as a confirmed market signal.
"""
from __future__ import annotations
import re
from typing import Any

DOMAIN_INSTRUMENTS = {
    "ENERGY": [("WTI", "WTI crude oil"), ("BRENT", "Brent crude oil")],
    "METALS": [("GOLD", "Gold"), ("SILVER", "Silver"), ("COPPER", "Copper")],
    "AGRICULTURE": [("CORN", "Corn"), ("WHEAT", "Wheat"), ("SOYBEAN", "Soybean")],
    # Keep these source themes for intelligence, but do not create candidates
    # outside the agreed tradable universe.
    "DEFENSE": [],
    "AI_TECH": [("QQQ", "Nasdaq-100 ETF")],
    "SPACE": [],
    "CRYPTO": [],
    "MEDIA": [],
    "REAL_ESTATE": [],
    "TRADE_POLICY": [
        ("SPY", "S&P 500 ETF"),
        ("QQQ", "Nasdaq-100 ETF"),
        ("GOLD", "Gold"),
    ],
    "RATES_MACRO": [
        ("GOLD", "Gold"),
        ("SPY", "S&P 500 ETF"),
        ("QQQ", "Nasdaq-100 ETF"),
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
                row = merged.setdefault(instrument, {
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
            "status": "WATCH",
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
        "bias": {"SPY": "SHORT_BIAS", "QQQ": "SHORT_BIAS", "GOLD": "LONG_BIAS"},
        "reason": "trade escalation may pressure risk assets and support defensive demand",
    },
    {
        "id": "trade_deescalation",
        "domains": {"TRADE_POLICY"},
        "patterns": [r"\b(tariffs reduced|tariffs lifted|tariff rollback|trade deal|trade agreement|sanctions lifted|sanctions eased|ceasefire agreement)\b"],
        "bias": {"SPY": "LONG_BIAS", "QQQ": "LONG_BIAS", "GOLD": "SHORT_BIAS"},
        "reason": "trade de-escalation may support risk appetite and reduce defensive demand",
    },
    {
        "id": "hawkish_rates",
        "domains": {"RATES_MACRO"},
        "patterns": [r"\b(rate hike|raises interest rates|higher for longer|hawkish|inflation hotter than expected|inflation accelerates)\b"],
        "bias": {"GOLD": "SHORT_BIAS", "SPY": "SHORT_BIAS", "QQQ": "SHORT_BIAS"},
        "reason": "higher expected rates may pressure gold and duration-sensitive ETFs",
    },
    {
        "id": "dovish_rates",
        "domains": {"RATES_MACRO"},
        "patterns": [r"\b(rate cut|cuts interest rates|dovish|rate cuts expected|inflation cools|inflation lower than expected)\b"],
        "bias": {"GOLD": "LONG_BIAS", "SPY": "LONG_BIAS", "QQQ": "LONG_BIAS"},
        "reason": "lower expected rates may support gold and duration-sensitive ETFs",
    },
]


def directional_news_candidates(findings: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    """Map explicit, recognized public-news language to cautious directional biases.

    Only dated individual items with a URL and event ID qualify. Biases are
    hypotheses, not trade signals; unrecognized or ambiguous headlines abstain.
    """
    if limit <= 0:
        return []
    candidates: dict[tuple[str, str], dict[str, Any]] = {}
    for finding in findings:
        if (
            finding.get("evidence") != "PUBLIC_RSS_ITEM"
            or not finding.get("event_id")
            or not finding.get("url")
            or not finding.get("published")
        ):
            continue
        text = " ".join(str(finding.get(k) or "") for k in ("title", "text"))
        text = " ".join(text.lower().split())
        domains = {str(x).upper() for x in finding.get("domains") or []}
        for rule in _DIRECTION_RULES:
            if not domains.intersection(rule["domains"]):
                continue
            if not any(re.search(pattern, text, re.I) for pattern in rule["patterns"]):
                continue
            for instrument, bias in rule["bias"].items():
                key = (str(finding["event_id"]), instrument)
                candidates[key] = {
                    "event_id": str(finding["event_id"]),
                    "title": str(finding.get("title") or "")[:240],
                    "source": str(finding.get("source") or "N/D"),
                    "published": str(finding.get("published") or ""),
                    "url": str(finding.get("url") or ""),
                    "instrument": instrument,
                    "bias": bias,
                    "rule": rule["id"],
                    "reason": rule["reason"],
                    "status": "BIAS_ONLY_NEEDS_PRICE_VOLUME_CONFIRMATION",
                }
    result = sorted(candidates.values(), key=lambda x: x["published"], reverse=True)
    return result[:limit]
