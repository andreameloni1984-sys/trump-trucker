"""Focused technical analysis for one news-selected commodity."""
from __future__ import annotations
from typing import Any
import math


def _ema(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    alpha = 2.0 / (period + 1)
    value = sum(values[:period]) / period
    for item in values[period:]:
        value = alpha * item + (1 - alpha) * value
    return value


def analyze_focused_market(instrument: str, candles: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Analyze timestamp-ordered OHLCV candles; never fabricate missing data."""
    rows = []
    for row in candles or []:
        try:
            o, h, l, c = (float(row[k]) for k in ("open", "high", "low", "close"))
            v = float(row.get("volume") or 0)
            if all(math.isfinite(x) and x > 0 for x in (o, h, l, c)) and h >= max(o, c) and l <= min(o, c):
                rows.append((o, h, l, c, max(v, 0.0)))
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
    result = {"instrument": str(instrument or "N/D").upper(), "direction": "NEUTRAL", "score": 0,
              "status": "INSUFFICIENT_DATA", "candles_used": len(rows), "ema50": None,
              "ema200": None, "rsi14": None, "atr14": None, "volume_ratio": None,
              "confirmations": [], "contradictions": []}
    if len(rows) < 200:
        result["reason"] = "Servono almeno 200 candele OHLCV complete per EMA200 e struttura."
        return result
    closes = [r[3] for r in rows]
    ema50, ema200 = _ema(closes, 50), _ema(closes, 200)
    changes = [b-a for a,b in zip(closes, closes[1:])][-14:]
    gains, losses = sum(max(x,0) for x in changes)/14, sum(max(-x,0) for x in changes)/14
    rsi = 100.0 if losses == 0 and gains else 50.0 if losses == 0 else 100 - 100/(1+gains/losses)
    trs, prev = [], None
    for _,h,l,c,_ in rows:
        trs.append(h-l if prev is None else max(h-l, abs(h-prev), abs(l-prev)))
        prev = c
    atr = sum(trs[-14:])/14
    recent, prior = rows[-20:], rows[-40:-20]
    rh, ph = max(x[1] for x in recent), max(x[1] for x in prior)
    rl, pl = min(x[2] for x in recent), min(x[2] for x in prior)
    vols = [x[4] for x in rows[-21:-1] if x[4] > 0]
    vr = rows[-1][4]/(sum(vols)/len(vols)) if vols and rows[-1][4] > 0 else None
    score, yes, no = 0, [], []
    if closes[-1] > ema50 > ema200:
        score += 35; yes.append("Prezzo sopra EMA50 e EMA50 sopra EMA200")
    elif closes[-1] < ema50 < ema200:
        score -= 35; yes.append("Prezzo sotto EMA50 e EMA50 sotto EMA200")
    else:
        no.append("Allineamento EMA non univoco")
    if 52 <= rsi <= 70:
        score += 20; yes.append("RSI sostiene momentum rialzista")
    elif 30 <= rsi <= 48:
        score -= 20; yes.append("RSI sostiene momentum ribassista")
    else:
        no.append("RSI neutrale o estremo")
    if rh > ph and rl > pl:
        score += 25; yes.append("Swing: massimi e minimi crescenti")
    elif rh < ph and rl < pl:
        score -= 25; yes.append("Swing: massimi e minimi decrescenti")
    else:
        no.append("Struttura swing mista")
    if vr is not None and vr >= 1.2:
        score += 10 if score > 0 else -10 if score < 0 else 0
        yes.append("Volume sopra 1.2x la media")
    direction = "LONG" if score >= 60 else "SHORT" if score <= -60 else "NEUTRAL"
    result.update({"direction": direction, "score": min(100, abs(score)),
                   "status": "DIRECTIONAL" if direction != "NEUTRAL" else "WAIT_CONFIRMATION",
                   "ema50": round(ema50,6), "ema200": round(ema200,6), "rsi14": round(rsi,2),
                   "atr14": round(atr,6), "volume_ratio": round(vr,3) if vr is not None else None,
                   "confirmations": yes, "contradictions": no,
                   "reason": "; ".join(yes+no)})
    return result
