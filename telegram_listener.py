"""Persistent SPUTNIK Telegram listener.

Telegram transport is deliberately separated from the GitHub Actions collector.
GitHub Actions periodically bootstraps the bot token and pings /health so a free
Render web service stays awake. The listener owns the single getUpdates session.
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
from sputnik_history import anticipatory_selector, build_public_history, CORE_ADMINISTRATION
from trump_tracker import (
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

BOT_TOKEN = ""
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
    return {
        "keyboard": [
            [{"text": "🏠 HOME"}, {"text": "🏆 CLASSIFICA"}],
            [{"text": "🟢 COSA COMPRARE"}, {"text": "🛒 CARRELLO CFD"}],
            [{"text": "🎯 CATALIZZATORI"}, {"text": "🏛️ TRUMP / WHITE HOUSE"}],
            [{"text": "📰 NEWS"}, {"text": "🧾 SEC / OGE"}],
            [{"text": "📊 SETTORI / IMPATTO"}, {"text": "🔎 ANALISI"}],
            [{"text": "💰 ACQUISTI"}, {"text": "🔄 AGGIORNA"}],
            [{"text": "⚙️ STATO"}, {"text": "ℹ️ AIUTO"}],
        ],
        "resize_keyboard": True,
        "is_persistent": True,
        "input_field_placeholder": "SPUTNIK • scegli un'operazione",
    }





def sputnik_home_message(state: dict[str, Any]) -> str:
    rows = rank_purchase_candidates(list((state.get("transactions") or {}).values()), limit=5)
    quotes = state.get("market_quotes") or state.get("quotes") or {}
    findings = list((state.get("intelligence_history") or {}).values())
    catalysts = catalyst_watchlist(findings, limit=5)

    # Build an operational dashboard without fabricating market levels.
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
            lines.extend([f"{i}. 🔵 {row["domain"]} — {row["score"]}/100 | ANTICIPA", f"   Eventi: {row["events"]} | Fonti: {", ".join(row["sources"])}", f"   {row["reason"]}"])
    lines.extend(["", "⚠️ ANTICIPA ≠ COMPRA: il selettore può segnalare prima del Form 4, ma non inventa Entry/SL/TP.", "⚠️ Storico basato solo su informazioni pubbliche documentate."])
    return "\n".join(lines)


def menu_markup() -> dict[str, Any]:
    """SPUTNIK dashboard: Commodities-style inline control panel."""
    return {
        "inline_keyboard": [
            [{"text": "🏠 HOME", "callback_data": "home"}],
            [{"text": "🟢 COSA COMPRARE", "callback_data": "buy"},
             {"text": "🔵 ANTICIPO", "callback_data": "anticipation"}],
            [{"text": "🏆 CLASSIFICA", "callback_data": "ranking"}],
            [{"text": "🛒 CARRELLO CFD", "callback_data": "cfd"},
             {"text": "🎯 CATALIZZATORI", "callback_data": "catalysts"}],
            [{"text": "🏛️ TRUMP / WHITE HOUSE", "callback_data": "brief"},
             {"text": "📰 NEWS", "callback_data": "news"}],
            [{"text": "🧾 SEC / OGE", "callback_data": "filings"},
             {"text": "💰 ACQUISTI", "callback_data": "purchases"}],
            [{"text": "📊 SETTORI / IMPATTO", "callback_data": "sectors"},
             {"text": "🔎 ANALISI", "callback_data": "analysis"}],
            [{"text": "🔄 AGGIORNA", "callback_data": "scan"},
             {"text": "⚙️ STATO", "callback_data": "status"}],
            [{"text": "ℹ️ AIUTO", "callback_data": "help"}],
        ]
    }


def answer_for_callback(callback: str, state: dict[str, Any]) -> str:
    if callback == "home":
        return sputnik_home_message(state)
    if callback == "cfd":
        return cfd_cart_message(state)
    if callback == "catalysts":
        return catalyst_watch_message(state)
    if callback == "anticipation":
        return anticipation_message(state)
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
    if callback=="status": return "🛰️ SPUTNIK — STATO\n━━━━━━━━━━━━━━━━━━\n📡 Telegram: ONLINE\n🟢 Listener: PERMANENTE\n🔎 Motore: GitHub Actions\n📡 Fonte: SEC EDGAR"
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
        send(
            "🛰️ SPUTNIK ATTIVO\n━━━━━━━━━━━━━━━━━━\n"
            "✅ Telegram collegato al listener permanente.\n"
            "📡 Motore dati: GitHub Actions.\n"
            "🔐 Questa chat privata è autorizzata.\n"
            "⏱️ Puoi usare /status /test /brief /filings /transactions /purchases /sales /positions /news /help\n"
            "🎯 Usa il menu qui sotto oppure scrivi: Trump ordina",
            chat_id,
            reply_markup=telegram_menu(),
        )
        return

    if chat_id != str(LOCAL_STATE.get("chat_id") or ""):
        return

    if command == "/stop":
        LOCAL_STATE["active"] = False
        save_local_state(LOCAL_STATE)
        send("🛰️ SPUTNIK FERMATO\n━━━━━━━━━━━━━━━━━━\n⛔ Monitoraggio Telegram sospeso.", chat_id)
        return

    if not LOCAL_STATE.get("active", True):
        return

    state = remote_state()
    if not state:
        state = {"telegram_active": True}

    if command in {"carrello cfd", "carrello cfd 300"}:
        send(cfd_cart_message(state, 300.0), chat_id, reply_markup=telegram_menu())
    elif command_key in {
        "cosa compro",
        "cosa compro oggi",
        "cosa comprare",
        "cosa comprare oggi",
        "cosa acquistare",
        "cosa acquistare oggi",
        "quale compro",
        "quale compro oggi",
        "quale azione compro",
        "quale azione comprare",
        "trump ordina",
        "trump cosa compro",
        "trump cosa comprare",
        "/ranking",
    }:
        rows = rank_purchase_candidates(
            list((state.get("transactions") or {}).values()),
            limit=5,
        )
        if not rows:
            send(
                "🛰️ SPUTNIK — CLASSIFICA\n━━━━━━━━━━━━━━━━━━\n"
                "⚪ NESSUN CANDIDATO\n"
                "Dati pubblici insufficienti per costruire una classifica verificabile.",
                chat_id,
            )
        else:
            lines = [
                "🛰️ SPUTNIK — CLASSIFICA",
                "━━━━━━━━━━━━━━━━━━",
                "🎯 Cosa osservare secondo le evidenze pubbliche:",
            ]
            for row in rows:
                emoji = "🟢" if row["signal"] == "COMPRA" else ("🟡" if row["signal"] == "OSSERVA" else "🔴")
                lines.extend([
                    f'{row["rank"]}. {emoji} {row["security"]} — {row["company"]}',
                    f'   Voto: {row["score"]}/100 | {row["signal"]}',
                    f'   Fonti: SEC primaria | Filing distinti: {row["filings"]}',
                    f'   Recenza: {row["recency"]}/10',
                    f'   {row["reason"]}',
                ])
            lines.extend([
                "",
                "⚠️ Il voto misura solo evidenza pubblica disponibile.",
                "⚠️ Non prova rendimento futuro, intenzioni o transazioni private.",
            ])
            send("\n".join(lines), chat_id, reply_markup=telegram_menu())
    elif command == "🎯 catalizzatori":
        send(catalyst_watch_message(state), chat_id, reply_markup=telegram_menu())
    elif command == "🛒 carrello cfd":
        send(cfd_cart_message(state), chat_id, reply_markup=telegram_menu())
    elif command == "🏠 home":
        send(sputnik_home_message(state), chat_id, reply_markup=telegram_menu())
    elif command == "🏆 classifica":
        send(answer_for_callback("ranking", state), chat_id, reply_markup=telegram_menu())
    elif command == "🟢 cosa comprare":
        send(answer_for_callback("buy", state), chat_id, reply_markup=telegram_menu())
    elif command == "🔵 anticipo":
        send(anticipation_message(state), chat_id, reply_markup=telegram_menu())
    elif command == "💰 acquisti":
        send(telegram_purchases_message(state), chat_id, reply_markup=telegram_menu())
    elif command in {"🧾 filings sec", "🧾 sec / oge"}:
        send(answer_for_callback("filings", state), chat_id, reply_markup=telegram_menu())
    elif command == "📊 settori / impatto":
        send(answer_for_callback("sectors", state), chat_id, reply_markup=telegram_menu())
    elif command == "🔎 analisi":
        send(answer_for_callback("analysis", state), chat_id, reply_markup=telegram_menu())
    elif command == "📰 news":
        send(telegram_news_message(state), chat_id, reply_markup=telegram_menu())
    elif command == "🏛️ trump / white house":
        send(telegram_brief_message(state), chat_id, reply_markup=telegram_menu())
    elif command == "📊 brief":
        send(telegram_brief_message(state), chat_id, reply_markup=telegram_menu())
    elif command == "🔄 aggiorna":
        send(answer_for_callback("scan", state), chat_id, reply_markup=telegram_menu())
    elif command == "⚙️ stato":
        send(answer_for_callback("status", state), chat_id, reply_markup=telegram_menu())
    elif command == "ℹ️ aiuto":
        send(telegram_help_message(), chat_id, reply_markup=telegram_menu())
    elif command in {"/help"}:
        send(telegram_help_message(), chat_id, reply_markup=menu_markup())
    elif command == "/filings":
        send(telegram_filings_message(state), chat_id)
    elif command == "/transactions":
        send(telegram_transactions_message(state), chat_id)
    elif command in {"/purchases", "💰 acquisti"}:
        send(telegram_purchases_message(state), chat_id)
    elif command == "/sales":
        send(telegram_sales_message(state), chat_id)
    elif command == "/positions":
        send(telegram_positions_message(state), chat_id)
    elif command in {"/news", "📰 news"}:
        send(telegram_news_message(state), chat_id)
    elif command in {"/brief", "📊 brief", "🏛️ trump / white house"}:
        send(telegram_brief_message(state), chat_id)
    elif command in {"/status", "⚙️ stato"}:
        send(
            "🛰️ SPUTNIK — STATO\n━━━━━━━━━━━━━━━━━━\n"
            "📡 Telegram: ONLINE\n"
            "🟢 Listener: PERMANENTE\n"
            "🔎 Motore: GitHub Actions\n"
            "📡 Fonte principale: SEC EDGAR\n"
            "🎯 Comando naturale: Trump ordina /ranking",
            chat_id,
        )
    elif command == "/test":
        send(telegram_test_message(), chat_id)
    elif command in {"/scan", "🔄 aggiorna"}:
        send(
            "🛰️ SPUTNIK — SCAN\n━━━━━━━━━━━━━━━━━━\n"
            "🔎 Il comando è ricevuto dal listener.\n"
            "📡 La raccolta SEC viene eseguita dal motore GitHub Actions.",
            chat_id,
        )



def dispatch_callback(query: dict[str, Any]) -> None:
    data = str(query.get("data") or "")
    message = query.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = str(chat.get("id", ""))
    if not chat_id or chat_id != str(LOCAL_STATE.get("chat_id") or ""):
        return
    try:
        api("answerCallbackQuery", {"callback_query_id": str(query.get("id"))}, timeout=10)
        state = remote_state() or {"telegram_active": True}
        text = answer_for_callback(data, state)
        api("editMessageText", {"chat_id": chat_id, "message_id": message.get("message_id"), "text": text, "reply_markup": menu_markup()}, timeout=20)
    except Exception as exc:
        print(f"SPUTNIK callback error: {type(exc).__name__}: {exc}")


def poll_loop() -> None:
    global BOT_TOKEN
    last_token = ""
    while not STOP_EVENT.is_set():
        with BOT_LOCK:
            token = BOT_TOKEN
        if not token:
            time.sleep(2)
            continue

        if token != last_token:
            last_token = token
            try:
                api("deleteWebhook", {"drop_pending_updates": False}, timeout=15)
                print("SPUTNIK: webhook Telegram disattivato; listener permanente pronto.")
            except Exception as exc:
                print(f"SPUTNIK: deleteWebhook error: {type(exc).__name__}")

        try:
            result = api(
                "getUpdates",
                {
                    "offset": int(LOCAL_STATE.get("offset", 0) or 0),
                    "timeout": POLL_TIMEOUT,
                    "allowed_updates": ["message", "callback_query"],
                },
                timeout=POLL_TIMEOUT + 10,
            )
            if not result.get("ok"):
                print(f"SPUTNIK: Telegram API error: {result.get('description', 'unknown')}")
                time.sleep(2)
                continue

            updates = result.get("result") or []
            for update in updates:
                update_id = int(update.get("update_id", 0))
                LOCAL_STATE["offset"] = max(int(LOCAL_STATE.get("offset", 0) or 0), update_id + 1)
                save_local_state(LOCAL_STATE)
                
                if update.get("callback_query"):
                    dispatch_callback(update["callback_query"])
                else:
                    dispatch(update.get("message") or {})
        except urllib.error.HTTPError as exc:
            print(f"SPUTNIK: Telegram HTTP {exc.code}")
            time.sleep(3)
        except Exception as exc:
            print(f"SPUTNIK: Telegram listener error: {type(exc).__name__}: {exc}")
            time.sleep(3)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        if self.path in {"/", "/health"}:
            body = b'{"status":"ok","service":"sputnik-telegram-listener"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        global BOT_TOKEN
        if self.path != "/bootstrap":
            self.send_response(404)
            self.end_headers()
            return

        token = self.headers.get("X-Telegram-Bot-Token", "").strip()
        if not token or ":" not in token:
            self.send_response(400)
            self.end_headers()
            return

        with BOT_LOCK:
            BOT_TOKEN = token
            os.environ["TELEGRAM_BOT_TOKEN"] = token
        print("SPUTNIK: Telegram bootstrap ricevuto; listener autorizzato.")

        body = b'{"status":"bootstrapped"}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    thread = threading.Thread(target=poll_loop, daemon=True)
    thread.start()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"SPUTNIK: Telegram listener HTTP online on port {PORT}.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        STOP_EVENT.set()
        server.server_close()


if __name__ == "__main__":
    main()
