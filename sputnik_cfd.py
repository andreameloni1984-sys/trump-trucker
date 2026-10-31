"""SPUTNIK CFD signal helpers.

Produces standardized CFD signals (Entry / SL / TP1 / TP2) from a
recommendation + fresh broker quote + ATR.

Never fabricates prices. If quote or ATR is missing/stale → status=WAIT
and levels are omitted; PREPARE is reserved for a fresh, priced setup below trigger.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import math
import json
import urllib.parse
import urllib.request

DEFAULT_RISK_PCT = 1.0
DEFAULT_CAPITAL = 300.0
ATR_MULTIPLIER = 1.5          # SL distance = 1.5 * ATR
QUOTE_MAX_AGE_MIN = 30


def _number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def _quote_is_fresh(quote: dict[str, Any], max_age_minutes: int = QUOTE_MAX_AGE_MIN) -> bool:
    stamp = quote.get("timestamp") or quote.get("updated_at") or quote.get("as_of")
    if not stamp:
        return False
    try:
        dt = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds()
        return -60 <= age <= max_age_minutes * 60
    except (TypeError, ValueError):
        return False


def _find_quote(instrument: str, quotes: dict[str, Any]) -> dict[str, Any] | None:
    """Map common commodity names to possible quote keys."""
    instrument = (instrument or "").upper()
    # Decision scenarios use display labels such as "ORO (XAU/USD)" and
    # "BRENT (petrolio)". Resolve the instrument family before quote lookup.
    base_name = instrument.split("(", 1)[0].strip()
    if base_name in {"ORO", "GOLD"}:
        base_name = "GOLD"
    elif base_name.startswith("BRENT"):
        base_name = "BRENT"
    elif base_name.startswith("WTI") or base_name == "PETROLIO WTI":
        base_name = "WTI"
    elif base_name.startswith("NASDAQ"):
        base_name = "NASDAQ100"
    mapping = {
        "WTI": ["WTI", "USOIL", "CL", "USOIL.cash"],
        "BRENT": ["BRENT", "UKOIL", "BRN", "UKOIL.cash"],
        "GOLD": ["GOLD", "XAUUSD", "XAU/USD", "XAUUSD.cash"],
        "SILVER": ["SILVER", "XAGUSD", "XAG/USD"],
        "COPPER": ["COPPER", "HG", "XCUUSD"],
        "NATURAL_GAS": ["NATGAS", "NG", "NATURALGAS"],
        "NASDAQ100": ["NASDAQ100", "NAS100", "USTEC", "QQQ"],
    }
    keys = mapping.get(base_name, [base_name])
    for key in keys:
        q = quotes.get(key) or quotes.get(key.lower()) or quotes.get(key.upper())
        if isinstance(q, dict):
            return q
    return None



YAHOO_FUTURES = {
    "GOLD": "GC=F", "ORO": "GC=F", "SILVER": "SI=F", "ARGENTO": "SI=F",
    "COPPER": "HG=F", "RAME": "HG=F", "WTI": "CL=F", "PETROLIO WTI": "CL=F",
    "BRENT": "BZ=F", "NATURAL_GAS": "NG=F", "GAS NATURALE": "NG=F",
    "WHEAT": "ZW=F", "GRANO": "ZW=F", "CORN": "ZC=F", "MAIS": "ZC=F",
    "SOYBEAN": "ZS=F", "SOIA": "ZS=F",
}


def fetch_yahoo_quote(instrument: str, timeout: int = 8) -> dict[str, Any] | None:
    """Fetch latest Yahoo 1-minute futures candle and calculate ATR(14)."""
    label = str(instrument or "").upper().split("(", 1)[0].strip()
    symbol = YAHOO_FUTURES.get(label)
    if not symbol:
        for name, ticker in YAHOO_FUTURES.items():
            if label.startswith(name):
                symbol = ticker
                break
    if not symbol:
        return None
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + urllib.parse.quote(symbol, safe="=")
    url += "?range=1d&interval=1m&includePrePost=true"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 SputnikMarketData/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        result = payload["chart"]["result"][0]
        timestamps = result.get("timestamp") or []
        quote_data = result["indicators"]["quote"][0]
        highs, lows, closes = quote_data.get("high") or [], quote_data.get("low") or [], quote_data.get("close") or []
        candles = [(float(h), float(l), float(cl), int(ts))
                   for h, l, cl, ts in zip(highs, lows, closes, timestamps)
                   if h is not None and l is not None and cl is not None]
        if len(candles) < 15:
            return None
        true_ranges = []
        previous_close = None
        for high, low, close, _ in candles:
            tr = high - low if previous_close is None else max(
                high - low, abs(high - previous_close), abs(low - previous_close)
            )
            true_ranges.append(tr)
            previous_close = close
        atr = sum(true_ranges[-14:]) / 14
        high, low, close, stamp = candles[-1]
        return {
            "price": close, "atr": atr,
            "timestamp": datetime.fromtimestamp(stamp, timezone.utc).isoformat(),
            "provider": "Yahoo Finance chart (1m futures)", "symbol": symbol,
            "candle_high": high, "candle_low": low,
        }
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        return None



SILV_SPOT_KEYS = {
    "GOLD": "gold", "ORO": "gold",
    "SILVER": "silver", "ARGENTO": "silver",
    "COPPER": "copper", "RAME": "copper",
}


def fetch_silv_reference(instrument: str, timeout: int = 6) -> dict[str, Any] | None:
    """Free keyless spot reference; never substitutes a futures execution quote."""
    label = str(instrument or "").upper().split("(", 1)[0].strip()
    key = SILV_SPOT_KEYS.get(label)
    if not key:
        return None
    request = urllib.request.Request(
        "https://data.silv.app/commodities.json",
        headers={"User-Agent": "Mozilla/5.0 SputnikMultiSource/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        item = (payload.get("commodities") or {}).get(key) or {}
        price = _number(item.get("price"))
        stamp = item.get("last_updated") or item.get("timestamp")
        if price is None or not stamp:
            return None
        reference = {
            "price": price, "timestamp": stamp,
            "provider": "SILV DATA spot reference",
            "symbol": key.upper(), "unit": item.get("unit"),
        }
        return reference if _quote_is_fresh(reference, 30) else None
    except (OSError, ValueError, KeyError, TypeError):
        return None


def attach_silv_crosscheck(quote: dict[str, Any], instrument: str) -> dict[str, Any]:
    """Add spot/futures comparison metadata; keep Yahoo futures as execution basis."""
    reference = fetch_silv_reference(instrument)
    if not reference:
        quote["crosscheck_provider"] = "SILV DATA"
        quote["crosscheck_status"] = "UNAVAILABLE_OR_STALE"
        return quote
    price = _number(quote.get("price"))
    ref_price = _number(reference.get("price"))
    quote["crosscheck_provider"] = reference["provider"]
    quote["crosscheck_price"] = ref_price
    quote["crosscheck_timestamp"] = reference["timestamp"]
    quote["crosscheck_unit"] = reference.get("unit")
    if price and ref_price:
        quote["crosscheck_spread_pct"] = round(abs(price - ref_price) / ref_price * 100, 3)
        quote["crosscheck_status"] = "SPOT_VS_FUTURES_BASIS_CHECK"
    else:
        quote["crosscheck_status"] = "UNCOMPARABLE"
    return quote


def build_cfd_signal(
    recommendation: dict[str, Any] | None,
    quotes: dict[str, Any] | None = None,
    risk_pct: float = DEFAULT_RISK_PCT,
) -> dict[str, Any]:
    """Build a standardized CFD signal dict from a SPUTNIK recommendation.

    Returns a dict with keys: instrument, direction, entry, stop, tp1, tp2,
    atr, score, status, reason, confirmation, risk_pct, timestamp.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    base = {
        "instrument": "N/D",
        "direction": "WAIT",
        "entry": None,
        "stop": None,
        "tp1": None,
        "tp2": None,
        "atr": None,
        "score": 0,
        "status": "NO_SIGNAL",
        "reason": "Nessuna raccomandazione disponibile.",
        "confirmation": "Conferma tecnica obbligatoria.",
        "risk_pct": risk_pct,
        "timestamp": now,
        "paper_only": True,
    }
    if not recommendation:
        return base

    instrument = str(recommendation.get("instrument") or "N/D").upper()
    bias = str(recommendation.get("bias") or "NEUTRAL").upper()
    score = float(recommendation.get("score") or 0)
    reason = str(recommendation.get("reason") or "")
    confirmation = str(recommendation.get("confirmation") or "Verifica prezzo e volume live.")

    base.update({
        "instrument": instrument,
        "direction": "LONG" if "LONG" in bias else "SHORT" if "SHORT" in bias else "NEUTRAL",
        "score": score,
        "reason": reason,
        "confirmation": confirmation,
        "status": "BIAS_ONLY",
    })

    quotes = quotes or {}
    quote = _find_quote(instrument, quotes)
    if not quote or not _quote_is_fresh(quote):
        # Pull a fresh public 1m futures candle and calculate ATR automatically.
        quote = fetch_yahoo_quote(instrument)
    if quote and _quote_is_fresh(quote):
        quote = attach_silv_crosscheck(quote, instrument)
    if not quote or not _quote_is_fresh(quote):
        base["status"] = "WAIT"
        base["reason"] += " | Quotazione live/fresca non disponibile anche dal fallback Yahoo Finance."
        return base

    entry = _number(quote.get("price") or quote.get("bid") or quote.get("last"))
    atr = _number(quote.get("atr") or quote.get("ATR") or quote.get("atr_14"))
    if entry is None or atr is None:
        base["status"] = "WAIT"
        base["reason"] += " | Prezzo o ATR mancanti."
        return base

    distance = ATR_MULTIPLIER * atr
    if base["direction"] == "LONG":
        stop = entry - distance
        tp1 = entry + distance          # 1R
        tp2 = entry + 2 * distance      # 2R
    elif base["direction"] == "SHORT":
        stop = entry + distance
        tp1 = entry - distance
        tp2 = entry - 2 * distance
    else:
        base["status"] = "NEUTRAL"
        return base

    base.update({
        "entry": round(entry, 4),
        "stop": round(stop, 4),
        "tp1": round(tp1, 4),
        "tp2": round(tp2, 4),
        "atr": round(atr, 4),
        "status": "SIGNAL" if score >= 70 else "PREPARE",
        "quote_time": quote.get("timestamp") or quote.get("updated_at"),
        "quote_provider": quote.get("provider") or "state/provider",
        "quote_symbol": quote.get("symbol") or instrument,
        "crosscheck_provider": quote.get("crosscheck_provider"),
        "crosscheck_status": quote.get("crosscheck_status"),
        "crosscheck_price": quote.get("crosscheck_price"),
        "crosscheck_spread_pct": quote.get("crosscheck_spread_pct"),
    })
    return base


def format_cfd_signal(signal: dict[str, Any]) -> str:
    """Telegram-ready standardized CFD signal message."""
    if not signal or signal.get("status") == "NO_SIGNAL":
        return (
            "🛰️ SPUTNIK — SEGNALE CFD\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🟡 Nessun segnale operativo.\n"
            "Monitorare: WTI, BRENT, GOLD.\n"
            "⚠️ PAPER ONLY"
        )

    direction = signal.get("direction", "NEUTRAL")
    icon = "🟢" if direction == "LONG" else "🔴" if direction == "SHORT" else "🟡"
    status = signal.get("status", "PREPARE")

    lines = [
        f"{icon} SPUTNIK CFD SIGNAL",
        "━━━━━━━━━━━━━━━━━━",
        "🧪 PAPER ONLY • NESSUN ORDINE AUTOMATICO",
        f"🕒 {signal.get('timestamp', '')}",
        "",
        f"📈 STRUMENTO: {signal.get('instrument')}",
        f"📌 DIREZIONE: {direction}",
        f"📊 SCORE: {signal.get('score', 0):.0f}/100",
        f"🧪 STATO: {status}",
    ]

    if signal.get("entry") is not None:
        lines.extend([
            "",
            f"💰 ENTRY: {signal['entry']}",
            f"🛑 SL:    {signal['stop']}",
            f"🎯 TP1:   {signal['tp1']} (1R)",
            f"🎯 TP2:   {signal['tp2']} (2R)",
            f"📏 ATR:   {signal.get('atr')}",
        ])
    else:
        lines.append("\n⏳ Livelli non disponibili (manca quote/ATR fresca).")

    lines.extend([
        "",
        f"📌 MOTIVO: {signal.get('reason', '')[:280]}",
        f"✅ CONFERMA: {signal.get('confirmation', '')}",
        f"⚠️ RISK: {signal.get('risk_pct', 1.0):.1f}% max",
        "",
        "⚠️ Segnale informativo. Verifica contesto e rischio. Nessun ordine inviato.",
    ])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Legacy helpers kept for backward compatibility
# ---------------------------------------------------------------------------

def _quote_for(row: dict[str, Any], quotes: dict[str, Any]) -> dict[str, Any] | None:
    keys = (
        str(row.get("ticker") or "").strip().upper(),
        str(row.get("security") or "").strip().upper(),
    )
    for key in keys:
        quote = quotes.get(key) or quotes.get(key.lower())
        if isinstance(quote, dict):
            return quote
    return None


def build_conditional_trade_plan(
    plan: dict[str, Any],
    quotes: dict[str, Any] | None,
    risk_pct: float = DEFAULT_RISK_PCT,
) -> dict[str, Any]:
    """Legacy wrapper — prefer build_cfd_signal for new code."""
    rec = {
        "instrument": plan.get("candidate"),
        "bias": plan.get("bias"),
        "score": plan.get("score", 0),
        "reason": plan.get("reason", ""),
    }
    return build_cfd_signal(rec, quotes, risk_pct)


def build_cfd_cart(
    ranked_rows: list[dict[str, Any]],
    quotes: dict[str, Any] | None,
    capital: float = DEFAULT_CAPITAL,
    risk_pct: float = DEFAULT_RISK_PCT,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Legacy cart builder. Prefer individual signals for new flows."""
    capital_value = _number(capital)
    if capital_value is None:
        raise ValueError("capital must be positive")
    if not 0 < risk_pct <= 5:
        raise ValueError("risk_pct must be between 0 and 5")
    if limit <= 0:
        return []
    cart = []
    for row in ranked_rows[:limit]:
        signal = str(row.get("signal") or "")
        item = {
            "security": row.get("security") or "N/D",
            "company": row.get("company") or "N/D",
            "score": row.get("score", 0),
            "evidence_signal": signal,
            "direction": "LONG" if signal == "COMPRA" else "WAIT",
            "status": "WAIT",
            "entry": None,
            "stop": None,
            "target": None,
            "risk_eur": round(capital_value * risk_pct / 100, 2),
            "units": None,
            "reason": "",
        }
        if signal != "COMPRA":
            item["reason"] = "Evidenza sotto soglia BUY."
            cart.append(item)
            continue
        quote = _quote_for(row, quotes or {})
        if not quote or not _quote_is_fresh(quote):
            item["reason"] = "WAIT: quotazione fresca non disponibile."
            cart.append(item)
            continue
        entry = _number(quote.get("price"))
        stop = _number(quote.get("stop"))
        target = _number(quote.get("target"))
        if entry is None or stop is None or target is None or not (stop < entry < target):
            item["reason"] = "WAIT: livelli non coerenti."
            cart.append(item)
            continue
        risk_per_unit = entry - stop
        units = (capital_value * risk_pct / 100) / risk_per_unit
        item.update({
            "status": "TRADE",
            "entry": entry,
            "stop": stop,
            "target": target,
            "units": round(units, 6),
            "rr": round((target - entry) / risk_per_unit, 2),
            "reason": "BUY + quote fresca.",
        })
        cart.append(item)
    return cart
