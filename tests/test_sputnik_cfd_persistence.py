import unittest

from trump_tracker import record_automatic_cfd_signal


class AutomaticCfdSignalPersistenceTests(unittest.TestCase):
    def signal(self):
        return {
            "timestamp": "2026-11-04 02:20 UTC",
            "instrument": "GOLD",
            "direction": "SHORT",
            "status": "EARLY_SETUP",
            "setup_status": "EARLY_SETUP",
            "execution_readiness": "EARLY_SETUP",
            "score": 80,
            "paper_trade_status": "NOT_EXECUTED",
            "quote_provider": "Yahoo Finance chart (1m futures)",
            "quote_symbol": "GC=F",
            "quote_time": "2026-11-04T02:19:00+00:00",
            "quote_age_seconds": 85.0,
            "quote_status": "FRESH",
            "quote_market_type": "FUTURES_CONTINUOUS",
            "quote_currency": "USD",
            "quote_unit": "troy_oz",
            "quote_contract_description": (
                "COMEX gold continuous futures; exact expiry not exposed"
            ),
            "quote_bid": None,
            "quote_ask": None,
            "entry": 3947.3999,
            "stop": 3951.5892,
            "tp1": 3943.2106,
            "tp2": 3939.0214,
            "atr": 2.7928,
            "crosscheck_status": (
                "SPOT_VS_FUTURES_BASIS_CHECK_INDEPENDENCE_UNVERIFIED"
            ),
            "crosscheck_market_type": "SPOT",
            "crosscheck_independence_status": "PROVIDER_REPORTED_NOT_AUDITED",
        }

    def test_persists_full_signal_snapshot_and_keeps_execution_not_executed(self):
        state = {}

        changed = record_automatic_cfd_signal(state, self.signal())

        self.assertTrue(changed)
        history = state["cfd_signal_history"]
        self.assertEqual(len(history), 1)
        record = next(iter(history.values()))

        self.assertEqual(record["record_type"], "SPUTNIK_AUTOMATIC_CFD_SIGNAL")
        self.assertEqual(record["instrument"], "GOLD")
        self.assertEqual(record["direction"], "SHORT")
        self.assertEqual(record["quote_symbol"], "GC=F")
        self.assertEqual(record["market_type"], "FUTURES_CONTINUOUS")
        self.assertEqual(record["currency"], "USD")
        self.assertEqual(record["unit"], "troy_oz")
        self.assertEqual(record["entry"], 3947.3999)
        self.assertEqual(record["stop_loss"], 3951.5892)
        self.assertEqual(record["take_profit_1"], 3943.2106)
        self.assertEqual(record["take_profit_2"], 3939.0214)
        self.assertEqual(record["atr"], 2.7928)
        self.assertEqual(record["execution_status"], "NOT_EXECUTED")
        self.assertEqual(
            record["signal_outcome_status"],
            "NON_VERIFIABLE_CONTRACT_EXPIRY_UNKNOWN",
        )
        self.assertIsNone(record["signal_outcome"])
        self.assertEqual(
            record["score_interpretation"],
            "INTELLIGENCE_PRIORITY_NOT_PROBABILITY_OR_EXECUTION_VALIDITY",
        )

    def test_identical_signal_snapshot_is_deduplicated(self):
        state = {}
        signal = self.signal()

        self.assertTrue(record_automatic_cfd_signal(state, signal))
        self.assertFalse(record_automatic_cfd_signal(state, signal))
        self.assertEqual(len(state["cfd_signal_history"]), 1)

    def test_different_quote_timestamp_is_a_distinct_point_in_time_snapshot(self):
        state = {}
        first = self.signal()
        second = self.signal()
        second["quote_time"] = "2026-11-04T02:20:00+00:00"

        self.assertTrue(record_automatic_cfd_signal(state, first))
        self.assertTrue(record_automatic_cfd_signal(state, second))
        self.assertEqual(len(state["cfd_signal_history"]), 2)

    def test_missing_quote_provenance_is_preserved_as_non_verifiable(self):
        state = {}
        signal = self.signal()
        signal["quote_provider"] = None
        signal["quote_symbol"] = None
        signal["quote_time"] = None
        signal["quote_age_seconds"] = None

        self.assertTrue(record_automatic_cfd_signal(state, signal))
        record = next(iter(state["cfd_signal_history"].values()))

        self.assertEqual(
            record["signal_outcome_status"],
            "NON_VERIFIABLE_MISSING_QUOTE_PROVENANCE",
        )
        self.assertIsNone(record["quote_timestamp"])
        self.assertIsNone(record["quote_age_seconds"])
        self.assertEqual(record["execution_status"], "NOT_EXECUTED")
        self.assertIsNone(record["signal_outcome"])

    def test_missing_levels_are_not_scored(self):
        state = {}
        signal = self.signal()
        signal["entry"] = None
        signal["stop"] = None
        signal["tp1"] = None
        signal["tp2"] = None
        signal["atr"] = None

        self.assertTrue(record_automatic_cfd_signal(state, signal))
        record = next(iter(state["cfd_signal_history"].values()))

        self.assertEqual(
            record["signal_outcome_status"],
            "NOT_SCORABLE_MISSING_LEVELS",
        )
        self.assertIsNone(record["entry"])
        self.assertIsNone(record["signal_outcome"])


if __name__ == "__main__":
    unittest.main()
