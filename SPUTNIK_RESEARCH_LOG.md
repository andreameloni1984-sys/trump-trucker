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

## 2026-10-27 — Telegram outputs one market-opportunity hypothesis

- **Finding:** the decision callback returned a multi-scenario explainer/watchlist, not the requested single `SPUTNIK — OPPORTUNITÀ DI MERCATO` result.
- **Implemented:** `sputnik_decision_engine.py` now emits one top-ranked catalyst hypothesis with instrument, LONG/SHORT bias, intraday/PAPER TRADING labels, catalyst/source, rationale, alternative scenario, invalidation and operational status. If no catalyst is identified it returns a transparent WAIT result.
- **Quote safety:** `telegram_listener.py` now passes persisted market quotes to the formatter. Entry/SL/TP are only calculated by `build_conditional_trade_plan` when a fresh timestamped quote and ATR are present; missing data is stated rather than invented.
- **Regression tests:** updated `tests/test_sputnik_decision_engine.py` for the new Telegram format and no-catalyst fallback. GitHub Actions validation is pending; do not consider this fully verified until the run completes.
- **Delivery limits:** code now feeds the Telegram callback response, but this change alone does not prove a scheduled/live Telegram message was sent. Render deployment status and credentials were not verified in this run.
- **Safety:** PAPER TRADING only; no real orders sent.
- **CI correction:** the first test run exposed two stale expectations and a missing explicit confirmation line. Updated the output to include the catalyst's confirmation criteria and adjusted the legacy-domain test to expect WAIT rather than an invented directional trade. Follow-up CI runs are pending.


## 2026-10-28 — Persist SPUTNIK action/reaction decisions for outcome review

- **Observed evidence gap:** the tracked `sputnik_state.json` snapshot contains 247 intelligence-history entries but an empty `events` map. Legacy findings preserve source/domain metadata, while the Telegram action/reaction path rendered a conditional opportunity without writing a structured record of the actual instrument, direction, quote timestamp, entry, SL and TP used in that analysis. This prevents later signal-by-signal scoring from those records alone.
- **Implemented on branch `fix/sputnik-signal-audit-journal-20261028`:** add `sputnik_signal_journal.py` and call it from the existing action/reaction view. Each displayed analysis appends one JSONL audit record with event ID/detection time, source, catalyst excerpt, instrument, direction, decision status, quote timestamp and available entry/SL/TP/ATR. Missing/stale quotes remain null and are explicitly marked not scorable; outcomes are initialized as unscored, never guessed.
- **Regression tests:** verify a fresh timestamped Brent quote yields the expected conditional levels; missing quotes do not invent prices; non-specific text records WAIT; source event identity is retained.
- **Empirical limit:** this creates a signal-analysis audit trail for future scoring; it does not backfill historical prices or prove a directional edge. Existing tracked state does not provide historical quote sequences or verified outcomes. Render's configured journal path/durable storage and live Telegram logs were not accessed.
- **Validation status:** branch/PR CI must complete before this is considered verified. No Telegram test message, broker connection, order, merge or deployment was made.
- **Safety:** PAPER ONLY; analysis journal, not an execution ledger.


## 2026-10-28 — Live log check: no outcome-grade SPUTNIK signal records

- **Render evidence checked:** the `sputnik-telegram-listener` application logs between 2026-10-27 05:45 UTC and 2026-10-28 05:50 UTC returned six service-start/Telegram-bootstrap sequences, but no structured decision, instrument, entry, SL/TP or outcome records. This does not prove no user-requested analysis occurred; the current listener does not log its rendered decision text.
- **Tracked state evidence:** `sputnik_state.json` was last updated at 2026-10-28T02:21:51Z. Its `events` map is empty; the intelligence history contains source/domain/status metadata, not price-level trade outcomes.
- **Conclusion:** no defensible SPUTNIK hit rate or realized directional accuracy can be calculated from the accessible records. PR #59 starts an audit record for future action/reaction analyses, but the Render journal path and durable storage have not been verified; do not treat file logging as durable until the service has a confirmed persistent destination.
- **Safety:** logs inspected read-only. No Telegram test message, broker connection, order, merge or deployment.


## 2026-10-28 — Preserve publication-to-detection latency in the SPUTNIK audit journal

- **Observed gap:** RSS ingestion validates each item's publication timestamp, but the action/reaction audit record only retained detection time. Without a normalized publication timestamp, later analysis could not measure how stale a catalyst was when detected or displayed.
- **Implemented on the existing PR #59 branch:** persist the normalized source `published_at` in intelligence history, pass it into the SPUTNIK analysis journal, and record `publication_to_detection_seconds` only when both timestamps parse. Missing/invalid timestamps remain null; no latency is inferred.
- **Regression test:** a synthetic item published 120 seconds before detection must retain the timestamp and report approximately 120 seconds; records without timestamp metadata must keep the latency null.
- **Evidence limits:** the tracked historical state does not contain complete source publication timestamps for older records, and the durable live journal has not been inspected. This enables measurement for newly ingested items only; it does not backfill past events or prove predictive edge.
- **Validation:** PR CI will run against the updated head. No Render workspace was selected because the available workspace must be explicitly confirmed before querying live resources. No merge, deployment, Telegram test message, or broker order.
- **Safety:** SPUTNIK remains a separate PAPER-only intelligence/audit service; no GAGARIN runtime integration was changed.
