"""SPUTNIK Trading Instrument Recommender.

After the catalyst analysis, produces one concrete instrument to monitor/trade
(paper only). Never places orders. Always requires price/volume confirmation.
"""
from __future__ import annotations

from typing import Any

from sputnik_catalyst import catalyst_watchlist, directional_news_candidates
from sputnik_action_reaction import match_historical_reactions, infer_direction, classify_event


COMMODITY_PRIORITY = {
    "WTI", "BRENT", "GOLD", "SILVER", "COPPER", "NATURAL_GAS",
    "CORN", "WHEAT", "SOYBEAN", "COFFEE", "COCOA", "SUGAR",
}


def recommend_trading_instrument(
    findings: list[dict[str, Any]],
    limit: int = 1,
) -> dict[str, Any] | None:
    """Return the single best instrument recommendation after analysis.

    Priority:
    1. Explicit directional news bias (RSS item-level)
    2. High-score catalyst watch with historical bias
    3. Highest catalyst score overall
    """
    if not findings:
        return None

    directional = directional_news_candidates(findings, limit=10)
    commodity_directional = [
        d for d in directional
        if d.get("instrument") in COMMODITY_PRIORITY
    ]
    if commodity_directional:
        best = commodity_directional[0]
        return {
            "instrument": best["instrument"],
            "bias": best["bias"].replace("_BIAS", ""),
            "score": 85.0,
            "reason": best["reason"],
            "source": best.get("source", ""),
            "url": best.get("url", ""),
            "title": best.get("title", ""),
            "status": "BIAS_ONLY_NEEDS_PRICE_VOLUME_CONFIRMATION",
            "confirmation": "Verificare prezzo e volume live prima di qualsiasi operazione paper.",
            "type": "DIRECTIONAL_NEWS",
        }

    watches = catalyst_watchlist(findings, limit=15)
    scored = []
    for w in watches:
        inst = str(w.get("instrument") or "").upper()
        if inst not in COMMODITY_PRIORITY and inst not in {"NASDAQ100", "USD"}:
            continue

        hist_dirs: dict[str, str] = {}
        for finding in findings:
            domains = set(finding.get("domains") or [])
            if not domains.intersection(set(w.get("domains") or [])):
                continue
            text = " ".join([
                str(finding.get("title") or ""),
                " ".join(finding.get("domains") or []),
                str(finding.get("text") or "")[:500],
            ])
            matches = match_historical_reactions(text, limit=2)
            if matches:
                hist_dirs.update(infer_direction(matches))

        bias = "NEUTRAL"
        for asset, direction in hist_dirs.items():
            if asset in {"OIL", "WTI", "BRENT"} and direction == "UP":
                bias = "LONG"
            elif asset in {"OIL", "WTI", "BRENT"} and direction == "DOWN":
                bias = "SHORT"
            elif asset == "GOLD" and direction == "UP":
                bias = "LONG"
            elif asset == "GOLD" and direction == "DOWN":
                bias = "SHORT"

        base = float(w.get("score") or 0)
        if w.get("primary_source"):
            base += 12
        if hist_dirs:
            base += 8
        if inst in COMMODITY_PRIORITY:
            base += 5

        scored.append({
            "instrument": inst,
            "description": w.get("description", ""),
            "bias": bias,
            "score": min(100.0, base),
            "domains": w.get("domains") or [],
            "sources": w.get("sources") or [],
            "primary_source": bool(w.get("primary_source")),
            "historical_bias": hist_dirs,
            "reason": "Catalizzatore pubblico prioritario + analogo storico" if hist_dirs else "Catalizzatore pubblico da verificare",
        })

    if not scored:
        return None

    scored.sort(key=lambda x: -x["score"])
    best = scored[0]

    return {
        "instrument": best["instrument"],
        "bias": best["bias"],
        "score": best["score"],
        "reason": best["reason"],
        "description": best["description"],
        "sources": best["sources"],
        "primary_source": best["primary_source"],
        "historical_bias": best.get("historical_bias") or {},
        "status": "WATCH_PRIORITY" if best["bias"] == "NEUTRAL" else "BIAS_READY",
        "confirmation": "Conferma tecnica obbligatoria: prezzo, volume e ATR prima di qualsiasi operazione paper.",
        "type": "CATALYST_WATCH",
    }


def format_trading_instrument_message(rec: dict[str, Any] | None) -> str:
    """Telegram-ready message with the recommended instrument."""
    if not rec:
        return (
            "🛰️ SPUTNIK — STRUMENTO DA TRADARE\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🟡 Nessun catalizzatore commodity sufficientemente forte.\n"
            "Monitorare: WTI, BRENT, GOLD.\n"
            "⚠️ Solo paper. Nessun ordine reale."
        )

    bias_emoji = "🟢" if rec["bias"] == "LONG" else "🔴" if rec["bias"] == "SHORT" else "🟡"
    lines = [
        "🛰️ SPUTNIK — STRUMENTO DA TRADARE",
        "━━━━━━━━━━━━━━━━━━",
        f"🎯 STRUMENTO: {rec['instrument']}",
        f"{bias_emoji} BIAS: {rec['bias']}",
        f"📊 SCORE CATALIZZATORE: {rec['score']:.0f}/100",
        f"📌 MOTIVO: {rec['reason']}",
    ]
    if rec.get("description"):
        lines.append(f"📝 {rec['description']}")
    if rec.get("title"):
        lines.append(f"📰 {rec['title'][:200]}")
    if rec.get("url"):
        lines.append(f"🔗 {rec['url']}")
    lines.extend([
        "",
        f"✅ CONFERMA: {rec['confirmation']}",
        f"🧪 STATO: {rec['status']}",
        "⚠️ PAPER TRADING ONLY — nessun ordine reale.",
    ])
    return "\n".join(lines)
