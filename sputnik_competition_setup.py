"""Competition-style execution filter for a single news-selected commodity.

Inspired by the publicly described Direction -> Location -> Aggression workflow:
trend context, VWAP location, then a confirmed breakout/retest with volume.
OHLCV volume is only a proxy for aggression; this is NOT exchange order flow.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
import math


def _ema(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    alpha = 2.0 / (period + 1)
    result = sum(values[:period]) / period
    for value in values[period:]:
        result = alpha * value + (1 - alpha) * result
    return result


def _utc_day(value: Any) -> str | None:
    try:
        if isinstance(value, (int, float)):
            dt = datetime.fromtimestamp(float(value), tz=timezone.utc)
        else:
            raw = str(value).strip().replace("Z", "+00:00")
            dt = datetime.fromisoformat(raw)
            if dt.tzinfo is None:
                return None
            dt = dt.astimezone(timezone.utc)
        return dt.date().isoformat()
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def evaluate_competition_setup(instrument: str, candles: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Return a confirmed setup only when trend, VWAP, retest and volume align."""
    rows = []
    for candle in candles or []:
        try:
            o, h, l, c = (float(candle[k]) for k in ("open", "high", "low", "close"))
            v = float(candle.get("volume") or 0)
            stamp = candle.get("timestamp") or candle.get("time") or candle.get("datetime")
            day = _utc_day(stamp)
            if (day and all(math.isfinite(x) and x > 0 for x in (o,h,l,c))
                    and h >= max(o,c) and l <= min(o,c) and math.isfinite(v) and v > 0):
                rows.append({"open":o,"high":h,"low":l,"close":c,"volume":v,"day":day})
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
    out = {"instrument":str(instrument or "N/D").upper(),"direction":"NEUTRAL",
           "status":"WAIT","score":0,"entry":None,"stop_reference":None,
           "vwap":None,"atr14":None,"volume_ratio":None,
           "confirmations":[],"reasons":[],"method":"DIRECTION_LOCATION_AGGRESSION"}
    if len(rows) < 60:
        out["reasons"] = ["Servono almeno 60 candele OHLCV timestamped e ordinate."]
        return out
    day = rows[-1]["day"]
    today = [r for r in rows if r["day"] == day]
    if len(today) < 30 or len(rows) < 50:
        out["reasons"] = ["Storico intraday della sessione UTC insufficiente."]
        return out
    closes = [r["close"] for r in rows]
    ema20, ema50 = _ema(closes,20), _ema(closes,50)
    pv = sum(((r["high"]+r["low"]+r["close"])/3)*r["volume"] for r in today)
    vol = sum(r["volume"] for r in today)
    vwap = pv/vol if vol else None
    trs=[]
    for i,r in enumerate(rows):
        prev=rows[i-1]["close"] if i else r["close"]
        trs.append(max(r["high"]-r["low"],abs(r["high"]-prev),abs(r["low"]-prev)))
    atr=sum(trs[-14:])/14
    prior=rows[-31:-1]
    resistance=max(r["high"] for r in prior)
    support=min(r["low"] for r in prior)
    recent=rows[-3:]
    avgvol=sum(r["volume"] for r in rows[-21:-1])/20
    volume_ratio=rows[-1]["volume"]/avgvol if avgvol else None
    last=rows[-1]
    # Retest: previous candle traded through the breakout level, last candle
    # closed back beyond it, with directional candle body and relative volume.
    long_retest=(rows[-2]["low"] <= resistance*1.0015 and last["close"] > resistance
                 and last["close"] > last["open"])
    short_retest=(rows[-2]["high"] >= support*0.9985 and last["close"] < support
                  and last["close"] < last["open"])
    trend_long=last["close"] > ema20 > ema50
    trend_short=last["close"] < ema20 < ema50
    vwap_long=last["close"] > vwap
    vwap_short=last["close"] < vwap
    vol_ok=volume_ratio is not None and volume_ratio >= 1.2
    long_ok=trend_long and vwap_long and long_retest and vol_ok
    short_ok=trend_short and vwap_short and short_retest and vol_ok
    confirms=[]
    if trend_long or trend_short: confirms.append("Direzione: EMA20/EMA50 allineate")
    if vwap_long or vwap_short: confirms.append("Location: prezzo dalla parte coerente del VWAP intraday")
    if long_retest or short_retest: confirms.append("Aggression proxy: breakout con retest e candela direzionale")
    if vol_ok: confirms.append("Volume ultimo candle >= 1.2x media delle 20 candele precedenti")
    direction="LONG" if long_ok and not short_ok else "SHORT" if short_ok and not long_ok else "NEUTRAL"
    out.update({"direction":direction,"status":"SETUP_CONFIRMED" if direction!="NEUTRAL" else "WAIT",
                "score":100 if direction!="NEUTRAL" else 0,"vwap":round(vwap,6),
                "atr14":round(atr,6),"volume_ratio":round(volume_ratio,3) if volume_ratio is not None else None,
                "entry":last["close"] if direction!="NEUTRAL" else None,
                "stop_reference":round(resistance-0.15*atr,6) if direction=="LONG" else round(support+0.15*atr,6) if direction=="SHORT" else None,
                "confirmations":confirms,
                "reasons":[] if direction!="NEUTRAL" else ["Non sono presenti tutte le conferme: trend + VWAP + breakout/retest + volume."]})
    return out
