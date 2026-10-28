"""State-change WTI futures alert for SPUTNIK.

Uses one explicitly named Yahoo Finance futures contract (never CL=F continuous).
No quote or technical level is emitted unless its timestamp and exact symbol are present.
"""
from __future__ import annotations

import json
import os
import statistics
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable

DEFAULT_SYMBOL = "CLZ26.NYM"
DEFAULT_EXPIRY = "2026-11-20"
YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/"


def fetch_intraday(symbol: str | None = None, now: datetime | None = None) -> dict[str, Any] | None:
    """Fetch 5-minute bars for the exact contract symbol; reject stale/mismatched data."""
    symbol = str(symbol or os.getenv("SPUTNIK_WTI_CONTRACT", DEFAULT_SYMBOL)).strip()
    if not symbol or symbol.upper() in {"CL=F", "WTI=F"}:
        return None
    expiry = str(os.getenv("SPUTNIK_WTI_EXPIRY", DEFAULT_EXPIRY)).strip()
    url = YAHOO_CHART + urllib.parse.quote(symbol, safe="") + "?range=1d&interval=5m"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 SPUTNIK WTI state monitor", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        print(f"SPUTNIK WTI: quotazione non disponibile ({type(exc).__name__}).")
        return None

    chart = payload.get("chart") or {}
    result = (chart.get("result") or [])
    if chart.get("error") or not result:
        return None
    row = result[0]
    meta = row.get("meta") or {}
    returned_symbol = str(meta.get("symbol") or "").upper()
    if returned_symbol != symbol.upper():
        return None
    timestamps = row.get("timestamp") or []
    indicators = row.get("indicators") or {}
    quote_rows = ((indicators.get("quote") or [{}])[0])
    opens, highs, lows, closes = (quote_rows.get(k) or [] for k in ("open", "high", "low", "close"))
    bars = []
    for i, epoch in enumerate(timestamps):
        try:
            values = [opens[i], highs[i], lows[i], closes[i]]
            if any(value is None for value in values):
                continue
            bars.append({
                "timestamp": datetime.fromtimestamp(int(epoch), timezone.utc).isoformat(),
                "epoch": int(epoch),
                "open": float(values[0]), "high": float(values[1]),
                "low": float(values[2]), "close": float(values[3]),
            })
        except (IndexError, TypeError, ValueError, OSError):
            continue
    if len(bars) < 8:
        return None
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    age_seconds = now.timestamp() - bars[-1]["epoch"]
    max_age = int(os.getenv("SPUTNIK_WTI_MAX_QUOTE_AGE_SECONDS", "1200"))
    if age_seconds < -120 or age_seconds > max_age:
        print(f"SPUTNIK WTI: ultima candela troppo vecchia/futura ({int(age_seconds)}s); nessun alert.")
        return None
    return {
        "symbol": symbol,
        "expiry": expiry,
        "currency": str(meta.get("currency") or "USD"),
        "exchange": str(meta.get("exchangeName") or "N/D"),
        "price": bars[-1]["close"],
        "timestamp": bars[-1]["timestamp"],
        "delay_seconds": max(0, int(age_seconds)),
        "bars": bars[-60:],
        "source": "Yahoo Finance chart API",
    }


def classify_state(bars: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Classify early weakness vs confirmed breakdown from the same 5m series."""
    if len(bars) < 8:
        return None
    recent = bars[-1]
    prior = bars[-13:-1]
    if len(prior) < 6:
        return None
    support = min(row["low"] for row in prior)
    ranges = [max(0.0, row["high"] - row["low"]) for row in bars[-14:-2]]
    median_range = statistics.median(ranges) if ranges else 0.0
    last_range = recent["high"] - recent["low"]
    # An early warning needs only one observable, reproducible weakness signal.
    lower_highs = bars[-1]["high"] < bars[-2]["high"] and bars[-2]["high"] < bars[-3]["high"]
    lower_lows = bars[-1]["low"] < bars[-2]["low"] and bars[-2]["low"] < bars[-3]["low"]
    wide_bearish = (
        recent["close"] < recent["open"]
        and median_range > 0
        and last_range >= 1.5 * median_range
    )
    # Repeated support tests: two of the last five lows within 0.15% of support.
    support_tests = sum(
        1 for row in bars[-5:]
        if abs(row["low"] - support) <= max(abs(support) * 0.0015, 0.01)
    )
    broken = recent["close"] < support
    failed_recovery = (
        len(bars) >= 2
        and bars[-2]["close"] < support
        and recent["close"] < support
    )
    confirmed = broken and failed_recovery and lower_lows
    if confirmed:
        state = "INVERSIONE CONFERMATA"
        evidence = "Due chiusure consecutive sotto il supporto calcolato e minimi discendenti."
    elif broken or lower_highs or lower_lows or wide_bearish or support_tests >= 2:
        state = "PRE-ALLARME DI POSSIBILE INVERSIONE"
        signals = []
        if broken:
            signals.append("chiusura sotto il supporto intraday")
        if lower_highs:
            signals.append("tre massimi consecutivi discendenti")
        if lower_lows:
            signals.append("tre minimi consecutivi discendenti")
        if wide_bearish:
            signals.append("candela ribassista ampia rispetto alla mediana delle 12 barre precedenti")
        if support_tests >= 2:
            signals.append("test ripetuti del supporto")
        evidence = "; ".join(signals)
    else:
        state = "LONG IN TENUTA"
        evidence = "Nessuna prova precoce di perdita di momentum rilevata nelle barre disponibili."
    return {
        "state": state,
        "evidence": evidence,
        "support": round(support, 4),
        "median_range": round(median_range, 4),
        "last_range": round(last_range, 4),
        "invalidation": (
            "Recupero e mantenimento sopra il supporto intraday, con massimi/minimi crescenti."
            if state != "LONG IN TENUTA"
            else "Un massimo fallito, una candela ribassista ampia o la perdita del supporto attiva il pre-allarme."
        ),
        "alternative": (
            "Il catalizzatore Iran può continuare a sostenere l'offerta/rischio geopolitico e favorire un nuovo massimo."
            if state != "INVERSIONE CONFERMATA"
            else "Un recupero stabile del supporto rotto annullerebbe la conferma ribassista."
        ),
    }


def build_alert(quote: dict[str, Any], classification: dict[str, Any]) -> str:
    delay = int(quote.get("delay_seconds") or 0)
    delay_text = f"ritardo stimato {delay // 60} min" if delay else "timestamp recente"
    return "\n".join([
        "🛰️ SPUTNIK — WTI / ALERT CAMBIO STATO",
        "━━━━━━━━━━━━━━━━━━",
        f"🚦 STATO: {classification['state']}",
        f"🛢️ Contratto: {quote['symbol']} | scadenza: {quote['expiry']}",
        f"💵 Prezzo: {float(quote['price']):.3f} USD/barile",
        f"🕒 Ultima candela: {quote['timestamp']} UTC ({delay_text})",
        f"📡 Fonte: {quote.get('source', 'N/D')} | mercato: {quote.get('exchange', 'N/D')}",
        f"🔎 Evidenze: {classification['evidence']}",
        f"🧱 Supporto intraday calcolato: {classification['support']:.3f} USD",
        f"🌡️ Range ultima candela: {classification['last_range']:.3f} | mediana barre recenti: {classification['median_range']:.3f} USD",
        f"⛔ Invalidazione: {classification['invalidation']}",
        f"↔️ Scenario alternativo: {classification['alternative']}",
        "⚠️ Analisi tecnica preliminare; PAPER ONLY, nessun ordine inviato.",
    ])


def check_and_send(
    state_store: dict[str, Any],
    send_func: Callable[[str], bool],
    quote: dict[str, Any] | None = None,
) -> str:
    """Send only on status changes. Persist state only after Telegram accepts the message."""
    quote = quote if quote is not None else fetch_intraday()
    if not quote:
        print("SPUTNIK WTI: nessun alert; contratto/quotazione intraday non verificabili.")
        return "NO_DATA"
    classification = classify_state(quote.get("bars") or [])
    if not classification:
        return "NO_DATA"
    previous = (state_store.get("wti_state_change_alert") or {}).get("state")
    current = classification["state"]
    if previous == current:
        print(f"SPUTNIK WTI: stato invariato ({current}); nessun duplicato Telegram.")
        return "UNCHANGED"
    message = build_alert(quote, classification)
    if not send_func(message):
        print("SPUTNIK WTI: Telegram non ha confermato l'invio; stato non aggiornato.")
        return "SEND_FAILED"
    state_store["wti_state_change_alert"] = {
        "state": current,
        "symbol": quote["symbol"],
        "expiry": quote["expiry"],
        "price": quote["price"],
        "timestamp": quote["timestamp"],
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
    print(f"SPUTNIK WTI: alert accettato da Telegram; nuovo stato={current}.")
    return "SENT"
