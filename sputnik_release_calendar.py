"""Classify scheduled US releases for Sputnik's pre-event watchlist.

Input times must be timezone-aware ISO-8601 timestamps. This module does not
fetch calendars or create trades; it maps scheduled release metadata to watch
priority and converts times using the IANA timezone database.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

ROME = ZoneInfo("Europe/Rome")
EASTERN = ZoneInfo("America/New_York")

RELEASE_RULES = (
    (("consumer price index", "cpi", "producer price index", "ppi", "pce price", "inflation"), "HIGH", ("NASDAQ-100", "S&P 500", "GOLD", "DXY")),
    (("employment situation", "nonfarm payroll", "unemployment rate", "employment cost index", "jobless claims"), "HIGH", ("NASDAQ-100", "S&P 500", "DXY", "GOLD")),
    (("fomc", "federal reserve", "interest rate decision", "fed funds rate"), "HIGH", ("NASDAQ-100", "S&P 500", "GOLD", "DXY")),
    (("gross domestic product", "gdp", "retail sales", "ism manufacturing", "ism services"), "MEDIUM", ("NASDAQ-100", "S&P 500", "DXY")),
    (("crude oil inventories", "eia petroleum", "opec"), "HIGH", ("WTI",)),
)

def classify_scheduled_release(title: str) -> dict[str, object]:
    body = " ".join(str(title or "").lower().split())
    for phrases, impact, instruments in RELEASE_RULES:
        if any(phrase in body for phrase in phrases):
            return {"impact": impact, "instruments": list(instruments), "matched": True}
    return {"impact": "UNCLASSIFIED", "instruments": [], "matched": False}

def release_time_in_rome(timestamp: str) -> str:
    """Convert an ISO-8601 timestamp with offset/Z to Europe/Rome time."""
    value = str(timestamp or "").strip()
    if not value:
        raise ValueError("timestamp ISO-8601 con fuso orario richiesto")
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timestamp senza fuso orario: conversione ambigua")
    return parsed.astimezone(ROME).isoformat(timespec="minutes")

def prepare_release_watch(title: str, timestamp: str) -> dict[str, object]:
    classification = classify_scheduled_release(title)
    return {
        "title": str(title or "").strip(),
        "scheduled_rome": release_time_in_rome(timestamp),
        "impact": classification["impact"],
        "instruments": classification["instruments"],
        "status": "PREPARE_BEFORE_RELEASE" if classification["matched"] else "CALENDAR_ITEM_UNCLASSIFIED",
        "direction": "NOT_INFERRED",
    }
