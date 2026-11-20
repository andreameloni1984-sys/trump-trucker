import json
import sqlite3
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from pravda_analytics.__main__ import (
    MISSING, as_of, export, ingest, normalize, read_gagarin, read_sputnik, report,
    recommendations, stamp, summarize,
)


def sputnik(**changes):
    signal = dict(url="https://example.org/news", ticker="XYZ", direction="SHORT",
                  stage="PREPARARE", published="2026-11-18T13:55:00+00:00",
                  signalled="2026-11-18T14:00:25+00:00", price=100,
                  price_timestamp="2026-11-18T14:00:00+00:00", score=75,
                  category="regolamentazione", prices={"5": 98, "15": 100, "60": 103},
                  complete=True, mfe=4, mae=5)
    signal.update(changes)
    return signal


def normalized_sputnik(**changes):
    signal = sputnik(**changes)
    return normalize("Sputnik", [signal["url"], signal["stage"]], {}, signal, signal["prices"], {})


class AnalyticsTests(unittest.TestCase):
    def test_actual_storage_shapes_dedup_and_later_update(self):
        with tempfile.TemporaryDirectory() as root:
            gagarin, state = (Path(root) / name for name in ("source.db", "sputnik.json"))
            event = dict(direction="LONG", published="2026-11-18T13:55:00+00:00", symbol="ABC")
            first = dict(state="PREPARARE", signaled_at="2026-11-18T14:00:00+00:00",
                         price=100, quote_at="2026-11-18T14:00:00+00:00")
            with sqlite3.connect(gagarin) as db:
                db.execute("CREATE TABLE candidates(id,event,latest,first_signal,entry_signal,observations,outcome)")
                values = [event, first, first, None, {"5": {"at": "2026-11-18T14:05:00+00:00", "price": 105}}, None]
                db.execute("INSERT INTO candidates VALUES (?,?,?,?,?,?,?)", ("key", *map(json.dumps, values)))
                db.execute("UPDATE candidates SET entry_signal=NULL,outcome=NULL")
            db_path = Path(root) / "analytics.db"
            for expected, signal in [(2, sputnik()), (0, sputnik()), (1, sputnik(prices={"5": 99}))]:
                state.write_text(json.dumps({"pravda": [signal, signal]}))
                with sqlite3.connect(db_path) as db:
                    self.assertEqual(ingest(db, [read_gagarin(gagarin), read_sputnik(state)]), expected)
                    self.assertEqual(db.execute("SELECT count(*) FROM signals").fetchone()[0], 2)

    def test_direction_and_simulated_profit_have_different_denominators(self):
        short = normalized_sputnik()
        self.assertEqual(short["observations"]["5"]["theoretical_pct"], 2)
        self.assertIsNone(short["profitable"])
        event = dict(direction="LONG", published="2026-11-18T13:55:00+00:00")
        signal = dict(state="ENTRARE", signaled_at="2026-11-18T14:00:00+00:00",
                      quote_at="2026-11-18T14:00:00+00:00", price=100, levels=[100, 98, 102, 104, 106])
        long = normalize("Gagarin", ["long"], event, signal,
                         {"5": dict(at="2026-11-18T14:05:00+00:00", price=104)},
                         dict(at="2026-11-18T14:03:00+00:00", reason="STOP", exit=98))
        metrics = summarize([short, long])
        self.assertEqual(metrics["horizons"]["5"]["accuracy"], 1)
        self.assertEqual(metrics["modeled_gross_r"], {"n": 1, "mean": -1})
        self.assertEqual(metrics["level_hits"]["stop"]["frequency"], 1)
        self.assertEqual(metrics["net_profitability"]["n"], 0)

    def test_missing_future_reference_and_future_labels(self):
        row = normalized_sputnik()
        self.assertEqual(row["observations"]["30"]["status"], MISSING)
        self.assertIsNone(normalized_sputnik(price=None)["observations"]["5"]["correct"])
        self.assertIsNone(normalized_sputnik(price_timestamp="2026-11-18T14:01:00+00:00")
                          ["observations"]["5"]["correct"])
        cutoff = stamp("2026-11-18T14:04:59+00:00")
        masked = as_of(row, cutoff)
        self.assertIsNone(masked["observations"]["5"]["observed_price"])
        self.assertIsNone(masked["mfe_observed_pct"])
        self.assertEqual(masked["observations"]["5"]["status"], MISSING)

    def test_discovery_requires_later_confirmation(self):
        cutoff = datetime(2026, 11, 20, tzinfo=timezone.utc)
        rows = []
        for days, wins in ((40, True), (10, False)):
            base = cutoff - timedelta(days=days)
            for idx in range(160):
                start = base + timedelta(minutes=idx)
                favored = idx < 80
                rows.append(normalized_sputnik(
                    category="FED" if favored else "SEC", signalled=start.isoformat(),
                    published=(start - timedelta(minutes=3)).isoformat(),
                    price_timestamp=start.isoformat(), prices={"60": 99 if favored == wins else 101},
                ))
        rejected = recommendations(rows, cutoff)
        self.assertGreater(rejected["tested"], 0)
        self.assertEqual(rejected["validated"], [])
        for row in rows[160:]:
            row["observations"]["60"]["correct"] = row["category"] == "FED"
        self.assertTrue(recommendations(rows, cutoff)["validated"])

    def test_daily_exports_with_missing_fields(self):
        cutoff = stamp("2026-11-19T00:00:00+00:00")
        rows, result = report([normalized_sputnik(title="=unsafe()")], date(2026, 11, 18), cutoff)
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root)
            export(directory, rows, result)
            self.assertIn("campione insufficiente", (directory / "report.md").read_text())
            self.assertIn("'=unsafe()", (directory / "signals.csv").read_text())
            self.assertEqual(json.loads((directory / "report.json").read_text())["report"]["total"]["signals"], 1)


if __name__ == "__main__":
    unittest.main()
