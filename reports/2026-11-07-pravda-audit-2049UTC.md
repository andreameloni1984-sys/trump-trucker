# PRAVDA — Audit indipendente SPUTNIK / GAGARIN

**Cut-off:** 2026-11-07 20:49:29 UTC (21:49:29 Europe/Rome)  
**Modalità:** PAPER ONLY. Verifica in sola lettura dei bot; aggiornato esclusivamente il ledger/report PRAVDA. Nessuna modifica al codice, strategia, filtri, punteggi o rischio.

## 1. Sintesi esecutiva

- Nessun trade con fill verificato e nessun outcome SL/TP verificabile.
- Il run GAGARIN direttamente ispezionato è concluso SUCCESS ma tutte le commodity risultano `MARKET_CLOSED`, con quote stale e senza livelli operativi.
- L'ultimo run SPUTNIK con log completo disponibile è SUCCESS e ha inviato due messaggi GOLD `NO_DIRECTION`; non sono segnali LONG/SHORT.
- Un commit SPUTNIK delle 20:07 UTC ha aggiornato `sputnik_state.json` e aggiunto due item RSS e uno snapshot page-level. I due item sono stati registrati come intelligence non direzionale, non come segnali.
- Non è disponibile in questa sessione un endpoint per enumerare integralmente tutte le GitHub Actions recenti. Di conseguenza, gli ultimi run citati sono gli ultimi log direttamente interrogabili, non una certificazione che non esistano run successivi.

## 2. GitHub Actions: run direttamente verificati

| Bot / funzione | Run | Esito | Osservazione |
|---|---:|---|---|
| SPUTNIK monitor | [#42388887315](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42388887315) | SUCCESS | 15:57:48–15:58:04 UTC; due messaggi GOLD NO_DIRECTION |
| SPUTNIK Telegram polling | [#42387284361](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42387284361) | SUCCESS | 15:37 UTC; Pending updates=0; non è una scansione di mercato |
| GAGARIN monitor | [#42386803148](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42386803148) | SUCCESS | 15:31:37–15:31:58 UTC; tutte le commodity MARKET_CLOSED |
| GAGARIN Telegram polling | [#42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549) | FAILURE | 00:16:30 UTC; API 409, webhook attivo e polling incompatibile |

Gli ultimi due monitor sono stati ispezionati tramite job e log; entrambi restituiscono zero artifact Actions. Il polling GAGARIN fallito è avvenuto sabato alle 00:16 UTC, fuori dal cron dichiarato `*/5 7-21 * * 1-5`. La PR #175 propone la gestione esplicita del conflitto senza cancellare il webhook, ma non è integrata.

### Cadenze dichiarate su main

- SPUTNIK `.github/workflows/trump_tracker.yml`: `2-59/5 * * * *`, ogni cinque minuti; il workflow scrive `sputnik_state.json` su main.
- GAGARIN `.github/workflows/gagarin-monitor.yml`: `*/15 * * * *`, ogni quindici minuti; `MONITOR_INTERVAL_MINUTES=15`.
- SPUTNIK daily summary: `0 6 * * *`.
- GAGARIN daily summary: `15 6 * * *`.
- GAGARIN Telegram polling: `*/5 7-21 * * 1-5`.

La configurazione cron non dimostra che ogni esecuzione sia partita o abbia completato la scansione. Per questo rapporto non attribuisco una cadenza effettiva senza la cronologia completa dei run.

## 3. SPUTNIK

### Ultimo monitor con log completo: #42388887315

- Job SUCCESS.
- SEC: HTTP 403 e cooldown; White House RSS: HTTPError.
- Un finding TRUTH_ARCHIVE page-level, senza titolo o timestamp individuale; non identifica un post specifico.
- GOLD: mapping configurato `GC=F`, ma ticker runtime/provider/timestamp della quotazione e scadenza esatta non esposti.
- Bias NEUTRAL, tecnica 5m non disponibile, `NO_DIRECTIONAL_NEWS`, score 70 e decisione WATCH.
- Entry, SL, TP e ATR assenti; `NOT_EXECUTED`.
- Telegram API ha confermato i messaggi #721 e #722 (round-trip rispettivamente 738 ms e 485 ms). Sono notifiche NO_DIRECTION, non operazioni. Il message_id 731 appare nei test della stessa run e non è contato come invio produttivo.

### Nuovo stato persistito alle 20:07 UTC

Il commit [8c5dd9d](https://github.com/andreameloni1984-sys/trump-trucker/commit/8c5dd9d2173e999dfb3259a4d0916c807d953e67), creato da SPUTNIK Bot alle 20:07:20 UTC, aggiorna `sputnik_state.json`. Il diff aggiunge:

1. `b5bcbe95005519e7f53462af`: item PUBLIC_RSS pubblicato alle 14:33:02 UTC, titolo generico “Quote post from November 7, 2026”, dominio MEDIA, classificazione OTHER / NO_ANALOGUE. Rilevato alle 20:07:18.941 UTC: ritardo circa **5h34m**.
2. `70079fc92de56f04887479dd`: item PUBLIC_RSS pubblicato alle 17:45:04 UTC, dichiarazione politica su minacce di impeachment e richiesta di indagine DOJ; domini AI_TECH/MEDIA, classificazione OTHER / NO_ANALOGUE. Rilevato alle 20:07:18.941 UTC: ritardo circa **2h22m**.
3. `ecd1dce1bc8c996f35efe329`: snapshot della homepage TRUTH_ARCHIVE, senza titolo e data individuale; `GEOPOLITICAL_ESCALATION` assegnato per analogia ma `historical_matches=[]` e `NO_ANALOGUE`.

I due item RSS e lo snapshot non contengono un catalizzatore commodity individuale con direzione verificata, prezzo, entry, SL, TP o ATR. Il commit prova un aggiornamento dello stato, ma non fornisce un run ID/log associato né prova di invio Telegram per questi item.

### Riepiloghi Telegram

- SPUTNIK Daily Summary [#42371347665](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42371347665): cron 06:00 UTC, avvio 12:11:08 UTC (ritardo **6h11m08s**); API ha confermato message_id=720 alle 12:11:16.861 UTC. Il corpo non è conservato, quindi non attribuisco strumento o direzione.
- Il workflow main usa `confirmed_message_id` e richiede `ok=true` e `result.message_id`; l'ACK API è dimostrato, non la visualizzazione sul dispositivo.

### Correzioni SPUTNIK già aperte

- [PR #144 — persistenza fuori da main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN, non merged; 2 workflow CI consultati SUCCESS.
- [PR #148 — stop alle raccomandazioni ripetute senza nuovo catalizzatore](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN, non merged; 2 workflow CI consultati SUCCESS.

Main continua a persistere lo stato su `sputnik_state.json`; le correzioni proposte non sono attive finché le PR non vengono integrate.

## 4. GAGARIN

### Ultimo monitor con log completo: #42386803148

- Job SUCCESS; `PAPER_TRADING_ONLY=1`; `MONITOR_INTERVAL_MINUTES=15`.
- `DATABASE_URL` è vuoto nei log del run.
- Otto commodity risultano `MARKET_CLOSED`; Yahoo segnala quote stale:
  - Grano, Mais e Soia: circa 73.013 secondi, cioè 20h17m.
  - Oro, Argento, Rame, Brent e WTI: circa 63.412 secondi, cioè 17h37m.
- EUR/USD e GBP/USD sono contesto FX ausiliario BiQuote, anch'essi stale.
- I timestamp puntuali delle quotazioni, i ticker effettivamente risolti, il market type e le scadenze non sono esposti nel log. Non è possibile associare prezzi/candele successive allo stesso contratto.

Argento è l'unico candidato con direzione LONG: probabilità 59, quality 49,5, confidence 32. Lo stato è PAPER_WATCH ed è bloccato da LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, CONFIDENCE_FAIL e FINAL_CONFLUENCE_FAIL. Entry, SL, TP e ATR sono assenti. Tutti gli altri strumenti non hanno direzione/setup valido.

Telegram API ha confermato il board #3715 alle 15:31:54.641 UTC, round-trip 489 ms. Il corpo del board non è conservato: non attribuisco al messaggio un singolo strumento o una direzione. Il run riporta:
- Recorded entries: 0
- Updated open outcomes: 0
- New feedback signals: 0
- New additional live forecasts: 0
- signals=0, open=0, closed=0; win_rate e avg_R N/D

### Journal e storico legacy

- `journal.csv`: 11 righe datate 17 ottobre, tutte “nessun segnale”.
- `paper_trade_log.csv`: ticket legacy WTI P0001, LONG, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55.
- `data/paper_open.json` contiene lo stesso P0001: è un solo ticket duplicato fra due artefatti, non due trade.
- `position.json`: Heating Oil LONG, entry 4,8844, SL 4,5418, TP1 5,4473, TP2 5,6284, TP3 5,882; apertura 15 settembre. Mancano provider, timestamp quote, contratto/scadenza e prova di fill.
- `gagarin_feedback.csv`: assente dal repository consultato.
- `DATABASE_URL` vuoto: persistenza condivisa del journal/feedback fra run non dimostrata.
- `commodities_prediction_log.json`: 981 record, tutti con ID univoco; ultimo record creato il 15 settembre 2026 alle 15:45:04 UTC. Status: 945 PENDING e 36 NEUTRALE; operational_signal: 960 WAIT, 15 LONG, 6 senza campo. PENDING/LONG non dimostrano esecuzione.

WTI P0001 e Heating Oil restano ESITO NON VERIFICABILE. Non sono stati confrontati spot, futures continui o scadenze diverse.

### Riepilogo giornaliero e PR GAGARIN

- Daily Summary [#42374841686](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42374841686): cron 06:15 UTC, avvio 12:58:56 UTC (ritardo **6h43m56s**). Il workflow main stampa “Summary sent” dopo la risposta HTTP, ma non verifica `ok=true` né `result.message_id`; nessuna accettazione Telegram è dimostrata.
- [PR #190](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/190), ACK del daily summary: OPEN, non merged; 5 workflow CI consultati SUCCESS.
- [PR #175](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175), conflitto webhook/polling: OPEN, non merged; 5 workflow CI consultati SUCCESS.
- [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192), identità contratto e outcome: OPEN, non merged; 6 workflow CI consultati SUCCESS.
- [PR #181](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/181), log della provenienza esatta della quotazione: OPEN, non merged; 6 workflow CI consultati SUCCESS.
- [PR #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202), persistenza journal PostgreSQL: OPEN/DRAFT, non merged; 6 workflow CI consultati SUCCESS.
- [PR #222](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222), rimozione del veto intraday `session_ok`: OPEN/DRAFT, non merged; 6 workflow CI consultati SUCCESS. I check verdi non attivano la correzione su main.
- [PR #30](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/30), paniere a otto commodity/esclusione Argento: OPEN/DRAFT, mergeable=false; 2 workflow CI consultati FAILURE (SOYUZ GAGARIN Tests ed Execution Layer), gli altri 3 SUCCESS. Argento è ancora nel runtime del run esaminato.

## 5. Ledger PRAVDA e statistiche

Ledger aggiornato in append-only con i tre nuovi record intelligence del commit SPUTNIK delle 20:07. Nessuna riga preesistente è stata sostituita.

- File: [pravda-signal-ledger-2026-11-07.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-07.csv)
- Blob SHA dopo aggiornamento: `8a6f7ad5dcbe4a3e1f10a3afb879af7e7578bcef`.
- Record totali: **61** — SPUTNIK **17**, GAGARIN **44**.
- `audit_signature` uniche: **61/61**.
- `source_record_id` unici: **61/61**.
- Duplicati: **0**.
- Outcome `ESITO_NON_VERIFICABILE`: **29**.
- Record `NON_TRADE`: **32**.
- Fill verificati: **0**.
- TP verificati: **0**.
- SL verificati: **0**.
- Campione di trade con outcome verificabile: **0**; win rate e Average R: **N/D**.

I tre record aggiunti sono due item PUBLIC_RSS e uno snapshot page-level, tutti classificati NON_TRADE. Nessuno è stato trasformato in un segnale operativo. I ticket WTI duplicati fra artefatti GAGARIN sono conteggiati una sola volta.

## 6. Difetti dimostrati e priorità di verifica

1. GAGARIN non conserva nel log runtime ticker risolto, timestamp quote e scadenza esatta; PR #181 propone telemetria, PR #192 propone identità/outcome esatti. Entrambe non integrate.
2. GAGARIN non dimostra persistenza condivisa: DATABASE_URL vuoto e feedback CSV assente; PR #202 non integrata.
3. Il polling GAGARIN ha un 409 webhook/polling documentato; PR #175 non integrata.
4. Il daily summary GAGARIN non verifica l'ACK Telegram; PR #190 non integrata.
5. Il veto `session_ok` resta su main finché PR #222 non viene integrata, benché i sei workflow CI consultati siano SUCCESS.
6. Argento resta nel runtime; PR #30 è draft, non mergeable e ha due workflow CI falliti.
7. SPUTNIK ha due item RSS rilevati con ritardo di circa 2h22m e 5h34m; entrambi OTHER/NO_ANALOGUE, non catalizzatori direzionali.
8. La persistenza SPUTNIK su main è ancora attiva; PR #144 non integrata. La soppressione delle raccomandazioni ripetute proposta da PR #148 non è attiva su main.

## 7. Prossimo controllo

- Acquisire l'elenco completo delle GitHub Actions recenti e distinguere monitor di mercato, polling, daily summary, fetch driver e CI.
- Al prossimo run GAGARIN in sessione aperta, verificare timestamp quote, età, ticker risolto, market type e scadenza esatta prima di valutare qualsiasi outcome.
- Per SPUTNIK, verificare che ogni nuovo finding abbia URL item-level, titolo, timestamp di pubblicazione e una classificazione non basata soltanto su una homepage.
- Ricontrollare lo stato delle PR citate e verificare solo le correzioni effettivamente integrate su main.
- Non attribuire outcome a nessun ticket senza prova di fill e sequenza cronologica di candele dello stesso identico contratto.

**Sicurezza:** nessuna modifica al codice dei bot, nessun cambio di strategia/filtri/punteggi/rischio, nessun merge/deploy, nessun segreto o impostazione Render toccati, nessun ordine reale. Nessun accesso o confronto Trading212 utilizzato. PAPER ONLY.
