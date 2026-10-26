import ast
import unittest
from pathlib import Path


class SputnikTelegramMenuTests(unittest.TestCase):
    def test_listener_parses_and_contains_persistent_home(self):
        source = Path("telegram_listener.py").read_text(encoding="utf-8")
        ast.parse(source)

        required_labels = (
            "🏆 CLASSIFICA",
            "🟢 COSA COMPRARE",
            "🛒 CARRELLO CFD",
            "🎯 CATALIZZATORI",
            "📰 NEWS",
            "🏛️ TRUMP / WHITE HOUSE",
            "💰 ACQUISTI",
            "🧾 SEC / OGE",
            "📊 SETTORI / IMPATTO",
            "🔎 ANALISI",
            "🔄 AGGIORNA",
            "⚙️ STATO",
            "ℹ️ AIUTO",
        )
        for label in required_labels:
            self.assertIn(label, source)
        self.assertIn('"POLITICA → EVIDENZA → CATALIZZATORE → CFD"', source)
        self.assertIn('def sputnik_home_message', source)
        self.assertIn('def bootstrap_state', source)
        self.assertIn('X-Telegram-Bot-Token', source)
        self.assertIn('X-Telegram-Chat-Id', source)
        self.assertIn('"telegram_configured"', source)
        self.assertIn('"authorized_chat"', source)
        self.assertIn('def menu_markup', source)
        self.assertIn('"inline_keyboard":', source)
        self.assertIn('"callback_data": "buy"', source)
        self.assertIn('"callback_data": "cfd"', source)
        self.assertIn('"callback_data": "anticipation"', source)
        self.assertIn('def anticipation_message', source)
        self.assertIn('🏆 CLASSIFICA OPERATIVA', source)
        self.assertIn('Entry {item["entry"]}', source)
        self.assertIn('WAIT: quotazione CFD non disponibile.', source)

        self.assertIn('"is_persistent": True', source)
        self.assertIn('reply_markup=telegram_menu()', source)
        self.assertNotIn('reply_markup=menu_markup(),', source.split('if command == "/start":', 1)[1].split('if chat_id !=', 1)[0])

    def test_home_buttons_have_dispatch_paths(self):
        source = Path("telegram_listener.py").read_text(encoding="utf-8")
        for command in (
            'command == "🏠 home"',
            'command == "🧾 filings sec"',
            'command == "🧾 sec / oge"',
            'command_key in {',
            '"cosa compro oggi"',
            '"cosa comprare oggi"',
            '"quale compro oggi"',
            'command == "🏆 classifica"',
            'command == "🟢 cosa comprare"',
            'command == "🧾 filings sec"',
            'command == "📊 settori / impatto"',
            'command == "🔎 analisi"',
            'command == "🔄 aggiorna"',
            'command == "⚙️ stato"',
            'command == "ℹ️ aiuto"',
        ):
            self.assertIn(command, source)

    def test_help_contains_complete_command_list(self):
        help_source = Path("trump_tracker.py").read_text(encoding="utf-8")
        for label in ("🏠 HOME", "🏆 CLASSIFICA", "🟢 COSA COMPRARE", "🛒 CARRELLO CFD", "🎯 CATALIZZATORI", "🏛️ TRUMP / WHITE HOUSE", "📰 NEWS", "🧾 SEC / OGE", "📊 SETTORI / IMPATTO", "🔎 ANALISI", "💰 ACQUISTI", "🔄 AGGIORNA", "⚙️ STATO", "ℹ️ AIUTO"):
            self.assertIn(label, help_source)
        for command in ("/start", "/stop", "/status", "/test", "/scan", "/filings", "/transactions", "/purchases", "/sales", "/news", "/brief", "/help"):
            self.assertIn(command, help_source)


    def test_update_offset_is_not_committed_when_dispatch_raises(self):
        from unittest.mock import patch
        import telegram_listener as listener

        with patch.object(listener, "LOCAL_STATE", {"offset": 10}) as state, \
             patch.object(listener, "save_local_state") as save, \
             patch.object(listener, "dispatch", side_effect=RuntimeError("dispatch failed")):
            with self.assertRaises(RuntimeError):
                listener._dispatch_update_and_ack({"update_id": 10, "message": {"text": "hi"}})
            self.assertEqual(state["offset"], 10)
            save.assert_not_called()

    def test_update_offset_is_committed_after_successful_dispatch(self):
        from unittest.mock import patch
        import telegram_listener as listener

        with patch.object(listener, "LOCAL_STATE", {"offset": 10}) as state, \
             patch.object(listener, "save_local_state") as save, \
             patch.object(listener, "dispatch") as dispatch:
            listener._dispatch_update_and_ack({"update_id": 10, "message": {"text": "hi"}})
            dispatch.assert_called_once_with({"text": "hi"})
            self.assertEqual(state["offset"], 11)
            save.assert_called_once_with(state)



    def test_local_state_normalizer_recovers_corrupt_cursor_and_fails_closed(self):
        source = Path("telegram_listener.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        node = next(
            item for item in tree.body
            if isinstance(item, ast.FunctionDef) and item.name == "_normalise_local_state"
        )
        isolated = ast.Module(body=[node], type_ignores=[])
        namespace = {"Any": object}
        exec(compile(isolated, "<sputnik-state-normalizer>", "exec"), namespace)
        normalise = namespace["_normalise_local_state"]

        self.assertEqual(
            normalise({"offset": "-9", "chat_id": " 123 ", "active": "false"}),
            {"offset": 0, "chat_id": "123", "active": False},
        )
        self.assertEqual(
            normalise({"offset": "not-an-integer", "chat_id": None, "active": "maybe"}),
            {"offset": 0, "chat_id": "", "active": False},
        )
        self.assertEqual(
            normalise({"offset": "42", "chat_id": 12345, "active": True}),
            {"offset": 42, "chat_id": "12345", "active": True},
        )
        self.assertEqual(
            normalise(["corrupt-json-shape"]),
            {"offset": 0, "chat_id": "", "active": True},
        )


if __name__ == "__main__":
    unittest.main()
