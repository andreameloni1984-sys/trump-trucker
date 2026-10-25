# Sputnik Research Log

## 2026-10-25 — Reject non-finite market values

- **Problem learned:** Python treats positive infinity as greater than zero. The previous numeric helper accepted `float("inf")`; conditional plans could consequently calculate infinite levels and retain a confirmed-trigger status. Extremely large integers could also raise `OverflowError` during float conversion instead of failing closed.
- **Single improvement implemented:** `sputnik_cfd.py::_number` now catches `OverflowError` and accepts a value only if it is finite and positive. This protects both conditional-plan inputs (price/ATR) and CFD-cart inputs (price/stop/target/capital).
- **Regression tests added:** infinite CFD target remains `WAIT`; infinite conditional price and ATR remain `WAIT` with no entry; an integer too large to convert to float is rejected without crashing.
- **Verification:** code and tests are committed on `fix/sputnik-finite-market-numbers-20261025`; GitHub Actions workflow `SPUTNIK Telegram menu tests` completed SUCCESS on tested code/test commit `5cb5bab90462a79aee91c6085d035053a5c1b9a9` (run `40141698337`, job `121014602185`); it ran `python -m unittest tests/test_telegram_menu.py tests/test_sputnik_ranking.py tests/test_sputnik_cfd.py tests/test_sputnik_catalyst.py tests/test_sputnik_history.py -v`.
- **Evidence boundary:** these tests establish input-validation behavior only. They do not prove price/volume confirmation, market predictive accuracy, profitability, or out-of-sample performance.
- **Blockers / production:** `SPUTNIK_RESEARCH_LOG.md` was not present on `main`, so this branch creates the persistent log. No merge or Render deploy is performed; production activation is not claimed.
- **Safety:** PAPER ONLY. No orders, broker connections, or Gagarin integration.

## 2026-10-25 — Reject overflowing derived CFD sizing and R/R

- **Problem learned:** validating individual inputs as finite is not enough. With tiny but finite entry/stop distances, the derived position size can overflow to infinity; a very large finite target divided by a tiny finite risk distance can likewise make the calculated risk/reward ratio infinite. Rounding can also collapse a positive derived value to zero.
- **Single improvement implemented:** `build_cfd_cart` now calculates the risk budget without an avoidable intermediate overflow, validates the risk budget, then rejects a candidate with `WAIT` before exposing levels if risk/reward inputs or derived size/RR are non-finite or non-positive. Rounded units and rounded RR must also remain finite and positive. No fallback levels or sizing are invented.
- **Regression tests added:** finite subnormal prices that overflow unit sizing must stay `WAIT`; finite price/stop/target values that overflow calculated R/R must also stay `WAIT`. Existing normal-case test continues to cover a valid long.
- **Verification:** code commit `51c5509f611a95872693b871e4cf925ee2e3c59a`; final test commit `de1dac984c0679c7d5ea77794565c34b0f845d7d`. The first CI run `40147756564` failed because the two new tests used a helper defined only on another test class; the fixture was corrected in `6d060bac93384b2ae2fc3de6dfe15bba13c84f2e`. CI runs `40147777862` and `40147803890` passed on intermediate commits; final run `40147811830` completed SUCCESS on the final code/test commit, job `121032821613`, and ran 32 tests with `python -m unittest tests/test_telegram_menu.py tests/test_sputnik_ranking.py tests/test_sputnik_cfd.py tests/test_sputnik_catalyst.py tests/test_sputnik_history.py -v`.
- **Evidence boundary:** this is arithmetic/input safety, not evidence of signal accuracy, profitability, price/volume confirmation, or out-of-sample performance.
- **Repository / production:** change is on `fix/sputnik-reject-overflowing-derived-size-20261025`, stacked on the open non-finite-input PR branch to preserve that dependency. No merge or Render deploy; production activation is not claimed.
- **Safety:** PAPER ONLY. No orders, broker connections, costs, or Gagarin integration.

## 2026-10-25 — Reject invalid derived conditional levels

- **Problem learned:** valid positive price and ATR inputs do not guarantee valid derived SL/TP levels. If ATR is too large relative to entry, a stop or target can become zero/negative; if ATR is too small relative to price, rounding to six decimals can collapse distinct levels to the same price. A conditional plan could previously expose such levels and inherit a trigger flag.
- **Single improvement implemented:** `build_conditional_trade_plan` now validates all rounded derived levels as finite and positive and requires strict directional ordering (`stop < entry < TP1 < TP2` for LONG; reverse order for SHORT). Invalid/collapsed levels return `WAIT` with all price levels left null.
- **Regression tests added:** LONG with stop below zero; SHORT with target below zero; valid positive inputs whose levels collapse after rounding. All tests set `trigger_confirmed=True` to ensure the numeric guard takes precedence.
- **Verification:** pending pull-request CI for this branch; do not infer success until the workflow result is inspected.
- **Evidence boundary:** this validates derived arithmetic only. It does not verify actual OHLCV price/volume confirmation or establish signal accuracy, profitability, or out-of-sample performance.
- **Repository / production:** branch is stacked on `fix/sputnik-reject-overflowing-derived-size-20261025` (PR #21) to preserve the prior numeric-safety changes and log history. No merge or Render deployment is performed.
- **Safety:** PAPER ONLY. No orders, broker connections, costs, or Gagarin integration.
