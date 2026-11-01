import ast
import unittest
from pathlib import Path


class SputnikTelegramMenuTests(unittest.TestCase):
    def setUp(self):
        self.source = Path("telegram_listener.py").read_text(encoding="utf-8")
        ast.parse(self.source)

    def test_persistent_keyboard_matches_current_menu(self):
        for label in (
            "🟢 COSA COMPRARE",
            "📡 SEGNALE CFD",
            "🎯 STRUMENTO",
            "📊 DASHBOARD",
            "🔄 AGGIORNA",
            "ℹ️ AIUTO",
        ):
            self.assertIn(label, self.source)
        self.assertIn('"is_persistent": True', self.source)
        self.assertIn('"one_time_keyboard": False', self.source)
        self.assertIn('def telegram_menu', self.source)
        self.assertIn('reply_markup=telegram_menu()', self.source)

    def test_each_visible_button_has_a_dispatch_route(self):
        expected_routes = {
            '"🟢 cosa comprare": "buy"',
            '"📡 segnale cfd": "segnale"',
            '"🎯 strumento": "strumento"',
            '"📊 dashboard": "home"',
            '"🔄 aggiorna": "scan"',
            '"ℹ️ aiuto": "help"',
        }
        for route in expected_routes:
            self.assertIn(route, self.source)
        self.assertIn("callback = command_map.get(command_key, \"home\")", self.source)

    def test_home_and_trading_callbacks_are_supported(self):
        for callback in (
            'if callback == "home":',
            'if callback in {"strumento", "strumento_da_tradare"}:',
            'if callback in {"segnale", "cfd_signal", "segnale_cfd"}:',
            'if callback=="help":',
            'if callback=="scan":',
        ):
            self.assertIn(callback, self.source)

    def test_start_sends_persistent_keyboard(self):
        start_block = self.source.split('if command == "/start":', 1)[1]
        start_block = start_block.split("# Map button texts and commands", 1)[0]
        self.assertIn('send("🛰️ SPUTNIK attivo.', start_block)
        self.assertIn("reply_markup=telegram_menu()", start_block)


    def test_dashboard_and_cart_render_bias_setup_and_paper_states_not_wait(self):
        home_block = self.source.split("def sputnik_home_message", 1)[1].split("def catalyst_watch_message", 1)[0]
        cart_block = self.source.split("def cfd_cart_message", 1)[1].split("def anticipation_message", 1)[0]
        self.assertIn("cfd_cart_display_state", self.source)
        for block in (home_block, cart_block):
            self.assertNotIn("WAIT", block)
            self.assertIn("TRADE PAPER", block)
            self.assertIn("NO_DIRECTION", block)


if __name__ == "__main__":
    unittest.main()
