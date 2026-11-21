import gzip
import json
import unittest
import zlib
from unittest.mock import MagicMock, patch

import trump_tracker
from trump_tracker import _decode_http_body, http_get_json


class SecGzipTests(unittest.TestCase):
    def test_decode_variants(self):
        body = b'{"name": "MUSK ELON"}'
        self.assertEqual(_decode_http_body(gzip.compress(body), "gzip"), body)
        self.assertEqual(_decode_http_body(gzip.compress(body), ""), body)  # magic bytes
        self.assertEqual(_decode_http_body(zlib.compress(body), "deflate"), body)
        self.assertEqual(_decode_http_body(body, ""), body)

    def test_http_get_json_handles_gzip_response(self):
        payload = {"name": "BERKSHIRE HATHAWAY INC", "filings": {"recent": {}}}
        response = MagicMock()
        response.read.return_value = gzip.compress(json.dumps(payload).encode())
        response.headers = {"Content-Encoding": "gzip"}
        response.__enter__.return_value = response
        with patch.object(trump_tracker.urllib.request, "urlopen", return_value=response):
            self.assertEqual(http_get_json("https://data.sec.gov/submissions/CIK0001067983.json", "UA test"), payload)


if __name__ == "__main__":
    unittest.main()
