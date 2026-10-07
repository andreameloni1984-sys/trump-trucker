import unittest
from unittest.mock import patch

from trump_tracker import FilingEvent, extract_form4_transactions


FORM4_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<ownershipDocument>
  <issuer><issuerName>Trump Media &amp; Technology Group Corp.</issuerName></issuer>
  <reportingOwner><reportingOwnerId><rptOwnerName>Example Insider</rptOwnerName></reportingOwnerId></reportingOwner>
  <nonDerivativeTable>
    <nonDerivativeTransaction>
      <securityTitle><value>Common Stock</value></securityTitle>
      <transactionDate><value>2026-10-06</value></transactionDate>
      <transactionCoding><transactionCode>P</transactionCode></transactionCoding>
      <transactionAmounts>
        <transactionShares><value>100</value></transactionShares>
        <transactionPricePerShare><value>10</value></transactionPricePerShare>
      </transactionAmounts>
    </nonDerivativeTransaction>
  </nonDerivativeTable>
</ownershipDocument>
"""


class Form4ParsingTests(unittest.TestCase):
    def event(self):
        return FilingEvent(
            source="SEC_EDGAR",
            cik="0001849635",
            accession="0001437749-26-021434",
            form="4",
            filed_at="2026-06-23",
            primary_document="rdgdoc.html",
            company="Trump Media & Technology Group Corp.",
            source_url="https://www.sec.gov/Archives/edgar/data/1849635/000143774926021434/rdgdoc.html",
            event_id="event1",
        )

    @patch("trump_tracker.filing_index_documents", return_value=[{"name": "rdgdoc.html"}, {"name": "rdgdoc.xml"}])
    @patch("trump_tracker.fetch_public_document")
    def test_html_primary_document_uses_sibling_xml(self, fetch, _index):
        fetch.side_effect = [FORM4_XML]
        rows = extract_form4_transactions(self.event(), "SPUTNIK/test contact@example.com")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].action, "ACQUISTATO")
        self.assertEqual(rows[0].transaction_code, "P")
        self.assertEqual(rows[0].security, "Common Stock")

    @patch("trump_tracker.filing_index_documents", return_value=[])
    @patch("trump_tracker.fetch_public_document")
    def test_unparseable_form4_returns_no_invented_transaction(self, fetch, _index):
        fetch.side_effect = [b"<html>not xml</html>"]
        rows = extract_form4_transactions(self.event(), "SPUTNIK/test contact@example.com")
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
