"""SPUTNIK CFD cart engine.

Builds a CFD watch/cart from already-ranked public-evidence candidates.
It never invents a market price, stop or target: a trade is actionable only
when a quote contains a current price plus explicit stop/target levels.
"""

from __future__ import annotations

from typing import Any

DEFAULT_RISK_PCT = 1.0
DEFAULT_CAPITAL = 300.0


def _number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _quote_for(row: dict[str, Any], quotes: dict[str, Any]) -> dict[str, Any] | None:
    keys = (
        str(row.get("ticker") or "").strip().upper(),
        str(row.get("security") or "").strip().upper(),
    )
    for key in keys:
        if not key:
            continue
        quote = quotes.get(key) or quotes.get(key.lower())
        if isinstance(quote, dict):
            return quote
    return None


def build_cfd_cart(
    ranked_rows: list[dict[str, Any]],
    quotes: dict[str, Any] | None,
    capital: float = DEFAULT_CAPITAL,
    risk_pct: float = DEFAULT_RISK_PCT,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Convert SPUTNIK evidence candidates into conservative CFD trade plans.

    Purchase evidence maps only to LONG. SHORT is intentionally unsupported
    here until a documented bearish event source is available. Missing quote,
    stop or target data produces WAIT rather than an invented trade.
    """
    capital_value = _number(capital)
    if capital_value is None:
        raise ValueError("capital must be positive")
    if risk_pct <= 0 or risk_pct > 5:
        raise ValueError("risk_pct must be between 0 and 5")
    if limit <= 0:
        return []

    quotes = quotes or {}
    cart: list[dict[str, Any]] = []

    for row in ranked_rows:
        signal = str(row.get("signal") or "")
        item: dict[str, Any] = {
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
            item["reason"] = "Evidenza SPUTNIK sotto soglia BUY: nessun CFD."
            cart.append(item)
            continue

        quote = _quote_for(row, quotes)
        if not quote:
            item["reason"] = "WAIT: quotazione corrente non disponibile."
            cart.append(item)
            continue

        entry = _number(quote.get("price"))
        stop = _number(quote.get("stop"))
        target = _number(quote.get("target"))
        if entry is None or stop is None or target is None:
            item["reason"] = "WAIT: entry, stop e target devono essere forniti dal motore dati."
            cart.append(item)
            continue

        if not (stop < entry < target):
            item["reason"] = "WAIT: livelli LONG non coerenti (stop < entry < target richiesto)."
            cart.append(item)
            continue

        risk_per_unit = entry - stop
        reward_per_unit = target - entry
        units = (capital_value * risk_pct / 100) / risk_per_unit
        item.update(
            {
                "status": "TRADE",
                "entry": entry,
                "stop": stop,
                "target": target,
                "units": round(units, 6),
                "rr": round(reward_per_unit / risk_per_unit, 2),
                "reason": "BUY SPUTNIK + quotazione e livelli verificabili.",
            }
        )
        cart.append(item)

    return cart[:limit]
