"""Official BLS macro-release calendar alerts for SPUTNIK.

The BLS iCalendar is the source of truth for scheduled BLS releases. Floating
calendar times are interpreted as America/New_York because the BLS schedule
explicitly states that its release times are Eastern Time.
"""
from __future__ import annotations

import hashlib
import html
import re
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

BLS_ICAL_URL = "https://www.bls.gov/schedule/news_release/bls.ics"
BLS_SCHEDULE_URL = "https://www.bls.gov/schedule/2026/"
USDA_WASDE_URL = "https://usda.azureedge.us/about-usda/general-information/staff-offices/office-chief-economist/commodity-markets/wasde-report"
BLS_TZ = ZoneInfo("America/New_York")
ROME_TZ = ZoneInfo("Europe/Rome")
HTTP_TIMEOUT_SECONDS = 20


def _unfold_ical(payload: str) -> list[str]:
    lines: list[str] = []
    for raw in payload.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if raw.startswith((" ", "\t")) and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    return lines


def _parse_ical_datetime(params: str, value: str) -> datetime | None:
    value = value.strip()
    if not value:
        return None
    # All-day DATE events have no release time and are not alertable.
    if len(value) == 8 and value.isdigit():
        return None
    try:
        if value.endswith("Z"):
            return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        parsed = datetime.strptime(value, "%Y%m%dT%H%M%S")
        tzid = ""
        for part in params.split(";"):
            if part.upper().startswith("TZID="):
                tzid = part.split("=", 1)[1].strip('"')
        zone = ZoneInfo(tzid) if tzid else BLS_TZ
        return parsed.replace(tzinfo=zone).astimezone(timezone.utc)
    except (ValueError, KeyError):
        return None


def parse_bls_ical(payload: bytes | str) -> list[dict]:
    text = payload.decode("utf-8-sig", errors="replace") if isinstance(payload, bytes) else str(payload)
    events: list[dict] = []
    current: dict[str, str] | None = None
    for line in _unfold_ical(text):
        upper = line.upper()
        if upper == "BEGIN:VEVENT":
            current = {}
            continue
        if upper == "END:VEVENT":
            if current:
                summary = current.get("SUMMARY", "").strip()
                start = current.get("DTSTART")
                if summary and start:
                    uid = current.get("UID") or hashlib.sha256(
                        f"{start}|{summary}".encode("utf-8")
                    ).hexdigest()
                    events.append({
                        "event_id": uid,
                        "summary": summary,
                        "start_utc": start,
                        "source": "BLS_OFFICIAL_ICAL",
                        "source_url": current.get("URL") or BLS_SCHEDULE_URL,
                    })
            current = None
            continue
        if current is None or ":" not in line:
            continue
        left, value = line.split(":", 1)
        key, *params = left.split(";")
        key = key.upper()
        if key == "DTSTART":
            parsed = _parse_ical_datetime(";".join(params), value)
            if parsed:
                current[key] = parsed.isoformat()
        elif key in {"UID", "SUMMARY", "URL"}:
            current[key] = value.strip()
    events.sort(key=lambda item: item["start_utc"])
    return events


def fetch_bls_calendar(opener=urllib.request.urlopen) -> list[dict]:
    request = urllib.request.Request(
        BLS_ICAL_URL,
        headers={
            "User-Agent": "SPUTNIK/1.0 public macro calendar",
            "Accept": "text/calendar,text/plain",
        },
    )
    with opener(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
        status = getattr(response, "status", 200)
        if status != 200:
            raise RuntimeError(f"BLS calendar HTTP {status}")
        payload = response.read()
    events = parse_bls_ical(payload)
    if not events:
        raise ValueError("BLS calendar returned no timed events")
    return events


def due_calendar_alerts(
    events: list[dict],
    sent_state: dict,
    now: datetime | None = None,
) -> list[dict]:
    """Return one not-yet-sent reminder stage per event; never infer market direction."""
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    current = current.astimezone(timezone.utc)
    due: list[dict] = []
    for event in events:
        try:
            release = datetime.fromisoformat(event["start_utc"].replace("Z", "+00:00"))
            if release.tzinfo is None or release.utcoffset() is None:
                continue
            release = release.astimezone(timezone.utc)
        except (KeyError, TypeError, ValueError):
            continue
        minutes = (release - current).total_seconds() / 60
        if 0 < minutes <= 15:
            stage = "15_MIN"
        elif 15 < minutes <= 60:
            stage = "1_HOUR"
        elif 60 < minutes <= 1440:
            stage = "24_HOURS"
        elif -10 <= minutes <= 0:
            stage = "RELEASE_WINDOW"
        else:
            continue
        sent = set(sent_state.get(event["event_id"], []))
        if stage in sent:
            continue
        due.append({**event, "stage": stage, "minutes_to_release": round(minutes, 1)})
    return due


def format_calendar_alert(event: dict) -> str:
    release = datetime.fromisoformat(event["start_utc"].replace("Z", "+00:00"))
    local = release.astimezone(ROME_TZ)
    minutes = event["minutes_to_release"]
    if event["stage"] == "RELEASE_WINDOW":
        timing = "PUBBLICAZIONE ATTESA / APPENA AVVENUTA"
    else:
        timing = f"TRA CIRCA {max(0, int(minutes))} MINUTI"
    return (
        "🗓️ SPUTNIK — CALENDARIO MACRO UFFICIALE\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"📌 EVENTO: {event['summary']}\n"
        f"⏰ {timing}\n"
        f"🕒 ORARIO: {local:%d/%m/%Y %H:%M} Italia\n"
        "📚 FONTE: " + ("U.S. Bureau of Labor Statistics" if event.get("source", "").startswith("BLS") else "U.S. Department of Agriculture (WASDE)") + "\n"
        f"🔗 {event.get('source_url') or BLS_SCHEDULE_URL}\n"
        "ℹ️ Promemoria di calendario: non è un segnale LONG/SHORT. "
        "Il dato effettivo e la reazione dei prezzi devono essere verificati separatamente."
    )


def parse_usda_wasde_calendar(payload: bytes | str) -> list[dict]:
    """Parse the official USDA WASDE release dates for every year published."""
    raw = payload.decode("utf-8-sig", errors="replace") if isinstance(payload, bytes) else str(payload)
    visible = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    visible = re.sub(r"\s+", " ", visible)
    events: list[dict] = []
    for match in re.finditer(
        r"In\s+(20\d{2})\s+the WASDE report will be released on\s+([^.]*)\.",
        visible,
        flags=re.IGNORECASE,
    ):
        year = int(match.group(1))
        for month, day in re.findall(r"([A-Za-z]{3})\.?\s+(\d{1,2})", match.group(2)):
            try:
                local = datetime.strptime(f"{month[:3]} {int(day)} {year}", "%b %d %Y").replace(tzinfo=BLS_TZ)
            except ValueError:
                continue
            events.append({
                "event_id": f"USDA-WASDE-{local:%Y%m%d}",
                "summary": "USDA WASDE — stime su cereali e semi oleosi",
                "start_utc": local.astimezone(timezone.utc).isoformat(),
                "source": "USDA_WASDE_OFFICIAL",
                "source_url": USDA_WASDE_URL,
            })
    events.sort(key=lambda item: item["start_utc"])
    return events


def fetch_usda_wasde_calendar(opener=urllib.request.urlopen) -> list[dict]:
    request = urllib.request.Request(
        USDA_WASDE_URL,
        headers={"User-Agent": "SPUTNIK/1.0 public macro calendar", "Accept": "text/html,application/xhtml+xml"},
    )
    with opener(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
        status = getattr(response, "status", 200)
        if status != 200:
            raise RuntimeError(f"USDA WASDE calendar HTTP {status}")
        payload = response.read()
    events = parse_usda_wasde_calendar(payload)
    if not events:
        raise ValueError("USDA WASDE calendar returned no release dates")
    return events


def fetch_macro_calendars() -> tuple[list[dict], list[str]]:
    """Fetch official calendars independently; one outage must not hide another."""
    events: list[dict] = []
    errors: list[str] = []
    for source_name, fetcher in (("BLS", fetch_bls_calendar), ("USDA_WASDE", fetch_usda_wasde_calendar)):
        try:
            events.extend(fetcher())
        except Exception as exc:
            errors.append(f"{source_name}: {type(exc).__name__}: {exc}")
    events.sort(key=lambda item: item["start_utc"])
    return events, errors
