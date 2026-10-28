"""Structured audit journal for SPUTNIK market-opportunity analyses.

Records what the Telegram action/reaction view actually evaluated, including
point-in-time source and quote timestamps. This is an audit log, not an order
ledger and not evidence of a trade outcome.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JOURNAL_PATH = Path(os.getenv("SPUTNIK_SIGNAL_JOURNAL_PATH", "data/sputnik_signal_journal.jsonl"))


def _parse_utc_timestamp(value: str) -> datetime | None:
    """Parse an ISO timestamp without guessing when source metadata is absent."""
    if not str(value or "").strip():
        return None
    try:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _publication_delay_seconds(published_at: str, detected_at: str) -> float | None:
    published = _parse_utc_timestamp(published_at)
    detected = _parse_utc_timestamp(detected_at)
    if published is None or detected is None:
        return None
    return round((detected - published).total_seconds(), 3)


def build_signal_record(
    text: str,
    source: str,
    quotes: dict[str, Any] | None = None,
    *,
    event_id: str = "",
    event_detected_at: str = "",
    event_published_at: str = "",
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build a truthful record; missing quotes remain missing, never inferred."""
    from sputnik_cfd import build_conditional_trade_plan
    from sputnik_decision_engine import conditional_plans

    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)

    rows = conditional_plans(text, limit=1)
    base: dict[str, Any] = {
        "record_id": uuid.uuid4().hex,
        "record_type": "SPUTNIK_ANALYSIS",
        "recorded_at": now.isoformat(),
        "source": str(source or "Fonte non specificata"),
        "event_id": str(event_id or ""),
        "event_detected_at": str(event_detected_at or ""),
        "event_published_at": str(event_published_at or ""),
        "publication_to_detection_seconds": _publication_delay_seconds(event_published_at, event_detected_at),
        "catalyst_excerpt": str(text or "")[:700],
        "horizon": "INTRADAY",
        "mode": "PAPER",
        "entry": None,
        "stop_loss": None,
        "take_profit_1": None,
        "take_profit_2": None,
        "quote_timestamp": None,
        "quote_price": None,
        "atr": None,
        "outcome_status": "NOT_YET_SCORED",
        "outcome_checked_at": None,
        "outcome": None,
    }

    if not rows:
        base.update({
            "instrument": None,
            "direction": "WAIT",
            "decision_status": "WAIT",
            "outcome_status": "NOT_SCORABLE_NO_SPECIFIC_CATALYST",
            "reason": "Nessun catalizzatore specifico corrisponde alle regole operative.",
        })
        return base

    plan = rows[0]
    trade = build_conditional_trade_plan(plan, quotes or {})
    direction = "SHORT" if "SHORT" in str(plan.get("bias", "")).upper() else "LONG"
    entry = trade.get("entry")
    base.update({
        "instrument": str(plan.get("candidate") or ""),
        "direction": direction,
        "decision_status": str(trade.get("status") or "WAIT"),
        "entry": entry,
        "stop_loss": trade.get("stop"),
        "take_profit_1": trade.get("tp1"),
        "take_profit_2": trade.get("tp2"),
        "quote_timestamp": trade.get("quote_time"),
        "quote_price": entry,
        "atr": trade.get("atr"),
        "reason": str(trade.get("reason") or ""),
        "confirmation_required": str(plan.get("confirmation") or ""),
        "invalidation": str(plan.get("invalidation") or ""),
    })
    if entry is None:
        base["outcome_status"] = "NOT_SCORABLE_NO_FRESH_QUOTE"
    return base


def append_signal_record(record: dict[str, Any], path: Path | None = None) -> None:
    """Append one JSONL audit row; surface write failures to the caller."""
    target = path or JOURNAL_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, allow_nan=False, default=str) + "\n"
    with target.open("a", encoding="utf-8") as handle:
        handle.write(line)
        handle.flush()
