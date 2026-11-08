# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 8 novembre 2026, 22:42:39 UTC (23:42:39 Europe/Rome)**

## Sintesi

Verificati i repository e i rispettivi branch `main`, le ultime run schedule disponibili, i log integrali dei job, i journal/feedback pubblici, lo stato SPUTNIK persistito e le PR aperte.

**Non risultano nuove run produttive dopo SPUTNIK #291 (20:35:50 UTC) e GAGARIN #170 (20:41:00 UTC).** I record #741, #742 e #3726 sono già nel ledger; nessun nuovo record eleggibile. È emersa una PR SPUTNIK nuova (#150), con CI superata, ma ancora non integrata.

## 1. Ledger PRAVDA

File: `reports/pravda-signal-ledger-2026-11-08.csv`

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

I 29 record non verificabili includono previsioni legacy e record senza identità contrattuale/prezzi successivi omogenei; non sono 29 operazioni. Win rate, average R e total R restano **N/D**.

Ultimi record già presenti:
- SPUTNIK #741 — WATCH / NEUTRAL, nessuna direzione.
- SPUTNIK #742 — NOT_EXECUTED / NO_DIRECTION.
- GAGARIN #3726 — WATCH pre-alert, corpo non conservato e strumento non attribuibile.

#741 e #742 sono due messaggi della stessa analisi GOLD. #3726 non è attribuibile a un mercato. Nessun record aggiunto in questo audit e nessuna modifica al CSV.

## 2. SPUTNIK — run produttiva #291

GitHub Actions run ID: `42520937991`; workflow `.github/workflows/trump_tracker.yml`; evento schedule; SUCCESS. Avvio: **20:35:50 UTC**. Runtime: `20:35:56.053060Z`.

### Fonti e analisi effettiva

Nel vero step di produzione:
- SEC CIK 0001849635: HTTP 403, cooldown 21.600 secondi; filing=0.
- White House RSS `https://www.whitehouse.gov/feed/`: HTTPError.
- Scansione intelligence pubblica: 1.066 ms, findings=0.
- Filing=0; transazioni=0; nuove correlazioni pubbliche=0.
- Forwarding GAGARIN=0 ms.

Le righe `OSError` per WHITE_HOUSE/TRUTH_ARCHIVE/OGE e la falsa “GAGARIN confirmation received” sono stampate nello step precedente di unit test, prima dell'avvio del runtime. Non vengono attribuite alla produzione.

### Messaggi

- Telegram #741: WATCH / NEUTRAL, tecnica 5m UNAVAILABLE, nessuna direzione. API ACK alle 20:35:58.6659378 UTC, 497 ms.
- Telegram #742: NOT_EXECUTED / NO_DIRECTION. API ACK alle 20:35:58.6670675 UTC, 444 ms.

Per #742 il titolo usa “CFD”, ma il corpo identifica `FUTURES_CONTINUOUS_FRONT_MONTH` senza scadenza esatta. Non sono esposti ticker risolto, provider, timestamp/età della quota, prezzo di riferimento, entry, SL, TP o ATR. Score 100/100 non è validità operativa; NOT_EXECUTED non è un trade. Gli ACK API non dimostrano la visualizzazione sul dispositivo.

### Stato persistito e ritardo del dato pubblico

La fase “Persist SPUTNIK state” ha creato il commit `7e4c6288bf3343076f2f31c5c1d47f142501fd86` alle 20:35:58 UTC. Il blob corrente di `sputnik_state.json` riporta:
- updated_at: 20:35:57.271795 UTC;
- events: 0;
- intelligence_history: 500 elementi.

Nella cronologia è presente un item RSS individuale pubblicato alle **13:49:32 UTC** e rilevato alle **16:15:42 UTC**: ritardo **2h26m10s**. La classificazione è OTHER / NO_ANALOGUE, non una direzione commodity. La scansione #291 non ha rilevato nuovi item ma ha comunque prodotto l'analisi GOLD usando la cronologia recente.

### PR SPUTNIK

- PR #150 “Stop repeating SPUTNIK recommendations without a new RSS item”: OPEN, non draft, mergeable; **2 commit avanti / 0 indietro** rispetto al main corrente. Le due CI associate (#42526381309 e #42526381230) sono SUCCESS alle 21:40:39–41 UTC. La modifica limita il recommender alle nuove evidenze RSS item-level. È la correzione esistente pertinente alla ripetizione dell'analisi quando la scansione non trova nuovi item; non è ancora in produzione.
- PR #147 (rimozione handoff GAGARIN): OPEN, **1 avanti / 7 indietro**; non integrata. Il main contiene ancora il codice/hook opzionale e le variabili workflow. Nel runtime #291 URL/key erano vuote e forwarding=0 ms: nessun handoff effettivo dimostrato.
- PR #145 (provenienza quote Yahoo): OPEN, **1 avanti / 9 indietro**; non integrata.
- PR #149: MERGED; rimuove il gate a ora fissa del daily brief.

Polling #51 (`42520176845`) è SUCCESS, avvio 20:27:04 UTC, ma il polling non prova la consegna al dispositivo.

## 3. GAGARIN — run produttiva #170

GitHub Actions run ID: `42521363444`; workflow `.github/workflows/gagarin-monitor.yml`; evento schedule; SUCCESS. Avvio: **20:41:00 UTC**. Timestamp interno motore: `20:41:12.654117Z`.

### Quotazioni e decisioni

Il log riporta **10 strumenti**: 8 commodity operative e 2 Forex ausiliari. Tutti `MARKET_CLOSED`.

- YAHOO commodity: età **168.073,8–177.677,7 secondi** (circa 46,7–49,4 ore).
- BIQUOTE EUR/USD e GBP/USD: circa **168.374 secondi** (46,8 ore).
- Non sono esposti timestamp assoluti della quota, ticker provider risolti, market type/contratto o scadenza.

Tutte le voci risultano bloccate da dati stale/mercato chiuso, setup e trigger non confermati e livelli mancanti. Nessuna entry, SL, TP o ATR operativo.

Riepilogo letterale:
- Recorded entries: 0
- Updated open outcomes: 0
- New feedback signals: 0
- New additional live forecasts: 0
- `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`

Telegram #3726: API SEND CONFIRMED alle 20:41:14.9990102 UTC, 337 ms; il corpo non è conservato e non è possibile attribuirlo a uno strumento/direzione. ACK API ≠ prova di visualizzazione sul dispositivo.

### Journal, feedback e persistenza

File pubblici su main:
- `journal.csv`: 11 righe del 17 ottobre, tutte “nessun segnale”.
- `paper_trade_log.csv`: un WTI LONG del 8 ottobre, LEGACY_IMPORT, entry 96.24, stop 89.37, TP1 103.11; nessun provider, timestamp quota, mercato/scadenza di esecuzione o prova di fill.
- `position.json`: Heating Oil LONG del 15 settembre, entry 4.8844, stop 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882; nessuna identità di contratto/quotazione.
- `data/paper_open.json`: WTI P0001 marcato OPEN, legacy, non riconciliato con il monitor corrente.
- `commodities_monitor_state.json`: timestamp 17 settembre, artefatto storico non aggiornato dalla run #170.
- `commodities_prediction_log.json`: 981 previsioni legacy; 945 PENDING e 36 NEUTRALE. Le 21 etichettate COMPRA ORA (19 RBOB, 2 Heating Oil) sono tutte PENDING, non fill. Mancano provider, timestamp quota, ticker provider, mercato e scadenza.
- `gagarin_feedback.csv`: assente su main.

Nel log della run #170 il valore risolto di `DATABASE_URL` è vuoto; il workflow dichiara che i paper journal sono dati operativi privati e non vanno committati nel repository pubblico finché lo storage privato non sia deployato e verificato. Non c'è evidenza di persistenza condivisa dei feedback in questa run. Non sono stati letti o modificati secret.

### Universo strumenti

Il main corrente `commodities/universe.py` definisce Oro, Argento, Rame, WTI, Brent, Grano, Mais e Soia, più EUR/USD e GBP/USD ausiliari. Il monitor #170 conferma 8 commodity + 2 Forex. Argento resta incluso; Platino e Palladio non compaiono. La PR #223, draft, propone un monitor M5 isolato a sette strumenti con Argento escluso, ma è **10 commit avanti / 3 indietro** rispetto al main e non è integrata. La PR #221 per rimuovere le route FX residue è draft, **14 avanti / 3 indietro**.

### Outcome engine e PR GAGARIN

Su main `engine/feedback.py`:
- il matching delle serie usa symbol/timeframe e un fallback sul solo symbol se esiste un solo stato;
- non richiede identità completa di provider, ticker, mercato e scadenza;
- controlla SL prima dei target: una candela OHLC che tocca SL e TP nella stessa barra viene registrata STOP, benché la sequenza intrabar sia ignota.

PR #192 è OPEN, non integrata, **6 avanti / 6 indietro**. Il branch aggiunge quote symbol, market type, mese/scadenza e classificazione ambigua del doppio tocco. Resta però un difetto dimostrato: `_market_contract_match()` non confronta esplicitamente il provider delle candele con `quote_provider` del segnale. Il head corrente è `295dba4b074e564a4c11aa3fca136a8e4360672c` (5 novembre); i check visibili su quel commit includono test SUCCESS ma anche Workers Build FAILURE. Nessun merge.

PR #237 (catalogo/simbolo broker) e #233 (identità spot senza scadenza) sono draft; i commenti esistenti documentano che slug del catalogo, ticker broker e simbolo app non sono intercambiabili e che l'assenza di scadenza non dimostra da sola un contratto spot. PR #235 per journal/feedback CFD durevoli è draft. Non è stato effettuato accesso a Trading212 né verificato un feed Trading212.

PR #222 è MERGED alle 20:24:56 UTC e rimuove `session_ok` come hard veto intraday. Non rimuove i controlli di mercato chiuso/freschezza: la run #170 resta bloccata da MARKET_CLOSED e quote stale.

## 4. Continuità delle GitHub Actions

| Processo | Cron dichiarato | Ultime due run schedule consultate | Gap tra le due | Gap al cut-off |
|---|---|---|---:|---:|
| SPUTNIK collector | `2-59/5 * * * *` | #289 16:15:37 → #291 20:35:50 UTC | 4h20m13s | 2h06m49s |
| SPUTNIK polling | ogni 5 min | #50 16:05:42 → #51 20:27:04 UTC | 4h21m22s | 2h15m35s |
| GAGARIN monitor | `*/15 * * * *` | #169 16:16:25 → #170 20:41:00 UTC | 4h24m35s | 2h01m39s |

Le CI della PR #150 alle 21:40 UTC non sono scansioni produttive. Le run schedule consultate sono SUCCESS, ma la cadenza osservata non rispetta i cron. La causa dei gap non è dimostrata.

## 5. Esiti e statistiche

Nessun segnale recente dispone di entry, SL, TP, ATR, provider, ticker risolto, timestamp quota e identità contrattuale completa. Non sono disponibili candele successive dello stesso identico strumento/contratto per stabilire SL prima o TP prima.

- Fill verificati: **0**
- SL verificati: **0**
- TP verificati: **0**
- Campione valido per win rate / average R / total R: **0**

Nessun backtest o risultato è stato inventato.

## 6. Fonti consultate

- SPUTNIK Actions #291 (run ID 42520937991), polling #51 (42520176845).
- GAGARIN monitor #170 (42521363444).
- SPUTNIK `trump_tracker.py`, `.github/workflows/trump_tracker.yml`, `sputnik_state.json`.
- GAGARIN `commodities/universe.py`, `.github/workflows/gagarin-monitor.yml`, `engine/feedback.py`, `journal.csv`, `paper_trade_log.csv`, `position.json`, `data/paper_open.json`, `commodities_monitor_state.json`, `commodities_prediction_log.json`.
- PR SPUTNIK #145, #147, #149, #150; PR GAGARIN #192, #221, #222, #223, #233, #235, #237.

## 7. Prossimo controllo

1. Verificare le nuove run schedule e misurare se la cadenza riprende.
2. Alla riapertura dei mercati, richiedere ticker provider, timestamp quota, provider, market type e scadenza prima di valutare un setup.
3. Verificare eventuale merge/aggiornamento delle PR #150, #147, #145, #192, #221, #223, #233, #235 e #237, senza eseguire merge.
4. Verificare persistenza journal/feedback solo tramite evidenza esplicita di scrittura e lettura, senza leggere secret.
5. Riconciliare WTI P0001 e Heating Oil legacy soltanto con prova di fill e prezzi successivi dello stesso contratto.

**PAPER ONLY.** Nessun ordine reale, nessun accesso a Trading212 dichiarato, nessuna consegna Telegram al dispositivo dichiarata. Nessun servizio a pagamento, nessuna modifica a secret o Render. PRAVDA non ha modificato codice, strategia, filtri, punteggi o rischio; nessun merge o deploy. Il ledger non è stato modificato perché non sono emersi nuovi record.
