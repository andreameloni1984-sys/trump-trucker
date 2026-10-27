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


## 2026-10-27 — Match catalyst actions/topics as whole words

- **Finding:** `sputnik_decision_engine.py::_evidence` used substring matching. The action token `hit` occurs inside the unrelated word `White`; paired with an oil-price topic, this could create a false oil-supply catalyst.
- **Implemented on research PR branch:** a whole-word/phrase matcher now checks action and topic evidence. Explicit variants such as `hit`, `hits`, `hitting`, and `attacked` remain listed in the rule table.
- **Regression:** `tests/test_sputnik_decision_engine.py::test_word_fragment_does_not_count_as_oil_disruption_action` rejects “White House discusses oil prices in a routine briefing.”
- **CI finding:** an earlier main-branch ranking run failed `test_message_has_confirmation_and_invalidation`; the current main file includes the expected invalidation line, but a fresh passing run on the current SHA is still required. This change is separate and does not claim to fix that prior run.
- **Deployment:** no merge/deploy; Render build-pipeline minutes remain exhausted. The change is on a non-main branch and no Render preview is configured.
- **Limits:** deterministic keyword matching only; no headline replay, price/volume event study, or OOS edge established. PAPER ONLY.


## 2026-10-27 — Preserve plural tariff topics after whole-word matching

- **CI finding:** the first PR #55 run failed two existing positive-control tests. The new whole-word matcher correctly stopped the false `hit` substring inside `White`, but it also exposed that the rule table listed singular `tariff` while the valid headline says `tariffs`.
- **Correction:** explicitly add `tariffs` (and `import duties`) to the tariff-escalation topic vocabulary, and add the plural `tariffs` to the trade-de-escalation vocabulary. This keeps word-boundary matching strict without losing known inflections.
- **Regression:** existing `test_tariff_action` is the positive control for “announces new tariffs”; the new word-fragment negative test remains.
- **CI:** rerun pending on the corrective commit. The previous PR #55 run failed at `test_tariff_action` and `test_message_has_confirmation_and_invalidation` because no catalyst was matched; do not treat that run as passing.
- **Deployment:** no merge/deploy. PAPER ONLY; no live alert delivery or market edge is claimed.


## 2026-10-27 — Keep new-tariff announcements separate from trade de-escalation

- **Review finding:** the first word-boundary correction added `tariffs` to both escalation and de-escalation topic vocabularies. A headline announcing new tariffs must not match a trade-de-escalation rule just because both mention tariffs.
- **Correction:** keep the plural `tariffs` and `import duties` in the escalation rule only; trade de-escalation continues to require its agreement/pause language. The existing tariff test now asserts that a new-tariff headline does not produce a `trade_deescalation` row.
- **CI:** the first run on commit `2f7c4ead73183db262fe75759665fec49e43027d` failed because whole-word matching exposed missing plural vocabulary. Commit `d76b48c62a653129c4622cb500ff33b333e6fb69` added that vocabulary; this follow-up narrows the de-escalation rule and adds an explicit regression assertion. CI for this head is pending.
- **Safety/limits:** no merge/deploy, no real orders. Keyword rules are not a substitute for source verification or price/volume confirmation; no historical or OOS performance claim.


## Final verification — whole-word catalyst matcher (2026-10-27)

- **Code/test head:** `899790b02620082b0b224fdec99ecf7fa2aa0cb8`.
- **CI PASS:** SPUTNIK ranking tests [40577683546](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40577683546). The suite includes the new whole-word negative control and the existing plural-tariff positive control. The earlier run on `2f7c4ead73183db262fe75759665fec49e43027d` failed two tests; explicit plural vocabulary and separation of escalation/de-escalation fixed the observed regressions. The Telegram-menu workflow did not trigger on this head and is not claimed as passed.
- **Main:** current SHA `780b06b078747d2ce71385e9b0f9a9942aaca794`; ranking workflow [40576677519](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40576677519) passed after the explicit invalidation-label correction. This is a separate main commit, not the PR #55 change.
- **Render:** latest successful deployment returned remains `9e5204bf7d9074dba27637013b7d98933a91e733`; later attempt `50851b0dc76f1b7ed0adaa872c47aa84793687f9` failed with exhausted pipeline minutes. No new deploy event was observed for main SHA `780b06b...`.
- **Runtime limits:** the queried 2026-10-27 20:10–20:25 UTC log window returned no SEC/White House/source lines, so current source ingestion and alert delivery are not confirmed. Setting names `GAGARIN_CLOUD_API_URL` / `GAGARIN_CLOUD_API_KEY` were inspected only in code; no secret values read.
- **Empirical limit:** deterministic keyword tests only; no historical headline replay, price/volume event study or OOS edge established. No merge/deploy. PAPER ONLY.


## 2026-10-27 — Treat punctuation-adjacent negation as a whole token

- **Finding:** after whole-word matching was added for catalyst actions/topics, the negation gate still used padded substring checks. A negation such as `never` adjacent to an em dash could evade the gate, leaving a sentence with an action/topic pair eligible as a catalyst.
- **Change:** `sputnik_decision_engine.py::_evidence` now uses the existing whole-word matcher for each normalized negation token, preserving multi-word phrases while recognizing punctuation boundaries.
- **Regression:** `tests/test_sputnik_decision_engine.py::test_negation_adjacent_to_punctuation_still_blocks_catalyst` rejects a negated tariff headline with em dashes; the existing explicit-negation and positive tariff controls remain in the same suite.
- **Commits:** code `d42ee07934fc6a8f2fa630d088aaa2c9bd791489`; regression test `66b3152b445a8560c286fa00bcf58fb3e5b1a5b7`.
- **CI:** SPUTNIK ranking tests passed on the code/test head: [run 40582630474](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40582630474). The current PR head at log-update time is `66b3152b445a8560c286fa00bcf58fb3e5b1a5b7), based on current `main` `780b06b078747d2ce71385e9b0f9a9942aaca794`; compare reports 6 commits ahead, 0 behind, and PR metadata says mergeable. This is branch CI, not a production check.
- **Operational path:** public text → sentence splitting → negation gate → catalyst action/topic evidence → conditional hypothesis → independent price/volume confirmation. News remains a hypothesis, not an order.
- **Render/runtime:** no Render or Telegram log connector was available in this run; no deploy was attempted and the live Render commit was not verified. The last known runtime report recorded exhausted build minutes; current quota could not be rechecked. SEC 403 cooldown code and the White House RSS URL are present in `trump_tracker.py`, but live ingestion/alert delivery is not confirmed. Only the names `GAGARIN_CLOUD_API_URL` and `GAGARIN_CLOUD_API_KEY` were inspected, never their values.
- **Empirical limit/safety:** synthetic unit regression only; no historical headline replay, event study or OOS edge. No merge/deploy, broker, real order or Telegram test message. PAPER ONLY.


## 2026-10-27 — Open-PR base audit

- **Main SHA:** `780b06b078747d2ce71385e9b0f9a9942aaca794`; latest main ranking workflow [40576677519](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40576677519) passed. Several earlier intermediate pushes failed before their corrective commits; those failures are retained as history, not hidden.
- **Open PR inventory:** 35 open PRs were returned. 25 target `main`; 24 of those had a base SHA older than current `main`; 10 are stacked on another branch. The inventory includes overlapping work on timestamp handling, source provenance/deduplication, SEC retry policy, Telegram dispatch and conditional market hypotheses.
- **Current PR #55:** base SHA matches current main, head `4eba9eea321a8f9280ca4be586e58d14753abea6`, compare is 7 commits ahead / 0 behind, GitHub metadata says mergeable; ranking workflow [40582775585](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40582775585) passed on that head.
- **Decision:** no automatic rebase, merge or deploy. Older PRs require individual diff review because many are stacked and some cover overlapping fixes; merging them as a batch could duplicate or regress behavior. PAPER ONLY.


## 2026-10-27 — Scope negation to semicolon-separated clauses

- **Finding:** `_sentences()` split on periods, question/exclamation marks, and newlines, but not semicolons. A sentence such as “The report denied a production cut; Iran threatens shipping near Hormuz and oil exports.” could suppress the independent shipping-risk clause because the earlier clause contained “denied”.
- **Change:** treat semicolons as clause boundaries before evaluating catalyst evidence. The existing negation guard remains conservative within each clause.
- **Regression:** `tests/test_sputnik_decision_engine.py::test_semicolon_scopes_negation_to_its_clause`; it uses the existing positive oil-flow wording after a semicolon and asserts that Brent remains a conditional candidate. Existing negative-control tests remain in place.
- **Commits:** code `818a2899d77db146e5e6043ab383214d91ccc159`; test `ec1721cab064f6f442ce12849deec995c89592e2`.
- **CI:** SPUTNIK ranking tests passed on code/test head `ec1721cab064f6f442ce12849deec995c89592e2`, run [40590079265](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40590079265).
- **Operational path:** public item text → clause splitting → negation guard → whole-word action/topic evidence → conditional catalyst hypothesis → independent price/volume confirmation. This change does not convert news into a confirmed trade.
- **IBKR session 9 crosswalk:** the recorded requirement to preserve source provenance, publication/availability timing, text evidence, and fixed reaction horizons maps to the public-item/catalyst path; this lexical regression addresses only clause-level false suppression. It does not validate source truth or predictive value.
- **Deployment/limits:** PR #55 branch only; no merge/deploy. Render workspace and Telegram runtime logs were not accessible through the tools in this run. Synthetic language regression only; no event replay, price/volume study, or OOS performance claim. PAPER ONLY.
- **Historical research:** the session 9 Library file was retrieved. The original complete 100-rule catalog was not found in the available Library results and is not reconstructed here.
