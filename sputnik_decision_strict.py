"""Strict SPUTNIK catalyst gate. Generic topic mentions are not trade signals."""
from __future__ import annotations
import re
from typing import Any
from sputnik_decision import SCENARIOS as BASE_SCENARIOS

RULES = {
    "tariff_escalation": (
        r"(?:impos\w*|announc\w*|rais\w*|increas\w*|introduc\w*|lev\w*|implement\w*|annunci\w*|aument\w*|applic\w*)\W{0,90}(?:tariff\w*|import dut\w*|dazi)",
        r"(?:tariff\w*|import dut\w*|dazi)\W{0,60}(?:impos\w*|announc\w*|rais\w*|increas\w*|introduc\w*|lev\w*|implement\w*|annunci\w*|aument\w*|applic\w*)",
    ),
    "trade_deescalation": (
        r"(?:sign\w*|reach\w*|agree\w*|announc\w*|finali[sz]\w*|firm\w*|raggiung\w*|concord\w*|sospend\w*|pause\w*)\W{0,80}(?:trade deal|trade agreement|accordo commerciale|intesa commerciale|tariff\w*|dazi|pausa sui dazi)",
        r"(?:trade deal|trade agreement|accordo commerciale|intesa commerciale|tariff pause|pausa sui dazi)\W{0,80}(?:sign\w*|reach\w*|agree\w*|announc\w*|finali[sz]\w*|firm\w*|raggiung\w*|concord\w*|sospend\w*|pause\w*)",
    ),
    "oil_supply_disruption": (
        r"(?:block\w*|clos\w*|disrupt\w*|interrupt\w*|attack\w*|seiz\w*|threat\w*|halt\w*|suspend\w*|interromp\w*|blocca\w*|chius\w*|attacc\w*|minacci\w*)\W{0,100}(?:oil|crude|brent|wti|petroleum|tanker\w*|shipping|export\w*|supply|hormuz|strait|petrolio|flussi|esportazion\w*|petrolier\w*|offerta)",
        r"(?:oil|crude|brent|wti|petroleum|tanker\w*|shipping|export\w*|supply|hormuz|strait|petrolio|flussi|esportazion\w*|petrolier\w*|offerta)\W{0,100}(?:block\w*|clos\w*|disrupt\w*|interrupt\w*|attack\w*|seiz\w*|threat\w*|halt\w*|suspend\w*|interromp\w*|blocca\w*|chius\w*|attacc\w*|minacci\w*)",
        r"(?:oil supply disruption|interruption of oil supply|interruzione dell[' ]offerta di petrolio|interruzione flussi petroliferi|blocco dello stretto di hormuz)",
    ),
}
NEGATION = re.compile(r"\b(?:not|never|did not|does not|do not|will not|would not|won't|denies?|denied|rejects?|rejected|withdrawn|cancelled|non|nessun[oaie]?|nega|smentisce|ritira|respinge)\b", re.I)

def _evidence(text: str, patterns: tuple[str, ...]) -> str:
    for sentence in re.split(r"(?<=[.!?])\s+|[\r\n]+", str(text or "")):
        sentence = " ".join(sentence.split())
        if not sentence:
            continue
        for pattern in patterns:
            match = re.search(pattern, sentence, re.I)
            if match:
                context = sentence[max(0, match.start() - 50):min(len(sentence), match.end() + 30)]
                if not NEGATION.search(context):
                    return sentence[:320]
    return ""

def conditional_plans(text: str, limit: int = 3) -> list[dict[str, Any]]:
    if not str(text or "").strip() or limit <= 0:
        return []
    rows = []
    for scenario in BASE_SCENARIOS:
        patterns = RULES.get(scenario["id"])
        if not patterns:
            continue
        evidence = _evidence(text, patterns)
        if not evidence:
            continue
        hits = [term for term in scenario.get("trigger", ()) if term in str(text).lower()]
        row = {key: value for key, value in scenario.items() if key != "trigger"}
        row.update(matched_terms=hits, match_count=len(hits), evidence=evidence)
        rows.append(row)
    rows.sort(key=lambda row: (row["match_count"], row["id"]), reverse=True)
    return rows[:limit]

def decision_message(text: str, source: str = "Fonte pubblica") -> str:
    plans = conditional_plans(text)
    lines = ["🛰️ SPUTNIK — RISULTATO OPERATIVO", "━━━━━━━━━━━━━━━━━━", f"📰 Fonte analizzata: {source}", ""]
    if not plans:
        lines.extend(["🟡 NESSUN CATALIZZATORE OPERATIVO RILEVATO",
                      "Serve un'azione concreta nella singola notizia, non una semplice menzione.",
                      "Non genero un piano quando il testo non supera il filtro."])
        return "\n".join(lines)
    for index, plan in enumerate(plans, 1):
        lines.extend([
            f"{index}. 🎯 {plan['event']}",
            f"➡️ Strumento da preparare: {plan['candidate']}",
            f"📈 Scenario: {plan['bias']}",
            f"🧾 Evidenza rilevata: {plan['evidence']}",
            f"🧭 REGOLA: {plan['if_then']}",
            f"✅ Conferma richiesta: {plan['confirmation']}",
            f"🛑 Annulla lo scenario se: {plan['invalidation']}",
            f"📎 Qualità della fonte: {plan['source_quality']}",
            "",
        ])
    lines.extend(["⚠️ Piano condizionale, non ordine immediato.",
                  "Entry, stop-loss, target e size richiedono quotazioni aggiornate e verificabili."])
    return "\n".join(lines)
