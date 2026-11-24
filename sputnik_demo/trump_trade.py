"""Acquisto automatico sulle "chiamate al mercato" di Trump — SOLO conto DEMO Trading 212.

    python -m sputnik_demo.trump_trade            # esegue
    python -m sputnik_demo.trump_trade --dry-run  # mostra cosa farebbe

Quando Trump scrive un invito esplicito a comprare (es. "GREAT TIME TO BUY", vedi
sputnik_market_call), Sputnik compra un ETF sull'S&P 500 sul conto demo:

* legge i post delle ultime 18 ore da sputnik_context.json (scritto dalla corsia veloce);
* se la borsa è chiusa (notte, weekend) compra alla riapertura, ma salta l'acquisto se
  il future sull'S&P 500 è già salito di oltre il 3% dal momento del post (movimento già fatto);
* importo fisso (SPUTNIK_TRUMP_TRADE_EUR, predefinito 10 €), stop −3% inserito su
  Trading 212, uscita a +6% o dopo 3 giorni di borsa;
* gli inviti a vendere restano solo un avviso: sul conto Invest non si può vendere allo scoperto.

ETF diverso da quelli del trader a 5 giorni e del PAC, così le gestioni non si mescolano.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

import sputnik_market_call

from .data import DataError, fetch
from .trader import Etf, eur, floor_qty, load_state, market_open, save_state

log = logging.getLogger("sputnik.trump_trade")

ETF = Etf("trump_sp500", "iShares Core S&P 500", "^GSPC", "SXR8.DE", "IE00B5BMR087", "EUR", "XETRA")
CONTEXT_FILE = Path(os.getenv("SPUTNIK_CONTEXT_FILE", "sputnik_context.json"))
MAX_POST_AGE = timedelta(hours=18)
MAX_RUN_UP = 0.03       # l'S&P 500 è già salito di oltre il 3% dal post: movimento perso, niente acquisto
STOP_PCT = 0.03
TARGET_PCT = 0.06
MAX_DAYS = 3
FOOTER = "Conto DEMO Trading 212 — nessun denaro reale."
EXIT_LABELS = {"stop": "stop", "target": "obiettivo raggiunto", "tempo": "3 giorni di borsa"}
FUTURES = "ES=F"        # future sull'S&P 500: si muove anche di notte, quando le borse sono chiuse
BERLIN = ZoneInfo("Europe/Berlin")


def amount() -> float:
    try:
        return max(float(os.getenv("SPUTNIK_TRUMP_TRADE_EUR", "").replace(",", ".") or 10), 0.0)
    except ValueError:
        return 10.0


def _time(value: str) -> datetime | None:
    try:
        t = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def next_open(t: datetime) -> datetime:
    """Prima apertura di Xetra dopo il momento t (i post notturni o del weekend si comprano all'apertura)."""
    local = t.astimezone(BERLIN)
    day = local.date()
    if local.weekday() < 5 and local.time() < time(9, 5):
        return datetime.combine(day, time(9, 5), BERLIN)
    day += timedelta(days=1)
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return datetime.combine(day, time(9, 5), BERLIN)


def still_valid(t: datetime, now: datetime) -> bool:
    return timedelta(0) <= now - t and now <= max(t + MAX_POST_AGE, next_open(t) + timedelta(hours=3))


def market_calls(context: dict, now: datetime) -> list[dict]:
    """Inviti al rialzo ancora validi (ultime 18 ore, o fino alla riapertura dopo notte e weekend)."""
    calls = []
    for item in context.get("trump") or []:
        found = sputnik_market_call.detect(item.get("title", ""))
        t = _time(item.get("published", ""))
        if found and found[0] == "RIALZO" and t and still_valid(t, now):
            calls.append({**item, "phrase": found[1], "at": t})
    return sorted(calls, key=lambda c: c["at"])


def price_at(bars, t: datetime) -> float | None:
    """Ultimo prezzo orario disponibile prima del post."""
    before = [c for ts, c in zip(bars.time, bars.close) if ts <= t and c]
    return before[-1] if before else None


def _trading_days_since(start: datetime, now: datetime) -> int:
    days, d = 0, start.date()
    while d < now.date():
        d += timedelta(days=1)
        if d.weekday() < 5:
            days += 1
    return days


def run(client, now: datetime | None = None, fetcher: Callable = fetch, send: Callable[[str], bool] = lambda t: False,
        st: dict | None = None, context: dict | None = None, dry_run: bool = False) -> dict:
    now = now or datetime.now(timezone.utc)
    st = st if st is not None else load_state()
    tt = st.setdefault("trump_trades", {"seen": [], "open": None, "closed": []})
    out: list[str] = []
    if not market_open(ETF, now):
        return st

    ticker = tt.get("ticker")
    if not ticker:
        matches = [r for r in client.instruments() if str(r.get("isin", "")).upper() == ETF.isin]
        matches.sort(key=lambda r: (r.get("currencyCode") != ETF.currency, len(str(r.get("ticker", "")))))
        if not matches:
            log.warning("%s non presente nel catalogo demo", ETF.name)
            return st
        ticker = tt["ticker"] = matches[0]["ticker"]

    # 1) posizione aperta: target, stop o scadenza
    pos = tt.get("open")
    if pos:
        held = {p.get("ticker"): p for p in client.portfolio()}.get(ticker)
        price = float(held.get("currentPrice") or 0) if held else 0.0
        reason = ("stop" if not held else "target" if price >= pos["target"]
                  else "tempo" if _trading_days_since(datetime.fromisoformat(pos["opened_at"]), now) >= MAX_DAYS
                  else None)
        if reason:
            exit_price = pos["stop"] if reason == "stop" else price
            if held and not dry_run:
                if pos.get("stop_order_id"):
                    try:
                        client.cancel(pos["stop_order_id"])
                    except Exception as exc:  # noqa: BLE001
                        log.warning("Annullamento stop: %s", exc)
                client.market(ticker, -float(held.get("quantity") or pos["quantity"]))
            result = (exit_price / pos["entry"] - 1)
            tt["closed"] = (tt.get("closed") or [])[-49:] + [{**pos, "exit": exit_price, "reason": reason,
                                                               "result_pct": round(result * 100, 2),
                                                               "closed_at": now.isoformat()}]
            tt["open"] = None
            out.append("\n".join([
                f"🤖 SPUTNIK DEMO — chiuso il trade Trump ({EXIT_LABELS[reason]})",
                f"{ETF.name}: {pos['entry']:,.2f} → {exit_price:,.2f} € · {result:+.1%}",
                FOOTER]))

    # 2) nuove chiamate al rialzo
    if not tt.get("open"):
        context = context if context is not None else _load_context()
        for call in market_calls(context, now):
            key = call.get("url") or call["title"]
            if key in tt["seen"]:
                continue
            tt["seen"] = (tt["seen"] + [key])[-100:]
            try:
                hourly = fetcher(FUTURES, range_="5d", interval="1h")
                then, current = price_at(hourly, call["at"]), hourly.last_price
            except DataError:
                then = current = None
            if then and current and current / then - 1 > MAX_RUN_UP:
                out.append(f"⏭️ SPUTNIK DEMO — trade Trump saltato: l'S&P 500 è già salito del "
                           f"{current / then - 1:.1%} dal post «{call['phrase']}».\n{FOOTER}")
                continue
            try:
                etf_price = fetcher(ETF.yahoo, range_="5d", interval="1d").last_price
            except DataError:
                etf_price = None
            budget = min(amount(), float(client.cash().get("free") or 0))
            if not etf_price or budget < 5:
                continue
            qty = 0.0
            if dry_run:
                out.append(f"[prova] comprerei {ETF.name} per {eur(budget)} dopo «{call['phrase']}»")
                break
            for decimals in (4, 3, 1, 0):
                q = floor_qty(budget / etf_price, decimals)
                if q <= 0:
                    continue
                try:
                    client.market(ticker, q)
                    qty = q
                    break
                except Exception as exc:  # noqa: BLE001
                    log.warning("Acquisto con %d decimali rifiutato: %s", decimals, exc)
            if not qty:
                out.append(f"⚠️ SPUTNIK DEMO — acquisto dopo il post di Trump non riuscito.\n{FOOTER}")
                break
            stop, target = round(etf_price * (1 - STOP_PCT), 2), round(etf_price * (1 + TARGET_PCT), 2)
            stop_id = None
            try:
                stop_id = client.stop(ticker, -qty, stop).get("id")
            except Exception as exc:  # noqa: BLE001
                log.warning("Stop non inserito: %s (lo gestisce il bot)", exc)
            tt["open"] = {"quantity": qty, "entry": etf_price, "stop": stop, "target": target,
                          "stop_order_id": stop_id, "opened_at": now.isoformat(), "post": call["title"][:200]}
            out.append("\n".join([
                "🤖 SPUTNIK DEMO — ⚡ comprato dopo il post di Trump",
                f"📰 «{call['phrase']}» ({call['at'].astimezone(sputnik_market_call.ROME):%H:%M del %d/%m})",
                f"🟢 {ETF.name}: {qty:g} quote a {etf_price:,.2f} € · circa {eur(qty * etf_price)}",
                f"Stop {stop:,.2f} (−3%) · Obiettivo {target:,.2f} (+6%) · uscita entro 3 giorni di borsa",
                FOOTER]))
            break

    for text in out:
        if dry_run:
            print(text)
        elif not send(text):
            log.warning("Messaggio non inviato")
    return st


def _load_context() -> dict:
    try:
        return json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if os.getenv("SPUTNIK_TRUMP_TRADE", "1").strip().lower() in {"0", "false", "no"}:
        print("SPUTNIK TRADE TRUMP: disattivato (SPUTNIK_TRUMP_TRADE=0).")
        return 0
    key = os.getenv("SPUTNIK_INVEST_DEMO_API_KEY", "").strip()
    secret = os.getenv("SPUTNIK_INVEST_DEMO_API_SECRET", "").strip()
    if not key or not secret:
        print("SPUTNIK TRADE TRUMP: chiavi demo assenti, nessuna operazione.")
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
