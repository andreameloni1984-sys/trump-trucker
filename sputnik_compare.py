"""Confronto settimanale: un portafoglio personale contro gli ETF S&P 500 e Mondo.

I pesi NON sono nel codice: arrivano dal secret SPUTNIK_PIE_WEIGHTS, nel formato
"SIMBOLO:peso,SIMBOLO:peso" con i simboli Yahoo (es. "AAPL:50,VWCE.DE:50").
Senza secret la sezione non compare. Data di partenza: SPUTNIK_PIE_START (AAAA-MM-GG).
Solo prezzi pubblici (Yahoo), nessun accesso a un conto. Il portafoglio è misurato come
comprato alla chiusura della data di partenza e tenuto senza ribilanciare; i simboli
che finiscono con .MI, .DE, .PA, .AS sono già in euro, gli altri convertiti dal dollaro.
Prezzi senza dividendi per le azioni: piccolo svantaggio (circa 1-1,5% l'anno).
"""
from __future__ import annotations

import logging
import os
from datetime import date, timedelta
from typing import Callable

EUR_SUFFIXES = (".MI", ".DE", ".PA", ".AS", ".MC", ".F")
BENCHMARKS = {"S&P 500 (VUAA)": "VUAA.DE", "Mondo (VWCE)": "VWCE.DE"}

log = logging.getLogger("sputnik.compare")


def _closes(fetcher: Callable, symbol: str) -> dict[date, float]:
    bars = fetcher(symbol, range_="1y", interval="1d")
    out = {t.date(): c for t, c in zip(bars.time, bars.close) if c}
    if bars.last_price and bars.time:
        out[bars.time[-1].date()] = bars.last_price
    return out


def _on_or_before(series: dict[date, float], day: date) -> float | None:
    for k in range(8):
        if day - timedelta(days=k) in series:
            return series[day - timedelta(days=k)]
    return None


def _change(series: dict[date, float], fx: dict[date, float] | None) -> float | None:
    if not series:
        return None
    a, z = _on_or_before(series, start_date()), series[max(series)]
    if not a or not z:
        return None
    if fx:   # da dollari a euro: prezzo / EURUSD
        fa, fz = _on_or_before(fx, start_date()), fx[max(fx)]
        if not fa or not fz:
            return None
        a, z = a / fa, z / fz
    return z / a - 1


def weights() -> dict[str, float]:
    out = {}
    for part in os.getenv("SPUTNIK_PIE_WEIGHTS", "").replace(";", ",").split(","):
        symbol, _, weight = part.strip().partition(":")
        try:
            if symbol and float(weight.replace("%", "")) > 0:
                out[symbol.strip().upper()] = float(weight.replace("%", ""))
        except ValueError:
            continue
    return out


def start_date() -> date:
    try:
        return date.fromisoformat(os.getenv("SPUTNIK_PIE_START", "").strip())
    except ValueError:
        return date(2026, 11, 25)


def returns(fetcher: Callable | None = None) -> dict[str, float] | None:
    w = weights()
    if not w:
        return None
    total = sum(w.values())
    if fetcher is None:
        from sputnik_demo.data import fetch as fetcher
    try:
        fx = _closes(fetcher, "EURUSD=X")
        pie = 0.0
        for symbol, weight in w.items():
            change = _change(_closes(fetcher, symbol), None if symbol.endswith(EUR_SUFFIXES) else fx)
            if change is None:
                log.warning("Prezzi mancanti per %s", symbol)
                return None
            pie += weight / total * change
        out = {"Il tuo portafoglio": pie}
        for name, symbol in BENCHMARKS.items():
            change = _change(_closes(fetcher, symbol), None)
            if change is None:
                return None
            out[name] = change
        return out
    except Exception as exc:  # noqa: BLE001
        log.warning("Confronto portafoglio non disponibile: %s", exc)
        return None


def section(fetcher: Callable | None = None) -> list[str]:
    if not weights():
        return []
    r = returns(fetcher)
    if not r:
        return ["📈 Il tuo portafoglio contro gli ETF: prezzi non disponibili questa settimana"]
    pct = lambda x: f"{x:+.1%}".replace(".", ",")
    lines = [f"📈 Il tuo portafoglio contro gli ETF (dal {start_date():%d/%m/%Y}, prezzi in euro):"]
    lines += [f"• {name}: {pct(value)}" for name, value in r.items()]
    pie, sp = r["Il tuo portafoglio"], r["S&P 500 (VUAA)"]
    gap = pie - sp
    lines.append(f"   → {'avanti' if gap >= 0 else 'indietro'} di {abs(gap) * 100:.1f} punti rispetto all'S&P 500".replace(".", ","))
    return lines
