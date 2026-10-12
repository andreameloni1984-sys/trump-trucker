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

def _fallback_watch(text: str) -> dict[str, str] | None:
    """Broad watch mode: always return a useful result without turning mentions into trades."""
    body = " ".join(str(text or "").lower().split())
    topics = [
        (("tariff", "tariffs", "dazi", "trade war", "trade deal", "accordo commerciale"),
         "COMMERCIO / DAZI", "NASDAQ-100 e oro", "Una notizia commerciale può muovere sia gli asset rischiosi sia i beni rifugio; la direzione dipende dai dettagli e dalla reazione dei prezzi."),
        (("oil", "petrol", "brent", "wti", "hormuz", "iran", "tanker", "petrolio", "energia"),
         "PETROLIO / OFFERTA ENERGETICA", "Brent e WTI", "Il petrolio è da monitorare se la notizia riguarda davvero produzione, trasporti o flussi fisici; una semplice menzione non prova una carenza."),
        (("fed", "federal reserve", "interest rate", "rates", "inflation", "inflazione", "tassi", "rendimenti", "treasury", "dollar", "dollaro"),
         "TASSI / DOLLARO", "USD, Treasury e Nasdaq", "La reazione dipende da come cambiano le aspettative sui tassi; verificare rendimenti e dollaro prima di concludere la direzione."),
        (("defense", "defence", "military", "missile", "war", "guerra", "difesa", "militare", "sanction", "sanzioni"),
         "GEOPOLITICA / DIFESA", "Settore difesa, petrolio e oro", "L'impatto dipende da conseguenze concrete su spesa, approvvigionamenti e rischio; non basta il tono della notizia."),
        (("sec", "form 4", "insider", "shares", "stock", "azioni", "ogE", "ethics", "disclosure"),
         "DISCLOSURE / SOCIETÀ", "Titolo citato nella disclosure, se identificabile", "Distinguere operazioni effettivamente documentate da opzioni, piani, intenzioni o semplici menzioni."),
    ]
    for keywords, label, instruments, explanation in topics:
        if any(word in body for word in keywords):
            return {"topic": label, "instruments": instruments, "explanation": explanation}
    return None


def decision_message(text: str, source: str = "Fonte pubblica") -> str:
    plans = conditional_plans(text)
    lines = [
        "🛰️ SPUTNIK — COSA SIGNIFICA",
        "━━━━━━━━━━━━━━━━━━",
        f"📰 Fonte: {source}",
        "",
    ]
    if plans:
        plan = plans[0]
        lines.extend([
            "🎯 RISULTATO: SCENARIO DA PREPARARE",
            f"📌 Evento: {plan['event']}",
            f"👀 Da osservare: {plan['candidate']}",
            f"➡️ Possibile direzione: {plan['bias']}",
            f"🧾 Perché: {plan.get('evidence', 'Catalizzatore rilevato nel testo')}",
            f"✅ Per agire: {plan['confirmation']}",
            f"🛑 Scenario da scartare se: {plan['invalidation']}",
            "",
            "In parole semplici: prepara lo strumento, ma entra solo se la notizia è confermata e il mercato dà il segnale richiesto.",
            "Prezzi, stop e obiettivi non vengono inventati: servono quotazioni aggiornate.",
        ])
        return "\n".join(lines)

    fallback = _fallback_watch(text)
    if fallback:
        lines.extend([
            "🟡 RISULTATO: MONITORARE, NON IGNORARE",
            f"📌 Tema: {fallback['topic']}",
            f"👀 Strumenti da tenere d'occhio: {fallback['instruments']}",
            f"🧠 Perché: {fallback['explanation']}",
            "✅ Prossimo passo: controllare la fonte originale e la reazione dei prezzi.",
            "🛑 Non comprare o vendere soltanto perché il tema è menzionato.",
            "",
            "In parole semplici: SPUTNIK ha individuato un tema utile, ma nel testo non c'è ancora una prova abbastanza concreta per indicare una direzione.",
        ])
    else:
        lines.extend([
            "🟡 RISULTATO: NESSUN CATALIZZATORE CHIARO",
            "Il testo non contiene un evento riconoscibile collegato in modo affidabile a un mercato.",
            "Azione pratica: non forzare un acquisto; attendere una notizia identificabile o dati di mercato pertinenti.",
        ])
    return "\n".join(lines)
