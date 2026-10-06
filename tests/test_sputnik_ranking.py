import unittest
from datetime import date

from sputnik_ranking import rank_purchase_candidates, score_purchase_candidate


def tx(event_id, security="ACME Common Stock", company="ACME Corp", tx_date="2026-10-05"):
    return {
        "event_id": event_id,
        "cik": "0000000001",
        "security": security,
        "company": company,
        "action": "ACQUISTATO",
        "source_kind": "FORM4_TRANSACTION",
        "source_url": "https://www.sec.gov/example",
        "transaction_date": tx_date,
        "filing_date": tx_date,
    }


class RankingTests(unittest.TestCase):
    def test_single_form4_cannot_be_buy(self):
        result = score_purchase_candidate([tx("e1")], today=date(2026, 10, 6))
        self.assertEqual(result["score"], 60)
        self.assertEqual(result["signal"], "OSSERVA")

    def test_repeated_recent_form4_stays_below_buy_until_three_filings(self):
        result = score_purchase_candidate(
            [tx("e1", tx_date="2026-10-05"), tx("e2", tx_date="2026-10-04")],
            today=date(2026, 10, 6),
        )
        self.assertEqual(result["score"], 65)
        self.assertEqual(result["signal"], "OSSERVA")

    def test_three_distinct_recent_filings_reach_buy_threshold(self):
        result = score_purchase_candidate(
            [
                tx("e1", tx_date="2026-10-05"),
                tx("e2", tx_date="2026-10-04"),
                tx("e3", tx_date="2026-10-03"),
            ],
            today=date(2026, 10, 6),
        )
        self.assertEqual(result["score"], 75)
        self.assertEqual(result["signal"], "COMPRA")

    def test_invalid_date_gets_no_recency_points(self):
        result = score_purchase_candidate([tx("e1", tx_date="not-a-date")], today=date(2026, 10, 6))
        self.assertEqual(result["recency"], 0)

    def test_non_purchase_is_excluded(self):
        item = tx("e1")
        item["action"] = "VENDUTO"
        self.assertEqual(rank_purchase_candidates([item]), [])

    def test_ranking_is_descending(self):
        rows = [
            tx("a1", security="LOW", company="Low", tx_date="2026-09-01"),
            tx("b1", security="HIGH", company="High", tx_date="2026-10-05"),
            tx("b2", security="HIGH", company="High", tx_date="2026-10-04"),
            tx("b3", security="HIGH", company="High", tx_date="2026-10-03"),
        ]
        ranked = rank_purchase_candidates(rows, today=date(2026, 10, 6))
        self.assertEqual(ranked[0]["security"], "HIGH")
        self.assertEqual(ranked[0]["rank"], 1)


if __name__ == "__main__":
    unittest.main()
