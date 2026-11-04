import unittest

from telegram.sputnik_watch import build_watch_message


class SputnikWatchScopeTests(unittest.TestCase):
    def test_empty_transaction_ranking_does_not_claim_no_market_opportunity(self):
        state = {
            "updated_at": "2026-11-04T09:31:39Z",
            "transactions": {},
            "intelligence_items": {f"item-{index}": {} for index in range(666)},
        }

        message = build_watch_message(state, min_score=55)

        self.assertIn("Nessun candidato nel ranking WATCH delle transazioni registrate", message)
        self.assertIn("non equivale a un'assenza di opportunità di mercato", message)
        self.assertIn("Notizie pubbliche archiviate: 666", message)
        self.assertIn("Storico segnali CFD: campo non presente", message)
        self.assertIn("2026-11-04T09:31:39Z", message)
        self.assertIn("Ambito: solo ranking delle transazioni registrate", message)

    def test_empty_state_is_not_reported_as_no_candidates(self):
        message = build_watch_message({})

        self.assertIn("Stato SPUTNIK non disponibile o vuoto", message)
        self.assertIn("ranking non valutabile", message)
        self.assertNotIn("Nessun candidato nel ranking WATCH", message)


if __name__ == "__main__":
    unittest.main()
