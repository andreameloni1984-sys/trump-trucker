"""Item-level public feed collector for SPUTNIK."""
from __future__ import annotations
import hashlib
import os
import re
from typing import Any
from sputnik_public_sources import parse_public_feed
from trump_tracker import ASSET_KEYWORDS, fetch_public_document, fetch_public_text, load_state, save_state, utc_now

FEEDS = {
    "WHITE_HOUSE": "https://www.whitehouse.gov/news/feed/",
    "TRUTH_ARCHIVE": "https://www.trumpstruth.org/feed",
}
OGE_URL = "https://www.oge.gov/web/oge.nsf/Open%20Government?OpenView"

def domains_for(text: str) -> list[str]:
    value = str(text or "").lower()
    return [name for name, words in ASSET_KEYWORDS.items()
            if any(re.search(rf"\b{re.escape(word)}\b", value) for word in words)]
