"""Entry point for the scheduled SPUTNIK WTI state-change alert."""
from __future__ import annotations

import os

from sputnik_wti_alert import check_and_send
from trump_tracker import load_state, save_state, send_telegram


def main() -> None:
    state = load_state()
    chat_id = str(state.get("telegram_chat_id") or os.getenv("TELEGRAM_CHAT_ID") or "").strip()
    result = check_and_send(
        state,
        lambda message: send_telegram(message, chat_id=chat_id or None),
    )
    if result == "SENT":
        save_state(state)


if __name__ == "__main__":
    main()
