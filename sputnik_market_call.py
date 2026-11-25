"""Allarme ⚡ per i post di Trump che sono una "chiamata al mercato".

Esempio reale: 9 aprile 2025, 9:37 di New York, "THIS IS A GREAT TIME TO BUY!!! DJT".
Circa quattro ore dopo Trump sospese i dazi e l'S&P 500 chiuse a +9,5%.

Il rilevamento è volutamente stretto (frasi esplicite su comprare/vendere o su borsa e
mercati che salgono/crollano) per non trasformare ogni post in un allarme. L'allarme
informa soltanto: nessun ordine viene inserito.
"""
from __future__ import annotations

import logging
import os
import re
from datetime import datetime
from typing import Callable
from zoneinfo import ZoneInfo

ROME = ZoneInfo("Europe/Rome")
DOMAIN = "MARKET_CALL"
# Stesse regole del trade Trump sul conto demo: stop 3%, obiettivo 6%, al massimo 3 giorni di borsa.
STOP_PCT, TARGET_PCT, MAX_DAYS = 0.03, 0.06, 3
LEVERAGE = 20   # CFD su indici (ESMA)

_MARKET = r"(?:stocks?|stock market|markets?|the market|wall street|dow|s&p|nasdaq|401\(?k\)?s?)"
BULLISH = re.compile("|".join([
    r"\bgreat time to (?:buy|invest)\b",
    r"\b(?:now is|it'?s|this is) (?:a |the )?(?:great|good|perfect|best) time to (?:buy|invest)\b",
    r"\bbuy (?:now|stocks|american|the dip)\b",
    rf"\b{_MARKET} (?:will|are going to|is going to|gonna) (?:go up|soar|boom|skyrocket|rise|explode|rocket)\b",
    rf"\b{_MARKET} (?:is|are) (?:booming|soaring|surging|skyrocketing)\b",
    r"\b(?:record|all[- ]time) highs? (?:for|in) (?:the )?(?:stock market|stocks|markets?)\b",
]), re.I)
BEARISH = re.compile("|".join([
    r"\b(?:great|good) time to sell\b",
    r"\bsell (?:now|your stocks|everything)\b",
    rf"\b{_MARKET} (?:will|is going to|are going to|gonna) (?:crash|collapse|tank|plunge|fall)\b",
    rf"\b(?:crash|collapse) (?:of|in) (?:the )?{_MARKET}\b",
]), re.I)


def detect(text: str) -> tuple[str, str] | None:
    """("RIALZO"|"RIBASSO", frase trovata) oppure None."""
    body = " ".join(str(text or "").replace("’", "'").split())
    for direction, pattern in (("RIALZO", BULLISH), ("RIBASSO", BEARISH)):
        match = pattern.search(body)
        if match:
            return direction, match.group(0)
    return None


def _when(published: str) -> str:
    try:
        return datetime.fromisoformat(str(published).replace("Z", "+00:00")).astimezone(ROME).strftime("%H:%M del %d/%m")
    except ValueError:
        return str(published or "ora non disponibile")


def _num(name: str, default: float) -> float:
    try:
        value = float(os.getenv(name, "").replace(",", ".") or default)
    except ValueError:
        return default
    return value if value > 0 else default


def _prices() -> tuple[float | None, float | None]:
    """(S&P 500 future, EUR/USD); None se non disponibili."""
    from sputnik_demo.data import fetch
    out = []
    for symbol in ("ES=F", "EURUSD=X"):
        try:
            out.append(fetch(symbol, range_="5d", interval="1d").last_price)
        except Exception as exc:  # noqa: BLE001
            logging.warning("Prezzo %s non disponibile: %s", symbol, type(exc).__name__)
            out.append(None)
    return out[0], out[1]


def _it(x: float, d: int = 2) -> str:
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def level_lines(direction: str, sp500: float | None, eurusd: float | None) -> list[str]:
    """Stop loss, take profit e importi in euro per un CFD sull'S&P 500 nella direzione di Trump."""
    if not sp500:
        return []
    stop, target = sp500 * STOP_PCT, sp500 * TARGET_PCT
    below, above = ("sotto", "sopra") if direction == "RIALZO" else ("sopra", "sotto")
    side = "🟢 LONG (compra)" if direction == "RIALZO" else "🔴 SHORT (vendi)"
    lines = [f"📌 Se vuoi seguirlo con un CFD sull'S&P 500 (US500): {side}",
             f"   🛑 Stop loss: {_it(stop, 0)} punti {below} il tuo prezzo di entrata (−3%)",
             f"   🎯 Take profit: {_it(target, 0)} punti {above} il tuo prezzo di entrata (+6%)",
             f"   ⏱️ Chiudi comunque dopo {MAX_DAYS} giorni di borsa"]
    if eurusd:
        risk = _num("ACCOUNT_SIZE", 200) * _num("RISK_PCT", 2) / 100
        units = risk / (stop / eurusd)
        notional = units * sp500 / eurusd
        lines += [f"   💶 Posizione da circa {_it(notional)} € (margine circa {_it(notional / LEVERAGE)} €)",
                  f"   ❌ Se scatta lo stop perdi circa {_it(risk)} € · ✅ al take profit guadagni circa {_it(risk * 2)} €",
                  f"   🔢 Quantità: {_it(units, 4)}"]
    return lines


def message(item: dict, prices: Callable[[], tuple] | None = None) -> str | None:
    found = detect(" ".join(str(item.get(k) or "") for k in ("title", "text")))
    if not found:
        return None
    direction, phrase = found
    arrow = "⬆️" if direction == "RIALZO" else "⬇️"
    return "\n".join([
        f"⚡ SPUTNIK — TRUMP PARLA AI MERCATI {arrow}",
        f"📰 {str(item.get('title') or '').strip()[:280]}",
        f"🔎 Frase chiave: «{phrase}» → invito al {direction.lower()} di borsa (S&P 500, Nasdaq)",
        f"🕒 {_when(item.get('published', ''))} (ora italiana)",
        "",
        *level_lines(direction, *(prices or _prices)()),
        "",
        "Cosa fare: controlla subito S&P 500 e Nasdaq. Se hai CFD aperti contro questa direzione, verifica lo stop.",
        "Precedente: 9/4/2025 «GREAT TIME TO BUY» → 4 ore dopo stop ai dazi, S&P 500 +9,5% in un giorno.",
        "ℹ️ Solo un avviso: nessun ordine automatico. Trump non sempre ha ragione.",
    ])
