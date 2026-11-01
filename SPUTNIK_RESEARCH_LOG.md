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


### Runtime workflow wiring — Narwhal optional feed

- Merged PR #81; commit fd46c27ad4b3e97c6c99765d1fa43711d1c88726.
- Added sputnik_cfd.py and tests/test_sputnik_cfd.py to the SPUTNIK runtime workflow path filters, and passed NARWHAL_REFERENCE_ENABLED=1 plus the NARWHAL_API_KEY repository secret to the scheduled runtime step.
- With the secret absent, the adapter exits as NOT_CONFIGURED before making a network request; no key or paid plan is required for the documented free tier.
- YAML syntax parsed successfully in a local validation. The workflow's push-triggered production run was not yet visible in the Actions query at log time. No live authenticated Narwhal response, deploy or Telegram delivery is claimed.


## 2026-11-01 — Remove false WAIT from the live dashboard/cart rendering

- **Finding:** `build_cfd_cart()` returns `EARLY_BIAS`, `EARLY_SETUP` or `NO_DIRECTION` and always marks `paper_trade_status=NOT_EXECUTED`. The Telegram dashboard/cart instead checked for a nonexistent `TRADE` state and rendered every row as `WAIT`, hiding supported LONG bias and misrepresenting an unexecuted paper suggestion.
- **Change:** add `cfd_cart_display_state()` as a single safe mapping for directional bias, setup timing and PAPER status. Dashboard and cart now show LONG/SHORT BIAS, `EARLY_BIAS`/`EARLY_SETUP`, or `NEUTRAL / NO_DIRECTION`; `TRADE PAPER: NOT_EXECUTED` is explicit. Conditional levels are shown only when present; the formatter does not label them as an executed trade or show calculated unit sizing.
- **Files:** `sputnik_cfd.py`, `telegram_listener.py`, `tests/test_sputnik_cfd.py`, `tests/test_telegram_menu.py`.
- **Tests:** add state-mapping regressions for missing quote, early setup, neutral side and unknown status; assert both user-facing dashboard/cart blocks contain no `WAIT` and expose PAPER/NO_DIRECTION.
- **Verification:** GitHub Actions pending at commit creation. No live Telegram send, live quote, deploy or order is claimed. PAPER ONLY.
- **Open:** Gagarin still needs a verified independent same-contract futures source; both bots still need a real 100-setup out-of-sample journal/metrics and production Telegram delivery verification.


### Verification — dashboard/cart state fix

- **Implementation commit:** `39ea9bf90dcc048a42f1520b96886ef1801dd6a4`.
- **GitHub Actions:** Telegram/menu workflow `41294183551` — SUCCESS, 65 tests; ranking/full test workflow `41294183516` — SUCCESS, 165 tests; SPUTNIK runtime workflow `41294183535` — SUCCESS.
- **Telegram runtime evidence:** the SPUTNIK runtime log recorded confirmed sendMessage responses with positive message IDs `631` and `632`. The confirmation helper accepts a message only when Telegram returns `ok=true` and a positive `result.message_id`. Four other send attempts in that same run were explicitly NOT confirmed; delivery is therefore partial, not fully reliable.
- **Runtime problems:** WHITE_HOUSE, TRUTH_ARCHIVE and OGE fetches reported `OSError`; the GAGARIN cloud handoff was disabled because its URL/key were not configured; one Form 4 XML could not be found. No live quote, Render deployment or order is claimed.
- **Follow-up:** dashboard footer now states that sizing is not displayed without complete specifications. PAPER ONLY; no paid data service or real order.


- **Post-footer rerun on main:** Telegram/menu workflow `41294250310` — SUCCESS, 65 tests; ranking/full tests `41294250217` — SUCCESS, 165 tests; runtime workflow `41294250220` — SUCCESS, 25 smoke tests. Runtime again confirmed Telegram messages `633` and `634`; four other attempts remained unconfirmed. The runtime workflow then persisted state to main. The repeated partial-delivery pattern remains open.

## 2026-11-01 — Cross-bot Telegram state audit (no second functional change)

- **Inspected main:** 9191eb449231d10a840c06ee35627034f93a373d. The previous SPUTNIK dashboard/cart fix remains present; no duplicate patch was applied.
- **Current CI evidence for the prior code fix:** Telegram/menu 41294183551 SUCCESS (65 tests), ranking/full tests 41294183516 SUCCESS (165 tests), runtime 41294183535 SUCCESS; post-footer rerun 41294250310 SUCCESS (65), 41294250217 SUCCESS (165), 41294250220 SUCCESS (25 smoke tests). These checks belong to the earlier SPUTNIK change, not a new SPUTNIK code change in this run.
- **New audit finding:** trump_tracker.py:gagarin_confirmation_message() still defaults a missing matched-row action to the literal WAIT. This is a user-facing fallback and should become an explicit non-execution state while preserving any available BIAS. The focused OHLCV analyzer also uses WAIT_CONFIRMATION as an internal neutral status; do not treat that as DOM/order-flow confirmation.
- **Work performed in this run:** no SPUTNIK functional file was changed, because the single functional improvement for this execution was applied to GAGARIN's legacy Telegram formatter. This log entry records the SPUTNIK audit and prevents a duplicate dashboard/cart change.
- **Open:** replace the missing-action Telegram fallback in trump_tracker.py; continue checking partial Telegram delivery (the prior runtime had four unconfirmed attempts despite four confirmed IDs across two runs); resolve WHITE_HOUSE/TRUTH_ARCHIVE/OGE OSError fetches and missing GAGARIN handoff configuration; verify Narwhal only with a real free-plan credential/response; continue the real 100-setup out-of-sample journal. No live quote, full Telegram delivery, deployment, or real order is claimed. PAPER ONLY.


## 2026-11-01 — Verify Sputnik handoff after Gagarin convergence correction

- **Inspected main:** `457b84e4df7725717b4246728049888b4d478d27`; no duplicate dashboard/cart change was made.
- **Current file finding:** `trump_tracker.py` at line 681 still formats a missing Gagarin action as the literal `WAIT`. The matched row can retain its instrument/price/probability, but the fallback is misleading and must be replaced with an explicit `NOT_EXECUTED`/status label while preserving any available BIAS.
- **Work in this execution:** no SPUTNIK functional file was changed; the single functional improvement was made in GAGARIN's `convergence_engine.py` so Sputnik's supported direction survives technical conflict and is graded as EARLY_BIAS / EARLY_SETUP / CONFIRMED.
- **SPUTNIK CI evidence:** the existing dashboard fix remains covered by the prior green Telegram/menu, ranking and runtime workflows (65, 165 and 25 smoke tests, respectively, as recorded in the preceding entry). No new SPUTNIK code test was triggered by this audit.
- **Files changed in SPUTNIK this execution:** `SPUTNIK_RESEARCH_LOG.md` only.
- **Open:** replace the `trump_tracker.py` missing-action fallback; verify complete Telegram delivery rather than relying only on individual confirmed message IDs; investigate WHITE_HOUSE/TRUTH_ARCHIVE/OGE fetch errors and missing GAGARIN handoff configuration. Do not convert internal `WAIT_CONFIRMATION` into a user-facing veto. No live quote, deploy, Telegram delivery, or real order is claimed. PAPER ONLY.

## 2026-11-01 — Cross-bot monitor and delivery audit (no SPUTNIK code change)

- **Repository state:** SPUTNIK PR #82 remains OPEN and mergeable; its handoff fix is not yet on main. Current main `trump_tracker.py:gagarin_confirmation_message()` still uses `row.get('action', 'WAIT')`. PR-head checks remain green: ranking 169 tests (run 41308564901) and item intelligence 39 tests (run 41308564692).
- **Scheduled tracker:** latest visible scheduled `trump_tracker.yml` run is `41287080980` at 2026-11-01 09:01:18Z, SUCCESS. Its logs show Telegram delivery confirmations for message IDs 623, 624 and 625, but also four attempts explicitly marked NOT confirmed because message_id was missing/invalid. This is partial delivery, not full reliability. The workflow file still declares a five-minute schedule, but no later scheduled tracker run was visible in the current run-history query; investigate the gap.
- **Polling:** Telegram polling run `41313286279` at 13:51:33Z completed SUCCESS. It processes inbound updates; it is not evidence of an outgoing signal delivery.
- **Source health:** the tracker log still reports OSError for WHITE_HOUSE, TRUTH_ARCHIVE and OGE, plus SEC HTTP 403 and White House RSS HTTPError. Other cached/public items were still rendered. These errors remain open.
- **No change this execution:** SPUTNIK functional code was not modified; the single functional improvement was made in GAGARIN. No new SPUTNIK tests were run by this audit and no deployment is claimed.
- **Open:** merge/integrate PR #82 after review; remove the main-branch WAIT fallback; investigate schedule gap and source errors; reduce unconfirmed Telegram attempts; verify a live delivery only through API `ok=true` and positive `message_id`. PAPER ONLY; no real orders.



## 2026-11-01 — Prevent false D-L-A confirmation in the SPUTNIK → GAGARIN handoff

- **Finding:** the handoff formatter inferred `SETUP CONFIRMED` from legacy action labels `PAPER_ENTRY` or `PAPER_SIGNAL`. GAGARIN's `engine/cloud_api_status.py` instead maps a `PAPER_SIGNAL` to EARLY_SETUP only when fresh setup inputs exist (otherwise EARLY_BIAS), and only a fresh validated `PAPER_ENTRY` can be CONFIRMED.
- **Change:** preserve an explicit valid GAGARIN setup stage. If the setup field is absent/invalid, default to EARLY_BIAS; infer CONFIRMED only when both `action=PAPER_ENTRY` and `trade_paper=ENTRY_AUTHORIZED_PAPER_ONLY` are explicitly present. The formatter is display-only and never submits an order.
- **Files:** `trump_tracker.py`; `tests/test_gagarin_confirmation_message.py`; this log.
- **Regression tests added:** legacy WAIT with LONG; missing action with SHORT; unsupported direction to NEUTRAL; PAPER_SIGNAL without setup remains EARLY_BIAS; explicit CONFIRMED stage is preserved; confirmation may be inferred only from explicit validated PAPER authorization.
- **Commits:** implementation commit recorded by the preceding branch update; test commit `1bc90a83355a202d1d30bd0bf05283515ec428c6`; final documentation commit follows.
- **Verification:** updated PR branch CI must pass before merge. Earlier PR-head checks (169 ranking tests and 39 item-intelligence tests) predate this refinement and are not claimed as verification of the new tests.
- **Open:** PR #82 was rebased onto current main after main advanced; it must be reopened and its updated CI verified. WHITE_HOUSE/TRUTH_ARCHIVE/OGE fetch reliability, full Telegram delivery, independent same-contract futures sources, and the real 100-setup out-of-sample journal remain open. PAPER ONLY.


### CI verification — D-L-A handoff provenance correction

- **PR head tested:** `6602742a810de9aec13d059cae4f01d30ecb5946`.
- **Ranking/full test workflow:** run `41321818062` — SUCCESS, `Ran 171 tests in 3.754s`. All six tests in `tests/test_gagarin_confirmation_message.py` ran and passed.
- **Item-intelligence workflow:** run `41321818168` — SUCCESS, `Ran 39 tests in 0.037s`.
- **Coverage verified:** a legacy WAIT no longer hides supported LONG/SHORT; unsupported direction is NEUTRAL/NO_DIRECTION; PAPER_SIGNAL alone does not imply CONFIRMED; explicit setup and explicit validated PAPER authorization are preserved separately.
- **Runtime warning:** both CI logs still show OSError for WHITE_HOUSE, TRUTH_ARCHIVE and OGE fetches. These did not fail the two workflows, but live source availability remains unverified.
- **Deployment / delivery:** no live GAGARIN handoff, Telegram message, quote, deployment or order was performed or verified. PAPER ONLY.


### Merge verification — SPUTNIK → GAGARIN handoff state contract

- **PR:** #82 merged successfully at 2026-11-01 15:34:33Z.
- **Merge commit:** `cfb0cea6180b1cf90b8fd974aa68908b7c2fee19`.
- **Main-branch readback:** `trump_tracker.py:gagarin_confirmation_message()` now renders separate BIAS / SETUP / TRADE PAPER fields; the missing-action `WAIT` fallback is absent. `tests/test_gagarin_confirmation_message.py` is present on main with six regression tests.
- **CI on final PR head before merge:** ranking/full suite run `41321818062` — SUCCESS, 171 tests; item-intelligence run `41321818168` — SUCCESS, 39 tests. All six new handoff tests were explicitly visible as passing in the ranking log.
- **Post-merge caveat:** the connector returned no PR-triggered workflow runs for the merge commit; the successful checks above are the final PR-head checks, not a separately verified post-merge push run. No production deployment or live Telegram handoff is claimed.
- **Open:** WHITE_HOUSE/TRUTH_ARCHIVE/OGE still emitted OSError in CI; live source availability remains unverified. Multi-source same-contract futures verification, full Telegram delivery, and the real 100-setup out-of-sample journal remain open. PAPER ONLY.



## 2026-11-01 — Audit OpenBB/GDELT candidates and SPUTNIK source coverage

- **Public-system study — OpenBB V5:** the official V5 documentation describes one provider package/namespace per data source (including `obb.sec`) and common Python, REST, MCP and Workspace surfaces. The current V5 documentation states Apache-2.0; V4 and earlier remain AGPL-3.0. Crucially, the software license does not grant rights to redistribute provider data, which remains subject to each source's own terms. No OpenBB dependency was added: it would increase the dependency surface, and free access/terms for each SEC or market-data provider have not been independently verified.
- **Public-data study — GDELT Project:** the official project describes an event database with 300+ event categories, actor coding and geographic fields, updated on a 15-minute cycle and extending back to 1979. Its event taxonomy could help discover policy/geopolitical developments and create historical event-study cohorts, but it is a news-derived secondary dataset, not primary proof or a market-direction signal. The official data page also distinguishes event occurrence from media discovery/reporting date; preserve both timestamps rather than treating publication/discovery time as event time. GDELT Cloud is a separate API product and is not assumed to be free.
- **Repository audit:** `sputnik_public_feed_monitor.py` currently declares White House and Trump Truth Archive item feeds plus the OGE public listing; `trump_tracker.py` contains SEC filing retrieval, including Form 4 processing. Repository code search found no GDELT integration. No new source was wired in this execution because its exact free endpoint, access terms, event-time mapping, attribution quality and runtime reliability have not yet been validated end-to-end.
- **SPUTNIK state:** the merged PR #82 handoff remains on main at `cfb0cea6180b1cf90b8fd974aa68908b7c2fee19`; `gagarin_confirmation_message()` preserves BIAS / SETUP / TRADE PAPER and no longer defaults a missing action to WAIT. No duplicate code change was made.
- **Validation:** documentation/repository audit only; no SPUTNIK source or test file changed and no new SPUTNIK tests were run. Existing CI evidence for the merged handoff remains 171 ranking tests and 39 item-intelligence tests, both SUCCESS on PR head as recorded above. No live White House/Truth Archive/OGE/SEC request, Telegram send, production deployment or trade is claimed.
- **Open:** previous monitor logs still report WHITE_HOUSE/TRUTH_ARCHIVE/OGE `OSError`, SEC 403 and partial Telegram acknowledgements. Re-test source health with safe timeouts/backoff; verify every send only on Telegram `ok=true` plus positive `message_id`; evaluate GDELT Project as a separately timestamped secondary discovery source only after endpoint and usage-term verification. PAPER ONLY.

## 2026-11-01 — Reject ambiguous publication timestamps in SPUTNIK feeds

- **Public-system study:** GDELT 2.0's official event codebook distinguishes the event's calendar date from its DATEADDED 15-minute record timestamp; the event-date field is daily-resolution and must not be mistaken for precise publication/observation time. Qlib's point-in-time documentation explains how using data versions unavailable at the historical decision time creates look-ahead leakage. Applicable lesson: preserve timestamp semantics and never manufacture an offset for historical ordering.
- **Finding:** trump_tracker.py:_parse_public_item_timestamp() previously assigned UTC to timezone-naive ISO/RFC timestamps (including date-only values). This silently converted an ambiguous source time into a precise UTC instant, affecting feed-age checks, catalyst ordering and event-study reproducibility.
- **Implemented:** timezone-aware source timestamps are still normalized to UTC; timestamps without an explicit timezone now return None and cannot become item-level market catalysts. Original raw publication text remains preserved in the finding when accepted. No event-occurrence time is inferred from publication time.
- **Files:** trump_tracker.py; tests/test_sputnik_item_intelligence.py; this log.
- **Commits:** code 830cc0cfa5a05ad94f775d42ae3975d305cd95e9; regression tests 5ae3006984385c58a81637edc8c7a0070455f6f8; documentation commit recorded below.
- **Regression coverage:** naive ISO datetime rejected; date-only value rejected; explicit +02:00 offset normalized to the correct UTC instant; an RSS item with a timezone-less timestamp is rejected by the feed-intelligence path. Existing timezone-explicit RSS fixtures remain eligible.
- **Validation:** GitHub Actions on initial PR head `6cc12240a2f41ca26ea356999bc527e5d7155fa3`: SPUTNIK ranking run `41336578490` — SUCCESS, 172 tests in 3.535s; item-intelligence run `41336578456` — SUCCESS, 40 tests in 0.036s. Both jobs completed successfully and include the new regressions. The CI logs also show expected offline-source `OSError` diagnostics for WHITE_HOUSE/TRUTH_ARCHIVE/OGE and test-only Telegram acknowledgements; these are not live source or delivery verification. No live feed, market quote, Telegram delivery, production deployment or trade was performed. PAPER ONLY.
- **Open:** sources that publish date-only or timezone-naive values remain unqualified source material, not timestamped catalysts; add an explicit source timezone mapping only when the publisher documents it. Continue verifying White House/Truth Archive/OGE/SEC source health and the real out-of-sample event study.
- **References:** GDELT Event Codebook V2.0 (https://data.gdeltproject.org/documentation/GDELT-Event_Codebook-V2.0.pdf); Qlib point-in-time documentation (https://qlib.readthedocs.io/en/latest/component/data.html).
