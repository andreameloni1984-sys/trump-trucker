"""Read-only Trading 212 INVEST Demo instrument metadata."""
import base64
import json
import os
import re
from urllib.request import Request, urlopen

URL = "https://demo.trading212.com/api/v0/equity/metadata/instruments"


def load_catalog():
    key = os.getenv("SPUTNIK_INVEST_DEMO_API_KEY")
    secret = os.getenv("SPUTNIK_INVEST_DEMO_API_SECRET")
    if not key or not secret:
        print("INVEST Demo: credenziali catalogo assenti, negoziabilità non verificata.")
        return None
    token = base64.b64encode(f"{key}:{secret}".encode()).decode()
    try:
        request = Request(URL, headers={"Authorization": f"Basic {token}"})
        with urlopen(request, timeout=10) as response:
            rows = json.load(response)
        if not isinstance(rows, list) or not rows:
            raise ValueError("catalogo vuoto o non valido")
        catalog = {}
        for row in rows:
            code = row["ticker"]
            match = re.fullmatch(r"([A-Z][A-Z0-9.-]{0,9})_US_EQ", code)
            if not match or row["type"] not in {"STOCK", "ETF"} or row["currencyCode"] != "USD":
                continue
            symbol = match[1].replace(".", "-")
            catalog.setdefault(symbol, []).append(row)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"INVEST Demo: catalogo indisponibile ({type(exc).__name__}).")
        return None
    verified = {symbol: records[0] for symbol, records in catalog.items() if len(records) == 1}
    print(f"INVEST Demo: {len(rows)} record, {len(verified)} simboli USA univoci.")
    return verified
