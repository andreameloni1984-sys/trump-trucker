"""Strict SPUTNIK catalyst gate. It returns conditional plans, never orders."""
from __future__ import annotations
import re
from typing import Any
from sputnik_decision import SCENARIOS as BASE_SCENARIOS

RULES = {
    "tariff_escalation": {
        "actions": ("impose", "imposes", "imposed", "imposing", "announce", "announces", "announced", "raise", "raises", "raised", "increase", "increases", "increased", "introduce", "introduced", "levies", "implement", "implemented", "annuncia", "annunciato", "aumenta", "aumentati", "imporre", "applica"),
        "topics": ("tariff", "tariffs", "import dut", "import duties", "dazi"),
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
    normalized = str(text or "").replace("?", ".").replace("!", ".").replace(";", ".")
    parts = []
    for line in normalized.splitlines():
        parts.extend(line.split("."))
    return [" ".join(part.lower().split()) for part in parts if part.strip()]

def _contains_term(text: str, term: str) -> bool:
    """Match a whole word/phrase, not a substring inside an unrelated word."""
    return re.search(rf"(?<!\w){re.escape(term.lower())}(?!\w)", text.lower()) is not None


def _evidence(text: str, rule: dict[str, tuple[str, ...]]) -> str:
    for sentence in _sentences(text):
        # Match negation tokens as whole words, including when punctuation
        # touches the token (for example, an em dash after "never").
        if any(_contains_term(sentence, term.strip()) for term in NEGATIONS):
            continue
        if any(_contains_term(sentence, action) for action in rule["actions"]) and any(_contains_term(sentence, topic) for topic in rule["topics"]):
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


def decision_message(text: str, source: str = "Fonte pubblica", quotes: dict[str, Any] | None = None) -> str:
    """Render one Telegram-ready market opportunity; never fabricate quote-based levels."""
    from sputnik_cfd import build_conditional_trade_plan

    plans = conditional_plans(text, limit=1)
    lines = [
        "🛰️ SPUTNIK — OPPORTUNITÀ DI MERCATO",
        "━━━━━━━━━━━━━━━━━━",
    ]
    if not plans:
        fallback = _fallback_watch(text)
        lines.extend([
            "",
            "🎯 STRUMENTO: da identificare",
            "🟡 DIREZIONE: WAIT — catalizzatore non abbastanza specifico",
            "⏱️ ORIZZONTE: INTRADAY",
            "🧪 MODALITÀ: PAPER TRADING",
            "",
            "━━━━━━━━━━━━━━━━━━",
            "📰 1. CATALIZZATORE",
            str(text or "Nessun testo evento disponibile")[:700],
            "",
            "📊 2. OPERAZIONE IPOTETICA",
            "• Entrata / stop loss / take profit: non calcolabili senza strumento, quotazione aggiornata e ATR.",
            "",
            "🧠 4. DECISIONE SPUTNIK",
            f"Stato: IN ATTESA DI CATALIZZATORE E QUOTAZIONI",
            f"Da monitorare: {fallback['instruments'] if fallback else 'mercati pertinenti alla notizia'}",
            f"Motivo: {fallback['explanation'] if fallback else 'Il testo non identifica un evento collegabile con sufficiente affidabilità a uno strumento.'}",
            "",
            f"🔎 Fonte: {source}",
            "⚠️ Ipotesi sperimentale. PAPER TRADING: nessun ordine reale.",
        ])
        return "\n".join(lines)

    plan = plans[0]
    trade = build_conditional_trade_plan(plan, quotes or {})
    direction = "SHORT" if "SHORT" in str(plan.get("bias", "")).upper() else "LONG"
    entry, stop, tp1, tp2 = (trade.get(k) for k in ("entry", "stop", "tp1", "tp2"))
    rr1 = trade.get("rr_tp1")
    rr2 = trade.get("rr_tp2")
    lines.extend([
        "",
        f"🎯 STRUMENTO: {plan.get('candidate', 'da identificare')}",
        f"🔴 DIREZIONE: {direction} ipotetico",
        "⏱️ ORIZZONTE: INTRADAY",
        "🧪 MODALITÀ: PAPER TRADING",
        "",
        "━━━━━━━━━━━━━━━━━━",
        "📰 1. CATALIZZATORE",
        str(plan.get("evidence") or text)[:700],
        f"📡 Fonte: {source}",
        "",
        "📊 2. OPERAZIONE IPOTETICA",
        f"• Entrata: {entry if entry is not None else 'quotazione aggiornata da verificare'}",
        f"• Stop loss: {stop if stop is not None else 'calcolato su ATR quando disponibile'}",
        f"• Take profit 1: {tp1 if tp1 is not None else 'da calcolare sulla quotazione effettiva'}",
        f"• Take profit 2: {tp2 if tp2 is not None else 'da calcolare sulla quotazione effettiva'}",
        f"• Rapporto rischio/rendimento: TP1 {rr1}R / TP2 {rr2}R, solo dopo calcolo sui prezzi effettivi" if entry is not None else "• Rapporto rischio/rendimento: da calcolare sui prezzi effettivi",
        "",
        "━━━━━━━━━━━━━━━━━━",
        "⚡ 3. PERCHÉ VALUTARE L'OPERAZIONE",
        f"Ipotesi: {plan.get('if_then') or plan.get('event', 'catalizzatore rilevato')}",
        f"🔄 Scenario alternativo: {plan.get('alternative') or 'una reazione opposta del mercato può invalidare la direzione ipotizzata.'}",
        f"❌ INVALIDAZIONE: {plan.get('invalidation', 'annuncio smentito o reazione del prezzo incompatibile con lo scenario')}",
        f"🛑 Annulla lo scenario se: {plan.get('invalidation', 'il catalizzatore viene smentito o il prezzo invalida la direzione')}",
        "",
        "━━━━━━━━━━━━━━━━━━",
        "🧠 4. DECISIONE SPUTNIK",
        f"Direzione: {direction} ipotetico",
        f"Prezzo: {entry if entry is not None else 'da aggiornare'}",
        f"Conferma tecnica: {'da verificare sul trigger di prezzo/volume' if trade.get('status') != 'TRIGGER CONFIRMED' else 'presente nei dati quotazione forniti'}",
        f"Conferma richiesta: {plan.get('confirmation', 'verificare il catalizzatore e la reazione del prezzo')}",
        f"Stato: {trade.get('status', 'WAIT')} — {trade.get('reason', 'quotazioni aggiornate necessarie')}",
        "",
        "⚠️ Segnale sperimentale. Nessun ordine reale.",
    ])
    return "\n".join(lines)
