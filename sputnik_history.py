"""SPUTNIK public administration history and anticipatory selector.

Only documented public roles/events are stored. This is a research memory layer,
not a private-relationship graph and not a claim about motives.
"""
from __future__ import annotations
from collections import Counter
from typing import Any
from sputnik_catalyst import DOMAIN_INSTRUMENTS

CORE_ADMINISTRATION = [
    {"name": "Donald J. Trump", "role": "President", "period": "2025-", "source": "WHITE_HOUSE"},
    {"name": "JD Vance", "role": "Vice President", "period": "2025-", "source": "WHITE_HOUSE"},
    {"name": "Scott Bessent", "role": "Secretary of the Treasury", "period": "2025-", "source": "WHITE_HOUSE"},
    {"name": "Howard Lutnick", "role": "Secretary of Commerce", "period": "2025-", "source": "WHITE_HOUSE"},
    {"name": "Brooke Rollins", "role": "Secretary of Agriculture", "period": "2025-", "source": "WHITE_HOUSE"},
    {"name": "Pete Hegseth", "role": "Secretary of War", "period": "2025-", "source": "WHITE_HOUSE"},
    {"name": "Marco Rubio", "role": "Secretary of State", "period": "2025-", "source": "WHITE_HOUSE"},
    {"name": "Jamieson Greer", "role": "United States Trade Representative", "period": "2025-", "source": "WHITE_HOUSE"},
    {"name": "Stephen Miller", "role": "Deputy Chief of Staff", "period": "2025-", "source": "WHITE_HOUSE"},
    {"name": "Steven Cheung", "role": "Director of Communications", "period": "2025-", "source": "WHITE_HOUSE"},
]

def build_public_history(findings: list[dict[str, Any]], existing: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Append documented public events to a deduplicated historical event ledger."""
    ledger = list(existing or [])
    seen = {str(x.get("event_id") or "") for x in ledger if x.get("event_id")}
    for finding in findings:
        event_id = str(finding.get("event_id") or "")
        if not event_id or event_id in seen:
            continue
        ledger.append({
            "event_id": event_id,
            "source": str(finding.get("source") or "UNKNOWN"),
            "url": str(finding.get("url") or ""),
            "domains": sorted({str(x).upper() for x in (finding.get("domains") or [])}),
            "evidence": str(finding.get("evidence") or ""),
            "status": str(finding.get("status") or ""),
            "detected_at": str(finding.get("detected_at") or ""),
        })
        seen.add(event_id)
    ledger.sort(key=lambda x: str(x.get("detected_at") or ""), reverse=True)
    return ledger

def anticipatory_selector(findings: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    """Select early WATCH candidates from repeated, primary-source public catalysts."""
    if limit <= 0:
        return []
    buckets: dict[str, dict[str, Any]] = {}
    for item in findings:
        source = str(item.get("source") or "UNKNOWN")
        event_id = str(item.get("event_id") or "")
        for domain in item.get("domains") or []:
            key = str(domain).upper()
            row = buckets.setdefault(key, {"domain": key, "events": set(), "sources": set(), "latest": ""})
            if event_id:
                row["events"].add(event_id)
            row["sources"].add(source)
            row["latest"] = max(row["latest"], str(item.get("detected_at") or ""))
    rows = []
    for row in buckets.values():
        events = len(row["events"])
        sources = len(row["sources"])
        primary = bool(row["sources"] & {"WHITE_HOUSE", "OGE", "SEC"})
        score = min(100, 45 + min(25, events * 5) + min(20, sources * 10) + (10 if primary else 0))
        if score < 60:
            continue
        rows.append({
            "domain": row["domain"],
            "instrument": (DOMAIN_INSTRUMENTS.get(row["domain"], [])[0][0] if DOMAIN_INSTRUMENTS.get(row["domain"]) else row["domain"]),
            "alternatives": [code for code, _ in DOMAIN_INSTRUMENTS.get(row["domain"], [])[1:]],
            "score": score,
            "events": events,
            "sources": sorted(row["sources"]),
            "latest": row["latest"],
            "signal": "ANTICIPA",
            "reason": "Catalizzatore pubblico ricorrente: anticipazione da verificare con prezzo/volume prima di un ordine.",
        })
    rows.sort(key=lambda x: (-x["score"], -x["events"], x["domain"]))
    return rows[:limit]
