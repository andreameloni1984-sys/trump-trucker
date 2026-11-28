from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import sputnik_compare as sc


def fake_fetcher(final):
    """Ogni simbolo vale 100 il giorno di partenza; alla fine vale 100 × final(symbol). EURUSD fisso a 1."""
    t0 = datetime(2026, 11, 25, 21, tzinfo=timezone.utc)

    def fetch(symbol, range_="1y", interval="1d"):
        end = final(symbol) if symbol != "EURUSD=X" else 1.0
        return SimpleNamespace(time=[t0 - timedelta(days=1), t0, t0 + timedelta(days=7)],
                               close=[100.0, 100.0, 100.0 * end], last_price=None)
    return fetch


def test_no_secret_no_section(monkeypatch):
    monkeypatch.delenv("SPUTNIK_PIE_WEIGHTS", raising=False)
    assert sc.section(fake_fetcher(lambda s: 1.0)) == []


def test_portfolio_vs_benchmarks(monkeypatch):
    monkeypatch.setenv("SPUTNIK_PIE_WEIGHTS", "AAA:90, BBB.MI:10")
    monkeypatch.setenv("SPUTNIK_PIE_START", "2026-11-25")
    text = "\n".join(sc.section(fake_fetcher(lambda s: {"BBB.MI": 1.10}.get(s, 1.0))))
    assert "Il tuo portafoglio: +1,0%" in text and "S&P 500 (VUAA): +0,0%" in text
    assert "avanti di 1,0 punti" in text


def test_missing_prices(monkeypatch):
    monkeypatch.setenv("SPUTNIK_PIE_WEIGHTS", "AAA:100")
    def broken(symbol, **kw):
        raise OSError("rete")
    assert "non disponibili" in sc.section(broken)[0]
