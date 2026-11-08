# PRAVDA — Audit incrementale SPUTNIK / GAGARIN

**Cut-off:** 8 novembre 2026, 08:35:41 UTC (09:35:41 Europe/Rome)  
**Perimetro:** repository main, ultime run Actions di produzione, ledger PRAVDA, journal/feedback tracciati, codice outcome e PR aperte. Sola verifica; PAPER ONLY.

## 1. Esito sintetico

- Ultima run di produzione verificata SPUTNIK: [#42439632866](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42439632866), completata alle 02:42:14 UTC. Età al cut-off: **5h53m27s**.
- Ultima run di produzione verificata GAGARIN: [#42438806862](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42438806862), completata alle 02:30:28 UTC. Età al cut-off: **6h05m13s**.
- Entrambe le run risultano SUCCESS a livello GitHub Actions, ma non hanno prodotto artifacts. Il successo del job non dimostra un segnale valido, una persistenza durevole o la consegna Telegram sul dispositivo.
- Il ledger [PRAVDA 2026-11-08](pravda-signal-ledger-2026-11-08.csv) contiene **81 record**: SPUTNIK 33, GAGARIN 48. **81 firme uniche, 81 source ID unici, zero duplicati**. Rispetto al ledger 2026-11-07 (74 record) sono stati aggiunti 7 record, tutti NON_TRADE. Rispetto all'audit precedente delle 07:39 UTC il ledger resta invariato.
- Classificazione complessiva: **52 NON_TRADE, 29 ESITO_NON_VERIFICABILE**. Fill verificati 0; SL verificati 0; TP verificati 0. Win rate, average R e total R: **N/D**. I record NON_TRADE e NOT_EXECUTED non sono operazioni; i 29 non verificabili non sono 29 trade.
- Nessun backtest è stato eseguito. Non ci sono percorsi di candele successive sufficientemente identificati e verificabili per attribuire esiti SL/TP ai candidati correnti.

## 2. SPUTNIK — produzione e intelligence

**Run:** [#42439632866](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42439632866) — schedule, avvio 02:41:59 UTC, completamento 02:42:14 UTC, SUCCESS, zero artifacts.

### Evidenza della run
- SEC: HTTP 403, cooldown 21.600 secondi, filings=0.
- White House RSS: HTTPError.
- Public intelligence findings=0; nessuna nuova correlazione di mercato.
- La run ha comunque emesso due messaggi collegati alla stessa analisi GOLD:
  - Telegram message **729**: NEUTRAL / WATCH / NO_DIRECTION. Tecnica 5m UNAVAILABLE, nessuna directional news.
  - Telegram message **730**: NEUTRAL / NO_DIRECTION / NOT_EXECUTED; market label FUTURES_CONTINUOUS_FRONT_MONTH, ma scadenza esatta UNKNOWN.
- I due messaggi non sono due segnali indipendenti. Il valore score 100 nel messaggio 730 non conferisce validità operativa.
- Per entrambi: ticker runtime non risolto, provider e timestamp/età della quotazione non esposti, prezzo di riferimento assente, nessun entry/SL/TP/ATR. NARWHAL risulta NOT_CONFIGURED. L'indipendenza della serie continuous front-month non è verificata.
- Telegram API ha accettato i message_id 729 e 730. I timestamp generazione/ACK nei log differiscono di circa 1 ms, mentre i round-trip dichiarati sono 414/392 ms: la latenza end-to-end non è ricostruibile con certezza. L'ACK API non prova la visualizzazione sul dispositivo.

### Difetti dimostrati e PR esistenti
- Il workflow main [trump_tracker.yml](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/trump_tracker.yml) continua a passare i riferimenti ai secret GAGARIN_CLOUD_API_URL e GAGARIN_CLOUD_API_KEY al processo SPUTNIK. La separazione completa non è quindi ancora in produzione.
- [PR #147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147) rimuove il percorso di handoff e i riferimenti ai secret dal workflow. È OPEN, non merged; il branch è 5 commit ahead e 0 behind rispetto a main. Le due CI più recenti sul suo head 09833136 sono SUCCESS: ranking [#42463175953](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42463175953) e item-intelligence [#42463175954](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42463175954).
- [PR #148](https://github.com/andreameloni1984-sys/trump-trucker/pull/148) corregge la ripetizione delle raccomandazioni senza un nuovo item RSS individuale. È OPEN, non merged; CI ranking e item-intelligence SUCCESS sul head corrente, ma il branch è 2 ahead e 3 behind rispetto a main. Prima di qualsiasi merge va riallineato.
- [PR #144](https://github.com/andreameloni1984-sys/trump-trucker/pull/144) per la persistenza dello stato fuori da main e [PR #145](https://github.com/andreameloni1984-sys/trump-trucker/pull/145) per la provenienza quote restano OPEN e non merged. Le lacune di stato e quote provenance non sono quindi considerate risolte in produzione.

## 3. GAGARIN — produzione, quote e journal

**Run:** [#42438806862](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42438806862) — schedule, avvio 02:30:08 UTC, completamento 02:30:28 UTC, SUCCESS, zero artifacts.

### Quote e candidato
- La run mostra otto commodity: Soia, Grano, Mais, Brent, WTI, Oro, Argento e Rame. EUR/USD e GBP/USD sono contesto ausiliario.
- Tutte le commodity sono MARKET_CLOSED e le quote Yahoo sono stale: circa **112.524 s** per cereali e **102.923 s** per energia/metalli. La chiusura domenicale è coerente con il calendario; i valori non sono utilizzabili come prezzi freschi.
- Unico candidato direzionale: **Argento LONG / PAPER_WATCH**, probabilità 59, qualità 49,5, confidence 32. Bloccato da LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, CONFIDENCE_FAIL e FINAL_CONFLUENCE_FAIL. Quote age 102.922,9 s; ticker provider risolto, timestamp assoluto quote, mercato, expiry e reference price non esposti. Nessun entry/SL/TP/ATR e nessuna paper entry.
- Il riepilogo della run registra signals=0, open=0, closed=0, recorded entries=0, updated outcomes=0 e nuovi feedback signals=0.
- Telegram message **3718** è stato accettato dall'API (round-trip dichiarato 560 ms), ma il body non è conservato. Non si può attribuire con certezza al candidato Argento né a un altro strumento; non è un ingresso.

### Universo e stato del journal
- Il main [commodities/universe.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities/universe.py) abilita Oro, Argento, Rame, WTI, Brent, Grano, Mais, Soia e due coppie FX ausiliarie. L'universo operativo esclude l'FX, ma include ancora Argento e non include Platino/Palladio: non coincide con il paniere commodity attualmente richiesto (Oro, Rame, Platino, Palladio, WTI, Brent, Grano, Mais, Soia).
- [journal.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/journal.csv): 11 righe del 17 ottobre, tutte senza segnale/structural touch.
- [paper_trade_log.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/paper_trade_log.csv): un solo ticket legacy WTI P0001 LONG (entry 96,24; SL 89,37; TP1 103,11; TP2 106,55), senza signal ID, fill, provider, ticker quotazione, timestamp quote, mercato o scadenza. Non è prova di esecuzione.
- [data/paper_open.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/data/paper_open.json) conserva P0001 come OPEN, mentre [data/day_registry.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/data/day_registry.json) ha positions=[] e la run corrente riporta open=0. È una discrepanza legacy/runtime, non un trade verificato.
- [commodities_prediction_log.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities_prediction_log.json) contiene 981 record; 945 PENDING e 36 NEUTRALE, ultimo record del 15 settembre. PENDING e score non dimostrano fill.
- gagarin_feedback.csv non è presente nel main tracciato. La workflow [gagarin-monitor.yml](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml) non carica artifacts né committa il journal operativo; il runner GitHub è effimero. La persistenza su database non è stata dimostrata in questa verifica.

### Difetto nel calcolo degli outcome
- In [engine/feedback.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py), il fingerprint del feedback usa symbol, direction, timeframe, livelli e timestamp barra, ma non provider, ticker quotazione risolto, market type, contratto/scadenza o quote timestamp.
- L'abbinamento delle candele successive avviene per symbol+timeframe, non per identità esatta di provider/strumento/contratto.
- Se la stessa candela OHLC tocca SL e TP, main assegna STOP per convenzione. Per la regola PRAVDA richiesta, l'ordine intrabar non è dimostrabile: l'esito deve essere **ESITO_NON_VERIFICABILE**, non STOP.
- [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) contiene la correzione proposta per identità esatta e ambiguità same-candle. È OPEN e non merged; main conserva ancora il comportamento descritto.

## 4. PR e Actions GAGARIN — stato delle correzioni

- [PR #231](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/231): report direzionale col Governor, calendario economico e routing news. OPEN, non merged; i test sul head 047abbc sono SUCCESS. Il branch descrive ancora un universo di otto commodity con Argento e senza Platino/Palladio. Il calendario non è quindi considerato attivo sul main.
- [PR #223](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): scan M5 separata ogni 5 minuti, observation-only, sette strumenti (Gold, Copper, WTI, Brent, Wheat, Corn, Soybean). OPEN, non merged; esclude Argento ma omette Platino e Palladio e non produce entry/SL/TP, journal o alert Telegram. Non equivale al monitor operativo completo richiesto.
- [PR #225](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225): offset della schedule provider-heavy mantenendo 15 minuti. OPEN, non merged.
- [PR #221](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221) e [PR #212](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/212): rimozione Forex, ma universo a otto con Argento; OPEN, non merged.
- [PR #234](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/234) e [PR #235](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/235): journal/feedback CFD Trading 212 e persistenza separata. OPEN, non merged e stacked; non rendono la pipeline end-to-end pronta. La descrizione di #235 dichiara registry vuoto e nessun feed/quote/Entry/SL/TP aggiunto.
- [PR #236](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/236) e [PR #237](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/237): evidenza catalogo CFD e binding simbolo. OPEN, non merged; i workflow di test visibili sui rispettivi head sono SUCCESS. Non sono una prova di feed quote né di accesso a un conto Trading 212.

## 5. Cadenza effettiva delle GitHub Actions

- SPUTNIK main dichiara cron `2-59/5 * * * *`, ma l'ultima collector run è #287 alle 02:41:59 UTC. Le precedenti #286 e #285 sono alle 23:37:18 e 20:07:13 UTC. La schedule osservata è quindi a intervalli di ore, non di 5 minuti. Ultimo Telegram Polling: run #48 alle 02:20:16 UTC.
- GAGARIN main dichiara cron `*/15 * * * *`, ma le ultime run sono #167 alle 02:30:08, #166 alle 23:03:38 e #165 alle 19:38:07 UTC: intervalli di circa 3h25–3h26, non 15 minuti.
- Le run elencate sono concluse SUCCESS; il gap è tra le run schedule osservate, non la durata del singolo job. PR #225 propone un offset ma non è integrata. La M5 scan di PR #223 non è integrata e sarebbe observation-only.

## 6. Conclusione e prossimo controllo

1. Nessun segnale operativo verificato e nessun esito SL/TP verificabile in questo cut-off. Tutti i candidati correnti sono bloccati, neutrali o privi di identità/quotazione sufficiente.
2. Non promuovere il ticket legacy P0001, i record PENDING, gli score o i messaggi WATCH/NOT_EXECUTED a trade.
3. Correzioni già proposte ma non integrate: SPUTNIK #147/#148/#144/#145; GAGARIN #192/#231/#223/#225/#221/#212. Non dichiararle risolte prima del merge e della verifica post-merge.
4. Prossimo controllo: verificare la successiva run schedule di entrambi i main, il suo log integrale e l'eventuale artifact/journal persistito; accettare un outcome solo dopo aver identificato lo stesso provider, ticker, mercato e contratto/scadenza e aver ordinato temporalmente le candele successive.

**Modifiche effettuate da PRAVDA:** solo questo rapporto Markdown. Nessun codice, strategia, filtro, score, rischio, secret, Render, ordine, merge o deploy modificato. Il ledger CSV resta invariato perché non sono emersi nuovi record eleggibili.
