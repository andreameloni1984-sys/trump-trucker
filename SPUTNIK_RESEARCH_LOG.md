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
