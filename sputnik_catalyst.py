"""SPUTNIK catalyst-to-market mapping.

Maps public-policy themes to instruments worth monitoring. The aggressive
profile broadens headline matching to produce EARLY_BIAS candidates sooner;
these remain hypotheses and never certify an entry or place an order.
"""
from __future__ import annotations
import re
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

_NEGATION_PATTERN = re.compile(
    r"\b(?:no|not|never|without|deny|denies|denied|unconfirmed|"
    r"unsubstantiated|false|didn't|doesn't|hasn't|wasn't|weren't|"
    r"did not|does not|has not|was not|were not)\b",
    re.I,
)
_CONTRAST_PATTERN = re.compile(
    r"[.;!?,]|\b(?:but|however|although|yet|nevertheless)\b",
    re.I,
)


def non_negated_pattern_matches(text: str, pattern: str | re.Pattern[str]):
    """Yield matches that are not explicitly negated in the same clause."""
    compiled = re.compile(pattern, re.I) if isinstance(pattern, str) else pattern
    for match in compiled.finditer(text):
        before = text[max(0, match.start() - 70):match.start()]
        before = _CONTRAST_PATTERN.split(before)[-1]
        after = text[match.end():match.end() + 45]
        if _NEGATION_PATTERN.search(match.group(0)) or _NEGATION_PATTERN.search(before):
            continue
        if re.match(
            r"\s*(?:was|is|has been|were)?\s*(?:not confirmed|not verified|unconfirmed|false|denied)\b",
            after,
            re.I,
        ):
            continue
        yield match


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


# Aggressive headline-to-direction rules. Match early warning language as well
# as explicit supply/demand events. These are directional biases only.
_DIRECTION_RULES = [
    {
        "id": "energy_supply_tightening",
        "domains": {"ENERGY"},
        "patterns": [
            r"\b(supply disruption|supply disrupted|production cut|cuts production|output cut|oil embargo|energy sanctions|pipeline attack|shipping disruption|"
            r"(iran|iranian|tehran).{0,45}(threatens?|threatened|warns?|warned|vows?|plans?|moves?|considers?|could).{0,35}(close|block|mine|shut).{0,25}(the )?(strait of hormuz|hormuz)|"
            r"(strait of hormuz|hormuz).{0,30}(closed|blocked|mined|shut|closure)|"
            r"(closure|blockade|mining).{0,30}(strait of hormuz|hormuz)|"
            r"iranian attack|tanker seizure|oil exports? disrupted|crude exports? disrupted|threat to shipping|naval blockade)\b"
        ],
        "bias": {"WTI": "LONG_BIAS", "BRENT": "LONG_BIAS"},
        "reason": "early warning of possible tighter physical oil supply",
    },
    {
        "id": "energy_supply_easing",
        "domains": {"ENERGY"},
        "patterns": [
            r"\b(production increase|raises output|output increase|supply restored|ceasefire.*oil|sanctions lifted.*oil|production boost|iran deal|iran agreement|hormuz reopened|"
            r"strait of hormuz.{0,25}(reopens?|reopened|reopening|open again)|"
            r"hormuz.{0,25}(reopens?|reopened|reopening|open again)|"
            r"shipping.{0,20}(restored|resumes|resumed|back to normal)|"
            r"(passage|traffic|transit).{0,30}(resumes|resumed|restored|reopened).{0,30}(hormuz|strait)|"
            r"oil exports? resume)\b"
        ],
        "bias": {"WTI": "SHORT_BIAS", "BRENT": "SHORT_BIAS"},
        "reason": "early warning of possible easing of energy supply constraints",
    },
    {
        "id": "trade_escalation",
        "domains": {"TRADE_POLICY"},
        "patterns": [
            r"\b(new tariffs|tariff increase|raises tariffs|tariffs on|trade war|trade restrictions|export ban|sanctions imposed|sanctions expanded|tariff threat|threatens tariffs|tariff deadline)\b"
        ],
        "bias": {"NASDAQ100": "SHORT_BIAS", "GOLD": "LONG_BIAS"},
        "reason": "trade escalation may pressure growth assets and support defensive demand",
    },
    {
        "id": "trade_deescalation",
        "domains": {"TRADE_POLICY"},
        "patterns": [
            r"\b(tariffs reduced|tariffs lifted|tariff rollback|trade deal|trade agreement|sanctions lifted|sanctions eased|ceasefire agreement|tariff pause|trade talks resume)\b"
        ],
        "bias": {"NASDAQ100": "LONG_BIAS", "GOLD": "SHORT_BIAS"},
        "reason": "trade de-escalation may support risk appetite and reduce defensive demand",
    },
    {
        "id": "hawkish_rates",
        "domains": {"RATES_MACRO"},
        "patterns": [
            r"\b(rate hike|raises interest rates|higher for longer|hawkish|inflation hotter than expected|inflation accelerates|yields surge|bond yields rise)\b"
        ],
        "bias": {"USD": "LONG_BIAS", "GOLD": "SHORT_BIAS", "NASDAQ100": "SHORT_BIAS"},
        "reason": "higher expected rates may support USD and pressure duration-sensitive assets",
    },
    {
        "id": "dovish_rates",
        "domains": {"RATES_MACRO"},
        "patterns": [
            r"\b(rate cut|cuts interest rates|dovish|rate cuts expected|inflation cools|inflation lower than expected|yields fall|bond yields decline)\b"
        ],
        "bias": {"USD": "SHORT_BIAS", "GOLD": "LONG_BIAS", "NASDAQ100": "LONG_BIAS"},
        "reason": "lower expected rates may weaken USD and support duration-sensitive assets",
    },
]


def directional_news_candidates(findings: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
    """Map dated, URL-backed public items to unambiguous directional hypotheses.

    Conflicting or explicitly negated wording is kept as WATCH rather than
    forcing a direction. Output remains a hypothesis, not an entry.
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
        matched_rules = []
        for rule in _DIRECTION_RULES:
            if not domains.intersection(rule["domains"]):
                continue
            if any(
                next(non_negated_pattern_matches(text, pattern), None) is not None
                for pattern in rule["patterns"]
            ):
                matched_rules.append(rule)

        instruments = list(dict.fromkeys(
            instrument
            for rule in matched_rules
            for instrument in rule["bias"]
        ))
        for instrument in instruments:
            applicable = [
                rule for rule in matched_rules if instrument in rule["bias"]
            ]
            biases = {rule["bias"][instrument] for rule in applicable}
            # One item can mention both escalation and de-escalation. Do not
            # let rule ordering manufacture a direction from mixed evidence.
            if len(biases) != 1:
                continue
            bias = next(iter(biases))
            rule = next(rule for rule in applicable if rule["bias"][instrument] == bias)
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
                "status": "EARLY_BIAS_NEEDS_PRICE_VOLUME_CONFIRMATION",
            }
    result = sorted(candidates.values(), key=lambda x: x["published"], reverse=True)
    return result[:limit]
