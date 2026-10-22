# SPUTNIK — Research & Implementation Log

Purpose: preserve useful findings and turn them into tested changes instead of accumulating research without implementation.

## Operating rules
- Scope: Sputnik only. No Gagarin integration, no broker connection, no live orders.
- Mode: PAPER ONLY. A news-derived bias is a hypothesis until the original source and market reaction are checked.
- Do not invent tickers, prices, entry, stop-loss, take-profit, accuracy rates, or backtest results.
- Each development cycle should deliver one concrete change, test, or a clearly documented blocker.
- Keep this log updated with the evidence, implementation, test status, and next action.

## 2026-10-22 — Equity catalyst screening
**Finding:** company-specific events can create opportunities distinct from broad index reactions. Positive/negative earnings surprises, guidance changes, contracts, buybacks, regulatory/legal risks, capital raises and M&A should be screened separately.

**Implemented:** added broad preliminary equity candidate rules to `sputnik_decision_engine.py`:
- earnings beat / record revenue / raised guidance / buyback / contract award / FDA approval → preliminary LONG candidate for the named company, if identifiable;
- earnings miss / guidance cut / profit warning / legal-regulatory investigation / recall → preliminary SHORT candidate for the named company;
- M&A → direction undetermined because target and acquirer can react differently;
- dividend cuts, dilution, capital raises, default/bankruptcy → preliminary SHORT candidate, subject to verification.

**Tests added:** `tests/test_sputnik_decision_engine.py` covers earnings beat, earnings miss and M&A ambiguity.

**Evidence / limitations:** these are screening heuristics, not a validated predictive model. Keyword matching can create false positives, miss context, or misread negation. No company ticker or trade levels should be inferred unless the source and fresh market data support them.

**Verification status:** code and tests committed to branch `sputnik-only-news-analysis`; GitHub Actions must be checked for the latest commit. Changes are not confirmed live on Telegram until a successful deployment is verified.

## Next priorities
1. Run/inspect tests on the latest branch and fix failures before merging.
2. Improve company/ticker extraction using explicit evidence from the story; otherwise label the issuer unknown.
3. Add tests for negation, rumor vs official disclosure, post-earnings price reaction, duplicate stories, and conflicting catalysts.
4. Record each signal and subsequent price outcome in a durable paper-trading journal; evaluate hit rate and expectancy only after a sufficient, timestamped sample.
5. Add price/volume confirmation only through a verified, timestamped market-data source. Never fabricate quotes or technical levels.

## 2026-10-22 — False-positive guard for denied/unconfirmed headlines
**Finding:** broad keyword screening can misclassify a denial, rumor, or explicitly unconfirmed report as a directional catalyst.

**Implemented:** the aggressive candidate screen now filters sentence-level denial/uncertainty markers before matching catalysts, so one denied sentence does not suppress a separate sentence that contains a positive event. Added regression tests for a denied lawsuit and an unconfirmed acquisition rumor.

**Limitations:** this is a conservative keyword guard, not full natural-language understanding; wording outside the marker list can still cause false positives. Review CI on the latest branch before merging.

**Current verification:** PR #10 remains open. The previously observed item-intelligence workflow passed on an earlier commit; it does not verify these latest changes. Production deployment/Telegram behavior remains unconfirmed.

## 2026-10-22 — CI regression follow-up
**Finding:** the first false-positive guard exposed two regression cases in the broad ranking suite: a denied lawsuit still produced a negative candidate, and the merger wording test did not produce the expected ambiguous M&A candidate. CI also revealed that the guard's regular-expression escaping needed correction.

**Implemented:** replaced substring-only uncertainty checks with clause-level regular-expression checks; clauses split at punctuation and semicolons; uncertainty patterns now use actual word boundaries. Added a regression case ensuring a confirmed acquisition clause can still be surfaced alongside a separate denial clause.

**Verification:** new CI runs must pass on the latest branch head before considering the change verified. Earlier workflow failures are documented rather than hidden. Production deployment remains unconfirmed.
