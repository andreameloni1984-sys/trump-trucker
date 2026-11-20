from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import patch

from sputnik_us_intraday import deliver, scan_invest
from sputnik_us_news import catalyst

NOW = datetime(2026, 11, 20, 16, 0, tzinfo=timezone.utc)
CATALOG = {"ORCL": {"type": "STOCK", "name": "Oracle"}}


def news(title, url="original"):
    return {"kind": "wire", "issuer": "", "title": title, "text": "",
            "url": f"https://example.org/{url}", "published": (NOW - timedelta(minutes=8)).isoformat()}


class InvestTests(unittest.TestCase):
    def setUp(self):
        issuers = patch("sputnik_us_news._sec_issuers", return_value={"oracle": {"ORCL", "ORCL-PD"}})
        issuers.start()
        self.addCleanup(issuers.stop)

    def test_catalog_missing_and_conflicting_exchange_symbol(self):
        item = news("Oracle (NYSE:ORCL) raises revenue guidance")
        with patch("sputnik_us_intraday.read_bars") as read:
            state = {}
            self.assertEqual(scan_invest([item], state, NOW, None, read=read), [])
            read.assert_not_called()
        self.assertIn("catalogo indisponibile", state["invest_events"][item["url"]]["detail"])
        self.assertIsNone(catalyst(news("Oracle (NYSE:IBM) raises revenue guidance"), invest=True))

    def test_prepare_then_enter_updates_pravda_and_only_notifies_once(self):
        item = news("Oracle (NYSE:ORCL) raises revenue guidance")
        state = {}
        clock = lambda: NOW
        without_quotes = lambda *args, **kwargs: ("dati indisponibili", [])
        messages = scan_invest([item], state, NOW, CATALOG, read=without_quotes, clock=clock)
        self.assertEqual(messages[0]["stage"], "PREPARARE")
        self.assertIn("ENTRY: N/D", messages[0]["text"])
        sent = []
        self.assertEqual(deliver(messages, send=lambda text: sent.append(text) or True, clock=clock), 1)
        self.assertEqual(scan_invest([item], state, NOW, CATALOG, read=without_quotes, clock=clock), [])

        bars = []
        for index in range(50):
            close = 100 + index * 0.03
            bars.append((int(NOW.timestamp()) - (50 - index) * 60, close + 0.04,
                         close - 0.04, close, 200 if index == 49 else 100))
        stamp, high, low, close, volume = bars[-1]
        bars[-1] = stamp, high + 0.08, low, close + 0.06, volume
        read = lambda *args, **kwargs: (None, bars)
        copy = news(item["title"], "syndicated")
        result = scan_invest([copy], state, NOW, CATALOG, read=read, clock=clock)
        self.assertEqual([message["stage"] for message in result], ["ENTRARE"])
        self.assertEqual(state["invest_events"][copy["url"]]["status"], "duplicato")
        opened = state["pravda"][-1]
        self.assertLess(opened["levels"]["stop"], opened["price"])
        self.assertLess(opened["levels"]["tp1"], opened["levels"]["tp2"])

        start = int(NOW.timestamp())
        followup = [(start + index * 60, 102, 101, 101.5, 100) for index in range(60)]
        later = NOW + timedelta(minutes=60)
        scan_invest([], state, later, CATALOG, read=lambda *args, **kwargs: (None, followup),
                    clock=lambda: later)
        self.assertEqual(opened["prices"], {str(horizon): 101.5 for horizon in (5, 15, 30, 60)})
        self.assertTrue(opened["complete"])
        self.assertIn("earnings", state["pravda_summary"])

    def test_short_is_research_and_future_announcement_is_discarded(self):
        item = news("Oracle (NYSE:ORCL) cuts revenue guidance")
        future = news("Oracle (NYSE:ORCL) plans to announce earnings", "future")
        state = {}
        result = scan_invest([item, future], state, NOW, CATALOG,
                             read=lambda *args, **kwargs: (None, []), clock=lambda: NOW)
        self.assertEqual(len(result), 1)
        self.assertIn("🔴 SHORT (tesi simulata)", result[0]["text"])
        self.assertEqual(result[0]["stage"], "PREPARARE")
        self.assertEqual(state["invest_events"][future["url"]]["evidence"], "annuncio futuro")
