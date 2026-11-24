from datetime import datetime, timezone

from sputnik_demo import pac


import pytest


@pytest.fixture(autouse=True)
def _importo(monkeypatch):
    # i test verificano la logica con importi tondi; i valori predefiniti del conto demo sono più bassi
    monkeypatch.setenv("SPUTNIK_PAC_MONTHLY", "100")

# Lunedì 23/11/2026, 10:00 a Francoforte: Xetra aperta
NOW = datetime(2026, 11, 23, 9, 0, tzinfo=timezone.utc)
CATALOG = [
    {"ticker": "VWCEd_EQ", "isin": "IE00BK5BQT80", "currencyCode": "EUR"},
    {"ticker": "8PSGd_EQ", "isin": "IE00B579F325", "currencyCode": "EUR"},
    {"ticker": "BTCEd_EQ", "isin": "DE000A27Z304", "currencyCode": "EUR"},
]
PRICES = {"VWCE.DE": 160.0, "8PSG.DE": 310.0, "BTCE.DE": 47.0}


class Bars:
    def __init__(self, price):
        self.last_price = price


def fetcher(symbol, **_):
    return Bars(PRICES[symbol])


class FakeClient:
    def __init__(self, catalog=CATALOG, holdings=None, free=5000.0):
        self.catalog, self.holdings, self.free = catalog, holdings or {}, free
        self.orders = []

    def instruments(self):
        return self.catalog

    def portfolio(self):
        return [{"ticker": t, "quantity": q, "currentPrice": p} for t, (q, p) in self.holdings.items()]

    def cash(self):
        return {"free": self.free}

    def market(self, ticker, quantity):
        self.orders.append((ticker, quantity))
        return {"id": len(self.orders)}


def test_first_month_buys_80_10_10_once():
    client, sent, st = FakeClient(), [], {}
    pac.run(client, NOW, fetcher, send=lambda t: sent.append(t) or True, st=st)
    spent = {t: q * {"VWCEd_EQ": 160, "8PSGd_EQ": 310, "BTCEd_EQ": 47}[t] for t, q in client.orders}
    assert abs(spent["VWCEd_EQ"] - 80) < 0.1 and abs(spent["8PSGd_EQ"] - 10) < 0.4 and abs(spent["BTCEd_EQ"] - 10) < 0.1
    assert len(sent) == 1 and "comprato Vanguard FTSE All-World" in sent[0]
    assert st["pac"]["months"] == ["2026-11"]
    pac.run(client, NOW, fetcher, send=lambda t: sent.append(t) or True, st=st)
    assert len(client.orders) == 3 and len(sent) == 1


def test_new_money_goes_to_underweight_without_selling():
    # mondo 800, oro 80, bitcoin 120 (oro sotto, bitcoin sopra ma entro 5 punti)
    client = FakeClient(holdings={"VWCEd_EQ": (5.0, 160.0), "8PSGd_EQ": (80 / 310, 310.0), "BTCEd_EQ": (120 / 47, 47.0)})
    pac.run(client, NOW, fetcher, st={})
    tickers = {t for t, q in client.orders}
    assert all(q > 0 for _, q in client.orders)
    assert "BTCEd_EQ" not in tickers and "8PSGd_EQ" in tickers


def test_drift_over_5_points_sells_excess_bitcoin():
    client = FakeClient(holdings={"VWCEd_EQ": (5.0, 160.0), "8PSGd_EQ": (100 / 310, 310.0), "BTCEd_EQ": (300 / 47, 47.0)})
    sent = []
    pac.run(client, NOW, fetcher, send=lambda t: sent.append(t) or True, st={})
    btc = [q for t, q in client.orders if t == "BTCEd_EQ"]
    assert btc and btc[0] < 0 and client.orders[0][0] == "BTCEd_EQ"   # prima la vendita
    assert "ribilanciamento" in sent[0]


def test_missing_bitcoin_goes_to_world_and_closed_market_waits():
    client = FakeClient(catalog=CATALOG[:2])
    sent = []
    pac.run(client, NOW, fetcher, send=lambda t: sent.append(t) or True, st={})
    spent = {t: q * {"VWCEd_EQ": 160, "8PSGd_EQ": 310}[t] for t, q in client.orders}
    assert abs(spent["VWCEd_EQ"] - 90) < 0.2 and "Bitcoin fisico" in sent[0]
    sunday = datetime(2026, 11, 22, 9, 0, tzinfo=timezone.utc)
    client2 = FakeClient()
    pac.run(client2, sunday, fetcher, st={})
    assert client2.orders == []


def test_dry_run_places_no_orders(capsys):
    client = FakeClient()
    st = {}
    pac.run(client, NOW, fetcher, st=st, dry_run=True)
    assert client.orders == [] and "[prova] compro" in capsys.readouterr().out
    assert "2026-11" not in st["pac"]["months"]
