import unittest
from unittest.mock import patch

import run_selected_commodity_alerts as alerts


class SelectedCommodityAlertTests(unittest.TestCase):
    def test_configured_universe_contains_exactly_eight_selected_commodities(self):
        configured = alerts.configured_contracts()
        self.assertEqual(set(configured), {
            "GOLD", "SILVER", "COPPER", "WTI", "BRENT", "WHEAT", "CORN", "SOYBEAN"
        })
        self.assertEqual(len(configured), 8)

    def test_contracts_are_not_continuous_future_symbols(self):
        for item in alerts.configured_contracts().values():
            self.assertNotIn("=F", item["symbol"])

    @patch("run_selected_commodity_alerts.fetch_intraday", return_value=None)
    def test_missing_quotes_never_send_alerts(self, fetch):
        state = {}
        with patch("run_selected_commodity_alerts.send_telegram") as sender:
            outcomes = alerts.run_all(state)
        self.assertEqual(set(outcomes.values()), {"NO_DATA"})
        sender.assert_not_called()

    def test_contract_overrides_are_supported(self):
        with patch.dict("os.environ", {"SPUTNIK_GOLD_CONTRACT": "GCZ26.CMX"}):
            self.assertEqual(alerts.configured_contracts()["GOLD"]["symbol"], "GCZ26.CMX")


if __name__ == "__main__":
    unittest.main()
