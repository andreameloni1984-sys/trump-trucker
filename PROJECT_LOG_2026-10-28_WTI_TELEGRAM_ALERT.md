# SPUTNIK WTI Telegram state-change alert — 2026-10-28

## Implemented
- Added `sputnik_wti_alert.py`: reads 5-minute candles for one explicit futures symbol, default `CLZ26.NYM`, and rejects continuous symbols such as `CL=F`.
- Quote timestamp must be within the configured freshness window (default 20 minutes); missing, stale, or mismatched quote data produces no alert.
- Three states: LONG IN TENUTA, PRE-ALLARME DI POSSIBILE INVERSIONE, and INVERSIONE CONFERMATA.
- Early warning requires only one observable weakness signal. Confirmation requires two consecutive closes under a frozen prior support and descending lows.
- Message includes exact symbol/expiry, price, candle timestamp, source, evidence, support, recent candle range vs median range, invalidation and alternative scenario.
- State is persisted only after Telegram API accepts the send; unchanged states are deduplicated.
- Added `run_wti_telegram_alert.py` and a scheduled workflow step, configured for CLZ26.NYM / 2026-11-20.

## Important constraints
- This change is on a feature branch and is not deployed until reviewed/merged.
- Yahoo chart availability for `CLZ26.NYM` is not yet verified in a live scheduled run. If the exact symbol is unavailable or stale, the monitor deliberately sends no market-state alert.
- The configured expiry is explicit to avoid accidental continuous-contract mixing. It must be rolled deliberately before expiry.
- PAPER ONLY; no orders are placed.

## Tests
- Added `tests/test_sputnik_wti_alert.py` for exact-symbol guard, early warning, confirmed break, duplicate suppression, and failed-send behavior.
- CI execution is pending.
