# Sputnik Research Log

## 2026-10-25 — Reject non-finite market values

- **Problem learned:** Python treats positive infinity as greater than zero. The previous numeric helper accepted `float("inf")`; conditional plans could consequently calculate infinite levels and retain a confirmed-trigger status. Extremely large integers could also raise `OverflowError` during float conversion instead of failing closed.
- **Single improvement implemented:** `sputnik_cfd.py::_number` now catches `OverflowError` and accepts a value only if it is finite and positive. This protects both conditional-plan inputs (price/ATR) and CFD-cart inputs (price/stop/target/capital).
- **Regression tests added:** infinite CFD target remains `WAIT`; infinite conditional price and ATR remain `WAIT` with no entry; an integer too large to convert to float is rejected without crashing.
- **Verification:** code and tests are committed on `fix/sputnik-finite-market-numbers-20261025`; GitHub Actions workflow `SPUTNIK Telegram menu tests` completed SUCCESS on tested code/test commit `5cb5bab90462a79aee91c6085d035053a5c1b9a9` (run `40141698337`, job `121014602185`); it ran `python -m unittest tests/test_telegram_menu.py tests/test_sputnik_ranking.py tests/test_sputnik_cfd.py tests/test_sputnik_catalyst.py tests/test_sputnik_history.py -v`.
- **Evidence boundary:** these tests establish input-validation behavior only. They do not prove price/volume confirmation, market predictive accuracy, profitability, or out-of-sample performance.
- **Blockers / production:** `SPUTNIK_RESEARCH_LOG.md` was not present on `main`, so this branch creates the persistent log. No merge or Render deploy is performed; production activation is not claimed.
- **Safety:** PAPER ONLY. No orders, broker connections, or Gagarin integration.
