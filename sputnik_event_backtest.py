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
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


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
                raw_value = candle[key]
            except (KeyError, TypeError) as exc:
                raise ValueError(f"candle {index} has invalid {key}") from exc
            # Python converts bool to 0.0/1.0; reject it before numeric coercion.
            if isinstance(raw_value, bool):
                raise ValueError(f"candle {index} {key} must not be boolean")
            try:
                value = float(raw_value)
            except (TypeError, ValueError, OverflowError) as exc:
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


def _bar_gap_diagnostics(candles: list[dict[str, Any]], bar_interval_minutes: int) -> dict[str, Any]:
    gaps = []
    for index in range(1, len(candles)):
        gap_minutes = (candles[index]["timestamp"] - candles[index - 1]["timestamp"]).total_seconds() / 60.0
        if gap_minutes > bar_interval_minutes:
            gaps.append(gap_minutes)
    return {
        "bar_interval_minutes": bar_interval_minutes,
        "unmodeled_gap_count": len(gaps),
        "max_gap_minutes": round(max(gaps), 2) if gaps else 0.0,
        "session_calendar_used": False,
    }


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


def _validate_source_url(value: str) -> str:
    url = str(value).strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("source_url must be an absolute HTTP(S) URL")
    return url


def load_events_csv(path: str | Path) -> list[dict[str, Any]]:
    """Load a traceable event ledger with exact timezone-aware publication times.

    Required columns: event_id,event_time,side,atr,atr_time,source_url.
    The URL is provenance metadata; its presence does not independently verify the claim.
    """
    required = {"event_id", "event_time", "side", "atr", "atr_time", "source_url"}
    events = []
    seen_ids = set()
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError(
                "event CSV requires columns: event_id,event_time,side,atr,atr_time,source_url"
            )
        for row_number, row in enumerate(reader, start=2):
            event_id = str(row.get("event_id") or "").strip()
            if not event_id:
                raise ValueError(f"event CSV row {row_number} has an empty event_id")
            if event_id in seen_ids:
                raise ValueError(f"event_id must be unique: {event_id}")
            seen_ids.add(event_id)
            event_dt = _dt(str(row.get("event_time") or "").strip())
            atr_dt = _dt(str(row.get("atr_time") or "").strip())
            if atr_dt > event_dt:
                raise ValueError(f"event CSV row {row_number} ATR timestamp is after event time")
            side = str(row.get("side") or "").strip().upper()
            if side not in {"LONG", "SHORT"}:
                raise ValueError(f"event CSV row {row_number} side must be LONG or SHORT")
            try:
                atr = float(row.get("atr", ""))
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(f"event CSV row {row_number} has invalid ATR") from exc
            if not math.isfinite(atr) or atr <= 0:
                raise ValueError(f"event CSV row {row_number} ATR must be finite and positive")
            source_url = _validate_source_url(row.get("source_url") or "")
            events.append({
                "event_id": event_id,
                "event_time": event_dt.isoformat(),
                "side": side,
                "atr": atr,
                "atr_time": atr_dt.isoformat(),
                "source_url": source_url,
            })
    if not events:
        raise ValueError("event ledger contains no events")
    return events


def _simulate(candles, entry_index, entry, side, atr, stop_atr, target_r, max_holding_bars, spread, bar_interval_minutes):
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
        if index > entry_index:
            gap_minutes = (candle["timestamp"] - candles[index - 1]["timestamp"]).total_seconds() / 60.0
            if gap_minutes > bar_interval_minutes:
                # Without an instrument/session calendar, a long gap could be a
                # market closure or missing data. Do not score a trade across it.
                return {
                    "status": "UNMODELED_SESSION_GAP",
                    "entry_time": candles[entry_index]["timestamp"].isoformat(),
                    "entry": round(entry, 8),
                    "stop": round(stop, 8),
                    "target": round(target, 8),
                    "exit": None,
                    "pnl_r": None,
                    "bars_held": index - entry_index,
                    "gap_start_time": candles[index - 1]["timestamp"].isoformat(),
                    "gap_end_time": candle["timestamp"].isoformat(),
                    "gap_minutes": round(gap_minutes, 2),
                }
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
    bar_interval_minutes: int = 5,
) -> dict[str, Any]:
    """Compare exploratory entry after the event with a later close-confirmed breakout."""
    side = side.upper()
    if side not in {"LONG", "SHORT"}:
        raise ValueError("side must be LONG or SHORT")
    if isinstance(bar_interval_minutes, bool) or not isinstance(bar_interval_minutes, int) or bar_interval_minutes < 1:
        raise ValueError("bar interval minutes must be a positive integer")
    numeric_values = (atr, stop_atr, target_r, spread)
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        for value in numeric_values
    ):
        raise ValueError("ATR, stop, target and spread must be finite numeric values")
    integer_values = (breakout_lookback, max_holding_bars)
    if any(
        isinstance(value, bool) or not isinstance(value, int) or value < 1
        for value in integer_values
    ):
        raise ValueError("lookback and holding bars must be positive integers")
    if atr <= 0 or stop_atr <= 0 or target_r <= 0:
        raise ValueError("ATR, stop and target must be positive")
    if spread < 0:
        raise ValueError("spread must be non-negative; pass the round-trip cost in price units")
    event_dt = _dt(event_time)
    atr_dt = _dt(atr_time)
    if atr_dt > event_dt:
        raise ValueError("ATR timestamp must be at or before event time to prevent look-ahead bias")
    _validate_candle_timestamps(candles)
    _validate_candle_values(candles)
    data_quality = _bar_gap_diagnostics(candles, bar_interval_minutes)
    if not candles:
        return {"event_time": event_dt.isoformat(), "side": side, "early": {"status": "NO_DATA"}, "breakout": {"status": "NO_DATA"}, "data_quality": data_quality}

    next_index = next((i for i, c in enumerate(candles) if c["timestamp"] > event_dt), None)
    event_gap_minutes = None
    event_gap_unmodeled = False
    if next_index is None:
        early = {"status": "NO_POST_EVENT_CANDLE"}
    else:
        event_gap_minutes = (candles[next_index]["timestamp"] - event_dt).total_seconds() / 60.0
        event_gap_unmodeled = event_gap_minutes > bar_interval_minutes
        if event_gap_unmodeled:
            early = {
                "status": "UNMODELED_SESSION_GAP",
                "gap_start_time": event_dt.isoformat(),
                "gap_end_time": candles[next_index]["timestamp"].isoformat(),
                "gap_minutes": round(event_gap_minutes, 2),
            }
        else:
            early = _simulate(candles, next_index, candles[next_index]["open"], side, atr, stop_atr, target_r, max_holding_bars, spread, bar_interval_minutes)

    breakout = {"status": "NO_BREAKOUT"}
    start = next_index if next_index is not None else len(candles)
    if event_gap_unmodeled:
        breakout = {
            "status": "UNMODELED_SESSION_GAP",
            "gap_start_time": event_dt.isoformat(),
            "gap_end_time": candles[next_index]["timestamp"].isoformat(),
            "gap_minutes": round(event_gap_minutes, 2),
        }
    else:
        for i in range(start, len(candles)):
            if i > 0:
                gap_minutes = (candles[i]["timestamp"] - candles[i - 1]["timestamp"]).total_seconds() / 60.0
                if gap_minutes > bar_interval_minutes:
                    breakout = {
                        "status": "UNMODELED_SESSION_GAP",
                        "gap_start_time": candles[i - 1]["timestamp"].isoformat(),
                        "gap_end_time": candles[i]["timestamp"].isoformat(),
                        "gap_minutes": round(gap_minutes, 2),
                    }
                    break
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
                    entry_index = i + 1
                    entry_gap_minutes = (candles[entry_index]["timestamp"] - candles[i]["timestamp"]).total_seconds() / 60.0
                    if entry_gap_minutes > bar_interval_minutes:
                        breakout = {
                            "status": "UNMODELED_SESSION_GAP",
                            "gap_start_time": candles[i]["timestamp"].isoformat(),
                            "gap_end_time": candles[entry_index]["timestamp"].isoformat(),
                            "gap_minutes": round(entry_gap_minutes, 2),
                        }
                    else:
                        # The breakout is known only at this candle's close. A causal fill is
                        # the next candle's open, never the already-observed signal close.
                        breakout = _simulate(candles, entry_index, candles[entry_index]["open"], side, atr, stop_atr, target_r, max_holding_bars, spread, bar_interval_minutes)
                        breakout["signal_time"] = candles[i]["timestamp"].isoformat()
                        breakout["signal_close"] = round(candles[i]["close"], 8)
                        breakout["entry_model"] = "next_bar_open_after_close_confirmation"
                break

    return {
        "event_time": event_dt.isoformat(),
        "side": side,
        "settings": {"atr": atr, "atr_time": atr_dt.isoformat(), "stop_atr": stop_atr, "target_r": target_r, "breakout_lookback": breakout_lookback, "max_holding_bars": max_holding_bars, "spread": spread, "bar_interval_minutes": bar_interval_minutes},
        "data_quality": data_quality,
        "early": early,
        "breakout": breakout,
        "interpretation": "Historical simulation only; any gap above the declared bar interval is not treated as continuous trading time; use a verified instrument/session calendar before scoring across such gaps.",
    }


def _is_scored_pnl(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
    )


def summarize_comparison_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize paired R outcomes without treating unscored trades as zero."""
    paired = []
    early_unscored = {}
    breakout_unscored = {}
    for result in results:
        early = result.get("early", {})
        breakout = result.get("breakout", {})
        early_r = early.get("pnl_r")
        breakout_r = breakout.get("pnl_r")
        if _is_scored_pnl(early_r) and _is_scored_pnl(breakout_r):
            paired.append((float(early_r), float(breakout_r)))
        else:
            if not _is_scored_pnl(early_r):
                status = str(early.get("status", "UNKNOWN"))
                early_unscored[status] = early_unscored.get(status, 0) + 1
            if not _is_scored_pnl(breakout_r):
                status = str(breakout.get("status", "UNKNOWN"))
                breakout_unscored[status] = breakout_unscored.get(status, 0) + 1

    differences = [early_r - breakout_r for early_r, breakout_r in paired]
    mean_early = statistics.mean(early for early, _ in paired) if paired else None
    mean_breakout = statistics.mean(breakout for _, breakout in paired) if paired else None
    mean_difference = statistics.mean(differences) if differences else None
    median_difference = statistics.median(differences) if differences else None
    return {
        "events_total": len(results),
        "paired_scored_events": len(paired),
        "unpaired_or_unscored_events": len(results) - len(paired),
        "mean_early_r_paired": round(mean_early, 4) if mean_early is not None else None,
        "mean_breakout_r_paired": round(mean_breakout, 4) if mean_breakout is not None else None,
        "mean_early_minus_breakout_r": round(mean_difference, 4) if mean_difference is not None else None,
        "median_early_minus_breakout_r": round(median_difference, 4) if median_difference is not None else None,
        "early_better_count": sum(value > 0 for value in differences),
        "breakout_better_count": sum(value < 0 for value in differences),
        "ties_count": sum(value == 0 for value in differences),
        "unscored_early_status_counts": early_unscored,
        "unscored_breakout_status_counts": breakout_unscored,
        "scoring_note": (
            "R averages and paired differences use only events with numeric P&L for both strategies; "
            "unscored outcomes are reported by status and are never treated as zero."
        ),
    }


def backtest_events(
    candles: list[dict[str, Any]],
    events: list[dict[str, Any]],
    *,
    stop_atr: float = 1.0,
    target_r: float = 2.0,
    breakout_lookback: int = 3,
    max_holding_bars: int = 12,
    spread: float = 0.0,
    bar_interval_minutes: int = 5,
) -> dict[str, Any]:
    """Run a paired early-vs-breakout study over a source-linked event ledger."""
    if not events:
        raise ValueError("event ledger contains no events")
    results = []
    seen_ids = set()
    for event in events:
        event_id = str(event.get("event_id") or "").strip()
        if not event_id:
            raise ValueError("each event must have a non-empty event_id")
        if event_id in seen_ids:
            raise ValueError(f"event_id must be unique: {event_id}")
        seen_ids.add(event_id)
        source_url = _validate_source_url(event.get("source_url") or "")
        result = backtest_event(
            candles,
            event["event_time"],
            event["side"],
            event["atr"],
            atr_time=event["atr_time"],
            stop_atr=stop_atr,
            target_r=target_r,
            breakout_lookback=breakout_lookback,
            max_holding_bars=max_holding_bars,
            spread=spread,
            bar_interval_minutes=bar_interval_minutes,
        )
        result["event_id"] = event_id
        result["source_url"] = source_url
        results.append(result)
    return {"summary": summarize_comparison_results(results), "results": results}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, help="OHLCV CSV with timezone-aware timestamps")
    parser.add_argument(
        "--events-csv",
        help="Batch ledger CSV with event_id,event_time,side,atr,atr_time,source_url; requires source-linked events",
    )
    parser.add_argument("--event-time", help="Single catalyst publication time, ISO-8601 with timezone")
    parser.add_argument("--side", choices=("LONG", "SHORT"))
    parser.add_argument("--atr", type=float, help="ATR known at event time, in price units")
    parser.add_argument("--atr-time", help="Timestamp when the supplied ATR was available; must be <= event time")
    parser.add_argument("--stop-atr", type=float, default=1.0)
    parser.add_argument("--target-r", type=float, default=2.0)
    parser.add_argument("--lookback", type=int, default=3)
    parser.add_argument("--holding-bars", type=int, default=12)
    parser.add_argument("--spread", type=float, default=0.0, help="Round-trip cost in price units")
    parser.add_argument("--bar-interval-minutes", type=int, default=5, help="Expected OHLCV bar interval; larger unexplained gaps fail closed")
    args = parser.parse_args()
    candles = load_candles_csv(args.csv)
    strategy_options = {
        "stop_atr": args.stop_atr,
        "target_r": args.target_r,
        "breakout_lookback": args.lookback,
        "max_holding_bars": args.holding_bars,
        "spread": args.spread,
        "bar_interval_minutes": args.bar_interval_minutes,
    }
    if args.events_csv:
        if any(value is not None for value in (args.event_time, args.side, args.atr, args.atr_time)):
            parser.error("use either --events-csv or the single-event arguments, not both")
        result = backtest_events(candles, load_events_csv(args.events_csv), **strategy_options)
    else:
        if any(value is None for value in (args.event_time, args.side, args.atr, args.atr_time)):
            parser.error("single-event mode requires --event-time, --side, --atr and --atr-time")
        result = backtest_event(
            candles, args.event_time, args.side, args.atr, atr_time=args.atr_time,
            **strategy_options,
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
