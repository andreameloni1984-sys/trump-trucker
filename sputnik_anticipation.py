"""Permissive, auditable catalyst anticipation for Sputnik (PAPER only).

This fallback only runs after the strict same-sentence matcher abstains. It may
surface one unambiguous action/topic match across adjacent sentences, but never
labels it as price-confirmed and never invents quote-based levels.
"""
from __future__ import annotations

import re
from typing import Any

from sputnik_decision_engine import BASE_SCENARIOS, NEGATIONS, RULES, conditional_plans
from sputnik_cfd import build_conditional_trade_plan


def _sentences(text: str) -> list[str]:
    normalized = str(text or "").replace("?", ".").replace("!", ".").replace(";", ".")
    return [" ".join(part.split()) for part in normalized.split(".") if part.strip()]


def _has_term(text: str, terms: tuple[str, ...]) -> bool:
    body = str(text or "").lower()
    return any(
        re.search(rf"(?<!\\w){re.escape(str(term).strip().lower())}(?!\\w)", body) is not None
        for term in terms
        if str(term).strip()
    )


def _is_negated(sentence: str) -> bool:
    return _has_term(sentence, tuple(str(term).strip() for term in NEGATIONS))


def adjacent_sentence_plan(text: str) -> dict[str, Any] | None:
    """Return a single adjacent-sentence catalyst only when the strict matcher abstains."""
    body = str(text or "").strip()
    if not body or conditional_plans(body, limit=1):
        return None

    sentences = _sentences(body)
    if len(sentences) < 2:
        return None

    matches: dict[str, dict[str, Any]] = {}
    for scenario in BASE_SCENARIOS:
        rule = RULES.get(str(scenario.get("id") or ""))
        if not rule:
            continue
        for left, right in zip(sentences, sentences[1:]):
            if _is_negated(left) or _is_negated(right):
                continue
            action_left = _has_term(left, rule["actions"])
            action_right = _has_term(right, rule["actions"])
            topic_left = _has_term(left, rule["topics"])
            topic_right = _has_term(right, rule["topics"])
            if not ((action_left and topic_right) or (topic_left and action_right)):
                continue
            row = {key: value for key, value in scenario.items() if key != "trigger"}
            row.update({
                "evidence": f"{left}. {right}"[:320],
                "evidence_mode": "ADJACENT_SENTENCES",
                "status": "ANTICIPATION_ONLY_NEEDS_PRICE_VOLUME_CONFIRMATION",
            })
            matches[str(scenario["id"])] = row
            break

    # If the same text could imply different scenarios, keep the old WAIT behavior.
    if len(matches) != 1:
        return None
    return next(iter(matches.values()))


def anticipation_message(
    plan: dict[str, Any],
    source: str = "Fonte pubblica",
    quotes: dict[str, Any] | None = None,
) -> str:
    """Format an early hypothesis; quote-based levels are shown only if valid."""
    trade = build_conditional_trade_plan(plan, quotes or {})
    bias = str(plan.get("bias") or "").upper()
    direction = "SHORT" if "SHORT" in bias else "LONG"
    entry, stop, tp1, tp2 = (trade.get(key) for key in ("entry", "stop", "tp1", "tp2"))
    lines = [
        "🛰️ SPUTNIK — OPPORTUNITÀ ANTICIPATA",
        "━━━━━━━━━━━━━━━━━━",
        f"🎯 STRUMENTO: {plan.get('candidate', 'da identificare')}",
        f"🟡 DIREZIONE IPOTIZZATA: {direction}",
        "⏱️ ORIZZONTE: INTRADAY",
        "🧪 MODALITÀ: PAPER TRADING",
        "",
        "📰 CATALIZZATORE — MATCH SU FRASI ADIACENTI",
        str(plan.get("evidence") or "")[:500],
        f"📡 Fonte: {source}",
        "",
        "📊 PIANO CONDIZIONALE",
        f"• Entrata: {entry if entry is not None else 'non calcolabile: quotazione aggiornata e ATR necessari'}",
        f"• Stop Loss: {stop if stop is not None else 'non calcolabile senza dati validi'}",
        f"• Take Profit 1: {tp1 if tp1 is not None else 'non calcolabile senza dati validi'}",
        f"• Take Profit 2: {tp2 if tp2 is not None else 'non calcolabile senza dati validi'}",
        f"• Stato livelli: {trade.get('status', 'WAIT')} — non equivale a conferma del segnale",
        "",
        f"🧠 Ipotesi: {plan.get('if_then') or plan.get('event', 'catalizzatore da verificare')}",
        f"✅ Conferma richiesta: {plan.get('confirmation', 'reazione indipendente di prezzo e volume')}",
        f"🔄 Scenario alternativo: {plan.get('alternative') or 'il mercato può reagire in direzione opposta'}",
        f"❌ INVALIDAZIONE: {plan.get('invalidation', 'fonte smentita o reazione incompatibile')}",
        "",
        "📌 DECISIONE: ANTICIPAZIONE, NON SEGNALE CONFERMATO",
        "Prezzo/volume/struttura restano necessari per la conferma; nessun ordine reale.",
    ]
    return "\n".join(lines)
