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
- **Verification:** code commit `51c5509f611a95872693b871e4cf925ee2e3c59a`; test-fixture correction commit `6d060bac93384b2ae2fc3de6dfe15bba13c84f2e`. First CI run `40147756564` failed because the two new tests used a helper defined only on another test class; the fixture was corrected. The subsequent run `40147777862`, job `121032721784`, completed SUCCESS and ran 32 tests with `python -m unittest tests/test_telegram_menu.py tests/test_sputnik_ranking.py tests/test_sputnik_cfd.py tests/test_sputnik_catalyst.py tests/test_sputnik_history.py -v`.
- **Evidence boundary:** this is arithmetic/input safety, not evidence of signal accuracy, profitability, price/volume confirmation, or out-of-sample performance.
- **Repository / production:** change is on `fix/sputnik-reject-overflowing-derived-size-20261025`, stacked on the open non-finite-input PR branch to preserve that dependency. No merge or Render deploy; production activation is not claimed.
- **Safety:** PAPER ONLY. No orders, broker connections, costs, or Gagarin integration.

