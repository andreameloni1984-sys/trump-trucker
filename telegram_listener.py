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


def send(text: str, chat_id: str | None = None) -> bool:
    target = str(chat_id or LOCAL_STATE.get("chat_id") or "").strip()
    if not target:
        return False
    try:
        result = api("sendMessage", {"chat_id": target, "text": text}, timeout=20)
        return bool(result.get("ok"))
    except Exception as exc:
        print(f"SPUTNIK Telegram send error: {type(exc).__name__}: {exc}")
        return False


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
            "🎯 Oppure scrivi: Trump ordina",
            chat_id,
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

    if command in {"trump ordina", "trump cosa compro", "trump cosa comprare"}:
        send(telegram_trump_order_message(state), chat_id)
    elif command == "/help":
        send(telegram_help_message(), chat_id)
    elif command == "/filings":
        send(telegram_filings_message(state), chat_id)
    elif command == "/transactions":
        send(telegram_transactions_message(state), chat_id)
    elif command == "/purchases":
        send(telegram_purchases_message(state), chat_id)
    elif command == "/sales":
        send(telegram_sales_message(state), chat_id)
    elif command == "/positions":
        send(telegram_positions_message(state), chat_id)
    elif command == "/news":
        send(telegram_news_message(state), chat_id)
    elif command == "/brief":
        send(telegram_brief_message(state), chat_id)
    elif command == "/status":
        send(
            "🛰️ SPUTNIK — STATO\n━━━━━━━━━━━━━━━━━━\n"
            "📡 Telegram: ONLINE\n"
            "🟢 Listener: PERMANENTE\n"
            "🔎 Motore: GitHub Actions\n"
            "📡 Fonte principale: SEC EDGAR\n"
            "🎯 Comando naturale: Trump ordina",
            chat_id,
        )
    elif command == "/test":
        send(telegram_test_message(), chat_id)
    elif command == "/scan":
        send(
            "🛰️ SPUTNIK — SCAN\n━━━━━━━━━━━━━━━━━━\n"
            "🔎 Il comando è ricevuto dal listener.\n"
            "📡 La raccolta SEC viene eseguita dal motore GitHub Actions.",
            chat_id,
        )


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
                    "allowed_updates": ["message"],
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
