"""Sputnik DEMO trader — esegue i segnali LONG del bot CFD di Gagarin con ETF europei
sul conto Trading 212 Invest DEMO.

    python -m sputnik_demo.trader            # esecuzione normale (serve la chiave demo)
    python -m sputnik_demo.trader --dry-run  # mostra cosa farebbe, senza ordini

Regole:
* compra l'ETF quando il bot CFD dà LONG sullo strumento (stessa strategia, stessi dati);
* stop loss inserito su Trading 212 subito dopo l'acquisto;
* vende al take profit (controllo ogni 15 minuti), dopo 5 giorni di borsa o con segnale opposto;
* niente short e niente leva (il conto Invest non li consente).

Limiti di sicurezza: max 40 € per operazione, max 3 posizioni, stop di tutti i nuovi
acquisti se il conto scende sotto l'85% del valore iniziale; solo conto DEMO.
"""
from __future__ import annotations

import argparse
import json
import logging
import math
import os
from dataclasses import dataclass
from datetime import datetime, time as dtime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

from . import strategy
from .data import Bars, DataError, completed_daily, fetch

log = logging.getLogger("sputnik_demo")

STATE_FILE = Path(os.getenv("SPUTNIK_DEMO_STATE_FILE", "sputnik_demo_state.json"))
MAX_EUR_PER_TRADE = float(os.getenv("SPUTNIK_DEMO_MAX_EUR", "40"))
MAX_POSITIONS = int(os.getenv("SPUTNIK_DEMO_MAX_POSITIONS", "3"))
KILL_SWITCH = 0.85          # sotto l'85% del valore iniziale: niente nuovi acquisti
MIN_ORDER_EUR = 5.0
PENDING_MAX_AGE = timedelta(days=4)   # copre il weekend; la nuova candela giornaliera lo rivaluta comunque
MAX_CHASE_ATR = 1.0


@dataclass(frozen=True)
class Etf:
    key: str
    name: str
    underlying: str     # simbolo dei dati del segnale (come il bot CFD)
    yahoo: str          # prezzo dell'ETF
    isin: str
    currency: str       # valuta di quotazione su Trading 212
    exchange: str       # XETRA / LSE (orari di mercato)


ETFS: tuple[Etf, ...] = (
    Etf("oro", "Xetra-Gold", "GC=F", "4GLD.DE", "DE000A0S9GB0", "EUR", "XETRA"),
    Etf("sp500", "Vanguard S&P 500", "^GSPC", "VUAA.DE", "IE00BFMXXD54", "EUR", "XETRA"),
    Etf("nasdaq", "iShares Nasdaq 100", "^NDX", "SXRV.DE", "IE00B53SZB19", "EUR", "XETRA"),
    Etf("wti", "WisdomTree WTI Crude Oil", "CL=F", "CRUD.L", "GB00B15KXV33", "USD", "LSE"),
)
BY_KEY = {e.key: e for e in ETFS}

HOURS = {"XETRA": ("Europe/Berlin", dtime(9, 5), dtime(17, 25)),
         "LSE": ("Europe/London", dtime(8, 5), dtime(16, 25))}

FOOTER = "Conto DEMO Trading 212 — nessun denaro reale."


# ----------------------------------------------------------------------------- stato

def empty_state() -> dict:
    return {"positions": {}, "pending": {}, "closed": [], "last_eval": {}, "start_value": None,
            "halted": False, "tickers": {}, "outbox": []}


def load_state(path: Path = STATE_FILE) -> dict:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return empty_state()
    base = empty_state()
    base.update(data if isinstance(data, dict) else {})
    return base


def save_state(state: dict, path: Path = STATE_FILE) -> None:
    Path(path).write_text(json.dumps(state, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------- utilità

def market_open(etf: Etf, now: datetime) -> bool:
    tz, start, end = HOURS[etf.exchange]
    local = now.astimezone(ZoneInfo(tz))
    return local.weekday() < 5 and start <= local.time() <= end


def floor_qty(value: float, decimals: int) -> float:
    factor = 10 ** decimals
    return math.floor(value * factor) / factor


def eur(x: float) -> str:
    return f"{x:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def resolve_tickers(client, state: dict, now: datetime) -> dict[str, str]:
    """Trova il ticker Trading 212 di ogni ETF tramite ISIN (una volta al giorno)."""
    today = now.date().isoformat()
    cached = state.get("tickers") or {}
    if cached.get("_date") == today:
        return {k: v for k, v in cached.items() if not k.startswith("_")}
    found: dict[str, str] = {}
    try:
        rows = client.instruments()
    except Exception as exc:  # noqa: BLE001
        log.warning("Catalogo Trading 212 non disponibile: %s", exc)
        return {k: v for k, v in cached.items() if not k.startswith("_")}
    for etf in ETFS:
        matches = [r for r in rows if str(r.get("isin", "")).upper() == etf.isin]
        matches.sort(key=lambda r: (r.get("currencyCode") != etf.currency, len(str(r.get("ticker", "")))))
        if matches:
            found[etf.key] = matches[0]["ticker"]
            log.info("%s → %s (%s)", etf.name, matches[0]["ticker"], matches[0].get("currencyCode"))
        else:
            log.warning("%s (ISIN %s) non presente nel catalogo del conto demo: escluso", etf.name, etf.isin)
    state["tickers"] = {"_date": today, **found}
    return found


# ----------------------------------------------------------------------------- ciclo

def run(client, now: datetime | None = None, fetcher: Callable[..., Bars] = fetch,
        send: Callable[[str], bool] = lambda t: False, st: dict | None = None,
        dry_run: bool = False) -> dict:
    now = now or datetime.now(timezone.utc)
    st = st if st is not None else load_state()
    out: list[str] = []

    cash = client.cash()
    total = float(cash.get("total") or 0)
    free = float(cash.get("free") or 0)
    if not st.get("start_value"):
        st["start_value"] = total
    if not st.get("halted") and st["start_value"] and total < KILL_SWITCH * st["start_value"]:
        st["halted"] = True
        out.append(f"🛑 SPUTNIK DEMO — conto a {eur(total)} (sotto l'85% di {eur(st['start_value'])}): "
                   f"nuovi acquisti sospesi. Le posizioni aperte restano protette dai loro stop.\n{FOOTER}")

    tickers = resolve_tickers(client, st, now)
    portfolio = {p.get("ticker"): p for p in client.portfolio()}
    try:
        fx = fetcher("EURUSD=X", range_="5d", interval="1d").last_price or 1.0
    except DataError:
        fx = None

    # 1) posizioni aperte: stop scattato, take profit, scadenza, segnale opposto
    for key, pos in list(st["positions"].items()):
        etf = BY_KEY[key]
        held = portfolio.get(pos["ticker"])
        if held is None:
            _close(st, key, pos, pos["stop"], "stop", now, out)
            continue
        price = float(held.get("currentPrice") or 0)
        reason = None
        if price and price >= pos["target"]:
            reason = "target"
        elif price and price <= pos["stop"]:
            reason = "stop"
        else:
            try:
                bars = completed_daily(fetcher(etf.underlying, range_="2y", interval="1d"), now)
                opened = datetime.fromisoformat(pos["opened_at"]).date()
                if sum(1 for t in bars.time if t.date() > opened) >= strategy.MAX_DAYS:
                    reason = "tempo"
                else:
                    setup = strategy.evaluate(bars)
                    if setup and setup.direction == "SHORT":
                        reason = "opposto"
            except DataError:
                pass
        if reason and market_open(etf, now):
            if dry_run:
                out.append(f"[prova] venderei {etf.name}: {reason}")
                continue
            if pos.get("stop_order_id"):
                try:
                    client.cancel(pos["stop_order_id"])
                except Exception as exc:  # noqa: BLE001
                    log.warning("Annullamento stop %s: %s", etf.name, exc)
            qty = float(held.get("quantity") or pos["quantity"])
            try:
                client.market(pos["ticker"], -qty)
            except Exception as exc:  # noqa: BLE001
                out.append(f"⚠️ SPUTNIK DEMO — vendita di {etf.name} non riuscita ({exc}). Riprovo al prossimo giro.")
                continue
            _close(st, key, pos, price, reason, now, out)

    # 2) nuovi segnali sulle barre giornaliere chiuse dello strumento di riferimento
    for etf in ETFS:
        if etf.key in st["positions"] or etf.key not in tickers:
            continue
        try:
            daily = fetcher(etf.underlying, range_="2y", interval="1d")
        except DataError:
            continue
        bars = completed_daily(daily, now)
        bar_id = bars.time[-1].strftime("%Y-%m-%d") if len(bars) else ""
        if st["last_eval"].get(etf.key) == bar_id:
            continue
        st["last_eval"][etf.key] = bar_id
        setup = strategy.evaluate(bars)
        if setup and setup.direction == "LONG":
            st["pending"][etf.key] = {
                "created": now.isoformat(), "reference": setup.reference, "atr": setup.atr,
                "stop_pct": strategy.STOP_ATR * setup.atr / setup.reference,
                "target_pct": strategy.TARGET_ATR * setup.atr / setup.reference,
                "reasons": setup.reasons, "bar": bar_id,
            }
        else:
            st["pending"].pop(etf.key, None)

    # 3) esecuzione degli acquisti in attesa
    for key, sig in list(st["pending"].items()):
        etf = BY_KEY[key]
        if now - datetime.fromisoformat(sig["created"]) > PENDING_MAX_AGE:
            st["pending"].pop(key)
            continue
        if st.get("halted") or len(st["positions"]) >= MAX_POSITIONS or key not in tickers:
            continue
        if not market_open(etf, now):
            continue
        if tickers[key] in portfolio:
            st["pending"].pop(key)
            log.warning("%s già in portafoglio senza essere registrato: nessun nuovo acquisto", etf.name)
            continue
        try:
            under = fetcher(etf.underlying, range_="5d", interval="1d").last_price
            etf_price = fetcher(etf.yahoo, range_="5d", interval="1d").last_price
        except DataError:
            continue
        if not under or not etf_price:
            continue
        if under - sig["reference"] > MAX_CHASE_ATR * sig["atr"]:
            st["pending"].pop(key)
            out.append(f"⏭️ SPUTNIK DEMO — {etf.name}: segnale saltato, il prezzo è già salito troppo.")
            continue
        budget_eur = min(MAX_EUR_PER_TRADE, free)
        if budget_eur < MIN_ORDER_EUR:
            continue
        budget_ccy = budget_eur * (fx if etf.currency == "USD" and fx else 1.0)
        if dry_run:
            out.append(f"[prova] comprerei {etf.name} per {eur(budget_eur)} (stop −{sig['stop_pct']:.1%}, "
                       f"target +{sig['target_pct']:.1%})")
            st["pending"].pop(key)
            continue
        order, qty = None, 0.0
        for decimals in (3, 1, 0):
            qty = floor_qty(budget_ccy / etf_price, decimals)
            if qty <= 0:
                continue
            try:
                order = client.market(tickers[key], qty)
                break
            except Exception as exc:  # noqa: BLE001
                log.warning("Acquisto %s con %d decimali rifiutato: %s", etf.name, decimals, exc)
        st["pending"].pop(key)
        if order is None:
            out.append(f"⚠️ SPUTNIK DEMO — acquisto di {etf.name} non riuscito (quantità o mercato non disponibili).")
            continue
        fill = etf_price
        try:
            held = {p.get("ticker"): p for p in client.portfolio()}.get(tickers[key])
            if held:
                fill = float(held.get("averagePrice") or etf_price)
                qty = float(held.get("quantity") or qty)
        except Exception:  # noqa: BLE001
            pass
        stop_price = round(fill * (1 - sig["stop_pct"]), 2)
        target_price = round(fill * (1 + sig["target_pct"]), 2)
        stop_id = None
        try:
            stop_order = client.stop(tickers[key], -qty, stop_price)
            stop_id = stop_order.get("id")
        except Exception as exc:  # noqa: BLE001
            log.warning("Stop %s non inserito: %s (verrà gestito dal bot)", etf.name, exc)
        st["positions"][key] = {
            "ticker": tickers[key], "quantity": qty, "entry": fill, "stop": stop_price, "target": target_price,
            "stop_order_id": stop_id, "opened_at": now.isoformat(), "spent_eur": round(budget_eur, 2),
            "reasons": sig["reasons"],
        }
        free -= budget_eur
        out.append("\n".join([
            f"🤖 SPUTNIK DEMO — 🟢 comprato {etf.name}",
            f"{qty:g} quote a {fill:,.2f} {etf.currency} · circa {eur(budget_eur)}",
            f"Stop {stop_price:,.2f} (−{sig['stop_pct']:.1%}) {'inserito su Trading 212' if stop_id else 'gestito dal bot'}"
            f" · Target {target_price:,.2f} (+{sig['target_pct']:.1%})",
            "Perché: " + "; ".join(sig["reasons"]),
            FOOTER,
        ]))

    queue = list(st.get("outbox") or []) + out
    st["outbox"] = []
    for text in queue:
        if dry_run:
            print("\n" + text)
        elif not send(text):
            st["outbox"].append(text)
    st["outbox"] = st["outbox"][-20:]
    return st


def _close(st: dict, key: str, pos: dict, price: float, reason: str, now: datetime, out: list[str]) -> None:
    etf = BY_KEY[key]
    pnl_pct = price / pos["entry"] - 1 if pos["entry"] else 0.0
    pnl_eur = pos.get("spent_eur", 0) * pnl_pct
    st["positions"].pop(key, None)
    st["closed"].append({**pos, "key": key, "exit": price, "reason": reason, "closed_at": now.isoformat(),
                         "pnl_pct": round(pnl_pct, 4), "pnl_eur": round(pnl_eur, 2)})
    label = {"target": "✅ take profit", "stop": "❌ stop loss", "tempo": "⏱️ scaduti 5 giorni",
             "opposto": "🔄 segnale opposto"}[reason]
    total = sum(c.get("pnl_eur", 0) for c in st["closed"])
    wins = sum(1 for c in st["closed"] if c.get("pnl_eur", 0) > 0)
    out.append("\n".join([
        f"🤖 SPUTNIK DEMO — venduto {etf.name} ({label})",
        f"Ingresso {pos['entry']:,.2f} → uscita {price:,.2f} · {pnl_pct:+.1%} ≈ {pnl_eur:+.2f} €",
        f"Storico demo: {len(st['closed'])} operazioni · vincenti {wins} · totale {total:+.2f} €",
        FOOTER,
    ]))


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if os.getenv("SPUTNIK_DEMO_TRADING", "1").strip().lower() in {"0", "false", "no"}:
        print("SPUTNIK DEMO: trading disattivato (SPUTNIK_DEMO_TRADING=0).")
        return 0
    key = os.getenv("SPUTNIK_INVEST_DEMO_API_KEY", "").strip()
    secret = os.getenv("SPUTNIK_INVEST_DEMO_API_SECRET", "").strip()
    if not key or not secret:
        print("SPUTNIK DEMO: chiavi demo assenti, nessuna operazione.")
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
        # run() aggiorna lo stato man mano: lo salviamo anche se il giro si interrompe a metà,
        # così un ordine già eseguito non viene mai ripetuto.
        if not args.dry_run:
            save_state(state)
    log.info("Posizioni aperte: %d · in attesa: %d · chiuse: %d",
             len(state["positions"]), len(state["pending"]), len(state["closed"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
