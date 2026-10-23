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
