from datetime import datetime, timedelta, timezone

from sputnik_demo import slow_trend as st_mod

NOW = datetime(2026, 12, 1, 9, 30, tzinfo=timezone.utc)      # martedì, Xetra aperta


class Bars:
    def __init__(self, closes, last=100.0):
        start = datetime(2024, 12, 15, tzinfo=timezone.utc)
        self.time = [start + timedelta(days=30 * i) for i in range(len(closes))]
        self.close = closes
        self.last_price = last


def fetcher(trend):
    def f(symbol, **_):
        if symbol.endswith(".DE"):
            return Bars([100.0], last=100.0)
        closes = [100 + i for i in range(24)] if trend[symbol] else [200 - i for i in range(24)]
        return Bars(closes)
    return f


class Client:
    def __init__(self, held=None):
        self.orders, self.held = [], held or {}

    def instruments(self):
        return [{"ticker": t, "isin": i, "currencyCode": "EUR"} for t, i in
                (("4GLD", "DE000A0S9GB0"), ("VUAA", "IE00BFMXXD54"), ("SXRV", "IE00B53SZB19"))]

    def portfolio(self):
        return [{"ticker": t, "quantity": q, "currentPrice": 110.0} for t, q in self.held.items()]

    def cash(self):
        return {"free": 5000.0}

    def market(self, ticker, qty):
        self.orders.append((ticker, qty))


def test_signal_majority_of_three():
    up = [100 + i for i in range(14)]
    assert st_mod.signal(up)[0] is True
    assert st_mod.signal([200 - i for i in range(14)])[0] is False
    assert st_mod.signal([100.0] * 5) is None


def test_buys_in_trend_sells_out_of_trend_once_a_month():
    client = Client(held={"VUAA": 2.0})
    sent, st = [], {}
    trend = {"GC=F": True, "^GSPC": False, "^NDX": True}
    st_mod.run(client, NOW, fetcher(trend), send=lambda t: sent.append(t) or True, st=st)
    assert ("4GLD", 2.0) in client.orders and ("SXRV", 2.0) in client.orders and ("VUAA", -2.0) in client.orders
    assert "COMPRATO" in sent[0] and "VENDUTO" in sent[0]
    st_mod.run(client, NOW + timedelta(hours=1), fetcher(trend), st=st)
    assert len(client.orders) == 3


def test_holds_when_nothing_changes_and_waits_when_closed():
    client = Client(held={"4GLD": 1.0})
    sent = []
    st_mod.run(client, NOW, fetcher({"GC=F": True, "^GSPC": False, "^NDX": False}),
               send=lambda t: sent.append(t) or True, st={})
    assert client.orders == [] and "resto investito" in sent[0] and "resto liquido" in sent[0]
    sunday = datetime(2026, 12, 6, 10, 0, tzinfo=timezone.utc)
    c2 = Client()
    st_mod.run(c2, sunday, fetcher({"GC=F": True, "^GSPC": True, "^NDX": True}), st={})
    assert c2.orders == []
