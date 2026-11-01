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


## 2026-10-31 — Add automatic fresh commodity quote fallback

- **Observed issue:** SPUTNIK's CFD builder only read quotes already persisted in state. The Telegram alert showed “quote/ATR unavailable” and stopped, even though the user wanted an instant price lookup.
- **Implemented:** `sputnik_cfd.py` now requests the latest Yahoo Finance 1-minute futures candles when the stored quote is absent or stale. It maps Gold, Silver, Copper, WTI, Brent, Natural Gas, Wheat, Corn and Soybeans to Yahoo futures symbols, calculates ATR(14) from the returned candles, and uses the source candle timestamp.
- **Freshness guard:** the existing 30-minute timestamp check remains in force. If Yahoo returns stale/closed-market data, insufficient candles, or an error, SPUTNIK still withholds entry/SL/TP rather than inventing prices.
- **Source:** Yahoo Finance chart endpoint, no API key required. Quotes may be delayed or unavailable for some instruments; this is a fallback source, not an exchange-direct feed.
- **Verification:** implementation committed as `b99642c4593f9bf2703fed553dc5241480968392`. Automated CI and production Render/Telegram deployment have not yet been verified. PAPER ONLY; no orders sent.


## 2026-10-31 — Add free independent SILV spot cross-check

- **Change:** after Sputnik obtains a timestamped Yahoo 1-minute futures quote, it now requests SILV DATA's public no-auth JSON feed for gold, silver and copper. It records the independent spot reference, timestamp, unit, and percentage difference in the signal metadata.
- **Important basis rule:** SILV is a spot reference while Yahoo symbols are futures. The calculated difference is labelled `SPOT_VS_FUTURES_BASIS_CHECK`; it is informational and does not replace the Yahoo futures entry price, ATR, SL or TP, nor automatically block a signal.
- **Freshness:** SILV reference is accepted only with a valid timestamp no older than 30 minutes. Timeout, missing symbol or stale data are reported as unavailable; no value is fabricated.
- **Cost:** SILV endpoint requires no API key and is documented as free. Its published update schedule is 15 minutes for precious metals; it is not a tick feed.
- **Verification:** code committed as `8acdd7677be751425818f3458abacce82e8eda5c`. Automated tests, live endpoint behavior from the bot runtime, GitHub Actions and Render/Telegram deployment have not yet been verified. PAPER ONLY; no orders sent.


## 2026-11-01 — Competition-style execution filter

Studied the CME Trading Challenge framework and published futures-trader material describing Direction, Location, Aggression, VWAP, breakout/retest, volume and strict risk controls. Added `sputnik_competition_setup.py` and tests. `sputnik_cfd.py` now requires the D-L-A setup to confirm when at least 60 timestamped OHLCV candles are available; otherwise it returns WAIT. OHLCV volume is explicitly only an aggression proxy, not true bid/ask footprint or DOM order flow. PAPER ONLY; CI and production deployment remain unverified.

- Follow-up integration: Yahoo's existing 1-minute futures fallback now preserves OHLCV and timestamps (not just the latest close/ATR), so the focused trend layer and D-L-A filter can consume a real one-day candle series. This is still Yahoo continuous-futures data, not exchange-native DOM/footprint; availability and volume quality vary by contract/session.

## 2026-11-01 — Explicit BIAS / SETUP / PAPER state; remove WAIT fallbacks

- **Finding:** the active CFD builder already preserved a directional catalyst when fresh price/ATR were missing, but one invalid-ATR regression still expected WAIT. The legacy cart and Telegram formatter also emitted WAIT for missing quotes or unsupported direction, obscuring the distinction between a market hypothesis and an executable setup.
- **Implemented:** build_cfd_signal() now returns NEUTRAL / NO_DIRECTION when no directional recommendation exists; a supported LONG/SHORT remains EARLY_BIAS when execution quote or ATR is unavailable. With fresh levels but no D-L-A confirmation it is EARLY_SETUP; only an explicitly confirmed D-L-A setup is CONFIRMED. Every builder output states paper_trade_status=NOT_EXECUTED.
- **Telegram:** the CFD formatter now prints separate BIAS, SETUP and TRADE PAPER fields. It explains missing levels without changing or hiding the bias. The legacy cart follows the same states and no longer labels a suggestion as an executed TRADE.
- **Method boundary:** D-L-A uses timestamped OHLCV and volume as an aggression proxy only; this is not DOM, footprint or exchange-native order flow. No tick-value/contract-size inference, no real orders and no paper trade journal entry are created by this formatter.
- **Tests added/updated:** no-recommendation neutral state; directional bias with unavailable quote; invalid ATR preserving LONG; Telegram labels and absence of WAIT; legacy cart state transitions. Fresh price/ATR still required for entry/SL/TP.
- **Limits:** this changes SPUTNIK's CFD signal presentation/state only. It does not prove profitability, live quote availability, Telegram delivery or deployment. Multi-source futures coverage and historical 100-setup out-of-sample validation remain open.
- **Safety:** PAPER ONLY; no broker orders, paid APIs, secret reads or Telegram test messages.
- **Direction conflict regression:** if focused OHLCV or a D-L-A setup points opposite to a supported catalyst, SPUTNIK now keeps the catalyst BIAS and records technical/setup direction plus ALIGNS/CONTRASTS separately. A technical-only direction is used only when no catalyst side exists. The regression test covers LONG news with SHORT focused/D-L-A evidence.
- **Telegram decision/reasoning path:** the no-plan fallback now reports NEUTRAL / NO_DIRECTION instead of WAIT. Analyst reasoning also uses NEUTRAL when no side is supported, and legacy status expectations were updated to EARLY_BIAS / EARLY_SETUP / NO_DIRECTION. The user-facing decision message no longer prints WAIT as the fallback.


## 2026-11-01 — SILV independence claim corrected on current main
- **Finding:** the CFD cross-check marked SILV as independent solely because its provider-reported component list did not name Yahoo. That is not an independent audit. A spot/futures basis is descriptive and does not prove independent price discovery.
- **Implemented:** keep the signed spot-minus-futures basis separately labelled; set independence to unknown with `PROVIDER_REPORTED_NOT_AUDITED`; retain `false` only for a known source overlap. Expose the caveat in the Telegram CFD message.
- **Execution safety:** Yahoo futures remain the only execution/ATR/entry/SL/TP basis. SILV remains spot-reference only; no averaging, no substitution, no orders.
- **Files:** `sputnik_cfd.py`, `tests/test_sputnik_cfd.py`, `SPUTNIK_RESEARCH_LOG.md`.
- **Validation:** after rebasing PR #74 onto current main, CI passed before merge: SPUTNIK ranking **147 tests** (run `41286827801`) and Telegram/menu/CFD **53 tests** (run `41286827810`), both SUCCESS. No live quote, deployment or Telegram delivery claimed.
- **Limit:** SILV component independence remains unaudited; status is explicitly unknown rather than independent.
- **Safety:** PAPER TRADING only; no paid APIs or real orders.


## 2026-11-01 — Preserve preliminary D-L-A direction before trigger confirmation

- **Finding:** the competition evaluator returned NEUTRAL/WAIT unless EMA trend, VWAP, breakout/retest and relative volume all aligned. This hid a directional context when EMA20/EMA50 and VWAP already agreed, and the Telegram D-L-A line could show no direction even though the setup was simply early.
- **Implemented:** the evaluator now publishes LONG/SHORT as an EARLY_SETUP bias when trend and VWAP agree. Breakout/retest, relative OHLCV volume (>=1.2x) and a valid structural stop are still required for SETUP_CONFIRMED. Insufficient history is INSUFFICIENT_DATA; unordered timestamps are INVALID_DATA; unsupported context is NEUTRAL/NO_DIRECTION. Entry and structural stop remain absent until confirmation.
- **Integration:** Sputnik displays the preliminary D-L-A direction and ALIGNS/CONTRASTS without replacing a supported news BIAS. If the news side is neutral, an aligned D-L context may be surfaced as DLA_EARLY technical-only bias. D-L-A is skipped for stale quote candles.
- **Data boundary:** aggression remains OHLCV volume proxy only; no DOM, footprint or exchange-native order flow is claimed. PAPER TRADING only; no orders are sent.
- **Files:** `sputnik_competition_setup.py`, `sputnik_cfd.py`, `tests/test_sputnik_competition_setup.py`, `tests/test_sputnik_cfd.py`, `SPUTNIK_RESEARCH_LOG.md`.
- **Tests added:** early context bias without trigger; full D-L-A confirmation requires volume and structural stop; neutral context; invalid candle ordering; Telegram visibility of early D-L-A bias; news-direction preservation and technical-only fallback.
- **Validation:** commit and GitHub Actions verification recorded after push. No live quote, deployment or Telegram delivery claimed.
- **Open:** add an audited independent futures reference for same-contract comparison; current Yahoo continuous futures remain the only execution basis, while SILV is spot-reference only and its source independence remains unaudited. Build the real historical 100-setup sample and out-of-sample metrics.


### CI verification — D-L-A early bias change

- **Implementation commit:** `da033603596c626945d896069c3fc5fe190069db`.
- **Files:** `sputnik_competition_setup.py`, `sputnik_cfd.py`, `tests/test_sputnik_competition_setup.py`, `tests/test_sputnik_cfd.py`, `SPUTNIK_RESEARCH_LOG.md`.
- **GitHub Actions:** ranking/full test discovery run `41289274251` — SUCCESS, **155 tests passed**; Telegram menu/CFD regression run `41289274274` — SUCCESS, **55 tests passed**.
- **Results:** early LONG/SHORT D-L context survives missing trigger; a supported news BIAS is not flipped by opposite D-L-A; technical-only early bias is labelled separately; no levels are emitted by the D-L-A evaluator before trigger, volume and structural stop confirmation.
- **Limitations:** these are deterministic CI tests, not historical-market performance validation. The Actions log includes mocked Telegram delivery fixtures; no live Telegram delivery, production deployment, real quote freshness, DOM/footprint feed or real order was verified.
- **Open:** independent same-contract futures references, source-independence audit, real 100-setup out-of-sample diary/metrics, and runtime monitoring verification remain open.


## 2026-11-01 — Add optional Narwhal free futures reference to SPUTNIK

- Provider terms checked: Narwhal official pricing lists Free at $0/month, 5,000 successful requests/month, 30 requests/minute and no overage charges. The futures reference documents 15-minute-delayed free latest prices; free one-minute bars are not included. The API requires a Bearer key.
- Implemented: SPUTNIK now has an opt-in, reference-only Narwhal quote reader for shared futures roots GC, SI, HG, CL, ZW, ZC and ZS. It is disabled by default and requires NARWHAL_REFERENCE_ENABLED=1 plus NARWHAL_API_KEY.
- Quota control: deterministic one-root rotation every 30 minutes. If the same free key is shared with GAGARIN's 15-minute rotation, nominal load is about 4,320 successful quote calls per 30-day month (2,880 GAGARIN + 1,440 SPUTNIK), below 5,000. Actual usage must still be monitored.
- Data contract: preserves provider, root symbol, source timestamp, USD currency, raw unit, price, age, delayed/stale/session flags and price-scale metadata. Bid/ask are null because this endpoint does not provide them. No exact delivery month or upstream source routing is disclosed.
- Safety: quote is shown in Telegram as NARWHAL REF only. It never replaces Yahoo futures execution price, ATR, entry, SL or TP. No percentage deviation is calculated because exact expiry and upstream independence cannot be verified. Stale or malformed values are status-labelled and not treated as live.
- Files: sputnik_cfd.py; tests/test_sputnik_cfd.py.
- Tests added: default disabled; missing key causes no network call; delayed quote preserves provenance and is reference-only; stale quote flagged; Telegram shows reference without changing Yahoo execution entry.
- Runtime limitation: no user Narwhal API key was available in this run, so the real authenticated endpoint response and production freshness were not verified. CI uses mocked endpoint responses only. Feature remains disabled until a free key is supplied through repository secret NARWHAL_API_KEY and variable NARWHAL_REFERENCE_ENABLED=1.
- Sources: Narwhal official futures API reference and pricing page. PAPER ONLY; no real orders.


### CI verification — Narwhal reference integration

- Merged PR #80; squash commit b5abfbfe0c4c3bf784ea0bf951500157a292179a.
- Final PR-head validation: SPUTNIK ranking workflow runs 41292920380 and 41292929636 — SUCCESS, 160 tests passed; Telegram menu/CFD workflow runs 41292920274 and 41292929656 — SUCCESS, 60 tests passed.
- One initial test-only failure was caused by a case-sensitive expected substring after lowercasing the Telegram message; corrected the assertion and reran both workflows successfully. No production signal logic was changed in that correction.
- These are mocked CI endpoint tests. No authenticated Narwhal request, live market quote, Telegram delivery or deployment was verified. Narwhal remains opt-in and disabled until the free API key is configured. PAPER ONLY.
