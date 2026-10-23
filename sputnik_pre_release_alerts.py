"""Send deduplicated pre-release alerts from the official BLS iCalendar feed.

This first connector covers BLS releases only. It sends informational watch alerts,
not directional trade signals. State is persisted by the repository workflow.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from sputnik_release_calendar import prepare_release_watch

BLS_ICS_URL = "https://www.bls.gov/schedule/news_release/bls.ics"
STATE_PATH = Path(os.getenv("SPUTNIK_RELEASE_STATE_FILE", "sputnik_release_state.json"))
ROME = ZoneInfo("Europe/Rome")
ET = ZoneInfo("America/New_York")
ALERT_WINDOW_MINUTES = int(os.getenv("SPUTNIK_RELEASE_ALERT_MINUTES", "30"))


def _unfold_ics(text: str) -> list[str]:
    lines: list[str] = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if line.startswith((" ", "\t")) and lines:
            lines[-1] += line[1:]
        else:
            lines.append(line)
    return lines


def _parse_dt(value: str, params: str) -> datetime:
    value = value.strip()
    if value.endswith("Z"):
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    if re.fullmatch(r"\d{8}", value):
        # All-day events have no exact release time; do not send a timed alert.
        raise ValueError("all-day event has no release time")
    parsed = datetime.strptime(value, "%Y%m%dT%H%M%S")
    tz_match = re.search(r"TZID=([^;:]+)", params)
    tz_name = tz_match.group(1) if tz_match else "America/New_York"
    return parsed.replace(tzinfo=ZoneInfo(tz_name))


def parse_bls_ics(text: str) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in _unfold_ics(text):
        if line == "BEGIN:VEVENT":
            current = {}
            continue
        if line == "END:VEVENT" and current is not None:
            if current.get("summary") and current.get("start") and current.get("uid"):
                events.append(current)
            current = None
            continue
        if current is None or ":" not in line:
            continue
        left, value = line.split(":", 1)
        key, _, params = left.partition(";")
        key = key.upper()
        if key == "SUMMARY":
            current["summary"] = value.replace("\\,", ",").replace("\\;", ";")
        elif key == "UID":
            current["uid"] = value.strip()
        elif key == "DTSTART":
            current["start"] = value.strip()
            current["start_params"] = params
        elif key == "URL":
            current["url"] = value.strip()
    return events


def upcoming_classified_events(events: list[dict[str, str]], now: datetime | None = None) -> list[dict[str, object]]:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    result: list[dict[str, object]] = []
    for event in events:
        try:
            release_at = _parse_dt(event["start"], event.get("start_params", ""))
        except (ValueError, KeyError, TypeError):
            continue
        minutes = (release_at.astimezone(timezone.utc) - now.astimezone(timezone.utc)).total_seconds() / 60
        if not 0 <= minutes <= ALERT_WINDOW_MINUTES:
            continue
        watch = prepare_release_watch(event["summary"], release_at.isoformat())
        if watch["status"] != "PREPARE_BEFORE_RELEASE":
            continue
        result.append({
            "uid": event["uid"],
            "title": event["summary"],
            "url": event.get("url", ""),
            "minutes_until": int(minutes),
            "scheduled_rome": watch["scheduled_rome"],
            "impact": watch["impact"],
            "instruments": watch["instruments"],
        })
    return sorted(result, key=lambda row: int(row["minutes_until"]))


def _load_state() -> dict[str, object]:
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"sent": []}
    except (OSError, ValueError):
        return {"sent": []}


def _send_telegram(message: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID sono necessari")
    payload = json.dumps({"chat_id": chat_id, "text": message, "disable_web_page_preview": True}).encode()
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        body = json.loads(response.read().decode("utf-8"))
    if not body.get("ok"):
        raise RuntimeError("Telegram API non ha confermato l'invio")


def format_alert(event: dict[str, object]) -> str:
    instruments = ", ".join(str(x) for x in event["instruments"])
    lines = [
        "🛰️ SPUTNIK — PRE-RELEASE WATCH",
        "━━━━━━━━━━━━━━━━━━",
        f"📅 Evento: {event['title']}",
        f"⏱️ Tra circa {event['minutes_until']} min · ora italiana {event['scheduled_rome']}",
        f"⚠️ Impatto atteso: {event['impact']}",
        f"👀 Strumenti da osservare: {instruments}",
        "🧭 Direzione: NON INFERITA — attendere dato, prezzo e conferma tecnica.",
        "ℹ️ Avviso informativo, non è un ordine né un segnale LONG/SHORT.",
    ]
    if event.get("url"):
        lines.append(f"Fonte ufficiale: {event['url']}")
    return "\n".join(lines)


def run(now: datetime | None = None) -> int:
    request = urllib.request.Request(BLS_ICS_URL, headers={"User-Agent": "SputnikReleaseWatch/1.0"})
    with urllib.request.urlopen(request, timeout=25) as response:
        calendar_text = response.read().decode("utf-8-sig")
    candidates = upcoming_classified_events(parse_bls_ics(calendar_text), now=now)
    state = _load_state()
    sent = set(str(x) for x in state.get("sent", []))
    new_sent = list(sent)
    count = 0
    for event in candidates:
        uid = str(event["uid"])
        if uid in sent:
            continue
        _send_telegram(format_alert(event))
        new_sent.append(uid)
        sent.add(uid)
        count += 1
    state["sent"] = new_sent[-2000:]
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"SPUTNIK release watch: {len(candidates)} prossimi eventi classificati, {count} nuovi avvisi.")
    return count


if __name__ == "__main__":
    run()
