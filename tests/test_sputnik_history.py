import unittest

from sputnik_history import anticipatory_selector, build_public_history, CORE_ADMINISTRATION


class SputnikHistoryTests(unittest.TestCase):
    def test_public_history_deduplicates_events(self):
        findings = [{"event_id":"a","source":"WHITE_HOUSE","domains":["ENERGY"],"detected_at":"2026-10-07"}]
        history = build_public_history(findings, findings)
        self.assertEqual(len(history), 1)

    def test_repeated_primary_catalyst_can_be_anticipatory(self):
        findings = [
            {"event_id":f"e{i}","source":"WHITE_HOUSE","domains":["ENERGY"],"detected_at":f"2026-10-0{i+1}"}
            for i in range(4)
        ]
        rows = anticipatory_selector(findings)
        self.assertEqual(rows[0]["domain"], "ENERGY")
        self.assertEqual(rows[0]["signal"], "ANTICIPA")
        self.assertGreaterEqual(rows[0]["score"], 60)

    def test_core_roster_is_public_documented_seed(self):
        self.assertGreaterEqual(len(CORE_ADMINISTRATION), 5)
        self.assertTrue(all(row["source"] == "WHITE_HOUSE" for row in CORE_ADMINISTRATION))


if __name__ == "__main__":
    unittest.main()
