"""Small, reproducible event-study harness for SPUTNIK catalyst hypotheses.

Input is user-supplied historical OHLCV CSV; this module never fetches data or places orders.
It compares an exploratory next-bar entry with a delayed breakout entry and uses conservative
stop-first handling when a candle touches both stop and target.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any


def _dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone, e.g. +00:00")
    return parsed



def _validate_candle_timestamps(candles: list[dict[str, Any]]) -> None:
    """Reject ambiguous, duplicate, or out-of-order bar times before simulation."""
    seen = set()
    previous = None
    for index, candle in enumerate(candles):
        timestamp = candle.get("timestamp")
        if not isinstance(timestamp, datetime) or timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("candle timestamps must be timezone-aware datetime values")
        if timestamp in seen:
            raise ValueError(f"candle timestamps must be unique; duplicate timestamp: {timestamp.isoformat()}")
        if previous is not None and timestamp < previous:
            raise ValueError(
                f"candle timestamps must be in chronological order; row {index} "
                f"({timestamp.isoformat()}) precedes the previous row ({previous.isoformat()})"
            )
        seen.add(timestamp)
        previous = timestamp


def _validate_candle_values(candles: list[dict[str, Any]]) -> None:
    """Reject non-finite OHLCV values and impossible/negative-volume bars."""
    for index, candle in enumerate(candles):
        values = {}
        for key in ("open", "high", "low", "close", "volume"):
            try:
                value = float(candle[key])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"candle {index} has invalid {key}") from exc
            if not math.isfinite(value):
                raise ValueError(f"candle {index} {key} must be finite")
            values[key] = value
        if values["volume"] < 0:
            raise ValueError(f"candle {index} volume must be non-negative")
        if values["high"] < max(values["open"], values["close"], values["low"]):
            raise ValueError(f"candle {index} high is inconsistent with OHLC values")
        if values["low"] > min(values["open"], values["close"], values["high"]):
            raise ValueError(f"candle {index} low is inconsistent with OHLC values")


def load_candles_csv(path: str | Path) -> list[dict[str, Any]]:
    """Load timestamp,open,high,low,close,volume CSV rows in chronological order."""
    candles = []
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"timestamp", "open", "high", "low", "close", "volume"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("CSV requires columns: timestamp,open,high,low,close,volume")
        for row in reader:
            candle = {"timestamp": _dt(row["timestamp"])}
            for key in ("open", "high", "low", "close", "volume"):
                candle[key] = float(row[key])
            candles.append(candle)
    _validate_candle_timestamps(candles)
    _validate_candle_values(candles)
    return candles


def _simulate(candles, entry_index, entry, side, atr, stop_atr, target_r, max_holding_bars, spread):
    risk = atr * stop_atr
    if not math.isfinite(risk) or risk <= 0 or not math.isfinite(entry):
        return {"status": "INVALID_INPUT", "entry": entry, "stop": None, "target": None, "pnl_r": None}
    sign = -1 if side == "SHORT" else 1
    stop = entry + risk if side == "SHORT" else entry - risk
    target = entry - risk * target_r if side == "SHORT" else entry + risk * target_r

    # The entry bar is observable after an open fill; include it in stop/target checks.
    # On later bars, account for gaps: stop orders fill at the worse opening price;
    # target limits conservatively fill at the target, not at a more favorable open.
    end_index = min(len(candles), entry_index + max_holding_bars)
    exit_index = entry_index
    exit_price = None
    status = None
    for index in range(entry_index, end_index):
        candle = candles[index]
        opening = candle["open"]
        if index > entry_index:
            if side == "SHORT" and opening >= stop:
                exit_price, status = opening, "STOP_GAP"
            elif side == "SHORT" and opening <= target:
                exit_price, status = target, "TARGET_GAP"
            elif side == "LONG" and opening <= stop:
                exit_price, status = opening, "STOP_GAP"
            elif side == "LONG" and opening >= target:
                exit_price, status = target, "TARGET_GAP"
            if status is not None:
                exit_index = index
                break

        stop_hit = candle["high"] >= stop if side == "SHORT" else candle["low"] <= stop
        target_hit = candle["low"] <= target if side == "SHORT" else candle["high"] >= target
        if stop_hit and target_hit:
            exit_price, status = stop, "STOP_AMBIGUOUS_STOP_FIRST"
        elif stop_hit:
            exit_price, status = stop, "STOP"
        elif target_hit:
            exit_price, status = target, "TARGET"
        if status is not None:
            exit_index = index
            break
    else:
        exit_index = end_index - 1
        exit_price = candles[exit_index]["close"]
        status = "TIME_EXIT" if end_index < len(candles) else "END_OF_DATA"

    gross_pnl = sign * (exit_price - entry)
    net_pnl = gross_pnl - spread
    return {
        "status": status,
        "entry_time": candles[entry_index]["timestamp"].isoformat(),
        "entry": round(entry, 8),
        "stop": round(stop, 8),
        "target": round(target, 8),
        "exit": round(exit_price, 8),
        "pnl_r": round(net_pnl / risk, 4),
        "bars_held": exit_index - entry_index + 1,
    }


def backtest_event(
    candles: list[dict[str, Any]],
    event_time: str,
    side: str,
    atr: float,
    *,
    atr_time: str,
    stop_atr: float = 1.0,
    target_r: float = 2.0,
    breakout_lookback: int = 3,
    max_holding_bars: int = 12,
    spread: float = 0.0,
) -> dict[str, Any]:
    """Compare exploratory entry after the event with a later close-confirmed breakout."""
    side = side.upper()
    if side not in {"LONG", "SHORT"}:
        raise ValueError("side must be LONG or SHORT")
    if not all(math.isfinite(value) for value in (atr, stop_atr, target_r, spread)):
        raise ValueError("ATR, stop, target and spread must be finite")
    if atr <= 0 or stop_atr <= 0 or target_r <= 0 or breakout_lookback < 1 or max_holding_bars < 1:
        raise ValueError("ATR, stop, target, lookback and holding bars must be positive")
    if spread < 0:
        raise ValueError("spread must be non-negative; pass the round-trip cost in price units")
    event_dt = _dt(event_time)
    atr_dt = _dt(atr_time)
    if atr_dt > event_dt:
        raise ValueError("ATR timestamp must be at or before event time to prevent look-ahead bias")
    _validate_candle_timestamps(candles)
    _validate_candle_values(candles)
    if not candles:
        return {"event_time": event_dt.isoformat(), "side": side, "early": {"status": "NO_DATA"}, "breakout": {"status": "NO_DATA"}}

    next_index = next((i for i, c in enumerate(candles) if c["timestamp"] > event_dt), None)
    if next_index is None:
        early = {"status": "NO_POST_EVENT_CANDLE"}
    else:
        early = _simulate(candles, next_index, candles[next_index]["open"], side, atr, stop_atr, target_r, max_holding_bars, spread)

    breakout = {"status": "NO_BREAKOUT"}
    start = next_index if next_index is not None else len(candles)
    for i in range(start, len(candles)):
        prior = candles[max(0, i - breakout_lookback):i]
        if len(prior) < breakout_lookback:
            continue
        if side == "SHORT":
            triggered = candles[i]["close"] < min(c["low"] for c in prior)
        else:
            triggered = candles[i]["close"] > max(c["high"] for c in prior)
        if triggered:
            if i + 1 >= len(candles):
                breakout = {"status": "BREAKOUT_NO_FOLLOWING_CANDLE"}
            else:
                # The breakout is known only at this candle's close. A causal fill is
                # the next candle's open, never the already-observed signal close.
                entry_index = i + 1
                breakout = _simulate(candles, entry_index, candles[entry_index]["open"], side, atr, stop_atr, target_r, max_holding_bars, spread)
                breakout["signal_time"] = candles[i]["timestamp"].isoformat()
                breakout["signal_close"] = round(candles[i]["close"], 8)
                breakout["entry_model"] = "next_bar_open_after_close_confirmation"
            break

    return {
        "event_time": event_dt.isoformat(),
        "side": side,
        "settings": {"atr": atr, "atr_time": atr_dt.isoformat(), "stop_atr": stop_atr, "target_r": target_r, "breakout_lookback": breakout_lookback, "max_holding_bars": max_holding_bars, "spread": spread},
        "early": early,
        "breakout": breakout,
        "interpretation": "Historical simulation only; compare multiple events, include realistic costs, and do not infer profitability from one event.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, help="OHLCV CSV with timezone-aware timestamps")
    parser.add_argument("--event-time", required=True, help="Catalyst publication time, ISO-8601 with timezone")
    parser.add_argument("--side", required=True, choices=("LONG", "SHORT"))
    parser.add_argument("--atr", type=float, required=True, help="ATR known at event time, in price units")
    parser.add_argument("--atr-time", required=True, help="Timestamp when the supplied ATR value was available, ISO-8601 with timezone; must be <= event time")
    parser.add_argument("--stop-atr", type=float, default=1.0)
    parser.add_argument("--target-r", type=float, default=2.0)
    parser.add_argument("--lookback", type=int, default=3)
    parser.add_argument("--holding-bars", type=int, default=12)
    parser.add_argument("--spread", type=float, default=0.0, help="Round-trip cost in price units")
    args = parser.parse_args()
    result = backtest_event(load_candles_csv(args.csv), args.event_time, args.side, args.atr,
                            atr_time=args.atr_time, stop_atr=args.stop_atr, target_r=args.target_r,
                            breakout_lookback=args.lookback, max_holding_bars=args.holding_bars,
                            spread=args.spread)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
