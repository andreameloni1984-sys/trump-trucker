"""Cane da guardia dei bot: avvisa su Telegram se un bot si ferma o fallisce.

    python sputnik_watchdog.py            # controllo + avvisi
    python sputnik_watchdog.py --dry-run  # solo stampa

Legge le ultime esecuzioni GitHub Actions dei bot (repo pubblici) e scrive solo
quando qualcosa cambia: "⚠️ fermo/in errore" e poi "✅ di nuovo regolare".
Un problema che continua viene ricordato al massimo ogni 12 ore.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.request
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Callable

OWNER = "andreameloni1984-sys"
STATE_FILE = Path(os.getenv("WATCHDOG_STATE_FILE", "data/watchdog_state.json"))
REMIND_EVERY = timedelta(hours=12)


@dataclass(frozen=True)
class Check:
    name: str
    repo: str
    workflow: str
    max_silence: timedelta
    weekdays_only: bool = False
    start: time = time(0, 0)     # finestra attiva (UTC)
    end: time = time(23, 59)


CHECKS = (
    Check("Gagarin · bot CFD", "commodity-news-scanner", "cfd-bot.yml", timedelta(hours=3)),
    Check("Sputnik · Trump e miliardari", "trump-trucker", "trump_tracker.yml", timedelta(hours=1)),
    Check("Sputnik · trader demo", "trump-trucker", "sputnik-demo-trader.yml", timedelta(minutes=90),
          weekdays_only=True, start=time(8, 0), end=time(16, 59)),
    Check("Stella Rossa · calendario USA", "agri-intelligence-bot", "oracle.yml", timedelta(hours=3),
          weekdays_only=True, start=time(12, 0), end=time(21, 59)),
)


def fetch_runs(repo: str, workflow: str) -> list[dict]:
    url = f"https://api.github.com/repos/{OWNER}/{repo}/actions/workflows/{workflow}/runs?branch=main&per_page=6"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "sputnik-watchdog"})
    token = os.getenv("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp).get("workflow_runs", [])


def _t(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def in_window(check: Check, now: datetime) -> bool:
    if check.weekdays_only and now.weekday() > 4:
        return False
    return check.start <= now.time() <= check.end


def diagnose(check: Check, runs: list[dict], now: datetime) -> str | None:
    """Restituisce la descrizione del problema, oppure None se è tutto regolare."""
    if not runs:
        return "nessuna esecuzione trovata"
    latest = max(_t(r["created_at"]) for r in runs)
    window_open_since = datetime.combine(now.date(), check.start, timezone.utc)
    if in_window(check, now) and now - latest > check.max_silence and now - window_open_since > check.max_silence:
        hours = (now - latest).total_seconds() / 3600
        return f"non parte da {hours:.1f} ore"
    finished = [r for r in runs if r.get("status") == "completed" and r.get("conclusion") in ("success", "failure")]
    finished.sort(key=lambda r: r["created_at"], reverse=True)
    if len(finished) >= 2 and all(r["conclusion"] == "failure" for r in finished[:2]):
        return f"le ultime esecuzioni sono fallite ({finished[0].get('html_url', '')})"
    return None


def run(now: datetime | None = None, fetch: Callable[[str, str], list[dict]] = fetch_runs,
        send: Callable[[str], bool] = lambda t: False, state: dict | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    state = state if state is not None else {}
    alerts = state.setdefault("alerts", {})
    for check in CHECKS:
        key = f"{check.repo}/{check.workflow}"
        try:
            problem = diagnose(check, fetch(check.repo, check.workflow), now)
        except Exception as exc:  # noqa: BLE001
            problem = f"stato non leggibile da GitHub ({type(exc).__name__})"
        previous = alerts.get(key)
        if problem:
            kind = problem.split(" ")[0] + " " + problem.split(" ")[1]   # es. "non parte", "le ultime", "stato non"
            due = (not previous or now - _t(previous["sent_at"]) >= REMIND_EVERY
                   or previous.get("kind") != kind)
            if due and send(f"⚠️ CANE DA GUARDIA — {check.name}\n{problem}.\n"
                            f"Controlla: https://github.com/{OWNER}/{check.repo}/actions/workflows/{check.workflow}"):
                alerts[key] = {"problem": problem, "kind": kind, "sent_at": now.isoformat()}
            print(f"{check.name}: PROBLEMA — {problem}")
        else:
            if previous and send(f"✅ CANE DA GUARDIA — {check.name} di nuovo regolare."):
                alerts.pop(key, None)
            print(f"{check.name}: regolare")
    return state


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        state = {}

    def send(text: str) -> bool:
        if args.dry_run:
            print(text)
            return True
        from trump_tracker import send_telegram
        return send_telegram(text)

    state = run(send=send, state=state)
    if not args.dry_run:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
