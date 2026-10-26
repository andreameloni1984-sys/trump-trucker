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


## 2026-10-26 — Require article-specific sources for historical analogues

- **Observed issue:** the historical pattern `tariff_pause_2025_04` pointed only to the Reuters homepage. The matcher could still use that pattern's stored market directions as if they were backed by a specific historical report.
- **Implemented:** added a minimum provenance check for historical patterns: source URL must use HTTPS and have an article-like path with a sufficiently specific final slug. Homepage-only URLs are excluded from historical matching.
- **Regression test:** `test_analogue_with_homepage_only_source_is_excluded` checks that the homepage-only tariff-pause pattern is not used.
- **Evidence boundary:** a specific-looking URL is only a provenance minimum; it does not prove source authenticity, correctness, event comparability, or a future price direction. Historical analogues remain descriptive evidence, not a live trade signal.
- **Verification status:** code/test head `d34959dbd6d1ab0761159b24e65bbdcc9784de6d` passed both [SPUTNIK ranking tests](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40272158895) and [SPUTNIK item intelligence tests](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40272158808). The log-only follow-up commit does not alter code/tests; no local test execution is claimed.
- **Production/safety:** Render/Telegram not inspected and no deployment claimed. PAPER ONLY; no orders, broker connection, paid service, or Gagarin integration.
