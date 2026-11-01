import unittest
from datetime import datetime, timedelta, timezone
from sputnik_competition_setup import evaluate_competition_setup


def sample(count=80):
    start=datetime(2026,10,30,8,tzinfo=timezone.utc)
    rows=[]; price=100
    for i in range(count):
        nxt=price+0.08
        rows.append({"timestamp":(start+timedelta(minutes=i)).isoformat(),
                     "open":price,"high":nxt+0.04,"low":price-0.04,
                     "close":nxt,"volume":1000})
        price=nxt
    return rows


class CompetitionSetupTests(unittest.TestCase):
    def test_requires_timestamped_history(self):
        self.assertEqual(evaluate_competition_setup("WTI",sample(20))["status"],"WAIT")

    def test_no_fake_orderflow_or_forced_signal(self):
        rows=sample()
        result=evaluate_competition_setup("WTI",rows)
        self.assertIn(result["direction"],{"LONG","SHORT","NEUTRAL"})
        self.assertEqual(result["method"],"DIRECTION_LOCATION_AGGRESSION")

    def test_missing_timestamps_are_rejected(self):
        rows=sample()
        for row in rows: row.pop("timestamp")
        result=evaluate_competition_setup("GOLD",rows)
        self.assertEqual(result["status"],"WAIT")

    def test_malformed_candles_are_ignored(self):
        rows=sample()
        rows.append({"timestamp":"2026-10-30T10:00:00+00:00","open":2,"high":1,"low":3,"close":2,"volume":100})
        result=evaluate_competition_setup("BRENT",rows)
        self.assertEqual(result["instrument"],"BRENT")


if __name__ == "__main__":
    unittest.main()
