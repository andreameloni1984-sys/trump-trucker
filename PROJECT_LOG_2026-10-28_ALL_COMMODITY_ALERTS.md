# SPUTNIK — all selected commodity state alerts — 2026-10-28

## Implemented
- Added `run_selected_commodity_alerts.py` to check the selected eight-commodity basket: gold, silver, copper, WTI, Brent, wheat, corn and soybeans.
- Runs from the existing five-minute SPUTNIK schedule and replaces the WTI-only workflow step, avoiding a second independent WTI alert path.
- Each instrument has an independent state key; unchanged states are suppressed and a state advances only after Telegram accepts the message.
- Alerts contain exact configured contract, expiry, provider timestamp, price/currency metadata, observable candle evidence, calculated intraday support, invalidation and an alternative scenario.
- Missing, stale or mismatched quotes produce no alert. No fabricated prices or order instructions.
- Added tests for the eight-symbol universe, continuous-symbol exclusion, missing-data behavior and contract overrides.

## Provider verification caveat
- Configured explicit candidate futures symbols for the December 2026 contracts. These symbols are not yet verified live against Yahoo chart metadata for every asset.
- The monitor checks that the provider returns the exact requested symbol and fresh candles. If a symbol is unsupported, that instrument safely reports NO_DATA and does not send an alert; adjust its contract via the `SPUTNIK_<ASSET>_CONTRACT` and `SPUTNIK_<ASSET>_EXPIRY` environment variables.
- Before relying on the schedule, verify all eight exact symbols in a live run and review CI results.

## Safety
PAPER ONLY. This does not place orders. Feature branch only; not deployed until reviewed and merged.
