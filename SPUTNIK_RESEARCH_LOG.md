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
- Regression tests are in `tests/test_sputnik_cfd.py`. GitHub Actions run [40133587039](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40133587039) completed with `success` on head `88cc31fcf5d3f43d4211615424a1c031891f187d`; the workflow ran the menu, ranking, CFD, catalyst, and history unittest files. This is CI evidence, not a local test run.
- This reduces one false-direction class. It does not establish price/volume confirmation, predictive accuracy, or profitability. The current main-branch plan still relies on a boolean trigger flag; a separate future improvement should validate actual OHLCV-derived evidence.
- PAPER ONLY: no broker connection, order, Gagarin integration, invented market data, or deployment.

### Change references
- Implementation commit: `1a1d3050f4c0f22fc38f33c03978faffc827c739`
- Regression-test commit: `397570749db93a72c2f3c0cf0281c3ae235a1af8`
- Branch: `fix/sputnik-explicit-direction-main-20261024`, based directly on `main`.
- Render check on 2026-10-24: service `sputnik-telegram-listener` still lists commit `9e5204bf7d9074dba27637013b7d98933a91e733` as `live`; the 2026-10-22 deploy of `50851b0dc76f1b7ed0adaa872c47aa84793687f9` is `build_failed`. No service logs were returned for 2026-10-24 21:00–21:17 UTC. This PR is not deployed and no deployment was attempted.

## 2026-10-24 — Require exact aliases for conditional-plan instruments

### Finding
The conditional-plan resolver used substring checks such as `"GOLD" in candidate`. A company name such as `Goldman Sachs` therefore matched the Gold commodity quote key and could receive a commodity price/ATR plan. Broad checks for `NASDAQ` could similarly confuse the Nasdaq-100 index with other Nasdaq-labelled instruments. This is an instrument-identity false-positive, not a market-direction edge.

### Implemented
- Replaced substring-based resolution with a finite allowlist of normalized, explicit aliases for supported Brent, WTI, Gold, and Nasdaq-100 instruments.
- Normalize punctuation and spacing, then require the whole normalized label to match an alias; unknown/ambiguous labels remain `WAIT` with no levels and an explicit unsupported-instrument reason.
- Added regression tests proving `Goldman Sachs` cannot use a `GOLD` quote, while exact aliases such as `Gold`, `XAU/USD`, and `NASDAQ-100` still resolve.

### Evidence and limits
- Source inspection reproduced the substring collision in `build_conditional_trade_plan`.
- Regression tests are in `tests/test_sputnik_cfd.py`; GitHub Actions results are pending until the draft PR is opened.
- The allowlist is deliberately conservative. New instruments/aliases must be added explicitly only when their quote-key semantics are verified. This does not validate quote provenance, OHLCV price/volume confirmation, predictive accuracy, or profitability.
- PAPER ONLY: no orders, broker connections, Gagarin integration, or deployment.

### Change references
- Branch: `fix/sputnik-exact-instrument-aliases-20261024`, stacked on `fix/sputnik-explicit-direction-main-20261024`.
- Implementation commit: `d6bd982d0b24bc07c759d018af7aeb42a2afe60d`.
- Regression-test commit: `ea19c356e334df951c9fff11f26edd23aa4c5b83`.

### Verification update — 2026-10-24 21:56 UTC
- GitHub Actions run [40136367007](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40136367007) completed with `success` for head `c3751f57245674f1a71931509644da732eb64af2`. The `SPUTNIK Telegram menu tests` workflow ran `tests/test_sputnik_cfd.py` with the new instrument-resolution regressions.
- Re-fetched `sputnik_cfd.py`, `tests/test_sputnik_cfd.py`, and this log from the feature branch; the exact-alias resolver, both regression tests, and log entry are present.
- Render service `sputnik-telegram-listener` is configured to auto-deploy from `main`. Latest listed live deploy remains commit `9e5204bf7d9074dba27637013b7d98933a91e733` (2026-10-16); the 2026-10-22 deploy attempt for `50851b0dc76f1b7ed0adaa872c47aa84793687f9` is `build_failed`. Logs at 2026-10-24 21:40:44–21:40:52 UTC show the existing listener HTTP online and permanent listener ready, but do not show this PR's code in production. No deploy was attempted.
- Pull request [#19](https://github.com/andreameloni1984-sys/trump-trucker/pull/19) remains draft/open and targets the direction-fix branch; no merge to `main`.
