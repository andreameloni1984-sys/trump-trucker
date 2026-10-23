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
