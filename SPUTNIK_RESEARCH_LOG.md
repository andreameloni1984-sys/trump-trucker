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


## 2026-10-27 — Add conditional WTI/Brent hypothesis for Iran diplomatic de-escalation

- **User goal:** Telegram should turn relevant public news into one concise instrument/direction hypothesis rather than only listing headlines.
- **Change:** add a narrow, explicit-language catalyst rule for an Iran agreement/deal/ceasefire, diplomatic breakthrough, de-escalation, or easing/lifting of Iran sanctions. It maps to WTI/Brent SHORT_BIAS only; it does not fabricate entry, stop, or target prices.
- **Test:** add regression coverage that a dated individual news item with explicit Iran agreement language produces WTI/Brent SHORT_BIAS candidates, still marked `BIAS_ONLY_NEEDS_PRICE_VOLUME_CONFIRMATION`.
- **Limits:** this is a conditional news-bias rule, not proof of predictive value. The supplied 16-item digest does not itself contain a verified Iran-de-escalation event, and this change does not send a Telegram message or add live quote/ATR calculations. Those require current market data and a connected runtime.
- **Deployment:** branch-only change; not merged or deployed. PAPER ONLY; no orders.


## 2026-10-27 — Abstain on negated Iran de-escalation language

- **Finding:** the conditional WTI/Brent SHORT_BIAS rule matched keyword overlap such as “Iran deal not reached” or “Iran rejects ceasefire”, even though the stated event was a failed/rejected agreement rather than de-escalation.
- **Change:** \`sputnik_catalyst.py\` now checks a narrow set of explicit negation/rejection patterns before applying only the \`iran_diplomatic_deescalation\` rule. Other catalyst rules are unchanged; ambiguous/negated wording abstains.
- **Regression:** \`tests/test_sputnik_item_intelligence.py::test_negated_iran_diplomacy_does_not_create_oil_short_hypothesis\` covers failed deal, rejected ceasefire, and sanctions remaining in place.
- **CI status at this check:** GitHub's PR-run endpoint returned no new workflow run for the updated test commit `6469d487ecf81b4ef2db3937d0252d537c1d6778`. Earlier successful Sputnik runs predate this negation guard and are not counted as validation. A fresh CI result is not claimed unless a run for this change becomes observable.
- **Deployment:** PR #54 branch only; no merge or deploy. Render build-pipeline minutes are exhausted.
- **Empirical limit:** this is a keyword-negation safety guard, not NLP fact verification or a predictive edge. No live-feed replay or price/volume study.
- **Safety:** PAPER/DEMO ONLY; no broker, orders, secrets, or Telegram test messages.

## 2026-10-27 — Abstain on explicitly negated directional catalyst phrases

- **Finding:** the headline rule set could interpret a negated phrase such as “no production cut” or “trade deal rejected” as if the catalyst had occurred, producing the opposite directional hypothesis. The existing negation guard covered only the Iran de-escalation rule.
- **Change:** `sputnik_catalyst.py` now checks local sentence context around a matched catalyst for explicit negation/rejection before emitting any rule-based bias. The guard is intentionally conservative; it is not full natural-language understanding.
- **Regression:** `tests/test_sputnik_item_intelligence.py` covers negated oil-supply and trade-deal examples plus positive controls. The misplaced `unittest.main()` block was moved to the end so later test methods are discoverable when the module is run directly.
- **Operational path:** individual dated RSS item → domain/rule matching → negation gate → `BIAS_ONLY_NEEDS_PRICE_VOLUME_CONFIRMATION` candidate. This does not confirm price/volume or authorize entry.
- **Code commit:** `ed2c0aed45c0acef0ea1a4e17be6a18cf24186f5` (includes the corrected regex escaping after the initial code commit).
- **Test commit:** `aaa25c440c318f21ac0f98716dcee79ebeff4ad2`.
- **CI:** new branch-head workflow has not yet completed at time of this entry; do not treat prior PR checks as verification of this change.
- **Deployment:** no merge/deploy; Render build-pipeline minutes remain exhausted.
- **Empirical limit:** unit-level language guard only; no live-news replay or directional performance claim.
- **Safety:** PAPER ONLY; no broker, orders, or Telegram test messages.

## 2026-10-27 — Final verification of negated-catalyst guard

- **Code/test:** code commit `ed2c0aed45c0acef0ea1a4e17be6a18cf24186f5`; regression tests and test-discovery repair commit `aaa25c440c318f21ac0f98716dcee79ebeff4ad2`.
- **CI:** item-intelligence tests PASS on run [40541330990](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40541330990); Telegram-menu tests PASS on run [40541330956](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40541330956), against the current research-log branch head. The tests specifically cover negated supply/trade headlines and positive controls.
- **Main / PR:** current `main` SHA observed: `608e053a8b87c71fa4a272dd97f71295eab18471`. PR #54 remains open; the new guard is not merged.
- **Render:** service remains configured to deploy `main`; last successful deploy in the available deployment list is `9e5204bf7d9074dba27637013b7d98933a91e733` (2026-10-16). The newer attempt on `50851b0dc76f1b7ed0adaa872c47aa84793687f9` failed (2026-10-22). No new SEC/RSS matching log lines were returned for the queried 2026-10-26 to 2026-10-27 window, so current source delivery is not confirmed by that query.
- **Limits:** keyword-negation guard is not full natural-language understanding and is not a live-news or predictive-performance test. No merge/deploy, broker, order, or Telegram test message.

## 2026-10-27 — Main workflow and source-log inspection

- Current `main`: `608e053a8b87c71fa4a272dd97f71295eab18471` (14:41 UTC).
- Latest scheduled `SPUTNIK` workflow returned in the recent-run list: [40523401974](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40523401974), SUCCESS at 14:40 UTC on the previous SHA `6992555ee972276cbc36995747368d2198c988fd). No newer scheduled run on current `main` was present in the returned top 10.
- PR #54 item-intelligence and Telegram-menu checks passed on the updated branch; this is separate from the main workflow.
- Render deployment history still identifies `9e5204bf7d9074dba27637013b7d98933a91e733` as the latest successful live commit and `50851b0dc76f1b7ed0adaa872c47aa84793687f9` as a failed later attempt. No deploy was triggered.
- The current 2026-10-26/27 log query returned no SEC/RSS matches. This absence does not establish feed health or failure; current source delivery remains unconfirmed.



## 2026-10-27 — Directional candidate point-in-time guard

- **Finding:** `directional_news_candidates()` required a non-empty publication string but did not independently reject naive ISO timestamps or future-dated publication times. When `available_at` was supplied by the Sputnik→Gagarin handoff, it was not validated at the directional-candidate boundary.
- **Change:** `sputnik_catalyst.py` now parses timezone-aware ISO-8601 and RFC-822 timestamps, rejects naive/malformed/future publication times, and validates an optional `available_at` as timezone-aware, not earlier than publication and not in the future. Legacy findings without `available_at` remain accepted for compatibility, but are less auditable.
- **Regression:** `tests/test_sputnik_item_intelligence.py::test_directional_news_candidates_rejects_naive_future_and_invalid_availability_times` covers valid ISO, valid RFC-822, naive/future publication, naive/future availability, and availability preceding publication.
- **Commits:** code `a720dadf814dd58677654ea8e7cbf6d394a2fa2d`; tests `e1da8f15a84b6b485bfcb5e53c09b0c4e2876768`.
- **CI:** PASS on latest branch head `829abc73c4b4438e66991bff8355517906352522`: item intelligence [40549168654](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40549168654) and Telegram menu [40549168761](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40549168761).
- **Operational path:** item-level RSS findings → `directional_news_candidates` → bias-only hypothesis. This does not create a trade entry; price/volume confirmation remains separate.
- **Empirical limit:** no live-feed replay or OOS market test. This is a causal timestamp/input-quality guard, not evidence of predictive edge.
- **Deployment:** PR #54 branch only; no merge/deploy. PAPER/DEMO only; no broker, real orders, secrets, or Telegram test messages.


## 2026-10-27 — Abstain on conflicting catalyst directions
- **Finding:** `directional_news_candidates()` assigned into a dictionary keyed by event/instrument, so if one item matched two rules with opposite biases, the later rule silently overwrote the earlier one. Example: “production cut announced, but supply restored” could produce a direction determined by rule order rather than the mixed evidence.
- **Change:** track event/instrument pairs with conflicting biases; remove the candidate and abstain for that pair. Same-direction duplicate rule matches remain a single hypothesis.
- **Operational path:** individual RSS item → temporal/evidence gates → rule matching → conflict gate → `BIAS_ONLY_NEEDS_PRICE_VOLUME_CONFIRMATION` candidates. No price entry is created.
- **Files:** `sputnik_catalyst.py`; regression test `tests/test_sputnik_item_intelligence.py::test_directional_news_candidates_abstains_when_energy_rules_conflict`.
- **CI:** pending for this latest change at log creation.
- **Deployment:** PR #54 branch only; no merge/deploy. Last Render live commit still needs a fresh deployment check before any live-state claim.
- **Empirical limits:** deterministic regression only; no historical headline replay or out-of-sample market validation. Keyword rules remain limited NLP. PAPER/DEMO ONLY.


## Recovered historical records — 2026-10-27
- **2026-10-03 — architecture proposal:** event clustering, deduplication, source weighting and evidence confidence; Sputnik remains public intelligence and Gagarin remains the separate market/trading engine. This is a historical design note, not proof that all stages were wired end-to-end.
- **2026-10-03 — TextExtractor regex finding:** historical conversation records the suspected whitespace-regex bug in re.sub(r"\\s+", ...), but the repository write was blocked at that time. It was not treated as fixed by this entry.
- **2026-10-05 — transaction registry:** historical work recorded ACQUISTATO/VENDUTO rows with title, quantity, price, effective transaction date, subject, SEC form and original SEC document; Form 144 was explicitly not treated as an executed sale.
- **2026-10-06 — ranking rubric:** historical conversation records a 0–100 Form 4 ranking, with one filing unable to reach COMPRA and at least three distinct filings plus score >=75 required. Exact weights are recorded in PR #53 with a caveat: the historical accepted specification is not an empirical calibration, and current main still needs reconciliation.
- **Session 9, 2026-10-20 — source-grounded research priorities:** preserve publication/availability/decision times; study chokepoints and freight against a price/volatility baseline; separate macro channels; keep controversial theses as opinions until reproducible evidence exists. Source: Library file “Registro Studio IBKR - aggiornato 2026-10-20 sessione 9.md”.
- **Current code mapping:** mixed-catalyst abstention is implemented only on PR #54 in sputnik_catalyst.py, tested in tests/test_sputnik_item_intelligence.py, and passed item-intelligence run 40559759406 plus Telegram-menu run 40559759468 on the tested branch head. No merge/deploy and no historical market replay.


## 2026-10-27 — Normalize publication timestamps before candidate sorting
- **Finding:** `directional_news_candidates()` sorted the original timestamp strings, so mixed timezone offsets / ISO and RFC-822 formats could appear in the wrong chronological order.
- **Code/test commit:** `6de670aa632ca152be3b1807abedeac41f8d084a` updates `sputnik_catalyst.py` and `tests/test_sputnik_item_intelligence.py`.
- **Change:** emit canonical UTC `published_at_utc`; preserve `available_at_utc` only when supplied; sort by normalized UTC. The original `published` text remains for source traceability.
- **Regression:** `test_directional_news_candidates_sort_by_normalized_utc_instant` verifies 10:00+02:00 sorts before 09:30Z and availability is normalized.
- **CI:** item intelligence PASS [40561147668](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40561147668); Telegram menu PASS [40561147750](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40561147750) on the code/test commit.
- **Historical mapping:** the Library session 9 record prioritizes publication time, first availability, primary source and fixed reaction horizons; this change addresses chronological timestamp consistency only. It does not fill missing availability timestamps or prove that news sentiment adds predictive value.
- **Operational path:** item-level RSS → timezone-aware parse / point-in-time validation → directional hypothesis → normalized ordering → digest/handoff. The status remains hypothesis-only until independent price/volume confirmation.
- **Deployment/empirical limit:** PR #54 branch only; no merge/deploy. Synthetic regression only; no historical feed replay or OOS market-return validation. PAPER only.


## Follow-up correction — compare parsed UTC instants, including fractional seconds
- **Finding:** the first UTC-ordering change used canonical ISO strings as the sort key. ISO strings with variable fractional-second precision are not always lexically ordered chronologically (for example, `09:30:00Z` versus `09:30:00.500Z`).
- **Correction:** sort by the parsed timezone-aware UTC datetime, while retaining canonical `published_at_utc` and optional `available_at_utc` output fields.
- **Regression:** `test_directional_news_candidates_sort_fractional_seconds_chronologically` covers the fractional-second edge case.
- **Commit:** `a66b913b1e2e13798b3d7766b2f617568aa90857`.
- **CI PASS on corrected code/test head:** item intelligence [40561374887](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40561374887); Telegram/menu tests [40561375377](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40561375377).
- **Limit/deployment:** no historical RSS replay or market-return validation; PR #54 branch only, no merge/deploy. This is timestamp-order correctness, not a trading edge.

## 2026-10-27 follow-up — scope negation to semicolon-delimited clauses

- **Finding:** the rule-negation guard bounded context at periods, exclamation marks and question marks, but not semicolons. An unrelated earlier clause such as “No new tariffs planned; rate hike announced” could therefore suppress a separate, explicitly stated macro catalyst.
- **Change:** `_NEGATION_BEFORE_MATCH` now stops at semicolons, and `_is_explicitly_negated_rule_match()` uses semicolons as left/right clause boundaries. Conflicting directional catalysts still abstain; this change only prevents unrelated negation from leaking across clauses.
- **Files:** `sputnik_catalyst.py`; `tests/test_sputnik_item_intelligence.py`.
- **Regression:** `test_negation_does_not_leak_across_semicolon_clauses` checks that a negated tariff clause does not suppress the independent rate-hike hypothesis.
- **Commits:** code `5a44e47376c6eef4fa159b7d6978c29393d06068`; test `d8f16c162ab7703423fd4a29779ba934ea6882dc`.
- **CI:** item intelligence PASS [40566862821](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40566862821); Telegram menu PASS [40566862738](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40566862738).
- **Operational path:** item-level public RSS → dated/source validation → clause-scoped negation guard → hypothesis-only catalyst → separate price/volume confirmation. No entry/SL/TP is created by this change.
- **Deployment/empirical limits:** PR #54 branch only; no merge/deploy. Synthetic regression only; no historical headline replay, OOS return test, or profitability claim. PAPER ONLY.

## 2026-10-27 — Require explicit point-in-time availability for directional news

- **Finding:** RSS item records carried a publication timestamp, but newly ingested items did not persist a distinct first-observed time. `directional_news_candidates()` tolerated missing `available_at`, so a legacy record could be promoted to a directional hypothesis without evidence of when Sputnik first had it.
- **Change:** `trump_tracker.py::intelligence_snapshot` now records canonical UTC `event_time` from the timezone-aware feed publication timestamp and `available_at` from the first-observed ingestion time. `sputnik_catalyst.py::directional_news_candidates` now requires an explicit, valid `available_at` not earlier than event time and not later than its captured `decision_time`; it emits `event_time_utc`, `available_at_utc`, and `decision_time_utc`. Legacy records lacking availability time abstain instead of guessing.
- **Regression:** `tests/test_sputnik_item_intelligence.py` verifies RSS ingestion timestamps, missing-availability abstention, and `available_at <= decision_time`; existing chronology, negation and contradiction tests remain in place.
- **Operational path:** RSS/Atom item → permalink/date validation → first-observed timestamp → dedup/state persistence → directional hypothesis (still `BIAS_ONLY_NEEDS_PRICE_VOLUME_CONFIRMATION`). This does not generate an entry or infer price/volume confirmation.
- **Commits:** source tracker 9fb84ed5d6320a16d76d9719f72af8a1e7fa1a0c; catalyst 30b3fce4edc6e3133296f2a960b661535f58d4e2; regression tests 92ca61dc8e4dfe49169646900178c90a6499021f.
- **CI:** pending for the latest test commit at the time this note was written; do not treat as verified until branch workflows finish.
- **Deployment:** PR #54 branch only; no merge/deploy. Render workspace/runtime logs are not available through this run's connected tools, so live feed delivery is unconfirmed.
- **Empirical limit:** unit tests only; no historical feed replay, WTI/Brent OHLCV alignment, cost/slippage test or OOS performance result. PAPER/DEMO only; no broker or orders.
