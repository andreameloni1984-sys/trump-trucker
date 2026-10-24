# SPUTNIK Research and Implementation Log

## 2026-10-24 — Exclude page metadata from generic source-text extraction

### Finding
The three reported alerts contained JSON-LD website metadata from the generic Trump archive and White House homepages (for example, `@type: WebSite`, page names, and broad descriptions), not individual dated posts or articles. `TextExtractor` previously collected text from every HTML data node, including `<script type="application/ld+json">`, styles, and navigation/footer elements. This could pollute keyword discovery with site-wide metadata.

### Implemented
- Updated `TextExtractor` in `trump_tracker.py` to ignore script, style, noscript, SVG, navigation, header, footer, and aside content while extracting visible page text.
- Added a regression test to `tests/test_sputnik_item_intelligence.py` with JSON-LD containing market keywords and verifies that only visible editorial content remains.
- Kept the existing hard gate: generic homepages are diagnostics only and cannot be emitted as individual market catalysts.

### Evidence and limits
- The provided notifications visibly contain JSON-LD `WebSite` schema and generic homepage URLs, which matches the failure mode addressed here.
- The change reduces metadata-driven keyword pollution; it does not by itself discover individual posts. Individual catalysts still require configured RSS/Atom entries with a title, explicit publication time, and a valid item permalink.
- Code and regression test were committed to the feature branch and must be re-read; no local Python test run, GitHub Actions success, live source fetch, or Telegram delivery is claimed.
- Informational only: no LONG/SHORT inference, prices, stop loss, take profit, orders, or direct Gagarin integration.

### Change references
- Extractor commit: `7eddbdcb7d42f4b40df8ac70071f916adf718478`
- Regression-test commit: `f8b0d19e15897afa692b7af00353150296779f03`
- Follow-up: verify CI and confirm the deployed Telegram bot runs this branch; a repository commit alone does not update the production service.


## 2026-10-23 — Historical analogue matching must agree with event class

### Finding
The historical reaction matcher in `sputnik_action_reaction.py` previously accepted a pattern when either (a) one of its keywords appeared **or** (b) its event class matched the current text. This allowed an event to inherit an analogue of the opposite class when a broad keyword such as "tariff" appeared. For example, a tariff-pause/de-escalation headline could also be matched to the historical tariff-escalation pattern, introducing conflicting directions into the output.

### Implemented
- Historical analogues are now returned only when the classified event type matches the analogue's event type **and** at least one pattern-specific keyword is present.
- Added a regression test for a 90-day tariff pause: it must match the de-escalation analogue and must not inherit the escalation analogue.
- Kept all outputs descriptive/historical; this does not create a live LONG/SHORT recommendation or claim predictive accuracy.

### Evidence and limits
- Evidence is a reproducible code-path defect and a targeted regression test, not a claim of improved market returns.
- Existing historical patterns are a small, hand-curated set; phrase matching is still heuristic and may misclassify ambiguous text. The classification and historical sources need further audit and larger labelled tests.
- Tests have not been executed in this session. GitHub Actions/CI and Render/Telegram production state must be verified separately; a branch commit or PR is not a deployment.
- PAPER ONLY: no broker, no orders, and no integration with Gagarin.

### Change references
- Implementation commit: `01424f5d79d83e4723311a4699853c041534c651`
- Regression-test commit: `79fb1d9b8ba8f0bfb3808cb8a3bdbaa3eb6d9a5a`
- Follow-up: run the repository test suite/CI, then audit false positives around negation and keyword boundaries without broadening historical matches.


## 2026-10-23 — Negation and generic trade mentions

### Finding
Keyword matching could confuse a denial of a reported policy change with confirmation, and generic tariff mentions could inherit a specific historical market reaction.

### Implemented
- Explicit non-imposition/withdrawal wording is classified separately from escalation.
- Denials of reports are classified as TRADE_AMBIGUOUS and produce no directional historical analogue.
- Historical patterns require a pattern-specific phrase, not only the word tariff.
- Added regression tests for non-imposition, denied reports, and generic tariff mentions.

### Evidence and limits
- The tests encode concrete failure modes; they are not evidence of improved trading performance.
- Phrase matching remains heuristic and may miss paraphrases, negation variants, or non-English wording. Classification alone does not prove that a policy changed.
- Tests have not been executed in this session. CI must be checked. PAPER ONLY; no orders, no Gagarin integration, and no deployment implied.


## 2026-10-23 — Separate statement wording from formal-action wording

### Finding
An alert that identifies a political or trade event can still blur a threat, a reported statement, a disputed story, and wording that describes a formal action. These states have different evidentiary strength and should be visible before readers interpret a historical market analogue.

### Implemented
- Added a conservative `classify_claim_status` label: `PROPOSAL_OR_THREAT`, `STATEMENT_REPORTED`, `FORMAL_ACTION_WORDING`, `UNVERIFIED_OR_DISPUTED`, or `STATUS_UNCLEAR`.
- Added the label to the action→reaction Telegram message.
- Added regression tests for threats, formal-action wording, disputed reports, and message rendering.

### Evidence and limits
- This is a transparent phrase-based warning label, not independent fact-checking; “formal action wording” means the text contains one of the listed phrases, not that the action was independently verified or legally effective.
- No new market direction or probability is invented. Historical analogue matching remains separate.
- Tests have not been executed in this session; check CI before merge. PAPER ONLY; no orders, no deployment implied, and no Gagarin integration.


## 2026-10-23 — Narrow Sputnik's candidate instruments by catalyst

### Implemented
- Added an event-driven watchlist selector with Nasdaq 100 as the first focus for technology and US-China trade catalysts.
- Selects WTI only for oil-supply/production/shipping catalysts, gold for explicit geopolitical-risk wording, and S&P 500 for broad US macroeconomic catalysts.
- Limits the displayed candidate list to two instruments and labels it as a preliminary watchlist, not a LONG/SHORT signal.
- Added regression tests for tariff, oil, macro, unrelated text, and message output.

### Limits and copying strategy
- Reused Sputnik's existing event-classification and evidence-first architecture rather than copying an unverified third-party trading bot. The selector is a transparent heuristic, not a backtested ranking or proof that Nasdaq reacts most.
- Text keyword coverage is incomplete; actual direction, current price, confirmation, invalidation, stop loss and take profit require separately verified market data and technical rules.
- Tests have not been executed in this session. CI must be checked. PAPER ONLY; no orders, deployment or Gagarin integration implied.


## 2026-10-23 — Prepare for scheduled US economic releases

### Implemented
- Added `sputnik_release_calendar.py` to classify common scheduled macro releases by watch priority and likely affected instruments.
- Added timezone-aware conversion to Europe/Rome using `zoneinfo`, so daylight-saving changes are handled by timezone rules rather than fixed hour offsets.
- Unknown calendar titles remain unclassified; the module never invents LONG/SHORT direction.
- Added six tests covering CPI, EIA oil inventories, unknown releases, timezone conversion, missing timezone and no directional inference.

### Limits
- This module does not yet fetch or schedule official calendars or send pre-release Telegram alerts. It is a reusable classification/conversion layer that must be connected to a trusted calendar feed in a subsequent change.
- Instrument mapping is heuristic, not a measured causal ranking. Verify each release against the issuing agency's calendar before treating it as scheduled.
- Tests have not been executed in this session; CI status must be checked. PAPER ONLY, no orders and no Gagarin integration.


## 2026-10-23 — Connect official BLS calendar to pre-release Telegram alerts

### Implemented
- Added `sputnik_pre_release_alerts.py`, which reads the official BLS iCalendar feed, parses timed events, classifies only known macro releases, converts event times with timezone-aware rules, and selects events in the next 30 minutes.
- Added a Telegram message explicitly marked as a pre-release watch; it names instruments to watch but does not infer LONG/SHORT direction.
- Added persistent UID-based deduplication state and a GitHub Actions workflow scheduled every five minutes. The workflow uses the existing `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` secrets.
- Added regression tests for iCalendar parsing, the alert window, unknown-event rejection, and non-directional message wording.

### Evidence and limits
- BLS publishes an official public release calendar and a direct iCalendar feed. The parser defaults timezone-less BLS timed events to America/New_York, while honoring explicit TZID and UTC timestamps.
- This is an initial BLS-only connector (e.g. CPI, PPI and employment releases); BEA, FOMC and EIA feeds are not connected in this change.
- GitHub Actions runs every five minutes, but actual delivery depends on the workflow being enabled, secrets being configured, the official feed being reachable, and GitHub Actions being available. The code has not been executed in this session; do not treat alerts as live until a workflow run succeeds.
- All-day and unclassified events are ignored. The 30-minute window and instrument mapping are heuristic; no price-based direction, stop loss, take profit or trade execution is generated.
- PAPER/INFORMATION ONLY; no broker orders and no Gagarin integration.


## 2026-10-23 — Expand pre-release monitoring to the official BEA calendar

### Implemented
- Added a parser for the BEA public machine-readable release-date JSON feed, normalizing each event to an offset-aware timestamp and a stable UID.
- Connected BEA events into Sputnik's existing pre-release watch alongside the BLS iCalendar feed. If BEA is temporarily unavailable, BLS monitoring continues and the degraded source is logged.
- Added `Personal Income and Outlays` to the high-impact inflation classification so BEA PCE releases can enter the watchlist.
- Added regression tests for BEA JSON normalization and invalid input; included the new files in the repository test workflow.

### Evidence and limits
- The official BEA site provides both a release schedule and a machine-readable JSON calendar: https://www.bea.gov/news/schedule and https://apps.bea.gov/API/signup/release_dates.json.
- This adds BEA coverage for GDP and Personal Income and Outlays/PCE, but does not yet connect the Federal Reserve or EIA calendars. BLS and BEA source coverage is not a complete macro calendar.
- Tests have not been executed in this session; no CI run or Telegram delivery has been confirmed. Verify the next workflow run before treating alerts as live.
- Classification is heuristic, direction is not inferred, and no price-based entry, stop loss, take profit, broker order, or Gagarin integration is added.


## 2026-10-24 — Measure post-release reactions without inventing forecasts

### Implemented
- Added `sputnik_event_outcomes.py` to preserve a pre-event scenario and, when supplied with trusted timestamped prices, calculate the observed percentage move after the scheduled release.
- Enforced timezone-aware timestamps, positive prices, a baseline no later than the scheduled release, and a post-event observation no earlier than the release.
- Added an idempotent JSONL upsert keyed by event ID so repeated runs replace the same event record instead of inflating the journal.
- Added four regression tests and included the new module/test in the repository test workflow.

### Evidence and limits
- This establishes a reproducible measurement contract for future forecast-vs-reaction evaluation; it does not prove predictive skill and does not fetch market prices automatically.
- Sputnik still needs a verified price feed and a caller that writes a pre-event baseline and then a post-event observation. Until that connection exists, no measured result or accuracy score should be claimed.
- Tests have not been executed in this session and CI has not returned a result. PAPER/INFORMATION ONLY; no orders and no Gagarin integration.


## 2026-10-24 — Require dated individual items before emitting source intelligence

### Finding
The three recent notifications exposed a source-ingestion failure: the homepage scan found broad words such as metals, AI and rates on generic White House/Trump archive pages, then emitted them as page-level findings with no article title or publication date. The default item-feed path covered the White House only, so the Trump archive was not being collected through the same item-level route.

### Implemented
- Homepage scans now remain change-detection diagnostics only; generic page text is not emitted as a market catalyst or item-level Telegram intelligence finding.
- Default RSS/Atom inputs now include the White House news feed and the Trump archive feed, with a distinct TRUTH_ARCHIVE_RSS source label.
- The public feed parser now requires a non-empty title, a parseable publication date, and a real item permalink. It rejects missing/invalid dates, missing links, and links to the source homepage/feed endpoint instead of substituting the feed URL as the article URL.
- Atom parsing prefers an alternate permalink over self links, which can otherwise point back to a feed representation rather than the article.
- Added regression tests for generic homepage suppression, default source coverage, source labeling, missing/invalid item metadata, and Atom link selection.
- Enabled manual dispatch for the item-intelligence test workflow so these checks can be rerun on demand.

### Evidence and limits
- Evidence is the reproduced code path and regression cases for the three failure modes; this is not evidence of improved trading returns.
- The configured Trump archive feed endpoint has not been verified live in this repository-only run. If it does not serve RSS/Atom, Sputnik will log the feed failure and continue; the next step would be to implement a documented public archive item endpoint if available.
- GitHub Actions completed successfully for the updated parser/collector code at commit `d628b7562c5754373e4071e763107f5e3c8fcb2e`; the item-intelligence suite reported 30 tests passing. That run preceded the two new regression-test commits, so those newly added cases are not yet confirmed by CI. No live Telegram delivery is claimed.
- The collector remains informational: no LONG/SHORT inference, no prices/SL/TP, no orders, and no Gagarin integration.

## 2026-10-24 — Deduplicate identical public posts across different feeds

### Finding
The item collector's deduplication key included the source label, feed URL, and feed-local GUID. The same public post syndicated or mirrored into two configured feeds could therefore be emitted twice, despite having the same underlying permalink. Tracking parameters and URL fragments could also make equivalent links appear different.

### Implemented
- Added canonical_public_item_url to normalize HTTP(S) item URLs, lowercase the host, remove default ports, fragments, trailing slashes, and known tracking query parameters while preserving meaningful query parameters.
- Added public_item_identity, preferring an item's original/public permalink when present and otherwise its canonical article permalink.
- Changed the collector's event hash to use that stable item identity rather than feed-local metadata, so the same item discovered from multiple feeds shares one deduplication key.
- Added unit tests for tracking-parameter normalization and matching original permalinks, plus an integration-style regression test where two feeds return the same article.

### Evidence and limits
- The defect was visible in the previous hash expression, which explicitly incorporated source and feed_url; the new tests encode the cross-feed duplicate case.
- The implementation is deterministic and uses only Python's standard library. URL canonicalization intentionally removes only known tracking parameters; it does not merge different article URLs merely because their titles look alike.
- Tests have been added but have not yet been executed in this run. GitHub CI status must be checked after the final commit; no live feed fetch or Telegram delivery is claimed.
- Existing persisted state uses the old hash format, so a previously seen item may be emitted once when first encountered under the new identity format. Subsequent discoveries use the stable cross-feed key.
- Informational only: no LONG/SHORT inference, price/SL/TP, broker orders, or Gagarin integration was added.

## 2026-10-24 — Reject stale or future-dated public news before alerting

### Finding
Even an individual feed entry with a title, permalink and parseable date can be a poor market alert if it is several days old or implausibly future-dated. On a fresh runner or after state reset, such an archived item could be emitted as if it were a new catalyst.

### Implemented
- Added UTC-normalized parsing for ISO-8601 and RFC-2822 publication dates. Naive timestamps are explicitly interpreted as UTC instead of inheriting the runner's local timezone.
- Added a publication freshness gate in `trump_tracker.py`: by default, item-level public catalysts older than 72 hours or more than 10 minutes in the future are skipped before deduplication and alert creation.
- Added `SPUTNIK_MAX_NEWS_AGE_HOURS` as an optional override, validated to the range 1–720 hours; invalid values fall back to 72 hours.
- Added regression tests for timezone normalization, recent dates, stale dates, implausible future dates, and end-to-end suppression of a stale feed item.
- Fixed the collector tests to use a deterministic UTC clock and a recent publication fixture.

### Evidence and limits
- The reproduced risk is in the feed collector's prior behavior: any parseable date could pass the parser regardless of age, and the item could then be treated as newly detected.
- The freshness decision is deterministic and uses only the Python standard library. The 72-hour window is a safety default, not a claim that every older article is irrelevant; operators can widen it explicitly if their use case requires historical monitoring.
- Tests have been added to the existing item-intelligence CI path. A local clone/test attempt was blocked because this environment could not resolve github.com; GitHub currently reports no status checks or workflow run for the latest commit, so the new cases are not verified as passing. No live feed or Telegram delivery was tested.
- Informational only: no LONG/SHORT inference, price/SL/TP, broker orders, or direct GAGARIN integration was added.

## 2026-10-24 — Report public-feed outages without fabricating market events

### Finding
The RSS/Atom collector logged a fetch or parse exception and continued. If a source such as the Trump archive stopped serving a feed, the normal result could simply be zero findings, which is indistinguishable from a quiet market-news cycle in the Telegram output. Repeated failures were not preserved as structured source-health state.

### Implemented
- Added per-feed health state to `trump_tracker.py`: source label, status, UTC check time, parsed item count, and exception type. A valid feed with zero eligible entries is recorded as `OK_NO_ELIGIBLE_ITEMS`, not misclassified as an outage.
- Added a deduplicated operational Telegram warning for feed fetch/parse failures. The warning contains source labels and exception types, explicitly says that no market signal is inferred, and is not formatted as a LONG/SHORT catalyst.
- The warning signature is latched only after Telegram confirms delivery; a failed send can be retried on a later run. A successful feed scan clears the latch so a future outage can be reported again.
- Health state is limited to currently configured feeds, preventing a removed feed from leaving a stale outage warning behind.
- Added regression tests for failure recording, one-warning deduplication, recovery/reset behavior, and valid empty feeds. Updated the test workflow path filters so changes to the public-source parser and item-intelligence tests trigger CI.

### Evidence and limits
- The prior code printed the exception and continued without structured feed-health state or a Telegram operational warning. The new tests encode the outage/recovery and empty-feed distinctions.
- The tests were added but have not yet been executed in this run. CI status must be checked after the last commit; no live source fetch or Telegram delivery is claimed.
- This is source-health observability, not proof that a feed is authentic or that a market catalyst is predictive. A source may return a syntactically valid but incomplete feed; such a case still requires separate live-source validation.
- Informational only: no LONG/SHORT inference, price/SL/TP, broker orders, or direct GAGARIN integration was added.

## 2026-10-24 — Reject Atom self links as article permalinks

### Finding
The Atom parser selected the first available link when an entry had no `rel="alternate"` link. That fallback could treat `rel="self"` (a representation/feed endpoint) as the public article permalink, allowing a non-article URL to pass the item-level extraction gate.

### Implemented
- The link selector now accepts Atom alternate links (including Atom's default alternate relation when `rel` is omitted) and legacy RSS text-valued `<link>` elements.
- It no longer falls back to explicitly typed Atom links such as `rel="self"` or `rel="enclosure"` when no alternate link exists.
- Added a regression test proving an Atom entry with only a self link is excluded, while the existing alternate-over-self test remains in place.

### Evidence and limits
- The defect was identified directly in `sputnik_public_sources.py::_link`; the new test uses a minimal Atom feed fixture and requires no network access.
- This reduces false article-permalink candidates but cannot independently verify that an alternate URL is reachable or that its article text matches the feed entry.
- The test has been added but has **not yet been executed in this run**. Await the pull-request CI result before claiming it passes.
- No LONG/SHORT signal, price, stop loss, or take profit is generated. No orders or new Gagarin integration are added.

### Change references
- Parser commit: `2507b9cc130684ec260a41df5e4d1620696cf5b9`
- Regression-test commit: `a174f359fea0c7b9e9f282ab0890650778793f4c`
- Follow-up: confirm CI runs the complete unittest suite and inspect any failures before merging.



## 2026-10-24 — Do not treat Atom update time as publication time

### Finding
The feed parser accepted Atom `<updated>` as a fallback for `published`. An old article edited recently could therefore pass the 72-hour freshness gate and be emitted as if it were a newly published market catalyst.

### Implemented
- The parser now requires an explicit publication field: RSS `pubDate`, Atom `published`, or a date metadata element.
- Atom `updated` is preserved separately as `updated` metadata, but it is never substituted for `published` when checking freshness or constructing the event identity.
- Added parser regression coverage for an Atom item that has only `updated`, and adjusted Atom fixtures to assert that publication and update timestamps remain distinct.
- Added an end-to-end regression test where an old article has a recent `updated` timestamp; it must be rejected by the existing freshness gate and must not enter the deduplication state.

### Evidence and limits
- The defect was directly present in `parse_public_feed`, which previously searched `pubdate`, `published`, `updated`, and `date` in a single fallback list.
- This is a conservative quality gate. Some Atom publishers omit `published`; their entries will now be skipped rather than risk misrepresenting an edit timestamp as the original publication time. If a source documents a reliable publication-time mapping, it can be handled explicitly in a later source-specific adapter.
- Regression tests were added, but their execution result must be checked in GitHub Actions before claiming they pass. No live feed fetch or Telegram delivery was tested.
- Informational only: no LONG/SHORT inference, price/SL/TP, orders, or direct GAGARIN integration was added.


## 2026-10-24 — Canonicalize publication timestamps in metadata deduplication fallback

### Finding
Cross-feed deduplication already preferred canonical item/permalink URLs. When a row had no usable URL, however, the fallback identity hashed the raw publication-date string. Two feeds could describe the same title and instant with different formats or timezone offsets (for example, ISO-8601 `+01:00` versus RFC-2822 `GMT`) and be emitted twice.

### Implemented
- The metadata fallback in `public_item_identity` now parses publication time with the existing timezone-aware parser and hashes its canonical UTC ISO-8601 representation alongside the whitespace-normalized, case-folded title.
- Added a regression test proving equivalent publication instants in different formats and title whitespace/case produce the same fallback identity.
- URL-based identity remains preferred; rows without a valid date still do not receive a metadata fallback identity.

### Evidence and limits
- The mismatch was visible in the prior fallback: it hashed the raw `published` text, while `parse_publication_datetime` already supports ISO-8601/RFC-2822 and normalizes to UTC.
- This improves deduplication only for URL-less items with a parseable publication date and normalized-equal titles. It does not merge paraphrased headlines, and timestamps with materially different publication times remain distinct.
- The new regression test was added but has **not been executed in this run**. Repository CI status and the full test suite must be checked before claiming the test passes. No live feed or Telegram delivery was verified.
- Informational only: no LONG/SHORT signal, price, stop loss, take profit, order execution, or Gagarin integration was added.

### Change references
- Parser commit: `60aaf0dd1ddb8affcc8fce41fff307816f6ba7c8`
- Regression test commit: `9ede1d3180cd2cd595ca61f46d8542764b176a42`
- Follow-up: run the parser and item-intelligence test suites in GitHub Actions and inspect the run result.


## 2026-10-24 — Surface the validated original permalink in intelligence alerts

### Finding
The item collector already retained both the archive/article permalink (`url`) and, when supplied by the feed, an original post permalink (`primary_url`). The Telegram intelligence formatter displayed only `url`, so readers could not directly open the original post even when the feed explicitly provided it. That reduced independent verification of archive-based items.

### Implemented
- The alert formatter now labels the feed/article link as `Articolo/archivio` and adds `Post originale` when a distinct, valid HTTP(S) original permalink is available.
- Original links are passed through `canonical_public_item_url` before display; unsupported schemes and malformed URLs are omitted, and duplicate canonical links are not repeated.
- Added regression tests for displaying both links and suppressing an invalid `javascript:` original link. The alert remains explicitly non-directional.

### Evidence and limits
- The collector already stores `primary_url` from recognized original-URL metadata, but the previous `intelligence_message` did not render it.
- This improves source traceability only when a feed provides an original permalink. It does not independently prove the linked page is reachable or that its contents match the feed entry; that still requires live-source validation.
- The formatter logic was checked in an isolated smoke test: five assertions passed for archive/original-link rendering, tracking-parameter removal, invalid-scheme suppression, and non-directional wording. The full repository unittest suite and the newly added test methods have **not** been executed; no CI result, live feed access, or Telegram delivery is claimed.
- No LONG/SHORT inference, price, stop loss, take profit, order execution, or new Gagarin integration was added.

### Change references
- Alert formatter commit: `40e916e4c3b1151ad8e42d739a104e13b2a8de40`
- Regression tests commit: `147c0e9ff745db9c0b3f079ed924fa21de55029f`
- Follow-up: run the repository unittest suite and verify actual Telegram rendering with a feed item that contains original-URL metadata.


## 2026-10-24 — Skip invalid Atom alternates instead of losing a valid article link

### Finding
The Atom link selector returned the first `rel="alternate"` URL and let the later item-level validation reject the whole entry if that first URL was malformed or pointed back to the feed endpoint. An entry could therefore contain a valid later alternate permalink but be discarded because an earlier alternate was unusable.

### Implemented
- The parser now validates each alternate candidate against the feed URL while scanning, skipping unsupported schemes and feed-level links and continuing until it finds a valid individual permalink.
- The same individual-link check is applied to legacy text-valued RSS links when a base feed URL is available.
- Added a regression test with a `javascript:` alternate, a feed-endpoint alternate, and a later valid article URL; the valid article must be extracted.

### Evidence and limits
- The previous `_link` returned immediately on the first alternate candidate, while `parse_public_feed` performed the individual-permalink check only after selection. This ordering could discard an entry even when a later valid link existed.
- The test is a deterministic XML fixture and does not require network access. The test has been added but has **not been executed in this run**; full unittest and GitHub Actions results remain unverified. No live source or Telegram delivery was tested.
- This change improves permalink extraction only; it does not prove the destination page is reachable or that its content matches the feed entry. No LONG/SHORT signal, price, stop loss, take profit, order execution, or Gagarin integration was added.

### Change references
- Parser commit: `d8dc8b4635aa23c83c10aa6b66ba44077c6c15a7`
- Regression-test commit: `a1c817d821ebd603295a4c15b636c66aeabfcbe4`
- Follow-up: run `tests/test_sputnik_public_sources.py` and the full item-intelligence suite in CI, then verify the configured live feeds.


## 2026-10-24 — Select valid publication timestamps deterministically

### Finding
`parse_public_feed` used `_text(entry, {"pubdate", "published", "date"})`. That helper returns the first matching XML child in document order, not the first valid publication field. A malformed generic date element placed before a valid Atom `published` or RSS `pubDate` could therefore cause a legitimate item to be discarded.

### Implemented
- Added `_publication_text`, which checks explicit publication fields in stable priority order (`pubDate`, `published`, then generic `date`) and returns the first value that parses as a date.
- Invalid higher-priority fields no longer mask a valid lower-priority publication field. Atom `updated` remains excluded from publication-date selection.
- Added a regression test with an invalid namespaced `dc:date` before a valid Atom `published` timestamp; the item must be retained with the original publication time while keeping `updated` separate.

### Evidence and limits
- The ordering defect was directly visible in the previous parser call: the generic `_text` helper searched XML children in document order and did not validate alternate candidate fields.
- The change improves deterministic extraction for entries that expose more than one date field. It does not establish that the publisher's date is truthful, and items without any parseable explicit publication field remain excluded.
- The regression test was committed but **has not been executed in this run**. The GitHub connector does not provide a workflow-dispatch action here; CI status must be checked after the commit. No live feed or Telegram delivery was verified.
- Informational only: no LONG/SHORT inference, price, stop loss, take profit, order execution, or Gagarin integration was added.

### Change references
- Parser commit: `211d34bbf91a376fe329bc09b99d396f12ad2f60`
- Regression-test commit: `7e90f690d57b0a66ef9fe57858ae0752403cd93f`
- Follow-up: run `tests/test_sputnik_public_sources.py` and the full item-intelligence suite in GitHub Actions and inspect the result before merge.


## 2026-10-24 — Retry item-level alerts when Telegram delivery fails

### Finding
`intelligence_snapshot` reserves each finding's deduplication key before the alert is sent, and the main loop persisted state before calling Telegram. If `send_telegram` returned `False` (for example, missing credentials or a temporary Telegram/network error), the item remained marked as seen and would be suppressed on the next scan. This could silently lose a valid dated source alert.

### Implemented
- Added `deliver_intelligence_findings` to centralize item-alert delivery.
- On confirmed Telegram success, the deduplication key remains in state so the same item is not repeatedly sent.
- On a failed send, the helper removes that item's `event_id` from `intelligence_items` and persists the rollback, allowing a later scan to rediscover and retry it.
- Replaced the previous inline intelligence-send loop with the helper.
- Added regression tests for both failure (key removed and state saved) and success (key retained).

### Evidence and limits
- `send_telegram` already returns a boolean success indicator. The previous caller ignored it, while the item key had already been added by `intelligence_snapshot` and saved before delivery; the new helper uses that existing return contract.
- The behavior is designed for at-least-once delivery: if Telegram accepts a message but the process crashes before state persistence elsewhere, a duplicate may still occur. This change does not claim exactly-once delivery.
- The code and tests were committed, then reread from GitHub to verify the helper, caller replacement, test cases and this log entry. The full Python test suite could not be executed in this run because this connector provides repository reads/writes but no workflow-dispatch action or local checkout. CI status must be checked after the final commit; no test pass is claimed. No live Telegram delivery was attempted.
- Informational only: no LONG/SHORT inference, prices, stop loss, take profit, real orders, or new Gagarin integration was added.

### Change references
- Implementation commit: `3b7e364176cf960f8ccec3e403f4251b9d3a04b3`
- Regression-test commit: `a7b9f1d3b5696b117d96fa2827b9fcd94cfff6c1`
- Follow-up: run `tests/test_sputnik_item_intelligence.py` in CI and inspect both new delivery-state tests before merge.


## 2026-10-24 — Validate public feed URLs before accepting source evidence

### Finding
The RSS/Atom parser checked that an item permalink used HTTP(S) and had a path, but did not reject URL user-info such as `https://trusted.example@evil.example/story`. Such a URL can visually suggest one host while the browser navigates to another. The parser also copied `primary_url` into the finding without an equivalent safety check, and the configured feed URL was not validated at the parser boundary. Unsafe or misleading links weaken source provenance and can make a non-verifiable catalyst look documented.

### Implemented
- Extended `canonical_public_item_url` to reject whitespace, control characters and backslashes in addition to its existing checks for HTTP(S), host, user-info and valid ports.
- Reused that canonical validation in the individual-permalink gate and validated the feed URL before parsing.
- Dropped an unsafe `primary_url` while preserving an independently safe item permalink; unsafe item permalinks are rejected rather than silently relabelled as the feed URL.
- Added five regression tests covering a `javascript:` item link, a user-info host-spoof URL, an unsafe primary URL, an invalid feed URL, and whitespace/backslash URLs.

### Evidence and limits
- The issue is supported by the parser's prior validation path and is now represented by explicit regression cases. These tests establish URL-handling behavior, not improved market returns or signal accuracy.
- The parser still does not prove that an article's claims are true, that the source is authoritative, or that an event caused a market move. Source reputation, publication freshness and price/volume confirmation remain separate checks.
- CI for this stacked change is pending at log-write time. No passing test result is claimed until the relevant GitHub Actions run is inspected. No live source fetch or Telegram delivery is claimed.
- PAPER ONLY: no LONG/SHORT signal, price, entry, stop, target, broker connection, real order, Gagarin integration, or production deployment was added.

### Change references
- URL-validation implementation commit: `7581ace2f7834d860df8624ed37f7e24d8672d6a`
- Regression-test commit: `bc4b533f43f46c93e65ff1ac26931332c747654f`
- Branch: `fix/sputnik-public-url-validation-stacked-20261024` (stacked on `fix/sputnik-historical-match-gate`)
- Follow-up: verify the new CI runs, then separately inspect Render/Telegram deployment state; the stacked PR must not be treated as production code before merge/deploy.
