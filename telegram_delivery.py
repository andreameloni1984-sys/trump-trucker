"""Strict acknowledgement helpers for Telegram Bot API sendMessage responses."""

from __future__ import annotations

from typing import Any


def confirmed_message_id(response: Any) -> int | None:
    """Return message_id when Telegram API accepts sendMessage; not a device receipt."""
    if not isinstance(response, dict) or response.get("ok") is not True:
        return None
    result = response.get("result")
    if not isinstance(result, dict):
        return None
    message_id = result.get("message_id")
    if type(message_id) is not int or message_id <= 0:
        return None
    return message_id
