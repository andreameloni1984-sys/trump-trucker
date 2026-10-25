# Sputnik Research & Implementation Log

## 2026-10-25 — Exclude future-dated Form 4 transactions from ranking

### Finding
The ranking function gave a future-dated transaction zero recency points but still allowed that row to count toward the number of distinct filing confirmations. A malformed/future transaction date must not contribute as though it were an observed historical purchase.

### Implemented
- Added `_transaction_date_not_future()` to `sputnik_ranking.py`.
- Use one reference date for both eligibility and recency scoring so a candidate is evaluated consistently.
- Exclude a row only when its transaction date parses successfully and is later than the reference date.
- Preserve the existing unknown-date behavior: missing or unparseable dates are not falsely labelled future, though they receive no recency points.
- Added regression tests for a future-dated row alone and for a future-dated row being unable to supply a third confirmation.

### Evidence
- Code commit: `3cf2122e8bd7dc9b5a81754165345d4d22271bdb`.
- Test commit: `236aa7880b26c9f22423ecddc04ecb3a946498d0`.
- CI evidence on tested PR head `bbca7e3a3ee984d36e0437fa8b059306c4a8ae52`:
  - [SPUTNIK ranking tests — SUCCESS](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40164511328); logs report 63 tests run, all OK, including both new regressions.
  - [SPUTNIK Telegram menu tests — SUCCESS](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40164511358).
- The later commit updates this log only; no local full-suite execution is claimed.

### Limitations / related work
- This is a chronology sanity check, not verification of the SEC source itself and not evidence of predictive accuracy.
- The separate PR #25 addresses filing dates earlier than transaction dates; it remains separate and is not silently assumed to be merged into `main`.
- No market price, entry, stop, target, or accuracy metric is inferred.

### Production and safety
- Render/Telegram production must be inspected separately; no deployment is authorized.
- PAPER ONLY: no real orders, broker connection, paid services, or Gagarin integration.
