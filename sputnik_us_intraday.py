"""Sputnik USA scheduled collector and paper Telegram delivery."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import monotonic

from sputnik_us_catalog import load_catalog, resolve_benchmark
from sputnik_us_market import MAX_CATALYST_AGE, MAX_QUOTE_AGE, evaluate, evaluate_bars, read_bars
from sputnik_us_pravda import record_observations, summarize
from sputnik_us_news import catalyst, collect_news, describe_news, eligible_news, same_event, verify_truth
from trump_tracker import send_telegram


def utc_now():
    return datetime.now(timezone.utc)


def format_signal(item, bias, levels):
    summary = item["title"]
    if bias["fact"] not in summary.lower():
        summary = f"{summary} — {bias['fact']}"
    return (
        "🛰️ SPUTNIK USA\n\n"
        f"AZIONE: {bias['ticker']}\n"
        f"DIREZIONE: {bias['direction']}\n\n"
        f"NOTIZIA: {summary}\n"
        f"MOTIVO: {bias['reason']}\n\n"
        f"ENTRY: {levels['entry']:.2f}\n"
        f"STOP LOSS: {levels['stop']:.2f}\n"
        f"TP1: {levels['tp1']:.2f}\n"
        f"TP2: {levels['tp2']:.2f}\n\n"
        f"FONTE: {item['url']}\n"
        "STATO: CONFERMATO\n\n"
        "PAPER ONLY"
    )


def scan(items, state, now, *, check=evaluate, clock=utc_now, reserve=True):
    events = state.setdefault("events", {})
    reservations = state.setdefault("reservations", {})
    for key, event in list(events.items()):
        if now - datetime.fromisoformat(event["published"]) > timedelta(days=2):
            del events[key]
    for key, stamp in list(reservations.items()):
        if now - datetime.fromisoformat(stamp) > timedelta(hours=8):
            del reservations[key]

    for item in eligible_news(items, now):
        if item["url"] in events:
            continue
        bias = catalyst(item)
        # Keep verifiable items for research, including those without a bias.
        events[item["url"]] = {key: item[key] for key in ("source", "kind", "url", "published", "title")}
        events[item["url"]].update(bias=bias, status="bias in attesa" if bias else "senza bias")
    candidates = []
    for event in events.values():
        if not event["bias"] or event["status"] in {"riservato", "duplicato"}:
            continue
        if now - datetime.fromisoformat(event["published"]) > MAX_CATALYST_AGE:
            event["status"] = "catalizzatore fuori finestra intraday"
        else:
            candidates.append(event)
    # Prefer the primary source when a news outlet reports the same event.
    candidates.sort(key=lambda event: (event["kind"] not in {"press", "wire"}, event["published"]))

    def check_candidate(item):
        bias = item["bias"]
        published = datetime.fromisoformat(item["published"])
        return check(bias["ticker"], bias["direction"], published, clock())

    outbox = []
    reserved_events = [event for event in events.values()
                       if event["bias"] and event["status"] == "riservato"]
    batch = []
    for item in candidates:
        if any(same_event(item, reserved) for reserved in reserved_events):
            item["status"] = "duplicato"
            continue
        if any(same_event(item, queued) for queued in batch):
            # Retry with the alternate source if the preferred record ages out.
            item["status"] = "in attesa della fonte primaria"
            continue
        batch.append(item)

    with ThreadPoolExecutor(max_workers=4) as pool:
        for item, (status, levels) in zip(batch, pool.map(check_candidate, batch)):
            item["status"] = status
            item.pop("levels", None)
            if status != "CONFERMATO" or levels is None:
                continue
            if not timedelta(0) <= clock() - datetime.fromisoformat(levels["quote_timestamp"]) <= MAX_QUOTE_AGE:
                item["status"] = "quotazione obsoleta prima dell’invio"
                continue
            item["levels"] = levels
            if reserve:
                item["status"] = "riservato"
                reservations[item["url"]] = now.isoformat()
            outbox.append({"text": format_signal(item, item["bias"], levels),
                           "quote_timestamp": levels["quote_timestamp"]})
    return outbox


def format_invest(item, record):
    levels = record.get("levels") or {}
    def number(value):
        return "N/D" if value is None else f"{value:.2f} USD"

    side = "🟢 LONG" if record["direction"] == "LONG" else "🔴 SHORT"
    note = " (tesi simulata)" if record["direction"] == "SHORT" else ""
    return (
        "🛰️ SPUTNIK INVEST\n\n"
        f"AZIONE: {record['name']} ({record['ticker']})\n"
        f"DIREZIONE: {side}{note}\n"
        f"NOTIZIA: {item['title']}\n"
        f"MOTIVO: {item['bias']['reason']}\n"
        f"PREZZO: {number(record['price'])}\n"
        f"ENTRY: {number(levels.get('entry'))}\n"
        f"STOP: {number(levels.get('stop'))}\n"
        f"TP1: {number(levels.get('tp1'))}\n"
        f"TP2: {number(levels.get('tp2'))}\n"
        f"AFFIDABILITÀ: {record['score']}/100 (euristico)\n"
        f"STATO: {record['stage']}\n"
        f"FONTE: {item['url']}"
    )


def scan_invest(items, state, now, catalog, *, read=read_bars, clock=utc_now, reserve=True):
    events = state.setdefault("invest_events", {})
    ledger = state.setdefault("pravda", [])
    for url, event in list(events.items()):
        if now - datetime.fromisoformat(event["published"]) > timedelta(days=2):
            del events[url]

    for item in eligible_news(items, now):
        if item["url"] in events:
            continue
        published = datetime.fromisoformat(item["published"])
        if item["kind"] == "truth" and now - published <= MAX_CATALYST_AGE:
            verified = verify_truth(item)
            if verified is not None:
                item = verified
                published = datetime.fromisoformat(item["published"])
            else:
                continue
        bias = catalyst(item, invest=True) if timedelta(0) <= now - published <= MAX_CATALYST_AGE else None
        category, evidence = describe_news(item, bias)
        if bias:
            bias["ticker"] = bias["ticker"].replace(".", "-")
        events[item["url"]] = {**{key: value for key, value in item.items() if key != "text"},
                               "bias": bias, "category": category, "evidence": evidence,
                               "beneficiaries": [],
                               "penalized": [],
                               "status": "SCARTARE" if not bias else "in attesa"}

    benchmarks = {}
    eligible = []
    impact_order = {"fed": 0, "policy": 0, "fda": 0, "agency": 0, "issuer": 1, "wire": 1}
    for event in sorted(events.values(), key=lambda item: (impact_order.get(item["kind"], 2),
                                                           item["published"])):
        if not event["bias"] or event["status"] in {"SCARTARE", "duplicato", "ENTRARE"}:
            continue
        if now - datetime.fromisoformat(event["published"]) > MAX_CATALYST_AGE:
            event.update(status="SCARTARE", detail="catalizzatore fuori finestra")
            continue
        bias = event["bias"]
        benchmark = bias.get("benchmark")
        if benchmark and not event.get("stages") and catalog is not None:
            if benchmark not in benchmarks:
                benchmarks[benchmark] = resolve_benchmark(catalog, benchmark)
            bias["ticker"] = benchmarks[benchmark] or ""
        ticker = bias["ticker"]
        if catalog is None or ticker not in catalog:
            event["detail"] = "catalogo indisponibile" if catalog is None else "simbolo INVEST non verificato"
            continue
        event["beneficiaries"] = [ticker] if bias["direction"] == "LONG" else []
        event["penalized"] = [ticker] if bias["direction"] == "SHORT" else []
        if any(same_event(event, other) for other in eligible) or any(
            other["url"] != event["url"] and other.get("stages") and same_event(event, other)
            for other in events.values() if other["bias"]
        ):
            event["status"] = "duplicato"
            continue
        eligible.append(event)

    instruments = {event["bias"]["ticker"]: catalog[event["bias"]["ticker"]]["type"]
                   for event in eligible}
    pending = [record for record in ledger if not record.get("complete")]
    instruments.update({record["ticker"]: record["type"] for record in pending})

    def fetch(ticker):
        expected = "ETF" if instruments[ticker] == "ETF" else "EQUITY"
        return read(ticker, now, expected, history=True)

    with ThreadPoolExecutor(max_workers=4) as pool:
        quotes = dict(zip(instruments, pool.map(fetch, instruments)))
    checked = clock()
    for record in pending:
        _, bars = quotes[record["ticker"]]
        record_observations(record, bars, checked)

    outbox = []
    for event in eligible:
        bias = event["bias"]
        ticker, side = bias["ticker"], bias["direction"]
        instrument = catalog[ticker]
        published = datetime.fromisoformat(event["published"])
        if checked - published > MAX_CATALYST_AGE:
            continue
        error, bars = quotes[ticker]
        price = None
        if bars:
            stamp, _, _, close, _ = bars[-1]
            if 0 <= checked.timestamp() - stamp - 60 <= MAX_QUOTE_AGE.total_seconds():
                price = close
        status, levels = error or "solo ricerca SHORT", None
        if side == "LONG" and not error and bars and price is not None:
            status, levels = evaluate_bars(bars, side, published, checked, invest=True)
        if status in {"volatilità eccessiva o prezzo già esteso", "reazione alla notizia già estesa"}:
            event.update(status="SCARTARE", detail=status)
            continue
        stage = "ENTRARE" if levels else "PREPARARE"
        event.update(status=stage, detail=status if not levels else levels["setup"])
        stages = event.setdefault("stages", [])
        if stage not in stages:
            record = {
                "url": event["url"], "title": event["title"], "published": event["published"],
                "category": event["category"], "rule": bias["rule"], "reason": bias["reason"], "ticker": ticker,
                "name": instrument.get("name") or ticker, "type": instrument["type"],
                "direction": side, "price": price, "levels": levels, "stage": stage,
                "price_timestamp": (datetime.fromtimestamp(stamp + 60, timezone.utc).isoformat()
                                    if price is not None else None),
                "score": (65 if bias["uncertainty"] == "alta" else 75) + (10 if levels else 0),
                "signalled": checked.isoformat(), "acquisition_seconds": event.get("acquisition_seconds"),
                "signal_latency_seconds": (checked - published).total_seconds(),
            }
            stages.append(stage)
            ledger.append(record)
        else:
            record = next(record for record in reversed(ledger)
                          if record["url"] == event["url"] and record["stage"] == stage)
        notifications = event.setdefault("notifications", [])
        if stage not in notifications and (stage == "PREPARARE" or record["levels"] == levels):
            if reserve:
                notifications.append(stage)
            outbox.append({"text": format_invest(event, record), "stage": stage,
                           "expires": (published + MAX_CATALYST_AGE).isoformat(),
                           "quote_timestamp": record["price_timestamp"],
                           "without_price": (format_invest(event, {**record, "price": None})
                                             if stage == "PREPARARE" else None)})
    state["pravda_summary"] = summarize(ledger)
    return outbox


def write_json(path, data):
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        try:
            json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)


def deliver(outbox, *, send=send_telegram, clock=utc_now):
    delivered = 0
    for message in outbox:
        now = clock()
        stamp = message["quote_timestamp"]
        fresh = stamp is None or timedelta(0) <= now - datetime.fromisoformat(stamp) <= MAX_QUOTE_AGE
        expires = message.get("expires")
        message_text = message["text"] if fresh else message.get("without_price")
        if message_text and (not expires or now <= datetime.fromisoformat(expires)) and send(message_text):
            delivered += 1
    return delivered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("preview", "collect", "deliver"), nargs="?", default="preview")
    parser.add_argument("--state", type=Path, default=Path("sputnik_us_state.json"))
    parser.add_argument("--outbox", type=Path, required=False)
    args = parser.parse_args()
    if args.mode != "preview" and args.outbox is None:
        parser.error("--outbox è richiesto per collect e deliver")
    if args.outbox is not None and args.state.resolve() == args.outbox.resolve():
        parser.error("stato e outbox devono essere file distinti")
    send_enabled = os.getenv("SPUTNIK_US_TELEGRAM_ENABLED") == "true"
    if send_enabled and args.mode != "preview" and not all(
        os.getenv(key) for key in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
    ):
        parser.error("Telegram Sputnik USA richiede credenziali")
    if args.mode == "deliver":
        if not send_enabled:
            parser.error("Telegram Sputnik USA richiede abilitazione esplicita")
        outbox = json.loads(args.outbox.read_text(encoding="utf-8"))
        total = len(outbox)
        delivered_count = 0
        # Checkpoint each acknowledged send to avoid replaying already delivered messages.
        while outbox:
            message = outbox[0]
            if deliver([message]) != 1:
                print(f"SPUTNIK INVEST: consegna interrotta dopo {delivered_count}/{total}; outbox residua conservata.")
                raise SystemExit(1)
            outbox.pop(0)
            write_json(args.outbox, outbox)
            delivered_count += 1
        args.outbox.unlink()
        print(f"SPUTNIK INVEST: Telegram ha confermato {delivered_count}/{total} messaggi.")
        return

    state = json.loads(args.state.read_text(encoding="utf-8")) if args.state.exists() else {}
    started = monotonic()
    with ThreadPoolExecutor(max_workers=2) as pool:
        catalog_request = pool.submit(load_catalog)
        news = collect_news()
        catalog = catalog_request.result()
    outbox = scan_invest(news, state, utc_now(), catalog, reserve=args.mode == "collect" and send_enabled)
    print(f"SPUTNIK INVEST: {len(news)} notizie, {len(outbox)} segnali, {monotonic() - started:.2f}s.")
    if args.mode == "collect":
        write_json(args.state, state)
        write_json(args.outbox, outbox)
    else:
        for message in outbox:
            print(message["text"])


if __name__ == "__main__":
    main()
