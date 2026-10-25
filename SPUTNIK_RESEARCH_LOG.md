# SPUTNIK Research Log

## 2026-10-25 — Count unique SEC filing IDs, not transaction dates

### Finding
In `sputnik_ranking.py`, confirmation count was computed from pairs of `(event_id, transaction_date)`. The collector in `trump_tracker.py` assigns the same event ID to transaction rows from the same SEC filing. A Form 4 containing multiple transactions on different dates could therefore be counted as multiple independent filings and potentially lift a security to `COMPRA` without three distinct disclosures.

### One change implemented
Count only distinct, non-empty `event_id` values when calculating filing confirmations. Do not use transaction dates to manufacture filing identity; rows without a stable event ID contribute no independent-filing confirmation points. The transaction can remain visible as an observed candidate, but missing identity cannot satisfy the three-filing BUY gate.

### Regression tests
- Multiple transaction rows with the same event ID and different transaction dates count as one filing and remain `OSSERVA`.
- Missing event IDs count as zero independent filings and cannot produce `COMPRA`.
- Existing controls preserve the behavior for one, two, and three distinct event IDs.

### CI evidence
Both pull-request workflows completed successfully on tested code/test head `e89d6de516a4cb40d07531b536782628d376bd0a`:
- [SPUTNIK Telegram menu tests — run 40160404865](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40160404865): job `tests` succeeded; it ran the Telegram menu, ranking, CFD, catalyst, and history test modules.
- [SPUTNIK ranking tests — run 40160404938](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40160404938): job `tests` succeeded and ran `python -m unittest discover -s tests -p "test_*.py" -v`. The job log confirms **63 tests ran, all passed**, including both new regression tests.

The connector reported both workflow runs as `completed` with conclusion `success`. This is CI evidence; no local full-suite execution is claimed. The later branch commit changes only this log.

### Evidence and limits
- `trump_tracker.py:event_id()` hashes CIK, SEC accession, form, and primary document.
- `extract_form4_transactions()` assigns the same `event.event_id` to every transaction row from that filing.
- This change prevents duplicate rows from inflating disclosure confirmation; it does not prove market direction, price/volume confirmation, predictive accuracy, or profitability.

### Rollout and safety
- Branch: `fix/sputnik-count-unique-form4-filings-20261025`
- Base: `main`
- Draft PR: [#24 — Count unique Form 4 filings in Sputnik confirmations](https://github.com/andreameloni1984-sys/trump-trucker/pull/24)
- No merge or production deployment performed.
- Render production verification is blocked because no workspace is selected and the connector explicitly requires the user to confirm which workspace to inspect. The only listed workspace was `My Workspace`; no service was queried and no deployment was triggered.
- PAPER ONLY: no orders, broker connections, purchases, costs, or Gagarin integration.
