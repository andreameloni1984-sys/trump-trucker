"""Persistent SPUTNIK Telegram listener.

Telegram transport is deliberately separated from the GitHub Actions collector.
The listener owns the single getUpdates session (legacy). Primary path is now
GitHub Actions polling.
"""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from sputnik_ranking import rank_purchase_candidates
from sputnik_cfd import build_cfd_cart
from sputnik_catalyst import catalyst_watchlist
from sputnik_action_reaction import action_reaction_message
from sputnik_decision_engine import decision_message
from sputnik_aggressive import aggressive_message
from sputnik_history import anticipatory_selector, build_public_history, CORE_ADMINISTRATION
from trump_tracker import (
    fetch_public_text,
    telegram_brief_message,
    telegram_filings_message,
    telegram_help_message,
    telegram_news_message,
    telegram_positions_message,
    telegram_purchases_message,
    telegram_sales_message,
    telegram_test_message,
    telegram_transactions_message,
    telegram_trump_order_message,
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
BOT_LOCK = threading.Lock()
STOP_EVENT = threading.Event()
LOCAL_STATE_FILE = Path(os.getenv("SPUTNIK_TELEGRAM_LOCAL_STATE", "telegram_listener_state.json"))
REMOTE_STATE_URL = os.getenv(
    "SPUTNIK_STATE_URL",
    "https://raw.githubusercontent.com/andreameloni1984-sys/trump-trucker/main/sputnik_state.json",
)
PORT = int(os.getenv("PORT", "10000"))
POLL_TIMEOUT = 25


def load_local_state() -> dict[str, Any]:
    if not LOCAL_STATE_FILE.exists():
        return {"offset": 0, "chat_id": "", "active": True}
    try:
        return json.loads(LOCAL_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"offset": 0, "chat_id": "", "active": True}


def save_local_state(state: dict[str, Any]) -> None:
    tmp = LOCAL_STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    tmp.replace(LOCAL_STATE_FILE)


LOCAL_STATE = load_local_state()

def bootstrap_state(token: str, chat_id: str = "") -> None:
    """Apply trusted bootstrap credentials without logging secrets."""
    global BOT_TOKEN
    token = str(token or "").strip()
    chat_id = str(chat_id or "").strip()
    with BOT_LOCK:
        BOT_TOKEN = token
        if token:
            os.environ["TELEGRAM_BOT_TOKEN"] = token
    if chat_id:
        LOCAL_STATE["chat_id"] = chat_id
        LOCAL_STATE["active"] = True
        save_local_state(LOCAL_STATE)


def api(method: str, payload: dict[str, Any], timeout: int = 35) -> dict[str, Any]:
    token = BOT_TOKEN
    if not token:
        raise RuntimeError("Telegram token non configurato")
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def send(text: str, chat_id: str | None = None, reply_markup: dict[str, Any] | None = None) -> bool:
    target = str(chat_id or LOCAL_STATE.get("chat_id") or "").strip()
    if not target:
        return False
    try:
        payload = {"chat_id": target, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        result = api("sendMessage", payload, timeout=20)
        return bool(result.get("ok"))
    except Exception as exc:
        print(f"SPUTNIK Telegram send error: {type(exc).__name__}: {exc}")
        return False


def telegram_menu() -> dict[str, Any]:
    """Pulsantiera persistente SPUTNIK."""
    return {
        "keyboard": [
            [{"text": "🟢 COSA COMPRARE"}],
            [{"text": "📡 SEGNALE CFD"}, {"text": "🎯 STRUMENTO"}],
            [{"text": "📊 DASHBOARD"}, {"text": "🔄 AGGIORNA"}],
            [{"text": "ℹ️ AIUTO"}],
        ],
        "resize_keyboard": True,
        "is_persistent": True,
        "one_time_keyboard": False,
        "input_field_placeholder": "Scegli un'azione…",
    }


def menu_markup() -> dict[str, Any]:
    """Inline keyboard per risposte rapide."""
    return {
        "inline_keyboard": [
            [{"text": "🟢 COSA COMPRARE", "callback_data": "buy"}],
            [
                {"text": "📡 SEGNALE CFD", "callback_data": "segnale"},
                {"text": "🎯 STRUMENTO", "callback_data": "strumento"},
            ],
            [
                {"text": "📊 DASHBOARD", "callback_data": "home"},
                {"text": "🔄 AGGIORNA", "callback_data": "scan"},
            ],
            [{"text": "ℹ️ AIUTO", "callback_data": "help"}],
        ]
    }


def sputnik_home_message(state: dict[str, Any]) -> str:
    rows = rank_purchase_candidates(list((state.get("transactions") or {}).values()), limit=5)
    quotes = state.get("market_quotes") or state.get("quotes") or {}
    findings = list((state.get("intelligence_history") or {}).values())
    catalysts = catalyst_watchlist(findings, limit=5)

    cart = build_cfd_cart(rows, quotes, capital=300.0, risk_pct=1.0, limit=5)
    by_security = {item.get("security"): item for item in cart}

    lines = [
        "🛰️ SPUTNIK — DASHBOARD",
        "━━━━━━━━━━━━━━━━━━",
        "POLITICA → EVIDENZA → CATALIZZATORE → CFD",
        "",
        "🏆 CLASSIFICA OPERATIVA",
    ]

    if rows:
        for row in rows:
            item = by_security.get(row.get("security"))
            status = "🟢 TRADE" if item and item.get("status") == "TRADE" else "🟡 WAIT"
            lines.append(f'{row["rank"]}. {status} {row["security"]} — {row["score"]}/100')
            lines.append(f'   {row["signal"]} | Filing {row["filings"]} | Recenza {row["recency"]}/10')
            if item and item.get("status") == "TRADE":
                lines.append(
                    f'   Entry {item["entry"]} | SL {item["stop"]} | TP {item["target"]} | '
                    f'R/R {item["rr"]} | Size {item["units"]}'
                )
            elif item:
                lines.append(f'   WAIT: {item["reason"]}')
            else:
                lines.append("   WAIT: quotazione CFD non disponibile.")
    else:
        lines.append("⚪ Nessun candidato SEC verificabile.")

    lines.extend(["", "🎯 CATALIZZATORI"])
    if catalysts:
        for row in catalysts:
            lines.append(
                f'🟡 {row["instrument"]} — {row["score"]}/100 | WATCH | '
                f'{", ".join(row["domains"])}'
            )
    else:
        lines.append("⚪ Nessun catalizzatore verificabile.")

    lines.extend([
        "",
        "🛒 CARRELLO CFD: €300 | rischio modello 1% per candidato.",
        "⚠️ Entry/SL/TP/Size compaiono solo con dati verificabili.",
        "⚠️ Nessuna inferenza di transazioni private o intenzioni personali.",
    ])
    return "\n".join(lines)


def catalyst_watch_message(state: dict[str, Any]) -> str:
    findings = list((state.get("intelligence_history") or {}).values())
    rows = catalyst_watchlist(findings, limit=8)
    lines = ["🛰️ SPUTNIK — CATALIZZATORI CFD", "━━━━━━━━━━━━━━━━━━"]
    if not rows:
        lines.append("⚪ Nessun catalizzatore verificabile disponibile.")
        return "\n".join(lines)
    for i, row in enumerate(rows, 1):
        lines.append("{} 🟡 {} — {}/100".format(i, row["instrument"], row["score"]))
        lines.append("   {} | {}".format(row["description"], ", ".join(row["domains"])))
        lines.append("   Fonti: {} | Eventi: {}".format(", ".join(row["sources"]), row["events"]))
        lines.append("   {}".format(row["reason"]))
    lines.extend(["", "⚠️ WATCHLIST: non è un ordine e non implica BUY/SELL.", "🎯 Il passaggio a CFD richiede poi una quotazione verificabile + SL + TP."])
    return "\n".join(lines)


def cfd_cart_message(state: dict[str, Any], capital: float = 300.0) -> str:
    rows = rank_purchase_candidates(list((state.get("transactions") or {}).values()), limit=5)
    quotes = state.get("market_quotes") or state.get("quotes") or {}
    cart = build_cfd_cart(rows, quotes, capital=capital, risk_pct=1.0, limit=3)
    lines = [
        "🛒 SPUTNIK — CARRELLO CFD (€{:.0f})".format(capital),
        "━━━━━━━━━━━━━━━━━━",
        "🎯 Base: evidenze pubbliche SPUTNIK",
        "⚠️ Un CFD entra nel carrello solo con prezzo + SL + TP forniti dal motore dati.",
    ]
    if not cart:
        lines.append("⚪ Nessun candidato disponibile.")
        return "\n".join(lines)
    for i, item in enumerate(cart, 1):
        status = "🟢 TRADE" if item["status"] == "TRADE" else "🟡 WAIT"
        lines.append("{} {} — {} / {}".format(i, status, item["security"], item["company"]))
        lines.append("   Evidenza: {}/100 | {}".format(item["score"], item["evidence_signal"]))
        if item["status"] == "TRADE":
            lines.append("   LONG | Entry {} | SL {} | TP {} | R/R {} | Size {}".format(item["entry"], item["stop"], item["target"], item["rr"], item["units"]))
            lines.append("   Rischio massimo modello: €{:.2f}".format(item["risk_eur"]))
        else:
            lines.append("   {}".format(item["reason"]))
    lines.extend(["", "ℹ️ Il carrello non trasforma una notizia politica in un ordine automatico.", "ℹ️ Nessuna posizione SHORT viene inferita da acquisti Form 4."])
    return "\n".join(lines)


def anticipation_message(state: dict[str, Any]) -> str:
    findings = list((state.get("intelligence_history") or {}).values())
    rows = anticipatory_selector(findings, limit=5)
    history = build_public_history(findings, state.get("public_history") or [])
    lines = ["🛰️ SPUTNIK — ANTICIPO", "━━━━━━━━━━━━━━━━━━", f"📚 Storico eventi pubblici: {len(history)} | Amministrazione core: {len(CORE_ADMINISTRATION)}", ""]
    if not rows:
        lines.append("⚪ Nessun segnale anticipatorio verificabile sopra soglia.")
    else:
        for i, row in enumerate(rows, 1):
            lines.extend([
                f'{i}. 🔵 {row["domain"]} — {row["score"]}/100 | ANTICIPA',
                f'   Eventi: {row["events"]} | Fonti: {", ".join(row["sources"])}',
                f'   {row["reason"]}',
            ])
    lines.extend(["", "⚠️ ANTICIPA ≠ COMPRA: il selettore può segnalare prima del Form 4, ma non inventa Entry/SL/TP.", "⚠️ Storico basato solo su informazioni pubbliche documentate."])
    return "\n".join(lines)


def action_reaction_result(state: dict[str, Any]) -> str:
    """Build a useful result from persisted findings, including legacy rows without text."""
    findings = list((state.get("intelligence_history") or {}).values())
    findings.sort(key=lambda row: str(row.get("detected_at") or ""), reverse=True)
    latest = findings[0] if findings else {}
    evidence_row = next(
        (row for row in findings if str(row.get("text") or row.get("snippet") or "").strip()),
        latest,
    )
    body = str(evidence_row.get("text") or evidence_row.get("snippet") or "").strip()
    url = str(evidence_row.get("url") or "")
    if not body and url:
        try:
            body = fetch_public_text(url)[:12000]
        except Exception as exc:
            print(f"SPUTNIK decision source refresh failed: {type(exc).__name__}")
    domains = evidence_row.get("domains") or []
    evidence_text = " ".join([body, " ".join(str(x) for x in domains)]).strip()
    source = str(evidence_row.get("source") or "Fonti pubbliche")
    if url:
        source = f"{source} — {url}"
    quotes = state.get("market_quotes") or state.get("quotes") or {}
    return decision_message(evidence_text, source, quotes=quotes)


def answer_for_callback(callback: str, state: dict[str, Any]) -> str:
    if callback == "home":
        return sputnik_home_message(state)
    if callback in {"strumento", "strumento_da_tradare"}:
        try:
            from sputnik_trading_instrument import recommend_trading_instrument, format_trading_instrument_message
            recent = list((state.get("intelligence_history") or {}).values())[-30:]
            rec = recommend_trading_instrument(recent)
            return format_trading_instrument_message(rec)
        except Exception as exc:
            return f"🛰️ SPUTNIK — STRUMENTO\n━━━━━━━━━━━━━━━━━━\n⚠️ Errore: {type(exc).__name__}"
    if callback in {"segnale", "cfd_signal", "segnale_cfd"}:
        try:
            from sputnik_trading_instrument import recommend_trading_instrument
            from sputnik_cfd import build_cfd_signal, format_cfd_signal
            recent = list((state.get("intelligence_history") or {}).values())[-30:]
            rec = recommend_trading_instrument(recent)
            quotes = state.get("market_quotes") or state.get("quotes") or {}
            signal = build_cfd_signal(rec, quotes)
            return format_cfd_signal(signal)
        except Exception as exc:
            return f"🛰️ SPUTNIK — SEGNALE CFD\n━━━━━━━━━━━━━━━━━━\n⚠️ Errore: {type(exc).__name__}"
    if callback == "action_reaction":
        return action_reaction_result(state)
    if callback == "cfd":
        return cfd_cart_message(state)
    if callback == "catalysts":
        return catalyst_watch_message(state)
    if callback == "anticipation":
        return anticipation_message(state)
    if callback == "aggressive":
        return aggressive_message(state)
    if callback in {"ranking", "buy"}:
        rows = rank_purchase_candidates(list((state.get("transactions") or {}).values()), limit=5)
        if not rows:
            return "🛰️ SPUTNIK — CLASSIFICA\n━━━━━━━━━━━━━━━━━━\n⚪ Nessun candidato verificabile con i dati pubblici disponibili."
        lines=["🛰️ SPUTNIK — " + ("COSA COMPRARE" if callback=="buy" else "CLASSIFICA"),"━━━━━━━━━━━━━━━━━━"]
        for row in rows:
            emoji="🟢" if row["signal"]=="COMPRA" else ("🟡" if row["signal"]=="OSSERVA" else "🔴")
            lines += [f'{row["rank"]}. {emoji} {row["security"]} — {row["company"]}',f'   {row["score"]}/100 | {row["signal"]}',f'   Filing: {row["filings"]} | Recenza: {row["recency"]}/10',f'   {row["reason"]}']
        lines += ["","⚠️ Classifica basata solo su evidenze pubbliche verificabili."]
        return "\n".join(lines)
    if callback=="news": return telegram_news_message(state)
    if callback=="brief": return telegram_brief_message(state)
    if callback=="purchases": return telegram_purchases_message(state)
    if callback=="filings": return telegram_filings_message(state)
    if callback=="sectors":
        return (
            "🛰️ SPUTNIK — SETTORI / IMPATTO\n━━━━━━━━━━━━━━━━━━\n"
            "🏛️ Trump / White House → eventi documentati\n"
            "↓\n"
            "🏭 Settori esposti → società interessate\n"
            "↓\n"
            "📈 Prezzo + insider + filing → verifica del segnale\n\n"
            "ℹ️ L'impatto settoriale viene mostrato come analisi, non come previsione certa."
        )
    if callback=="analysis":
        rows = rank_purchase_candidates(list((state.get("transactions") or {}).values()), limit=3)
        if not rows:
            return "🛰️ SPUTNIK — ANALISI\n━━━━━━━━━━━━━━━━━━\n⚪ Dati insufficienti per un'analisi verificabile."
        lines=["🛰️ SPUTNIK — ANALISI","━━━━━━━━━━━━━━━━━━","🔎 Incrocio: SEC + filing + recenza"]
        for row in rows:
            lines.append(f'{row["security"]} — {row["company"]}: {row["score"]}/100 ({row["signal"]})')
        return "\n".join(lines)
    if callback=="status": return "🛰️ SPUTNIK — STATO\n━━━━━━━━━━━━━━━━━━\n📡 Telegram: ONLINE\n🟢 Motore: GitHub Actions\n📡 Fonte: SEC EDGAR"
    if callback=="help": return telegram_help_message()
    if callback=="scan": return "🔄 SPUTNIK — AGGIORNAMENTO\n━━━━━━━━━━━━━━━━━━\n📡 Raccolta dati affidata al motore GitHub Actions.\n⏳ Attendi il prossimo snapshot."
    return "🛰️ SPUTNIK"


def remote_state() -> dict[str, Any]:
    try:
        req = urllib.request.Request(
            REMOTE_STATE_URL,
            headers={"User-Agent": "SPUTNIK Telegram listener/1.0"},
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
            if isinstance(data, dict):
                return data
    except Exception as exc:
        print(f"SPUTNIK remote state unavailable: {type(exc).__name__}")
    return {}


def dispatch(message: dict[str, Any]) -> None:
    chat = message.get("chat") or {}
    chat_id = str(chat.get("id", ""))
    if str(chat.get("type", "")) != "private" or not chat_id:
        return

    command = " ".join(str(message.get("text", "")).strip().lower().split())
    command_key = command.rstrip("?!.,:;")
    if not command:
        return

    if command == "/start":
        LOCAL_STATE["chat_id"] = chat_id
        LOCAL_STATE["active"] = True
        save_local_state(LOCAL_STATE)
        send("🛰️ SPUTNIK attivo. Usa i pulsanti qui sotto.", chat_id=chat_id, reply_markup=telegram_menu())
        return

    # Map button texts and commands
    command_map = {
        "/start": "home",
        "/help": "help",
        "🟢 cosa comprare": "buy",
        "📡 segnale cfd": "segnale",
        "🎯 strumento": "strumento",
        "📊 dashboard": "home",
        "🔄 aggiorna": "scan",
        "ℹ️ aiuto": "help",
        "cosa comprare": "buy",
        "segnale": "segnale",
        "strumento": "strumento",
        "dashboard": "home",
        "aggiorna": "scan",
        "aiuto": "help",
    }

    callback = command_map.get(command_key, "home")
    try:
        reply = answer_for_callback(callback, remote_state())
        send(reply, chat_id=chat_id, reply_markup=telegram_menu())
    except Exception as exc:
        print(f"Dispatch error: {exc}")
        send("⚠️ Errore temporaneo.", chat_id=chat_id)
