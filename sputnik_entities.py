"""Exact SEC issuer identity helpers; no fuzzy entity matching."""
from __future__ import annotations
import re
import unicodedata

def normalize_cik(value):
    digits = re.sub(r"\D", "", str(value or ""))
    if not digits or len(digits) > 10:
        raise ValueError("CIK non valido")
    return digits.zfill(10)

def normalize_ticker(value):
    ticker = str(value or "").strip().upper()
    return ticker if re.fullmatch(r"[A-Z][A-Z0-9.-]{0,14}", ticker) else ""

def normalize_company_name(value):
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.casefold()
    text = re.sub(r"[^\w]+", " ", text)
    return " ".join(text.split())

def resolve_sec_issuer(cik, company, tickers=()):
    normalized_cik = normalize_cik(cik)
    name = " ".join(str(company or "").split()).strip() or f"CIK {normalized_cik}"
    values = tickers if isinstance(tickers, (list, tuple, set)) else [tickers]
    symbols = sorted({symbol for value in values if (symbol := normalize_ticker(value))})
    return {
        "entity_id": f"sec:cik:{normalized_cik}",
        "cik": normalized_cik,
        "company": name,
        "normalized_company": normalize_company_name(name),
        "ticker": symbols[0] if len(symbols) == 1 else "",
        "tickers": ",".join(symbols),
        "resolution_method": "SEC_CIK_EXACT",
    }
