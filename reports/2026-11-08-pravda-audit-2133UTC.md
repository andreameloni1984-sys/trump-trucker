# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 8 novembre 2026, 21:33:44 UTC (22:33:44 Europe/Rome)**

## Sintesi

Verificati i run Actions più recenti, i log integrali dei job, i workflow correnti, il ledger, i journal pubblici, l'archivio predittivo e le PR di correzione.

**Nessun nuovo record da aggiungere al ledger** rispetto all'audit delle 21:12 UTC: gli ultimi record sono già presenti (#741, #742 e #3726). Nessun fill verificato e nessun esito SL/TP valutabile.

È stata rilevata una correzione metodologica importante: nel log SPUTNIK alcune righe di errore attribuite in precedenza alle fonti di produzione (TRUTH_ARCHIVE/OGE e parte dei messaggi WHITE_HOUSE) sono stampate durante lo step di unit test, prima dell'avvio del collector. Non vanno attribuite al runtime produttivo.

## 1. Ledger PRAVDA

File: [pravda-signal-ledger-2026-11-08.csv](pravda-signal-ledger-2026-11-08.csv)

- Blob SHA: `251d38a306eb3d6ddd3bced8e77849a09b622918`
- Record: **94**
- SPUTNIK: **42**
- GAGARIN: **52**
- Firme uniche: **94**
- Source ID unici: **94**
- Duplicati firma/source ID: **0**
- `NON_TRADE`: **65**
- `ESITO_NON_VERIFICABILE`: **29**
- Fill verificati: **0**
- SL verificati: **0**
- TP verificati: **0**

I conteggi descrivono record auditati, non operazioni. I 29 record non verificabili non sono 29 trade. Win rate, average R e total R restano **N/D**.

### Campi non valorizzati o placeholder nel ledger

Conteggi su 94 righe; i placeholder `NOT_APPLICABLE` sono inclusi e non implicano un difetto per i record informativi:

| Campo | Righe non valorizzate/placeholder |
|---|---:|
| generated_at_utc | 6 |
| sent_at_utc | 32 |
| instrument | 7 |
| ticker | 61 |
| market_type | 77 |
| contract_expiry | 94 |
| provider | 46 |
| quote_timestamp_utc | 92 |
| direction | 11 |
| entry / SL / TP1 | 66 ciascuno |
| ATR | 82 |

Le lacune impediscono di ricostruire una parte significativa dei record come strumenti/contratti valutabili.

### Ultimi record già presenti

- SPUTNIK #741 — `run:42520937991/telegram_message:741`, GOLD, WATCH / NO_DIRECTION, NON_TRADE.
- SPUTNIK #742 — `run:42520937991/telegram_message:742`, GOLD, NOT_EXECUTED / NO_DIRECTION, NON_TRADE.
- GAGARIN #3726 — `run:42521363444/telegram_watch_pre_alert:3726`, WATCH pre-alert, strumento e direzione non attribuibili, NON_TRADE.

#741 e #742 sono due messaggi della stessa analisi GOLD, non due setup. Nessuna riga aggiunta in questo audit.

## 2. SPUTNIK — run produttiva #291

[GitHub Actions #42520937991](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42520937991) — evento schedule, SUCCESS. Avvio 20:35:50 UTC; job concluso alle 20:36:03 UTC.

### Separazione tra test e runtime

Il job esegue prima lo step `Run SPUTNIK Telegram delivery regression tests` e soltanto dopo `Run SPUTNIK (Render-independent)`.

Le righe:
- `source WHITE_HOUSE unavailable: OSError`
- `source TRUTH_ARCHIVE unavailable: OSError`
- `source OGE unavailable: OSError`
- `GAGARIN handoff disabled`
- `GAGARIN confirmation received`

compaiono alle 20:35:55.948–20:35:55.951 UTC, **prima** del timestamp di avvio runtime `20:35:56.053060Z`. Sono output dello step di test/fixture, non evidenza del comportamento produttivo. Le righe di test che menzionano Telegram round-trip 0 ms e message_id=731 non sono invii produttivi.

### Evidenze del vero runtime

Dopo `SPUTNIK: run started`:
- SEC CIK 0001849635: HTTP 403; cooldown 21.600 secondi; filing=0.
- Estrazione transazioni: 0.
- White House RSS `https://www.whitehouse.gov/feed/`: HTTPError.
- Scansione intelligence pubblica: 1.066 ms; findings=0.
- Forwarding GAGARIN: 0 ms.
- Filing trovati: 0; nuove operazioni documentate: 0; nuove correlazioni pubbliche: 0.
- Analisi GOLD: bias NEUTRAL; tecnica 5m UNAVAILABLE; `NO_DIRECTIONAL_NEWS`; WATCH; nessuna tesi LONG/SHORT sostenibile.

Telegram API:
- #741 alle 20:35:58.6659378 UTC, round-trip 497 ms, API `delivery confirmed`.
- #742 alle 20:35:58.6670675 UTC, round-trip 444 ms, API `delivery confirmed`.

Gli ACK e i message_id provano l'accettazione API, non la visualizzazione sul dispositivo.

#742 riporta `NOT_EXECUTED`, score 100/100 e nessuna direzione. Il titolo lo presenta come CFD, mentre il corpo identifica un future continuo front-month senza scadenza esatta verificata. Ticker risolto, provider, timestamp/età della quota, prezzo di riferimento, entry, SL, TP e ATR non sono disponibili. Score 100 non equivale a validità operativa.

### Polling

[SPUTNIK Telegram Polling #51](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42520176845) — avvio 20:27:04 UTC, SUCCESS; `Pending updates: 0`. Il polling non certifica la consegna dei messaggi #741/#742 al dispositivo.

### PR SPUTNIK

- [PR #149](https://github.com/andreameloni1984-sys/trump-trucker/pull/149): MERGED il 8 novembre alle 20:25:23 UTC; rimosso il gate a ora fissa per il daily brief. Non modifica la direzione dei segnali.
- [PR #147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN, mergeable; confronto diretto main/head: **1 ahead / 6 behind**. Head `8b27db788421fb90e18f4435e593a64aa88d51fc`; CI sullo stesso head: ranking #645 e item-intelligence #256, entrambi SUCCESS. La correzione rimuove il handoff GAGARIN, ma non è su main; il main corrente contiene ancora la funzione di handoff e le variabili del workflow.
- [PR #145](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN, mergeable; **1 ahead / 8 behind**. Head `25d27e8468a1d22dd71ed4114138b57bee1c512b`; ranking #644 e Telegram menu #297 hanno superato rispettivamente 186 e 68 test. La diagnostica Yahoo/provenienza non è su main.

La correzione metodologica sui log dei test è già stata registrata nei commenti esistenti della PR #147; non è stato aggiunto un commento duplicato.

## 3. GAGARIN — run produttiva #170

[GitHub Actions #42521363444](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42521363444) — schedule, SUCCESS. Avvio 20:41:00 UTC; timestamp interno del motore 20:41:12.654 UTC.

### Quotazioni e decisioni

Dieci strumenti analizzati:
- 8 commodity: YAHOO;
- 2 Forex ausiliari: BIQUOTE;
- tutti e 10 `MARKET_CLOSED`;
- età delle quote: **168.074–177.678 secondi** (circa 46,7–49,4 ore).

Il log non espone timestamp assoluto della quota, ticker provider risolto, market type/contratto o scadenza. L'età da sola non sostituisce l'identità contrattuale.

Le voci risultano bloccate da `LIVE_DATA_NOT_FRESH`, `NO_VALID_SETUP`, `TRIGGER_NOT_CONFIRMED`, direzione/setup non valido e livelli mancanti; su alcuni strumenti sono presenti anche gate probability/quality/confidence non superati. Non risultano entry, stop, TP1/2/3, stop ATR o RR utilizzabili.

Riepilogo letterale:
- Recorded entries: 0
- Updated open outcomes: 0
- New feedback signals: 0
- New additional live forecasts: 0
- `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`

Telegram #3726: API SEND CONFIRMED alle 20:41:14.9990102 UTC, round-trip 337 ms; il log dice WATCH pre-alert accepted. Il corpo non è conservato, quindi non è attribuibile a uno strumento/direzione.

### Journal e persistenza

File verificati su main:
- `journal.csv`: 11 righe del 17 ottobre, tutte “nessun segnale”.
- `paper_trade_log.csv`: un vecchio WTI LONG del 8 ottobre, `LEGACY_IMPORT`, entry 96.24, stop 89.37, TP1 103.11; nessun provider, timestamp quota, mercato/scadenza o prova di fill.
- `position.json`: vecchia posizione Heating Oil LONG del 15 settembre; entry 4.8844, stop 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882; nessun provider/contratto/quotazione verificabile.
- `data/paper_open.json`: WTI P0001 marcato OPEN, legacy, non riconciliato con il monitor corrente.
- `commodities_prediction_log.json`: 981 record dal 10 al 15 settembre; 945 PENDING e 36 NEUTRALE. Azioni: 21 COMPRA ORA (19 RBOB, 2 Heating Oil; tutti PENDING), 292 LONG attendere conferma, 15 SHORT attendere conferma, 576 ATTENDERE, 77 NON ENTRARE. ATR valorizzato soltanto in 6 record. Mancano provider, timestamp quota, ticker provider, market type e scadenza.
- `gagarin_feedback.csv`: non presente su main (GitHub Contents 404).

**Rettifica sulla persistenza:** il workflow mappa `DATABASE_URL` dal secret, ma nel log della run #170 l'ambiente mostra il valore risolto vuoto (`DATABASE_URL:`). Il workflow dichiara che i paper journal non vanno committati nel repository pubblico e che la persistenza sarà riattivata solo dopo storage privato D1 deployato e verificato. Non c'è quindi evidenza di persistenza condivisa del feedback in questa run; non è stata consultata o modificata alcuna configurazione segreta.

### Motore outcome su main

Il file [engine/feedback.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py) conferma:
- schema feedback senza campi espliciti per provider, quote ticker, market type e scadenza;
- matching delle serie successive tramite symbol/timeframe, con fallback sul solo symbol quando esiste un solo stato;
- controllo `stop_hit` prima dei target: se la stessa candela OHLC tocca SL e TP, il codice registra STOP, benché la sequenza intrabar non sia ricostruibile.

Questo non rispetta il criterio PRAVDA: il doppio tocco nella stessa candela deve restare `ESITO NON VERIFICABILE`.

### PR GAGARIN

- [PR #222](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222): MERGED alle 20:24:56 UTC; rimuove `session_ok` come hard veto intraday nel Governor. Non rimuove market-open effettivo, freschezza quote o gli altri controlli. La run #170 su main aggiornato è comunque bloccata da mercato chiuso e dati stale.
- [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, mergeable; **6 ahead / 6 behind**. Head `295dba4b074e564a4c11aa3fca136a8e4360672c`. Il branch aggiunge controlli ticker/mercato/scadenza e classifica il doppio tocco SL+TP nella stessa candela come non verificabile. Rimane però il difetto già segnalato: `_market_contract_match()` non confronta esplicitamente `row.quote_provider` con il provider della serie di candele. Commenti esistenti: [#6706619879](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6706619879) e [#6725075554](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6725075554). Nessun commento duplicato.

## 4. Continuità delle GitHub Actions

| Processo | Cron dichiarato | Ultime due run schedule consultate | Gap |
|---|---|---|---:|
| SPUTNIK collector | `2-59/5 * * * *` | #289 16:15:37 → #291 20:35:50 UTC | 4h20m13s |
| SPUTNIK polling | cron 5 minuti | #50 16:05:42 → #51 20:27:04 UTC | 4h21m22s |
| GAGARIN monitor | `*/15 * * * *` | #169 16:16:25 → #170 20:41:00 UTC | 4h24m35s |

Al cut-off 21:33:44 UTC, dall'ultima run consultata erano trascorsi:
- SPUTNIK collector: 57m54s;
- SPUTNIK polling: 1h06m40s;
- GAGARIN monitor: 52m44s.

Le run push e le CI delle PR non sono scansioni schedule. Le esecuzioni consultate sono SUCCESS, ma la frequenza osservata non rispetta i cron. La causa dei gap non è dimostrata.

## 5. Esiti e statistiche

Nessun record nuovo ha entry, SL, TP, ATR, provider, ticker risolto, timestamp quota e identità contrattuale sufficienti per avviare una valutazione prospettica. Non è disponibile una sequenza successiva di prezzi/candele omogenea per decidere SL prima o TP prima.

- Fill verificati: 0
- SL verificati: 0
- TP verificati: 0
- Campione valido per win rate/average R/total R: 0

Nessun backtest o risultato è stato inventato.

## 6. Fonti consultate

- [SPUTNIK run #291](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42520937991)
- [SPUTNIK polling #51](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42520176845)
- [GAGARIN monitor #170](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42521363444)
- [Workflow SPUTNIK](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/trump_tracker.yml)
- [Workflow GAGARIN](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml)
- [GAGARIN feedback engine](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py)
- Journal/archivi GAGARIN: `journal.csv`, `paper_trade_log.csv`, `position.json`, `data/paper_open.json`, `commodities_prediction_log.json`.
- PR esaminate: SPUTNIK #145/#147/#149; GAGARIN #192/#222.

## 7. Prossimo controllo

1. Verificare le nuove run schedule e misurare nuovamente i gap.
2. Alla riapertura dei mercati, richiedere ticker esatto, provider, timestamp quota, market type e scadenza prima di accettare setup.
3. Verificare eventuali aggiornamenti delle PR #145/#147/#192 e la loro CI sul head corrente.
4. Verificare la persistenza del journal soltanto tramite evidenza esplicita di scrittura/lettura, senza leggere o esporre secret.
5. Riconciliare WTI P0001 e Heating Oil legacy solo con prova di esecuzione e prezzi successivi dello stesso identico contratto.

**PAPER ONLY.** Nessun ordine reale, nessun accesso a Trading212 dichiarato, nessuna consegna Telegram al dispositivo dichiarata. Nessun servizio a pagamento, nessuna modifica a secret o Render. PRAVDA non ha modificato codice, strategia, filtri, punteggi o rischio; non ha effettuato merge o deploy. In questo audit non è stato modificato il ledger perché non sono emersi nuovi record.
