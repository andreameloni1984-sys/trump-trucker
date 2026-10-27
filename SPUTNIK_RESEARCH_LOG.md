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
