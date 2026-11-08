# PRAVDA — Audit incrociato SPUTNIK / GAGARIN

**Cut-off:** 8 novembre 2026, 02:34:19 UTC (03:34:19 Europe/Rome).

## Sintesi esecutiva

Controllati gli ultimi workflow schedule disponibili, job e log, artifact Actions, journal/feedback GAGARIN, workflow di monitoraggio, ledger PRAVDA e PR correttive aperte.

- È comparso un nuovo monitor GAGARIN: run [#42438806862](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42438806862), concluso alle 02:30:28 UTC con SUCCESS.
- Non è comparso un nuovo monitor di mercato SPUTNIK dopo [#42426077974](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42426077974), concluso il 7 novembre alle 23:37:31 UTC. Il polling SPUTNIK [#42438101190](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42438101190) è un workflow distinto e non è una scansione di mercato.
- Il nuovo GAGARIN ha prodotto un solo candidato direzionale: Argento LONG in PAPER_WATCH, bloccato da mercato chiuso, quotazione stale, trigger non confermato/mismatch e confidence insufficiente. Non è un segnale autorizzato né un trade.
- Telegram GAGARIN ha confermato via API il messaggio #3718 (560 ms); il corpo non è conservato, quindi non lo attribuisco ad Argento e non dichiaro consegna sul dispositivo.
- Ledger aggiornato con due record audit: candidato Argento e messaggio #3718. Totale **79** record, **79** firme uniche, **79** source ID unici, zero duplicati.
- Fill verificati: **0**. SL-first: **0**. TP-first: **0**. Win rate / Average R: **N/D**.

## SPUTNIK

### Monitor e polling

Ultimo monitor di mercato individuato: [run #42426077974](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42426077974), workflow `.github/workflows/trump_tracker.yml`, event schedule, job `sputnik` SUCCESS, concluso il 7 novembre alle 23:37:31 UTC.

Al cut-off delle 02:34:19 UTC erano trascorse **2h56m48s** dalla conclusione. Il cron su main è `2-59/5 * * * *` (ogni cinque minuti, con minuto iniziale 2). L'intervallo tra i due monitor di mercato più recenti consultati (#42409488950 terminato 20:07:24 UTC e #42426077974 terminato 23:37:31 UTC) è **3h30m07s**, non cinque minuti.

Il run Telegram Polling più recente è [#42438101190](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42438101190), concluso l'8 novembre alle 02:20:24 UTC. Log: `Pending updates: 0`. È polling, non monitor di mercato; non dimostra l'invio di nuovi alert.

### Ultimo contenuto di mercato/intelligence verificato

Il run #42426077974:
- sette item RSS individuali più una rilevazione page-level TRUTH_ARCHIVE;
- tutti senza mapping commodity/direzione verificabile (`NO_ANALOGUE`);
- SEC HTTP 403 con cooldown 21.600 secondi e zero filing;
- White House RSS HTTPError;
- handoff SPUTNIK→GAGARIN disabilitato perché `GAGARIN_CLOUD_API_URL` e `GAGARIN_CLOUD_API_KEY` non configurati.
- messaggi #726 digest, #727 GOLD NEUTRAL/WATCH e #728 GOLD NO_DIRECTION/NOT_EXECUTED: ACK API rispettivamente 636, 516 e 454 ms. #727 e #728 sono due rappresentazioni della stessa analisi GOLD, non due setup indipendenti. Nessuna entry, SL, TP, ATR o scadenza esatta verificabile.

Gli score/priorità non sono validità operativa. Il front-month continuo senza scadenza identificata non è un contratto negoziabile verificato.

### PR SPUTNIK pertinenti

- [#144 — Persist SPUTNIK state outside main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN, non integrata.
- [#145 — Quote provenance](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN.
- [#148 — Stop repeating recommendations](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN.
- [#138 — Log scheduled-run gaps](https://github.com/andreameloni1984-sys/trump-trucker/pull/138): OPEN.
- [#136 — Continuous-futures provenance](https://github.com/andreameloni1984-sys/trump-trucker/pull/136): OPEN.

Il workflow main continua ad avere `contents: write` e a persistere `sputnik_state.json` su main. Non è stato modificato.

## GAGARIN

### Nuovo monitor #42438806862

- Run: [#42438806862](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42438806862).
- Creato alle 02:30:08 UTC; job iniziato 02:30:11 e terminato 02:30:27; run aggiornato/concluso alle 02:30:28 UTC.
- Job `Run Gagarin directly on GitHub`: SUCCESS.
- Artifact Actions: **0**.
- Timestamp applicativo: 02:30:21.567863 UTC.
- `PAPER_TRADING_ONLY=1`; `DATABASE_URL` vuoto; `NARWHAL_API_KEY` vuoto.

Il run precedente #42423479990 era terminato alle 23:03:58 UTC: intervallo tra le due scansioni **3h26m30s**, contro cron `*/15 * * * *`. Il nuovo run dimostra una nuova scansione, ma un singolo recupero non dimostra ancora il ritorno a una cadenza regolare.

### Universo, quotazioni e candidato

Il log dichiara otto commodity operative più EUR/USD e GBP/USD ausiliari, dieci strumenti analizzati. Tutti risultavano `MARKET_CLOSED`.

- Soia e Grano: Yahoo age circa **112.524 s** (31h15m24s).
- Mais: Yahoo age circa **112.524 s**.
- Brent, WTI, Oro, Argento e Rame: Yahoo age circa **102.922–102.923 s** (28h35m circa).
- EUR/USD e GBP/USD ausiliari: BiQuote age circa 102.925 s.

Il log non espone timestamp OHLC esatto, ticker provider risolto, mercato/scadenza o prezzo di riferimento. Le quote sono stale e il mercato è chiuso.

Unico candidato commodity con direzione:
- ID: `run:42438806862/classification:Argento`.
- Generazione/classificazione: **2026-11-08T02:30:25.6902087Z**.
- Strumento logico: Argento; riferimento logico XAG/USD, ticker provider risolto non emesso.
- Provider: Yahoo; quote age **102922.9 s** (~28h35m23s); timestamp quotazione non esposto.
- Direzione: LONG; tecnica/trigger: `TRIGGER_DIRECTION_MISMATCH`.
- Probabilità 59, qualità 49,5, confidence 32.
- Stato `PAPER_WATCH`, `NOT_AUTHORIZED`.
- Blocchi: `MARKET_CLOSED`, `LIVE_DATA_NOT_FRESH`, `TRIGGER_NOT_CONFIRMED`, `TRIGGER_DIRECTION_MISMATCH`, `CONFIDENCE_FAIL`, `FINAL_CONFLUENCE_FAIL`.
- Entry, SL, TP e ATR: assenti. Nessun fill.

Il riepilogo del run: `signals=0 open=0 closed=0`; `Recorded entries: 0`; `Updated open outcomes: 0`; `New feedback signals: 0`; `New additional live forecasts: 0`.

### Telegram GAGARIN

Il log riporta `Telegram SEND CONFIRMED | message_id=3718 | api_roundtrip=560ms`. Il timestamp della riga di conferma è 02:30:25.6916281 UTC; il timestamp esatto della richiesta di invio non è esposto. Il corpo del messaggio non è conservato. Poiché Argento è l'unico candidato direzionale nel run, la correlazione è plausibile ma non provata: il board #3718 resta non attribuibile a uno strumento specifico. ACK API non equivale a visualizzazione sul dispositivo.

### Journal e feedback

Letture correnti:
- `journal.csv`: 11 righe del 17 ottobre, tutte senza entry/SL/TP e con esito `nessun segnale`.
- `paper_trade_log.csv`: una riga legacy WTI P0001 LONG, entry 96,24, SL 89,37, TP1 103,11 e TP2 106,55; nessuna prova di fill, provider, quote timestamp, mercato/scadenza o ATR.
- `data/paper_open.json`: contiene lo stesso P0001; non è una seconda posizione.
- `gagarin_feedback.csv`: 404 Not Found.
- `DATABASE_URL`: vuoto nel run #42438806862.
- Il monitor non ha prodotto artifact Actions.

P0001 resta una registrazione legacy non verificata, non un trade. Non ho valutato livelli su spot o su contratti differenti.

### PR GAGARIN pertinenti

- [#175 — Handle active Telegram webhook in scheduled polling](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): OPEN. Il problema riguarda il polling in entrata (precedente errore 409); non invalida il sendMessage #3718.
- [#181 — Log exact quote provenance](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/181): OPEN.
- [#192 — Exact-contract and ambiguous-outcome audit fixes](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN.
- [#219 — Remove EUR/USD and GBP/USD](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219): OPEN, non integrata; i due FX risultano ancora ausiliari nel runtime.
- [#222 — Remove intraday session veto](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222): OPEN/DRAFT.
- [#223 — Isolated seven-instrument M5 scan (silver excluded)](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): OPEN/DRAFT; aggiunge una scansione separata, non rimuove Argento dal monitor completo.
- [#225 — Offset monitor schedule](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225): OPEN/DRAFT; non modifica il cron su main finché non integrata.
- [#202 — Persist journal and daily feedback](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): OPEN/DRAFT.

Nessuna PR è stata considerata integrata senza merge verificato. Le PR relative a Trading 212 non sono state usate per questa verifica.

## Ledger e statistiche

Ledger: [pravda-signal-ledger-2026-11-08.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-08.csv).

Dopo l'append e una nuova lettura del CSV:
- Record: **79**.
- SPUTNIK: **31**.
- GAGARIN: **48**.
- `audit_signature`: **79 uniche**, zero duplicati.
- `source_record_id`: **79 unici**, zero duplicati.
- `NON_TRADE`: **50**.
- `ESITO_NON_VERIFICABILE`: **29**.
- Fill verificati: **0**; SL-first: **0**; TP-first: **0**.
- Win rate / Average R: **N/D**.

Nuove righe aggiunte:
1. `run:42438806862/classification:Argento` — candidato LONG bloccato, NON_TRADE.
2. `run:42438806862/telegram_watch_board/message:3718` — ACK Telegram, corpo non conservato e strumento non attribuibile, NON_TRADE.

Il timestamp in `sent_at_utc` del board #3718 è il timestamp del log di conferma API, non l'istante esatto della richiesta di invio.

## Limiti e prossimo controllo

- SPUTNIK: nessun monitor di mercato successivo a #42426077974 nell'elenco recente consultato; polling #42438101190 è distinto.
- GAGARIN: un nuovo run è avvenuto, ma l'intervallo precedente è stato 3h26m30s; servono ulteriori run per dimostrare il ripristino della cadenza.
- Tutti i prezzi GAGARIN sono stale/mercato chiuso; mancano quote timestamp, ticker risolti e scadenze.
- Nessun segnale ha entry/SL/TP/ATR completi e fill verificato; nessuna candela successiva dello stesso identico contratto utilizzabile.
- Nessuna prova di consegna Telegram al dispositivo; solo ACK API.
- Il polling GAGARIN resta separatamente da correggere tramite PR #175.

Prossimo controllo: verificare la scansione SPUTNIK successiva, almeno due o più run GAGARIN consecutivi per la cadenza, e alla riapertura dei mercati acquisire ticker esatto, timestamp OHLC, provider, mercato e scadenza prima di qualsiasi valutazione SL/TP.

**Ambito rispettato:** nessuna modifica a codice, workflow, strategia, filtri, scoring o rischio; nessun merge/deploy, ordine reale, segreto o configurazione Render modificati. Nessun servizio a pagamento o accesso Trading212. PAPER ONLY.
