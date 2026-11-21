"""Test in SOLA LETTURA del conto Trading 212 Invest DEMO di Sputnik.

    python sputnik_t212_demo_check.py

Usa i secret SPUTNIK_INVEST_DEMO_API_KEY / SPUTNIK_INVEST_DEMO_API_SECRET.
Legge saldo e posizioni; non inserisce, modifica o cancella ordini.
Le chiavi non vengono mai stampate.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request

DEMO_BASE = "https://demo.trading212.com/api/v0"


def split_credentials(key: str, secret: str) -> tuple[str, str, str]:
    """Gestisce chiave e segreto incollati insieme nello stesso secret (due righe o 'chiave:segreto')."""
    key, secret, note = (key or "").strip(), (secret or "").strip(), ""
    parts = [p.strip() for p in key.replace("\r", "\n").split("\n") if p.strip()]
    if len(parts) >= 2:
        note = "la chiave contiene più righe: uso la prima come chiave e la seconda come segreto"
        key, secret = parts[0], secret or parts[1]
    elif not secret and ":" in key:
        note = "la chiave contiene 'chiave:segreto': li separo"
        key, secret = (x.strip() for x in key.split(":", 1))
    return "".join(key.split()), "".join(secret.split()), note


def _get(path: str, auth: str) -> tuple[int, object]:
    request = urllib.request.Request(DEMO_BASE + path, method="GET")
    request.add_unredirected_header("Authorization", auth)
    request.add_header("User-Agent", "Sputnik-demo-check")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        return exc.code, None
    except Exception as exc:  # noqa: BLE001
        return 0, type(exc).__name__


def run() -> tuple[bool, str]:
    key, secret, note = split_credentials(
        os.getenv("SPUTNIK_INVEST_DEMO_API_KEY", ""), os.getenv("SPUTNIK_INVEST_DEMO_API_SECRET", "")
    )
    if not key or not secret:
        return False, "\n".join([
            "🧪 SPUTNIK · TEST TRADING 212 DEMO — ❌ chiavi mancanti",
            f"Chiave: {'presente' if key else 'assente'} · segreto: {'presente' if secret else 'assente'}",
            "Servono i secret SPUTNIK_INVEST_DEMO_API_KEY e SPUTNIK_INVEST_DEMO_API_SECRET in trump-trucker.",
        ])
    auth = "Basic " + base64.b64encode(f"{key}:{secret}".encode()).decode()
    status, cash = _get("/equity/account/cash", auth)
    if status != 200 or not isinstance(cash, dict):
        reason = f"HTTP {status}" if status else f"errore di rete ({cash})"
        hint = {
            401: "chiave rifiutata: verifica che sia del conto DEMO, non scaduta o revocata, senza limiti di IP.",
            403: "chiave valida ma senza permesso di lettura dell'account: abilita i permessi Account e Portfolio.",
            429: "troppe richieste: riprova tra un minuto.",
        }.get(status, "controlla chiave, segreto e permessi.")
        return False, "\n".join([
            "🧪 SPUTNIK · TEST TRADING 212 DEMO — ❌ accesso non riuscito",
            f"Esito: {reason} · chiave {len(key)} caratteri · segreto {len(secret)} caratteri",
            *([f"Nota: {note}"] if note else []),
            f"Causa probabile: {hint}",
        ])
    _, info = _get("/equity/account/info", auth)
    pstatus, positions = _get("/equity/portfolio", auth)
    ccy = info.get("currencyCode", "") if isinstance(info, dict) else ""
    lines = [
        "🧪 SPUTNIK · TEST TRADING 212 DEMO — ✅ collegamento riuscito",
        *([f"Nota: {note}"] if note else []),
        "",
        f"Valore totale: {cash.get('total', 'n.d.')} {ccy}",
        f"Liquidità disponibile: {cash.get('free', 'n.d.')} {ccy}",
        f"Investito: {cash.get('invested', 'n.d.')} {ccy}",
        f"Profitto/perdita aperti: {cash.get('ppl', 'n.d.')} {ccy}",
    ]
    if pstatus == 200 and isinstance(positions, list):
        lines.append(f"Posizioni aperte: {len(positions)}")
        for p in positions[:5]:
            lines.append(f"• {p.get('ticker')} · quantità {p.get('quantity')} · P/L {p.get('ppl')}")
    else:
        lines.append(f"Posizioni: non leggibili (HTTP {pstatus}) — manca il permesso Portfolio?")
    lines += ["", "Test in sola lettura: nessun ordine inserito. Conto DEMO, nessun denaro reale."]
    return True, "\n".join(lines)


def main() -> int:
    ok, text = run()
    print(text)
    if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
        from trump_tracker import send_telegram
        send_telegram(text)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
