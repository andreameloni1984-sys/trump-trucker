"""
SPUTNIK — Telegram Polling Runner (one-shot)

Alternativa al listener persistente.
Esegue getUpdates, processa i comandi in sospeso usando la logica esistente e termina.
Adatto a GitHub Actions.
"""

from __future__ import annotations

import os
import sys
from typing import Any

try:
    from telegram_listener import (
        api,
        send,
        answer_for_callback,
        remote_state,
        telegram_menu,
    )
except ImportError:
    print("Impossibile importare da telegram_listener.py", flush=True)
    sys.exit(1)


def get_updates(offset: int | None = None) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"timeout": 0, "allowed_updates": ["message", "callback_query"]}
    if offset is not None:
        params["offset"] = offset
    try:
        result = api("getUpdates", params, timeout=15)
        if not result.get("ok"):
            print(f"getUpdates not ok: {result}", flush=True)
            return []
        return result.get("result") or []
    except Exception as exc:
        print(f"getUpdates error: {type(exc).__name__}: {exc}", flush=True)
        return []


def process_message(message: dict[str, Any], state: dict[str, Any]) -> None:
    chat = message.get("chat") or {}
    chat_id = str(chat.get("id", ""))
    text = (message.get("text") or "").strip()

    if not chat_id or not text:
        return

    print(f"Processing message | chat_id={chat_id} | text={text[:80]}", flush=True)

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

    key = text.lower().rstrip("?!.,:;")
    callback = command_map.get(key, "home")

    try:
        reply = answer_for_callback(callback, state)
        ok = send(reply, chat_id=chat_id, reply_markup=telegram_menu())
        print(f"Reply sent: {ok}", flush=True)
    except Exception as exc:
        print(f"Error processing message: {type(exc).__name__}: {exc}", flush=True)
        send("⚠️ Errore temporaneo. Riprova tra poco.", chat_id=chat_id)


def main() -> None:
    print("🛰️ SPUTNIK POLLING RUNNER", flush=True)
    print("One-shot — processa update pendenti e termina", flush=True)

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print("TELEGRAM_BOT_TOKEN mancante", flush=True)
        raise SystemExit(1)

    state = remote_state()
    print(f"Remote state loaded: {bool(state)}", flush=True)

    updates = get_updates()
    print(f"Pending updates: {len(updates)}", flush=True)

    max_offset = None
    for update in updates:
        uid = update.get("update_id")
        if uid is not None:
            max_offset = uid + 1 if max_offset is None else max(max_offset, uid + 1)

        message = update.get("message")
        if message:
            process_message(message, state)

        callback_query = update.get("callback_query")
        if callback_query:
            data = str(callback_query.get("data") or "")
            chat_id = str((callback_query.get("message") or {}).get("chat", {}).get("id", ""))
            if chat_id and data:
                try:
                    reply = answer_for_callback(data, state)
                    send(reply, chat_id=chat_id, reply_markup=telegram_menu())
                except Exception as exc:
                    print(f"Callback error: {exc}", flush=True)

    if max_offset is not None:
        get_updates(offset=max_offset)

    print("Polling run completed", flush=True)


if __name__ == "__main__":
    main()
