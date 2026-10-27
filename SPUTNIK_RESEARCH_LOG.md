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
