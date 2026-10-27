import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta, timezone

from sputnik_event_backtest import backtest_event, backtest_events, load_candles_csv, load_events_csv, summarize_comparison_results


def run_backtest(data, event_time, side, atr, *args, **kwargs):
    """Use an explicitly pre-event ATR snapshot in deterministic fixtures."""
    event_dt = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
    kwargs.setdefault("atr_time", (event_dt - timedelta(minutes=5)).isoformat())
    kwargs.setdefault("available_at", event_time)
    return backtest_event(data, event_time, side, atr, *args, **kwargs)


def candles(rows, start=None):
    start = start or datetime(2026, 1, 1, tzinfo=timezone.utc)
    output = []
    for i, (open_, high, low, close, volume) in enumerate(rows):
        output.append({
            "timestamp": start + timedelta(minutes=5 * i),
            "open": float(open_), "high": float(high), "low": float(low),
            "close": float(close), "volume": float(volume),
        })
    return output


class SputnikEventBacktestTests(unittest.TestCase):
    def test_execution_cost_model_deducts_commission_and_two_sided_slippage(self):
        start = datetime(2026, 1, 1, 0, 5, tzinfo=timezone.utc)
        data = candles([(100.0, 100.5, 99.5, 100.2, 1000)], start=start)
        result = run_backtest(
            data,
            "2026-01-01T00:00:00+00:00",
            "LONG",
            1.0,
            max_holding_bars=1,
            spread=0.02,
            commission_round_trip_usd_per_contract=10.0,
            slippage_ticks_per_side=1.0,
            tick_size=0.01,
            contract_multiplier=1000.0,
        )
        early = result["early"]
        self.assertAlmostEqual(early["gross_pnl_price_units"], 0.2)
        # 0.02 spread + $10/1000 barrels + two 0.01 ticks = 0.05 price units.
        self.assertAlmostEqual(early["round_trip_cost_price_units"], 0.05)
        self.assertAlmostEqual(early["net_pnl_price_units"], 0.15)
        self.assertAlmostEqual(early["pnl_r"], 0.15)
        # USD per CL contract = price-unit P&L/cost multiplied by 1,000 barrels.
        self.assertAlmostEqual(early["gross_pnl_usd_per_contract"], 200.00)
        self.assertAlmostEqual(early["net_pnl_usd_per_contract"], 150.00)
        self.assertAlmostEqual(early["round_trip_cost_usd_per_contract"], 50.00)

    def test_execution_cost_model_rejects_invalid_cost_inputs(self):
        data = candles([(100.0, 100.5, 99.5, 100.2, 1000)])
        with self.assertRaisesRegex(ValueError, "must be non-negative"):
            run_backtest(
                data, "2026-01-01T00:00:00+00:00", "LONG", 1.0,
                commission_round_trip_usd_per_contract=-1.0,
            )
        with self.assertRaisesRegex(ValueError, "tick_size and contract_multiplier must be positive"):
            run_backtest(
                data, "2026-01-01T00:00:00+00:00", "LONG", 1.0,
                tick_size=0.0,
            )

    def test_exploratory_short_can_enter_before_breakout(self):
        data = candles([
            (100, 101, 99, 100, 1000),
            (100, 100.5, 98.8, 99, 1200),
            (99, 99.2, 97.5, 98, 1500),
            (97.4, 98.2, 96.0, 97, 1800),
            (97, 97.2, 95.0, 96, 1900),
        ])
        result = run_backtest(data, "2026-01-01T00:02:00+00:00", "SHORT", 1.0, breakout_lookback=2)
        self.assertEqual(result["early"]["entry"], 100.0)
        self.assertEqual(result["early"]["status"], "TARGET")
        self.assertEqual(result["early"]["exit_time"], data[2]["timestamp"].isoformat())
        self.assertNotEqual(result["breakout"]["status"], "NO_BREAKOUT")
        # Close-confirmed breakouts can only be filled on the following bar.
        self.assertEqual(result["breakout"]["entry"], 97.4)
        self.assertEqual(result["breakout"]["signal_bar_time"], data[2]["timestamp"].isoformat())
        self.assertEqual(result["breakout"]["signal_time"], (data[2]["timestamp"] + timedelta(minutes=5)).isoformat())
        self.assertEqual(result["breakout"]["decision_time"], result["breakout"]["entry_time"])
        self.assertEqual(result["breakout"]["entry_time"], data[3]["timestamp"].isoformat())
        self.assertEqual(result["breakout"]["entry_model"], "next_bar_open_after_close_confirmation")
        self.assertGreater(result["early"]["pnl_r"], 0)

    def test_stop_wins_when_stop_and_target_hit_in_same_candle(self):
        data = candles([
            (100, 100.5, 99.5, 100, 1000),
            (100, 103, 97, 100, 1000),
            (100, 100, 100, 100, 1000),
        ])
        result = run_backtest(data, "2025-12-31T23:59:00+00:00", "LONG", 1.0, target_r=2.0)
        self.assertEqual(result["early"]["status"], "STOP_AMBIGUOUS_STOP_FIRST")
        self.assertEqual(result["early"]["pnl_r"], -1.0)

    def test_entry_bar_is_checked_for_stop_and_target(self):
        data = candles([
            (100, 103, 97, 100, 1000),
            (100, 100, 100, 100, 1000),
        ])
        result = run_backtest(data, "2025-12-31T23:59:00+00:00", "LONG", 1.0, target_r=2.0)
        self.assertEqual(result["early"]["status"], "STOP_AMBIGUOUS_STOP_FIRST")
        self.assertEqual(result["early"]["bars_held"], 1)

    def test_no_future_candle_does_not_invent_entry(self):
        data = candles([(100, 101, 99, 100, 1000)])
        result = run_backtest(data, "2026-01-02T00:00:00+00:00", "LONG", 1.0)
        self.assertEqual(result["early"]["status"], "NO_POST_AVAILABILITY_CANDLE")

    def test_future_atr_timestamp_is_rejected(self):
        data = candles([(100, 101, 99, 100, 1000)])
        with self.assertRaisesRegex(ValueError, "ATR timestamp must be at or before event time"):
            backtest_event(
                data,
                "2026-01-01T00:00:00+00:00",
                "LONG",
                1.0,
                atr_time="2026-01-01T00:05:00+00:00",
                available_at="2026-01-01T00:00:00+00:00",
            )


    def test_non_finite_ohlcv_from_csv_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad_wti.csv"
            path.write_text(
                "timestamp,open,high,low,close,volume\n"
                "2026-01-01T00:00:00+00:00,100,101,99,100,nan\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "volume must be finite"):
                load_candles_csv(path)

    def test_negative_volume_in_direct_backtest_input_is_rejected(self):
        data = candles([(100, 101, 99, 100, 1000)])
        data[0]["volume"] = -1.0
        with self.assertRaisesRegex(ValueError, "volume must be non-negative"):
            backtest_event(
                data,
                "2025-12-31T23:59:00+00:00",
                "LONG",
                1.0,
                atr_time="2025-12-31T23:54:00+00:00",
                available_at="2025-12-31T23:59:00+00:00",
            )

    def test_event_to_first_bar_gap_requires_session_calendar(self):
        data = candles([
            (100, 101, 99, 100, 1000),
            (100, 101, 99, 100, 1000),
        ])
        # Event is stamped at the first bar, but the next available bar is 10 minutes later.
        data[1]["timestamp"] = data[0]["timestamp"] + timedelta(minutes=10)
        result = run_backtest(data, "2026-01-01T00:00:00+00:00", "LONG", 1.0)
        self.assertEqual(result["early"]["status"], "UNMODELED_SESSION_GAP")
        self.assertEqual(result["early"]["gap_minutes"], 10.0)
        self.assertEqual(result["breakout"]["status"], "UNMODELED_SESSION_GAP")
        self.assertEqual(result["data_quality"]["unmodeled_gap_count"], 1)
        self.assertFalse(result["data_quality"]["session_calendar_used"])

    def test_open_trade_is_not_scored_across_unmodeled_bar_gap(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        data = [
            {"timestamp": start, "open": 100.0, "high": 100.5, "low": 99.5, "close": 100.0, "volume": 1000.0},
            {"timestamp": start + timedelta(minutes=5), "open": 100.0, "high": 100.5, "low": 99.5, "close": 100.0, "volume": 1000.0},
            {"timestamp": start + timedelta(minutes=25), "open": 100.0, "high": 100.5, "low": 99.5, "close": 100.0, "volume": 1000.0},
        ]
        result = run_backtest(data, "2025-12-31T23:59:00+00:00", "LONG", 1.0)
        self.assertEqual(result["early"]["status"], "UNMODELED_SESSION_GAP")
        self.assertIsNone(result["early"]["pnl_r"])
        self.assertEqual(result["breakout"]["status"], "UNMODELED_SESSION_GAP")

    def test_boolean_ohlcv_values_are_rejected(self):
        for key in ("open", "high", "low", "close", "volume"):
            with self.subTest(key=key):
                data = candles([(100, 101, 99, 100, 1000)])
                data[0][key] = True
                with self.assertRaisesRegex(ValueError, rf"candle 0 {key} must not be boolean"):
                    backtest_event(
                        data,
                        "2025-12-31T23:59:00+00:00",
                        "LONG",
                        1.0,
                        atr_time="2025-12-31T23:54:00+00:00",
                available_at="2025-12-31T23:59:00+00:00",
                    )

    def test_invalid_bar_interval_fails_closed(self):
        data = candles([(100, 101, 99, 100, 1000)])
        for interval in (0, True, 2.5):
            with self.subTest(interval=interval):
                with self.assertRaisesRegex(ValueError, "bar interval minutes"):
                    backtest_event(
                        data, "2026-01-01T00:00:00+00:00", "LONG", 1.0,
                        atr_time="2025-12-31T23:55:00+00:00",
                        available_at="2026-01-01T00:00:00+00:00",
                        bar_interval_minutes=interval,
                    )

    def test_invalid_direction_rejected(self):
        with self.assertRaises(ValueError):
            backtest_event(candles([(100, 101, 99, 100, 1000)]), "2026-01-01T00:00:00+00:00", "MAYBE", 1.0, atr_time="2025-12-31T23:55:00+00:00", available_at="2026-01-01T00:00:00+00:00")

    def test_both_results_are_reported_even_when_breakout_absent(self):
        data = candles([
            (100, 101, 99, 100, 1000),
            (100, 100.4, 99.4, 100, 1000),
            (100, 100.3, 99.5, 100, 1000),
            (100, 100.2, 99.6, 100, 1000),
        ])
        result = run_backtest(data, "2025-12-31T23:59:00+00:00", "SHORT", 1.0, breakout_lookback=2)
        self.assertIn("status", result["early"])
        self.assertEqual(result["breakout"]["status"], "NO_BREAKOUT")

    def test_out_of_order_candle_timestamps_are_rejected_in_direct_input(self):
        data = candles([
            (100, 101, 99, 100, 1000),
            (99, 100, 98, 99, 1200),
        ])
        data.reverse()
        with self.assertRaisesRegex(ValueError, "chronological order"):
            backtest_event(
                data,
                "2025-12-31T23:59:00+00:00",
                "SHORT",
                1.0,
                atr_time="2025-12-31T23:54:00+00:00",
                available_at="2025-12-31T23:59:00+00:00",
            )

    def test_out_of_order_candle_timestamps_are_rejected_in_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "out_of_order_wti.csv"
            path.write_text(
                "timestamp,open,high,low,close,volume\n"
                "2026-01-01T00:05:00+00:00,99,100,98,99,1200\n"
                "2026-01-01T00:00:00+00:00,100,101,99,100,1000\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "chronological order"):
                load_candles_csv(path)

    def test_duplicate_candle_timestamps_are_rejected(self):
        data = candles([
            (100, 101, 99, 100, 1000),
            (99, 100, 98, 99, 1200),
        ])
        data[1]["timestamp"] = data[0]["timestamp"]
        with self.assertRaisesRegex(ValueError, "timestamps must be unique"):
            backtest_event(data, "2025-12-31T23:59:00+00:00", "SHORT", 1.0, atr_time="2025-12-31T23:54:00+00:00", available_at="2025-12-31T23:59:00+00:00")

    def test_naive_candle_timestamps_are_rejected(self):
        data = candles(
            [(100, 101, 99, 100, 1000)],
            start=datetime(2026, 1, 1),
        )
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            backtest_event(data, "2025-12-31T23:59:00+00:00", "LONG", 1.0, atr_time="2025-12-31T23:54:00+00:00", available_at="2025-12-31T23:59:00+00:00")

    def test_gap_through_short_stop_fills_at_worse_open(self):
        data = candles([
            (100, 100.5, 99.5, 100, 1000),
            (100, 100.5, 99.5, 100, 1000),
            (102.5, 103, 102, 102.8, 1400),
        ])
        result = run_backtest(data, "2026-01-01T00:00:00+00:00", "SHORT", 1.0)
        self.assertEqual(result["early"]["status"], "STOP_GAP")
        self.assertEqual(result["early"]["stop"], 101.0)
        self.assertEqual(result["early"]["exit"], 102.5)
        self.assertEqual(result["early"]["pnl_r"], -2.5)

    def test_gap_through_long_target_does_not_assume_better_fill(self):
        data = candles([
            (100, 100.5, 99.5, 100, 1000),
            (100, 100.5, 99.5, 100, 1000),
            (103, 104, 102.5, 103.5, 1400),
        ])
        result = run_backtest(data, "2026-01-01T00:00:00+00:00", "LONG", 1.0, target_r=2.0)
        self.assertEqual(result["early"]["status"], "TARGET_GAP")
        self.assertEqual(result["early"]["target"], 102.0)
        self.assertEqual(result["early"]["exit"], 102.0)
        self.assertEqual(result["early"]["pnl_r"], 2.0)


    def test_negative_wti_prices_are_simulated_not_rejected(self):
        # Negative futures prices are historically possible; OHLC geometry remains valid.
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        data = [
            {"timestamp": start, "open": -5.0, "high": -4.5, "low": -5.5, "close": -5.0, "volume": 1000.0},
            {"timestamp": start + timedelta(minutes=5), "open": -5.5, "high": -5.0, "low": -7.1, "close": -6.8, "volume": 1200.0},
        ]
        result = backtest_event(
            data,
            "2025-12-31T23:59:00+00:00",
            "SHORT",
            1.0,
            atr_time="2025-12-31T23:54:00+00:00",
                available_at="2025-12-31T23:59:00+00:00",
        )
        self.assertEqual(result["early"]["status"], "TARGET")
        self.assertEqual(result["early"]["entry"], -5.0)
        self.assertEqual(result["early"]["stop"], -4.0)
        self.assertEqual(result["early"]["target"], -7.0)
        self.assertEqual(result["early"]["pnl_r"], 2.0)


    def test_invalid_spread_costs_are_rejected_instead_of_silently_clamped(self):
        data = candles([(100, 101, 99, 100, 1000)])
        for invalid_spread in (-0.01, float("nan"), float("inf")):
            with self.subTest(spread=invalid_spread):
                with self.assertRaisesRegex(ValueError, "spread|finite"):
                    backtest_event(
                        data,
                        "2026-01-01T00:00:00+00:00",
                        "LONG",
                        1.0,
                        atr_time="2025-12-31T23:55:00+00:00",
                        available_at="2026-01-01T00:00:00+00:00",
                        spread=invalid_spread,
                    )

    def test_valid_round_trip_spread_cost_is_deducted_from_r_multiple(self):
        data = candles([
            (100, 100.5, 99.5, 100, 1000),
            (100, 100.5, 99.5, 100, 1000),
            (103, 104, 102.5, 103.5, 1400),
        ])
        result = run_backtest(data, "2026-01-01T00:00:00+00:00", "LONG", 1.0, target_r=2.0, spread=0.5)
        self.assertEqual(result["early"]["status"], "TARGET_GAP")
        self.assertEqual(result["early"]["pnl_r"], 1.5)


    def test_boolean_numeric_and_integer_parameters_are_rejected(self):
        data = candles([(100, 101, 99, 100, 1000)])
        event_time = "2026-01-01T00:00:00+00:00"
        atr_time = "2025-12-31T23:55:00+00:00"
        numeric_cases = ("atr", "stop_atr", "target_r", "spread")
        for field in numeric_cases:
            with self.subTest(field=field):
                options = {"stop_atr": 1.0, "target_r": 2.0, "spread": 0.0}
                atr = 1.0
                if field == "atr":
                    atr = True
                else:
                    options[field] = True
                with self.assertRaisesRegex(ValueError, "numeric"):
                    backtest_event(data, event_time, "LONG", atr, atr_time=atr_time, available_at=event_time, **options)

        integer_cases = ("breakout_lookback", "max_holding_bars")
        for field in integer_cases:
            with self.subTest(field=field):
                options = {"breakout_lookback": 3, "max_holding_bars": 12}
                options[field] = True
                with self.assertRaisesRegex(ValueError, "integers"):
                    backtest_event(data, event_time, "LONG", 1.0, atr_time=atr_time, available_at=event_time, **options)


    def test_entry_waits_until_first_bar_after_source_available_at(self):
        data = candles([
            (100, 101, 99, 100, 1000),
            (100, 101, 99, 100, 1000),
            (101, 102, 100, 101, 1100),
            (101, 102, 100, 101, 1200),
        ])
        result = run_backtest(
            data, "2026-01-01T00:02:00+00:00", "LONG", 1.0,
            available_at="2026-01-01T00:07:00+00:00",
        )
        self.assertEqual(result["available_at"], "2026-01-01T00:07:00+00:00")
        self.assertEqual(result["early"]["decision_time"], "2026-01-01T00:07:00+00:00")
        self.assertEqual(result["early"]["entry_time"], data[2]["timestamp"].isoformat())
        self.assertNotEqual(result["early"]["entry_time"], data[1]["timestamp"].isoformat())

    def test_availability_before_publication_is_rejected(self):
        data = candles([(100, 101, 99, 100, 1000)])
        with self.assertRaisesRegex(ValueError, "available_at must be at or after event_time"):
            backtest_event(
                data, "2026-01-01T00:02:00+00:00", "LONG", 1.0,
                atr_time="2026-01-01T00:00:00+00:00",
                available_at="2026-01-01T00:01:00+00:00",
            )

    def test_event_ledger_requires_source_url_and_timezone_aware_times(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.csv"
            path.write_text(
                "event_id,event_time,available_at,side,atr,atr_time\n"
                "evt-1,2026-01-01T00:02:00+00:00,2026-01-01T00:02:00+00:00,SHORT,1.0,2026-01-01T00:00:00+00:00\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "source_url"):
                load_events_csv(path)

            path.write_text(
                "event_id,event_time,available_at,side,atr,atr_time,source_url\n"
                "evt-1,2026-01-01T00:02:00,2026-01-01T00:02:00+00:00,SHORT,1.0,2026-01-01T00:00:00+00:00,https://example.com/event/1\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "timestamps must include a timezone"):
                load_events_csv(path)

    def test_event_ledger_requires_https_standard_port_source_url(self):
        cases = (
            ("http://example.com/event/1", "absolute HTTPS URL"),
            ("https://example.com:8443/event/1", "standard HTTPS port"),
            ("https://example.com:bad/event/1", "invalid port"),
        )
        for source_url, message in cases:
            with self.subTest(source_url=source_url), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "events.csv"
                path.write_text(
                    "event_id,event_time,available_at,side,atr,atr_time,source_url\n"
                    f"evt-1,2026-01-01T00:02:00+00:00,2026-01-01T00:02:00+00:00,SHORT,1.0,2026-01-01T00:00:00+00:00,{source_url}\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, message):
                    load_events_csv(path)


    def test_batch_backtest_reports_paired_difference_and_unscored_statuses(self):
        data = candles([
            (100, 101, 99, 100, 1000),
            (100, 100.5, 98.8, 99, 1200),
            (99, 99.2, 97.5, 98, 1500),
            (97.4, 98.2, 96.0, 97, 1800),
            (97, 97.2, 95.0, 96, 1900),
        ])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.csv"
            path.write_text(
                "event_id,event_time,available_at,side,atr,atr_time,source_url\n"
                "evt-1,2026-01-01T00:02:00+00:00,2026-01-01T00:02:00+00:00,SHORT,1.0,2026-01-01T00:00:00+00:00,https://example.com/event/1\n"
                "evt-2,2026-01-01T00:30:00+00:00,2026-01-01T00:30:00+00:00,SHORT,1.0,2026-01-01T00:25:00+00:00,https://example.com/event/2\n",
                encoding="utf-8",
            )
            ledger = load_events_csv(path)

        result = backtest_events(data, ledger, breakout_lookback=2)
        summary = result["summary"]
        self.assertEqual(summary["events_total"], 2)
        self.assertEqual(summary["paired_scored_events"], 1)
        self.assertEqual(summary["unpaired_or_unscored_events"], 1)
        self.assertEqual(summary["mean_early_minus_breakout_r"], 0.0)
        self.assertEqual(summary["ties_count"], 1)
        self.assertEqual(summary["unscored_early_status_counts"], {"NO_POST_AVAILABILITY_CANDLE": 1})
        self.assertEqual(summary["unscored_breakout_status_counts"], {"NO_BREAKOUT": 1})
        self.assertEqual(result["results"][0]["source_url"], "https://example.com/event/1")



    def test_summary_adds_non_overlapping_paired_sensitivity(self):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        def trade(pnl, start_minute, end_minute):
            return {
                "pnl_r": pnl,
                "entry_time": (base + timedelta(minutes=start_minute)).isoformat(),
                "exit_time": (base + timedelta(minutes=end_minute)).isoformat(),
            }
        results = [
            {
                "event_time": base.isoformat(),
                "early": trade(1.0, 5, 20),
                "breakout": trade(0.5, 10, 25),
            },
            {
                "event_time": (base + timedelta(minutes=10)).isoformat(),
                "early": trade(2.0, 15, 30),
                "breakout": trade(1.0, 20, 35),
            },
            {
                "event_time": (base + timedelta(minutes=60)).isoformat(),
                "early": trade(0.2, 65, 80),
                "breakout": trade(0.1, 70, 85),
            },
        ]
        summary = summarize_comparison_results(results)
        self.assertEqual(summary["paired_scored_events"], 3)
        self.assertEqual(summary["non_overlapping_paired_events"], 2)
        self.assertEqual(summary["non_overlapping_events_excluded_for_overlap"], 1)
        self.assertEqual(summary["non_overlapping_events_missing_timestamps"], 0)
        self.assertEqual(summary["non_overlapping_mean_early_minus_breakout_r"], 0.3)
        self.assertEqual(summary["non_overlapping_median_early_minus_breakout_r"], 0.3)
        self.assertIn("does not guarantee statistical independence", summary["non_overlapping_sensitivity_note"])

    def test_batch_summary_reports_overlapping_trade_windows(self):
        results = [
            {
                "early": {
                    "pnl_r": 1.0,
                    "entry_time": "2026-01-01T00:00:00+00:00",
                    "exit_time": "2026-01-01T00:15:00+00:00",
                },
                "breakout": {
                    "pnl_r": 0.5,
                    "entry_time": "2026-01-01T00:05:00+00:00",
                    "exit_time": "2026-01-01T00:20:00+00:00",
                },
            },
            {
                "early": {
                    "pnl_r": 0.5,
                    "entry_time": "2026-01-01T00:10:00+00:00",
                    "exit_time": "2026-01-01T00:25:00+00:00",
                },
                "breakout": {
                    "pnl_r": 0.75,
                    "entry_time": "2026-01-01T00:18:00+00:00",
                    "exit_time": "2026-01-01T00:28:00+00:00",
                },
            },
        ]
        summary = summarize_comparison_results(results)
        self.assertEqual(summary["early_scored_trade_windows"], 2)
        self.assertEqual(summary["breakout_scored_trade_windows"], 2)
        self.assertEqual(summary["overlapping_trade_pairs_early"], 1)
        self.assertEqual(summary["overlapping_trade_pairs_breakout"], 1)
        self.assertIn("not independent", summary["overlap_diagnostic_note"])

    def test_event_ledger_preserves_original_permalink_for_provenance(self):
        original_url = "https://EXAMPLE.com/event/1?token=b&expires=2&utm_source=feed#source"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.csv"
            path.write_text(
                "event_id,event_time,available_at,side,atr,atr_time,source_url\n"
                f"evt-1,2026-01-01T00:02:00+00:00,2026-01-01T00:02:00+00:00,SHORT,1.0,2026-01-01T00:00:00+00:00,{original_url}\n",
                encoding="utf-8",
            )
            ledger = load_events_csv(path)
        self.assertEqual(ledger[0]["source_url"], original_url)
        result = backtest_events(candles([(100, 101, 99, 100, 1000)]), ledger)
        self.assertEqual(result["results"][0]["source_url"], original_url)


    def test_event_ledger_rejects_duplicate_canonical_source_urls(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate_events.csv"
            path.write_text(
                "event_id,event_time,available_at,side,atr,atr_time,source_url\n"
                "evt-1,2026-01-01T00:02:00+00:00,2026-01-01T00:02:00+00:00,SHORT,1.0,2026-01-01T00:00:00+00:00,https://EXAMPLE.com/event/1?utm_source=a#story\n"
                "evt-2,2026-01-01T00:07:00+00:00,2026-01-01T00:07:00+00:00,SHORT,1.0,2026-01-01T00:05:00+00:00,https://example.com/event/1/?utm_source=b\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unique after canonicalization"):
                load_events_csv(path)

    def test_batch_backtest_rejects_duplicate_canonical_source_urls(self):
        data = candles([(100, 101, 99, 100, 1000)])
        events = [
            {"event_id": "evt-1", "event_time": "2026-01-01T00:00:00+00:00",
             "available_at": "2026-01-01T00:00:00+00:00",
             "side": "LONG", "atr": 1.0, "atr_time": "2025-12-31T23:55:00+00:00",
             "source_url": "https://example.com/event/1?utm_campaign=first"},
            {"event_id": "evt-2", "event_time": "2026-01-01T00:00:00+00:00",
             "available_at": "2026-01-01T00:00:00+00:00",
             "side": "LONG", "atr": 1.0, "atr_time": "2025-12-31T23:55:00+00:00",
             "source_url": "https://EXAMPLE.com/event/1/#duplicate"},
        ]
        with self.assertRaisesRegex(ValueError, "unique after canonicalization"):
            backtest_events(data, events)


    def test_breakout_rejects_entry_before_signal_bar_close(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        data = candles([
            (100, 101, 99, 100, 1000),
            (100, 100.5, 98, 98.5, 1200),
            (98.5, 99, 97, 98, 1300),
        ], start=start)
        data[1]["timestamp"] = start + timedelta(minutes=1)
        data[2]["timestamp"] = start + timedelta(minutes=2)
        result = run_backtest(
            data, "2026-01-01T00:00:00+00:00", "SHORT", 1.0,
            breakout_lookback=1, bar_interval_minutes=5,
        )
        self.assertEqual(result["early"]["status"], "UNMODELED_BAR_INTERVAL")
        self.assertEqual(result["breakout"]["status"], "UNMODELED_BAR_INTERVAL")
        self.assertEqual(result["data_quality"]["unexpected_short_interval_count"], 2)
        self.assertEqual(result["data_quality"]["min_observed_interval_minutes"], 1.0)
        self.assertIsNone(result["early"].get("pnl_r"))
        self.assertIsNone(result["breakout"].get("pnl_r"))



    def test_event_ledger_deduplicates_common_ad_click_tracking_parameters(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tracking_duplicates.csv"
            path.write_text(
                "event_id,event_time,available_at,side,atr,atr_time,source_url\n"
                "evt-1,2026-01-01T00:02:00+00:00,2026-01-01T00:02:00+00:00,SHORT,1.0,2026-01-01T00:00:00+00:00,https://example.com/event/1?msclkid=click-a&story=one\n"
                "evt-2,2026-01-01T00:07:00+00:00,2026-01-01T00:07:00+00:00,SHORT,1.0,2026-01-01T00:05:00+00:00,https://EXAMPLE.com/event/1/?story=one&srsltid=click-b#article\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unique after canonicalization"):
                load_events_csv(path)

    def test_event_ledger_decision_time_delays_entry_and_must_follow_availability(self):
        start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
        data = candles([(100, 101, 99, 100, 1000)] * 6, start=start)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events_with_decision_time.csv"
            path.write_text(
                "event_id,event_time,available_at,decision_time,side,atr,atr_time,source_url\n"
                "evt-1,2026-01-01T00:02:00+00:00,2026-01-01T00:03:00+00:00,"
                "2026-01-01T00:12:00+00:00,LONG,1.0,2026-01-01T00:00:00+00:00,"
                "https://example.com/event/1\n",
                encoding="utf-8",
            )
            events = load_events_csv(path)
            self.assertEqual(events[0]["decision_time"], "2026-01-01T00:12:00+00:00")
            report = backtest_events(data, events, max_holding_bars=1)
            result = report["results"][0]
            self.assertEqual(result["decision_time_source"], "explicit")
            self.assertEqual(result["early"]["decision_time"], "2026-01-01T00:12:00+00:00")
            self.assertEqual(result["early"]["entry_time"], data[3]["timestamp"].isoformat())

            path.write_text(
                "event_id,event_time,available_at,decision_time,side,atr,atr_time,source_url\n"
                "evt-1,2026-01-01T00:02:00+00:00,2026-01-01T00:03:00+00:00,"
                "2026-01-01T00:02:00+00:00,LONG,1.0,2026-01-01T00:00:00+00:00,"
                "https://example.com/event/1\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "decision_time is before available_at"):
                load_events_csv(path)


if __name__ == "__main__":
    unittest.main()
