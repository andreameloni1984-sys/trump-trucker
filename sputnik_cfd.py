"""SPUTNIK CFD signal helpers.

Produces standardized CFD signals (Entry / SL / TP1 / TP2) from a
recommendation + fresh broker quote + ATR.

Never fabricates prices. If quote or ATR is missing/stale → status=PREPARE
and levels are omitted.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

DEFAULT_RISK_PCT = 1.0
DEFAULT_CAPITAL = 300.0
ATR_MULTIPLIER = 1.5          # SL distance = 1.5 * ATR
QUOTE_MAX_AGE_MIN = 30


def _number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


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
    mapping = {
        "WTI": ["WTI", "USOIL", "CL", "USOIL.cash"],
        "BRENT": ["BRENT", "UKOIL", "BRN", "UKOIL.cash"],
        "GOLD": ["GOLD", "XAUUSD", "XAU/USD", "XAUUSD.cash"],
        "SILVER": ["SILVER", "XAGUSD", "XAG/USD"],
        "COPPER": ["COPPER", "HG", "XCUUSD"],
        "NATURAL_GAS": ["NATGAS", "NG", "NATURALGAS"],
        "NASDAQ100": ["NASDAQ100", "NAS100", "USTEC", "QQQ"],
    }
    keys = mapping.get(instrument, [instrument])
    for key in keys:
        q = quotes.get(key) or quotes.get(key.lower()) or quotes.get(key.upper())
        if isinstance(q, dict):
            return q
    return None


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
        "direction": "LONG" if bias == "LONG" else "SHORT" if bias == "SHORT" else "NEUTRAL",
        "score": score,
        "reason": reason,
        "confirmation": confirmation,
        "status": "BIAS_ONLY",
    })

    quotes = quotes or {}
    quote = _find_quote(instrument, quotes)
    if not quote or not _quote_is_fresh(quote):
        base["status"] = "PREPARE"
        base["reason"] += " | Quotazione fresca non disponibile."
        return base

    entry = _number(quote.get("price") or quote.get("bid") or quote.get("last"))
    atr = _number(quote.get("atr") or quote.get("ATR") or quote.get("atr_14"))
    if entry is None or atr is None:
        base["status"] = "PREPARE"
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
