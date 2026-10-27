import unittest
from datetime import date

from sputnik_ranking import disclosure_business_days

from sputnik_ranking import _parse_date, disclosure_lag, disclosure_lag_bucket, rank_purchase_candidates, score_purchase_candidate


def tx(event_id, security="ACME Common Stock", company="ACME Corp", tx_date="2026-10-05"):
    return {
        "event_id": event_id,
        "cik": "0000000001",
        "security": security,
        "company": company,
        "action": "ACQUISTATO",
        "source_kind": "FORM4_TRANSACTION",
        "source_url": f"https://www.sec.gov/Archives/edgar/data/0000000001/000000000126{int(event_id[-1]) if event_id and event_id[-1].isdigit() else 1:06d}/form4.xml",
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

    def test_filing_identity_normalizes_default_https_port_and_trailing_dot(self):
        first = tx("e1", tx_date="2026-10-05")
        second = tx("e2", tx_date="2026-10-05")
        first.pop("accession_number", None)
        second.pop("accession_number", None)
        path = "/Archives/edgar/data/0000000001/000000000126000001/form4.xml"
        first["source_url"] = "https://www.sec.gov" + path + "?source=rss"
        second["source_url"] = "https://www.sec.gov.:443" + path + "#document"

        result = score_purchase_candidate([first, second], today=date(2026, 10, 6))

        self.assertEqual(result["filings"], 1)
        self.assertEqual(result["confirmations"], 5)
        self.assertEqual(result["score"], 60)

    def test_non_primary_or_ambiguous_form4_source_urls_are_excluded(self):
        invalid_urls = [
            "http://www.sec.gov/Archives/edgar/data/0000000001/e1/form4.xml",
            "https://sec.gov.example/Archives/edgar/data/0000000001/e1/form4.xml",
            "https://spoof.example@www.sec.gov/Archives/edgar/data/0000000001/e1/form4.xml",
            "https://www.sec.gov:444/Archives/edgar/data/0000000001/e1/form4.xml",
            "https://www.sec.gov/",
            "https://www.sec.gov/Archives/edgar/data/",
            "https://www.sec.gov/Archives/edgar/data/not-a-cik/000000000126000001/form4.xml",
            "https://www.sec.gov/Archives/edgar/data/1/not-an-accession/form4.xml",
            "https://www.sec.gov/Archives/edgar/data/1/000000000126000001/index.html",
            "https://www.sec.gov/Archives/edgar/data/1/000000000126000001/filing",
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

    def test_invalid_transaction_or_filing_date_is_excluded(self):
        invalid_transaction = tx("e1", tx_date="not-a-date")
        invalid_filing = tx("e2", tx_date="2026-10-05")
        invalid_filing["filing_date"] = "not-a-date"
        self.assertEqual(
            score_purchase_candidate([invalid_transaction], today=date(2026, 10, 6)),
            {},
        )
        self.assertEqual(
            score_purchase_candidate([invalid_filing], today=date(2026, 10, 6)),
            {},
        )

    def test_future_transaction_date_is_excluded_from_as_of_ranking(self):
        item = tx("e1", tx_date="2026-10-07")
        self.assertEqual(
            score_purchase_candidate([item], today=date(2026, 10, 6)),
            {},
        )

    def test_filing_before_transaction_is_excluded(self):
        item = tx("e1", tx_date="2026-10-05")
        item["filing_date"] = "2026-10-04"
        self.assertEqual(
            score_purchase_candidate([item], today=date(2026, 10, 6)),
            {},
        )

    def test_future_filing_date_is_excluded_from_as_of_ranking(self):
        item = tx("e1", tx_date="2026-10-05")
        item["filing_date"] = "2026-10-07"
        self.assertEqual(
            score_purchase_candidate([item], today=date(2026, 10, 6)),
            {},
        )



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



    def test_sec_url_cik_must_match_transaction_issuer(self):
        item = tx("e1")
        item["cik"] = "0000000002"
        self.assertEqual(
            score_purchase_candidate([item], today=date(2026, 10, 6)),
            {},
        )

    def test_sec_url_accession_must_match_transaction_metadata_when_present(self):
        item = tx("e1")
        item["accession_number"] = "0000000001-26-000099"
        self.assertEqual(
            score_purchase_candidate([item], today=date(2026, 10, 6)),
            {},
        )

    def test_matching_sec_url_accession_is_accepted(self):
        item = tx("e1")
        item["accession_number"] = "0000000001-26-000001"
        result = score_purchase_candidate([item], today=date(2026, 10, 6))
        self.assertTrue(result)
        self.assertEqual(result["filings"], 1)

    def test_parse_date_rejects_timestamps_and_trailing_garbage(self):
        # SEC transaction/filing fields are calendar dates, not timestamps.
        # Never silently salvage the first ten characters of a malformed value.
        self.assertIsNone(_parse_date("2026-10-05T23:30:00Z"))
        self.assertIsNone(_parse_date("2026-10-05 trailing-data"))
        self.assertIsNone(_parse_date("2026-1-5"))
        self.assertIsNone(_parse_date(None))
        self.assertEqual(_parse_date("2026-10-05"), date(2026, 10, 5))

    def test_invalid_date_suffix_cannot_pass_filing_chronology(self):
        item = tx("e1", tx_date="2026-10-05 garbage")
        self.assertEqual(score_purchase_candidate([item], today=date(2026, 10, 6)), {})

if __name__ == "__main__":
    unittest.main()
