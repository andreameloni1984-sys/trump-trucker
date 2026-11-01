"""SPUTNIK public-policy impact model inspired by Trump-post market research.

It uses transparent, auditable topic/event rules plus a small sentiment
lexicon. It is not a trained or calibrated predictive model. It only emits
dated, URL-backed EARLY_BIAS hypotheses; price/volume confirmation and
Gagarin-style risk checks remain separate. Publicly documented actor roles
are accepted as metadata; relationships are never inferred from names.
"""
from __future__ import annotations

import re
from typing import Any

_POSITIVE = {
    "deal": 1, "agreement": 1, "peace": 1, "ceasefire": 1, "reopen": 1,
    "reopening": 1, "restore": 1, "restored": 1, "resume": 1, "resumes": 1,
    "growth": 1, "increase": 1, "boost": 1, "support": 1, "supporting": 1,
    "breakthrough": 1, "cooperation": 1, "lower": 1, "cut": 1,
}
_NEGATIVE = {
    "attack": -1, "attacks": -1, "war": -1, "conflict": -1, "threat": -1,
    "threatens": -1, "sanction": -1, "sanctions": -1, "ban": -1,
    "embargo": -1, "blockade": -1, "disruption": -1, "disrupted": -1,
    "escalation": -1, "escalate": -1, "tariff": -1, "tariffs": -1,
    "crisis": -1, "shortage": -1, "restrict": -1, "restriction": -1,
    "higher": -1, "surge": -1,
}
_NEGATION = re.compile(r"\b(?:no|not|never|deny|denied|false|unconfirmed|without)\b", re.I)

_CLAUSE_BOUNDARY = re.compile(r"[.;!?]|\\b(?:but|however|although|yet|nevertheless)\\b", re.I)


def _match_is_negated(text: str, match: re.Match[str]) -> bool:
    """Check negation only in the matched clause, not a preceding contrast."""
    start = 0
    end = len(text)
    for boundary in _CLAUSE_BOUNDARY.finditer(text):
        if boundary.end() <= match.start():
            start = boundary.end()
        elif boundary.start() >= match.end():
            end = boundary.start()
            break
    clause = text[start:end]
    return bool(_NEGATION.search(clause))

# Rules require concrete policy/event language. Generic positive/negative
# tone alone never creates an instrument bias.
_RULES = [
    {
        "id": "OIL_SUPPLY_TIGHTENING",
        "domains": {"ENERGY"},
        "pattern": re.compile(
            r"\b(?:oil|crude|petroleum|wti|brent|opec|tanker|hormuz|pipeline)\b.{0,90}"
            r"\b(?:cut|cuts|cutting|sanction|sanctions|embargo|blockade|attack|disruption|disrupted|"
            r"seizure|close|closed|restrict|restriction|production decline)\b|"
            r"\b(?:sanctions|embargo|blockade|attack|disruption|disrupted|seizure|closed)\b.{0,90}"
            r"\b(?:oil|crude|petroleum|wti|brent|opec|tanker|hormuz|pipeline)\b", re.I),
        "bias": {"WTI": "LONG_BIAS", "BRENT": "LONG_BIAS"},
        "topic": "ENERGY_SUPPLY",
        "reason": "possibile restrizione dell'offerta petrolifera",
    },
    {
        "id": "OIL_SUPPLY_EASING",
        "domains": {"ENERGY"},
        "pattern": re.compile(
            r"\b(?:oil|crude|petroleum|wti|brent|tanker|hormuz|pipeline)\b.{0,90}"
            r"\b(?:deal|agreement|ceasefire|reopen|reopening|restore|restored|resume|resumes|"
            r"sanctions lifted|production increase|supply restored)\b", re.I),
        "bias": {"WTI": "SHORT_BIAS", "BRENT": "SHORT_BIAS"},
        "topic": "ENERGY_SUPPLY",
        "reason": "possibile allentamento dei vincoli sull'offerta petrolifera",
    },
    {
        "id": "TRADE_ESCALATION",
        "domains": {"TRADE_POLICY"},
        "pattern": re.compile(r"\b(?:new tariffs|tariff increase|raises tariffs|trade war|export ban|"
                              r"trade restrictions|tariff threat|sanctions imposed)\b", re.I),
        "bias": {"GOLD": "LONG_BIAS", "NASDAQ100": "SHORT_BIAS"},
        "topic": "TRADE_POLICY",
        "reason": "escalation commerciale: possibile pressione sugli asset growth e domanda difensiva",
    },
    {
        "id": "TRADE_DEESCALATION",
        "domains": {"TRADE_POLICY"},
        "pattern": re.compile(r"\b(?:trade deal|trade agreement|tariffs reduced|tariffs lifted|"
                              r"tariff pause|trade talks resume|sanctions eased)\b", re.I),
        "bias": {"GOLD": "SHORT_BIAS", "NASDAQ100": "LONG_BIAS"},
        "topic": "TRADE_POLICY",
        "reason": "distensione commerciale: possibile recupero della propensione al rischio",
    },
    {
        "id": "GEOPOLITICAL_ESCALATION",
        "domains": {"GEOPOLITICS", "SANCTIONS"},
        "pattern": re.compile(r"\b(?:military attack|missile strike|armed conflict|military escalation|"
                              r"naval blockade|new sanctions|sanctions expanded|invasion)\b", re.I),
        "bias": {"GOLD": "LONG_BIAS", "WTI": "LONG_BIAS", "BRENT": "LONG_BIAS"},
        "topic": "GEOPOLITICS",
        "reason": "escalation geopolitica: possibile premio di rischio su oro ed energia",
    },
    {
        "id": "GEOPOLITICAL_DEESCALATION",
        "domains": {"GEOPOLITICS", "SANCTIONS"},
        "pattern": re.compile(r"\b(?:peace agreement|ceasefire agreement|ceasefire|peace deal|"
                              r"sanctions lifted|sanctions eased|hostilities end)\b", re.I),
        "bias": {"GOLD": "SHORT_BIAS", "WTI": "SHORT_BIAS", "BRENT": "SHORT_BIAS"},
        "topic": "GEOPOLITICS",
        "reason": "distensione geopolitica: possibile riduzione del premio di rischio",
    },
    {
        "id": "AGRICULTURE_EXPORT_RESTRICTION",
        "domains": {"AGRICULTURE", "TRADE_POLICY"},
        "pattern": re.compile(r"\b(?:grain|wheat|corn|maize|soy|soybean|agricultural exports?)\b.{0,90}"
                              r"\b(?:export ban|export restriction|embargo|port closure|shipping ban)\b|"
                              r"\b(?:export ban|export restriction|embargo|port closure|shipping ban)\b.{0,90}"
                              r"\b(?:grain|wheat|corn|maize|soy|soybean|agricultural exports?)\b", re.I),
        "bias": {"WHEAT": "LONG_BIAS", "CORN": "LONG_BIAS", "SOYBEAN": "LONG_BIAS"},
        "topic": "AGRICULTURE_SUPPLY",
        "reason": "possibile restrizione delle esportazioni agricole",
    },
]


def _sentiment(text: str) -> float:
    tokens = re.findall(r"[a-z']+", text.lower())
    score = 0
    for index, token in enumerate(tokens):
        value = _POSITIVE.get(token, _NEGATIVE.get(token, 0))
        if not value:
            continue
        context = tokens[max(0, index - 3):index]
        if any(word in {"no", "not", "never", "without"} for word in context):
            value *= -1
        score += value
    return max(-1.0, min(1.0, score / max(2.0, len(tokens) ** 0.5)))


def _normalized_name(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", str(value or "").lower()))


def resolve_public_actor_role(author: str) -> str | None:
    """Resolve an author only through an explicit, user-maintained public-role map.

    SPUTNIK_ACTOR_ROLE_MAP must be a JSON object: {"Public Name": "family"}.
    No relationship is inferred from a name or from social proximity.
    """
    import json
    import os

    raw = os.getenv("SPUTNIK_ACTOR_ROLE_MAP", "").strip()
    if not raw:
        return None
    try:
        mapping = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(mapping, dict):
        return None
    target = _normalized_name(author)
    if not target:
        return None
    allowed = {"president", "administration", "cabinet", "family", "adviser", "advisor", "ally", "associate", "friend", "entourage"}
    for name, role in mapping.items():
        if _normalized_name(name) == target and str(role or "").strip().lower() in allowed:
            return str(role).strip().lower()
    return None


def _actor_context(finding: dict[str, Any]) -> tuple[str, float]:
    role = str(finding.get("actor_role") or finding.get("author_role") or "").strip().lower()
    if role:
        if any(word in role for word in ("president", "presidential", "trump")):
            return "PRESIDENT", 1.0
        if any(word in role for word in ("white house", "administration", "cabinet", "secretary")):
            return "ADMINISTRATION", 0.85
        if any(word in role for word in ("family", "relative", "adviser", "advisor", "ally", "associate", "friend", "entourage")):
            return "PUBLICLY_IDENTIFIED_ASSOCIATE", 0.65
        return "OTHER_PUBLIC_ACTOR", 0.5
    source = str(finding.get("source") or "").upper()
    feed_url = str(finding.get("feed_url") or finding.get("url") or "").lower()
    if source in {"TRUTH_ARCHIVE", "TRUTH SOCIAL"} or "trumpstruth.org" in feed_url or "truthsocial.com" in feed_url:
        return "PRESIDENT_OFFICIAL_CHANNEL", 1.0
    if source in {"WHITE_HOUSE", "WHITE_HOUSE_RSS"} or "whitehouse.gov" in feed_url:
        return "ADMINISTRATION_OFFICIAL_CHANNEL", 0.85
    if source == "OGE":
        return "PUBLIC_ETHICS_DISCLOSURE", 0.75
    if source == "SEC":
        return "PUBLIC_SEC_DISCLOSURE", 0.65
    return "PUBLIC_SOURCE_ROLE_UNVERIFIED", 0.45


def analyze_public_policy_item(finding: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert a verified public item into cautious directional early-bias rows."""
    if (
        finding.get("evidence") != "PUBLIC_RSS_ITEM"
        or not str(finding.get("event_id") or "").strip()
        or not str(finding.get("url") or "").strip()
        or not str(finding.get("published") or "").strip()
    ):
        return []
    text = " ".join(str(finding.get(key) or "") for key in ("title", "text", "snippet"))
    domains = {str(item).upper() for item in finding.get("domains") or []}
    if not text.strip() or not domains:
        return []
    actor_class, actor_weight = _actor_context(finding)
    sentiment = _sentiment(text)
    source = str(finding.get("source") or "UNKNOWN")
    matches: list[dict[str, Any]] = []
    for rule in _RULES:
        if not domains.intersection(rule["domains"]) or not rule["pattern"].search(text):
            continue
        # A negation invalidates only the event in its own clause. A
        # previous clause separated by punctuation/contrast must not suppress
        # a later, independently stated policy event.
        matched = rule["pattern"].search(text)
        if _match_is_negated(text, matched):
            continue
        for instrument, bias in rule["bias"].items():
            priority = round(min(95, 55 + abs(sentiment) * 12 + actor_weight * 10 + (8 if source in {"WHITE_HOUSE", "WHITE_HOUSE_RSS", "TRUTH_ARCHIVE"} or "whitehouse.gov" in str(finding.get("feed_url") or "").lower() or "trumpstruth.org" in str(finding.get("feed_url") or "").lower() else 0)))
            matches.append({
                "event_id": str(finding["event_id"]),
                "title": str(finding.get("title") or "")[:240],
                "source": source,
                "published": str(finding["published"]),
                "url": str(finding["url"]),
                "instrument": instrument,
                "bias": bias,
                "rule": rule["id"],
                "topic": rule["topic"],
                "sentiment_score": round(sentiment, 4),
                "actor_class": actor_class,
                "actor_weight": actor_weight,
                "priority_score": priority,
                "reason": rule["reason"],
                "status": "EARLY_BIAS_NEEDS_PRICE_VOLUME_CONFIRMATION",
                "evidence": "PUBLIC_DATED_URL_BACKED_ITEM",
                "model": "TRANSPARENT_TOPIC_EVENT_SENTIMENT_V1",
                "probability_calibrated": False,
                "paper_trade_status": "NOT_EXECUTED",
            })
    return matches
