import ast
import unittest
from pathlib import Path


class SputnikTelegramMenuTests(unittest.TestCase):
    def test_listener_parses_and_contains_menu(self):
        source = Path("telegram_listener.py").read_text(encoding="utf-8")
        ast.parse(source)
        for label in ("🏆 CLASSIFICA", "🟢 COSA COMPRARE", "📰 NEWS", "🏛️ TRUMP / WHITE HOUSE", "💰 ACQUISTI"):
            self.assertIn(label, source)
        self.assertIn("def telegram_menu", source)


if __name__ == "__main__":
    unittest.main()
