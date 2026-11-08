# PRAVDA — Audit incrociato SPUTNIK / GAGARIN

**Cut-off:** 8 novembre 2026, 01:56:22 UTC (02:56:22 Europe/Rome).

## Sintesi esecutiva

Verificati il ledger PRAVDA pubblicato, i commit recenti dei due repository, i workflow di monitoraggio, i job/log degli ultimi run di mercato già identificati, gli artifact Actions disponibili, i journal/feedback GAGARIN e lo stato delle PR correttive.

- **Nessun nuovo segnale operativo verificabile** rispetto al ledger delle 00:21 UTC. Non sono state aggiunte righe e non è stato modificato il CSV.
- Ledger: **77 record**, SPUTNIK 31, GAGARIN 46; 77 firme `audit_signature` uniche e 77 `source_record_id` unici; zero duplicati.
- Fill verificati: **0**. Outcome SL-first: **0**. Outcome TP-first: **0**. Win rate e Average R: **N/D**.
- L'ultimo run SPUTNIK con log completo consultato resta #42426077974, concluso il 7 novembre alle 23:37:31 UTC. Al cut-off era terminato da **2h18m51s**.
- L'ultimo run GAGARIN con log completo consultato resta #42423479990, concluso il 7 novembre alle 23:03:58 UTC. Al cut-off era terminato da **2h52m24s**.
- In questo passaggio non è stato possibile ottenere un elenco completo e aggiornato delle Actions schedule successivo al precedente audit. Pertanto questi sono gli ultimi run con log direttamente verificati, non una certificazione dell'assenza assoluta di run successivi.
- I mercati sono chiusi la domenica; nessun outcome può essere ricavato da quotazioni stale o da contratti non identificati.

## SPUTNIK

### Ultimo run con log completo: #42426077974

- Job `sputnik`: SUCCESS; nessun artifact Actions.
- Cron su main: `2-59/5 * * * *`.
- Il run parte alle 23:37:23.703 UTC; analisi e notifiche durano circa 3,15 secondi.
- SEC: HTTP 403, cooldown dichiarato di 21.600 secondi, zero filing.
- White House RSS: HTTPError.
- Otto osservazioni pubbliche: sette item RSS individuali e una fotografia page-level TRUTH_ARCHIVE. Tutte senza mapping commodity/direzione verificabile; ritardo item-level già misurato tra circa 1h49m e 4h57m.
- Handoff SPUTNIK→GAGARIN disabilitato perché URL e API key cloud non configurati.

### Messaggi Telegram di produzione

| ID | Generazione UTC | ACK API UTC | Contenuto | Classificazione |
|---|---|---|---|---|
| 726 | 23:37:26.853 | 23:37:26.854 | Digest intelligence | NON_TRADE |
| 727 | 23:37:26.854 | 23:37:26.855 | GOLD NEUTRAL, tecnica 5m indisponibile, WATCH | NON_TRADE |
| 728 | 23:37:26.855 | 23:37:26.856 | GOLD CFD, NO_DIRECTION, NOT_EXECUTED | NON_TRADE |

Gli ACK API sono rispettivamente 636 ms, 516 ms e 454 ms. Provano l'accettazione da parte dell'API, non la visualizzazione sul dispositivo. #727 e #728 sono due formati della stessa analisi GOLD, non due setup indipendenti. Non ci sono entry, SL, TP, ATR o quotazione attribuibile; il front-month continuo non espone una scadenza esatta verificata. Score/priorità 100 non è validità operativa.

### Persistenza e workflow

Il workflow main ha `contents: write` e persiste `sputnik_state.json` su main. Il commit `42f685921fa356f2669e85b6764b290535b95f8e` è collegato allo step di persistenza del run #42426077974. La PR #144 propone un branch dedicato ma resta OPEN e non integrata. La lettura diretta di `sputnik_state.json` in questo passaggio non ha restituito il contenuto, quindi non certifico nuovamente il suo `updated_at` corrente.

PR consultate:
- [#144 — Persist SPUTNIK state outside main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN.
- [#145 — Expose SPUTNIK quote provenance](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN.
- [#146 — Individual alerts and economic calendar](https://github.com/andreameloni1984-sys/trump-trucker/pull/146): OPEN.
- [#147 — Remove GAGARIN handoff](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN.
- [#148 — Stop repeating recommendations](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN.

## GAGARIN

### Ultimo run con log completo: #42423479990

- Job monitor: SUCCESS; nessun artifact Actions.
- Cron su main: `*/15 * * * *`.
- Workflow `contents: read`; commento operativo dichiara la persistenza dei journal disabilitata fino a storage privato D1 verificato.
- Tutte le dieci righe runtime risultavano `MARKET_CLOSED`: otto commodity più EUR/USD e GBP/USD come contesto ausiliario.
- Età quote nel run: circa 90.532 secondi (25h09m) per metalli/petrolio/rame e circa 100.133 secondi (27h49m) per cereali/soia. Il log non fornisce timestamp esatto OHLC, ticker provider risolto, market type e scadenza del contratto.
- Argento: LONG, probabilità 59, qualità 49,5, confidence 32, `PAPER_WATCH`; blocchi `LIVE_DATA_NOT_FRESH`, `TRIGGER_NOT_CONFIRMED`, `TRIGGER_DIRECTION_MISMATCH`, `CONFIDENCE_FAIL`, `FINAL_CONFLUENCE_FAIL`. Non è un ingresso.
- Riepilogo: `signals=0 open=0 closed=0`; nuovi feedback 0; nuove forecast 0.
- Telegram #3717: API ACK 474 ms, ma corpo non conservato; non lo attribuisco a uno strumento.

### Journal e feedback

Lettura diretta su main:
- `journal.csv`: 11 righe del 17 ottobre, tutte con entry/SL/TP vuoti e `nessun segnale`.
- `paper_trade_log.csv`: una riga legacy WTI P0001 LONG, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55; nessuna prova di fill, provider, timestamp quote, mercato/scadenza o ATR.
- `data/paper_open.json`: stesso P0001; non è una seconda posizione.
- `position.json`: vecchia posizione Heating Oil LONG, entry 4,8844, SL 4,5418, TP1 5,4473, TP2 5,6284, TP3 5,882; nessuna prova di fill e contratto incompleto.
- `gagarin_feedback.csv`: 404 Not Found.
- Il precedente log monitor riportava `DATABASE_URL` vuoto.

I record PENDING, i ticket legacy e le posizioni senza fill non sono trade verificati. Non sono stati valutati contro prezzi spot o contratti diversi.

PR consultate:
- [#175 — Handle active Telegram webhook](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): OPEN.
- [#181 — Quote provenance](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/181): OPEN.
- [#192 — Exact-contract and ambiguous-outcome audit fixes](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN.
- [#196 — Restrict analysis to eight commodities](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/196): OPEN.
- [#219 — Remove EUR/USD and GBP/USD](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219): OPEN.
- [#222 — Remove intraday session veto](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222): OPEN.
- [#223 — Isolated seven-instrument M5 scan](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): OPEN; non rimuove Argento dal monitor completo.
- [#235 — Isolated PAPER journal persistence](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/235): OPEN.

## Ledger e statistiche

Ledger letto direttamente da main: [pravda-signal-ledger-2026-11-08.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-08.csv).

Conteggio ricalcolato sulle righe CSV:
- Record: **77**.
- SPUTNIK: **31**; GAGARIN: **46**.
- `audit_signature`: 77 valori unici, 0 duplicati.
- `source_record_id`: 77 valori unici, 0 duplicati.
- Fill verificati: **0**; SL-first: **0**; TP-first: **0**.
- Win rate / Average R: **N/D**.

Non sono emersi nuovi messaggi o segnali da aggiungere. Il ledger resta invariato. Le notifiche #726–#728, i WATCH, i PENDING e i ticket senza fill non entrano nelle statistiche di performance.

## Limiti di questa verifica

- Non è stato ottenuto un elenco Actions schedule completo e aggiornato oltre i run già documentati; i timestamp sopra sono gli ultimi log direttamente recuperati.
- Non è possibile concludere che non vi siano state esecuzioni successive soltanto dall'assenza di nuovi commit.
- Nessun nuovo fill e nessun set di candele successive sullo stesso identico contratto è disponibile.
- Mercati chiusi; quote GAGARIN già stale al momento del run.
- Nessuna prova di consegna Telegram al dispositivo: soltanto ACK API.
- Il contenuto corrente di `sputnik_state.json` non è stato restituito dalla lettura GitHub in questo passaggio.

## Prossimo controllo

1. Recuperare l'elenco completo dei run schedule e separare monitor, polling, summary e test.
2. Al primo run GAGARIN con mercato aperto, acquisire timestamp OHLC, ticker esatto, provider, market type e scadenza.
3. Per SPUTNIK, distinguere item datati, mapping commodity, quote e scadenza; non usare il continuous front-month come contratto eseguibile.
4. Verificare i merge effettivi delle PR prima di attribuire a main le correzioni proposte.

**Ambito rispettato:** nessuna modifica a codice, strategia, filtri, scoring o rischio; nessun merge/deploy, ordine reale, segreto o configurazione Render modificati. PAPER ONLY.
