from __future__ import annotations

import json
from datetime import datetime, timezone

BEA_SCHEDULE_URL = "https://www.bea.gov/news/schedule"


def parse_bea_release_dates(text: str) -> list[dict[str, str]]:
    """Normalize the BEA public release_dates JSON into timezone-aware events."""
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError("BEA calendar JSON must be an object")
    events: list[dict[str, str]] = []
    for title, record in payload.items():
        if title == "file_last_updated" or not isinstance(record, dict):
            continue
        dates = record.get("release_dates", [])
        if not isinstance(dates, list):
            continue
        for value in dates:
            try:
                when = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            except ValueError:
                continue
            if when.tzinfo is None:
                continue
            events.append({
                "uid": "bea:" + str(title).strip().lower() + ":" + when.astimezone(timezone.utc).isoformat(),
                "summary": str(title).strip(),
                "start": when.isoformat(),
                "start_params": "",
                "url": BEA_SCHEDULE_URL,
                "source": "BEA",
            })
    return events
