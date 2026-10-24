# SPUTNIK Research and Implementation Log

## 2026-10-24 — Require an explicit direction in conditional plans

### Finding
On the repository's `main` branch, `build_conditional_trade_plan` inferred SHORT when the bias contained the substring `SHORT`, and inferred LONG for every other value. Consequently, a missing or ambiguous bias such as `NEUTRAL`, `WAIT`, `LONG_SETUP`, or `NOT_SHORT` could be turned into a directional plan when quote and ATR data were present. The branch's `main` version also marks the plan as trigger-confirmed from a single `trigger_confirmed=True` flag; this change deliberately addresses direction parsing only and does not validate that flag's market evidence.

### Implemented
- Accept only normalized, exact `LONG` or `SHORT` values for conditional-plan direction.
- Return the default `WAIT` result with no entry/stop/targets when bias is absent or ambiguous.
- Add regression tests for missing/ambiguous bias while the quote trigger flag is true, and tests that exact LONG/SHORT remain directional.

### Evidence and limits
- Reproduced directly from the `main` source path: substring matching made `NOT_SHORT` SHORT and defaulted other unknown strings to LONG.
- Regression tests are in `tests/test_sputnik_cfd.py`; CI must be checked after the pull request is opened. No local test run is claimed.
- This reduces one false-direction class. It does not establish price/volume confirmation, predictive accuracy, or profitability. The current main-branch plan still relies on a boolean trigger flag; a separate future improvement should validate actual OHLCV-derived evidence.
- PAPER ONLY: no broker connection, order, Gagarin integration, invented market data, or deployment.

### Change references
- Implementation commit: `1a1d3050f4c0f22fc38f33c03978faffc827c739`
- Regression-test commit: `397570749db93a72c2f3c0cf0281c3ae235a1af8`
- Branch: `fix/sputnik-explicit-direction-main-20261024`, based directly on `main`.
- Production/Render must be verified separately; a feature branch or CI result is not a deployment.
