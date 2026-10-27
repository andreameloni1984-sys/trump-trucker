import unittest
from datetime import date

from sputnik_ranking import disclosure_business_days

from sputnik_ranking import disclosure_lag, disclosure_lag_bucket, rank_purchase_candidates, score_purchase_candidate


def tx(event_id, security="ACME Common Stock", company="ACME Corp", tx_date="2026-10-05"):
    return {
        "event_id": event_id,
        "cik": "0000000001",
        "security": security,
        "company": company,
        "action": "ACQUISTATO",
        "source_kind": "FORM4_TRANSACTION",
        "source_url": f"https://www.sec.gov/Archives/edgar/data/0000000001/{event_id}/form4.xml",
        "transaction_date": tx_date,
        "filing_date": tx_date,
    }


class RankingTests(unittest.TestCase):
    def test_single_form4_cannot_be_buy(self):
        result = score_purchase_candidate([tx("e1")], today=date(2026, 10, 6))
        self.assertEqual(result["score"], 60)
        self.assertEqual(result["event_strength"], 20)
        self.assertEqual(result["signal"], "OSSERVA")

    def test_repeated_recent_form4_stays_below_buy_until_three_filings(self):
        result = score_purchase_candidate(
            [tx("e1", tx_date="2026-10-05"), tx("e2", tx_date="2026-10-04")],
            today=date(2026, 10, 6),
        )
        self.assertEqual(result["score"], 65)
        self.assertEqual(result["signal"], "OSSERVA")

    def test_three_distinct_recent_filings_do_not_buy_without_other_evidence(self):
        result = score_purchase_candidate(
            [
                tx("e1", tx_date="2026-10-05"),
                tx("e2", tx_date="2026-10-04"),
                tx("e3", tx_date="2026-10-03"),
            ],
            today=date(2026, 10, 6),
        )
        self.assertEqual(result["score"], 70)
        self.assertEqual(result["signal"], "OSSERVA")

    def test_multiple_transactions_from_one_filing_count_as_one_confirmation(self):
        first = tx("e1", tx_date="2026-10-05")
        second = tx("e2", tx_date="2026-10-04")
        same_filing_url = "https://www.sec.gov/Archives/edgar/data/1/000000000126000001/form4.xml?source=rss"
        first["source_url"] = same_filing_url
        second["source_url"] = same_filing_url + "#transaction"
        first["accession_number"] = "0000000001-26-000001"
        second["accession_number"] = "000000000126000001"

        result = score_purchase_candidate([first, second], today=date(2026, 10, 6))

        self.assertEqual(result["filings"], 1)
        self.assertEqual(result["confirmations"], 5)
        self.assertEqual(result["score"], 60)
        self.assertEqual(result["signal"], "OSSERVA")

    def test_non_primary_or_ambiguous_form4_source_urls_are_excluded(self):
        invalid_urls = [
            "http://www.sec.gov/Archives/edgar/data/0000000001/e1/form4.xml",
            "https://sec.gov.example/Archives/edgar/data/0000000001/e1/form4.xml",
            "https://spoof.example@www.sec.gov/Archives/edgar/data/0000000001/e1/form4.xml",
            "https://www.sec.gov:444/Archives/edgar/data/0000000001/e1/form4.xml",
            "https://www.sec.gov/",
            "https://www.sec.gov/Archives/edgar/data/",
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                item = tx("e1")
                item["source_url"] = url
                self.assertEqual(
                    score_purchase_candidate([item], today=date(2026, 10, 6)),
                    {},
                )

    def test_primary_sec_archive_url_with_query_remains_valid(self):
        item = tx("e1")
        item["source_url"] += "?source=rss#document"
        result = score_purchase_candidate([item], today=date(2026, 10, 6))
        self.assertTrue(result)
        self.assertEqual(result["source_quality"], 25)

    def test_invalid_date_gets_no_recency_points(self):
        result = score_purchase_candidate([tx("e1", tx_date="not-a-date")], today=date(2026, 10, 6))
        self.assertEqual(result["recency"], 0)



    def test_disclosure_business_days_weekend_aware(self):
        self.assertEqual(disclosure_business_days("2026-10-09", "2026-10-12"), 1)
        self.assertEqual(disclosure_business_days("2026-10-10", "2026-10-12"), 1)
        self.assertEqual(disclosure_business_days("2026-10-05", "2026-10-08"), 3)
        self.assertEqual(disclosure_business_days("2026-10-05", "2026-10-05"), 0)
        self.assertIsNone(disclosure_business_days("2026-10-08", "2026-10-07"))

    def test_disclosure_lag_same_day(self):
        self.assertEqual(disclosure_lag("2026-10-05", "2026-10-05"), 0)
        self.assertEqual(disclosure_lag_bucket("2026-10-05", "2026-10-05"), "SAME_DAY")

    def test_disclosure_lag_buckets(self):
        self.assertEqual(disclosure_lag_bucket("2026-10-05", "2026-10-07"), "1-3_GIORNI")
        self.assertEqual(disclosure_lag_bucket("2026-10-05", "2026-11-19"), "4-45_GIORNI")
        self.assertEqual(disclosure_lag_bucket("2026-10-05", "2026-12-01"), "OLTRE_45_GIORNI")

    def test_disclosure_lag_invalid_or_negative_is_unknown(self):
        self.assertIsNone(disclosure_lag("not-a-date", "2026-10-05"))
        self.assertEqual(disclosure_lag_bucket("2026-10-05", "2026-10-04"), "N/D")
        self.assertEqual(disclosure_lag_bucket("not-a-date", "2026-10-05"), "N/D")

    def test_disclosure_lag_is_reported_but_does_not_change_score(self):
        item = tx("e1", tx_date="2026-10-05")
        item["filing_date"] = "2026-10-20"
        result = score_purchase_candidate([item], today=date(2026, 10, 21))
        self.assertEqual(result["score"], 55)
        self.assertEqual(result["disclosure_lag_days"], 15)
        self.assertEqual(result["disclosure_lag_bucket"], "4-45_GIORNI")
        self.assertEqual(result["disclosure_business_days"], 11)

    def test_non_purchase_is_excluded(self):
        item = tx("e1")
        item["action"] = "VENDUTO"
        self.assertEqual(rank_purchase_candidates([item]), [])

    def test_missing_security_identity_is_excluded_from_ranking(self):
        missing_security = tx("e1")
        missing_security["security"] = ""
        missing_cik = tx("e2")
        missing_cik["cik"] = ""
        self.assertEqual(
            rank_purchase_candidates(
                [missing_security, missing_cik], today=date(2026, 10, 6)
            ),
            [],
        )

    def test_unidentified_row_cannot_merge_into_named_security_group(self):
        identified = tx("e1", security="ACME Common Stock", company="ACME Corp")
        unidentified = tx("e2", security="", company="ACME Corp")
        result = rank_purchase_candidates(
            [identified, unidentified], today=date(2026, 10, 6)
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["filings"], 1)

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
