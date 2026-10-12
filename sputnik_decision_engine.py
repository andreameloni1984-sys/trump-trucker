"""Strict SPUTNIK catalyst gate. It returns conditional plans, never orders."""
from __future__ import annotations
import re
from typing import Any
from sputnik_decision import SCENARIOS as BASE_SCENARIOS

RULES = {
    "tariff_escalation": {
        "actions": ("impose", "imposes", "imposed", "imposing", "announce", "announces", "announced", "raise", "raises", "raised", "increase", "increases", "increased", "introduce", "introduced", "levies", "implement", "implemented", "annuncia", "annunciato", "aumenta", "aumentati", "imporre", "applica"),
        "topics": ("tariff", "import dut", "dazi"),
    },
    "trade_deescalation": {
        "actions": ("signed", "signs", "reached", "reach", "agreed", "agrees", "announced", "announce", "finalized", "firmato", "raggiunto", "concordato", "suspended", "suspends", "paused", "pause", "sospende", "sospesi", "proroga", "estende"),
        "topics": ("trade deal", "trade agreement", "accordo commerciale", "intesa commerciale", "tariff pause", "pausa sui dazi", "dazi", "tariff"),
    },
    "oil_supply_disruption": {
        "actions": ("blocks", "blocked", "closes", "closed", "disrupts", "disrupted", "interrupts", "interrupted", "attacks", "attacked", "threatens", "threatened", "halts", "halted", "suspends", "suspended", "interrompe", "interrotto", "blocca", "bloccato", "chiude", "chiusura", "attacca", "attaccato", "minaccia", "minacciato"),
        "topics": ("tanker", "shipping", "exports", "export", "supply", "hormuz", "strait", "petrolio", "flussi", "esportazioni", "petroliere", "offerta"),
    },
}
NEGATIONS = (" not ", " never ", "did not", "does not", "do not", "will not", "would not", "won't", "denied", "rejects", "rejected", "withdrawn", "cancelled", " non ", "nessun", "nega", "smentisce", "ritira", "respinge")

def _sentences(text: str) -> list[str]:
    normalized = str(text or "").replace("?", ".").replace("!", ".")
    parts = []
    for line in normalized.splitlines():
        parts.extend(line.split("."))
    return [" ".join(part.lower().split()) for part in parts if part.strip()]

def _evidence(text: str, rule: dict[str, tuple[str, ...]]) -> str:
    for sentence in _sentences(text):
        padded = " " + sentence + " "
        if any(term in padded for term in NEGATIONS):
            continue
        if any(action in sentence for action in rule["actions"]) and any(topic in sentence for topic in rule["topics"]):
            return sentence[:320]
    return ""

def conditional_plans(text: str, limit: int = 3) -> list[dict[str, Any]]:
    if not str(text or "").strip() or limit <= 0:
        return []
    rows = []
    for scenario in BASE_SCENARIOS:
        rule = RULES.get(scenario["id"])
        if not rule:
            continue
        evidence = _evidence(text, rule)
        if not evidence:
            continue
        hits = [term for term in scenario.get("trigger", ()) if term in str(text).lower()]
        row = {key: value for key, value in scenario.items() if key != "trigger"}
        row.update(matched_terms=hits, match_count=len(hits), evidence=evidence)
        rows.append(row)
    rows.sort(key=lambda row: (row["match_count"], row["id"]), reverse=True)
    return rows[:limit]

def decision_message(text: str, source: str = "Fonte pubblica") -> str:
    plans = conditional_plans(text)
    lines = ["🛰️ SPUTNIK — RISULTATO OPERATIVO", "━━━━━━━━━━━━━━━━━━", f"📰 Fonte analizzata: {source}", ""]
    if not plans:
        lines.extend(["🟡 NESSUN CATALIZZATORE OPERATIVO RILEVATO", "Serve un'azione concreta nella singola notizia, non una semplice menzione.", "Non genero un piano quando il testo non supera il filtro."])
        return "\n".join(lines)
    for index, plan in enumerate(plans, 1):
        lines.extend([f"{index}. 🎯 {plan['event']}", f"➡️ Strumento da preparare: {plan['candidate']}", f"📈 Scenario: {plan['bias']}", f"🧾 Evidenza rilevata: {plan['evidence']}", f"🧭 REGOLA: {plan['if_then']}", f"✅ Conferma richiesta: {plan['confirmation']}", f"🛑 Annulla lo scenario se: {plan['invalidation']}", f"📎 Qualità della fonte: {plan['source_quality']}", ""])
    lines.extend(["⚠️ Piano condizionale, non ordine immediato.", "Entry, stop-loss, target e size richiedono quotazioni aggiornate e verificabili."])
    return "\n".join(lines)
