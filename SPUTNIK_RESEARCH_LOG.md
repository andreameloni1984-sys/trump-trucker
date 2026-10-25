# Sputnik Research & Implementation Log

## 2026-10-25 — Reject impossible SEC filing chronology

### Finding
The ranking engine accepted Form 4 transaction rows even when the documented filing date was earlier than the transaction date. Such a row has an impossible chronology and could contribute to the distinct-filing confirmation count.

### Implemented
- Added `_filing_chronology_valid()` in `sputnik_ranking.py`.
- Exclude a row only when both dates parse successfully and filing date precedes transaction date.
- Missing or malformed dates remain eligible for the existing informational/unknown-date behavior; this change does not pretend missing data proves invalid chronology.
- Added regression tests for an impossible row by itself and for an impossible row not inflating the independent-filing count.

### Evidence
- Code commit: `33666a67b81c57a27e144ea2696abc1214d5dc32`.
- Test commit: `15be9334e96f79aab5bae46497c4752c016dc7fc`.
- CI evidence: both pull-request workflows completed successfully on head `a7c981cde0d69a0d9dbaed789698818fcc5254c9`:
- [SPUTNIK Telegram menu tests — SUCCESS](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40164109684).
- [SPUTNIK ranking tests — SUCCESS](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40164109766); its test log reports 63 tests run, all OK, including the ranking test module. The code and regression tests are in this tested PR head. No local full-suite execution is claimed.

### Limitations / next checks
- This validates date ordering only; it does not verify the SEC filing itself or prove market-direction accuracy.
- Disclosure business-day calculations still do not model federal holidays or SEC exceptions.
- No market prices, entries, stops, targets, or predictive metrics are inferred.
- Production Render/Telegram status must be checked separately; no deployment is authorized.

### Safety
PAPER ONLY. No real orders, broker connection, deployment, paid services, or Gagarin integration.

### CI result update (2026-10-25)
- Telegram menu workflow: completed/success.
- Ranking workflow: completed/success; test log confirms 63 tests, OK.
- Render workspace listing returned a single workspace named `My Workspace`, but production inspection was not performed because workspace selection requires explicit user confirmation. No deploy was triggered.
