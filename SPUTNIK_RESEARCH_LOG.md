# SPUTNIK — Research and implementation log

## 2026-10-26 — Include individual Trump archive posts in the default feed scan

- **Observed issue:** the page-level `TRUTH_ARCHIVE` scan correctly rejects generic archive metadata, but the default item-level RSS scan only included the White House feed. As a result, individual Trump posts could be missed unless `SPUTNIK_RSS_FEEDS` was explicitly configured.
- **Change:** `_configured_rss_feeds()` now defaults to both `https://www.whitehouse.gov/feed/` and `https://www.trumpstruth.org/feed`. Existing item-level parsing continues to use each feed item's title, publication timestamp, URL, text, and deduplication identity.
- **Regression test:** added a test that the default feed list contains both feeds when no environment override is configured.
- **Safety boundary:** this makes individual posts discoverable; it does not turn keyword matches into trade signals. Posts remain catalyst candidates, and price/volume/structure confirmation and risk checks are still required. No order execution, broker connection, deployment, or Gagarin integration was performed.
- **Verification status:** code and test were committed to branch `fix/sputnik-truth-archive-feed`; CI and live feed parsing still need to be checked before merge.


## 2026-10-26 — Require dated, individual public-source entries before catalyst classification

- **Observed issue:** the RSS parser could fall back to the feed URL when an item had no permalink, and intelligence_snapshot() accepted feed entries with missing or unparseable publication timestamps. This allowed non-individual or poorly timestamped rows to enter the public-catalyst history.
- **Implemented:** validate the publication time (ISO/RFC 822), reject timestamps more than five minutes in the future, and require a distinct HTTP(S) item permalink. A verified original permalink may substitute for a missing feed link; a feed-level URL cannot.
- **Regression tests:** missing date, unparseable date, implausibly future date, and missing item permalink are all rejected before deduplication/history insertion.
- **Evidence boundary:** valid metadata establishes a dated public item, not the authenticity of its claims or a directional market signal. Price/volume confirmation remains separate. No production deployment or Telegram delivery is claimed.


## 2026-10-26 — Prevent first-scan RSS backfill from flooding Telegram

- **Finding:** after the TRUTH archive feed was enabled, the first main-branch workflow found 65 item-level RSS candidates. The workflow completed, but the sender does not log per-message Telegram acceptance, so the exact number delivered cannot be confirmed from Actions logs. This exposed a back-catalog burst risk when a feed is added.
- **Implemented:** track initialization per feed, silently seed older entries on the first successful scan, emit only items published within the last five minutes during bootstrap, and ignore items older than a configurable maximum age (default 24 hours). Rejected back-catalog items are still deduplicated so they are not reconsidered every poll.
- **Regression tests:** a new feed containing a two-hour-old item or a two-day-old item produces no catalyst on first scan and records the item/feed initialization state.
- **Verification:** merged to main in commit `67359fb88890ae8ae2b7361c7ba89789adea1003`. The follow-up `SPUTNIK` main workflow succeeded and reported zero new public-source correlations; the listener health endpoint returned `status: ok`. Item-intelligence CI passed 19 tests and ranking CI passed 63 tests before merge.
- **Safety boundary:** the first run after enabling the feed processed 65 candidates and called the sender for each, but per-message Telegram acceptance is not logged, so the exact delivered count is unknown. The backfill guard prevents those stored items from being re-emitted; no test messages or orders were sent.


## 2026-10-26 — Require source and event-specific evidence for historical analogues

- Finding: the historical matcher could accept a pattern when either a broad keyword matched or the event class matched. A de-escalation headline containing the generic word tariff could therefore inherit a different event's historical reaction. The tariff-pause record also pointed only to the Reuters homepage.
- Change: require an HTTPS article-like URL, event-class agreement, and at least one pattern-specific keyword before a historical analogue contributes any directional vote.
- Regression coverage: generic homepage-only and same-class-but-unrelated analogues are rejected; existing escalation and softening examples remain covered.
- Limits: URL shape is only a minimum provenance check, not proof of authenticity or predictive power. No live trade direction is inferred from the historical analogue alone.
- Verification: committed on branch fix/sputnik-analogue-evidence-gate-20261026; awaiting GitHub Actions. Not deployed to Render/Telegram in this run.
- Next: resolve the existing historical-analogue PR conflict through normal review; verify production deploy separately.
