"""Multi-commodity state-change alert runner for SPUTNIK; PAPER ONLY."""
from __future__ import annotations

import os
from typing import Any

from sputnik_wti_alert import fetch_intraday, classify_state
from trump_tracker import load_state, save_state, send_telegram

# Explicit futures contracts, not continuous symbols. Verify availability from returned
# Yahoo metadata at runtime; unknown/unavailable symbols safely produce no alert.
DEFAULT_CONTRACTS = {
    "GOLD": {"name": "ORO", "symbol": "GCZ26.CMX", "expiry": "2026-12-29"},
    "SILVER": {"name": "ARGENTO", "symbol": "SIZ26.CMX", "expiry": "2026-12-29"},
    "COPPER": {"name": "RAME", "symbol": "HGZ26.CMX", "expiry": "2026-12-29"},
    "WTI": {"name": "PETROLIO WTI", "symbol": "CLZ26.NYM", "expiry": "2026-11-20"},
    "BRENT": {"name": "PETROLIO BRENT", "symbol": "BZZ26.NYM", "expiry": "2026-12-31"},
    "WHEAT": {"name": "GRANO", "symbol": "ZWZ26.CBT", "expiry": "2026-12-14"},
    "CORN": {"name": "MAIS", "symbol": "ZCZ26.CBT", "expiry": "2026-12-14"},
    "SOYBEAN": {"name": "SOIA", "symbol": "ZSZ26.CBT", "expiry": "2026-11-13"},
}


def configured_contracts() -> dict[str, dict[str, str]]:
    """Allow explicit ticker/expiry overrides without guessing a provider symbol."""
    result: dict[str, dict[str, str]] = {}
    for key, default in DEFAULT_CONTRACTS.items():
        symbol = os.getenv(f"SPUTNIK_{key}_CONTRACT", default["symbol"]).strip()
        expiry = os.getenv(f"SPUTNIK_{key}_EXPIRY", default["expiry"]).strip()
        result[key] = {"name": default["name"], "symbol": symbol, "expiry": expiry}
    return result


def run_all(state: dict[str, Any]) -> dict[str, str]:
    outcomes: dict[str, str] = {}
    alert_state = state.setdefault("commodity_state_change_alerts", {})
    chat_id = str(state.get("telegram_chat_id") or os.getenv("TELEGRAM_CHAT_ID") or "").strip()
    for key, contract in configured_contracts().items():
        # Reuse strict quote validation, setting contract-specific environment values.
        os.environ["SPUTNIK_WTI_CONTRACT"] = contract["symbol"]
        os.environ["SPUTNIK_WTI_EXPIRY"] = contract["expiry"]
        quote = fetch_intraday(contract["symbol"])
        if not quote:
            outcomes[key] = "NO_DATA"
            continue
        classification = classify_state(quote.get("bars") or [])
        if not classification:
            outcomes[key] = "NO_DATA"
            continue
        previous = (alert_state.get(key) or {}).get("state")
        current = classification["state"]
        if previous == current:
            outcomes[key] = "UNCHANGED"
            continue
        quote["expiry"] = contract["expiry"]
        quote["name"] = contract["name"]
        delay = int(quote.get("delay_seconds") or 0)
        delay_text = f"ritardo stimato {delay // 60} min" if delay else "timestamp recente"
        message = "\\n".join([
            f"🛰️ SPUTNIK — {contract['name']} / ALERT CAMBIO STATO",
            "━━━━━━━━━━━━━━━━━━",
            f"🚦 STATO: {classification['state']}",
            f"📊 Contratto: {quote['symbol']} | scadenza: {contract['expiry']}",
            f"💵 Prezzo: {float(quote['price']):.4f} {quote.get('currency') or 'valuta non verificata'}",
            f"🕒 Ultima candela: {quote['timestamp']} UTC ({delay_text})",
            f"📡 Fonte: {quote.get('source', 'N/D')} | mercato: {quote.get('exchange', 'N/D')}",
            f"🔎 Evidenze: {classification['evidence']}",
            f"🧱 Supporto intraday calcolato: {classification['support']:.4f}",
            f"🌡️ Range ultima candela: {classification['last_range']:.4f} | mediana recente: {classification['median_range']:.4f}",
            f"⛔ Invalidazione: {classification['invalidation']}",
            f"↔️ Scenario alternativo: {classification['alternative']}",
            "⚠️ Analisi preliminare; PAPER ONLY, nessun ordine inviato.",
        ])
        if send_telegram(message, chat_id=chat_id or None):
            alert_state[key] = {
                "state": current,
                "symbol": quote["symbol"],
                "expiry": contract["expiry"],
                "price": quote["price"],
                "timestamp": quote["timestamp"],
            }
            outcomes[key] = "SENT"
        else:
            outcomes[key] = "SEND_FAILED"
    state["commodity_state_change_last_run"] = outcomes
    print("SPUTNIK commodity state alerts: " + ", ".join(f"{k}={v}" for k, v in outcomes.items()))
    return outcomes


def main() -> None:
    state = load_state()
    run_all(state)
    save_state(state)


if __name__ == "__main__":
    main()
