"""SPUTNIK v4 — public filing intelligence engine.

SPUTNIK is deliberately separate from GAGARIN.
It monitors only publicly documented SEC filings configured through CIKs,
normalizes and deduplicates events, tracks filing timing, and sends
informational Telegram alerts. It does not place trades or infer private activity.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SEC_SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik}.json"
STATE_FILE = Path(os.getenv("SPUTNIK_STATE_FILE", "sputnik_state.json"))
MAX_STATE_EVENTS = 5000


@dataclass
class FilingEvent:
    source: str
    cik: str
    accession: str
    form: str
    filed_at: str
    primary_document: str
    company: str
    source_url: str
    event_id: str
    evidence: str = "PRIMARY_DOCUMENT"
    status: str = "CONFIRMED"
    transaction_type: str = "DISCLOSURE_ONLY"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def http_get_json(url: str, user_agent: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    return json.loads(raw.decode("utf-8"))


def normalize_cik(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if not digits:
        raise ValueError(f"CIK non valido: {value!r}")
    return digits.zfill(10)


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {"events": {}, "updated_at": None}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # Corrupted state must not crash the whole collector.
        return {"events": {}, "updated_at": None}


def save_state(state: dict[str, Any]) -> None:
    state["updated_at"] = utc_now().isoformat()
    events = state.get("events", {})
    if len(events) > MAX_STATE_EVENTS:
        keep = sorted(
            events.items(),
            key=lambda item: item[1].get("filed_at", ""),
            reverse=True,
        )[:MAX_STATE_EVENTS]
        state["events"] = dict(keep)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(STATE_FILE)


def event_id(cik: str, accession: str, form: str, document: str) -> str:
    raw = "|".join((cik, accession, form, document))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def filing_url(cik: str, accession: str, document: str) -> str:
    accession_compact = accession.replace("-", "")
    return (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{int(cik)}/{accession_compact}/{document}"
    )


def fetch_sec_events(cik: str, user_agent: str, forms: set[str]) -> list[FilingEvent]:
    data = http_get_json(SEC_SUBMISSIONS.format(cik=cik), user_agent)
    recent = data.get("filings", {}).get("recent", {})

    fields = ["accessionNumber", "filingDate", "form", "primaryDocument"]
    if not all(field in recent for field in fields):
        raise ValueError("Formato SEC submissions inatteso: campi mancanti.")

    company = data.get("name") or f"CIK {cik}"
    events: list[FilingEvent] = []

    for accession, filed, form, document in zip(
        recent["accessionNumber"],
        recent["filingDate"],
        recent["form"],
        recent["primaryDocument"],
    ):
        if form not in forms:
            continue

        eid = event_id(cik, accession, form, document)
        events.append(
            FilingEvent(
                source="SEC_EDGAR",
                cik=cik,
                accession=accession,
                form=form,
                filed_at=filed,
                primary_document=document,
                company=company,
                source_url=filing_url(cik, accession, document),
                event_id=eid,
            )
        )

    return events


def collect() -> list[FilingEvent]:
    raw_ciks = os.getenv("SPUTNIK_CIKS", "").strip()
    if not raw_ciks:
        print("SPUTNIK: nessun CIK configurato. Impostare SPUTNIK_CIKS.")
        return []

    user_agent = os.getenv(
        "SEC_USER_AGENT",
        "SPUTNIK document monitor / contact not configured",
    )
    forms = {
        item.strip()
        for item in os.getenv(
            "SPUTNIK_SEC_FORMS",
            "3,4,5,8-K,13D,13G,13F-HR,13F-HR/A,144",
        ).split(",")
        if item.strip()
    }

    events: list[FilingEvent] = []
    for raw in raw_ciks.split(","):
        cik = normalize_cik(raw)
        try:
            events.extend(fetch_sec_events(cik, user_agent, forms))
            time.sleep(0.2)
        except Exception as exc:
            print(f"SPUTNIK: SEC source error CIK {cik}: {exc}")

    return events


def new_events(events: list[FilingEvent], state: dict[str, Any]) -> list[FilingEvent]:
    known = state.setdefault("events", {})
    fresh = []
    for event in events:
        if event.event_id in known:
            continue
        known[event.event_id] = asdict(event)
        fresh.append(event)
    return fresh


def telegram_message(event: FilingEvent) -> str:
    return (
        "🛰️ SPUTNIK — NUOVO DOCUMENTO\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🏢 {event.company}\n"
        f"📄 Form: {event.form}\n"
        f"📅 Filing: {event.filed_at}\n"
        f"🧾 Stato: {event.status}\n"
        f"🔎 Evidenza: {event.evidence}\n"
        f"📌 Tipo: {event.transaction_type}\n"
        f"🔗 {event.source_url}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "ℹ️ Evento documentale pubblico. Nessuna operazione privata viene inferita."
    )


def send_telegram(message: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("SPUTNIK: Telegram non configurato.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode(
        {"chat_id": chat_id, "text": message, "disable_web_page_preview": "true"}
    ).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if payload.get("ok") is True:
            return True
        print(f"SPUTNIK: Telegram API error: {payload.get('description', 'unknown error')}")
    except urllib.error.HTTPError as exc:
        print(f"SPUTNIK: Telegram HTTP error {exc.code}.")
        try:
            payload = json.loads(exc.read().decode("utf-8", errors="replace"))
            print(f"SPUTNIK: Telegram API error: {payload.get('description', 'unknown error')}")
        except Exception:
            pass
    except urllib.error.URLError as exc:
        print(f"SPUTNIK: Telegram network error: {exc.reason}")
    except Exception as exc:
        print(f"SPUTNIK: Telegram exception: {type(exc).__name__}")
    return False


def telegram_test_message() -> str:
    return (
        "🛰️ SPUTNIK — TELEGRAM ONLINE\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "✅ Connessione Telegram verificata.\n"
        "🔐 Token e Chat ID ricevuti da GitHub Secrets.\n"
        "📡 SPUTNIK resta separato da GAGARIN.\n"
        "ℹ️ Messaggio di test: nessuna operazione di mercato."
    )


def main() -> None:
    if os.getenv("SPUTNIK_TELEGRAM_TEST", "").strip().lower() in {"1", "true", "yes"}:
        print("SPUTNIK: esecuzione test Telegram.")
        if not send_telegram(telegram_test_message()):
            raise SystemExit("SPUTNIK: test Telegram fallito.")
        print("SPUTNIK: test Telegram riuscito.")
        return

    state = load_state()
    events = collect()
    fresh = new_events(events, state)
    save_state(state)

    print(f"SPUTNIK: {len(events)} filing trovati, {len(fresh)} nuovi.")

    for event in fresh:
        message = telegram_message(event)
        print(message)
        send_telegram(message)


if __name__ == "__main__":
    main()
