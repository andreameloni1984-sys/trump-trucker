"""Auditable, deterministic reasoning layer for SPUTNIK public catalysts.

This module explains evidence and uncertainty; it never creates a trade,
changes a catalyst classification, or bypasses quote/ATR safeguards.
"""
from __future__ import annotations

from typing import Any


def build_reasoning(text: str, plan: dict[str, Any] | None = None,
                    trade: dict[str, Any] | None = None) -> dict[str, Any]:
    body = " ".join(str(text or "").split())
    plan = plan or {}
    trade = trade or {}
    evidence = str(plan.get("evidence") or "")
    bias = str(plan.get("bias") or "").upper()
    candidate = str(plan.get("candidate") or "non identificato")
    confirmations = []
    contradictions = []
    missing = []

    if evidence:
        confirmations.append("Evento specifico individuato nel testo pubblico: " + evidence[:220])
    else:
        missing.append("Nessun evento direzionale sufficientemente specifico nel testo disponibile.")

    if plan:
        confirmations.append("La regola evento-catalizzatore associa questa evidenza a " + candidate + ".")
        if "LONG" in bias:
            thesis = "LONG"
        elif "SHORT" in bias:
            thesis = "SHORT"
        else:
            thesis = "NEUTRAL"
    else:
        thesis = "NEUTRAL"
        contradictions.append("NO_DIRECTION: il testo non supera il filtro evento-azione; una semplice menzione non basta.")

    # Distinguish a news thesis from market confirmation and quote availability.
    trade_status = str(trade.get("status") or "")
    if trade.get("entry") is not None and trade_status in {"EARLY_SETUP", "CONFIRMED", "PREPARE", "TRIGGER CONFIRMED"}:
        confirmations.append("Quotazione timestamped e ATR disponibili: livelli condizionali calcolati.")
    else:
        missing.append("Conferma indipendente di prezzo/volume e struttura non dimostrata da Sputnik.")
    if trade_status in {"WAIT", "EARLY_BIAS"}:
        missing.append("Bias conservato; quotazione futures fresca o ATR valido non disponibile: entry/SL/TP omessi.")
    elif trade_status in {"EARLY_SETUP", "PREPARE"}:
        missing.append("EARLY_SETUP non equivale a trigger D-L-A confermato: attendere il timing richiesto.")
    if not body:
        missing.append("Testo originale dell'evento assente o vuoto.")

    alternative = str(plan.get("alternative") or
                      "Il mercato può ignorare la notizia, averla già scontata o reagire in direzione opposta.")
    invalidation = str(plan.get("invalidation") or
                       "Smentita dell'evento, fonte non confermata o reazione del prezzo incompatibile.")

    if thesis == "NEUTRAL":
        conclusion = "NO_DIRECTION: nessun lato sostenibile dal testo; mantenere il monitoraggio senza inventare una direzione."
    elif trade_status in {"CONFIRMED", "TRIGGER CONFIRMED"}:
        conclusion = f"Tesi {thesis} con setup confermato dai dati disponibili; resta soggetta ai controlli esterni."
    elif trade_status in {"EARLY_SETUP", "PREPARE"}:
        conclusion = f"Tesi {thesis} da catalizzatore; setup preliminare, non trade paper eseguito."
    else:
        conclusion = f"Tesi {thesis} solo da notizia: non autorizzare un trade paper finché prezzo e rischio non sono verificati."

    return {
        "candidate": candidate,
        "thesis": thesis,
        "confirmations": confirmations,
        "contradictions": contradictions,
        "missing": missing,
        "alternative": alternative,
        "invalidation": invalidation,
        "conclusion": conclusion,
    }


def format_reasoning(reasoning: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "🧠 5. RAGIONAMENTO SPUTNIK",
        f"• Tesi: {reasoning.get('thesis', 'NEUTRAL')} — {reasoning.get('conclusion', '')}",
    ]
    for label, key in (("A favore", "confirmations"), ("Contrasti", "contradictions"),
                       ("Da verificare", "missing")):
        values = reasoning.get(key) or []
        if values:
            lines.append(f"• {label}:")
            lines.extend("  - " + str(value)[:260] for value in values[:3])
    lines.extend([
        "• Scenario alternativo: " + str(reasoning.get("alternative") or "")[:260],
        "• Invalidazione: " + str(reasoning.get("invalidation") or "")[:260],
    ])
    return lines
