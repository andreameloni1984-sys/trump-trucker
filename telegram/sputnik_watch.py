"""SPUTNIK WATCH pre-alert helper.

Identifica candidati vicini a un segnale operativo (score alto ma non ancora TRADE).
Il riepilogo dichiara esplicitamente il proprio perimetro: ranking delle transazioni,
non una valutazione completa di notizie pubbliche o segnali CFD.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _record_count(value: Any) -> int:
    if isinstance(value, (dict, list, tuple, set)):
        return len(value)
    return 0


def _state_context_lines(state: dict[str, Any]) -> list[str]:
    transactions = state.get("transactions") or {}
    intelligence_items = state.get("intelligence_items") or {}
    cfd_history_present = "cfd_signal_history" in state
    cfd_history = state.get("cfd_signal_history") or []

    lines = [
        f"Transazioni registrate: {_record_count(transactions)}",
        f"Notizie pubbliche archiviate: {_record_count(intelligence_items)} (non valutate dal ranking WATCH)",
        (
            f"Storico segnali CFD: {_record_count(cfd_history)}"
            if cfd_history_present
            else "Storico segnali CFD: campo non presente nello stato"
        ),
    ]

    updated_at = str(state.get("updated_at") or "").strip()
    if not updated_at:
        lines.append("Aggiornamento stato: timestamp non disponibile")
        return lines

    try:
        parsed = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            lines.append(f"Aggiornamento stato: {updated_at} (fuso orario assente)")
            return lines
        age_seconds = (datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).total_seconds()
        if age_seconds >= 0:
            age_minutes = int(age_seconds // 60)
            lines.append(f"Aggiornamento stato: {updated_at} | età {age_minutes} min")
        else:
            future_minutes = int(abs(age_seconds) // 60)
            lines.append(f"Aggiornamento stato: {updated_at} | timestamp futuro di {future_minutes} min")
    except (TypeError, ValueError, OverflowError):
        lines.append(f"Aggiornamento stato: timestamp non interpretabile ({updated_at})")
    return lines


def _empty_or_unavailable_message(state: dict[str, Any], ranking_error: str | None = None) -> str:
    lines = [
        "🟡 **SPUTNIK — WATCH**",
        "━━━━━━━━━━━━━━━━━━",
        "Ambito: solo ranking delle transazioni registrate; non è una scansione completa di notizie o CFD.",
        "",
    ]
    if not state:
        lines += [
            "⚠️ Stato SPUTNIK non disponibile o vuoto: ranking non valutabile.",
            "Questo non equivale a un'assenza di candidati di mercato.",
        ]
    elif ranking_error:
        lines += [
            f"⚠️ Ranking WATCH non disponibile: errore {ranking_error}.",
            "Non è possibile concludere che non esistano candidati.",
        ]
        lines += _state_context_lines(state)
    else:
        lines += [
            "Nessun candidato nel ranking WATCH delle transazioni registrate.",
            "Questo non equivale a un'assenza di opportunità di mercato.",
        ]
        lines += _state_context_lines(state)
    return "\n".join(lines)


def build_watch_message(state: dict[str, Any], min_score: float = 60.0) -> str:
    """Costruisce un messaggio WATCH e rende espliciti perimetro e freschezza."""
    try:
        from sputnik_ranking import rank_purchase_candidates
        rows = rank_purchase_candidates(
            list((state.get("transactions") or {}).values()),
            limit=8,
        )
    except Exception as exc:
        return _empty_or_unavailable_message(state, ranking_error=type(exc).__name__)

    watch = [r for r in rows if float(r.get("score", 0) or 0) >= min_score and r.get("signal") != "COMPRA"]
    if not watch:
        return _empty_or_unavailable_message(state)

    lines = [
        "🟡 **SPUTNIK — WATCH**",
        "━━━━━━━━━━━━━━━━━━",
        "Ambito: solo ranking delle transazioni registrate; non è una scansione completa di notizie o CFD.",
        "",
    ]
    lines += _state_context_lines(state)
    lines += ["", "Candidati vicini a un segnale operativo", ""]
    for i, row in enumerate(watch[:3], 1):
        lines.append(
            f"{i}. {row.get('security')} — {row.get('score')}/100 | {row.get('signal')}"
        )
        lines.append(f"   {row.get('reason', '')[:120]}")
    lines += ["", "⚠️ Solo monitoraggio. Non è un ordine."]
    return "\n".join(lines)
