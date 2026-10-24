# SPUTNIK Research and Implementation Log

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

### Evidence and limits
- Evidence is the reproduced code path and regression cases for the three failure modes; this is not evidence of improved trading returns.
- The configured Trump archive feed endpoint has not been verified live in this repository-only run. If it does not serve RSS/Atom, Sputnik will log the feed failure and continue; the next step would be to implement a documented public archive item endpoint if available.
- GitHub Actions completed successfully for the updated parser/collector code at commit `d628b7562c5754373e4071e763107f5e3c8fcb2e`; the item-intelligence suite reported 30 tests passing. That run preceded the two new regression-test commits, so those newly added cases are not yet confirmed by CI. No live Telegram delivery is claimed.
- The collector remains informational: no LONG/SHORT inference, no prices/SL/TP, no orders, and no Gagarin integration.
