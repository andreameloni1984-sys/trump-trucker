# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-06 15:31 UTC (16:31 Europe/Rome)**

## Sintesi

- Nessun nuovo collector di mercato SPUTNIK dopo [#42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412), avviato alle 11:31:39 UTC.
- Nessun nuovo monitor prezzi GAGARIN dopo [#42203497432](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42203497432), avviato alle 10:32:52 UTC.
- Distinti dai monitor: SPUTNIK Daily Summary #42226158074; GAGARIN Daily Summary #42232309653, FETCH DRIVERS #42235888213 e Telegram Polling #42236174265.
- Nuovo riscontro CI: SPUTNIK PR #143 ha due suite verdi, ma resta OPEN; GAGARIN PR #220 fallisce 4 test e ne passa 568.
- Ledger invariato: 32 record, 32 firme uniche, zero duplicati.
- Nessun fill, TP o SL verificabile. Win rate e average R: N/D.

## 1. GitHub Actions e frequenza

Le liste sono state controllate sulle 100 esecuzioni più recenti di ciascun repository, distinguendo nome/percorso del workflow e tipo di evento. Nei risultati più recenti non compare un run di mercato successivo a quelli sotto indicati.

### SPUTNIK
- Ultimo collector: [#42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412), workflow `.github/workflows/trump_tracker.yml`.
- Avvio 11:31:39 UTC; conclusione 11:31:53 UTC; SUCCESS.
- Cut-off 15:31 UTC: circa 3h59m senza nuovo collector.
- Cron su main: `2-59/5 * * * *`.
- Il log del collector registra SEC HTTP 403 con cooldown 21600s, White House RSS HTTPError, scansione pubblica con `findings=0`, zero filing e zero correlazioni pubbliche.
- Il workflow dichiara Telegram polling disabilitato nel collector perché esiste un listener dedicato.
- Persistenza del file `sputnik_state.json` eseguita con push su `main`; la PR #141 per spostare lo stato su branch dedicato resta aperta.

Altri run:
- [Daily Summary #42226158074](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42226158074), 13:31:21 UTC: riepilogo, non collector.
- [Telegram Polling #42206505491](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42206505491), 10:56:51 UTC: polling, non collector.

### GAGARIN
- Ultimo monitor: [#42203497432](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42203497432), workflow `.github/workflows/gagarin-monitor.yml`.
- Avvio 10:32:52 UTC; conclusione 10:33:10 UTC; SUCCESS.
- Cut-off 15:31 UTC: circa 4h58m senza nuovo monitor.
- Cron su main: `*/15 * * * *`.
- Il workflow dichiara PAPER ONLY e lascia la persistenza dei journal disabilitata in attesa di storage privato verificato.

Altri run:
- [Daily Summary #42232309653](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42232309653), 14:15:30 UTC: riepilogo.
- [FETCH DRIVERS #42235888213](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42235888213), 14:39:35 UTC: snapshot driver.
- [Telegram Polling #42236174265](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42236174265), 14:41:31 UTC: polling, non monitor prezzi.

La causa dei gap di schedulazione non è determinata; non attribuisco il ritardo a una causa ipotetica.

## 2. SPUTNIK — GOLD LONG già registrato

Il log di #42210907412 conferma:
- Messaggio analisi #707 generato alle 11:31:48.566 UTC; API round-trip 549 ms; message_id 707.
- Messaggio CFD #708 generato alle 11:31:48.567717 UTC; API round-trip 437 ms; message_id 708.
- I due messaggi sono due fasi dello stesso candidato, non due segnali distinti.

Campi del candidato:
- Strumento: GOLD.
- Mapping configurato: GC=F; ticker risolto runtime non confermato.
- Mercato dichiarato: future continuo front-month; scadenza esatta UNKNOWN.
- Provider runtime e timestamp/età della quotazione: non esposti.
- Direzione preliminare: LONG.
- Entry 4075.8999; SL 4074.2713; TP1 4077.5285; TP2 4079.1570; ATR 1.0857.
- Score 70; stato `EARLY_SETUP / NOT_EXECUTED`.

Incoerenza: messaggio #707 descrive LONG tecnico a 5m e momentum +0,064% in 15m, mentre #708 riporta tecnica `NOT_ASSESSED`, D-L-A `NEUTRAL / NO_DIRECTION`, swing con massimi/minimi decrescenti ed EMA non univoche. Nessuna notizia direzionale verificata. Narwhal non configurato; indipendenza delle componenti SILV non dimostrata. Il messaggio avverte che i livelli sul continuo senza scadenza non sono utilizzabili.

Il log scrive “delivery confirmed”, ma i dati verificano solo l'ACK dell'API Telegram e l'ID messaggio; non la consegna sul dispositivo. Non c'è prova di fill PAPER.

Esito: `ESITO_NON_VERIFICABILE`. Nessun timestamp quote e nessuna candela successiva dello stesso ticker/contratto/scadenza. Non usare spot o un altro future per assegnare TP/SL.

## 3. GAGARIN — ultimo monitor e candidati

Nel run #42203497432 tutte le otto commodity risultano stale su Yahoo:
- Grano 622,4 s
- Brent 604,3 s
- WTI 601,2 s
- Oro 614,5 s
- Argento 606,0 s
- Rame 607,1 s
- Mais 622,4 s
- Soia 664,5 s

Le età delle quote sono presenti, ma i timestamp assoluti della quotazione e la scadenza del contratto non sono sufficientemente esposti per un audit di outcome sul contratto esatto. EUR/USD e GBP/USD sono presenti come contesto Forex non operativo e risultano LIVE su BiQuote (187,0 e 187,5 s).

Candidati:
- Grano SHORT: probabilità 63, qualità 52,5, confidenza 35, `PAPER_WATCH`; blocchi `LIVE_DATA_NOT_FRESH`, `TRIGGER_NOT_CONFIRMED`, `TRIGGER_DIRECTION_MISMATCH`, `RR_FAIL`, `FINAL_CONFLUENCE_FAIL`.
- Brent, WTI, Oro, Argento, Rame, Mais e Soia: `PAPER_WATCH`, senza livelli operativi completi; tra i blocchi figurano dati stale, setup/trigger non validi e entry/stop/target/ATR mancanti.
- GBP/USD e EUR/USD: `CONTESTO FX — NON OPERATIVO`.

Risultato: nessuna entrata autorizzata; recorded entries 0; open outcomes aggiornati 0; nuovi feedback 0; nuove previsioni live aggiuntive 0; `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D`.

Il riepilogo Telegram #3701 ha avuto API ACK con round-trip 509 ms; non è un trade e non prova consegna al dispositivo.

## 4. Telegram Polling GAGARIN — conflitto webhook

[Run #42236174265](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42236174265), job `127954240667`, fallisce dopo:
- token presente;
- diagnostica Telegram OK, bot identificato;
- `getUpdates` rifiutato con API error 409: webhook attivo, polling non consentito.

La [PR #175](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175) esiste ma resta OPEN, non integrata. Il difetto è del runner polling; non prova da solo un guasto del monitor prezzi. Evidenza già segnalata nel [commento PRAVDA #6688546557](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175#issuecomment-6688546557).

## 5. CI recente: nuove PR

### SPUTNIK PR #143
[PR #143 — Fix SPUTNIK short-token false domain labels](https://github.com/andreameloni1984-sys/trump-trucker/pull/143), head `0fadd3edd698744fd545b15ce244fe74af8f4228`, OPEN e non merged.
- [Ranking tests #42243656376](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42243656376): SUCCESS.
- [Item intelligence tests #42243656439](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42243656439): SUCCESS.
I test verdi provano il branch, non l'attivazione su main. Riscontro PRAVDA pubblicato: [commento #6688603099](https://github.com/andreameloni1984-sys/trump-trucker/pull/143#issuecomment-6688603099).

### GAGARIN PR #219 e #220
- [PR #219](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219), head `8c3192fc33701f0a6484a3f4dbc872f061cf6648`, OPEN/non merged. Il run [#42239182472](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42239182472) aveva 21 failed e 549 passed.
- [PR #220](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/220), head `1b2127da35e88310b5cfd272e7b753bbb0ac8cb3`, OPEN/DRAFT e basata sulla #219. Il run [#42243611787](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42243611787) ha **4 failed, 568 passed**.

I quattro test falliti nel run #42243611787:
1. `test_all_enabled_commodities_are_scanned_outside_session_windows`: ancora si aspetta EUR/USD e GBP/USD.
2. `test_all_ten_active_symbols_have_explicit_free_market_basis_routes`: ancora si aspetta il paniere a dieci strumenti.
3. `test_lubjanka_interception_is_not_dropped_by_telegram_top_ten_limit`: attesi 10 alert, ottenuti 0.
4. `test_pattern_analysis_is_calculated_once_per_alert`: attesa una chiamata pattern, ottenute 0.

I primi due test sono aspettative obsolete rispetto allo scopo di rimuovere il Forex; gli ultimi due sono regressioni separate su alert/LUBJANKA e pattern analysis e non vanno liquidate come conseguenza della rimozione FX. Nota PRAVDA pubblicata: [commento #6688602424](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/220#issuecomment-6688602424).

PR correlate ancora aperte:
- [#175 — webhook/polling](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175)
- [#181 — quote provenance](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/181)
- [#198 — restore ranking baseline](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/198)
- [#212 — eight-commodity universe](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/212)
- [#218 — reject stale BiQuote CFD](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/218)
- [#219 — remove FX](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219)
- [#220 — explicit quote aliases](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/220)

## 6. Journal, feedback e ledger

GAGARIN main:
- `journal.csv`: 11 righe dati, tutte del 17 ottobre con `nessun segnale`.
- `paper_trade_log.csv`: un WTI LONG legacy del 8 ottobre; entry 96.24, SL 89.37, TP1 103.11, TP2 106.55; provider, timestamp quote, contratto e fill mancanti.
- `data/paper_open.json`: P0001 contiene la stessa posizione WTI; non è un secondo trade.
- `position.json`: Heating Oil LONG del 15 settembre, entry 4.8844, SL 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882; provenienza incompleta.
- `commodities_prediction_log.json`: 981 record, ultimo creato 2026-09-15T15:45:04.462276Z; gli ultimi record hanno `action=COMPRA ORA` ma `status=PENDING`, quindi non provano fill.
- `gagarin_feedback.csv`: assente su main (404).
- `DATABASE_URL`: vuoto nel monitor; persistenza DB non dimostrata.

Ledger PRAVDA:
- SHA blob `cfcd19a244cb38e0bb6549de5f191ce68277575a`.
- 32 record, 32 firme uniche, zero duplicati.
- Ultimo record GOLD LONG SPUTNIK #707/#708, già registrato una sola volta.
- Nessun nuovo segnale individuale completo da aggiungere.
- Fill verificati 0; TP verificati 0; SL verificati 0; outcome verificabili 0; win rate e average R N/D.

## 7. Prossimo controllo

1. Separare collector/monitor da summary, polling, driver snapshot e CI.
2. Verificare se parte il prossimo collector SPUTNIK e il prossimo monitor GAGARIN; il gap osservato non ha ancora una causa dimostrata.
3. Controllare la risoluzione del conflitto webhook/polling tramite PR #175.
4. Verificare la suite #220: rimuovere le aspettative FX obsolete senza perdere test LUBJANKA e pattern/exit.
5. Verificare quote commodity fresche e timestamp assoluti, ticker runtime, mercato e scadenza.
6. Attribuire TP/SL solo a candele successive dello stesso identico contratto e rispettando l'ordine temporale.

**Perimetro:** nessun codice o workflow bot modificato; nessuna strategia, filtro, score o rischio modificato; nessun merge, deploy o rerun; nessun ordine reale; nessuna modifica a secrets o Render; nessun servizio a pagamento. PRAVDA ha soltanto letto log/artefatti, aggiunto due commenti di audit su PR esistenti e creato questo documento. PAPER ONLY.
