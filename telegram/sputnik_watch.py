"""SPUTNIK WATCH pre-alert helper.

Identifica candidati vicini a un segnale operativo (score alto ma non ancora TRADE).
"""

from __future__ import annotations

from typing import Any


def build_watch_message(state: dict[str, Any], min_score: float = 60.0) -> str:
    """Costruisce un messaggio WATCH dai candidati di ranking."""
    try:
        from sputnik_ranking import rank_purchase_candidates
        rows = rank_purchase_candidates(
            list((state.get("transactions") or {}).values()),
            limit=8,
        )
    except Exception:
        return ""

    watch = [r for r in rows if float(r.get("score", 0) or 0) >= min_score and r.get("signal") != "COMPRA"]
    if not watch:
        return ""

    lines = [
        "🟡 **SPUTNIK — WATCH**",
        "━━━━━━━━━━━━━━━━━━",
        "Candidati vicini a un segnale operativo",
        "",
    ]
    for i, row in enumerate(watch[:3], 1):
        lines.append(
            f"{i}. {row.get('security')} — {row.get('score')}/100 | {row.get('signal')}"
        )
        lines.append(f"   {row.get('reason', '')[:120]}")
    lines += ["", "⚠️ Solo monitoraggio. Non è un ordine."]
    return "\n".join(lines)
