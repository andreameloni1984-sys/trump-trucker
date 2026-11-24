from datetime import datetime, timedelta, timezone

from sputnik_demo import trump_trade as tt


import pytest


@pytest.fixture(autouse=True)
def _importo(monkeypatch):
    # i test verificano la logica con importi tondi; i valori predefiniti del conto demo sono più bassi
    monkeypatch.setenv("SPUTNIK_TRUMP_TRADE_EUR", "50")

POST = datetime(2025, 4, 9, 13, 37, tzinfo=timezone.utc)          # mercoledì, 15:37 a Francoforte
CTX = {"trump": [{"title": "THIS IS A GREAT TIME TO BUY!!! DJT", "published": POST.isoformat(), "url": "p1"},
                 {"title": "Somalians own Minnesota", "published": POST.isoformat(), "url": "p2"}]}


class Bars:
    def __init__(self, times, closes, last):
        self.time, self.close, self.last_price = times, closes, last


def fetcher(run_up=0.0):
    def f(symbol, **_):
        if symbol == tt.FUTURES:
            return Bars([POST - timedelta(hours=1)], [5000.0], 5000.0 * (1 + run_up))
        return Bars([], [], 500.0)
    return f


class Client:
    def __init__(self):
        self.orders, self.stops, self.held = [], [], {}

    def instruments(self):
        return [{"ticker": "SXR8d_EQ", "isin": "IE00B5BMR087", "currencyCode": "EUR"}]

    def cash(self):
        return {"free": 1000.0}

    def portfolio(self):
        return [{"ticker": t, "quantity": q, "currentPrice": p} for t, (q, p) in self.held.items()]

    def market(self, ticker, qty):
        self.orders.append((ticker, qty))
        return {}

    def stop(self, ticker, qty, price):
        self.stops.append((ticker, qty, price))
        return {"id": 7}

    def cancel(self, _):
        pass


def test_buys_once_on_great_time_to_buy():
    client, sent, st = Client(), [], {}
    now = POST + timedelta(minutes=10)
    tt.run(client, now, fetcher(), send=lambda t: sent.append(t) or True, st=st, context=CTX)
    assert client.orders == [("SXR8d_EQ", 0.1)] and client.stops[0][2] == 485.0
    assert "comprato dopo il post di Trump" in sent[0]
    tt.run(client, now + timedelta(minutes=15), fetcher(), st=st, context=CTX)
    assert len(client.orders) == 1


def test_skips_when_market_already_moved():
    client, sent = Client(), []
    tt.run(client, POST + timedelta(minutes=30), fetcher(run_up=0.05), send=lambda t: sent.append(t) or True,
           st={}, context=CTX)
    assert client.orders == [] and "saltato" in sent[0]


def test_night_post_bought_at_next_open_but_not_days_later():
    night = datetime(2025, 4, 11, 22, 0, tzinfo=timezone.utc)   # venerdì sera
    ctx = {"trump": [{**CTX["trump"][0], "published": night.isoformat()}]}
    monday = datetime(2025, 4, 14, 7, 30, tzinfo=timezone.utc)   # 9:30 a Francoforte
    assert tt.market_calls(ctx, monday)
    assert not tt.market_calls(ctx, monday + timedelta(days=1))


def test_closes_after_target():
    client, st = Client(), {}
    now = POST + timedelta(minutes=10)
    tt.run(client, now, fetcher(), st=st, context=CTX)
    client.held = {"SXR8d_EQ": (0.1, 531.0)}
    sent = []
    tt.run(client, now + timedelta(days=1), fetcher(), send=lambda t: sent.append(t) or True, st=st, context=CTX)
    assert client.orders[-1] == ("SXR8d_EQ", -0.1) and "obiettivo" in sent[0]
    assert st["trump_trades"]["open"] is None and st["trump_trades"]["closed"][0]["result_pct"] == 6.2


def test_sell_calls_and_closed_market_do_nothing():
    client = Client()
    ctx = {"trump": [{"title": "The stock market will crash", "published": POST.isoformat(), "url": "x"}]}
    tt.run(client, POST + timedelta(minutes=5), fetcher(), st={}, context=ctx)
    sunday = datetime(2025, 4, 13, 10, 0, tzinfo=timezone.utc)
    tt.run(client, sunday, fetcher(), st={}, context=CTX)
    assert client.orders == []
