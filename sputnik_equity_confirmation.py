"""Read-only equity reaction confirmation for Sputnik.

Only explicit, independently verified ticker/event/direction inputs are
eligible. This does not infer sentiment from policy headlines or place orders.
"""
from __future__ import annotations

from datetime import datetime, timezone
from math import isfinite
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import json
import re

_TICKER = re.compile(r"[A-Z][A-Z0-9.-]{0,9}")


def confirmed_equity_plan(*, ticker: str, direction: str, source_url: str,
                          event_id: str, published_at: datetime,
                          verified: bool, now: datetime) -> dict | None:
    """Confirm LONG/SHORT only on post-event 1m breakout and expanded volume."""
    if (verified is not True or direction not in {"LONG", "SHORT"}
            or not isinstance(ticker, str) or not _TICKER.fullmatch(ticker)
            or not isinstance(event_id, str) or not event_id.strip()
            or not isinstance(now, datetime) or now.tzinfo is None
            or not isinstance(published_at, datetime) or published_at.tzinfo is None
            or not 0 <= (now - published_at).total_seconds() <= 1800):
        return None
    try:
        url = urlsplit(source_url)
        if (url.scheme != "https" or not url.hostname or url.username or url.password
                or url.port not in (None, 443)):
            return None
        endpoint = ("https://query1.finance.yahoo.com/v8/finance/chart/"
                    + ticker + "?interval=1m&range=1d")
        with urlopen(Request(endpoint, headers={"User-Agent": "Mozilla/5.0"}),
                     timeout=10) as response:
            data = json.load(response)
        series = data["chart"]["result"][0]
        stamps = series["timestamp"]
        quotes = series["indicators"]["quote"][0]
        bars = []
        for i, stamp in enumerate(stamps):
            closed = datetime.fromtimestamp(int(stamp) + 60, tz=timezone.utc)
            if closed > now:
                continue
            values = [float(quotes[k][i]) for k in ("close", "high", "low", "volume")]
            if (not all(isfinite(v) and v > 0 for v in values)
                    or not values[2] <= values[0] <= values[1]):
                continue
            bars.append((closed, *values))
        tail = bars[-21:]
        if len(tail) < 21 or any(
                a[0] >= b[0] or (b[0] - a[0]).total_seconds() > 120
                for a, b in zip(tail, tail[1:])
        ):
            return None
        if not 0 <= (now - tail[-1][0]).total_seconds() <= 60:
            return None
        if tail[-1][0] < published_at or tail[-1][0] > now:
            return None
        # Avoid claiming a news reaction from a breakout that happened before
        # the news. The breakout candle itself must begin after publication.
        if tail[-1][0].timestamp() - 60 < published_at.timestamp():
            return None
        prev = tail[:-1]
        last = tail[-1]
        if last[4] < 1.5 * sum(b[4] for b in prev) / 20:
            return None
        # Avoid an intrabar reversal being labelled a confirmed news breakout.
        if direction == "LONG" and last[1] <= prev[-1][1]:
            return None
        if direction == "SHORT" and last[1] >= prev[-1][1]:
            return None
        if direction == "LONG" and last[1] <= max(b[2] for b in prev):
            return None
        if direction == "SHORT" and last[1] >= min(b[3] for b in prev):
            return None
        atr = sum(b[2] - b[3] for b in prev) / 20
        entry = last[1]
        stop = entry - 1.5 * atr if direction == "LONG" else entry + 1.5 * atr
        target = entry + 3 * atr if direction == "LONG" else entry - 3 * atr
        if not atr > 0 or min(entry, stop, target) <= 0:
            return None
        return {"ticker": ticker, "direction": direction, "entry": entry,
                "stop": stop, "target": target, "quote_timestamp": last[0].isoformat(),
                "source_url": source_url, "event_id": event_id,
                "status": "CONFIRMED_RESEARCH_ONLY"}
    except (OSError, ValueError, TypeError, KeyError, IndexError, OverflowError, AttributeError):
        return None


def format_confirmed_equity_telegram(plan: dict | None) -> str | None:
    """Format only an independently confirmed plan; never send a message."""
    if not isinstance(plan, dict) or plan.get("status") != "CONFIRMED_RESEARCH_ONLY":
        return None
    ticker, side = plan.get("ticker"), plan.get("direction")
    if not isinstance(ticker, str) or not _TICKER.fullmatch(ticker) or side not in ("LONG", "SHORT"):
        return None
    try:
        raw_levels = [plan[k] for k in ("entry", "stop", "target")]\n        if any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in raw_levels):\n            return None\n        entry, stop, target = (float(x) for x in raw_levels)
        if not all(isfinite(x) and x > 0 for x in (entry, stop, target)):
            return None
        if not ((stop < entry < target) if side == "LONG" else (target < entry < stop)):
            return None
        url = urlsplit(plan["source_url"])
        if (url.scheme != "https" or not url.hostname or url.username or url.password
                or url.port not in (None, 443) or len(plan["source_url"]) > 1500
                or any(ch in plan["source_url"] for ch in "\r\n\x00")):
            return None
        stamp = datetime.fromisoformat(plan["quote_timestamp"])
        if stamp.tzinfo is None:
            return None
        event = plan["event_id"]
        if (not isinstance(event, str) or not event.strip() or len(event) > 200
                or any(ch in event for ch in "\r\n\x00")):
            return None
    except (KeyError, ValueError, TypeError, AttributeError):
        return None
    return (f"🛰️ SPUTNIK — {ticker} {side} (SOLO SEGNALAZIONE)\n"
            f"Entry: {entry:.4f} | Stop: {stop:.4f} | Target: {target:.4f}\n"
            f"Quotazione: {stamp.isoformat()}\n"
            f"Evento: {event}\nFonte: {plan['source_url']}\n"
            "NESSUN ORDINE AUTOMATICO")
