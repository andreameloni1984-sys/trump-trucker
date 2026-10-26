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


## 2026-10-25 — Reject impossible Form 4 filing chronology

### Finding
The ranking path already reported negative disclosure lag as `N/D`, but it could still accept that row as purchase evidence. A filing date earlier than its documented transaction date is internally inconsistent and should not contribute to a ranked candidate.

### Implemented
- Replaced the future-only date check with `_transaction_dates_consistent()`.
- Excluded a row when its parseable transaction date is in the future or its parseable filing date predates the transaction date.
- Kept missing/unparseable dates as unknown; this change does not claim those rows are validated.
- Added regression test `test_filing_before_transaction_date_is_excluded`.

### Evidence and verification status
- Code commit: `622bb0e82f972f36dfca5567e2c5e110d73c5f84`.
- Test commit: `916dd3fe83136a1cddb51b28d41631a13bdb57d0`.
- This branch has not yet had CI results for the new head; tests are added but **not yet verified by CI**.
- This is chronology validation only, not proof of source authenticity or predictive accuracy.

### Blocks and safety
- Production Render/Telegram status not checked in this execution; no deployment claimed.
- PAPER ONLY: no real orders, broker connection, paid services, or Gagarin integration.


## 2026-10-26 — Prevent duplicate filing IDs from inflating confirmations

### Finding
The ranking previously counted a confirmation using the pair `(event_id, transaction_date)`. If one filing/event ID appeared on multiple rows with different transaction dates, those rows could be counted as separate confirmations and potentially inflate the BUY score.

### Implemented
- Count confirmations by distinct, non-empty `event_id` only.
- Rows with a missing event ID no longer add confirmation points.
- Added regression test `test_same_filing_id_with_different_transaction_dates_counts_once`.

### Evidence and verification
- Ranking code commit: `4e783243ff84d67719848069303182f6f00bcfe2`.
- Test commit: `43ee75aa1785f7f971505bb148103e01abc445a1`.
- Earlier CI for the chronology fix completed successfully: [ranking tests](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40194402671) and [Telegram menu tests](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40194402674).
- Those CI runs predate this duplicate-ID change; the current head still needs its own CI result. No local test run is claimed.

### Limits and safety
This prevents one class of duplicate-evidence inflation; it does not validate the identity of every event ID or prove market predictiveness. Production Render/Telegram was not checked and no deploy is claimed. PAPER ONLY; no real orders, broker connection, paid service, or Gagarin integration.
