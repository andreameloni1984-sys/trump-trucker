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
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


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
    observed_intervals = []
    short_intervals = []
    for index in range(1, len(candles)):
        gap_minutes = (candles[index]["timestamp"] - candles[index - 1]["timestamp"]).total_seconds() / 60.0
        observed_intervals.append(gap_minutes)
        if gap_minutes > bar_interval_minutes:
            gaps.append(gap_minutes)
        elif gap_minutes < bar_interval_minutes:
            # A 1-minute feed must not be simulated as if it contained 5-minute bars:
            # holding limits and close-confirmation times would otherwise be wrong.
            short_intervals.append(gap_minutes)
    return {
        "bar_interval_minutes": bar_interval_minutes,
        "unmodeled_gap_count": len(gaps),
        "max_gap_minutes": round(max(gaps), 2) if gaps else 0.0,
        "unexpected_short_interval_count": len(short_intervals),
        "min_observed_interval_minutes": round(min(observed_intervals), 2) if observed_intervals else None,
        "session_calendar_used": False,
    }


def load_candles_csv(path: str | Path) -> list[dict[str, Any]]:
    """Load OHLCV rows with timezone-aware timestamps representing candle opens."""
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
    """Validate a source permalink while preserving its exact supplied form."""
    url = str(value).strip()
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise ValueError("source_url must be an absolute HTTPS URL")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("source_url must not contain embedded credentials")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("source_url has an invalid port") from exc
    if port not in (None, 443):
        raise ValueError("source_url must use the standard HTTPS port")
    # Keep the original scheme/host casing, query order, tracking parameters,
    # and fragment for evidence provenance. Canonical identity is separate.
    return url


def _canonical_source_url(value: str) -> str:
    """Build a conservative deduplication key without rewriting the stored permalink."""
    url = _validate_source_url(value)
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    host = parsed.hostname.lower()
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    port = parsed.port
    default_port = (scheme == "https" and port == 443) or (scheme == "http" and port == 80)
    netloc = host if port is None or default_port else f"{host}:{port}"

    # Remove known tracking parameters but preserve the order of all remaining
    # query parameters: some publishers use order-sensitive/signed permalinks.
    tracking_keys = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref_src", "msclkid", "dclid", "ttclid", "twclid", "srsltid", "yclid", "igshid", "mkt_tok", "vero_id", "vero_conv"}
    query_pairs = [
        (key, val) for key, val in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in tracking_keys
    ]
    query = urlencode(query_pairs)
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/") or "/"
    return urlunparse((scheme, netloc, path, parsed.params, query, ""))


def load_events_csv(path: str | Path) -> list[dict[str, Any]]:
    """Load a traceable event ledger with exact timezone-aware publication times.

    Required columns: event_id,event_time,available_at,side,atr,atr_time,source_url.
    The URL is provenance metadata; its presence does not independently verify the claim.
    """
    required = {"event_id", "event_time", "available_at", "side", "atr", "atr_time", "source_url"}
    events = []
    seen_ids = set()
    seen_sources = set()
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError(
                "event CSV requires columns: event_id,event_time,available_at,side,atr,atr_time,source_url"
            )
        for row_number, row in enumerate(reader, start=2):
            event_id = str(row.get("event_id") or "").strip()
            if not event_id:
                raise ValueError(f"event CSV row {row_number} has an empty event_id")
            if event_id in seen_ids:
                raise ValueError(f"event_id must be unique: {event_id}")
            seen_ids.add(event_id)
            event_dt = _dt(str(row.get("event_time") or "").strip())
            available_dt = _dt(str(row.get("available_at") or "").strip())
            if available_dt < event_dt:
                raise ValueError(f"event CSV row {row_number} available_at is before event_time")
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
            canonical_source = _canonical_source_url(source_url)
            if canonical_source in seen_sources:
                raise ValueError(f"source_url must be unique after canonicalization: {canonical_source}")
            seen_sources.add(canonical_source)
            events.append({
                "event_id": event_id,
                "event_time": event_dt.isoformat(),
                "available_at": available_dt.isoformat(),
                "side": side,
                "atr": atr,
                "atr_time": atr_dt.isoformat(),
                "source_url": source_url,
            })
    if not events:
        raise ValueError("event ledger contains no events")
    return events


def _simulate(candles, entry_index, entry, side, atr, stop_atr, target_r, max_holding_bars, round_trip_cost, bar_interval_minutes):
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
    net_pnl = gross_pnl - round_trip_cost
    return {
        "status": status,
        "entry_time": candles[entry_index]["timestamp"].isoformat(),
        "exit_time": candles[exit_index]["timestamp"].isoformat(),
        "entry": round(entry, 8),
        "stop": round(stop, 8),
        "target": round(target, 8),
        "exit": round(exit_price, 8),
        "gross_pnl_price_units": round(gross_pnl, 8),
        "net_pnl_price_units": round(net_pnl, 8),
        "round_trip_cost_price_units": round(round_trip_cost, 8),
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
    available_at: str,
    stop_atr: float = 1.0,
    target_r: float = 2.0,
    breakout_lookback: int = 3,
    max_holding_bars: int = 12,
    spread: float = 0.0,
    commission_round_trip_usd_per_contract: float = 0.0,
    slippage_ticks_per_side: float = 0.0,
    tick_size: float = 0.01,
    contract_multiplier: float = 1000.0,
    bar_interval_minutes: int = 5,
) -> dict[str, Any]:
    """Compare early/breakout entries with spread, commission and slippage cost deductions."""
    side = side.upper()
    if side not in {"LONG", "SHORT"}:
        raise ValueError("side must be LONG or SHORT")
    if isinstance(bar_interval_minutes, bool) or not isinstance(bar_interval_minutes, int) or bar_interval_minutes < 1:
        raise ValueError("bar interval minutes must be a positive integer")
    numeric_values = (atr, stop_atr, target_r, spread, commission_round_trip_usd_per_contract, slippage_ticks_per_side, tick_size, contract_multiplier)
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        for value in numeric_values
    ):
        raise ValueError("ATR, stop, target and all execution-cost inputs must be finite numeric values")
    integer_values = (breakout_lookback, max_holding_bars)
    if any(
        isinstance(value, bool) or not isinstance(value, int) or value < 1
        for value in integer_values
    ):
        raise ValueError("lookback and holding bars must be positive integers")
    if atr <= 0 or stop_atr <= 0 or target_r <= 0:
        raise ValueError("ATR, stop and target must be positive")
    if spread < 0 or commission_round_trip_usd_per_contract < 0 or slippage_ticks_per_side < 0:
        raise ValueError("spread, round-trip commission and slippage must be non-negative")
    if tick_size <= 0 or contract_multiplier <= 0:
        raise ValueError("tick_size and contract_multiplier must be positive")
    round_trip_cost = (
        spread
        + commission_round_trip_usd_per_contract / contract_multiplier
        + 2.0 * slippage_ticks_per_side * tick_size
    )
    if not math.isfinite(round_trip_cost):
        raise ValueError("combined round-trip execution cost must be finite")
    event_dt = _dt(event_time)
    available_dt = _dt(available_at)
    if available_dt < event_dt:
        raise ValueError("available_at must be at or after event_time")
    atr_dt = _dt(atr_time)
    if atr_dt > event_dt:
        raise ValueError("ATR timestamp must be at or before event time to prevent look-ahead bias")
    _validate_candle_timestamps(candles)
    _validate_candle_values(candles)
    data_quality = _bar_gap_diagnostics(candles, bar_interval_minutes)
    if data_quality["unexpected_short_interval_count"]:
        reason = {
            "status": "UNMODELED_BAR_INTERVAL",
            "expected_interval_minutes": bar_interval_minutes,
            "unexpected_short_interval_count": data_quality["unexpected_short_interval_count"],
            "pnl_r": None,
        }
        return {
            "event_time": event_dt.isoformat(),
            "available_at": available_dt.isoformat(),
            "side": side,
            "settings": {
                "atr": atr, "atr_time": atr_dt.isoformat(), "stop_atr": stop_atr,
                "target_r": target_r, "breakout_lookback": breakout_lookback,
                "max_holding_bars": max_holding_bars, "spread": spread,
                "commission_round_trip_usd_per_contract": commission_round_trip_usd_per_contract,
                "slippage_ticks_per_side": slippage_ticks_per_side, "tick_size": tick_size,
                "contract_multiplier": contract_multiplier, "round_trip_cost_price_units": round_trip_cost,
                "bar_interval_minutes": bar_interval_minutes,
            },
            "data_quality": data_quality,
            "early": {**reason, "decision_time": available_dt.isoformat()},
            "breakout": dict(reason),
            "interpretation": (
                "Historical simulation refused: observed candle spacing is shorter than the declared interval; "
                "entry timing and holding-bar limits would be inconsistent."
            ),
        }
    if not candles:
        return {"event_time": event_dt.isoformat(), "available_at": available_dt.isoformat(), "side": side, "early": {"status": "NO_DATA", "decision_time": available_dt.isoformat()}, "breakout": {"status": "NO_DATA"}, "data_quality": data_quality}

    next_index = next((i for i, c in enumerate(candles) if c["timestamp"] > available_dt), None)
    availability_gap_minutes = None
    availability_gap_unmodeled = False
    if next_index is None:
        early = {"status": "NO_POST_AVAILABILITY_CANDLE"}
    else:
        availability_gap_minutes = (candles[next_index]["timestamp"] - available_dt).total_seconds() / 60.0
        availability_gap_unmodeled = availability_gap_minutes > bar_interval_minutes
        if availability_gap_unmodeled:
            early = {
                "status": "UNMODELED_SESSION_GAP",
                "gap_start_time": available_dt.isoformat(),
                "gap_end_time": candles[next_index]["timestamp"].isoformat(),
                "gap_minutes": round(availability_gap_minutes, 2),
            }
        else:
            early = _simulate(candles, next_index, candles[next_index]["open"], side, atr, stop_atr, target_r, max_holding_bars, round_trip_cost, bar_interval_minutes)
    early["decision_time"] = available_dt.isoformat()

    breakout = {"status": "NO_BREAKOUT"}
    start = next_index if next_index is not None else len(candles)
    if availability_gap_unmodeled:
        breakout = {
            "status": "UNMODELED_SESSION_GAP",
            "gap_start_time": available_dt.isoformat(),
            "gap_end_time": candles[next_index]["timestamp"].isoformat(),
            "gap_minutes": round(availability_gap_minutes, 2),
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
                        # Candle timestamps are bar opens: the signal close is observable
                        # only at the next bar boundary. Never score a fill before that time.
                        signal_dt = candles[i]["timestamp"] + timedelta(minutes=bar_interval_minutes)
                        entry_dt = candles[entry_index]["timestamp"]
                        if entry_dt < signal_dt:
                            breakout = {
                                "status": "UNMODELED_BAR_INTERVAL",
                                "signal_bar_time": candles[i]["timestamp"].isoformat(),
                                "signal_time": signal_dt.isoformat(),
                                "entry_time": entry_dt.isoformat(),
                                "expected_gap_minutes": float(bar_interval_minutes),
                                "observed_gap_minutes": round(entry_gap_minutes, 2),
                            }
                        else:
                            breakout = _simulate(candles, entry_index, candles[entry_index]["open"], side, atr, stop_atr, target_r, max_holding_bars, round_trip_cost, bar_interval_minutes)
                            breakout["signal_bar_time"] = candles[i]["timestamp"].isoformat()
                            breakout["signal_time"] = signal_dt.isoformat()
                            breakout["decision_time"] = signal_dt.isoformat()
                            breakout["signal_close"] = round(candles[i]["close"], 8)
                            breakout["entry_model"] = "next_bar_open_after_close_confirmation"
                break

    return {
        "event_time": event_dt.isoformat(),
        "available_at": available_dt.isoformat(),
        "side": side,
        "settings": {"atr": atr, "atr_time": atr_dt.isoformat(), "stop_atr": stop_atr, "target_r": target_r, "breakout_lookback": breakout_lookback, "max_holding_bars": max_holding_bars, "spread": spread, "commission_round_trip_usd_per_contract": commission_round_trip_usd_per_contract, "slippage_ticks_per_side": slippage_ticks_per_side, "tick_size": tick_size, "contract_multiplier": contract_multiplier, "round_trip_cost_price_units": round_trip_cost, "bar_interval_minutes": bar_interval_minutes},
        "data_quality": data_quality,
        "early": early,
        "breakout": breakout,
        "interpretation": "Historical simulation only. Early-entry timing uses available_at, not just publication event_time; breakout decision_time is the signal-bar timestamp and fills occur on the next bar. Unmodeled gaps fail closed.",
    }


def _is_scored_pnl(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
    )


def _overlapping_scored_trade_pairs(results: list[dict[str, Any]], strategy_key: str) -> tuple[int, int]:
    """Count strictly overlapping time windows among trades with scored P&L and timestamps."""
    windows = []
    for result in results:
        trade = result.get(strategy_key, {})
        if not _is_scored_pnl(trade.get("pnl_r")):
            continue
        start_value = trade.get("entry_time")
        end_value = trade.get("exit_time")
        if not isinstance(start_value, str) or not isinstance(end_value, str):
            continue
        try:
            start = _dt(start_value)
            end = _dt(end_value)
        except (TypeError, ValueError):
            continue
        if end < start:
            continue
        windows.append((start, end))

    overlapping_pairs = 0
    for index, (start, end) in enumerate(windows):
        for other_start, other_end in windows[index + 1:]:
            if start < other_end and other_start < end:
                overlapping_pairs += 1
    return len(windows), overlapping_pairs



def _non_overlapping_paired_differences(results: list[dict[str, Any]]) -> tuple[list[float], int, int]:
    """Build a chronological sensitivity sample with no cross-event trade-window overlap.

    An event is retained only when both strategies have scored P&L and valid timezone-aware
    entry/exit timestamps. If either trade window overlaps any window from a previously retained
    event, the whole event pair is excluded. This deterministic greedy filter is a sensitivity
    diagnostic, not a guarantee of statistical independence.
    """
    candidates = []
    missing_timestamps = 0
    for index, result in enumerate(results):
        early = result.get("early", {})
        breakout = result.get("breakout", {})
        early_r = early.get("pnl_r")
        breakout_r = breakout.get("pnl_r")
        if not (_is_scored_pnl(early_r) and _is_scored_pnl(breakout_r)):
            continue
        try:
            event_time = _dt(result.get("event_time", ""))
            windows = []
            for trade in (early, breakout):
                start = _dt(trade.get("entry_time", ""))
                end = _dt(trade.get("exit_time", ""))
                if end < start:
                    raise ValueError("trade exit precedes entry")
                windows.append((start, end))
        except (TypeError, ValueError):
            missing_timestamps += 1
            continue
        candidates.append((event_time, index, float(early_r) - float(breakout_r), windows))

    candidates.sort(key=lambda item: (item[0], item[1]))
    selected_differences = []
    accepted_windows = []
    excluded_for_overlap = 0
    for _, _, difference, windows in candidates:
        overlaps = any(
            start < prior_end and prior_start < end
            for start, end in windows
            for prior_start, prior_end in accepted_windows
        )
        if overlaps:
            excluded_for_overlap += 1
            continue
        selected_differences.append(difference)
        accepted_windows.extend(windows)
    return selected_differences, excluded_for_overlap, missing_timestamps


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
    early_windows, early_overlaps = _overlapping_scored_trade_pairs(results, "early")
    breakout_windows, breakout_overlaps = _overlapping_scored_trade_pairs(results, "breakout")
    non_overlap_differences, non_overlap_excluded, non_overlap_missing_times = _non_overlapping_paired_differences(results)
    non_overlap_mean = statistics.mean(non_overlap_differences) if non_overlap_differences else None
    non_overlap_median = statistics.median(non_overlap_differences) if non_overlap_differences else None
    return {
        "events_total": len(results),
        "early_scored_trade_windows": early_windows,
        "breakout_scored_trade_windows": breakout_windows,
        "overlapping_trade_pairs_early": early_overlaps,
        "overlapping_trade_pairs_breakout": breakout_overlaps,
        "paired_scored_events": len(paired),
        "non_overlapping_paired_events": len(non_overlap_differences),
        "non_overlapping_events_excluded_for_overlap": non_overlap_excluded,
        "non_overlapping_events_missing_timestamps": non_overlap_missing_times,
        "non_overlapping_mean_early_minus_breakout_r": round(non_overlap_mean, 4) if non_overlap_mean is not None else None,
        "non_overlapping_median_early_minus_breakout_r": round(non_overlap_median, 4) if non_overlap_median is not None else None,
        "non_overlapping_early_better_count": sum(value > 0 for value in non_overlap_differences),
        "non_overlapping_breakout_better_count": sum(value < 0 for value in non_overlap_differences),
        "non_overlapping_ties_count": sum(value == 0 for value in non_overlap_differences),
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
        "overlap_diagnostic_note": (
            "Overlapping scored trade windows are counted separately for each strategy. "
            "When counts are non-zero, event outcomes are not independent; interpret aggregate "
            "averages cautiously and use the non-overlapping sensitivity figures or an event-clustered analysis."
        ),
        "non_overlapping_sensitivity_note": (
            "The non-overlapping sensitivity sample is selected chronologically and excludes a paired event "
            "if either strategy's trade window overlaps any trade window from a previously retained event. "
            "Events with unscored P&L are not eligible; paired events with missing/invalid timestamps are counted "
            "separately. This reduces direct window overlap but does not guarantee statistical independence."
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
    commission_round_trip_usd_per_contract: float = 0.0,
    slippage_ticks_per_side: float = 0.0,
    tick_size: float = 0.01,
    contract_multiplier: float = 1000.0,
    bar_interval_minutes: int = 5,
) -> dict[str, Any]:
    """Run a paired early-vs-breakout study over a source-linked event ledger."""
    if not events:
        raise ValueError("event ledger contains no events")
    results = []
    seen_ids = set()
    seen_sources = set()
    for event in events:
        event_id = str(event.get("event_id") or "").strip()
        if not event_id:
            raise ValueError("each event must have a non-empty event_id")
        if event_id in seen_ids:
            raise ValueError(f"event_id must be unique: {event_id}")
        seen_ids.add(event_id)
        source_url = _validate_source_url(event.get("source_url") or "")
        canonical_source = _canonical_source_url(source_url)
        if canonical_source in seen_sources:
            raise ValueError(f"source_url must be unique after canonicalization: {canonical_source}")
        seen_sources.add(canonical_source)
        result = backtest_event(
            candles,
            event["event_time"],
            event["side"],
            event["atr"],
            atr_time=event["atr_time"],
            available_at=event["available_at"],
            stop_atr=stop_atr,
            target_r=target_r,
            breakout_lookback=breakout_lookback,
            max_holding_bars=max_holding_bars,
            spread=spread,
            commission_round_trip_usd_per_contract=commission_round_trip_usd_per_contract,
            slippage_ticks_per_side=slippage_ticks_per_side,
            tick_size=tick_size,
            contract_multiplier=contract_multiplier,
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
    parser.add_argument("--available-at", help="Timestamp when the catalyst became available to the system; must be >= event time")
    parser.add_argument("--stop-atr", type=float, default=1.0)
    parser.add_argument("--target-r", type=float, default=2.0)
    parser.add_argument("--lookback", type=int, default=3)
    parser.add_argument("--holding-bars", type=int, default=12)
    parser.add_argument("--spread", type=float, default=0.0, help="Round-trip spread cost in price units")
    parser.add_argument("--commission-round-trip-usd-per-contract", type=float, default=0.0, help="Round-trip commission per contract in USD")
    parser.add_argument("--slippage-ticks-per-side", type=float, default=0.0, help="Assumed slippage in ticks for each side of the trade")
    parser.add_argument("--tick-size", type=float, default=0.01, help="Instrument tick size in price units (CL: 0.01 USD/barrel)")
    parser.add_argument("--contract-multiplier", type=float, default=1000.0, help="Units per contract (CL: 1000 barrels)")
    parser.add_argument("--bar-interval-minutes", type=int, default=5, help="Expected OHLCV bar interval; larger unexplained gaps fail closed")
    args = parser.parse_args()
    candles = load_candles_csv(args.csv)
    strategy_options = {
        "stop_atr": args.stop_atr,
        "target_r": args.target_r,
        "breakout_lookback": args.lookback,
        "max_holding_bars": args.holding_bars,
        "spread": args.spread,
        "commission_round_trip_usd_per_contract": args.commission_round_trip_usd_per_contract,
        "slippage_ticks_per_side": args.slippage_ticks_per_side,
        "tick_size": args.tick_size,
        "contract_multiplier": args.contract_multiplier,
        "bar_interval_minutes": args.bar_interval_minutes,
    }
    if args.events_csv:
        if any(value is not None for value in (args.event_time, args.available_at, args.side, args.atr, args.atr_time)):
            parser.error("use either --events-csv or the single-event arguments, not both")
        result = backtest_events(candles, load_events_csv(args.events_csv), **strategy_options)
    else:
        if any(value is None for value in (args.event_time, args.available_at, args.side, args.atr, args.atr_time)):
            parser.error("single-event mode requires --event-time, --available-at, --side, --atr and --atr-time")
        result = backtest_event(
            candles, args.event_time, args.side, args.atr, atr_time=args.atr_time,
            available_at=args.available_at, **strategy_options,
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
