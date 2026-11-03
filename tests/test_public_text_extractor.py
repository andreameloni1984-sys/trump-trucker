import unittest

from trump_tracker import _domains_for_public_text


class PublicItemTextClassificationTests(unittest.TestCase):
    def test_item_text_maps_trade_policy_without_html_extraction(self):
        text = "President announces new tariffs on China after trade talks."
        self.assertEqual(_domains_for_public_text(text), ["TRADE_POLICY"])

    def test_routine_political_endorsement_does_not_create_market_domain(self):
        text = (
            "I endorse the candidate. He is doing a fantastic job representing "
            "his district and is a great representative."
        )
        self.assertEqual(_domains_for_public_text(text), ["POLITICAL_CAMPAIGN"])

    def test_concrete_oil_supply_action_keeps_energy_domain(self):
        text = "OPEC announced a crude oil production cut that reduces supply."
        self.assertIn("ENERGY", _domains_for_public_text(text))


if __name__ == "__main__":
    unittest.main()
