import unittest
from datetime import datetime, timedelta, timezone

from sputnik_demo import trader
from sputnik_demo.data import Bars
from sputnik_demo.t212 import DEMO_BASE, DemoClient

# Lunedì 23/11/2026 ore 10:00 a Francoforte (09:00 UTC): Xetra e Londra aperte
OPEN = datetime(2026, 11, 23, 9, 0, tzinfo=timezone.utc)
START = datetime(2025, 1, 1, tzinfo=timezone.utc)


def bars(closes, last_price=None):
    times = [START + timedelta(days=i) for i in range(len(closes))]
    return Bars("T", times, list(closes), [c * 1.005 for c in closes], [c * 0.995 for c in closes], list(closes),
                last_price=last_price or closes[-1], last_price_time=times[-1])


def breakout():
    closes = [100 * 1.002 ** i for i in range(235)]
    top = closes[-1]
    closes += [top * (1 - 0.002 * (i % 5)) for i in range(24)] + [top * 1.03]
    return closes


class FakeClient:
    def __init__(self, cash=200.0):
        self._cash = cash
        self.holdings = {}
        self.calls = []
        self.next_id = 1

    def cash(self):
        return {"total": self._cash, "free": self._cash}

    def instruments(self):
        return [{"ticker": "4GLDd_EQ", "isin": "DE000A0S9GB0", "currencyCode": "EUR"},
                {"ticker": "VUAAd_EQ", "isin": "IE00BFMXXD54", "currencyCode": "EUR"},
                {"ticker": "VUAAl_EQ", "isin": "IE00BFMXXD54", "currencyCode": "USD"}]

    def portfolio(self):
        return [{"ticker": t, **v} for t, v in self.holdings.items()]

    def market(self, ticker, qty):
        self.calls.append(("market", ticker, qty))
        if qty > 0:
            self.holdings[ticker] = {"quantity": qty, "averagePrice": 100.0, "currentPrice": 100.0}
        else:
            self.holdings.pop(ticker, None)
        return {"id": self.next_id}

    def stop(self, ticker, qty, price):
        self.calls.append(("stop", ticker, qty, price))
        self.next_id += 1
        return {"id": self.next_id}

    def cancel(self, oid):
        self.calls.append(("cancel", oid))


def fetcher_factory(gold_closes, flat=False):
    def fetch(symbol, range_="2y", interval="1d"):
        if symbol == "EURUSD=X":
            return bars([1.10] * 5)
        if symbol == "GC=F":
            return bars(gold_closes)
        if symbol in ("4GLD.DE",):
            return bars([100.0] * 5)
        return bars([100.0] * 300)  # altri strumenti piatti: nessun segnale
    return fetch


class TraderTests(unittest.TestCase):
    def test_only_demo_url_allowed(self):
        with self.assertRaises(ValueError):
            DemoClient("k", "s", base="https://live.trading212.com/api/v0")
        self.assertIn("demo.trading212.com", DEMO_BASE)

    def test_long_signal_buys_etf_with_stop_and_limits(self):
        client, sent = FakeClient(), []
        st = trader.run(client, now=OPEN, fetcher=fetcher_factory(breakout()), send=lambda t: sent.append(t) or True,
                        st=trader.empty_state())
        buys = [c for c in client.calls if c[0] == "market"]
        self.assertEqual(len(buys), 1)
        self.assertEqual(buys[0][1], "4GLDd_EQ")
        self.assertLessEqual(buys[0][2] * 100.0, trader.MAX_EUR_PER_TRADE + 0.01)
        self.assertTrue(any(c[0] == "stop" and c[2] < 0 for c in client.calls))
        self.assertIn("oro", st["positions"])
        self.assertTrue(any("comprato Xetra-Gold" in t for t in sent))

    def test_closed_market_waits_then_buys(self):
        client = FakeClient()
        saturday = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
        st = trader.run(client, now=saturday, fetcher=fetcher_factory(breakout()), st=trader.empty_state())
        self.assertFalse(client.calls)
        self.assertIn("oro", st["pending"])
        st = trader.run(client, now=OPEN, fetcher=fetcher_factory(breakout()), st=st)
        self.assertIn("oro", st["positions"])

    def test_take_profit_sells(self):
        client, sent = FakeClient(), []
        st = trader.run(client, now=OPEN, fetcher=fetcher_factory(breakout()), st=trader.empty_state())
        pos = st["positions"]["oro"]
        client.holdings[pos["ticker"]]["currentPrice"] = pos["target"] + 0.5
        st = trader.run(client, now=OPEN + timedelta(hours=1), fetcher=fetcher_factory(breakout()),
                        send=lambda t: sent.append(t) or True, st=st)
        self.assertNotIn("oro", st["positions"])
        self.assertEqual(st["closed"][0]["reason"], "target")
        self.assertTrue(any(c[0] == "cancel" for c in client.calls))
        self.assertTrue(any("take profit" in t for t in sent))

    def test_stop_triggered_on_t212_is_recorded(self):
        client = FakeClient()
        st = trader.run(client, now=OPEN, fetcher=fetcher_factory(breakout()), st=trader.empty_state())
        client.holdings.clear()  # lo stop su Trading 212 ha venduto
        st = trader.run(client, now=OPEN + timedelta(hours=2), fetcher=fetcher_factory(breakout()), st=st)
        self.assertEqual(st["closed"][0]["reason"], "stop")

    def test_kill_switch_blocks_new_buys(self):
        st = trader.empty_state()
        st["start_value"] = 200.0
        client = FakeClient(cash=160.0)
        st = trader.run(client, now=OPEN, fetcher=fetcher_factory(breakout()), st=st)
        self.assertTrue(st["halted"])
        self.assertFalse([c for c in client.calls if c[0] == "market"])

    def test_max_positions(self):
        st = trader.empty_state()
        for k in ("sp500", "nasdaq", "wti"):
            st["positions"][k] = {"ticker": f"X{k}", "quantity": 1, "entry": 100, "stop": 90, "target": 120,
                                  "stop_order_id": None, "opened_at": OPEN.isoformat(), "spent_eur": 40}
        client = FakeClient()
        for k in ("sp500", "nasdaq", "wti"):
            client.holdings[f"X{k}"] = {"quantity": 1, "averagePrice": 100, "currentPrice": 100}
        st = trader.run(client, now=OPEN, fetcher=fetcher_factory(breakout()), st=st)
        self.assertFalse([c for c in client.calls if c[0] == "market" and c[2] > 0])

    def test_resolves_isin_preferring_currency(self):
        st = trader.empty_state()
        found = trader.resolve_tickers(FakeClient(), st, OPEN)
        self.assertEqual(found["sp500"], "VUAAd_EQ")
        self.assertNotIn("nasdaq", found)


if __name__ == "__main__":
    unittest.main()
