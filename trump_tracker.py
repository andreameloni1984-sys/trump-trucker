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
from html.parser import HTMLParser
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SEC_SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik}.json"
STATE_FILE = Path(os.getenv("SPUTNIK_STATE_FILE", "sputnik_state.json"))
MAX_STATE_EVENTS = 5000
TELEGRAM_POLL_TIMEOUT = 5


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


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
    def handle_data(self, data: str) -> None:
        text = re.sub(r"\\s+", " ", data).strip()
        if text:
            self.parts.append(text)

    def text(self) -> str:
        return " ".join(self.parts)


INTELLIGENCE_SOURCES = {
    "WHITE_HOUSE": "https://www.whitehouse.gov/",
    "TRUTH_ARCHIVE": "https://www.trumpstruth.org/",
    "OGE": "https://www.oge.gov/",
}

ASSET_KEYWORDS = {
    "ENERGY": ["oil", "crude", "brent", "wti", "natural gas", "lng", "energy", "petroleum"],
    "METALS": ["gold", "silver", "copper", "aluminum", "steel", "uranium"],
    "AGRICULTURE": ["corn", "wheat", "soybean", "sugar", "coffee", "cocoa", "cotton"],
    "DEFENSE": ["defense", "drone", "missile", "military", "aerospace", "weapons"],
    "AI_TECH": ["artificial intelligence", "ai", "semiconductor", "chip", "data center", "cloud"],
    "SPACE": ["spacex", "rocket", "satellite", "space"],
    "CRYPTO": ["bitcoin", "ethereum", "crypto", "digital asset", "stablecoin"],
    "MEDIA": ["truth social", "truth", "media", "streaming"],
    "REAL_ESTATE": ["real estate", "property", "hotel", "resort"],
}

def fetch_public_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": os.getenv("SEC_USER_AGENT", "SPUTNIK/4.0 public-source-monitor"),
            "Accept": "text/html,application/xhtml+xml,text/plain",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read()
    parser = TextExtractor()
    parser.feed(raw.decode("utf-8", errors="replace"))
    return parser.text()

def intelligence_snapshot(state: dict[str, Any]) -> list[dict[str, Any]]:
    if os.getenv("SPUTNIK_SOCIAL_ENABLED", "1").strip().lower() not in {"1", "true", "yes"}:
        return []

    known = state.setdefault("intelligence", {})
    findings: list[dict[str, Any]] = []

    for source, url in INTELLIGENCE_SOURCES.items():
        try:
            body = fetch_public_text(url)
        except Exception as exc:
            print(f"SPUTNIK: source {source} unavailable: {type(exc).__name__}")
            continue

        normalized = body.lower()
        domains = []
        for domain, keywords in ASSET_KEYWORDS.items():
            if any(keyword in normalized for keyword in keywords):
                domains.append(domain)

        digest = hashlib.sha256((source + "|" + body[:200000]).encode("utf-8")).hexdigest()[:24]
        if known.get(source) == digest:
            continue
        known[source] = digest

        if domains:
            findings.append({
                "source": source,
                "url": url,
                "domains": domains,
                "evidence": "PUBLIC_SOURCE_TEXT",
                "status": "POTENTIAL_CORRELATION",
            })

    return findings

def intelligence_message(item: dict[str, Any]) -> str:
    return (
        "🛰️ SPUTNIK — INTELLIGENCE\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"📡 Fonte: {item['source']}\n"
        f"🧩 Aree citate: {', '.join(item['domains'])}\n"
        f"🔎 Evidenza: {item['evidence']}\n"
        "⚠️ Stato: CORRELAZIONE DA VERIFICARE\n"
        f"🔗 {item['url']}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "ℹ️ Una menzione social o una correlazione non prova un investimento."
    )

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


def telegram_api(method: str, token: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(params or {}).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def poll_telegram_commands(state: dict[str, Any]) -> bool:
    """Process /start, /stop, /status and /test without exposing secrets.

    Returns whether monitoring should be active after processing commands.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return bool(state.get("telegram_active", False))

    offset = int(state.get("telegram_update_offset", 0) or 0)
    try:
        payload = telegram_api(
            "getUpdates",
            token,
            {"offset": offset, "timeout": TELEGRAM_POLL_TIMEOUT, "allowed_updates": '["message"]'},
        )
    except Exception as exc:
        print(f"SPUTNIK: Telegram polling error: {type(exc).__name__}")
        return bool(state.get("telegram_active", False))

    if not payload.get("ok"):
        print(f"SPUTNIK: Telegram polling API error: {payload.get('description', 'unknown error')}")
        return bool(state.get("telegram_active", False))

    active = bool(state.get("telegram_active", False))
    updates = payload.get("result", [])
    print(f"SPUTNIK: Telegram updates ricevuti: {len(updates)}")
    accepted = 0
    for update in updates:
        update_id = int(update.get("update_id", 0))
        state["telegram_update_offset"] = max(offset, update_id + 1)

        message = update.get("message") or {}
        incoming_chat = str((message.get("chat") or {}).get("id", ""))
        if incoming_chat != str(chat_id):
            print("SPUTNIK: ricevuto un comando da una chat non autorizzata.")
            continue

        accepted += 1
        text = str(message.get("text", "")).strip().lower()
        if text == "/start":
            active = True
            send_telegram(
                "🛰️ SPUTNIK ATTIVO\n━━━━━━━━━━━━━━━━━━\n"
                "✅ Monitoraggio attivato.\n"
                "📡 Controllo SEC ad ogni esecuzione GitHub Actions.\n"
                "⏱️ Comandi: /status /stop /test"
            )
        elif text == "/stop":
            active = False
            send_telegram("🛰️ SPUTNIK FERMATO\n━━━━━━━━━━━━━━━━━━\n⛔ Monitoraggio sospeso.")
        elif text == "/status":
            status = "ATTIVO" if active else "FERMO"
            send_telegram(
                f"🛰️ SPUTNIK — STATO\n━━━━━━━━━━━━━━━━━━\n"
                f"📡 Monitoraggio: {status}\n"
                "⏱️ Frequenza: ogni 15 minuti\n"
                "🔎 Fonte: SEC EDGAR"
            )
        elif text == "/test":
            send_telegram(telegram_test_message())

    print(f"SPUTNIK: Telegram comandi autorizzati: {accepted}")
    state["telegram_active"] = active
    return active


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
    active = poll_telegram_commands(state)

    if not active:
        save_state(state)
        print("SPUTNIK: monitoraggio fermo. Usa /start su Telegram.")
        return

    events = collect()
    fresh = new_events(events, state)
    intelligence = intelligence_snapshot(state)
    save_state(state)

    print(f"SPUTNIK: {len(events)} filing trovati, {len(fresh)} nuovi.")
    print(f"SPUTNIK: {len(intelligence)} nuove correlazioni da fonti pubbliche.")

    for event in fresh:
        message = telegram_message(event)
        print(message)
        send_telegram(message)

    for item in intelligence:
        message = intelligence_message(item)
        print(message)
        send_telegram(message)


if __name__ == "__main__":
    main()
