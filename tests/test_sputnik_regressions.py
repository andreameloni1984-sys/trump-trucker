import unittest
from datetime import date

from trump_tracker import FilingEvent, TransactionRecord, event_id, filing_url, normalize_cik


class SputnikRegressionTests(unittest.TestCase):
    def test_normalize_cik_pads_to_ten_digits(self):
        self.assertEqual(normalize_cik("320193"), "0000320193")

    def test_event_id_is_stable_for_same_public_filing_identity(self):
        first = event_id("0000320193", "0000320193-26-000001", "4", "form4.xml")
        second = event_id("0000320193", "0000320193-26-000001", "4", "form4.xml")
        self.assertEqual(first, second)

    def test_filing_url_uses_compact_accession(self):
        url = filing_url("0000320193", "0000320193-26-000001", "form4.xml")
        self.assertIn("/320193/000032019326000001/form4.xml", url)

    def test_form4_record_keeps_transaction_and_filing_dates_separate(self):
        tx = TransactionRecord(
            event_id="abc",
            cik="0000320193",
            company="Example Corp",
            form="4",
            action="ACQUISTATO",
            security="Common Stock",
            transaction_date="2026-10-01",
            filing_date="2026-10-02",
        )
        self.assertNotEqual(tx.transaction_date, tx.filing_date)
        self.assertEqual((date.fromisoformat(tx.filing_date) - date.fromisoformat(tx.transaction_date)).days, 1)


if __name__ == "__main__":
    unittest.main()
