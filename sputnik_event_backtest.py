"""Small, reproducible event-study harness for SPUTNIK catalyst hypotheses.

Input is user-supplied historical OHLCV CSV; this module never fetches data or places orders.
It compares an exploratory next-bar entry with a delayed breakout entry and uses conservative
stop-first handling when a candle touches both stop and target.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone, e.g. +00:00")
    return parsed


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
            if candle["high"] < max(candle["open"], candle["close"], candle["low"]):
                raise ValueError("candle high is inconsistent with OHLC values")
            if candle["low"] > min(candle["open"], candle["close"], candle["high"]):
                raise ValueError("candle low is inconsistent with OHLC values")
            candles.append(candle)
    candles.sort(key=lambda candle: candle["timestamp"])
    return candles


def _simulate(candles, entry_index, entry, side, atr, stop_atr, target_r, max_holding_bars, spread):
    risk = atr * stop_atr
    if risk <= 0 or entry <= 0:
        return {"status": "INVALID_INPUT", "entry": entry, "stop": None, "target": None, "pnl_r": None}
    sign = -1 if side == "SHORT" else 1
    stop = entry + risk if side == "SHORT" else entry - risk
    target = entry - risk * target_r if side == "SHORT" else entry + risk * target_r
    last_index = min(len(candles), entry_index + 1 + max_holding_bars)
    for index in range(entry_index + 1, last_index):
        candle = candles[index]
        stop_hit = candle["high"] >= stop if side == "SHORT" else candle["low"] <= stop
        target_hit = candle["low"] <= target if side == "SHORT" else candle["high"] >= target
        if stop_hit and target_hit:
            exit_price, status = stop, "STOP_AMBIGUOUS_STOP_FIRST"
            break
        if stop_hit:
            exit_price, status = stop, "STOP"
            break
        if target_hit:
            exit_price, status = target, "TARGET"
            break
    else:
        exit_price = candles[last_index - 1]["close"] if last_index > entry_index + 1 else entry
        status = "TIME_EXIT" if last_index < len(candles) else "END_OF_DATA"
    gross_pnl = sign * (exit_price - entry)
    net_pnl = gross_pnl - max(0.0, spread)
    return {
        "status": status,
        "entry_time": candles[entry_index]["timestamp"].isoformat(),
        "entry": round(entry, 8),
        "stop": round(stop, 8),
        "target": round(target, 8),
        "exit": round(exit_price, 8),
        "pnl_r": round(net_pnl / risk, 4),
        "bars_held": max(0, min(last_index - 1, index if 'index' in locals() else last_index - 1) - entry_index),
    }


def backtest_event(
    candles: list[dict[str, Any]],
    event_time: str,
    side: str,
    atr: float,
    *,
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
    if atr <= 0 or stop_atr <= 0 or target_r <= 0 or breakout_lookback < 1 or max_holding_bars < 1:
        raise ValueError("ATR, stop, target, lookback and holding bars must be positive")
    event_dt = _dt(event_time)
    candles = sorted(candles, key=lambda candle: candle["timestamp"])
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
                breakout = _simulate(candles, i, candles[i]["close"], side, atr, stop_atr, target_r, max_holding_bars, spread)
                breakout["signal_time"] = candles[i]["timestamp"].isoformat()
            break

    return {
        "event_time": event_dt.isoformat(),
        "side": side,
        "settings": {"atr": atr, "stop_atr": stop_atr, "target_r": target_r, "breakout_lookback": breakout_lookback, "max_holding_bars": max_holding_bars, "spread": spread},
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
    parser.add_argument("--stop-atr", type=float, default=1.0)
    parser.add_argument("--target-r", type=float, default=2.0)
    parser.add_argument("--lookback", type=int, default=3)
    parser.add_argument("--holding-bars", type=int, default=12)
    parser.add_argument("--spread", type=float, default=0.0, help="Round-trip cost in price units")
    args = parser.parse_args()
    result = backtest_event(load_candles_csv(args.csv), args.event_time, args.side, args.atr,
                            stop_atr=args.stop_atr, target_r=args.target_r,
                            breakout_lookback=args.lookback, max_holding_bars=args.holding_bars,
                            spread=args.spread)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
