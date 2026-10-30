import unittest

from telegram_delivery import confirmed_message_id


class TelegramDeliveryConfirmationTests(unittest.TestCase):
    def test_accepts_explicit_success_with_positive_message_id(self):
        self.assertEqual(
            confirmed_message_id({"ok": True, "result": {"message_id": 731}}),
            731,
        )

    def test_rejects_api_failure(self):
        self.assertIsNone(
            confirmed_message_id({"ok": False, "description": "chat not found"})
        )

    def test_rejects_success_without_result_or_message_id(self):
        self.assertIsNone(confirmed_message_id({"ok": True}))
        self.assertIsNone(confirmed_message_id({"ok": True, "result": {}}))

    def test_rejects_non_integer_or_non_positive_message_id(self):
        for message_id in ("731", True, 0, -1, None):
            with self.subTest(message_id=message_id):
                self.assertIsNone(
                    confirmed_message_id({"ok": True, "result": {"message_id": message_id}})
                )

    def test_rejects_truthy_non_boolean_ok_values(self):
        self.assertIsNone(
            confirmed_message_id({"ok": "true", "result": {"message_id": 731}})
        )


if __name__ == "__main__":
    unittest.main()
