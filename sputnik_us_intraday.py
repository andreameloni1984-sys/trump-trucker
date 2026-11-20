"""Sputnik USA scheduled collector and paper Telegram delivery."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from zoneinfo import ZoneInfo

from sputnik_us_market import MAX_CATALYST_AGE, MAX_QUOTE_AGE, evaluate
from sputnik_us_news import catalyst, collect_news, eligible_news
from trump_tracker import send_telegram


def utc_now():
    return datetime.now(timezone.utc)


def format_signal(item, bias, levels):
    local = datetime.fromisoformat(item["published"]).astimezone(ZoneInfo("Europe/Rome"))
    summary = item["title"]
    if bias["fact"] not in summary.lower():
        summary = f"{summary} — {bias['fact']}"
    return (
        "🛰️ SPUTNIK — SEGNALE USA\n\n"
        f"Ticker: {bias['ticker']}\n"
        f"Direzione: {bias['direction']}\n\n"
        f"Notizia: {summary}\n"
        f"Motivazione: {bias['reason']}\n\n"
        f"ENTRY: {levels['entry']:.2f}\n"
        f"SL: {levels['stop']:.2f}\n"
        f"TP1: {levels['tp1']:.2f}\n"
        f"TP2: {levels['tp2']:.2f}\n"
        f"Rischio/rendimento: 1:{levels['rr1']:.2f} / 1:{levels['rr2']:.2f}\n\n"
        f"Fonte: {item['url']}\n"
        f"Ora: {local:%d/%m/%Y %H:%M %Z} (Europe/Rome)\n"
        "Stato: CONFERMATO\n\n"
        "PAPER ONLY"
    )


def scan(items, state, now, *, check=evaluate, clock=utc_now):
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
    candidates.sort(key=lambda event: (event["kind"] == "press", event["published"]))

    def check_candidate(item):
        bias = item["bias"]
        published = datetime.fromisoformat(item["published"])
        return check(bias["ticker"], bias["direction"], published, clock())

    outbox = []
    checked_keys = set()
    with ThreadPoolExecutor(max_workers=4) as pool:
        batch = []
        for item in candidates:
            bias = item["bias"]
            key = f"{bias['rule']}:{bias['ticker']}"
            if key in reservations:
                item["status"] = "duplicato"
                continue
            if key in checked_keys:
                item["status"] = "duplicato"
                continue
            checked_keys.add(key)
            batch.append((key, item))
        for (key, item), (status, levels) in zip(batch, pool.map(check_candidate, [i for _, i in batch])):
            item["status"] = status
            if levels is None:
                continue
            if not timedelta(0) <= clock() - datetime.fromisoformat(levels["quote_timestamp"]) <= MAX_QUOTE_AGE:
                item["status"] = "quotazione obsoleta prima dell’invio"
                continue
            item["status"] = "riservato"
            item["levels"] = levels
            reservations[key] = now.isoformat()
            outbox.append({"text": format_signal(item, item["bias"], levels),
                           "quote_timestamp": levels["quote_timestamp"]})
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
        age = clock() - datetime.fromisoformat(message["quote_timestamp"])
        if timedelta(0) <= age <= MAX_QUOTE_AGE and send(message["text"]):
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
    if args.mode == "deliver":
        outbox = json.loads(args.outbox.read_text(encoding="utf-8"))
        args.outbox.unlink()
        count = deliver(outbox)
        print(f"SPUTNIK USA: Telegram ha confermato {count}/{len(outbox)} messaggi.")
        if count != len(outbox):
            raise SystemExit(1)
        return

    state = json.loads(args.state.read_text(encoding="utf-8")) if args.state.exists() else {}
    news = collect_news()
    outbox = scan(news, state, utc_now())
    print(f"SPUTNIK USA: {len(news)} elementi verificabili, {len(outbox)} setup eseguibili.")
    if args.mode == "collect":
        write_json(args.state, state)
        write_json(args.outbox, outbox)
    else:
        for message in outbox:
            print(message["text"])


if __name__ == "__main__":
    main()
