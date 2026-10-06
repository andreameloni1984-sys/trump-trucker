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
            "🧾 FILINGS SEC",
            "📊 SETTORI / IMPATTO",
            "🔎 ANALISI",
            "🔄 AGGIORNA",
            "⚙️ STATO",
            "ℹ️ AIUTO",
        )
        for label in required_labels:
            self.assertIn(label, source)

        self.assertIn('"is_persistent": True', source)
        self.assertIn('reply_markup=telegram_menu()', source)
        self.assertNotIn('reply_markup=menu_markup(),', source.split('if command == "/start":', 1)[1].split('if chat_id !=', 1)[0])

    def test_home_buttons_have_dispatch_paths(self):
        source = Path("telegram_listener.py").read_text(encoding="utf-8")
        for command in (
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


if __name__ == "__main__":
    unittest.main()
