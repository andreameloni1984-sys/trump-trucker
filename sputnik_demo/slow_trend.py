"""Trend lento con ETF — SOLO conto DEMO Trading 212 Invest.

    python -m sputnik_demo.slow_trend            # esegue il controllo del mese se non è già fatto
    python -m sputnik_demo.slow_trend --dry-run  # mostra cosa farebbe

Una volta al mese (primo giorno di borsa utile, orario Xetra) guarda la chiusura di fine mese
di oro, S&P 500 e Nasdaq 100 e la confronta con quella di 3, 6 e 12 mesi prima:
* se è più alta in almeno 2 confronti su 3 → tiene l'ETF (lo compra se non c'è);
* altrimenti → vende l'ETF e resta liquido.

Studio (S&P 500 1927-2026): stesso rendimento del compra e tieni ma peggior crollo −51%
invece di −86%; circa 1-2 cambi l'anno. Prende il posto del trader "a 5 giorni", che
replicava i segnali di Gagarin. Importo fisso per ETF: SPUTNIK_TREND_EUR (predefinito 30 €, conto demo da 200 €).
"""
from __future__ import annotations

import argparse
import logging
import os
from datetime import datetime, timezone
from typing import Callable

from .data import DataError, fetch
from .trader import Etf, eur, floor_qty, load_state, market_open, save_state

log = logging.getLogger("sputnik.slow_trend")

ASSETS: tuple[Etf, ...] = (
    Etf("oro", "Xetra-Gold", "GC=F", "4GLD.DE", "DE000A0S9GB0", "EUR", "XETRA"),
    Etf("sp500", "Vanguard S&P 500", "^GSPC", "VUAA.DE", "IE00BFMXXD54", "EUR", "XETRA"),
    Etf("nasdaq", "iShares Nasdaq 100", "^NDX", "SXRV.DE", "IE00B53SZB19", "EUR", "XETRA"),
)
LOOKBACKS = (3, 6, 12)   # mesi
FOOTER = "Trend lento sul conto DEMO Trading 212 — nessun denaro reale."


def budget() -> float:
    try:
        return max(float(os.getenv("SPUTNIK_TREND_EUR", "").replace(",", ".") or 30), 0.0)
    except ValueError:
        return 30.0


def month_ends(bars, before: datetime) -> list[float]:
    """Chiusure dell'ultimo giorno di ogni mese, escluso il mese in corso."""
    current = (before.year, before.month)
    out: dict[tuple[int, int], float] = {}
    for t, c in zip(bars.time, bars.close):
        if c and (t.year, t.month) < current:
            out[(t.year, t.month)] = c
    return [out[k] for k in sorted(out)]


def signal(closes: list[float]) -> tuple[bool, list[str]] | None:
    """True = in trend (investito). Serve almeno un anno di chiusure mensili."""
    if len(closes) <= max(LOOKBACKS):
        return None
    last = closes[-1]
    votes, detail = 0, []
    for m in LOOKBACKS:
        chg = last / closes[-1 - m] - 1
        votes += chg > 0
        detail.append(f"{m} mesi {chg:+.1%}")
    return votes >= 2, detail


def resolve(client, st: dict) -> dict[str, str]:
    cached = st.get("tickers_trend")
    if cached:
        return cached
    rows = client.instruments()
    found = {}
    for a in ASSETS:
        matches = sorted([r for r in rows if str(r.get("isin", "")).upper() == a.isin],
                         key=lambda r: (r.get("currencyCode") != a.currency, len(str(r.get("ticker", "")))))
        if matches:
            found[a.key] = matches[0]["ticker"]
    st["tickers_trend"] = found
    return found


def trim(client, st: dict, now: datetime, send: Callable[[str], bool], dry_run: bool) -> None:
    """Una volta al giorno: riporta all'importo previsto le posizioni del trend oltre 2 volte l'importo
    (es. dopo un abbassamento di SPUTNIK_TREND_EUR), per liberare liquidità alle altre gestioni demo."""
    tr = st["trend"]
    today = now.date().isoformat()
    if tr.get("trim_date") == today or not tr.get("holdings"):
        return
    tr["trim_date"] = today
    tickers = resolve(client, st)
    held = {p.get("ticker"): p for p in client.portfolio()}
    lines = []
    for a in ASSETS:
        pos = held.get(tickers.get(a.key, ""))
        if a.key not in tr["holdings"] or not pos:
            continue
        qty, price = float(pos.get("quantity") or 0), float(pos.get("currentPrice") or 0)
        if not price or qty * price <= 2 * budget():
            continue
        sell = floor_qty((qty * price - budget()) / price, 1)
        if sell <= 0:
            continue
        if not dry_run:
            try:
                client.market(tickers[a.key], -sell)
            except Exception as exc:  # noqa: BLE001
                log.warning("Riduzione %s non riuscita: %s", a.name, exc)
                continue
        lines.append(f"• {a.name}: venduto {sell:g} quote (circa {eur(sell * price)}), "
                     f"resta circa {eur((qty - sell) * price)}")
    if lines:
        text = "\n".join(["✂️ SPUTNIK TREND LENTO — posizioni riportate all'importo previsto "
                          f"({eur(budget())} per ETF) per liberare liquidità", "", *lines, "", FOOTER])
        if dry_run:
            print(text)
        elif not send(text):
            log.warning("Messaggio riduzione non inviato")


def run(client, now: datetime | None = None, fetcher: Callable = fetch, send: Callable[[str], bool] = lambda t: False,
        st: dict | None = None, dry_run: bool = False) -> dict:
    now = now or datetime.now(timezone.utc)
    st = st if st is not None else load_state()
    tr = st.setdefault("trend", {"months": [], "holdings": {}, "history": []})
    month = now.strftime("%Y-%m")
    if not all(market_open(a, now) for a in ASSETS):
        return st
    trim(client, st, now, send, dry_run)
    if month in tr["months"]:
        return st
    tickers = resolve(client, st)
    held = {p.get("ticker"): p for p in client.portfolio()}
    lines, changes = [f"📈 SPUTNIK TREND LENTO — controllo di {now:%m/%Y}", ""], 0
    for a in ASSETS:
        if a.key not in tickers:
            lines.append(f"• {a.name}: non presente nel catalogo demo")
            continue
        try:
            sig = signal(month_ends(fetcher(a.underlying, range_="2y", interval="1d"), now))
        except DataError:
            sig = None
        if sig is None:
            log.warning("Dati insufficienti per %s: controllo rimandato", a.name)
            return st
        long_, detail = sig
        ticker = tickers[a.key]
        pos = held.get(ticker)
        qty = float(pos.get("quantity") or 0) if pos else 0.0
        state = "🟢 in trend" if long_ else "🔴 fuori trend"
        if long_ and qty <= 0:
            try:
                price = fetcher(a.yahoo, range_="5d", interval="1d").last_price
            except DataError:
                price = None
            amount = min(budget(), float(client.cash().get("free") or 0))
            if not price or amount < 5:
                lines.append(f"• {a.name}: {state} — acquisto non possibile ora (prezzo o liquidità)")
                continue
            q = 0.0
            if not dry_run:
                for dec in (4, 3, 1, 0):
                    cand = floor_qty(amount / price, dec)
                    if cand <= 0:
                        continue
                    try:
                        client.market(ticker, cand)
                        q = cand
                        break
                    except Exception as exc:  # noqa: BLE001
                        log.warning("Acquisto %s con %d decimali rifiutato: %s", a.name, dec, exc)
                if not q:
                    lines.append(f"• {a.name}: {state} — ⚠️ acquisto non riuscito")
                    continue
            changes += 1
            tr["holdings"][a.key] = {"since": now.isoformat(), "entry": price}
            shares = q or amount / price
            short = " — liquidità insufficiente per l'importo pieno" if shares * price < budget() - 1 else ""
            lines.append(f"• {a.name}: {state} → 🟢 COMPRATO {shares:g} quote a {price:,.2f} € "
                         f"(circa {eur(shares * price)}){short}")
        elif not long_ and qty > 0:
            if not dry_run:
                try:
                    client.market(ticker, -qty)
                except Exception as exc:  # noqa: BLE001
                    lines.append(f"• {a.name}: {state} — ⚠️ vendita non riuscita ({exc})")
                    continue
            changes += 1
            price = float(pos.get("currentPrice") or 0)
            entry = (tr["holdings"].pop(a.key, None) or {}).get("entry")
            res = f" · risultato {price / entry - 1:+.1%}" if entry and price else ""
            tr["history"] = (tr["history"] + [{"key": a.key, "sold": now.isoformat(), "entry": entry, "exit": price}])[-60:]
            lines.append(f"• {a.name}: {state} → 🔴 VENDUTO a {price:,.2f} €{res}, resto liquido")
        else:
            lines.append(f"• {a.name}: {state} — {'resto investito' if long_ else 'resto liquido'}")
        lines.append(f"   ({', '.join(detail)})")
    lines += ["", "Regola: investito se il prezzo di fine mese è sopra quello di 3, 6 e 12 mesi prima "
              "(almeno 2 su 3). Prossimo controllo il mese prossimo.", FOOTER]
    text = "\n".join(lines)
    if dry_run:
        print(text)
        return st
    tr["months"] = (tr["months"] + [month])[-36:]
    if not send(text):
        log.warning("Messaggio trend non inviato")
    log.info("Trend lento: %d cambi", changes)
    return st


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if os.getenv("SPUTNIK_TREND", "1").strip().lower() in {"0", "false", "no"}:
        print("SPUTNIK TREND: disattivato (SPUTNIK_TREND=0).")
        return 0
    key = os.getenv("SPUTNIK_INVEST_DEMO_API_KEY", "").strip()
    secret = os.getenv("SPUTNIK_INVEST_DEMO_API_SECRET", "").strip()
    if not key or not secret:
        print("SPUTNIK TREND: chiavi demo assenti, nessuna operazione.")
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
