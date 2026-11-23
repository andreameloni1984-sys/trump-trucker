"""Allarme ⚡ per i post di Trump che sono una "chiamata al mercato".

Esempio reale: 9 aprile 2025, 9:37 di New York, "THIS IS A GREAT TIME TO BUY!!! DJT".
Circa quattro ore dopo Trump sospese i dazi e l'S&P 500 chiuse a +9,5%.

Il rilevamento è volutamente stretto (frasi esplicite su comprare/vendere o su borsa e
mercati che salgono/crollano) per non trasformare ogni post in un allarme. L'allarme
informa soltanto: nessun ordine viene inserito.
"""
from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo

ROME = ZoneInfo("Europe/Rome")
DOMAIN = "MARKET_CALL"

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


def message(item: dict) -> str | None:
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
        "Cosa fare: controlla subito S&P 500 e Nasdaq. Se hai CFD aperti contro questa direzione, verifica lo stop.",
        "Precedente: 9/4/2025 «GREAT TIME TO BUY» → 4 ore dopo stop ai dazi, S&P 500 +9,5% in un giorno.",
        "ℹ️ Solo un avviso: nessun ordine automatico. Trump non sempre ha ragione.",
    ])
