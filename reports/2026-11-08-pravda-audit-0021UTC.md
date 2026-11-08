# PRAVDA — Audit incrociato SPUTNIK / GAGARIN

**Cut-off:** 8 novembre 2026, 00:21 UTC (01:21 Europe/Rome).

## Sintesi esecutiva

Controllati i run GitHub Actions con `event=schedule`, i job e i log dei due monitor, gli artifact, lo stato SPUTNIK, il ledger, i journal/feedback GAGARIN e le PR correttive.

- **Nessun nuovo trade verificabile.** Nessun nuovo messaggio contiene entry, SL, TP e ATR utilizzabili insieme a identità esatta dello strumento/contratto e quotazione fresca.
- **SPUTNIK:** ultimo monitor di mercato `#42426077974`, SUCCESS, 23:37:18–23:37:31 UTC del 7 novembre. Il precedente monitor era `#42409488950`, 20:07:13–20:07:24 UTC: intervallo tra avvii 3h30m05s. Al cut-off il monitor più recente era terminato da 43m29s, contro cron `2-59/5 * * * *`.
- **GAGARIN:** ultimo monitor completo `#42423479990`, SUCCESS, 23:03:38–23:03:58 UTC del 7 novembre. Il precedente era `#42407171354`, 19:38:07–19:38:24 UTC: intervallo tra avvii 3h25m31s. Al cut-off il monitor più recente era terminato da 1h17m02s, contro cron `*/15 * * * *`.
- Nelle Actions filtrate per evento `schedule` non risultano monitor di mercato successivi a quelli sopra entro il cut-off. I run di polling, daily summary e test PR non sono scansioni di mercato.

## SPUTNIK

### Run di mercato `#42426077974`

Log: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42426077974

- Job `sputnik`: SUCCESS. Artifact Actions: nessuno.
- Il run parte alle 23:37:23.703 UTC e completa l'analisi in circa 3,15 secondi; fase notifiche circa 1,81 secondi.
- SEC: HTTP 403, cooldown dichiarato di 21.600 secondi; zero filing e zero nuove operazioni SEC.
- White House RSS: HTTPError.
- Intelligence pubblica: 8 nuove correlazioni salvate nello stato, composte da 7 item individuali `PUBLIC_RSS` e una rilevazione page-level `TRUTH_ARCHIVE`. Gli item individuali hanno ritardi di rilevamento tra circa 1h49m e 4h57m. Le classificazioni registrate sono `NO_ANALOGUE`; nessuna ha prodotto mapping commodity, direzione, quotazione o livelli.
- Il handoff SPUTNIK→GAGARIN è disabilitato nel run perché `GAGARIN_CLOUD_API_URL` e `GAGARIN_CLOUD_API_KEY` non sono configurati.

### Messaggi Telegram di produzione verificati

| ID | Generazione UTC | ACK API UTC | Contenuto | Valutazione PRAVDA |
|---|---|---|---|---|
| 726 | 23:37:26.853 | 23:37:26.854 | Digest delle 8 correlazioni pubbliche | Intelligence, non segnale |
| 727 | 23:37:26.854 | 23:37:26.855 | GOLD, bias NEUTRAL, tecnica 5m indisponibile, WATCH | NO_DIRECTION, nessun livello |
| 728 | 23:37:26.855 | 23:37:26.856 | GOLD CFD, NEUTRAL/NO_DIRECTION, `NOT_EXECUTED` | Non-trade; scadenza non verificata |

Tutti e tre hanno ricevuto risposta API positiva con round-trip rispettivamente 636 ms, 516 ms e 454 ms. Questo prova l'accettazione API, non la visualizzazione sul dispositivo. I messaggi 727 e 728 sono due formati della stessa analisi GOLD, non due setup indipendenti.

Per #727: priorità catalizzatore 100/100 non è un punteggio di validità; direzione tecnica 5m `UNAVAILABLE`, allineamento notizie `NO_DIRECTIONAL_NEWS`, stato `WATCH`; nessuna entry, SL, TP, ATR o quotazione attribuibile.

Per #728: score 100 non è validità operativa; `D-L-A` non valutato, `TRADE PAPER: NOT_EXECUTED`, `NARWHAL REF: NOT_CONFIGURED`; strumento indicato come front-month continuo senza scadenza esatta né indipendenza upstream verificata. Nessun livello operativo. La riga di rischio 1,0% è un limite informativo, non esposizione eseguita.

Nel medesimo log, prima dell'avvio del monitor, compaiono output dei test di regressione (inclusi invii non confermati e un `message_id` simulato). Sono esclusi dal ledger di produzione: sono stati registrati soltanto i tre messaggi #726–#728 generati dopo `run started`.

### Persistenza SPUTNIK — rettifica

Il commit `42f685921fa356f2669e85b6764b290535b95f8e` è generato dallo step `Persist SPUTNIK state` del run `#42426077974`; non è un commit privo di run associato. Il log mostra il push su `main`. Il file `sputnik_state.json` contiene `updated_at=2026-11-07T23:37:25Z` e la cronologia delle 8 osservazioni. La correzione proposta in PR #144 sposta invece lo stato su un branch dedicato: la PR non è ancora integrata, quindi la scrittura pubblica su `main` è ancora il comportamento osservato.

PR #144: https://github.com/andreameloni1984-sys/trump-trucker/pull/144 — OPEN, non draft, mergeable; non merged. I due run PR più recenti consultati, #42426394830 (ranking tests) e #42426394789 (Telegram menu tests), sono SUCCESS. I test verdi non equivalgono al merge né alla correzione del monitor main.

Polling SPUTNIK `#42423194296` (23:00:10–23:00:21 UTC) è SUCCESS con `Pending updates: 0`; è polling Telegram, non monitor di mercato.

## GAGARIN

### Run completo `#42423479990`

Log: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42423479990

- Job `Run Gagarin directly on GitHub`: SUCCESS. Artifact Actions: nessuno.
- Il log stampa `DATABASE_URL` vuoto.
- Il riepilogo dichiara 8 commodity operative, ma elenca anche EUR/USD e GBP/USD come contesto FX ausiliario: il ranking contiene quindi 10 righe.
- Tutti gli strumenti del run sono `MARKET_CLOSED`. Età delle quotazioni: circa 100.133 secondi (27h49m) per soia/grano/mais; circa 90.532 secondi (25h09m) per metalli, petrolio e rame; BIQUOTE FX circa 90.534 secondi.
- Il log mostra provider e quote age, ma non espone timestamp esatto della candela, ticker provider risolto, market type e scadenza. Non è quindi possibile associare un prezzo successivo allo stesso identico contratto.
- Argento è ancora nella classifica: LONG, probabilità 59, qualità 49,5, confidence 32, `PAPER_WATCH`. Blocchi espliciti: `LIVE_DATA_NOT_FRESH`, `TRIGGER_NOT_CONFIRMED`, `TRIGGER_DIRECTION_MISMATCH`, `CONFIDENCE_FAIL`, `FINAL_CONFLUENCE_FAIL`. Non è un ingresso.
- Il run conclude `signals=0 open=0 closed=0`, `New feedback signals: 0`.
- Telegram message #3717 è stato accettato dall'API (474 ms), ma il corpo non è conservato: non attribuisco il board ad Argento o ad altro strumento.

### Journal, feedback e legacy

- `journal.csv`: 11 righe del 17 ottobre, tutte con campi di ingresso/livelli vuoti e `nessun segnale`.
- `paper_trade_log.csv`: un ticket legacy WTI P0001, LONG, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55; nota riferita a chiusura spot del 6 ottobre, ma nessuna prova di fill, provider, timestamp preciso, mercato/contratto di esecuzione o ATR.
- `data/paper_open.json` contiene lo stesso P0001: è lo stesso ticket, non una seconda posizione.
- `position.json`: vecchia posizione Heating Oil LONG aperta il 15 settembre; nessuna prova di fill e identità di contratto incompleta.
- `commodities_prediction_log.json`: 981 record; ultimo `created_at` 2026-09-15T15:45:04Z, Benzina RBOB, stato PENDING. Non è prova di esecuzione e non espone provider/timestamp della quotazione per il record più recente.
- `gagarin_feedback.csv`: 404 Not Found. Nessun feedback file consultabile.

### Polling Telegram GAGARIN

Run #42317191549, 7 novembre 00:16:15–00:16:32 UTC: FAILURE. Il log documenta `getUpdates` HTTP/API 409: webhook attivo, polling incompatibile. PR #175 è ancora OPEN e non merged: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175. Il monitor può comunque inviare con `sendMessage`; il conflitto riguarda il runner di polling e non prova un mancato invio degli alert.

## PR correttive consultate

| PR | Stato al controllo | Rilievo |
|---|---|---|
| SPUTNIK #144 | OPEN, non draft, mergeable; CI ranking/menu consultata SUCCESS | Spostamento stato su branch dedicato; main continua a scrivere `sputnik_state.json` |
| GAGARIN #175 | OPEN, non draft | Gestione 409 webhook/polling non integrata |
| GAGARIN #181 | OPEN, non draft | Provenienza esatta ticker/mercato/timestamp non ancora presente nel log main |
| GAGARIN #192 | OPEN, non draft | Fingerprint esatto contratto e ambiguità SL/TP same-candle non integrate |
| GAGARIN #219 | OPEN, non draft | Rimozione Forex ausiliario non integrata; il run main continua a elencare EUR/USD e GBP/USD |
| GAGARIN #222 | OPEN, draft | Rimozione del veto `session_ok`, non integrata |
| GAGARIN #223 | OPEN, draft | Scan M5 isolato su sette strumenti; non rimuove Argento dal monitor completo |
| GAGARIN #235 | OPEN, draft | Persistenza isolata del journal CFD PAPER, non integrata |

PR #219: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219
PR #181: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/181
PR #192: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192
PR #222: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222
PR #223: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223
PR #235: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/235

## Ledger e statistiche

Snapshot giornaliero creato a partire dal ledger del 7 novembre (74 record) con tre nuove righe di notifica SPUTNIK (#726, #727, #728). Le 8 osservazioni intelligence erano già presenti nel ledger precedente e non sono state duplicate.

- Record totali: **77**.
- SPUTNIK: **31**; GAGARIN: **46**.
- Firme uniche: **77**; source ID unici: **77**; duplicati: **0**.
- `NON_TRADE`: **48**; `ESITO_NON_VERIFICABILE`: **29**.
- Fill verificati: **0**; outcome SL-first: **0**; outcome TP-first: **0**.
- Win rate e Average R: **N/D**, campione di fill verificati pari a zero.

Ledger: https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-08.csv

Le tre nuove righe sono notifiche/analisi non operative. Non sono state conteggiate come trade. I record storici `PENDING`, `NOT_EXECUTED`, `PAPER_WATCH` e i ticket senza fill restano esclusi da qualsiasi statistica di performance. Nessun esito SL/TP è stato inferito da spot, futures continui o scadenze diverse.

## Fonti e limiti

Fonti consultate: Actions schedule e job log dei run #42426077974, #42423479990 e #42317191549; artifact listing dei due monitor (nessun artifact); workflow `trump_tracker.yml` e `gagarin-monitor.yml`; `sputnik_state.json`; ledger 7 novembre; `journal.csv`, `paper_trade_log.csv`, `data/paper_open.json`, `position.json`, `commodities_prediction_log.json`; lookup `gagarin_feedback.csv` (404); metadati PR sopra elencate.

Non è stato possibile verificare prezzi/candele successive dello stesso identico contratto perché nessun nuovo ingresso è stato registrato, le quotazioni GAGARIN erano stale/mercato chiuso e SPUTNIK non espone ticker/scadenza/serie verificabili. Non è stata dichiarata consegna Telegram al dispositivo: si riportano soltanto gli ACK API espliciti.

## Prossimo controllo

1. Verificare il primo run monitor successivo per ciascun bot, separandolo da polling, summary e test.
2. Per GAGARIN acquisire timestamp OHLC, ticker provider risolto, market type e scadenza esplicita; se mancano, lasciare `ESITO NON VERIFICABILE`.
3. Per SPUTNIK associare ogni notizia a un item datato e a un mapping commodity verificabile; non usare il front-month continuo per attribuire outcome senza scadenza.
4. Verificare se PR #144 e le correzioni GAGARIN vengono integrate; non considerare i branch PR come comportamento di `main`.

**Ambito rispettato:** nessuna modifica a codice, strategia, filtri, scoring o rischio; nessun merge/deploy, ordine reale, segreto o configurazione Render modificati. PAPER ONLY.