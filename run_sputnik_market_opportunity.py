"""SPUTNIK preliminary market-opportunity alerts, PAPER ONLY.

Uses fresh exact-contract 5-minute quotes and the existing permissive early-warning
classifier. It does not invent a news catalyst or submit orders.
"""
from __future__ import annotations

import os
from typing import Any

from run_selected_commodity_alerts import configured_contracts
from sputnik_wti_alert import fetch_intraday, classify_state
from trump_tracker import load_state, save_state, send_telegram


def build_opportunity(quote: dict[str, Any], classification: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    state = classification["state"]
    if state == "LONG IN TENUTA":
        return None

    entry = float(quote["price"])
    volatility = float(classification.get("median_range") or 0)
    if entry <= 0 or volatility <= 0:
        return None

    # A bearish pre-alert: stop is volatility-based; targets are 1R and 2R.
    risk_distance = max(1.5 * volatility, abs(entry) * 0.0005)
    stop = entry + risk_distance
    tp1 = entry - risk_distance
    tp2 = entry - 2 * risk_distance
    if tp2 <= 0:
        return None

    direction = "SHORT (ipotesi preliminare)"
    currency = str(quote.get("currency") or "valuta non verificata")
    name = str(quote.get("name") or quote.get("symbol") or "strumento")
    msg = "\n".join([
        "🛰️ SPUTNIK — OPPORTUNITÀ DI MERCATO",
        "━━━━━━━━━━━━━━━━━━",
        f"📌 Strumento: {name}",
        f"🧭 Direzione: {direction}",
        "⏱️ Orizzonte: INTRADAY",
        "🧪 Modalità: PAPER TRADING",
        f"📰 Catalizzatore: non verificato da questo modulo; lettura tecnica preliminare.",
        f"📡 Fonte prezzo: {quote.get('source', 'N/D')} | contratto: {quote.get('symbol', 'N/D')}",
        f"🕒 Ultima candela: {quote.get('timestamp', 'N/D')} UTC",
        f"💵 Ingresso teorico: {entry:.4f} {currency}",
        f"🛑 Stop loss: {stop:.4f} {currency} (1,5 × range mediano recente)",
        f"🎯 TP1: {tp1:.4f} {currency} | R/R 1:1",
        f"🎯 TP2: {tp2:.4f} {currency} | R/R 1:2",
        f"🔎 Evidenza: {classification.get('evidence', 'N/D')}",
        f"⛔ Invalidazione: {classification.get('invalidation', 'N/D')}",
        f"↔️ Scenario alternativo: {classification.get('alternative', 'N/D')}",
        "⚠️ PRE-ALLARME, non segnale garantito. Verificare spread, liquidità e feed del broker. Nessun ordine inviato.",
    ])
    details = {
        "state": state,
        "symbol": quote.get("symbol"),
        "timestamp": quote.get("timestamp"),
        "entry": entry,
        "stop": stop,
        "tp1": tp1,
        "tp2": tp2,
    }
    return msg, details


def run(state: dict[str, Any]) -> dict[str, str]:
    outcomes: dict[str, str] = {}
    sent_state = state.setdefault("market_opportunity_state", {})
    chat_id = str(state.get("telegram_chat_id") or os.getenv("TELEGRAM_CHAT_ID") or "").strip()

    for key, contract in configured_contracts().items():
        os.environ["SPUTNIK_WTI_CONTRACT"] = contract["symbol"]
        os.environ["SPUTNIK_WTI_EXPIRY"] = contract["expiry"]
        quote = fetch_intraday(contract["symbol"])
        if not quote:
            outcomes[key] = "NO_FRESH_QUOTE"
            continue
        quote["name"] = contract["name"]
        quote["expiry"] = contract["expiry"]
        classification = classify_state(quote.get("bars") or [])
        if not classification:
            outcomes[key] = "NO_CLASSIFICATION"
            continue
        opportunity = build_opportunity(quote, classification)
        if not opportunity:
            outcomes[key] = "NO_EARLY_SETUP"
            continue
        message, details = opportunity
        previous = sent_state.get(key) or {}
        signature = f"{details['state']}|{details['timestamp']}"
        if previous.get("signature") == signature:
            outcomes[key] = "DUPLICATE"
            continue
        if send_telegram(message, chat_id=chat_id or None):
            sent_state[key] = {"signature": signature, **details}
            outcomes[key] = "SENT"
        else:
            outcomes[key] = "SEND_FAILED"

    state["market_opportunity_last_run"] = outcomes
    print("SPUTNIK market opportunities: " + ", ".join(f"{k}={v}" for k, v in outcomes.items()))
    return outcomes


def main() -> None:
    state = load_state()
    run(state)
    save_state(state)


if __name__ == "__main__":
    main()
