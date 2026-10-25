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

### Evidence and limits
- `trump_tracker.py:event_id()` hashes CIK, SEC accession, form, and primary document.
- `extract_form4_transactions()` assigns `event.event_id` to each transaction row from that filing.
- This change prevents duplicate rows from inflating disclosure confirmation; it does not prove market direction, price/volume confirmation, predictive accuracy, or profitability.
- CI evidence is pending at branch creation and will be added after the pull-request checks complete.
- Local execution of the complete test suite is not claimed.

### Rollout and safety
- Branch: `fix/sputnik-count-unique-form4-filings-20261025`
- Base: `main`
- No merge or production deployment performed.
- Render/Telegram production verification remains separate; a workspace selection is required before querying that account's service details.
- PAPER ONLY: no orders, broker connections, purchases, costs, or Gagarin integration.
