import pytest
from datetime import datetime, timezone

import sputnik_analyst
import sputnik_market_call as mc
import trump_tracker


def test_april_9_2025_post_is_a_bullish_market_call():
    found = mc.detect("THIS IS A GREAT TIME TO BUY!!! DJT")
    assert found and found[0] == "RIALZO"
    assert sputnik_market_call_domain_kept("THIS IS A GREAT TIME TO BUY!!! DJT")


def sputnik_market_call_domain_kept(text):
    domains = trump_tracker._domains_for_public_text(text)
    return not domains and mc.detect(text) is not None


def test_other_bullish_and_bearish_phrases():
    assert mc.detect("The Stock Market is going to boom like never before")[0] == "RIALZO"
    assert mc.detect("Now is a great time to invest in America!")[0] == "RIALZO"
    assert mc.detect("If they win, the stock market will crash")[0] == "RIBASSO"


def test_ordinary_posts_are_not_market_calls():
    for text in ("BE COOL! Everything is going to work out well.",
                 "Somalians have taken over Minnesota, they own it",
                 "Oil prices have dropped precipitously after the Midterm Elections",
                 "Great rally in Pennsylvania tonight, buy tickets at the link"):
        assert mc.detect(text) is None, text


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    monkeypatch.setattr(mc, "_prices", lambda: (None, None))


def test_message_levels_long_and_short():
    item = {"title": "THIS IS A GREAT TIME TO BUY!!! DJT", "published": "2025-04-09T13:37:00+00:00"}
    text = mc.message(item, prices=lambda: (6000.0, 1.0))
    assert "🟢 LONG (compra)" in text
    assert "🛑 Stop loss: 180 punti sotto" in text and "🎯 Take profit: 360 punti sopra" in text
    assert "perdi circa 4,00 €" in text and "guadagni circa 8,00 €" in text
    short = mc.message({"title": "The stock market is going to crash", "published": ""}, prices=lambda: (6000.0, None))
    assert "🔴 SHORT (vendi)" in short and "180 punti sopra" in short and "€" not in short


def test_message_without_prices_has_no_levels():
    text = mc.message({"title": "THIS IS A GREAT TIME TO BUY!!! DJT", "published": ""})
    assert "Stop loss" not in text


def test_message_has_direction_time_and_no_order():
    text = mc.message({"title": "THIS IS A GREAT TIME TO BUY!!! DJT", "published": "2025-04-09T13:37:00+00:00"})
    assert text.startswith("⚡ SPUTNIK — TRUMP PARLA AI MERCATI ⬆️")
    assert "15:37 del 09/04" in text and "nessun ordine automatico" in text


def test_deliver_puts_market_call_first():
    now = datetime(2025, 4, 9, 13, 45, tzinfo=timezone.utc)
    state = {"analyst_started_at": "2025-01-01T00:00:00+00:00"}
    item = {"title": "THIS IS A GREAT TIME TO BUY!!! DJT", "published": "2025-04-09T13:37:00+00:00",
            "evidence": "PUBLIC_RSS_ITEM", "domains": ["MARKET_CALL"], "source": "PUBLIC_RSS", "url": "u"}
    sent = []
    sputnik_analyst.deliver(state, [item], [], [], lambda t: sent.append(t) or True, now=now)
    assert sent and sent[0].startswith("⚡ SPUTNIK")
