"""Competition-style D-L-A evaluator for a single news-selected commodity.

Direction = EMA context; Location = VWAP; Aggression = breakout/retest plus
relative OHLCV volume. A preliminary context bias remains visible before the
trigger. OHLCV volume is only a proxy, never DOM/footprint/order flow.
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


def _utc_stamp(value: Any) -> float | None:
    try:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            stamp = float(value)
            return stamp if math.isfinite(stamp) and stamp > 0 else None
        raw = str(value or "").strip().replace("Z", "+00:00")
        if not raw:
            return None
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            return None
        return dt.astimezone(timezone.utc).timestamp()
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def evaluate_competition_setup(
    instrument: str,
    candles: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """Expose D-L-A context early; confirm only with trigger, volume and stop."""
    rows = []
    for candle in candles or []:
        try:
            o, h, l, c = (
                float(candle[k]) for k in ("open", "high", "low", "close")
            )
            v = float(candle.get("volume") or 0)
            stamp = _utc_stamp(
                candle.get("timestamp") or candle.get("time") or candle.get("datetime")
            )
            if (
                stamp is not None
                and all(math.isfinite(x) and x > 0 for x in (o, h, l, c))
                and h >= max(o, c)
                and l <= min(o, c)
                and math.isfinite(v)
                and v > 0
            ):
                rows.append({
                    "open": o, "high": h, "low": l, "close": c,
                    "volume": v, "timestamp": stamp,
                    "day": datetime.fromtimestamp(stamp, timezone.utc).date().isoformat(),
                })
        except (KeyError, TypeError, ValueError, OverflowError, OSError):
            continue

    out = {
        "instrument": str(instrument or "N/D").upper(),
        "direction": "NEUTRAL",
        "bias": "NEUTRAL / NO_DIRECTION",
        "status": "INSUFFICIENT_DATA",
        "setup_status": "INSUFFICIENT_DATA",
        "score": 0,
        "entry": None,
        "stop_reference": None,
        "vwap": None,
        "atr14": None,
        "volume_ratio": None,
        "context_direction": "NEUTRAL",
        "location_direction": "NEUTRAL",
        "trigger_direction": "NEUTRAL",
        "confirmations": [],
        "missing_conditions": [],
        "reasons": [],
        "method": "DIRECTION_LOCATION_AGGRESSION",
        "aggression_source": "OHLCV_VOLUME_PROXY",
        "order_flow_confirmed": False,
    }

    if len(rows) < 60:
        out["missing_conditions"] = ["INSUFFICIENT_TIMESTAMPED_OHLCV"]
        out["reasons"] = ["Servono almeno 60 candele OHLCV valide e timestamped."]
        return out

    if any(
        rows[index]["timestamp"] >= rows[index + 1]["timestamp"]
        for index in range(len(rows) - 1)
    ):
        out["status"] = "INVALID_DATA"
        out["setup_status"] = "INVALID_DATA"
        out["missing_conditions"] = ["CANDLE_ORDER_INVALID"]
        out["reasons"] = ["Le candele devono essere strettamente ordinate per timestamp UTC."]
        return out

    day = rows[-1]["day"]
    today = [row for row in rows if row["day"] == day]
    if len(today) < 30:
        out["missing_conditions"] = ["INSUFFICIENT_CURRENT_SESSION_HISTORY"]
        out["reasons"] = ["Storico intraday della sessione UTC insufficiente: servono 30 candele."]
        return out

    closes = [row["close"] for row in rows]
    ema20, ema50 = _ema(closes, 20), _ema(closes, 50)
    if ema20 is None or ema50 is None:
        out["missing_conditions"] = ["INSUFFICIENT_TREND_HISTORY"]
        out["reasons"] = ["Storico insufficiente per EMA20/EMA50."]
        return out

    pv = sum(
        ((row["high"] + row["low"] + row["close"]) / 3) * row["volume"]
        for row in today
    )
    volume_today = sum(row["volume"] for row in today)
    vwap = pv / volume_today if volume_today else None

    true_ranges = []
    for index, row in enumerate(rows):
        previous_close = rows[index - 1]["close"] if index else row["close"]
        true_ranges.append(max(
            row["high"] - row["low"],
            abs(row["high"] - previous_close),
            abs(row["low"] - previous_close),
        ))
    atr = sum(true_ranges[-14:]) / 14

    prior = rows[-31:-1]
    resistance = max(row["high"] for row in prior)
    support = min(row["low"] for row in prior)
    last = rows[-1]
    previous = rows[-2]
    average_volume = sum(row["volume"] for row in rows[-21:-1]) / 20
    volume_ratio = last["volume"] / average_volume if average_volume else None

    trend_long = last["close"] > ema20 > ema50
    trend_short = last["close"] < ema20 < ema50
    trend_direction = (
        "LONG" if trend_long else "SHORT" if trend_short else "NEUTRAL"
    )
    vwap_long = vwap is not None and last["close"] > vwap
    vwap_short = vwap is not None and last["close"] < vwap
    location_direction = (
        "LONG" if vwap_long else "SHORT" if vwap_short else "NEUTRAL"
    )

    long_retest = (
        previous["low"] <= resistance * 1.0015
        and last["close"] > resistance
        and last["close"] > last["open"]
    )
    short_retest = (
        previous["high"] >= support * 0.9985
        and last["close"] < support
        and last["close"] < last["open"]
    )
    trigger_direction = (
        "LONG" if long_retest else "SHORT" if short_retest else "NEUTRAL"
    )
    volume_ok = volume_ratio is not None and volume_ratio >= 1.2

    # A directional D-L context bias needs trend and VWAP to agree.
    bias = (
        trend_direction
        if trend_direction in {"LONG", "SHORT"} and location_direction == trend_direction
        else "NEUTRAL"
    )
    trigger_aligned = bias in {"LONG", "SHORT"} and trigger_direction == bias
    candidate_entry = last["close"] if bias in {"LONG", "SHORT"} else None
    candidate_stop = (
        resistance - 0.15 * atr if bias == "LONG"
        else support + 0.15 * atr if bias == "SHORT"
        else None
    )
    structural_stop_ok = (
        candidate_entry is not None
        and candidate_stop is not None
        and (
            candidate_stop < candidate_entry if bias == "LONG"
            else candidate_stop > candidate_entry
        )
        and math.isfinite(candidate_stop)
        and candidate_stop > 0
    )
    confirmed = trigger_aligned and volume_ok and structural_stop_ok

    score = 30 if trend_direction in {"LONG", "SHORT"} else 0
    if bias in {"LONG", "SHORT"}:
        score += 20
    if trigger_aligned:
        score += 25
    if trigger_aligned and volume_ok:
        score += 15
    if confirmed:
        score += 10

    confirmations = []
    if trend_direction in {"LONG", "SHORT"}:
        confirmations.append(f"Direction: EMA20/EMA50 {trend_direction}")
    if location_direction in {"LONG", "SHORT"}:
        confirmations.append(f"Location: VWAP {location_direction}")
    if bias in {"LONG", "SHORT"}:
        confirmations.append(f"Contesto D-L: bias {bias}")
    if trigger_direction in {"LONG", "SHORT"}:
        confirmations.append(f"Trigger: breakout/retest {trigger_direction}")
    if volume_ok:
        confirmations.append(
            f"Aggression proxy: volume {volume_ratio:.2f}x media 20 candele"
        )

    missing = []
    if trend_direction not in {"LONG", "SHORT"}:
        missing.append("DIRECTION_NOT_CONFIRMED")
    if bias not in {"LONG", "SHORT"}:
        missing.append("LOCATION_NOT_ALIGNED_WITH_TREND")
    if not trigger_aligned:
        missing.append("TRIGGER_NOT_CONFIRMED")
    if not volume_ok:
        missing.append("AGGRESSION_PROXY_BELOW_1_2X")
    if trigger_aligned and volume_ok and not structural_stop_ok:
        missing.append("STRUCTURAL_STOP_NOT_VALID")

    status = (
        "SETUP_CONFIRMED" if confirmed
        else "EARLY_SETUP" if bias in {"LONG", "SHORT"}
        else "NO_DIRECTION"
    )
    reasons = []
    if status == "NO_DIRECTION":
        reasons.append(
            "NO_DIRECTION: EMA20/EMA50 e VWAP non sostengono lo stesso lato."
        )
    elif status == "EARLY_SETUP":
        reasons.append(
            f"BIAS {bias} mantenuto; setup non confermato: {', '.join(missing)}."
        )

    out.update({
        "direction": bias,
        "bias": bias if bias in {"LONG", "SHORT"} else "NEUTRAL / NO_DIRECTION",
        "status": status,
        "setup_status": status,
        "score": min(100, score),
        "vwap": round(vwap, 6) if vwap is not None else None,
        "atr14": round(atr, 6),
        "volume_ratio": round(volume_ratio, 3) if volume_ratio is not None else None,
        "context_direction": trend_direction,
        "location_direction": location_direction,
        "trigger_direction": trigger_direction,
        "entry": round(candidate_entry, 6) if confirmed else None,
        "stop_reference": round(candidate_stop, 6) if confirmed else None,
        "confirmations": confirmations,
        "missing_conditions": missing,
        "reasons": reasons,
    })
    return out
