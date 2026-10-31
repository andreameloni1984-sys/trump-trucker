"""SPUTNIK Trading Instrument Recommender.

Converts verified public catalysts into an early, explicitly conditional market
hypothesis. Catalyst priority is kept separate from directional conviction.
No prices are invented and no orders are placed.
"""
from __future__ import annotations

import re
from typing import Any

from sputnik_catalyst import catalyst_watchlist, directional_news_candidates, non_negated_pattern_matches
from sputnik_action_reaction import match_historical_reactions, infer_direction

COMMODITY_PRIORITY = {
    "WTI", "BRENT", "GOLD", "SILVER", "COPPER", "NATURAL_GAS",
    "CORN", "WHEAT", "SOYBEAN", "COFFEE", "COCOA", "SUGAR",
}

# Wider than the legacy rules, but still tied to a dated, URL-backed item.
# These create a preliminary thesis, never a confirmed entry.
_EARLY_RULES = (
    ("BRENT", "LONG", re.compile(
        r"\b(attacks? on .{0,50}(oil|energy|refiner|pipeline)|"
        r"(oil|energy) (facility|infrastructure|pipeline).{0,35}(attack|strike|hit)|"
        r"tanker.{0,35}(attack|mine|explod|struck)|"
        r"(iran|iranian|tehran).{0,45}(threatens?|threatened|warns?|warned|vows?|plans?|moves?|considers?|could).{0,35}(close|block|mine|shut).{0,25}(the )?(strait of hormuz|hormuz)|"
        r"(strait of hormuz|hormuz).{0,30}(closed|blocked|mined|shut|closure)|"
        r"(closure|blockade|mining).{0,30}(strait of hormuz|hormuz)|"
        r"shipping disruption|oil supply disruption|"
        r"crude exports? disrupted|refinery.{0,30}(attack|shut|damage)|"
        r"(tanker|oil vessel).{0,50}(hormuz|saudi|red sea).{0,35}(attack|struck|hit|seized)|"
        r"(tanker|oil vessel).{0,35}(attack|struck|hit|seized).{0,50}(hormuz|saudi|red sea)|"
        r"(attack|strike).{0,50}(tanker|oil vessel).{0,35}(hormuz|saudi|red sea))\b", re.I),
     "Rischio concreto per infrastrutture o trasporto fisico del greggio: possibile premio di offerta."),
    ("WTI", "LONG", re.compile(
        r"\b(us crude supply disruption|u\.s\. crude supply disruption|"
        r"oil supply disruption|production outage|pipeline outage|"
        r"crude exports? disrupted|oil production cut)\b", re.I),
     "Possibile restringimento dell'offerta petrolifera."),
    ("BRENT", "SHORT", re.compile(
        r"\b((ceasefire|peace (agreement|deal)).{0,50}(iran|hormuz|oil|shipping|energy)|"
        r"(iran|hormuz|oil|shipping|energy).{0,50}(ceasefire|peace (agreement|deal))|hormuz reopened|"
        r"strait of hormuz.{0,25}(reopens?|reopened|reopening|open again)|"
        r"hormuz.{0,25}(reopens?|reopened|reopening|open again)|"
        r"shipping.{0,20}(restored|resumes|resumed|back to normal)|"
        r"(passage|traffic|transit).{0,30}(resumes|resumed|restored|reopened).{0,30}(hormuz|strait)|"
        r"oil exports? resume|sanctions lifted.{0,30}oil|"
        r"iran.{0,40}(agreement|deal|settlement))\b", re.I),
     "Possibile riduzione del premio geopolitico e dei rischi sulle forniture."),
    ("WTI", "SHORT", re.compile(
        r"\b((ceasefire|peace (agreement|deal)).{0,50}(iran|hormuz|oil|shipping|energy)|"
        r"(iran|hormuz|oil|shipping|energy).{0,50}(ceasefire|peace (agreement|deal))|hormuz reopened|shipping restored|"
        r"oil exports? resume|sanctions lifted.{0,30}oil|"
        r"iran.{0,40}(agreement|deal|settlement))\b", re.I),
     "Possibile riduzione del premio geopolitico e dei rischi sulle forniture."),
)


def _early_direction(findings: list[dict[str, Any]], instrument: str) -> dict[str, Any] | None:
    candidates = []
    for finding in findings:
        if finding.get("evidence") != "PUBLIC_RSS_ITEM" or not finding.get("url") or not finding.get("published"):
            continue
        text = " ".join(str(finding.get(k) or "") for k in ("title", "text"))
        matched_rules = []
        for asset, direction, pattern, reason in _EARLY_RULES:
            if asset != instrument:
                continue
            if next(non_negated_pattern_matches(text, pattern), None) is not None:
                matched_rules.append((direction, reason))

        directions = {direction for direction, _ in matched_rules}
        # Mixed escalation/de-escalation wording is not assigned a direction.
        if len(directions) != 1:
            continue
        direction = next(iter(directions))
        reason = next(reason for matched_direction, reason in matched_rules if matched_direction == direction)
        candidates.append({
            "bias": direction,
            "reason": reason,
            "title": str(finding.get("title") or "")[:240],
            "source": str(finding.get("source") or "PUBLIC_RSS"),
            "url": str(finding.get("url") or ""),
            "published": str(finding.get("published") or ""),
            "event_id": str(finding.get("event_id") or ""),
        })
    if not candidates:
        return None
    candidates.sort(key=lambda x: x["published"], reverse=True)
    return candidates[0]

def recommend_trading_instrument(
    findings: list[dict[str, Any]],
    limit: int = 1,
) -> dict[str, Any] | None:
    """Return one prioritized commodity and a reasoned conditional thesis."""
    if not findings:
        return None

    # A specific, dated Brent risk headline must take precedence over the
    # broader ENERGY classifier, which can otherwise return WTI first for the
    # same Hormuz/Saudi tanker event.
    early_brent = _early_direction(findings, "BRENT")
    if early_brent:
        return {
            "instrument": "BRENT",
            "bias": early_brent["bias"],
            "score": 85.0,
            "reason": early_brent["reason"],
            "source": early_brent.get("source", ""),
            "url": early_brent.get("url", ""),
            "title": early_brent.get("title", ""),
            "published": early_brent.get("published", ""),
            "status": "PRELIMINARY_DIRECTIONAL_BIAS",
            "confirmation": "Ipotesi preliminare: verificare prezzo, volume e ATR live prima dell'ingresso paper.",
            "type": "EARLY_CATALYST_RULE",
            "alternative": "Se il catalizzatore viene smentito o il prezzo non reagisce, non inseguire il movimento.",
            "invalidation": "Notizia smentita, catalizzatore rientrato o struttura di prezzo contraria.",
        }

    directional = directional_news_candidates(findings, limit=10)
    commodity_directional = [d for d in directional if d.get("instrument") in COMMODITY_PRIORITY]
    if commodity_directional:
        best = commodity_directional[0]
        instrument = best["instrument"]
        bias = best["bias"].replace("_BIAS", "")
        return {
            "instrument": instrument, "bias": bias, "score": 85.0,
            "reason": best["reason"], "source": best.get("source", ""),
            "url": best.get("url", ""), "title": best.get("title", ""),
            "status": "PRELIMINARY_DIRECTIONAL_BIAS",
            "confirmation": "Ipotesi preliminare: verificare prezzo, volume e ATR live prima dell'ingresso paper.",
            "type": "DIRECTIONAL_NEWS",
            "alternative": "Se il catalizzatore viene smentito o il prezzo non reagisce, non inseguire il movimento.",
            "invalidation": "Notizia smentita, catalizzatore rientrato o struttura di prezzo contraria.",
        }

    watches = catalyst_watchlist(findings, limit=15)
    scored = []
    for w in watches:
        inst = str(w.get("instrument") or "").upper()
        if inst not in COMMODITY_PRIORITY:
            continue

        # First look for a concrete, dated headline with an explicit supply /
        # demand implication, even if the legacy keyword classifier missed it.
        early = _early_direction(findings, inst)
        hist_dirs: dict[str, str] = {}
        for finding in findings:
            if inst not in {"WTI", "BRENT", "GOLD"}:
                continue
            domains = set(finding.get("domains") or [])
            if not domains.intersection(set(w.get("domains") or [])):
                continue
            sample = " ".join([
                str(finding.get("title") or ""),
                " ".join(finding.get("domains") or []),
                str(finding.get("text") or "")[:700],
            ])
            matches = match_historical_reactions(sample, limit=2)
            if matches:
                hist_dirs.update(infer_direction(matches))

        bias = early["bias"] if early else "NEUTRAL"
        if not early:
            for asset, direction in hist_dirs.items():
                if asset in {"OIL", "WTI", "BRENT"} and direction == "UP":
                    bias = "LONG"
                elif asset in {"OIL", "WTI", "BRENT"} and direction == "DOWN":
                    bias = "SHORT"
                elif asset in {"GOLD"} and direction == "UP":
                    bias = "LONG"
                elif asset in {"GOLD"} and direction == "DOWN":
                    bias = "SHORT"

        base = float(w.get("score") or 0)
        if w.get("primary_source"):
            base += 12
        if hist_dirs:
            base += 8
        if early:
            base += 10
        scored.append({
            "instrument": inst, "description": w.get("description", ""),
            "bias": bias, "score": min(100.0, base),
            "domains": w.get("domains") or [], "sources": w.get("sources") or [],
            "primary_source": bool(w.get("primary_source")),
            "historical_bias": hist_dirs, "early": early,
            "reason": early["reason"] if early else (
                "Catalizzatore pubblico prioritario; direzione non dimostrata dai dati disponibili."
            ),
        })

    if not scored:
        return None
    scored.sort(key=lambda x: (-x["score"], x["instrument"]))
    best = scored[0]
    early = best.get("early") or {}
    bias = best["bias"]
    return {
        "instrument": best["instrument"], "bias": bias, "score": best["score"],
        "reason": best["reason"], "description": best["description"],
        "sources": best["sources"], "primary_source": best["primary_source"],
        "historical_bias": best.get("historical_bias") or {},
        "title": early.get("title", ""), "source": early.get("source", ""),
        "url": early.get("url", ""), "published": early.get("published", ""),
        "status": "PRELIMINARY_DIRECTIONAL_BIAS" if bias != "NEUTRAL" else "WATCH_NEUTRAL",
        "confirmation": "Verificare quotazione aggiornata, struttura, volume e ATR. Se i dati mancano o sono obsoleti, nessun livello operativo.",
        "alternative": (
            "Se il rischio di offerta si attenua o la notizia viene smentita, il premio geopolitico può rientrare."
            if bias == "LONG" else
            "Se il catalizzatore non si concretizza e il prezzo mantiene i supporti, l'ipotesi ribassista perde forza."
            if bias == "SHORT" else
            "Attendere una notizia specifica e una reazione osservabile del prezzo; non attribuire una direzione allo score."
        ),
        "invalidation": (
            "Notizia smentita, normalizzazione dei flussi o rottura della struttura tecnica contraria."
            if bias == "LONG" else
            "Notizia smentita, escalation dell'interruzione delle forniture o recupero della struttura tecnica."
            if bias == "SHORT" else
            "Nessuna direzione finché catalizzatore e reazione del prezzo non risultano coerenti."
        ),
        "type": "CATALYST_ANALYSIS",
    }


def format_trading_instrument_message(rec: dict[str, Any] | None) -> str:
    """Telegram-ready analyst brief; never fabricates entry/SL/targets."""
    if not rec:
        return (
            "🛰️ SPUTNIK — ANALISI DI MERCATO\n━━━━━━━━━━━━━━━━━━\n"
            "🟡 Nessun catalizzatore commodity verificabile.\n"
            "⚠️ PAPER TRADING ONLY — nessun ordine reale."
        )
    bias = str(rec.get("bias") or "NEUTRAL").upper()
    icon = "🟢" if bias == "LONG" else "🔴" if bias == "SHORT" else "🟡"
    lines = [
        "🛰️ SPUTNIK — ANALISI DI MERCATO", "━━━━━━━━━━━━━━━━━━",
        f"🎯 STRUMENTO: {rec.get('instrument', 'N/D')}",
        f"{icon} BIAS PRELIMINARE: {bias}",
        f"📊 PRIORITÀ CATALIZZATORE: {float(rec.get('score') or 0):.0f}/100",
        f"📌 TESI: {rec.get('reason', 'Nessuna tesi disponibile.')}",
    ]
    if rec.get("title"):
        lines.extend(["", f"📰 EVENTO: {str(rec['title'])[:240]}"])
    if rec.get("published"):
        lines.append(f"🕒 PUBBLICATO: {rec['published']}")
    sources = list(dict.fromkeys(
        str(x).strip() for x in ([rec.get("source")] + list(rec.get("sources") or [])) if str(x or "").strip()
    ))
    if sources:
        lines.append("🔎 FONTI: " + " | ".join(sources[:4]))
    if rec.get("url"):
        lines.append(f"🔗 ORIGINALE: {rec['url']}")
    lines.extend([
        "", f"↔️ SCENARIO ALTERNATIVO: {rec.get('alternative', 'Attendere nuove evidenze.')}",
        f"⛔ INVALIDAZIONE: {rec.get('invalidation', 'Tesi non più valida se il catalizzatore viene smentito.')}",
        "",
    ])
    if bias == "NEUTRAL":
        lines.append("🧭 DECISIONE: WATCH — priorità alta non significa direzione LONG/SHORT.")
    else:
        lines.append(f"🧭 DECISIONE: {bias} PRELIMINARE — ipotesi anticipata, NON ingresso confermato.")
    lines.extend([
        "📐 OPERATIVITÀ: ingresso, SL, TP1 e TP2 solo con quotazione fresca e ATR verificato.",
        f"✅ CONTROLLO: {rec.get('confirmation', 'Verificare i dati di mercato live.')}",
        f"🧪 STATO: {rec.get('status', 'WATCH')}",
        "⚠️ PAPER TRADING ONLY — nessun ordine reale.",
    ])
    return "\n".join(lines)
