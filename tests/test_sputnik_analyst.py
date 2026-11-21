import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import sputnik_analyst as an
from trump_tracker import FilingEvent, TransactionRecord

NOW = datetime(2026, 11, 23, 9, 0, tzinfo=timezone.utc)  # 10:00 a Roma


def ev(cik="0001494730", acc="a1", form="4", filed="2026-11-22", company="MUSK ELON"):
    return FilingEvent("SEC_EDGAR", cik, acc, form, filed, "doc.xml", company,
                       f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/doc.xml", f"id-{cik}-{acc}")


def trade(event, action="ACQUISTATO", code="P", issuer="Tesla, Inc.", ticker="TSLA"):
    return TransactionRecord(event.event_id, event.cik, event.company, event.form, action, "Common Stock",
                             "1000", "250", "2026-11-20", event.company, event.source_url, transaction_code=code,
                             filing_date=event.filed_at, issuer=issuer, ticker=ticker)


def trump_item(title="Trump announces new tariffs on steel imports", hours_ago=1, domains=("TRADE_POLICY", "METALS")):
    published = (NOW - timedelta(hours=hours_ago)).isoformat()
    return {"evidence": "PUBLIC_RSS_ITEM", "title": title, "published": published, "domains": list(domains),
            "url": "https://www.trumpstruth.org/statuses/1", "feed_url": "https://www.trumpstruth.org/feed",
            "event_id": f"t-{title}", "detected_at": published}


class WatchlistTests(unittest.TestCase):
    def test_name_check_rejects_wrong_cik(self):
        self.assertTrue(an.name_matches("1494730", "Musk Elon"))
        self.assertFalse(an.name_matches("1494730", "SOME OTHER PERSON"))
        self.assertFalse(an.name_matches("123", "Anyone"))

    def test_extra_ciks_from_env(self):
        with patch.dict(os.environ, {"SPUTNIK_CIKS": "999, 1494730"}):
            ciks = [w.cik for w in an.watchlist()]
        self.assertIn("0000000999", ciks)
        self.assertEqual(ciks.count("0001494730"), 1)

    def test_themes(self):
        self.assertIn("AUTO", an.themes_for_security("Tesla, Inc."))
        self.assertIn("METALS", an.themes_for_security("Nucor Corp"))
        self.assertIn("METALS", an.expand_news_themes(["TRADE_POLICY"]))


class SelectionTests(unittest.TestCase):
    def test_first_run_archives_silently_then_alerts_new(self):
        state = {}
        old = ev(acc="old", filed="2025-01-01")
        recent = ev(acc="recent", filed="2026-11-21")
        alert, archive = an.select_filings([old, recent], state, NOW)
        self.assertEqual(alert, [])
        self.assertEqual([e.accession for e in archive], ["recent"])
        new = ev(acc="new", filed="2026-11-23")
        alert, archive = an.select_filings([old, recent, new], state, NOW)
        self.assertEqual([e.accession for e in alert], ["new"])
        self.assertEqual(archive, [])

    def test_old_filing_never_alerts(self):
        state = {}
        an.select_filings([ev(acc="x", filed="2026-11-20")], state, NOW)
        alert, _ = an.select_filings([ev(acc="late", filed="2026-09-01")], state, NOW)
        self.assertEqual(alert, [])


class MessageTests(unittest.TestCase):
    def setUp(self):
        self.state = {"intelligence_history": {}}

    def test_trade_move_and_message(self):
        e = ev()
        moves = an.remember_moves(self.state, [trade(e)], NOW)
        self.assertEqual(len(moves), 1)
        m = moves[0]
        self.assertEqual(m["who"], "Elon Musk")
        self.assertEqual(m["value"], 250000)
        self.assertIn("TSLA", m["issuer"])
        text = an.move_message(m, self.state, NOW)
        self.assertIn("HA COMPRATO", text)
        self.assertIn("Tesla", text)
        self.assertIn("non è un segnale operativo", text)
        self.assertEqual(an.remember_moves(self.state, [trade(e)], NOW), [])  # nessun doppione

    def test_13f_summary(self):
        e = ev(cik="0001067983", acc="f", form="13F-HR", company="BERKSHIRE HATHAWAY INC")
        rows = [TransactionRecord(e.event_id, e.cik, e.company, e.form, "POSIZIONE_DICHIARATA", name, "1", str(v),
                                  e.filed_at, e.company, e.source_url, source_kind="13F_POSITION", filing_date=e.filed_at)
                for name, v in (("APPLE INC COM", 6e10), ("OCCIDENTAL PETE CORP COM", 1.2e10), ("CHUBB LTD", 8e9))]
        m = an.remember_moves(self.state, rows, NOW)[0]
        self.assertEqual(m["kind"], "13F")
        self.assertEqual(m["top"][0]["security"], "APPLE INC COM")
        self.assertIn("ENERGY", m["themes"])
        self.assertIn("60.00 mld $", an.move_message(m, self.state, NOW))

    def test_trump_message_links_billionaire_moves(self):
        e = ev(cik="0000921669", company="ICAHN CARL C")
        an.remember_moves(self.state, [trade(e, issuer="Cleveland-Cliffs Inc.", ticker="CLF")], NOW)
        text = an.trump_message(trump_item(), self.state, NOW)
        self.assertIn("TRUMP", text)
        self.assertIn("Carl Icahn", text)
        self.assertIn("Truth Social", text)

    def test_move_message_links_trump(self):
        self.state["intelligence_history"]["t"] = trump_item(hours_ago=48)
        e = ev(cik="0000921669", company="ICAHN CARL C")
        m = an.remember_moves(self.state, [trade(e, issuer="Nucor Corp", ticker="NUE")], NOW)[0]
        self.assertIn("Collegamento con Trump", an.move_message(m, self.state, NOW))


class DeliveryTests(unittest.TestCase):
    def test_first_run_only_activation_then_alerts_and_cap(self):
        state = {"intelligence_history": {}}
        sent = []
        n = an.deliver(state, [trump_item()], [], [], lambda t: sent.append(t) or True, NOW)
        self.assertEqual(n, 1)
        self.assertIn("ANALISTA ATTIVO", sent[0])
        sent.clear()
        later = NOW + timedelta(minutes=15)
        items = [trump_item(title=f"Tariffs news {i}", hours_ago=0.5) for i in range(9)] + [trump_item("Old post", hours_ago=30)]
        state["analyst_brief_date"] = later.date().isoformat()
        an.deliver(state, items, [], [], lambda t: sent.append(t) or True, later)
        self.assertEqual(len(sent), an.MAX_ALERTS_PER_RUN)
        self.assertIn("altre", sent[-1])
        self.assertFalse(any("Old post" in t for t in sent))

    def test_brief_once_per_day_after_hour(self):
        state = {"intelligence_history": {"t": trump_item()}, "analyst_started_at": (NOW - timedelta(days=1)).isoformat()}
        sent = []
        an.deliver(state, [], [], [], lambda t: sent.append(t) or True, NOW)
        self.assertTrue(any("RIEPILOGO" in t for t in sent))
        sent.clear()
        an.deliver(state, [], [], [], lambda t: sent.append(t) or True, NOW + timedelta(hours=1))
        self.assertFalse(any("RIEPILOGO" in t for t in sent))
        early = {"analyst_started_at": "2026-11-01T00:00:00+00:00"}
        an.deliver(early, [], [], [], lambda t: sent.append(t) or True, datetime(2026, 11, 24, 4, 0, tzinfo=timezone.utc))
        self.assertFalse(any("RIEPILOGO" in t for t in sent))

    def test_failed_send_is_kept_for_retry(self):
        state = {}
        an.deliver(state, [], [], [], lambda t: False, NOW)
        self.assertEqual(len(state["analyst_outbox"]), 1)
        sent = []
        an.deliver(state, [], [], [], lambda t: sent.append(t) or True, NOW + timedelta(minutes=15))
        self.assertTrue(any("ANALISTA ATTIVO" in t for t in sent))
        self.assertEqual(state["analyst_outbox"], [])

    def test_disclosure_alert_for_13d(self):
        state = {"analyst_started_at": NOW.isoformat(), "analyst_brief_date": NOW.date().isoformat()}
        sent = []
        e = ev(cik="0001336528", form="SC 13D", company="PERSHING SQUARE CAPITAL MANAGEMENT, L.P.")
        an.deliver(state, [], [e], [], lambda t: sent.append(t) or True, NOW)
        self.assertEqual(len(sent), 1)
        self.assertIn("13D", sent[0])
        self.assertIn("Ackman", sent[0])


if __name__ == "__main__":
    unittest.main()


class AttributionTests(unittest.TestCase):
    def test_issuer_insider_not_attributed_to_billionaire(self):
        state = {}
        e = ev(cik="0001067983", acc="b", company="BERKSHIRE HATHAWAY INC")
        rec = trade(e, issuer="BERKSHIRE HATHAWAY INC", ticker="BRK.B")
        rec.reporting_owner = "Some Director"
        self.assertEqual(an.remember_moves(state, [rec], NOW), [])

    def test_billionaire_as_owner_is_attributed(self):
        state = {}
        e = ev(cik="0001067983", acc="c", company="BERKSHIRE HATHAWAY INC")
        rec = trade(e, issuer="Occidental Petroleum Corp", ticker="OXY")
        rec.reporting_owner = "BERKSHIRE HATHAWAY INC"
        m = an.remember_moves(state, [rec], NOW)[0]
        self.assertTrue(m["who"].startswith("Warren Buffett"))
        self.assertFalse(m["insider"])

    def test_trump_media_insiders_kept_and_labelled(self):
        state = {}
        e = ev(cik="0001849635", acc="d", company="Trump Media & Technology Group Corp.")
        rec = trade(e, action="VENDUTO", code="S", issuer="Trump Media & Technology Group Corp.", ticker="DJT")
        rec.reporting_owner = "NUNES DEVIN"
        m = an.remember_moves(state, [rec], NOW)[0]
        self.assertEqual(m["who"], "Nunes Devin (insider di Trump Media)")

    def test_old_misattributed_moves_hidden(self):
        state = {"analyst_moves": {"x": {"kind": "TRADE", "cik": "0001067983", "owner": "Some Director",
                                         "issuer": "BERKSHIRE", "filed": NOW.date().isoformat(), "who": "Warren Buffett"}}}
        self.assertEqual(an.recent_moves(state, 7, NOW), [])

    def test_short_security(self):
        self.assertEqual(an.short_security("Common Stock, $0.01 par value per share"), "Common Stock")
        self.assertEqual(an.short_security("Class A Common Stock"), "Class A Common Stock")


class ContextExportTests(unittest.TestCase):
    def test_export_has_trump_bias_and_money(self):
        state = {"intelligence_history": {"t": trump_item("Trump announces new tariffs on China", hours_ago=2)}}
        e = ev(cik="0000921669", company="ICAHN CARL C")
        an.remember_moves(state, [trade(e, issuer="Nucor Corp", ticker="NUE")], NOW)
        with patch.object(an, "_now", return_value=NOW):
            ctx = an.export_context(state, NOW)
        self.assertEqual(len(ctx["trump"]), 1)
        self.assertIn("published", ctx["trump"][0])
        self.assertEqual(ctx["money"][0]["who"], "Carl Icahn")

    def test_write_context_only_on_change(self):
        import tempfile
        state = {"intelligence_history": {}}
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "ctx.json")
            self.assertTrue(an.write_context(state, path, NOW))
            self.assertFalse(an.write_context(state, path, NOW + timedelta(minutes=15)))
