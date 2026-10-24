from __future__ import annotations

"""Record pre-event expectations and measured post-release market reactions.

This module does not fetch prices or invent a directional forecast. Callers must
supply timestamped, observed prices from a trusted provider before calculating
reaction metrics.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _aware_iso(value: str) -> datetime:
    text = str(value or "").strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def create_pre_event_record(event_id: str, title: str, scheduled_at: str,
                            instrument: str, scenario: str,
                            baseline_price: float | None = None,
                            baseline_at: str | None = None) -> dict[str, Any]:
    if not event_id.strip() or not title.strip() or not instrument.strip():
        raise ValueError("event_id, title and instrument are required")
    scheduled = _aware_iso(scheduled_at)
    record: dict[str, Any] = {
        "event_id": event_id.strip(),
        "title": title.strip(),
        "scheduled_at_utc": scheduled.isoformat(),
        "instrument": instrument.strip(),
        "scenario": scenario.strip() or "NO_DIRECTIONAL_SCENARIO",
        "direction": "NOT_INFERRED",
        "baseline_price": None,
        "baseline_at_utc": None,
        "post_price": None,
        "post_at_utc": None,
        "reaction_pct": None,
        "evaluation_status": "AWAITING_POST_EVENT_PRICE",
    }
    if baseline_price is not None:
        if baseline_price <= 0:
            raise ValueError("baseline price must be positive")
        if not baseline_at:
            raise ValueError("baseline_at is required when baseline_price is supplied")
        observed_at = _aware_iso(baseline_at)
        if observed_at > scheduled:
            raise ValueError("baseline observation must be at or before scheduled event")
        record["baseline_price"] = float(baseline_price)
        record["baseline_at_utc"] = observed_at.isoformat()
    return record


def evaluate_post_event(record: dict[str, Any], post_price: float, post_at: str) -> dict[str, Any]:
    if post_price <= 0:
        raise ValueError("post-event price must be positive")
    if record.get("baseline_price") is None or not record.get("baseline_at_utc"):
        raise ValueError("cannot evaluate without a pre-event baseline price")
    post_time = _aware_iso(post_at)
    scheduled = _aware_iso(record["scheduled_at_utc"])
    baseline_time = _aware_iso(record["baseline_at_utc"])
    if post_time < scheduled:
        raise ValueError("post-event observation must not precede the scheduled event")
    if post_time <= baseline_time:
        raise ValueError("post-event observation must follow the baseline observation")
    result = dict(record)
    result["post_price"] = float(post_price)
    result["post_at_utc"] = post_time.isoformat()
    result["reaction_pct"] = round((float(post_price) / float(record["baseline_price"]) - 1) * 100, 6)
    result["evaluation_status"] = "REACTION_MEASURED_DIRECTION_NOT_PREDICTED"
    return result


def upsert_jsonl(path: str | Path, record: dict[str, Any]) -> None:
    """Replace an existing event_id record or append a new one, atomically."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    if target.exists():
        for line in target.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict) and row.get("event_id") != record.get("event_id"):
                rows.append(row)
    rows.append(record)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    temporary.replace(target)
