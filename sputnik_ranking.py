"""SPUTNIK buy-ranking engine.

Pure scoring logic only. It ranks publicly documented Form 4 purchases and never
infers private transactions, motives, or undocumented relationships.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone
from typing import Any

BUY_THRESHOLD = 75
WATCH_THRESHOLD = 55


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None


def _recency_score(transaction_date: str, today: date | None = None) -> int:
    tx_date = _parse_date(transaction_date)
    if tx_date is None:
        return 0
    today = today or datetime.now(timezone.utc).date()
    age = (today - tx_date).days
    if age < 0:
        return 0
    if age <= 1:
        return 10
    if age <= 7:
        return 8
    if age <= 30:
        return 5
    if age <= 90:
        return 2
    return 0


def score_purchase_candidate(items: list[dict[str, Any]], today: date | None = None) -> dict[str, Any]:
    """Score one documented security candidate from Form 4 purchases.

    A single SEC filing cannot reach BUY: confirmation points require distinct
    filing events. Unsupported relationship, sector and social points remain zero.
    """

    valid = [
        item for item in items
        if item.get("action") == "ACQUISTATO"
        and item.get("source_kind") == "FORM4_TRANSACTION"
        and item.get("source_url")
    ]
    if not valid:
        return {}

    valid.sort(key=lambda x: str(x.get("transaction_date") or ""), reverse=True)
    latest = valid[0]

    filing_ids = {
        (str(x.get("event_id") or ""), str(x.get("transaction_date") or ""))
        for x in valid
    }
    distinct_filings = len(filing_ids)

    source_quality = 25       # SEC primary document.
    event_strength = 25       # Form 4 purchase code P.
    confirmations = min(15, distinct_filings * 5)
    documented_relationship = 0
    recency = _recency_score(str(latest.get("transaction_date") or ""), today)
    sector_impact = 0
    social_confirmation = 0

    raw_score = min(
        100,
        source_quality
        + event_strength
        + confirmations
        + documented_relationship
        + recency
        + sector_impact
        + social_confirmation,
    )

    if distinct_filings >= 3 and raw_score >= BUY_THRESHOLD:
        signal = "COMPRA"
    elif raw_score >= WATCH_THRESHOLD:
        signal = "OSSERVA"
    else:
        signal = "EVITA"

    return {
        "label": f"{latest.get('security') or 'Titolo N/D'} — {latest.get('company') or 'Società N/D'}",
        "security": latest.get("security") or "Titolo N/D",
        "company": latest.get("company") or "Società N/D",
        "score": raw_score,
        "signal": signal,
        "source_quality": source_quality,
        "event_strength": event_strength,
        "confirmations": confirmations,
        "documented_relationship": documented_relationship,
        "recency": recency,
        "sector_impact": sector_impact,
        "social_confirmation": social_confirmation,
        "filings": distinct_filings,
        "date": latest.get("transaction_date") or latest.get("filing_date") or "N/D",
        "url": latest.get("source_url") or "",
        "reason": (
            f"Form 4 P documentato; {distinct_filings} filing distinti; "
            f"recenza {recency}/10."
        ),
    }


def rank_purchase_candidates(
    transactions: list[dict[str, Any]],
    limit: int = 5,
    today: date | None = None,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in transactions:
        if item.get("action") != "ACQUISTATO":
            continue
        if item.get("source_kind") != "FORM4_TRANSACTION":
            continue
        key = "|".join((
            str(item.get("cik") or ""),
            str(item.get("security") or "").strip().lower(),
            str(item.get("company") or "").strip().lower(),
        ))
        if key:
            grouped[key].append(item)

    ranked = [
        score_purchase_candidate(items, today=today)
        for items in grouped.values()
    ]
    ranked = [item for item in ranked if item]
    ranked.sort(key=lambda item: (item["score"], item["filings"], item["date"]), reverse=True)
    for position, item in enumerate(ranked[:limit], 1):
        item["rank"] = position
    return ranked[:limit]
