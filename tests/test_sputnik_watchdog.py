import unittest
from datetime import datetime, timedelta, timezone

import sputnik_watchdog as wd

MON_14 = datetime(2026, 11, 23, 14, 0, tzinfo=timezone.utc)


def run(minutes_ago, conclusion="success", status="completed"):
    return {"created_at": (MON_14 - timedelta(minutes=minutes_ago)).isoformat().replace("+00:00", "Z"),
            "status": status, "conclusion": conclusion, "html_url": "https://x"}


class WatchdogTests(unittest.TestCase):
    def check(self, name):
        return next(c for c in wd.CHECKS if name in c.name)

    def test_regular(self):
        self.assertIsNone(wd.diagnose(self.check("Trump"), [run(10), run(25)], MON_14))

    def test_stopped(self):
        self.assertIn("non parte", wd.diagnose(self.check("Trump"), [run(200)], MON_14))

    def test_two_failures(self):
        self.assertIn("fallite", wd.diagnose(self.check("Trump"), [run(5, "failure"), run(20, "failure")], MON_14))
        self.assertIsNone(wd.diagnose(self.check("Trump"), [run(5, "failure"), run(20)], MON_14))

    def test_outside_window_not_stopped(self):
        sunday = datetime(2026, 11, 22, 14, 0, tzinfo=timezone.utc)
        self.assertIsNone(wd.diagnose(self.check("Stella"), [run(60 * 30)], sunday))

    def test_alert_once_then_recovery(self):
        sent = []
        state = {}
        bad = lambda repo, wf: [run(300)]
        wd.run(MON_14, fetch=bad, send=lambda t: sent.append(t) or True, state=state)
        n = len(sent)
        self.assertTrue(any("CANE DA GUARDIA" in t for t in sent))
        wd.run(MON_14 + timedelta(hours=1), fetch=bad, send=lambda t: sent.append(t) or True, state=state)
        self.assertEqual(len(sent), n)  # nessuna ripetizione entro 12 ore
        good = lambda repo, wf: [run(-55)]
        wd.run(MON_14 + timedelta(hours=1), fetch=good, send=lambda t: sent.append(t) or True, state=state)
        self.assertTrue(any("di nuovo regolare" in t for t in sent))
        self.assertEqual(state["alerts"], {})

    def test_unreadable_is_reported(self):
        def boom(repo, wf):
            raise OSError("down")
        sent = []
        wd.run(MON_14, fetch=boom, send=lambda t: sent.append(t) or True, state={})
        self.assertTrue(all("non leggibile" in t for t in sent))


if __name__ == "__main__":
    unittest.main()
