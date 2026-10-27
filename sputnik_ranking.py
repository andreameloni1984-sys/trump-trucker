"""SPUTNIK buy-ranking engine.

Pure scoring logic only. It ranks publicly documented Form 4 purchases and never
infers private transactions, motives, or undocumented relationships.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone
from typing import Any
from urllib.parse import urlsplit, urlunsplit

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


def disclosure_lag(transaction_date: str, filing_date: str) -> int | None:
    """Return calendar days between the documented transaction and filing dates."""
    tx = _parse_date(transaction_date)
    filing = _parse_date(filing_date)
    if tx is None or filing is None:
        return None
    return (filing - tx).days


def disclosure_business_days(transaction_date: str, filing_date: str) -> int | None:
    """Count weekdays strictly after transaction date through filing date.

    Informational only: this does not model federal holidays or SEC exceptions.
    """
    tx = _parse_date(transaction_date)
    filing = _parse_date(filing_date)
    if tx is None or filing is None or filing < tx:
        return None
    days = 0
    cursor = tx
    while cursor < filing:
        cursor = cursor.fromordinal(cursor.toordinal() + 1)
        if cursor.weekday() < 5:
            days += 1
    return days


def disclosure_lag_bucket(transaction_date: str, filing_date: str) -> str:
    """Classify disclosure timing without treating timing as proof of intent."""
    lag = disclosure_lag(transaction_date, filing_date)
    if lag is None or lag < 0:
        return "N/D"
    if lag == 0:
        return "SAME_DAY"
    if lag <= 3:
        return "1-3_GIORNI"
    if lag <= 45:
        return "4-45_GIORNI"
    return "OLTRE_45_GIORNI"


def _filing_identity(item: dict[str, Any]) -> str:
    """Return a stable filing identity; transactions from one filing count once."""
    accession = str(item.get("accession_number") or item.get("accession") or "").strip()
    if accession:
        normalized_accession = "".join(char for char in accession.lower() if char.isalnum())
        if normalized_accession:
            return f"accession:{normalized_accession}"

    source_url = str(item.get("source_url") or "").strip()
    try:
        parsed = urlsplit(source_url)
        if parsed.scheme.lower() in {"http", "https"} and parsed.netloc:
            canonical = urlunsplit((
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path.rstrip("/"),
                "",
                "",
            ))
            if canonical:
                return f"url:{canonical}"
    except ValueError:
        pass
    return f"url:{source_url}"


def _is_primary_sec_form4_url(value: Any) -> bool:
    """Accept only unambiguous HTTPS SEC EDGAR archive document URLs."""
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = urlsplit(value.strip())
        if parsed.scheme.lower() != "https":
            return False
        if parsed.username is not None or parsed.password is not None:
            return False
        if parsed.port not in (None, 443):
            return False
        host = (parsed.hostname or "").lower().rstrip(".")
        if host not in {"sec.gov", "www.sec.gov"}:
            return False
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 6:
            return False
        if [part.lower() for part in parts[:3]] != ["archives", "edgar", "data"]:
            return False
        return parts[3].isdigit() and bool(parts[4]) and bool(parts[5])
    except (TypeError, ValueError):
        return False


def score_purchase_candidate(items: list[dict[str, Any]], today: date | None = None) -> dict[str, Any]:
    """Score one documented security candidate from Form 4 purchases.

    A single SEC filing cannot reach BUY: confirmation points require distinct
    filing events. Only primary HTTPS SEC EDGAR archive URLs qualify for the
    primary-source score. Unsupported relationship, sector and social points remain zero.
    """

    valid = [
        item for item in items
        if item.get("action") == "ACQUISTATO"
        and item.get("source_kind") == "FORM4_TRANSACTION"
        and _is_primary_sec_form4_url(item.get("source_url"))
    ]
    if not valid:
        return {}

    valid.sort(key=lambda x: str(x.get("transaction_date") or ""), reverse=True)
    latest = valid[0]

    # Multiple transaction rows from the same Form 4 must not count as
    # independent confirmations. Prefer the SEC accession when available;
    # otherwise use the canonical source permalink.
    filing_ids = {_filing_identity(item) for item in valid}
    distinct_filings = len(filing_ids)

    source_quality = 25       # SEC primary document.
    event_strength = 20       # Historical 100-point rubric: documented event.
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
        "filing_date": latest.get("filing_date") or "N/D",
        "disclosure_lag_days": disclosure_lag(
            str(latest.get("transaction_date") or ""),
            str(latest.get("filing_date") or ""),
        ),
        "disclosure_business_days": disclosure_business_days(
            str(latest.get("transaction_date") or ""),
            str(latest.get("filing_date") or ""),
        ),
        "disclosure_lag_bucket": disclosure_lag_bucket(
            str(latest.get("transaction_date") or ""),
            str(latest.get("filing_date") or ""),
        ),
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
        cik = str(item.get("cik") or "").strip()
        security = str(item.get("security") or "").strip()
        # Never rank an unidentified issuer/security or merge it into a guessed group.
        if not cik or not security:
            continue
        key = "|".join((
            cik,
            security.lower(),
            str(item.get("company") or "").strip().lower(),
        ))
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
