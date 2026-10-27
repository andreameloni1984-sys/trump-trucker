"""Conditional decision engine: translate public policy catalysts into testable market plans.

Signals are conditional watch plans, not guaranteed predictions or automatic orders.
A plan is activated only after the stated catalyst and market confirmation are observed.
"""
from __future__ import annotations

from typing import Any

SCENARIOS = [
    {
        "id": "tariff_escalation",
        "trigger": ("tariff", "tariffs", "trade war", "import duties", "dazi"),
        "event": "Escalatione commerciale / nuovi dazi",
        "candidate": "ORO (XAU/USD)",
        "bias": "LONG condizionale",
        "if_then": "Se viene annunciato un aumento concreto dei dazi e oro rompe una resistenza intraday con USD non in forte rialzo, valutare LONG sull'oro.",
        "confirmation": "Annuncio ufficiale + rottura confermata su prezzo/volume; controllare DXY e rendimenti reali.",
        "invalidation": "Nessuna rottura, USD e rendimenti in rialzo, oppure annuncio ritirato/rinviato.",
        "source_quality": "Catalizzatore politico da verificare su fonte primaria; prezzo non incluso.",
    },
    {
        "id": "trade_deescalation",
        "trigger": ("trade deal", "trade agreement", "tariff pause", "pause tariffs", "dazi sospesi", "accordo commerciale"),
        "event": "De-escalation commerciale / accordo o pausa dei dazi",
        "candidate": "NASDAQ-100 (indice/CFD)",
        "bias": "LONG condizionale",
        "if_then": "Se una pausa/accordo commerciale è confermata ufficialmente e Nasdaq supera il massimo della sessione con futures in rialzo, valutare LONG sul Nasdaq-100.",
        "confirmation": "Conferma ufficiale + breakout del massimo intraday; verificare ampiezza del mercato e futures.",
        "invalidation": "Accordo non confermato, breakout fallito o nuova escalation.",
        "source_quality": "Catalizzatore politico da verificare su fonte primaria; prezzo non incluso.",
    },
    {
        "id": "oil_supply_disruption",
        "trigger": ("hormuz", "oil supply", "oil exports", "crude", "brent", "wti", "iran", "tanker", "petroleum"),
        "event": "Rischio di interruzione dell'offerta energetica",
        "candidate": "BRENT (petrolio)",
        "bias": "LONG condizionale",
        "if_then": "Se la notizia documenta un rischio concreto per i flussi fisici di petrolio e Brent rompe il massimo intraday, valutare LONG sul Brent.",
        "confirmation": "Fonte ufficiale/agenzia affidabile + breakout del prezzo; verificare scorte, spread Brent-WTI e conferme indipendenti.",
        "invalidation": "Flussi normali, notizia smentita, prezzo che rientra sotto il livello di breakout.",
        "source_quality": "Tema energia rilevato; serve verificare che la notizia riguardi davvero l'offerta fisica.",
    },
    {
        "id": "oil_diplomatic_deescalation",
        "trigger": ("peace talks", "diplomatic efforts", "ease hostilities", "easing tensions", "diplomatic breakthrough", "prevent escalation", "negoziati di pace", "distensione diplomatica"),
        "event": "Possibile de-escalation geopolitica che riduce il premio di rischio sul petrolio",
        "candidate": "WTI (petrolio USA)",
        "bias": "SHORT condizionale",
        "if_then": "Con progressi diplomatici credibili, si può valutare un ingresso anticipato esplorativo SHORT anche prima del breakout, con size ridotta e stop definito; la rottura del minimo con pressione di vendita è una conferma aggiuntiva, non un requisito assoluto.",
        "confirmation": "Preferibile: conferma indipendente della notizia e pressione di vendita. Il breakout del minimo aumenta la confidenza ma non è obbligatorio per un ingresso esplorativo; verificare sempre i rischi di nuove interruzioni dell'offerta.",
        "invalidation": "Nuovi attacchi alle infrastrutture o alle rotte, smentita dei progressi diplomatici, oppure recupero del livello di rottura.",
        "source_quality": "La diplomazia può ridurre il premio di rischio, ma l'effetto è condizionale e può essere compensato da interruzioni dell'offerta.",
    },
    {
        "id": "defense_escalation",
        "trigger": ("missile", "military strike", "defense spending", "defence spending", "military operation", "defense contract"),
        "event": "Escalation militare o spesa/commessa difesa",
        "candidate": "SETTORE DIFESA (ETF/azioni liquide)",
        "bias": "LONG condizionale",
        "if_then": "Se viene confermata una nuova commessa o un'escalation con impatto concreto sulla spesa e il settore rompe la resistenza, valutare LONG su uno strumento liquido del settore difesa.",
        "confirmation": "Comunicazione ufficiale/contratto verificato + conferma di prezzo e volumi.",
        "invalidation": "Nessun impatto su spesa/commesse o breakout fallito.",
        "source_quality": "Tema geopolitico rilevato; non equivale a un ordine di acquisto.",
    },
]

def conditional_plans(text: str, limit: int = 3) -> list[dict[str, Any]]:
    body = " ".join(str(text or "").lower().split())
    if not body:
        return []
    matches = []
    for scenario in SCENARIOS:
        hits = [word for word in scenario["trigger"] if word in body]
        if hits:
            matches.append({**scenario, "matched_terms": hits, "match_count": len(hits)})
    matches.sort(key=lambda row: (row["match_count"], row["id"]), reverse=True)
    return matches[:max(0, limit)]

def decision_message(text: str, source: str = "Fonte pubblica") -> str:
    plans = conditional_plans(text)
    lines = ["🛰️ SPUTNIK — RISULTATO OPERATIVO", "━━━━━━━━━━━━━━━━━━", f"📰 Fonte analizzata: {source}", ""]
    if not plans:
        lines.extend([
            "🟡 NESSUN TRADE CONDIZIONALE ATTIVATO",
            "Il testo non contiene un catalizzatore riconosciuto con regole esplicite.",
            "Non trasformo una semplice menzione in un acquisto.",
        ])
        return "\n".join(lines)
    for i, plan in enumerate(plans, 1):
        lines.extend([
            f"{i}. 🎯 {plan['event']}",
            f"➡️ Strumento da preparare: {plan['candidate']}",
            f"📈 Scenario: {plan['bias']}",
            f"🧭 REGOLA: {plan['if_then']}",
            f"✅ Conferma richiesta: {plan['confirmation']}",
            f"🛑 Annulla lo scenario se: {plan['invalidation']}",
            f"📎 Affidabilità: {plan['source_quality']}",
            "",
        ])
    lines.extend([
        "⚠️ È un piano condizionale, non un ordine immediato.",
        "Entry, stop-loss, target e size vanno calcolati solo con quotazioni aggiornate e verificabili.",
    ])
    return "\n".join(lines)
