"""
SPUTNIK — Telegram Polling Runner (one-shot)

Alternativa al listener persistente.
Esegue getUpdates, processa i comandi in sospeso usando la logica esistente e termina.
Adatto a GitHub Actions.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

# Assicura che la root del repo sia nel path (necessario quando lanciato da Actions)
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from telegram_listener import (
        api,
        send,
        answer_for_callback,
        remote_state,
        telegram_menu,
    )
except ImportError as e:
    print(f"Impossibile importare da telegram_listener.py: {e}", flush=True)
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


def normalize_text(text: str) -> str:
    """Rimuove emoji e normalizza il testo per il matching."""
    # Rimuove la maggior parte degli emoji e simboli
    cleaned = re.sub(r"[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF\u2B00-\u2BFF]+", "", text)
    return " ".join(cleaned.lower().split()).rstrip("?!.,:;")


def process_message(message: dict[str, Any], state: dict[str, Any]) -> None:
    chat = message.get("chat") or {}
    chat_id = str(chat.get("id", ""))
    text = (message.get("text") or "").strip()

    if not chat_id or not text:
        return

    print(f"Processing message | chat_id={chat_id} | text={text[:80]}", flush=True)

    # Gestione speciale per /start
    if text.lower().startswith("/start"):
        welcome = (
            "🛰️ **SPUTNIK attivo**\n\n"
            "Usa i pulsanti qui sotto per interagire:\n"
            "🟢 COSA COMPRARE\n"
            "📡 SEGNALE CFD\n"
            "🎯 STRUMENTO\n"
            "📊 DASHBOARD\n"
            "🔄 AGGIORNA\n"
            "ℹ️ AIUTO"
        )
        ok = send(welcome, chat_id=chat_id, reply_markup=telegram_menu())
        print(f"Welcome sent: {ok}", flush=True)
        return

    # Matching robusto (ignora emoji e case)
    norm = normalize_text(text)
    print(f"Normalized: '{norm}'", flush=True)

    command_map = {
        "/help": "help",
        "cosa comprare": "buy",
        "segnale cfd": "segnale",
        "segnale": "segnale",
        "strumento": "strumento",
        "dashboard": "home",
        "aggiorna": "scan",
        "aiuto": "help",
        "help": "help",
    }

    callback = command_map.get(norm, "home")
    print(f"Mapped to callback: {callback}", flush=True)

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
