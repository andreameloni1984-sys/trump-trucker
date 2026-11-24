"""Piano di accumulo (PAC) con ribilanciamento — SOLO conto DEMO Trading 212 Invest.

    python -m sputnik_demo.pac            # esegue il PAC del mese se non è già stato fatto
    python -m sputnik_demo.pac --dry-run  # mostra cosa farebbe, senza ordini

* Una volta al mese (il primo giorno di borsa utile, in orario Xetra) investe la cifra
  mensile (variabile SPUTNIK_PAC_MONTHLY, predefinita 20 €) con i pesi obiettivo
  80% ETF azionario mondiale · 10% oro fisico · 10% bitcoin fisico.
* I soldi nuovi vanno prima alle parti sotto peso, così il portafoglio si riequilibra
  senza vendere. Se una parte si allontana dall'obiettivo di oltre 5 punti, il bot
  vende l'eccesso e compra ciò che manca (ribilanciamento).
* Usa strumenti diversi da quelli del trader a 5 giorni (niente 4GLD), così le due
  gestioni non si mescolano nello stesso conto demo.
"""
from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from .data import DataError, fetch
from .trader import eur, floor_qty, load_state, market_open, save_state, Etf

log = logging.getLogger("sputnik.pac")

DEFAULT_MONTHLY = 20.0      # conto demo da 200 EUR: importi piccoli
DRIFT_LIMIT = 0.05          # 5 punti percentuali dall'obiettivo → ribilanciamento
MIN_ORDER_EUR = 1.0
FOOTER = "PAC sul conto DEMO Trading 212 — nessun denaro reale."


@dataclass(frozen=True)
class Sleeve:
    key: str
    label: str
    weight: float
    options: tuple[Etf, ...]   # in ordine di preferenza: il primo presente nel catalogo demo


SLEEVES: tuple[Sleeve, ...] = (
    Sleeve("mondo", "Azioni mondo", 0.80, (
        Etf("mondo", "Vanguard FTSE All-World", "", "VWCE.DE", "IE00BK5BQT80", "EUR", "XETRA"),
        Etf("mondo", "iShares Core MSCI World", "", "EUNL.DE", "IE00B4L5Y983", "EUR", "XETRA"),
    )),
    Sleeve("oro", "Oro fisico", 0.10, (
        Etf("oro", "Invesco Physical Gold", "", "8PSG.DE", "IE00B579F325", "EUR", "XETRA"),
        Etf("oro", "iShares Physical Gold", "", "PPFB.DE", "IE00B4ND3602", "EUR", "XETRA"),
    )),
    Sleeve("bitcoin", "Bitcoin fisico", 0.10, (
        Etf("bitcoin", "ETC Group Physical Bitcoin", "", "BTCE.DE", "DE000A27Z304", "EUR", "XETRA"),
    )),
)


def monthly_amount() -> float:
    try:
        value = float(os.getenv("SPUTNIK_PAC_MONTHLY", "").replace(",", ".") or DEFAULT_MONTHLY)
    except ValueError:
        value = DEFAULT_MONTHLY
    return max(value, 0.0)


def resolve(client, pac: dict, now: datetime) -> tuple[dict[str, tuple[Etf, str]], list[str]]:
    """Strumento scelto per ogni parte: (Etf, ticker Trading 212). Catalogo letto una volta al giorno."""
    today = now.date().isoformat()
    cached = pac.get("instruments") or {}
    if cached.get("_date") == today:
        chosen = {}
        for sleeve in SLEEVES:
            if sleeve.key in cached:
                etf = next((e for e in sleeve.options if e.isin == cached[sleeve.key]["isin"]), None)
                if etf:
                    chosen[sleeve.key] = (etf, cached[sleeve.key]["ticker"])
        return chosen, list(cached.get("_missing", []))
    rows = client.instruments()
    by_isin: dict[str, list[dict]] = {}
    for r in rows:
        by_isin.setdefault(str(r.get("isin", "")).upper(), []).append(r)
    chosen, missing = {}, []
    for sleeve in SLEEVES:
        for etf in sleeve.options:
            matches = sorted(by_isin.get(etf.isin, []),
                             key=lambda r: (r.get("currencyCode") != etf.currency, len(str(r.get("ticker", "")))))
            if matches:
                chosen[sleeve.key] = (etf, matches[0]["ticker"])
                break
        else:
            missing.append(sleeve.key)
    pac["instruments"] = {"_date": today, "_missing": missing,
                          **{k: {"isin": e.isin, "ticker": t} for k, (e, t) in chosen.items()}}
    return chosen, missing


def targets(available: list[str]) -> dict[str, float]:
    """Pesi obiettivo; la quota di una parte non disponibile va all'ETF mondo."""
    w = {s.key: s.weight for s in SLEEVES if s.key in available}
    lost = sum(s.weight for s in SLEEVES if s.key not in available)
    if "mondo" in w:
        w["mondo"] += lost
    total = sum(w.values()) or 1.0
    return {k: v / total for k, v in w.items()}


def plan(values: dict[str, float], weights: dict[str, float], new_money: float) -> tuple[dict[str, float], bool]:
    """Euro da comprare (+) o vendere (−) per parte, e se è un ribilanciamento con vendite."""
    current = sum(values.values())
    after = current + new_money
    drift = current > 0 and any(abs(values.get(k, 0) / current - w) > DRIFT_LIMIT for k, w in weights.items())
    if drift:
        return {k: after * w - values.get(k, 0) for k, w in weights.items()}, True
    gaps = {k: max(after * w - values.get(k, 0), 0.0) for k, w in weights.items()}
    total_gap = sum(gaps.values())
    if total_gap <= 0:
        return {k: new_money * w for k, w in weights.items()}, False
    return {k: new_money * g / total_gap for k, g in gaps.items()}, False


def _order(client, ticker: str, euros: float, price: float) -> float:
    """Ordine a mercato per circa `euros` (negativo = vendita). Restituisce la quantità eseguita."""
    sign = 1 if euros > 0 else -1
    for decimals in (4, 3, 1, 0):
        qty = floor_qty(abs(euros) / price, decimals)
        if qty <= 0:
            continue
        try:
            client.market(ticker, sign * qty)
            return sign * qty
        except Exception as exc:  # noqa: BLE001
            log.warning("Ordine %s con %d decimali rifiutato: %s", ticker, decimals, exc)
    return 0.0


def run(client, now: datetime | None = None, fetcher: Callable = fetch, send: Callable[[str], bool] = lambda t: False,
        st: dict | None = None, dry_run: bool = False, force: bool = False) -> dict:
    now = now or datetime.now(timezone.utc)
    st = st if st is not None else load_state()
    pac = st.setdefault("pac", {"months": [], "invested": 0.0})
    month = now.strftime("%Y-%m")
    if not force and month in pac.get("months", []):
        log.info("PAC di %s già eseguito", month)
        return st
    chosen, missing = resolve(client, pac, now)
    if not chosen:
        log.warning("Nessuno strumento del PAC nel catalogo demo")
        return st
    if not all(market_open(etf, now) for etf, _ in chosen.values()):
        log.info("Xetra chiusa: PAC rimandato")
        return st

    held = {p.get("ticker"): p for p in client.portfolio()}
    prices, values = {}, {}
    for key, (etf, ticker) in chosen.items():
        h = held.get(ticker)
        price = float(h.get("currentPrice") or 0) if h else 0.0
        if not price:
            try:
                price = fetcher(etf.yahoo, range_="5d", interval="1d").last_price or 0.0
            except DataError:
                price = 0.0
        if not price:
            log.warning("Prezzo di %s non disponibile: PAC rimandato", etf.name)
            return st
        prices[key] = price
        values[key] = float(h.get("quantity") or 0) * price if h else 0.0

    weights = targets(list(chosen))
    free = float(client.cash().get("free") or 0)
    money = min(monthly_amount(), free)
    orders, rebalance = plan(values, weights, money)

    lines = [f"🥧 SPUTNIK PAC DEMO — {'ribilanciamento e ' if rebalance else ''}acquisto di {now:%m/%Y}", ""]
    if missing:
        lines.append("ℹ️ Non presente nel catalogo demo: " + ", ".join(
            s.label for s in SLEEVES if s.key in missing) + " (quota spostata sull'ETF mondo)")
    done = {}
    # prima le vendite (liberano liquidità), poi gli acquisti
    for key, euros in sorted(orders.items(), key=lambda kv: kv[1]):
        etf, ticker = chosen[key]
        if abs(euros) < MIN_ORDER_EUR:
            continue
        if dry_run:
            done[key] = euros / prices[key]
            lines.append(f"[prova] {'compro' if euros > 0 else 'vendo'} {etf.name} per {eur(abs(euros))}")
            continue
        qty = _order(client, ticker, euros, prices[key])
        if qty == 0:
            lines.append(f"⚠️ {etf.name}: ordine non riuscito")
            continue
        done[key] = qty
        lines.append(f"{'🟢 comprato' if qty > 0 else '🔴 venduto'} {etf.name}: {abs(qty):g} quote "
                     f"a {prices[key]:,.2f} € · circa {eur(abs(qty) * prices[key])}")

    new_values = {k: values.get(k, 0) + done.get(k, 0) * prices[k] for k in chosen}
    total = sum(new_values.values())
    if total:
        lines += ["", "Pesi dopo l'operazione (obiettivo):"]
        lines += [f"• {next(s.label for s in SLEEVES if s.key == k)}: {new_values[k] / total:.0%} ({weights[k]:.0%})"
                  for k in chosen]
    bought = sum(q * prices[k] for k, q in done.items() if q > 0) - sum(-q * prices[k] for k, q in done.items() if q < 0)
    if not dry_run and done:
        pac["invested"] = round(float(pac.get("invested", 0)) + max(bought, 0), 2)
        if month not in pac.setdefault("months", []):
            pac["months"].append(month)
        pac["months"] = pac["months"][-36:]
        lines += ["", f"Valore PAC: {eur(total)} · versati in totale: {eur(pac['invested'])}"]
    lines.append(FOOTER)
    text = "\n".join(lines)
    if dry_run:
        print(text)
    elif done:
        if not send(text):
            log.warning("Messaggio PAC non inviato")
    return st


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if os.getenv("SPUTNIK_PAC", "1").strip().lower() in {"0", "false", "no"}:
        print("SPUTNIK PAC: disattivato (SPUTNIK_PAC=0).")
        return 0
    key = os.getenv("SPUTNIK_INVEST_DEMO_API_KEY", "").strip()
    secret = os.getenv("SPUTNIK_INVEST_DEMO_API_SECRET", "").strip()
    if not key or not secret:
        print("SPUTNIK PAC: chiavi demo assenti, nessuna operazione.")
        return 0
    from .t212 import DemoClient

    def send(text: str) -> bool:
        if not (os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID")):
            print(text)
            return True
        from trump_tracker import send_telegram
        return send_telegram(text)

    state = load_state()
    try:
        run(DemoClient(key, secret), send=send, st=state, dry_run=args.dry_run)
    finally:
        if not args.dry_run:
            save_state(state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
