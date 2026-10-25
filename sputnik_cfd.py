"""SPUTNIK CFD planning helpers.

Never fabricates quotes. Conditional plans use the current broker quote and ATR
when both are available; they remain WAIT until a price trigger is confirmed.
"""
from __future__ import annotations
from datetime import datetime, timezone
import math
from typing import Any

DEFAULT_RISK_PCT = 1.0
DEFAULT_CAPITAL = 300.0


def _number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def _quote_for(row: dict[str, Any], quotes: dict[str, Any]) -> dict[str, Any] | None:
    keys = (str(row.get("ticker") or "").strip().upper(),
            str(row.get("security") or "").strip().upper())
    for key in keys:
        quote = quotes.get(key) or quotes.get(key.lower())
        if isinstance(quote, dict):
            return quote
    return None


def _quote_is_fresh(quote: dict[str, Any], max_age_minutes: int = 30) -> bool:
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


def build_conditional_trade_plan(plan: dict[str, Any], quotes: dict[str, Any] | None,
                                 risk_pct: float = DEFAULT_RISK_PCT) -> dict[str, Any]:
    """Calculate indicative SL/TP from a fresh broker quote and ATR.

    Uses 1.5 ATR stop and 1R/2R targets. It is only a PREPARE plan unless the
    quote explicitly carries trigger_confirmed=True. No price or ATR is guessed.
    """
    if not 0 < risk_pct <= 5:
        raise ValueError("risk_pct must be between 0 and 5")
    candidate = str(plan.get("candidate") or "").upper()
    keys = []
    if "BRENT" in candidate: keys = ["BRENT", "UKOIL", "BRN"]
    elif "WTI" in candidate: keys = ["WTI", "USOIL", "CL"]
    elif "ORO" in candidate or "GOLD" in candidate: keys = ["GOLD", "XAUUSD", "XAU/USD"]
    elif "NASDAQ" in candidate: keys = ["NASDAQ100", "NAS100", "USTEC", "QQQ"]
    quotes = quotes or {}
    quote = next((quotes.get(k) or quotes.get(k.lower()) for k in keys
                  if isinstance(quotes.get(k) or quotes.get(k.lower()), dict)), None)
    result = {"candidate": candidate or "N/D", "status": "WAIT", "entry": None,
              "stop": None, "tp1": None, "tp2": None, "rr_tp1": 1.0,
              "rr_tp2": 2.0, "quote_time": None,
              "reason": "Quotazione broker aggiornata o ATR non disponibili."}
    if not quote:
        return result
    result["quote_time"] = quote.get("timestamp") or quote.get("updated_at") or quote.get("as_of")
    if not _quote_is_fresh(quote):
        result["reason"] = "Quotazione assente, senza timestamp o più vecchia di 30 minuti."
        return result
    entry = _number(quote.get("price"))
    atr = _number(quote.get("atr") or quote.get("ATR") or quote.get("atr_14"))
    if entry is None or atr is None:
        return result
    bias = str(plan.get("bias") or "").upper()
    direction = "SHORT" if "SHORT" in bias else "LONG"
    distance = 1.5 * atr
    if direction == "LONG":
        stop, tp1, tp2 = entry - distance, entry + distance, entry + 2 * distance
    else:
        stop, tp1, tp2 = entry + distance, entry - distance, entry - 2 * distance

    # Validate the derived levels after rounding, not just their source inputs.
    # Large ATR relative to price can create non-positive targets/stops, while
    # small distances can collapse distinct levels to the same rounded price.
    rounded_entry, rounded_stop = round(entry, 6), round(stop, 6)
    rounded_tp1, rounded_tp2 = round(tp1, 6), round(tp2, 6)
    derived_levels = (rounded_entry, rounded_stop, rounded_tp1, rounded_tp2)
    levels_are_positive_finite = all(
        math.isfinite(value) and value > 0 for value in derived_levels
    )
    if direction == "LONG":
        levels_are_ordered = rounded_stop < rounded_entry < rounded_tp1 < rounded_tp2
    else:
        levels_are_ordered = rounded_tp2 < rounded_tp1 < rounded_entry < rounded_stop
    if not levels_are_positive_finite or not levels_are_ordered:
        result["reason"] = (
            "Livelli SL/TP derivati non validi: non positivi, non finiti "
            "o coincidenti dopo arrotondamento; piano mantenuto WAIT."
        )
        return result

    result.update({"direction": direction, "entry": rounded_entry,
                   "stop": rounded_stop, "tp1": rounded_tp1, "tp2": rounded_tp2,
                   "atr": round(atr, 6),
                   "status": "TRIGGER CONFIRMED" if quote.get("trigger_confirmed") is True else "PREPARE",
                   "reason": "Livelli indicativi calcolati da prezzo broker e ATR; trigger tecnico da confermare."})
    return result


def build_cfd_cart(ranked_rows: list[dict[str, Any]], quotes: dict[str, Any] | None,
                   capital: float = DEFAULT_CAPITAL, risk_pct: float = DEFAULT_RISK_PCT,
                   limit: int = 3) -> list[dict[str, Any]]:
    """Create a CFD cart only from verified prices and explicit SL/TP."""
    capital_value = _number(capital)
    if capital_value is None:
        raise ValueError("capital must be positive")
    if not 0 < risk_pct <= 5:
        raise ValueError("risk_pct must be between 0 and 5")
    if limit <= 0:
        return []
    risk_budget = capital_value * (risk_pct / 100)
    if not math.isfinite(risk_budget) or risk_budget <= 0:
        raise ValueError("risk budget must be finite and positive")
    cart = []
    for row in ranked_rows:
        signal = str(row.get("signal") or "")
        item = {"security": row.get("security") or "N/D",
                "company": row.get("company") or "N/D", "score": row.get("score", 0),
                "evidence_signal": signal, "direction": "LONG" if signal == "COMPRA" else "WAIT",
                "status": "WAIT", "entry": None, "stop": None, "target": None,
                "risk_eur": round(risk_budget, 2), "units": None, "reason": ""}
        if signal != "COMPRA":
            item["reason"] = "Evidenza SPUTNIK sotto soglia BUY: nessun CFD."
            cart.append(item); continue
        quote = _quote_for(row, quotes or {})
        if not quote:
            item["reason"] = "WAIT: quotazione corrente non disponibile."
            cart.append(item); continue
        entry, stop, target = (_number(quote.get(k)) for k in ("price", "stop", "target"))
        if entry is None or stop is None or target is None or not _quote_is_fresh(quote):
            item["reason"] = "WAIT: servono prezzo recente con timestamp e livelli SL/TP validi."
            cart.append(item); continue
        if not stop < entry < target:
            item["reason"] = "WAIT: livelli LONG non coerenti (stop < entry < target richiesto)."
            cart.append(item); continue
        risk_per_unit = entry - stop
        reward_per_unit = target - entry
        units = risk_budget / risk_per_unit
        rr = reward_per_unit / risk_per_unit
        if not all(math.isfinite(value) and value > 0 for value in
                   (risk_per_unit, reward_per_unit, units, rr)):
            item["reason"] = "WAIT: calcoli di rischio/rendimento non finiti o non rappresentabili."
            cart.append(item); continue
        rounded_units = round(units, 6)
        rounded_rr = round(rr, 2)
        if not all(math.isfinite(value) and value > 0 for value in (rounded_units, rounded_rr)):
            item["reason"] = "WAIT: unità o rapporto rischio/rendimento non validi dopo arrotondamento."
            cart.append(item); continue
        item.update({"status": "TRADE", "entry": entry, "stop": stop, "target": target,
                     "units": rounded_units, "rr": rounded_rr,
                     "reason": "BUY SPUTNIK + quotazione recente e livelli verificabili."})
        cart.append(item)
    return cart[:limit]
