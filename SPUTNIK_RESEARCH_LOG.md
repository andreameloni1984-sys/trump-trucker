## 2026-10-27 15:24 UTC — CLZ26 hypothesis audit and explicit execution-cost components

### Previously formulated WTI hypothesis — outcome check
- **Hypothesis timestamp recovered from prior conversation:** 2026-10-27 14:16:51 UTC. Instrument: NYMEX WTI December 2026 futures (CLZ26); conditional SHORT only after a break below $100.50; reference near $101.45; hypothetical trigger/entry reference $100.45; stop $101.55; TP1 $98.25; TP2 $97.15. No order was placed.
- **Public quote snapshots inspected:** Oilprice.com displayed CLZ26 $100.24 with session range $100.05–$102.82 and row time “10:10” (timezone not stated on the table); its page header described WTI data as about 11 minutes old at retrieval. Farmbucks displayed $101.71 and a $100.52–$102.82 day range at 2026-10-27 09:07 UTC-5 (14:07 UTC), marked “Delayed 10 min” and “Updated 20 min ago”. The Farmbucks timestamp precedes the hypothesis, while Oilprice's time-zone basis and the timestamp of its session low/high are not supplied.
- **Classification: NON-VERIFIABLE due to missing reliable post-hypothesis intraday bars.** The Oilprice session low is below the $100.50 trigger, but its timestamp is unknown, so it cannot prove the trigger happened after 14:16:51 UTC. The published range crosses the $101.55 stop level, but the high's timestamp is also unknown. The displayed low remains above both targets, but no reliable timestamped post-hypothesis bar sequence was available to close the evaluation. No stop/TP result is inferred from daily extrema alone.
- **Sources:** https://oilprice.com/futures/wti/ ; https://farmbucks.com/futures/energy/wti-crude?contract=CLZ26 . Quotes are delayed/age-ambiguous; not suitable to certify the sequence after the hypothesis. No fabricated prices or times were used.

### One functional improvement — cost decomposition in the event backtest
- **Status before change:** PR #45 was open/unmerged/mergeable at head `68a20178ec9f82c74549cd1fd94d9d6c8d45e831`; current-head ranking-test workflow [40526742393](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40526742393) had completed successfully.
- **Finding:** the simulator deducted a single round-trip cost in price units, but could not separately represent per-contract commission and per-side slippage. This makes it harder to stress-test early-entry vs breakout under transparent futures execution assumptions.
- **Implemented in `sputnik_event_backtest.py`:** added `commission_round_trip_usd_per_contract`, `slippage_ticks_per_side`, `tick_size`, and `contract_multiplier` to single-event, batch and CLI paths. The effective cost deducted from gross P&L is `spread + commission_usd_per_contract / contract_multiplier + 2 * slippage_ticks_per_side * tick_size`. Results now expose gross P&L, net P&L and the effective round-trip cost in price units; settings preserve every input.
- **CL defaults/documentation:** tick size defaults to $0.01 per barrel and multiplier to 1,000 barrels per contract, matching the published CL contract specifications. Commission and slippage default to zero for backward compatibility; a real study must supply defensible values. The costs are deducted from P&L rather than used to reconstruct individual market fills, so stop/target path sensitivity to slippage remains a limitation.
- **Regression tests:** added `test_execution_cost_model_deducts_commission_and_two_sided_slippage` and `test_execution_cost_model_rejects_invalid_cost_inputs`. The deterministic synthetic example verifies $0.02 spread + $10/1,000-barrel commission + two $0.01 ticks = $0.05 per barrel of round-trip costs; these are test values, not observed market data.
- **Commits:** implementation `4e74ef52898ac4041cbcdd8536860bddd25eadfb`; tests `2532ced317bfab202b83b1dc90c30aec5fa2273f`.
- **CI verification:** workflow [40530382388](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40530382388) completed successfully on the code/test revision; the job log confirms `python -m unittest discover -s tests -p "test_*.py" -v`, **118 tests ran, OK**. No local-run claim is made.
- **Data/performance blocker:** still no exchange-verified, timestamped CL OHLCV sequence paired with a source-linked event ledger and system-availability times. No real-event backtest or early-entry profitability claim.
- **Safety/deployment:** PR branch only; no orders, broker changes, Telegram test messages, or production deployment.

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


## 2026-10-27 — Add a conditional WTI hypothesis for verified diplomatic de-escalation

- **Observed need:** Sputnik could map attacks and physical supply threats to a conditional Brent LONG watch, but had no explicit opposing scenario for credible diplomatic progress that reduces the geopolitical risk premium. That left the recent mixed oil-news pattern under-expressed.
- **Implemented on branch `feat/oil-deescalation-watch-20261027`:** added `oil_diplomatic_deescalation` to `sputnik_decision.py`, with WTI as the candidate and SHORT as a conditional hypothesis only after credible diplomatic evidence and an intraday low break with selling volume. Added a strict evidence rule in `sputnik_decision_engine.py` so generic mentions of diplomacy do not qualify.
- **Tests added:** explicit de-escalation wording maps to conditional WTI SHORT watch; generic diplomacy mention does not.
- **Risk controls:** new attacks/physical supply interruptions invalidate the scenario; no entry, stop, target, or position size is fabricated without fresh quote/ATR data. This does not place orders.
- **Verification status:** code and regression tests committed to the feature branch. Test suite and CI have not been run in this environment; do not describe this as production-deployed or live in Telegram until CI passes, the change is reviewed/merged, and deployment is confirmed.


## 2026-10-27 — Suppress campaign-endorsement noise in market interpretation

- **Observed input:** two TRUTH_ARCHIVE items praised/endorsed congressional candidates. Their broad topic tags included ENERGY/DEFENSE/AI_TECH, but the supplied text contained no specific policy change, contract, supply disruption, or economic catalyst.
- **Implemented on `feat/oil-deescalation-watch-20261027`:** `sputnik_decision_engine.py` now recognizes explicit standalone endorsement/campaign phrasing when no strict market catalyst was found and returns a clear no-market-catalyst result instead of a generic sector watchlist. It instructs the pipeline to archive without a trading alert unless concrete policy/economic evidence exists.
- **Regression test:** added a test asserting an endorsement does not create LONG/SHORT conditional plans.
- **Limits/status:** test added but not executed in this environment. The feature branch and PR #45 are not production deployment; Telegram behavior changes only after review/merge/deploy and verification.


## 2026-10-27 — Flexible early-entry mode instead of mandatory breakout

- **User feedback:** requiring a fully confirmed technical breakout can make a useful news-driven signal arrive too late.
- **Implemented on `feat/oil-deescalation-watch-20261027`:** the decision message now explicitly supports an exploratory early entry when the catalyst is credible, with reduced exposure (about one-third of normal size), a predefined stop, and optional scaling only if confirmation follows. A breakout raises confidence but is not a universal prerequisite. The WTI diplomatic-de-escalation scenario now permits an exploratory SHORT before the intraday-low break instead of forbidding anticipation.
- **Regression test:** added a test for the flexible-mode wording and reduced-size guidance.
- **Risk boundary:** this is an early hypothesis, not certainty. Never invent entry/SL/TP values without a fresh quote and volatility measure; invalidation and physical supply risks still apply. PAPER ONLY; no orders sent.
- **Verification/deployment:** test added but not run here. Feature branch / PR #45 is not confirmed live in Telegram; deployment remains unverified.


## 2026-10-27 — Add a reproducible early-entry vs breakout event backtest

- **Purpose:** test the user's concern that waiting for a technical breakout may make Sputnik late, without assuming that early entries are automatically better.
- **Implemented:** added `sputnik_event_backtest.py`, a command-line harness that reads timezone-aware OHLCV CSV data and compares an exploratory entry at the first bar after a catalyst timestamp with a delayed close-confirmed breakout entry. It records entry, stop, target, exit, outcome and R-multiple; a candle touching stop and target in the same bar is treated conservatively as stop-first. Spread/cost input is supported.
- **Tests added:** early SHORT entry and target, no-breakout case, no future candle, invalid direction, and conservative ambiguous-candle handling. Updated an existing test to check that volume remains in the confirmation rule rather than requiring it in the entry trigger.
- **CI:** expanded `.github/workflows/sputnik_tests.yml` pull-request path filters so the new harness and tests run with the existing suite. Awaiting GitHub Actions results after the latest commit.
- **How to run:** `python -m unittest tests/test_sputnik_event_backtest.py -v`; with market data: `python sputnik_event_backtest.py --csv candles.csv --event-time 2026-10-27T08:30:00+00:00 --side SHORT --atr 0.45 --atr-time 2026-10-27T08:25:00+00:00 --spread 0.02`.
- **Limitations:** no market data is bundled, so this does not yet establish profitability. Use historical WTI bars and actual catalyst publication timestamps, include realistic costs, and evaluate many events before drawing conclusions. PAPER ONLY; no orders, Telegram test messages, or deployment performed.

## 2026-10-27 — Remove same-close fill bias from the breakout comparator

- **Finding:** the first event-backtest version detected a breakout using a candle's close, then also filled the delayed strategy at that same close. Because the breakout is only known after the candle closes, this assumes an unrealistically precise fill and can bias the early-vs-breakout comparison. The simulator also skipped stop/target checks on the entry candle.
- **Implemented on `feat/oil-deescalation-watch-20261027`:** breakout detection still uses the completed candle close, but the simulated delayed entry now occurs at the following candle's open. The signal timestamp and signal close are reported separately from the actual entry timestamp/price. The simulator now checks the entry candle's range and counts it as the first holding bar; stop wins when OHLC data cannot determine which of stop/target was hit first.
- **Regression coverage:** changed the fixture so the following open differs from the breakout close; assert signal time, next-bar entry time, and entry price; added a test for stop/target ambiguity on the entry bar.
- **CI diagnosis:** the preceding GitHub Actions run for head `452dbd5fdd9e7d69aab366adf780ffe5205d8847` ran 87 tests and failed one assertion because the test searched for English `volume` while the Italian confirmation says `volumi`. The assertion now checks the common stem `volum`. GitHub Actions run `40446808772` completed successfully on code head `5e3ad63fcd6cf8cfb6e61b9785d51ec7323d27e9`: 88 tests ran, `OK`.
- **Verification limits:** no local repository checkout was possible in this environment (GitHub clone DNS resolution failed); use the new GitHub Actions run as the authoritative test execution. No WTI market data or independently verified event-timestamp dataset has yet been added, so no strategy performance conclusion is claimed. PAPER ONLY; no orders, broker changes, Telegram test messages, or deployment.
- **Historical-data research lead:** the public GitHub sample [getdata-finance/usoil-5m-ohlcv-commodities-historical-data](https://github.com/getdata-finance/usoil-5m-ohlcv-commodities-historical-data) documents 35,882 five-minute bars from 2026-03-26 through 2026-09-25, with UTC bar-start timestamps and OHLC fields. Its `volume` is explicitly tick volume and the symbol is labelled USOIL, so source provenance/instrument equivalence to NYMEX CL futures is not established. Treat it only as a candidate for parser/pipeline validation until provenance is independently checked; do not present it as exchange-traded CL volume.
- **News-time research lead:** The American Presidency Project's dated Truth Social archives publish post times in PT/ET and link to individual original Truth Social posts (example archive: https://www.presidency.ucsb.edu/documents/truth-social-posts-september-4-2026). A backtest event ledger should retain both the archive citation and original permalink, normalize the displayed timezone explicitly, and reject rows whose publication time cannot be reconciled. No paired event/price dataset has yet been assembled or tested.


## 2026-10-27 — Reject ambiguous candle timestamps in the event backtest

- **Status before this change:** PR #45 was open and unmerged. The current head `7c4ed1b14bc44c7ee0aec1bb3f4176c99b7a09af` had a successful GitHub Actions run (#172); that result applies to the prior code, not this new change.
- **Finding:** the backtest sorted candles but accepted duplicate timestamps and timezone-naive candle datetimes when called directly. Duplicate bars can be counted twice in breakout lookback/holding periods; naive timestamps cannot be safely aligned with the timezone-aware catalyst time.
- **Implemented on `feat/oil-deescalation-watch-20261027`:** a shared candle-timestamp validator now rejects duplicate instants and timestamps without an explicit timezone both when loading CSV and when calling `backtest_event()` directly. The input is rejected rather than silently guessed or deduplicated.
- **Regression tests added:** duplicate timestamps raise a clear `ValueError`; naive candle timestamps raise a clear `ValueError`.
- **Verification:** GitHub Actions run [40450927338](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40450927338) completed successfully on code commit `5eff38d7c45468726e4b632359b77662bd69cceb`. The workflow ran `python -m unittest discover -s tests -p "test_*.py" -v`; the check/job concluded `success`. The check summary did not expose an exact test count. This is the first CI result counted for the timestamp-validation change; no local test run is claimed.
- **Data lead investigated this run:** FirstRate Data's [NYMEX CL intraday page](https://firstratedata.com/i/futures/CL) lists 1-minute through daily bars and a public `Download Sample` ZIP; the page states coverage through 2026-10-23 and describes its source as major exchanges. The binary ZIP could not be retrieved by the available fetch/download tools, so its contents, timestamps, license terms, and schema have not been inspected. Treat it as a lead, not yet as validated input. Full-history intraday data appears to be sold, so no purchase was made.
- **Event-time lead:** the [American Presidency Project social-media archive](https://www.presidency.ucsb.edu/documents/app-categories/social-media?field_docs_start_date_time_value%5Bvalue%5D%5Bdate%5D=2026&items_per_page=60) indexes dated Truth Social entries. The ledger still needs to capture each post's original permalink, displayed timezone and normalized UTC publication time; no paired event/candle dataset has been assembled.
- **Data/performance status:** no verified WTI OHLCV + source-linked event-time dataset has been assembled, so no comparative performance result is claimed. The previously documented USOIL sample remains tick-volume data with unverified equivalence to NYMEX CL. PAPER ONLY; no broker changes, orders, Telegram test messages, or production deployment.


## 2026-10-27 — Model gap-through stop fills conservatively

- **Status before change:** PR #45 was open/unmerged and mergeable. GitHub Actions run [40451055995](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40451055995) passed on prior head `dbe051073a8571ec3575ea90c14cc8ee2a4e1a75`; that result predates the gap-handling change below.
- **Finding:** the OHLC simulator checked each candle's high/low against stop and target but ignored the next candle's opening gap. A stop-market exit could therefore be recorded at the stop price even when the market opened beyond it, understating adverse execution and potentially overstating the early-entry strategy.
- **Implemented on `feat/oil-deescalation-watch-20261027`:** for candles after entry, if the open gaps through a stop, the simulator exits at the worse opening price (`STOP_GAP`). If the open gaps through a target, it conservatively records the target price (`TARGET_GAP`) rather than assuming price improvement. Existing same-bar stop-first handling remains unchanged.
- **Regression tests added:** a SHORT stop gap must exit at the worse open and show a loss greater than 1R; a LONG target gap must not assume a fill better than the target.
- **Verification status:** code commit `68480a79d6c6abc739eccb46d92d5d115f2f2fea`; test commit `ada4ab72b6b673ecd66d49921cd5917b15669632`. The latest successful Actions run above is for the previous head; CI for these new commits must be checked separately. No local execution is claimed.
- **Data/performance status:** no verified WTI OHLCV + source-linked event-time dataset has been assembled, so no real-event comparison or profitability conclusion is claimed. Gap handling improves execution realism but does not model order-book liquidity, slippage beyond the observed open, commissions, or futures contract rolls. PAPER ONLY; no broker changes, orders, Telegram test messages, or production deployment.

- **Follow-up CI result (2026-10-27):** GitHub Actions run [40459502930](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40459502930) completed successfully on code commit `ada4ab72b6b673ecd66d49921cd5917b15669632`. The workflow ran `python -m unittest discover -s tests -p "test_*.py" -v`: **92 tests ran, OK**. The log contains some expected network-source `OSError` messages in offline/mock tests; the test command still exited successfully. The subsequent PR-head commit `c17cdc603f270cfd5ec7c2e85762520534d782c6` only appends research documentation; no code changed after the passing test commit.


## 2026-10-27 — Require causal timestamp for the ATR input

- **Status before change:** PR #45 was open, unmerged and mergeable. The latest verified Actions run at the start of this iteration was [40459550664](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40459550664), successful on the then-current head; it predates this code change.
- **Finding:** the event backtest accepted a caller-supplied ATR value but could not tell whether that value had been computed from data available after the catalyst. A future-derived ATR can leak information into stop/target distances even when entry timing itself is causal.
- **Implemented:** `backtest_event()` now requires an explicit timezone-aware `atr_time` timestamp and rejects it if it is later than the catalyst publication time. The CLI requires `--atr-time`; output settings preserve the declared ATR availability timestamp for audit. This checks the declared availability time, not the ATR value's underlying provenance, which must still be audited from the source data.
- **Regression test:** all existing synthetic tests now supply a pre-event ATR timestamp; added a test proving that an ATR timestamp after the event raises a clear `ValueError`.
- **Commits:** code `cc230b626f2a1024c7cf7df0cda55b17524d47f8`; regression tests `c81ad78952816d50a125ba8252e653add5b0ebc7`.
- **CI feedback and correction:** first run [40461331569](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40461331569) ran 93 tests and failed 3 event-backtest tests because three direct test calls omitted the newly required `atr_time`. Those fixtures were corrected in test commit `b69804d0161f90b4fc03f1f019cf684a74a8f594`. The subsequent run [40461398846](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40461398846) checked the PR merge commit containing that correction, ran **93 tests, and passed (`OK`)**. This is the authoritative verification for the ATR guard and updated fixtures; no local test execution is claimed.
- **Data/performance status:** no verified WTI OHLCV plus source-linked news-time dataset is available in the branch, so no real-event strategy comparison or profitability claim is made. PAPER ONLY; no orders, broker changes, Telegram test messages, or deployment.


## 2026-10-27 — Reject non-finite and invalid OHLCV inputs

- **Status before change:** PR #45 was open, unmerged and mergeable. Latest verified PR workflow run [40461445259](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40461445259) completed successfully on head `b372f5f800f70254a5e4a9e796011ef3c9495357` (93 tests, as recorded in the prior section). This run predates the change below.
- **Finding:** Python float parsing accepts `NaN` and infinities. Comparisons against NaN are false, so malformed OHLCV CSV rows could bypass the existing high/low consistency checks and silently contaminate simulated fills/P&L. Negative volume is also not a valid bar input.
- **Implemented on `feat/oil-deescalation-watch-20261027`:** added shared OHLCV validation for both CSV loading and direct `backtest_event()` calls. All OHLCV values must be finite; volume must be non-negative; high/low must be consistent with open/close/low/high. Negative WTI prices are not prohibited because historical futures data can include negative prices.
- **Regression tests added:** a CSV row with `NaN` volume must be rejected; a direct backtest input with negative volume must be rejected.
- **Commits:** code `d6f6e8afab7d4280832125970a2a0f84ba311803`; tests `803b6844848d2ff5db530d09fa91bac8527afea3`.
- **Verification status at log entry:** CI for these new commits is pending; no local test execution is claimed. Record the actual GitHub Actions outcome below once observed.
- **Data/performance status:** no verified WTI OHLCV + source-linked news-time dataset has been assembled. This data-integrity guard improves input quality but does not establish whether early entry outperforms breakout. No orders, broker changes, Telegram test messages, or deployment.


- **Follow-up CI result (2026-10-27):** the first run with the new regression tests failed because the CSV fixture contained literal backslash-n characters instead of line breaks; this was a test-fixture defect, not a production-data result. Corrected the fixture in test commit `d084b73da2211257c54ebaca8be2caed7156ca45`. GitHub Actions run [40471614339](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40471614339) completed successfully on that commit; the `Run ranking tests` step passed. The connector's run summary did not expose an exact test count, so none is claimed. The code commit's separate earlier run [40471511861](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40471511861) also passed, but did not yet include the two new tests.


- **Additional public-data lead (2026-10-27):** found the public [getdata-finance USOIL 5-minute sample](https://github.com/getdata-finance/usoil-5m-ohlcv-commodities-historical-data), whose README states 35,882 bars from 2026-03-26 through 2026-09-25, ISO timestamps with UTC offsets, and an MIT license. The sample schema matches `datetime,open,high,low,close,volume`, making it a candidate for a pilot parser/backtest. The repository labels the instrument USOIL; it is **not verified as NYMEX CL futures**, and the meaning/provenance of its volume is not independently verified. Attempting to retrieve the full CSV through the available GitHub file connector returned empty content, and direct download was unavailable in this run. Therefore no rows were imported, validated locally, or used for a performance calculation. This is a lead, not a validated dataset.



## 2026-10-27 — Preserve negative WTI prices in event simulation

- **Status before change:** PR #45 was open/unmerged. The then-current head `4c8d2a1950c0d81d14ccc3ac7625769f5e3f96b7` had a successful GitHub Actions run [40471816412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40471816412); that run predates this change.
- **Finding:** the shared OHLCV validator intentionally permits negative prices (relevant to historical WTI futures), but `_simulate()` rejected every entry price `<= 0` as `INVALID_INPUT`. This contradicted the validator's policy and would silently exclude negative-price historical bars from performance evaluation.
- **Implemented on `feat/oil-deescalation-watch-20261027`:** `_simulate()` now requires a finite entry and finite positive risk distance, but no longer assumes that the entry price must be positive.
- **Regression test added:** a synthetic SHORT event at -5.0 with ATR 1.0 checks stop -4.0, target -7.0 and a target exit at 2R. These are synthetic values only, not observed market data.
- **Verification status:** code commit `9d82d5b72f1075767fe7fb82605c1b7d13b8fd34`; test commit `69aea0c3dad1d7e1fe42352ca3633b06753eecb1`. GitHub Actions run [40479389788](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40479389788) was observed in progress; its final result must be recorded after completion. No local test run is claimed.
- **Data/performance status:** this fix only makes the simulator compatible with negative price bars; it does not validate any source dataset. No source-linked WTI OHLCV plus news-time ledger has been assembled, and no real-event performance result is claimed. PAPER ONLY; no broker changes, orders, Telegram test messages, or deployment.


- **Follow-up CI result (2026-10-27):** GitHub Actions run [40479389788](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40479389788) completed successfully on test commit `69aea0c3dad1d7e1fe42352ca3633b06753eecb1`. The workflow ran `python -m unittest discover -s tests -p "test_*.py" -v`: **96 tests ran in 0.038s, OK**. The log includes expected mocked/offline source `OSError` messages; the test command exited successfully. The subsequent commit `4ca69bf87abf9cc27b23658ca13f88400d781863` only appends this research record; no code changed after the passing test commit.


## 2026-10-27 — Inspect public USOIL M5 sample and test event-time provenance

- **Data retrieval succeeded this time:** fetched the public `USOIL_5m.csv` text through the GitHub Contents endpoint from [getdata-finance/USOIL 5-minute sample](https://github.com/getdata-finance/usoil-5m-ohlcv-commodities-historical-data/blob/main/USOIL_5m.csv). The repository metadata reports file size 2,301,232 bytes; the CSV was inspected in memory only and was not committed into this repository.
- **Observed dataset:** 35,882 data rows, columns `datetime,open,high,low,close,volume`, from `2026-03-26T02:30:00+00:00` through `2026-09-25T20:40:00+00:00`. Prices range from 67.029 to 117.604 in this sample.
- **Validation performed in-memory:** 0 malformed rows; 0 missing/invalid or timezone-naive timestamps; 0 duplicate instants; 0 non-finite OHLCV values; 0 negative volumes; 0 invalid OHLC geometries; 0 out-of-order rows. There are 135 intervals longer than five minutes, with a maximum observed gap of 4,385 minutes. These gaps must be treated as session/data gaps, not silently interpreted as continuous tradable time.
- **Important instrument caveat:** this is labeled `USOIL`, not exchange-identified NYMEX `CL`. The feed/vendor provenance and whether `volume` represents traded futures volume or a tick/CFD proxy remain unverified. The sample is now validated as a structurally clean *candidate input*, not as authoritative CL futures data.
- **Event timestamp check:** the American Presidency Project's April 7, 2026 Iran ceasefire statement links to original Truth Social post `116365796713313030` ([archive record](https://www.presidency.ucsb.edu/documents/statement-united-states-military-operations-iran-0); [original post](https://truthsocial.com/@realDonaldTrump/posts/116365796713313030)). The archive supplies the date and permalink but does not expose a precise publication time in the accessible record; the original page is JavaScript-only to this connector. Therefore this event cannot yet be aligned causally to a 5-minute bar without guessing the event time.
- **Outcome:** no event backtest was run and no performance metric was calculated. Next data task is to obtain exchange-identified CL bars with documented volume/session/roll handling and exact publication timestamps for a set of events; retain source URL, source time zone, normalized UTC time, and confidence for each event. PAPER ONLY; no orders, broker changes, Telegram test messages, or deployment.


## 2026-10-27 — Reject invalid spread/cost inputs in event backtest

- **Status before change:** PR #45 was open, unmerged and mergeable. The prior head `7edba900ed2cdd1f210b87ba6046dca71c11e39b` had a successful GitHub Actions run [40479646861](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40479646861); that run predates this change.
- **Finding:** the backtest used `max(0.0, spread)`, silently converting a negative spread input into zero cost. NaN could also be silently treated as zero by that clamp, while an infinite value could contaminate the reported net R multiple. This can make a malformed cost configuration look more favorable than it is.
- **Implemented on `feat/oil-deescalation-watch-20261027`:** `backtest_event()` now rejects non-finite ATR, stop multiplier, target multiple or spread values and rejects negative spread costs. Since `spread` is defined as a round-trip cost in price units, the simulator now subtracts the validated cost directly instead of silently clamping it.
- **Regression tests added:** negative, NaN and infinite spread values must raise `ValueError`; a valid synthetic round-trip cost of 0.5 price units is deducted from a synthetic 2R target result, leaving 1.5R. These are deterministic fixtures, not market observations or performance estimates.
- **Commits:** implementation `3b216bee8cbe7b99bece97c04f00153d46888fe6`; tests `3d69075fffa7bf1759d123d1806be3eb572bbefd`.
- **Verification:** GitHub Actions run [40485651959](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40485651959) completed successfully on the test commit. The workflow executed `python -m unittest discover -s tests -p "test_*.py" -v`: **98 tests ran in 0.046s, OK**. This is CI verification; no local test run is claimed.
- **Data/performance status:** no exchange-verified NYMEX CL OHLCV plus exact, source-linked news timestamps has been assembled, so no real-event comparison or claim that early entry outperforms breakout is made. The public USOIL sample remains a structurally clean candidate with unverified equivalence to CL and unverified volume provenance. PAPER ONLY; no orders, broker changes, Telegram test messages or production deployment.


### Additional CL data-source check (2026-10-27)
- A fresh search found [FinzData's NYMEX CL futures page](https://finzdata.com/futures/cl): it advertises individual CL contracts and continuous series, intraday 1-minute/5-minute bars from 2007, bar-start timestamps in US Eastern time, and full intraday access for a stated one-time price of $39; only the last 30 days of daily bars are free. This is a potential exact-instrument source, but no data were downloaded and no purchase was made.
- [FirstRate Data's NYMEX CL page](https://firstratedata.com/i/futures/CL) lists 1-minute/5-minute intraday series from 2008 and says the files are exchange-sourced CSV ZIPs. Its public sample link resolved to `frd_sample_futures_CL.zip`, but the available web connector cannot inspect ZIP content and the container download attempt failed. Schema, sample values, timezone and license terms therefore remain unverified.
- These are source leads, not acquired/validated datasets. The next step is to obtain an inspectable licensed CL sample and build a separate event ledger whose catalyst timestamps are exact, timezone-aware and source-linked. No real-event backtest or profitability claim is made.


## 2026-10-27 — Reject out-of-order OHLCV rows instead of silently sorting

- **Status before change:** PR #45 was open, unmerged and mergeable. The latest CI run before this change, [40485775035](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40485775035), passed on prior head `68e22a06b144ef4750565a0d6abb23bcee4b3de1`.
- **Finding:** both `load_candles_csv()` and `backtest_event()` silently sorted candle timestamps. That made an out-of-order source file appear clean and could conceal data-pipeline problems; the prior in-memory dataset audit's “out-of-order rows: 0” result did not prove the parser would reject disorder.
- **Implemented on `feat/oil-deescalation-watch-20261027`:** timestamp validation now rejects any candle timestamp earlier than the previous input row. Removed implicit sorting from both CSV loading and direct backtest calls. Inputs must already be chronological; duplicate and timezone-naive timestamp checks remain.
- **Regression tests added:** an unsorted direct candle list must raise `ValueError`; an unsorted CSV must also raise `ValueError`.
- **Commits:** implementation `ce7dda8311107b173e6045d1427b1601903730ed`; tests `0b7591088fe6280a2c3b50dec061d064d17b31a2`; corrected test-fixture line endings `f390f8ff50ed8d87c5e6acb26be221e87e5dade0`.
- **CI feedback:** first run [40489813026](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40489813026) failed because the new CSV fixture encoded literal `\\n` text instead of line breaks. Fixed the fixture; follow-up run [40489845149](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40489845149) completed with conclusion **success** on `f390f8ff50ed8d87c5e6acb26be221e87e5dade0`; the `Run ranking tests` step passed. The available summary does not expose the exact test count, so none is claimed.
- **Data/performance status:** this is a data-integrity improvement only. No exchange-verified NYMEX CL dataset paired to exact source-linked catalyst timestamps has been assembled; no real-event comparison or profitability claim is made. PAPER ONLY; no broker changes, orders, Telegram test messages or production deployment.


### 2026-10-27 — Reject boolean parameters in event backtest
- **Finding:** Python treats `True` as numeric 1 and as an integer. The event backtest accepted boolean ATR/stop/target/spread inputs and boolean lookback/holding counts, which can silently change the simulated risk geometry.
- **Files:** `sputnik_event_backtest.py`; `tests/test_sputnik_event_backtest.py`.
- **Change:** require ATR, stop multiplier, target R and spread to be finite non-boolean int/float values; require lookback and holding-bar parameters to be positive non-boolean integers.
- **Regression:** `test_boolean_numeric_and_integer_parameters_are_rejected` covers all six parameter paths.
- **Commits:** code `5d63e2f722b780da8b8b596a67c8db2f41cd8167`; tests `8a2090dd17b321a5d8e7705bc7845cad9b43e38c`.
- **CI:** SPUTNIK ranking tests PASS on test commit `8a2090dd17b321a5d8e7705bc7845cad9b43e38c`.
- **Deployment:** PR #45 branch only; no merge/deploy. Render workspace selection is not available in this automation context; pipeline quota is known exhausted.
- **Empirical limit:** numeric input hygiene only. No verified NYMEX CL/event-time dataset, real-event replay or out-of-sample result.
- **Safety:** PAPER ONLY; no broker, orders, secrets or Telegram test messages.

## 2026-10-27 — Paired multi-event comparison with a source-linked event ledger

- **Status before change:** PR #45 was open, unmerged and mergeable at head 49954e3cdb47e71070f87926cf9b59c263cc1363. Its latest observed ranking-test run before this change was GitHub Actions run [40501429954](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40501429954), successful.
- **Finding:** sputnik_event_backtest.py could compare early entry and breakout for only one catalyst per invocation. That made it harder to assess whether one approach consistently outperforms across a sample, and made it easy to over-focus on an isolated event.
- **Implemented:** added load_events_csv() with required columns event_id,event_time,side,atr,atr_time,source_url. It rejects missing/duplicate IDs, non-HTTP(S) source links, timezone-naive event/ATR times, invalid direction/ATR, and ATR timestamps later than the event. Added backtest_events() and summarize_comparison_results() plus CLI --events-csv mode. The report calculates early and breakout mean R on the same paired scored events, mean/median paired difference (early minus breakout), counts where each strategy wins or ties, and separate counts of unscored statuses. Events without numeric P&L for both strategies are excluded from the paired averages and are never treated as zero.
- **Regression tests:** added test_event_ledger_requires_source_url_and_timezone_aware_times and test_batch_backtest_reports_paired_difference_and_unscored_statuses. The batch fixture is synthetic and tests accounting only; it is not market-performance evidence.
- **Commits:** implementation 5d0904e4f0d0635b541b4c671d46a751114b64b3; tests e7a9f14c560f4071fb44e7d84f9becac60e4f528.
- **CI verification:** GitHub Actions run [40502767174](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40502767174) completed successfully; job tests and step Run ranking tests both have conclusion success. The available summary does not expose the exact unittest count, so no count is claimed. This is CI verification; no local test run is claimed.
- **Limits / next step:** no verified exchange-identified NYMEX CL OHLCV file has yet been paired with a source-linked ledger of exact publication timestamps. source_url is traceability metadata, not independent verification of the linked statement or timestamp. No real-event batch backtest, performance conclusion, or out-of-sample result is claimed. Need acquire/validate CL bars and a dated event ledger, then run the paired study with defensible spread/slippage/commission assumptions and session/contract-roll handling.
- **Safety:** PR branch only; no merge or production deploy, no broker changes/orders, and no Telegram test messages.

### Data-source follow-up (2026-10-27)
- Freshly checked FinzData's CL page: it advertises NYMEX CL 5-minute intraday bars from 2007-05-16, bar-start timestamps in US Eastern time, and continuous series with adjusted/unadjusted choices. The page currently advertises full-history access for a one-time $29 and only the latest 30 days of daily bars for free; no data were purchased or retrieved. [Vendor page](https://finzdata.com/futures/cl). This current advertised price differs from the $39 noted in an earlier research entry, so treat pricing as time-sensitive and recheck before any purchase.
- Reuters reported a paid/licensed Truth API feed with an archive dating to 2022, potentially a more authoritative source for exact post times, but pricing/terms and actual timestamp fields were not verified and no access was obtained. [Reuters report, 2026-07-16](https://www.reuters.com/technology/trump-media-unveils-data-feed-businesses-tracking-truth-social-posts-2026-07-16/).
- Attempted to inspect https://trumpstruth.org/feed directly; the web connector rejected its application/xml content type. The feed exists as a public lead, but exact item timestamp fields were not inspected in this run. No event was assigned a candle and no market-performance result was calculated.


## 2026-10-27 13:00 UTC — Canonical source-permalink deduplication in event ledger
- **Finding:** batch mode rejected repeated event IDs but allowed two IDs to cite the same underlying source URL. The same publication could therefore be counted as multiple independent catalyst events.
- **Change:** `sputnik_event_backtest.py::_validate_source_url()` now canonicalizes scheme/host casing, default ports, trailing path slashes, fragments and common tracking parameters. Non-tracking query parameters are retained because some publishers use them as document identifiers. CSV loading and direct `backtest_events()` calls reject duplicate canonical source URLs as well as duplicate event IDs.
- **Regression:** `tests/test_sputnik_event_backtest.py` adds CSV and direct-call tests proving that different event IDs with the same canonical permalink are rejected.
- **Operational path:** source-linked event ledger → permalink validation/canonicalization → duplicate-source guard → paired early/breakout event study.
- **CI:** the first run on the new test commit failed because the CSV fixture contained escaped backslash-n text instead of line breaks (run [40508643456](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40508643456)). Fixed the fixture in test commit `c9deb226b1210d44912626452a2f27674521cb52`; the full ranking test workflow then passed on that exact commit: [40508741124](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40508741124).
- **Deployment:** PR #45 branch only; no merge/deploy. The branch is substantially divergent from current main and needs reconciliation/review before merge.
- **Empirical limits:** source-URL deduplication prevents one URL from masquerading as multiple events; it does not prove semantic equivalence across different URLs or establish predictive value. No source-linked, exact-time NYMEX CL event replay or walk-forward result is claimed.
- **Safety:** PAPER/DEMO ONLY; no broker, orders, secrets or Telegram test messages.


## 2026-10-27 — Diagnose overlapping trade windows in paired event study

- **Finding:** batch mode reported paired mean/median R differences, but it did not show whether separate catalyst events produced trades held over the same market interval. Overlapping trade windows make event outcomes dependent and can make a small event sample look more conclusive than it is.
- **Implemented:** scored simulations now include `exit_time`. The paired summary counts scored trade windows and strict temporal overlaps separately for early-entry and breakout strategies, and adds an explicit caveat to interpret aggregate averages cautiously when event outcomes overlap. This is a diagnostic, not an automatic exclusion of events.
- **Regression coverage:** the existing early-entry fixture asserts the recorded exit timestamp; `test_batch_summary_reports_overlapping_trade_windows` verifies overlap counts and the dependence warning using synthetic timestamps and R values.
- **Commits:** implementation `5f62204a7fc175f53af58dd4afdb80e5564ba2b6`; regression test `b63b099650444b613173a5b0ac4b694fb2111b8d`.
- **CI verification:** GitHub Actions run [40510664664](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40510664664) completed successfully on test commit `b63b099650444b613173a5b0ac4b694fb2111b8d`; job `tests` and step `Run ranking tests` both concluded `success`. The implementation commit's run [40510650474](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40510650474) also concluded `success`. The following commit `0cfbc8deecf3ef9f2d1de3e44fe5a19e1e340d92` updates only this research log; the workflow path filter does not trigger tests for this documentation-only change.
- **Empirical limits:** no validated NYMEX CL dataset paired to exact source-linked catalyst timestamps has been acquired. This change improves interpretation of a future batch result but does not show which strategy performs better. Costs still require defensible spread, slippage and commission inputs; session gaps and contract-roll handling need verified data.
- **Safety:** PR #45 branch only; no merge/deploy, broker changes, orders, or Telegram test messages.


### Data-source follow-up — exact Truth Social timestamps and CL sample (2026-10-27)

- **New event-archive lead:** the public Hugging Face dataset [Cameronk199/donald-trump-truth-social-posts](https://huggingface.co/datasets/Cameronk199/donald-trump-truth-social-posts) documents a `created_at_utc` field described as the original post timestamp normalized to UTC, plus `truth_url` and `source_url` provenance fields. Its README reports 36,170 unique posts covering `2022-02-14T15:54:00Z` through `2026-08-31T12:09:00Z`, snapshot generated `2026-10-26T12:58:33Z`. It is an independent archive derived from public Trumpstruth detail pages, not an official Truth Social feed; the dataset card says `license: other`, so downstream rights/terms must be checked before redistributing data.
- **Retrieval limitation:** the web connector can inspect the README but rejects the Parquet/JSONL download route; the container download attempt for the archive did not succeed. No rows were ingested or event timestamps independently checked against original pages in this run.
- **CL data limitation:** FirstRate Data's public sample link resolves to `frd_sample_futures_CL.zip`, but the browser connector rejects the ZIP content type and the available container download also failed. No sample bars were acquired. The vendor describes NYMEX CL intraday bars from 2008, including 5-minute CSV ZIPs; full dataset access remains a separate acquisition/verification step.
- **CI:** the overlap-diagnostic implementation and regression test passed run [40510664664](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40510664664) on test commit `b63b099650444b613173a5b0ac4b694fb2111b8d`. Subsequent research-log updates also triggered CI: runs [40510714646](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40510714646) on `0cfbc8deecf3ef9f2d1de3e44fe5a19e1e340d92`, [40510742079](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40510742079) on `2ad52d041124b1b7b6f7291d27b3d392340de217`, and [40510866600](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40510866600) on `890dcb8626d5907b2d578bbb087a00ac25ddcd6f` all completed successfully. Each run reported the `tests` job and `Run ranking tests` step as `success`; the available summaries do not expose an exact unittest count.
- **Next step:** obtain the archive in a locally readable form, filter posts to actual market catalysts, preserve original UTC timestamps and permalinks, then pair them with verified CL bars. No event replay or profitability result is claimed.


## 2026-10-27 13:34 UTC — Non-overlapping paired-event sensitivity analysis

- **Status before change:** PR #45 was open, unmerged and mergeable at head `0dc3c722df3f2b326543e10d000f490ccf08bc4f`. Latest completed prior ranking-test run observed was [40510954613](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40510954613), conclusion `success`.
- **Finding:** the batch summary counted overlapping trade windows and warned that outcomes may be dependent, but its mean/median paired difference still used all scored events. A high-overlap event sample could therefore make the headline comparison overstate how much independent evidence exists.
- **Implemented:** `summarize_comparison_results()` now also reports a deterministic chronological non-overlapping sensitivity sample. It keeps an event only when both strategies have scored P&L and timezone-aware entry/exit times, and excludes the whole paired event if either trade window overlaps any window from a previously retained event. It reports retained-pair count, overlap exclusions, missing/invalid timestamp count, mean/median early-minus-breakout R difference, and early/breakout/tie counts for this subset. The original all-paired statistics remain unchanged.
- **Caveat:** this greedy non-overlapping subset is a sensitivity diagnostic; it reduces direct temporal overlap but does not guarantee statistical independence or replace out-of-sample/event-clustered inference.
- **Regression:** added `test_summary_adds_non_overlapping_paired_sensitivity` with synthetic timestamps and P&L. It verifies that one overlapping event is excluded and that the two retained paired differences produce a mean/median of 0.3R. These values are synthetic test fixtures, not market observations.
- **Commits:** implementation `d379b98f7a86166d3be194225a22cebe2f2ccc85`; test `272687cd2b0fc19b2ad559ba6243dd41262362f4`.
- **Verification:** GitHub Actions run [40513210285](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40513210285) was triggered for the test commit. Its `tests` job's `Run ranking tests` step completed with conclusion `success`; at the last API check, the enclosing job/run still reported `in_progress` with no final conclusion. Thus the test command step passed, but the final workflow conclusion has not yet been confirmed. A local run was not possible because the execution container could not resolve `raw.githubusercontent.com`; no local-test claim is made.
- **Data/performance status:** no exchange-verified NYMEX CL OHLCV has been paired with a source-linked ledger of exact catalyst publication times. No real-event replay, profitability conclusion, or production deployment is claimed.
- **Safety:** PR branch only; no orders, broker changes, Telegram test messages, or deployment.


## R&D update — 2026-10-27: separate publication time from system availability
- **Finding:** the event-study harness chose the first candle after `event_time` even when the catalyst became available to the system later. This could simulate an entry before the system could know the news.
- **Change:** `sputnik_event_backtest.py` now requires `available_at` separately from `event_time`; rejects availability earlier than publication; the early-entry path waits for the first candle timestamp strictly after `available_at`; output records `available_at` and an explicit early `decision_time`. Breakout output records its signal-bar `decision_time` separately from next-bar execution.
- **Ledger/CLI:** batch CSV now requires `available_at`; single-event CLI requires `--available-at`. Existing CSV ledgers must be migrated before they can be replayed.
- **Regression:** `tests/test_sputnik_event_backtest.py::test_entry_waits_until_first_bar_after_source_available_at` and `test_availability_before_publication_is_rejected`, plus updated ledger fixtures.
- **Commits:** code `8fbad8a207305541709325060fcee1ef5182281f`; tests/fixture correction `3ff465067a8a74432d8f09fc67afd0cfcbcfdacb`.
- **CI:** first run [40513793845](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40513793845) exposed two fixture/expectation errors; they were corrected. Final ranking-tests workflow [40513932535](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40513932535) completed successfully.
- **Operational path:** source publication `event_time` → system receipt `available_at` → decision time → first permissible bar/next-bar execution.
- **Empirical limit:** synthetic regressions only; no source-linked exact-time catalyst ledger paired with exchange-verified NYMEX CL bars, no out-of-sample result, and no session/expiry/rollover calendar. PR branch only; no merge/deploy.
- **Safety:** PAPER ONLY; no broker, order, secret, or Telegram test message.


## Historical-source recovery status — 2026-10-27
- Retrieved and inspected the Library file `Registro Studio IBKR - aggiornato 2026-10-20 sessione 9.md` (535 lines). Its documented priorities include point-in-time `event_time`/`available_at`/`decision_time`, and testing any options/positioning feature against a baseline rather than treating it as directional proof. The options webinar's presentation was consulted; the video was not recorded as watched.
- Library search did **not** recover an authentic numbered 100-rule catalog. Searches for the exact phrases `catalogo dei 100 punti`, `100 regole`, `ORB_RETEST_TIMING_GATE`, and the named Feedback Engine record did not locate a source document that could substantiate a complete catalog. Do not invent or reconstruct missing rules from memory.
- Search did surface historical code snapshots such as `commodity_bot_v3.9.py` and `commodity_bot_v4.0.py` containing descriptive MAE/MFE and adaptive SL/TP logic. These are code snapshots, not proof of a complete research catalog, current production behavior, or empirical profitability.
- This recovery is a source audit only. Any lesson still requires an operational code path, regression test, CI result, deployment confirmation, and out-of-sample evidence before it can be called implemented/validated.

## 2026-10-27 — Make breakout decision timestamps causal

- **Finding:** the event backtest used the opening timestamp of the breakout candle as `signal_time` and `decision_time`, although the breakout predicate depends on that candle's completed close. This made the audit metadata appear up to one bar earlier than the information was available.
- **Change:** document that OHLCV timestamps must represent bar opens; record the signal time at the bar boundary after the close; align decision time to that boundary and reject a next candle that starts before the declared close boundary as `UNMODELED_BAR_INTERVAL`.
- **Regression tests:** assert signal-bar time, causal signal/decision time, equality with the next-bar entry time on contiguous five-minute data, and fail-closed behavior for a one-minute spacing passed as five-minute candles.
- **CI:** code and tests committed to the existing PR branch; a fresh Actions run must confirm the new revision. No local execution or empirical performance result is claimed.
- **Limits:** source-provider timestamp semantics still need confirmation before importing real candles. This fixes timestamp integrity, not strategy profitability. No merge, deploy, broker, or order execution.

## 2026-10-27 — Audit of the historical 100+ point register

- **Recovered directly from prior conversation context:** point 100, “Execution Regime: Volatility × Liquidity” (Calm/Liquid, Thin, Fast/Liquid, Stress; proposed module `EXECUTION_REGIME_ENGINE`); point 101, “Overnight Risk Engine / Next-Session Volatility Forecast” (overnight WTI returns/range/realized volatility/volume/jumps as a next-session volatility input, explicitly not direction); point 102, “Setup Transferability / Instrument-Specific Edge”; point 103, “Sweep Validity / Continuation-vs-Reversal” (an isolated sweep is not proof of reversal; distinguish break, follow-through, acceptance/rejection and wait for structure/trigger).
- **Source audit:** the Library file “Registro Studio IBKR - aggiornato 2026-10-20 sessione 9.md” contains the IBKR study sessions and numbered material through 36, not the original 100+ point register. The retrieved historical context does not contain points 1–99 in full; they are deliberately not reconstructed.
- **Implementation mapping:** the breakout timestamp correction in this PR is a point-in-time audit improvement, not implementation of sweep detection. Point 103's sweep-specific detector and point 101's overnight-volatility study remain unimplemented; point 102 needs instrument-specific out-of-sample evidence. Do not label these as completed.
- **Validation boundary:** the recovered register is a historical research source, not evidence of profitability. PAPER ONLY; no merge, deploy, broker, or orders.

## 2026-10-27 — Verification follow-up for causal breakout timestamps

- **Code commit:** `fe9c160b7a5fa48e8f2af003de2ffb4b53252ec6`; **regression-test commit:** `fecae28557af1f3689ed17cc098dfe18821ef4ef`.
- **CI:** SPUTNIK ranking tests passed on the code/test revision in run [40522083277](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40522083277); the later log-only revision also passed in run [40522102565](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40522102565). The subsequent historical-register edit is documentation-only.
- **Deployment:** PR #45 remains open and unmerged. No Render/Telegram runtime-log connector was available in this execution, so production deployment and message delivery are not confirmed. Render build-pipeline quota remains a deployment blocker.
- **Safety:** PAPER ONLY; no secret values inspected, no Telegram test message, no broker, no orders.


## 2026-10-27 — Require secure source URLs in the WTI event backtest

- **Finding:** the event-ledger loader accepted HTTP and non-standard-port source URLs even though the operational Sputnik permalink gate requires unambiguous HTTPS item links. This could let a manually supplied research CSV bypass the same minimum provenance hygiene.
- **Change:** `sputnik_event_backtest.py::_validate_source_url` now requires HTTPS, rejects embedded credentials, and permits only the default HTTPS port (or explicit 443); malformed ports fail closed.
- **Regression:** `tests/test_sputnik_event_backtest.py` covers HTTP, non-standard port, and malformed port. Also moved the `unittest.main()` guard to the end so the trailing breakout-timestamp regression is actually defined during direct execution.
- **Operational path:** CSV event ledger → source URL validation → canonical deduplication → early-entry/breakout comparison.
- **Validation limit:** this is source-URL hygiene and test-discovery correctness, not a claim that the event is authentic or the trading rule profitable. Await CI on the final PR head; no live replay, merge, Render deploy, Telegram message, broker, or order.
- **Safety:** PAPER ONLY.


## 2026-10-27 — CI and runtime verification for secure backtest source URLs

- **Code commit:** `4be6f1fb81b3badf52efa11212b9049be2e89a77`; **test/discovery fix:** `e08c660c76eff751ae78802b511ecc5f2ce8c96c`; **research-log update before this entry:** `563d421c13923aa3038c8f2a34407232c672f32a`.
- **CI:** SPUTNIK ranking tests PASS on final code/test revision, run [40526067753](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40526067753). The first run failed because the new CSV fixture contained literal escaped newline characters; the fixture was corrected before the passing run.
- **PR:** #45 remains open/unmerged; no merge or deployment.
- **Render:** listener is configured on `main`; last live Sputnik deployment is commit `9e5204bf7d9074dba27637013b7d98933a91e733` from 2026-10-16. The 2026-10-22 attempt for `50851b0dc76f1b7ed0adaa872c47aa84793687f9` failed because the workspace ran out of build-pipeline minutes. App logs at 2026-10-27 14:41 UTC show listener online and Telegram bootstrap authorized, but this window contains no SEC/White House feed log entries and does not prove a market alert was delivered.
- **Empirical limit:** no historical WTI replay or profitability result from this URL-validation change.
- **Safety:** no secrets inspected, no test Telegram message, no broker or orders; PAPER ONLY.


## 2026-10-27 — Reject candle spacing shorter than the declared timeframe

- **Finding:** the WTI event backtest marked gaps longer than the declared interval, but did not reject a dataset sampled more frequently than that interval. For example, one-minute bars passed with a five-minute setting could distort holding-bar duration and early-entry timing even though the breakout path had a local timing check.
- **Change:** `_bar_gap_diagnostics()` now reports unexpected short intervals and the minimum observed spacing; `backtest_event()` fails closed with `UNMODELED_BAR_INTERVAL` for both early and breakout models when candle spacing is shorter than the declared interval.
- **Regression:** the short-spacing fixture now asserts both models are unscored, the interval mismatch count is two, and no P&L is produced.
- **Operational path:** OHLCV timestamp validation → declared-interval diagnostics → early/breakout simulation eligibility.
- **Verification:** implementation commit `65a9137b0a336ce8b6d8355fe65c0adf53d2d1cc`; test commit `6e73a4e9b91b9207c916f3b5f344601d1fe47cb1`; GitHub Actions run [40526436413](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40526436413) passed on final PR head `4dd8dd93861e954f57617c567e94c43a03e87482`: 116 tests ran, OK. No empirical backtest result is claimed.
- **Limits:** this prevents timeframe-mismatch scoring but does not provide an exchange session calendar or validate the source instrument/volume. PR #45 remains open/unmerged; no Render deploy, Telegram test message, broker, or order.
- **Safety:** PAPER ONLY.


## 2026-10-27 — Historical notes recovered from prior conversation context (not a reconstructed catalog)

- **Exact names recovered:** `ORDER_FLOW_DATA_INTEGRITY_GATE`; `ORDER_FLOW_PROVIDER_AUDIT`; `SELECTIVE_LLM_ARCHITECTURE`. The recovered architecture note says LLMs are for ambiguous text/context, while deterministic code owns calculations, sizing, stop loss, exposure, and final authorization. The recovered experiment discipline is: preregister → full grid → costs → falsification → out-of-sample (OOS) → promote/reject.
- **Numbered catalog boundary:** no original complete 100-point file is available in the retrieved context. Points 51–99 are not retrievable; only the titles of 100–103 are explicitly recoverable, without their verbatim original explanations. The Library file `Registro Studio IBKR - aggiornato 2026-10-20 sessione 9.md` contains numbered study entries through 36 and explicitly treats its options presentation as illustrative, not a backtest. Do not present paraphrases as the original catalog.

- **Sputnik mapping/status:** item permalink/time validation and the WTI event-ledger HTTPS gate implement part of source/data integrity; SEC 403 cooldown is present, but the last Render log query contained no fresh SEC/White House feed entries, so current source recovery is unverified. No dedicated order-flow provider audit or LLM-based final authorization is claimed. The event backtest is an experimental comparison, not the complete preregistered full-grid/cost/falsification/OOS workflow; no empirical WTI edge is established.
- **Related commits and tests:** current work in PR #45; secure URL tests passed on code/test commit `e08c660c76eff751ae78802b511ecc5f2ce8c96c` (run [40526067753](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40526067753)). A subsequent short-interval regression commit is on the same branch; its current-head CI was not visible as complete at this audit.
- **Deployment:** PR remains unmerged; Render live commit remains `9e5204bf7d9074dba27637013b7d98933a91e733`; build pipeline quota is exhausted. PAPER ONLY; no secrets, broker, order or Telegram test.


## 2026-10-27 — Audit of the original 100-point research catalog

- **Recovery attempt:** searched the Library (including `Registro Studio IBKR - aggiornato 2026-10-20 sessione 9.md`) and retrieved prior-conversation summaries dated 2026-10-03.
- **Verified result:** the earlier conversation explicitly recorded that the original numbered 1–100 catalog and complete list of roughly 100 points had not been recovered; only incremental summaries were available. The IBKR session-9 file is a separate study register, with numbered study items through item 32 and later hypotheses; it is not evidence of the missing 100-point catalog.
- **Decision:** do not reconstruct or relabel missing items as original lessons. Apply only directly retrievable, source-backed findings and record inferred hypotheses separately. Items 100–103 appearing in recent implementation notes remain implementation hypotheses, not proof that the original catalog has been recovered.
- **Scope:** this is a provenance/research-integrity finding, not a code feature or empirical trading result.


## 2026-10-27 — Deduplicate common ad-click tracking parameters

- **Finding:** the event-ledger canonicalizer already removes `utm_*`, `fbclid`, `gclid`, and selected mailing/referrer keys, but still treated common ad-click IDs such as `msclkid` and `srsltid` as distinct event sources. This can let the same publisher permalink appear twice in a manually assembled event ledger.
- **Implemented:** extend only the canonical deduplication key with common click IDs (`msclkid`, `dclid`, `ttclid`, `twclid`, `srsltid`, `yclid`, `igshid`, `mkt_tok`, `vero_id`, `vero_conv`). The original `source_url` remains untouched for provenance; remaining query parameter order is preserved.
- **Files:** `sputnik_event_backtest.py`; `tests/test_sputnik_event_backtest.py`.
- **Regression:** two rows with the same article URL but different Microsoft/Google-search click IDs, host casing, trailing slash and fragment must be rejected as duplicate canonical sources.
- **CI:** initial run 40530933881 failed because the fixture encoded literal backslash-n separators, so the CSV header parsed as one field; corrected in test commit `fe08204af8be96dc9ff42c939396e0ec6894dea2`. Follow-up run [40531033411](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40531033411) passed: 119 tests, OK.
- **Operational path:** event CSV → `load_events_csv` → `_canonical_source_url` → duplicate-source gate before event backtest.
- **Deployment:** PR #45 branch only; Render auto-deploy targets `main`, and no deploy was triggered.
- **Empirical validation:** source deduplication only; no WTI return or predictive-edge claim.


## Recovered from prior conversation summaries — 2026-10-03/06 (not the missing 100-point catalog)

- **2026-10-03 07:04 UTC summary:** public-disclosure intelligence covered OGE/Senate/House sources, disclosure lag, amount buckets, and the pipeline `source → document → transaction → normalization → deduplication → sector/commodity → score → Telegram`.
- **2026-10-03 21:17 UTC summary:** proposed reusable components were event clustering, deduplication, source weighting and evidence confidence. The notes explicitly rejected keyword-to-market causality and automatic LONG/SHORT solely from keywords.
- **2026-10-05 05:33 UTC summary:** keep verified facts, signals and correlations separate; do not turn rumors into certainty.
- **Mapping to current work:** PR #45 implements a causal event ledger with `event_time`, `available_at`, pre-event ATR time, source permalink and canonical URL deduplication. It does not yet implement the complete OGE/Senate/House document-to-transaction pipeline, source-primary verification, disclosure-lag model, or empirical news-to-commodity edge.
- **Test/CI:** click-ID canonical dedup regression passes in run [40531033411](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40531033411); the research-log commit run [40531124518](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40531124518) also passed.
- **Deployment:** PR #45 remains open; Render service targets `main`. No deploy.
- **Empirical status:** no event-linked, verified NYMEX CL out-of-sample result. These are recovered conversation summaries, not a recovered original numbered catalog.

## 2026-10-27 — CLZ26 hypothesis audit and USD-per-contract reporting

- **Hypothesis under review:** timestamp recorded in the prior research log as 2026-10-27 14:16:51 UTC; conditional SHORT only below 100.50, reference about 101.45, stop 101.55, TP1 98.25, TP2 97.15. No order was placed.
- **Freshest usable quote snapshot found:** Farmbucks identifies the instrument as NYMEX December 2026 CLZ26 and displayed 100.11 USD/bbl at 2026-10-27 10:25 UTC-5 (15:25 UTC), with session range 99.85–102.82. The page labels futures quotes delayed by 10 minutes and also says “updated 21 min ago” at retrieval. Source: https://farmbucks.com/futures/energy/wti-crude
- **Outcome classification:** **NON-VERIFIABLE**. The displayed price and low are below 100.50 after the hypothesis timestamp, suggesting the trigger level was crossed by the snapshot, but the source does not give timestamped intraday bars or the first-crossing time. The 101.55 stop lies within the displayed session range and the range alone cannot establish whether it was touched after entry. TP1/TP2 are below the displayed low as of the snapshot, but that is not a complete post-hypothesis path or a final session result. Do not label this as a certified trigger/stop/target outcome.
- **Single code improvement:** scored trades now report gross P&L, net P&L and round-trip cost in USD per contract, in addition to the existing price-unit fields. Conversion uses the declared contract multiplier (CL default 1,000 barrels/contract); the R multiple remains calculated from net price-unit P&L divided by price-unit risk.
- **Files changed:** `sputnik_event_backtest.py`; `tests/test_sputnik_event_backtest.py`; this log.
- **Regression:** extended `test_execution_cost_model_deducts_commission_and_two_sided_slippage` to assert synthetic gross P&L $200, net P&L $150 and round-trip cost $50 per contract for the fixture. These are test values, not market results.
- **CI verification:** GitHub Actions run [40538023486](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/40538023486) ran `python -m unittest discover -s tests -p "test_*.py" -v` on PR head `15a7c60b86f2a646ca41e0676609e89b1ba409ea`; **119 tests ran, OK**. The CI log also emitted handled `OSError` messages for WHITE_HOUSE, TRUTH_ARCHIVE and OGE source fetches, so external source availability was not validated by this suite. A local clone/test attempt was blocked because the container could not resolve `github.com`.
- **Data/performance block:** no reliable post-hypothesis 1-minute/5-minute CLZ26 OHLCV sequence with source timestamps was obtained; no historical trade outcome or strategy profitability is claimed. The quote is delayed.
- **Safety:** PR branch only; no orders, broker changes, Telegram test messages, or production deployment.
 
## 2026-10-27 — Separate source availability from strategy decision time

- **Finding:** the event ledger captured publication time (event_time) and system availability (available_at), but the simulator implicitly equated strategy decision time with available_at. This can overstate early-entry timeliness when processing/analysis latency exists.
- **Implemented:** backtest_event accepts an optional timezone-aware decision_time; the first eligible entry bar must open strictly after it. A supplied decision time before available_at is rejected. Batch event CSVs may include decision_time; legacy ledgers remain compatible but the output explicitly labels the fallback decision_time_source=assumed_available_at.
- **Operational path:** event CSV → load_events_csv → backtest_events → backtest_event → earliest eligible entry bar and early.decision_time. CLI single-event mode also accepts --decision-time.
- **Files:** sputnik_event_backtest.py, tests/test_sputnik_event_backtest.py.
- **Regression:** added test_event_ledger_decision_time_delays_entry_and_must_follow_availability; verifies that a decision at 00:12 cannot fill on the 00:05 or 00:10 bar, and rejects a decision timestamp earlier than availability.
- **Commits:** implementation 322a94dd57c162e4ee57a3211d29d96d9de83991; test 591fd6b97355983562fee9b734e17fc0cec3ae8b.
- **CI:** pending at log update; report only the workflow result visible after this commit.
- **Deployment:** PR #45 branch only; no merge/deploy.
- **Empirical limit:** this removes one optimistic timing assumption only when actual decision times are supplied. Legacy ledgers still assume decision time equals availability and are labeled accordingly. No verified CL/event-time sample or profitability claim.

