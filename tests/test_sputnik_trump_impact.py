import unittest

from sputnik_trump_impact import analyze_public_policy_item


def item(text, domains, source="TRUTH_ARCHIVE", actor_role=None):
    result = {
        "evidence": "PUBLIC_RSS_ITEM",
        "event_id": "evt-1",
        "url": "https://example.org/public-item",
        "published": "2026-11-01T10:00:00Z",
        "source": source,
        "title": text,
        "text": text,
        "domains": domains,
    }
    if actor_role:
        result["actor_role"] = actor_role
    return result


class TrumpPolicyImpactTests(unittest.TestCase):
    def test_truth_social_oil_supply_disruption_creates_early_long_bias(self):
        rows = analyze_public_policy_item(item(
            "New sanctions threaten crude oil exports and tanker shipments",
            ["ENERGY"],
        ))
        self.assertEqual({row["instrument"] for row in rows}, {"WTI", "BRENT"})
        self.assertTrue(all(row["bias"] == "LONG_BIAS" for row in rows))
        self.assertTrue(all(row["paper_trade_status"] == "NOT_EXECUTED" for row in rows))
        self.assertTrue(all(row["probability_calibrated"] is False for row in rows))

    def test_trade_deal_maps_growth_and_defensive_assets_in_opposite_directions(self):
        rows = analyze_public_policy_item(item(
            "The administration announced a trade deal and trade agreement",
            ["TRADE_POLICY"],
            source="WHITE_HOUSE",
        ))
        by_instrument = {row["instrument"]: row["bias"] for row in rows}
        self.assertEqual(by_instrument["NASDAQ100"], "LONG_BIAS")
        self.assertEqual(by_instrument["GOLD"], "SHORT_BIAS")

    def test_publicly_identified_family_or_adviser_role_is_weighted_but_not_assumed(self):
        rows = analyze_public_policy_item(item(
            "New tariffs and trade restrictions announced",
            ["TRADE_POLICY"],
            actor_role="publicly identified adviser",
        ))
        self.assertTrue(rows)
        self.assertTrue(all(row["actor_class"] == "PUBLICLY_IDENTIFIED_ASSOCIATE" for row in rows))
        self.assertTrue(all(row["actor_weight"] == 0.65 for row in rows))

    def test_unverified_or_missing_source_metadata_does_not_create_bias(self):
        for overrides in (
            {"evidence": "PUBLIC_PAGE"},
            {"url": ""},
            {"published": ""},
            {"event_id": ""},
        ):
            finding = item("New tariffs announced", ["TRADE_POLICY"])
            finding.update(overrides)
            self.assertEqual(analyze_public_policy_item(finding), [])

    def test_negated_policy_event_is_suppressed(self):
        rows = analyze_public_policy_item(item(
            "No new tariffs announced; the trade restrictions are not confirmed",
            ["TRADE_POLICY"],
        ))
        self.assertEqual(rows, [])

    def test_negated_first_clause_does_not_suppress_later_confirmed_event(self):
        rows = analyze_public_policy_item(item(
            "No tariffs were announced; but new tariffs take effect tomorrow",
            ["TRADE_POLICY"],
        ))
        by_instrument = {row["instrument"]: row["bias"] for row in rows}
        self.assertEqual(by_instrument["NASDAQ100"], "SHORT_BIAS")
        self.assertEqual(by_instrument["GOLD"], "LONG_BIAS")

    def test_negated_event_remains_suppressed_within_same_clause(self):
        rows = analyze_public_policy_item(item(
            "New tariffs were not confirmed by the administration",
            ["TRADE_POLICY"],
        ))
        self.assertEqual(rows, [])

    def test_agricultural_export_restriction_maps_to_grains(self):
        rows = analyze_public_policy_item(item(
            "Wheat and corn export ban threatens agricultural exports",
            ["AGRICULTURE"],
            source="WHITE_HOUSE",
        ))
        self.assertEqual({row["instrument"] for row in rows}, {"WHEAT", "CORN", "SOYBEAN"})


    def test_policy_model_is_integrated_into_existing_directional_candidates(self):
        from sputnik_catalyst import directional_news_candidates
        finding = item(
            "New sanctions threaten crude oil exports and tanker shipments",
            ["ENERGY"],
        )
        rows = directional_news_candidates([finding], limit=8)
        wti = next(row for row in rows if row["instrument"] == "WTI")
        self.assertEqual(wti["bias"], "LONG_BIAS")
        self.assertIn("policy_impact", wti)
        self.assertEqual(wti["policy_impact"]["model"], "TRANSPARENT_TOPIC_EVENT_SENTIMENT_V1")


    def test_actor_role_mapping_requires_exact_explicit_public_registry(self):
        import json
        from unittest.mock import patch
        from sputnik_trump_impact import resolve_public_actor_role
        with patch.dict("os.environ", {
            "SPUTNIK_ACTOR_ROLE_MAP": json.dumps({
                "Jane Public": "family",
                "Alex Adviser": "adviser",
            })
        }, clear=True):
            self.assertEqual(resolve_public_actor_role("Jane Public"), "family")
            self.assertEqual(resolve_public_actor_role("Unknown Person"), None)
            self.assertEqual(resolve_public_actor_role("Jane Public Jr"), None)

    def test_feed_url_identifies_truth_archive_and_white_house_official_roles(self):
        from sputnik_trump_impact import _actor_context
        truth = {"source": "PUBLIC_RSS", "feed_url": "https://www.trumpstruth.org/feed"}
        white_house = {"source": "WHITE_HOUSE_RSS", "feed_url": "https://www.whitehouse.gov/news/feed/"}
        self.assertEqual(_actor_context(truth)[0], "PRESIDENT_OFFICIAL_CHANNEL")
        self.assertEqual(_actor_context(white_house)[0], "ADMINISTRATION_OFFICIAL_CHANNEL")

    def test_sentiment_is_context_only_and_does_not_override_event_direction(self):
        rows = analyze_public_policy_item(item(
            "A positive breakthrough: new sanctions threaten crude oil exports",
            ["ENERGY"],
        ))
        self.assertTrue(rows)
        self.assertTrue(all(row["bias"] == "LONG_BIAS" for row in rows))
        self.assertTrue(all(row["model"] == "TRANSPARENT_TOPIC_EVENT_SENTIMENT_V1" for row in rows))


    def test_contrast_word_starts_a_new_clause_without_punctuation(self):
        rows = analyze_public_policy_item(item(
            "No tariffs were announced but new tariffs take effect tomorrow",
            ["TRADE_POLICY"],
        ))
        by_instrument = {row["instrument"]: row["bias"] for row in rows}
        self.assertEqual(by_instrument["NASDAQ100"], "SHORT_BIAS")
        self.assertEqual(by_instrument["GOLD"], "LONG_BIAS")


if __name__ == "__main__":
    unittest.main()
