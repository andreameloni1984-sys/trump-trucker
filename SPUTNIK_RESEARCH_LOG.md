# Sputnik Research & Implementation Log

## 2026-10-26 — Require issuer and security identity before ranking

### Finding
`rank_purchase_candidates()` previously built a grouping key by joining CIK, security and company strings, then tested the joined key for truthiness. Because the separators themselves make the key non-empty, rows with missing issuer/security identifiers could enter ranking and potentially be mixed with other incomplete rows. The output could fall back to a generic “Titolo N/D” label instead of a verifiable security identity.

### Implemented
- Require a non-empty SEC issuer CIK and non-empty security description before adding a Form 4 purchase row to a ranking group.
- Keep company name as a grouping discriminator when available, but do not use it as a substitute for issuer/security identity.
- Add regression tests for missing CIK/security and for an unidentified row not inflating a named security's filing count.

### Evidence
- Code commit: `7cc1868b6bf522a50cd105444c2f238e1d9f0623`.
- Test commit: `432042e3877b5439a223b64e15a1f07a078bd21f`.
- CI evidence: both workflows completed successfully on PR head `f35237847f7a57303e340f88f093cd85db9498d8`:
- [SPUTNIK ranking tests — SUCCESS](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40267542867).
- [SPUTNIK Telegram menu tests — SUCCESS](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40267542843).

### Limitations / blockers
- A security description is not a ticker or unique exchange instrument identifier; it reduces ambiguity but does not replace issuer/security mapping validation.
- This change improves candidate identity hygiene, not market-direction accuracy or profitability.
- Production Render/Telegram must be checked separately; no deployment authorized or performed.

### Safety
PAPER ONLY. No real orders, broker connections, paid services, or Gagarin integration.
