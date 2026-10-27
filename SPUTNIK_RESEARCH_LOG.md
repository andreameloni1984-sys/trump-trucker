# SPUTNIK — Research and implementation log

## 2026-10-26 — Include individual Trump archive posts in the default feed scan

- **Observed issue:** the page-level `TRUTH_ARCHIVE` scan correctly rejects generic archive metadata, but the default item-level RSS scan only included the White House feed. As a result, individual Trump posts could be missed unless `SPUTNIK_RSS_FEEDS` was explicitly configured.
- **Change:** `_configured_rss_feeds()` now defaults to both `https://www.whitehouse.gov/feed/` and `https://www.trumpstruth.org/feed`. Existing item-level parsing continues to use each feed item's title, publication timestamp, URL, text, and deduplication identity.
- **Regression test:** added a test that the default feed list contains both feeds when no environment override is configured.
- **Safety boundary:** this makes individual posts discoverable; it does not turn keyword matches into trade signals. Posts remain catalyst candidates, and price/volume/structure confirmation and risk checks are still required. No order execution, broker connection, deployment, or Gagarin integration was performed.
- **Verification status:** code and test were committed to branch `fix/sputnik-truth-archive-feed`; CI and live feed parsing still need to be checked before merge.


## 2026-10-26 — Require dated, individual public-source entries before catalyst classification

- **Observed issue:** the RSS parser could fall back to the feed URL when an item had no permalink, and intelligence_snapshot() accepted feed entries with missing or unparseable publication timestamps. This allowed non-individual or poorly timestamped rows to enter the public-catalyst history.
- **Implemented:** validate the publication time (ISO/RFC 822), reject timestamps more than five minutes in the future, and require a distinct HTTP(S) item permalink. A verified original permalink may substitute for a missing feed link; a feed-level URL cannot.
- **Regression tests:** missing date, unparseable date, implausibly future date, and missing item permalink are all rejected before deduplication/history insertion.
- **Evidence boundary:** valid metadata establishes a dated public item, not the authenticity of its claims or a directional market signal. Price/volume confirmation remains separate. No production deployment or Telegram delivery is claimed.


## 2026-10-26 — Prevent first-scan RSS backfill from flooding Telegram

- **Finding:** after the TRUTH archive feed was enabled, the first main-branch workflow found 65 item-level RSS candidates. The workflow completed, but the sender does not log per-message Telegram acceptance, so the exact number delivered cannot be confirmed from Actions logs. This exposed a back-catalog burst risk when a feed is added.
- **Implemented:** track initialization per feed, silently seed older entries on the first successful scan, emit only items published within the last five minutes during bootstrap, and ignore items older than a configurable maximum age (default 24 hours). Rejected back-catalog items are still deduplicated so they are not reconsidered every poll.
- **Regression tests:** a new feed containing a two-hour-old item or a two-day-old item produces no catalyst on first scan and records the item/feed initialization state.
- **Verification:** merged to main in commit `67359fb88890ae8ae2b7361c7ba89789adea1003`. The follow-up `SPUTNIK` main workflow succeeded and reported zero new public-source correlations; the listener health endpoint returned `status: ok`. Item-intelligence CI passed 19 tests and ranking CI passed 63 tests before merge.
- **Safety boundary:** the first run after enabling the feed processed 65 candidates and called the sender for each, but per-message Telegram acceptance is not logged, so the exact delivered count is unknown. The backfill guard prevents those stored items from being re-emitted; no test messages or orders were sent.


## 2026-10-26 — Require source and event-specific evidence for historical analogues

- Finding: the historical matcher could accept a pattern when either a broad keyword matched or the event class matched. A de-escalation headline containing the generic word tariff could therefore inherit a different event's historical reaction. The tariff-pause record also pointed only to the Reuters homepage.
- Change: require an HTTPS article-like URL, event-class agreement, and at least one pattern-specific keyword before a historical analogue contributes any directional vote.
- Regression coverage: generic homepage-only and same-class-but-unrelated analogues are rejected; existing escalation and softening examples remain covered.
- Limits: URL shape is only a minimum provenance check, not proof of authenticity or predictive power. No live trade direction is inferred from the historical analogue alone.
- Verification: committed on branch fix/sputnik-analogue-evidence-gate-20261026; awaiting GitHub Actions. Not deployed to Render/Telegram in this run.
- Next: resolve the existing historical-analogue PR conflict through normal review; verify production deploy separately.


## 2026-10-26 — Reduce Telegram intelligence notification flood

### User-reported issue
The user reported receiving roughly 60 Sputnik notifications but no actionable market signal. The code path sent one Telegram message for every new intelligence finding, including generic page-level scans; each message explicitly said it was not a confirmed LONG/SHORT signal. This was a notification-volume and expectation mismatch, not evidence of 60 trades or 60 confirmed catalysts.

### Implemented
- Added `intelligence_digest_message()` to create one compact digest per run from dated, item-level `PUBLIC_RSS_ITEM` records with event ID, publication time, and permalink.
- Changed the main notification path to send at most one intelligence digest per run rather than one push per finding.
- Generic `PUBLIC_SOURCE_TEXT_PAGE_LEVEL` findings remain in local research history but do not trigger Telegram pushes.
- Digest explicitly labels items as catalysts to verify, not confirmed LONG/SHORT signals, and states that price/volume confirmation is still required.
- Added tests for batching 60 findings into one digest (showing at most five links) and suppressing generic/missing-metadata findings.

### Verification status
- Code commit: `369cebbc0bc8491cf332b7c35311e995d4786e7e`.
- Test commit: `a51089923cc7ba8bcef6a5963e81f8198a89cd25`.
- Pull request branch: `fix/sputnik-telegram-intelligence-digest-20261026`.
- CI must run against the new branch head before this change is considered verified. No local test execution is claimed.
- This reduces notification spam; it does not create price/volume-confirmed LONG/SHORT signals.

### Production and safety
- Render/Telegram production has not been changed or deployed by this run. The live service will not use this change until a reviewed merge and verified deployment.
- PAPER ONLY: no real orders, no broker connection, no Gagarin integration, no paid services.


## 2026-10-26 — Remove Sputnik Telegram reply keyboard

- **Richiesta:** eliminare la pulsantiera persistente dalla chat Telegram di Sputnik.
- **Modifica:** `send_telegram()` include ora `reply_markup={"remove_keyboard": true}` in ogni risposta del bot, così Telegram rimuove la tastiera personalizzata quando arriva un messaggio di Sputnik.
- **Verifica aggiunta:** test unitario che controlla il payload inviato a Telegram e la richiesta di rimozione della tastiera.
- **Limite:** questa modifica rimuove la tastiera personalizzata di risposta; non cancella eventuali comandi mostrati nel menu Telegram né modifica retroattivamente messaggi con tastiere inline.
- **Stato:** modifica proposta nel branch della PR #33; non ancora distribuita in produzione. Test non eseguiti in questo ambiente.

 
## 2026-10-26 — Convert explicit news catalysts into directional hypotheses

- **Problema:** il digest descriveva notizie ma non proponeva nemmeno un'ipotesi direzionale utile.
- **Modifica:** aggiunte regole conservative per frasi esplicite su escalation/de-escalation commerciale, interruzioni dell'offerta energetica e sorprese sui tassi. Il digest può ora mostrare strumenti e bias LONG_BIAS/SHORT_BIAS con motivazione e fonte.
- **Guardrail:** richiede evento RSS individuale con ID, permalink e data; notizie ambigue e pagine generiche non generano ipotesi. Le ipotesi non sono segnali d'ingresso: Sputnik non dispone qui di conferma indipendente live di prezzo, volume e struttura, quindi dichiara che l'ingresso non è autorizzato.
- **Test aggiunti:** escalation commerciale mappa a ipotesi su NASDAQ100 e GOLD; pagine generiche e titoli vaghi devono essere ignorati.
- **Verifica:** codice e test salvati nel branch della PR #33; esecuzione dei test e CI non ancora confermate; nessun deploy di produzione eseguito.


## 2026-10-26 — Prefer individual Atom alternate links over self endpoints

- **Finding:** Atom feeds may list a `rel="self"` API endpoint before the article's `rel="alternate"` permalink. Selecting the first `link` could store an API URL as the news item's canonical URL, weakening deduplication and making a Telegram source link less useful.
- **Implemented:** the public-feed parser now selects only default/alternate links and ignores self/enclosure links. An explicit alternate link is preferred when present; if no valid alternate exists, the parser falls back to the feed URL, which the existing operational intake gate rejects as a non-individual permalink.
- **Regression tests:** self-before-alternate ordering and self-only entries.
- **Limits:** parser-level tests only; live feed behavior and Render deployment are separate checks. No Telegram test message or trade order was sent.


## 2026-10-26 — Require issuer and security identity before ranking

- **Finding:** joining missing CIK/security values with separators still created a truthy grouping key, allowing unidentified Form 4 rows to enter ranking or inflate the filing count for a named security.
- **Implemented:** `rank_purchase_candidates()` now skips rows without both issuer CIK and security description before grouping.
- **Regression tests:** missing CIK/security are excluded; an unidentified row cannot inflate the filing count for an identified security.
- **Limits:** a security description is not a ticker or exchange instrument ID; this is identity hygiene, not a directional prediction or profitability claim. Render deployment remains blocked by exhausted build minutes.
- **Safety:** PAPER ONLY; no broker, orders, or paid services.


## 2026-10-26 — Suppress repeated SEC requests after HTTP 403

- **Finding:** SEC submissions and filing-document fetches had no host-wide cooldown after HTTP 403. A collector cycle with multiple CIKs could repeat denied requests and emit avoidable errors.
- **Implemented:** `trump_tracker.py` now starts a six-hour process-local cooldown for SEC hosts after HTTP 403, skips remaining CIKs while the cooldown is active, and leaves White House/other public-source requests unaffected.
- **Regression tests:** `tests/test_sec_403_cooldown.py` verifies that the first 403 starts the cooldown, a subsequent SEC request is suppressed without another network call, and non-SEC public documents still fetch.
- **CI:** pending on PR branch; no test result is claimed until GitHub Actions completes.
- **Deployment:** Render auto-deploy is commit-triggered, but the workspace has exhausted build-pipeline minutes. This branch is not live; no manual deploy was triggered.
- **Limits:** the cooldown is process-local and resets on process restart; it reduces repeated denied requests but does not repair SEC access policy or prove filings are current.
- **Safety:** PAPER ONLY; no broker, order, secret-value inspection, test Telegram message, or paid service.

## 2026-10-27 — Count distinct SEC filings and align the documented event weight

- **Evidence:** the retrievable 2026-10-06 conversation records the user-accepted Sputnik 0–100 scoring design: source quality 25, event strength 20, independent confirmations 15, documented relationship 15, recency 10, sector impact 10, and social-evidence quality 5. I did not find a standalone Library source independently confirming those exact weights, so they are treated as the accepted implementation specification—not empirical proof and not 100 separate rules. Current `main` used event strength 25 and counted `(event_id, transaction_date)` as a filing identity.
- **Finding:** separate transaction rows from the same SEC Form 4 could be counted as independent confirmations; the event weight also differed from the documented rubric.
- **Change:** `sputnik_ranking.py` now prefers SEC accession identity and otherwise canonicalizes the source permalink (scheme/host normalized, query and fragment removed). Multiple rows from one filing count once. Event-strength weight is aligned to 20.
- **Regression tests:** `tests/test_sputnik_ranking.py` covers accession normalization, same-filing rows with different event IDs/transaction dates, and three recent distinct filings. With unsupported relationship/sector/social evidence left at zero, three filings score 70 and remain `OSSERVA`, not `COMPRA`.
- **Operational path:** public Form 4 rows → candidate grouping → distinct filing count → 0–100 score → COMPRA/OSSERVA/EVITA.
- **CI:** PASS on PR head `6200775032b1946da9a3269e3b26c71acef64fd2`: SPUTNIK ranking tests run `40469292377` and Telegram menu tests run `40469292329`.
- **Deployment:** Render main service is auto-deploy on main; branch is not merged. No deploy was triggered. Latest observed listener live commit remains `9e5204bf7d9074dba27637013b7d98933a91e733`; latest deploy attempt `50851b0dc76f1b7ed0adaa872c47aa84793687f9` failed. Build quota is exhausted.
- **Empirical validation:** no historical replay or out-of-sample ranking study performed. This is scoring-integrity validation, not a return/profitability claim.
- **Safety:** PAPER/DEMO ONLY; no broker, order, or Telegram test message.

## 2026-10-27 08:33 UTC (09:33 CET) — Require numeric SEC accession and a filing document URL

- **Finding:** the primary-source gate checked that CIK/accession path components were merely non-empty and that a sixth path segment existed. A lookalike archive path with a non-numeric CIK/accession or an index page could pass the provenance gate.
- **Change:** `sputnik_ranking.py::_is_primary_sec_form4_url()` now requires a numeric CIK, an 18-digit dashless accession directory, and a document filename ending in `.xml`, `.htm`, `.html`, or `.txt`; generic `index.htm/html` pages are rejected. Nested document paths remain allowed.
- **Files:** `sputnik_ranking.py`; `tests/test_sputnik_ranking.py`.
- **Regression:** test fixtures now use SEC-shaped numeric accession directories. Invalid CIK/accession, index-page and non-document URLs are rejected; existing valid archive URLs with query/fragment remain accepted.
- **Commits:** code `b4e881be69655312994edc775783f45c3bb2c232`; tests `b03828b0b6f30e3f5b6b2a0a447c03601ac149d7`.
- **CI:** PASS on the code/test head: [ranking tests](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40474531848), [Telegram menu tests](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40474531852).
- **Deployment:** PR #53 only, not merged. Render workspace was not selected in this run; no deploy was triggered, and the live commit was not re-verified.
- **Empirical limit:** stricter provenance validation is not predictive validation; no historical replay or out-of-sample return study.
- **Safety:** PAPER/DEMO ONLY; no secrets, broker, orders or Telegram test messages.


## 2026-10-27 08:53 UTC — Fail closed on impossible or future Form 4 chronology

- **Finding:** the ranking validated source provenance and distinct filing identity, but an otherwise valid SEC URL could still contribute confirmation points when the transaction/filing dates were invalid, future-dated, or chronologically impossible.
- **Change:** `sputnik_ranking.py` now requires parseable transaction and filing dates with `transaction_date <= filing_date <= as_of_date`. `rank_purchase_candidates()` resolves one UTC as-of date and uses it consistently across candidate groups.
- **Regression:** `tests/test_sputnik_ranking.py` now rejects invalid transaction/filing dates, future transactions, future filings, and a filing dated before its transaction.
- **CI:** new code/test commit will trigger the ranking and related PR workflows; final status is to be recorded after GitHub Actions completes.
- **Deployment:** PR #53 branch only; no merge/deploy. Render build-pipeline minutes remain exhausted.
- **Empirical limit:** chronology integrity only; no historical replay or out-of-sample return validation.
- **Safety:** PAPER/DEMO ONLY; no broker, orders, secrets, or Telegram test messages.


## 2026-10-27 09:07 UTC — Match SEC archive provenance to the transaction row

- **Finding:** URL-shape validation alone can accept a genuine SEC archive document that belongs to a different issuer or filing than the transaction row being scored.
- **Change:** `sputnik_ranking.py::_source_matches_filing_identity()` now requires the archive CIK to match the row CIK. When accession metadata is present, its normalized accession must match the 18-digit accession in the URL. Rows with absent/non-numeric CIKs fail closed.
- **Operational path:** Form 4 transaction → primary URL validation → CIK/accession consistency → distinct filing count → ranking.
- **Regression:** `tests/test_sputnik_ranking.py` rejects issuer CIK mismatch and accession mismatch, and accepts matching accession metadata.
- **Commits:** code/test commits are recorded in the PR activity; research-log commit follows the code and tests.
- **CI:** pending for this update; record final workflow outcomes after GitHub Actions completes.
- **Deployment:** PR #53 branch only; no merge or deploy. Render workspace was not selected; live commit not re-verified.
- **Empirical limit:** identity/provenance integrity only; no filing replay, market outcome study, or out-of-sample return validation.
- **Safety:** PAPER/DEMO ONLY; no secrets, broker, orders, or Telegram test messages.


## Verification — 2026-10-27 09:07 UTC (SEC row/URL identity)

- **Final code commit:** `f5f9f3acd4d47da02346ef2eda3149b1a5b10ccc`
- **Regression tests commit:** `3806d87b9387d9b0d9d9075babb76c9f38291dc4`
- **Research log prior commit:** `4f98d38376321c8fc25a8d8dc2588c9bdc849dec`
- **CI on final code/test/log head:** ranking tests [run 40478611051](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40478611051) and Telegram menu tests [run 40478611202](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40478611202), both SUCCESS.
- **Deployment:** PR #53 branch only; not merged or deployed. Render workspace not selected, so live commit was not checked this run.
- **Empirical limit:** provenance consistency only; no filing replay or out-of-sample return test.


## 2026-10-27 — Reject malformed SEC calendar-date fields

- **Finding:** `_parse_date()` attempted ISO datetime parsing and then fell back to `value[:10]`. A malformed value such as `2026-10-05 trailing-data` could therefore be treated as a valid SEC transaction/filing date; datetime strings could also be silently reduced to a date despite these fields representing SEC calendar dates.
- **Change:** parse only strict `YYYY-MM-DD` strings in `sputnik_ranking.py`; reject timestamps and malformed suffixes rather than inferring a date. Upstream timestamp normalization must be explicit before values enter these date fields.
- **Operational path:** Form 4 transaction/filing fields → strict date parsing → chronology/as-of guard → distinct-filing scoring.
- **Regression:** `tests/test_sputnik_ranking.py` covers timestamps, trailing garbage, non-padded dates, non-string values, and a malformed date passed into the ranking path.
- **CI:** pending for this code/test update; record final workflow outcomes after GitHub Actions completes.
- **Deployment:** PR #53 branch only; no merge/deploy. Render build-pipeline quota remains exhausted.
- **Empirical limit:** schema/chronology integrity only; no SEC replay or out-of-sample return validation.
- **Safety:** PAPER/DEMO ONLY; no secrets, broker, orders, or Telegram test messages.


## Final CI verification — strict SEC date parser (2026-10-27 09:50 UTC)

- **Final code head:** `926fc13b0c7b9c4328ab491ff7d4ab2b029c8d9c`; parser fix corrected an escaping error in the first regex edit before the final successful run.
- **Regression tests:** commit `7c0897e8b071a48762a4f032b9ff5698ccdf8f82`; the initial run failed because the regex was over-escaped, and the corrected code commit was then tested.
- **CI PASS on corrected code head:** ranking [run 40483767939](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40483767939) and Telegram menu [run 40483767930](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40483767930).
- **Deployment:** PR #53 branch only, no merge/deploy; Render workspace not selected in this runtime.
- **Empirical limit:** strict date schema only; no filing replay or out-of-sample market validation.

## 2026-10-27 — Recover the accepted Sputnik 0–100 scoring rubric from the 2026-10-06 conversation

- **Historical source:** prior conversation record dated 2026-10-06 02:35 UTC. No independent Library document with these exact weights was found, so treat this as the user's accepted implementation specification, not as a separately sourced research finding.
- **Recovered weights (sum 100):** source quality 25; political/documentary event strength 20; independent confirmations 15; documented company/sector relationship 15; timeliness 10; sector impact 10; social signal 5.
- **Recorded penalties:** unverifiable, duplicate, stale, contradictory, or undocumented evidence must reduce or disqualify a candidate. Unsupported relationship/sector/social evidence stays at zero rather than being inferred.
- **Implementation mapping:** `sputnik_ranking.py` → SEC/Form 4 source validation, filing identity/deduplication, chronology checks, component scoring and `/ranking` / “Trump ordina” output; regression coverage in `tests/test_sputnik_ranking.py`. PR #53 contains the current implementation work.
- **CI evidence:** PR #53 records passing ranking and Telegram-menu tests on the tested code commit `cb79a0f680aec16a82b41d4248631515c0bd7071`; later branch changes must be checked independently before merge.
- **Deployment:** PR #53 remains open; no merge/deploy. Render's latest known successful Sputnik deployment is commit `9e5204bf7d9074dba27637013b7d98933a91e733`; the later attempt `50851b0dc76f1b7ed0adaa872c47aa84793687f9` failed. The live service is not using this PR's code.
- **Empirical limit:** the rubric is an accepted scoring specification, not a validated probability model. No historical replay, calibration, or out-of-sample profitability result is claimed.
- **Terminology:** this recovered item is a 100-point score rubric; it is not evidence of a separate catalog containing 100 individual lessons.

