"""SPUTNIK Aggressive: early-opportunity screening, not an auto-trader.

Aggressive means broader/faster candidate surfacing and explicit triggers. It never
weakens price confirmation, invents quotes, or converts a political mention into an order.
"""
from __future__ import annotations

from typing import Any

from sputnik_catalyst import catalyst_watchlist
from sputnik_decision_engine import conditional_plans
from sputnik_ranking import rank_purchase_candidates
from sputnik_cfd import build_conditional_trade_plan


def aggressive_message(state: dict[str, Any]) -> str:
    findings = list((state.get("intelligence_history") or {}).values())
    findings.sort(key=lambda row: str(row.get("detected_at") or ""), reverse=True)
    catalysts = catalyst_watchlist(findings, limit=8)
    transactions = list((state.get("transactions") or {}).values())
    quotes = state.get("market_quotes") or state.get("quotes") or {}
    candidates = rank_purchase_candidates(transactions, limit=5)

    lines = [
        "🔥 SPUTNIK AGGRESSIVO — EARLY OPPORTUNITIES",
        "━━━━━━━━━━━━━━━━━━",
        "Modalità: screening anticipato, soglia WATCH più ampia",
        "Obiettivo: individuare prima i catalizzatori e preparare scenari LONG/SHORT.",
        "",
        "⚡ CATALIZZATORI DA SEGUIRE",
    ]
    if catalysts:
        for i, row in enumerate(catalysts, 1):
            lines.append(
                f"{i}. {row['instrument']} — priorità {row['score']}/100 | PREPARARE"
            )
            lines.append(
                f"   {row['description']} | fonti: {', '.join(row['sources']) or 'N/D'}"
            )
            lines.append(
                "   Trigger: conferma della notizia primaria + prezzo/volume nella direzione attesa."
            )
    else:
        lines.append("Nessun catalizzatore item-level presente nello snapshot.")

    lines.extend(["", "📄 DISCLOSURE / ACQUISTI PUBBLICI"])
    if candidates:
        for row in candidates:
            lines.append(
                f"{row['rank']}. {row['security']} ({row['company']}) — "
                f"{row['score']}/100 | {row['signal']} | filing {row['filings']}"
            )
            lines.append(f"   {row['reason']}")
    else:
        lines.append("Nessun acquisto Form 4 verificabile nel dataset corrente.")

    # Search actual stored source text for strict, explicit policy catalyst plans.
    plans = []
    for finding in findings[:30]:
        text = str(finding.get("text") or finding.get("snippet") or "").strip()
        if text:
            for plan in conditional_plans(text, limit=2):
                plans.append((finding, plan))
    deduped = {}
    for finding, plan in plans:
        deduped.setdefault(plan["id"], (finding, plan))
    lines.extend(["", "🎯 SCENARI CONDIZIONALI"])
    if deduped:
        for finding, plan in list(deduped.values())[:4]:
            lines.append(f"• {plan['event']} → {plan['candidate']} | {plan['bias']}")
            lines.append(f"  Conferma: {plan['confirmation']}")
            lines.append(f"  Invalidazione: {plan['invalidation']}")
            if finding.get("url"):
                lines.append(f"  Fonte: {finding['url']}")
            trade = build_conditional_trade_plan(plan, quotes)
            if trade.get("entry") is not None:
                lines.append(
                    f"  📍 {trade['status']} {trade.get('direction', plan['bias'])} | "
                    f"Prezzo {trade['entry']} | SL {trade['stop']} | "
                    f"TP1 {trade['tp1']} | TP2 {trade['tp2']} | R/R 1:2"
                )
                lines.append(f"  ATR: {trade['atr']} | Quotazione: {trade['quote_time']}")
                lines.append(f"  Nota: {trade['reason']}")
            else:
                lines.append(f"  🟡 SL/TP non calcolabili: {trade['reason']}")
    else:
        lines.append("Nessun testo salvato soddisfa le regole esplicite dei catalizzatori.")

    lines.extend([
        "",
        "⚠️ AGGRESSIVO = ricerca più ampia e anticipata, NON leva più alta né ordini automatici.",
        "Prima di un CFD servono quotazione aggiornata, direzione confermata, Entry, SL, TP e size calcolata sul rischio.",
        "Un segnale politico senza conferma del prezzo resta PREPARARE/WATCH, non TRADE.",
    ])
    return "\n".join(lines)
