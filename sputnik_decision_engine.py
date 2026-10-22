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
        "actions": ("blocks", "blocked", "closes", "closed", "disrupts", "disrupted", "interrupts", "interrupted", "attacks", "attacked", "attack", "attacking", "hitting", "hit", "hits", "strike", "strikes", "struck", "escalates", "escalated", "threatens", "threatened", "halts", "halted", "suspends", "suspended", "interrompe", "interrotto", "blocca", "bloccato", "chiude", "chiusura", "attacca", "attaccato", "minaccia", "minacciato"),
        "topics": ("tanker", "shipping", "exports", "export", "supply", "hormuz", "strait", "petrolio", "flussi", "esportazioni", "petroliere", "offerta", "oil prices", "oil price", "saudi arabia", "houthi", "houthis", "diesel", "energy flows"),
    },
}
NEGATIONS = (" never ", "did not", "does not", "do not", "will not", "would not", "was not", "were not", "is not", "are not", "has not", "have not", "had not", "cannot", "can not", "not confirmed", "not yet", "won't", "didn't", "doesn't", "don't", "isn't", "aren't", "wasn't", "weren't", "denied", "rejects", "rejected", "withdrawn", "cancelled", " non ", "nessun", "nega", "smentisce", "ritira", "respinge")

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
    # Older persisted findings contain only domain labels (no text/snippet).
    # Map those labels to a watchlist without inferring direction or a trade.
    domain_topics = [
        (("energy", "petrol", "brent", "wti"), "ENERGIA", "Brent e WTI",
         "L'archivio segnala il settore energia, ma non conserva il testo dell'evento. Verificare una notizia primaria su produzione, trasporti o scorte prima di attribuire una direzione."),
        (("metals", "gold", "silver", "oro", "argento"), "METALLI", "Oro e argento",
         "L'archivio segnala metalli, ma non conserva un catalizzatore specifico. Controllare rendimenti reali, dollaro e reazione dei prezzi."),
        (("agriculture", "corn", "wheat", "sugar", "coffee", "cocoa"), "AGRICOLTURA", "Grano, zucchero e cacao",
         "L'archivio segnala agricoltura, ma non dimostra uno shock dell'offerta. Verificare raccolti, meteo, scorte e prezzi."),
        (("defense", "military", "missile", "difesa"), "DIFESA / GEOPOLITICA", "Settore difesa, petrolio e oro",
         "L'archivio segnala difesa/geopolitica, ma manca un evento verificabile. Controllare comunicati ufficiali e reazione dei prezzi."),
        (("ai_tech", "semiconductor", "technology", "tech"), "TECNOLOGIA", "Nasdaq-100 e semiconduttori",
         "L'archivio segnala tecnologia, ma non identifica una società o un catalizzatore preciso. Verificare l'annuncio originale e la reazione del settore."),
        (("crypto", "bitcoin", "ethereum"), "CRIPTO", "Bitcoin ed Ethereum",
         "L'archivio segnala cripto, ma non identifica un catalizzatore preciso. Verificare la fonte primaria e i prezzi aggiornati."),
        (("real_estate", "property", "immobiliare"), "IMMOBILIARE", "REIT e settore immobiliare",
         "L'archivio segnala immobiliare, ma non dimostra un impatto economico. Verificare tassi, rendimenti e notizia primaria."),
        (("media", "truth", "social"), "MEDIA / SOCIAL", "Titolo o settore citato nella fonte originale",
         "Una menzione su un sito o social non dimostra un investimento né un impatto sul mercato. Recuperare il singolo post o comunicato originale."),
    ]
    for keywords, label, instruments, explanation in [*topics, *domain_topics]:
        if any(word in body for word in keywords):
            return {"topic": label, "instruments": instruments, "explanation": explanation}

    # Always return a transparent operational outcome, even for empty/stale feeds.
    # This is a monitoring result, not a fabricated LONG/SHORT recommendation.
    return {
        "topic": "DATI INSUFFICIENTI — MONITORAGGIO OPERATIVO",
        "instruments": "Nasdaq-100, oro, Brent e USD",
        "explanation": "Non è stato recuperato un catalizzatore specifico. Questi strumenti sono una watchlist generale, non una previsione direzionale. Prossimo passo: recuperare una notizia item-level da fonte primaria e verificare prezzo e volume prima di valutare LONG o SHORT.",
    }


def _aggressive_candidates(text: str) -> list[dict[str, str]]:
    """Broader early-opportunity screen; directions are hypotheses, not confirmed trades."""
    body = " ".join(str(text or "").lower().split())
    candidates: list[dict[str, str]] = []
    rules = [
        (("tariff", "tariffs", "dazi", "trade war", "import duty", "import duties"),
         ("ORO (XAU/USD)", "LONG preliminare", "Dazi/tensioni commerciali possono aumentare la domanda difensiva; verificare USD e rendimenti reali."),
          ("NASDAQ-100", "SHORT preliminare", "L'escalation commerciale può pesare sulle aspettative di crescita e sui titoli growth; verificare futures e ampiezza di mercato.")),
        (("trade deal", "trade agreement", "tariff pause", "pause tariffs", "accordo commerciale", "dazi sospesi", "negoziati commerciali"),
         ("NASDAQ-100", "LONG preliminare", "Una distensione commerciale può sostenere gli asset rischiosi; verificare che l'accordo sia concreto e che i futures confermino."),
          ("ORO (XAU/USD)", "SHORT preliminare", "Una riduzione del rischio può indebolire la domanda difensiva; USD e rendimenti possono però invertire la reazione.")),
        (("hormuz", "oil supply", "oil exports", "crude", "brent", "wti", "iran", "tanker", "petroleum", "petrolio", "diesel", "shipping", "petroliere"),
         ("BRENT (petrolio)", "LONG preliminare", "Un rischio concreto ai flussi fisici può sostenere il greggio; distinguere minacce da interruzioni effettive."),
          ("ORO (XAU/USD)", "LONG preliminare", "Un aumento del rischio geopolitico può sostenere i beni rifugio; verificare USD e rendimenti.")),
        (("fed", "federal reserve", "interest rate", "rates", "inflation", "inflazione", "tassi", "rendimenti", "treasury"),
         ("ORO (XAU/USD)", "DIREZIONE DA DETERMINARE", "Tassi e inflazione possono muovere l'oro in direzioni opposte: distinguere sorpresa hawkish/dovish e controllare rendimenti reali."),
          ("NASDAQ-100", "DIREZIONE DA DETERMINARE", "La sorpresa sui tassi può muovere i titoli growth; valutare il contenuto preciso e la reazione dei Treasury.")),
        (("missile", "military strike", "defense spending", "defence spending", "military operation", "defense contract", "guerra", "attacco", "sanzioni", "sanctions"),
         ("SETTORE DIFESA (ETF/azioni liquide)", "LONG preliminare", "Escalation o spesa militare può sostenere il settore, ma la reazione dipende da contratti, aspettative e prezzo già scontato."),
          ("BRENT (petrolio)", "LONG preliminare", "Rischi geopolitici possono aumentare il premio sul greggio se coinvolgono aree o rotte energetiche.")),
        (("semiconductor", "semiconductors", "artificial intelligence", " ai ", "chip", "technology stocks", "nasdaq"),
         ("NASDAQ-100 / SEMICONDUTTORI", "DIREZIONE DA DETERMINARE", "Il tema può creare opportunità nel settore tech; servono nome della società, dettaglio dell'evento e reazione del mercato.")),
    ]
    for rule in rules:
        keywords = rule[0]
        if any(word in body for word in keywords):
            for item in rule[1:]:
                candidate, bias, reason = item
                if not any(row["candidate"] == candidate for row in candidates):
                    candidates.append({"candidate": candidate, "bias": bias, "reason": reason})
    return candidates[:5]


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
            f"✅ Conferma richiesta: {plan['confirmation']}",
            f"🛑 Annulla lo scenario se: {plan['invalidation']}",
            "",
            "In parole semplici: prepara lo strumento, ma entra solo se la notizia è confermata e il mercato dà il segnale richiesto.",
            "Prezzi, stop e obiettivi non vengono inventati: servono quotazioni aggiornate.",
        ])
        aggressive = [row for row in _aggressive_candidates(text) if row["candidate"] != plan["candidate"]]
        if aggressive:
            lines.extend(["", "⚡ ALTRI SETUP ANTICIPATI (screening aggressivo)"])
            for row in aggressive[:3]:
                lines.extend([
                    f"• {row['candidate']} — {row['bias']}",
                    f"  Tesi: {row['reason']}",
                ])
            lines.append("Scenari anticipati: possibili falsi positivi; verificare fonte e prezzi.")
        return "\n".join(lines)

    aggressive = _aggressive_candidates(text)
    if aggressive:
        lines.extend([
            "⚡ RISULTATO: EARLY OPPORTUNITIES — SCREENING AGGRESSIVO",
            "Le direzioni sotto sono ipotesi iniziali: più opportunità, meno filtro, nessuna certezza.",
            "",
        ])
        for index, row in enumerate(aggressive, 1):
            lines.extend([
                f"{index}. 🎯 Strumento: {row['candidate']}",
                f"➡️ Direzione preliminare: {row['bias']}",
                f"🧠 Tesi: {row['reason']}",
                "✅ Conferma: verificare la notizia originale e la reazione di prezzo/volume.",
                "🛑 Invalidazione: reazione contraria, notizia smentita o catalizzatore già scontato.",
                "",
            ])
        lines.append("Entry, stop e target richiedono quotazioni aggiornate: non vengono inventati.")
        return "\n".join(lines)

    fallback = _fallback_watch(text)
    if fallback:
        lines.extend([
            "🟡 RISULTATO: WATCHLIST AMPIA",
            f"📌 Tema: {fallback['topic']}",
            f"👀 Strumenti da tenere d'occhio: {fallback['instruments']}",
            f"🧠 Perché: {fallback['explanation']}",
            "✅ Prossimo passo: verificare fonte originale e prezzi.",
            "⚠️ Screening aggressivo: tema da approfondire, non ancora una direzione affidabile.",
        ])
    else:
        lines.extend([
            "🟡 RISULTATO: FEED SENZA CATALIZZATORE RICONOSCIBILE",
            "La notizia non è abbastanza specifica per una tesi direzionale; controllare il feed e recuperare il contenuto dell'evento.",
        ])
    return "\n".join(lines)
