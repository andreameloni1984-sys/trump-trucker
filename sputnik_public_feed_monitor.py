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

# Keep macro/political catalyst labels for discovery, but prevent non-selected
# tradable assets from becoming operational commodity candidates.
OPERATIONAL_ASSET_KEYWORDS = {
    "ENERGY": ["oil", "crude", "brent", "wti", "petroleum", "opec", "oilfield", "refinery", "oil supply"],
    "METALS": ["gold", "silver", "copper"],
    "AGRICULTURE": ["corn", "wheat", "soybean"],
    "DEFENSE": ASSET_KEYWORDS["DEFENSE"],
    "AI_TECH": ASSET_KEYWORDS["AI_TECH"],
    "SPACE": ASSET_KEYWORDS["SPACE"],
    "CRYPTO": ASSET_KEYWORDS["CRYPTO"],
    "MEDIA": ASSET_KEYWORDS["MEDIA"],
    "REAL_ESTATE": ASSET_KEYWORDS["REAL_ESTATE"],
    "TRADE_POLICY": ASSET_KEYWORDS["TRADE_POLICY"],
    "RATES_MACRO": ASSET_KEYWORDS["RATES_MACRO"],
}

def domains_for(text: str) -> list[str]:
    value = str(text or "").lower()
    return [
        name for name, words in OPERATIONAL_ASSET_KEYWORDS.items()
        if any(re.search(rf"\\b{re.escape(word)}\\b", value) for word in words)
    ]
