# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-06 23:57:23 UTC (2026-11-07 00:57:23 Europe/Rome)**

## Sintesi esecutiva

- È comparso un nuovo collector SPUTNIK: [#42311247999](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42311247999), avviato alle 23:20:35 UTC, SUCCESS. Ha prodotto un candidato GOLD LONG in stato EARLY_BIAS/NOT_EXECUTED, senza livelli operativi e senza provenienza completa della quotazione.
- È comparso un nuovo monitor GAGARIN: [#42304574886](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42304574886), avviato alle 22:25:16 UTC, SUCCESS. Tutte le otto commodity erano stale; nessuna entrata e nessun outcome aggiornato.
- I monitor hanno ripreso a eseguire almeno una volta, ma non rispettano la cadenza dichiarata: gap tra collector SPUTNIK 4h58m11s e tra monitor GAGARIN 4h43m57s.
- Ledger aggiornato da 35 a 40 record: 40 firme uniche, zero duplicati.
- Nuovi record: un candidato SPUTNIK GOLD EARLY_BIAS/NOT_EXECUTED; tre WATCH commodity GAGARIN bloccati; un pre-alert board GAGARIN non attribuibile.
- Nessun fill, SL o TP verificato. Campione di trade verificabili: 0; win rate e average R: N/D.
- Il codice feedback su main continua a non vincolare l'outcome a ticker/mercato/scadenza; PR #192 contiene la correzione proposta, ma è aperta e divergente rispetto a main.

## 1. GitHub Actions e continuità

Sono state esaminate le 100 Actions più recenti per ciascun repository, distinguendo run di mercato, polling, riepiloghi e test PR.

### SPUTNIK
- Ultimo collector: [#42311247999](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42311247999), 23:20:35–23:20:45 UTC, SUCCESS.
- SHA eseguito: `efe601a7af853660da1eca4d4a512533a9a72550`.
- Collector precedente: [#42270098789](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42270098789), 18:22:24 UTC. Gap: 4h58m11s, nonostante cron dichiarato ogni 5 minuti.
- Età dell'ultimo collector al cut-off: 36m48s.
- Il run ha effettuato 30 test di regressione con esito OK prima della scansione. Il test stampa un message_id simulato #731: non è una notifica di produzione e non è stato registrato.
- Dopo il collector, lo step di persistenza ha creato e inviato il commit `f503a7b507868dcfb5bf4f76ca81aadbf906372e` su main. Questo commit è successivo allo SHA con cui il run era partito.

### GAGARIN
- Ultimo monitor: [#42304574886](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42304574886), 22:25:16–22:25:36 UTC, SUCCESS.
- SHA eseguito e main al momento del run: `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`.
- Monitor precedente: [#42263910777](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42263910777), 17:41:19 UTC. Gap: 4h43m57s, nonostante cron dichiarato ogni 15 minuti.
- Età dell'ultimo monitor al cut-off: 1h32m07s.
- Il polling GAGARIN più recente individuato resta [#42289526533](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42289526533), FAILURE: conflitto API 409 webhook attivo/polling. Il monitor #423045 ha comunque inviato un messaggio outbound; ciò non dimostra che il polling sia risolto.

I gap sono dimostrati dai run disponibili; la causa tecnica della mancata schedulazione non è determinata.

## 2. SPUTNIK — nuovo candidato GOLD LONG

Il run #42311247999 ha prodotto i messaggi collegati #713 (analisi) e #714 (CFD). Sono registrati come un solo candidato.

- Firma ledger: `PRAVDA-SPUTNIK-CFD-RUN42311247999-20261106T232043Z-GOLD-LONG-EARLY-BIAS`.
- Generazione CFD: 2026-11-06 23:20:43.370895 UTC.
- ACK API Telegram #714: 23:20:43.3721907 UTC; round-trip dichiarato 383 ms. È accettazione API, non prova di visualizzazione sul dispositivo o di esecuzione.
- Strumento: GOLD.
- Mapping configurato: GC=F; ticker runtime non confermato.
- Mercato: future continuo front-month; scadenza esatta UNKNOWN.
- Provider, timestamp e anzianità della quotazione: non esposti.
- Bias CFD: LONG; tecnica LONG solo tecnica; D-L-A NEUTRAL/NO_DIRECTION e NOT_ASSESSED.
- Messaggio analisi #713: bias preliminare NEUTRAL, tecnica UNAVAILABLE per dati 5m insufficienti/non aggiornati, nessuna notizia direzionale.
- Score 70/100; nessuna entry, SL, TP o ATR emessi perché non era disponibile una quotazione futures fresca o ATR valido.
- Stato: EARLY_BIAS / NOT_EXECUTED.

**Esito: ESITO NON VERIFICABILE; non è un trade.** Mancano contratto esatto, provider/timestamp della quota e livelli operativi; non sono disponibili candele successive dello stesso contratto.

Altre osservazioni:
- Scansione pubblica: findings=1. Il record TRUTH_ARCHIVE più recente è una pagina archivio a livello pagina, senza titolo o data di pubblicazione specifica; è una potenziale correlazione, non un catalizzatore individuale verificato.
- SEC: HTTP 403; White House RSS: HTTPError; i log di test segnalano WHITE_HOUSE/TRUTH_ARCHIVE/OGE non disponibili.
- NARWHAL API key assente; NARWHAL REF NOT_CONFIGURED; indipendenza upstream non dimostrata.
- GAGARIN forwarding=0ms perché GAGARIN_CLOUD_API_URL/API_KEY non sono configurati.
- I record RSS 43495 e 43496 restano nello stato: il 43495 (pubblicato 12:01:50Z, rilevato 18:22:30Z) ha un ritardo di circa 6h20m40s e il termine GOLD è stato classificato METALS nel contesto Super Intelligence/AI; il 43496 (pubblicato 18:05:27Z, rilevato 18:22:30Z) ha circa 17m04s di ritardo.
- Lo stato SPUTNIK è ora persistito: `sputnik_state.json` aggiornato alle 23:20:41.952764Z, 500 record in intelligence_history, zero eventi attivi. Il run ha committato la persistenza su main. Questo aggiorna il precedente snapshot che risultava vuoto; non prova che la schedulazione sia regolare.

## 3. GAGARIN — prezzi e WATCH osservati

Il run #42304574886 dichiara 8 commodity operative e 2 strumenti Forex ausiliari, non operativi.

### Quotazioni commodity

| Strumento | Provider | Età al monitor |
|---|---|---:|
| Brent | Yahoo | 1.547,5 s |
| WTI | Yahoo | 1.533,2 s |
| Soia | Yahoo | 11.133,1 s |
| Oro | Yahoo | 1.530,7 s |
| Grano | Yahoo | 11.132,7 s |
| Mais | Yahoo | 11.135,9 s |
| Argento | Yahoo | 1.531,7 s |
| Rame | Yahoo | 1.542,9 s |

Tutte le otto commodity sono stale. Cinque quotazioni hanno circa 25m30s di anzianità; grano, mais e soia superano 3h05m. Il log riporta `ALL_PROVIDER_CANDLES_STALE`; timestamp della quotazione, ticker esatto, mercato e scadenza non sono esposti.

### Candidati direzionali visibili nella classifica

| Strumento | Direzione | Prob. | Quality | Confidence | Blocchi principali |
|---|---|---:|---:|---:|---|
| WTI | SHORT | 66 | 57,5 | 37 | stale, trigger non confermato, mismatch direzionale, confluence fail |
| Mais | LONG | 63 | 52,5 | 35 | stale, trigger non confermato, mismatch direzionale, RR_FAIL |
| Argento | LONG | 59 | 49,5 | 32 | stale, trigger non confermato, mismatch direzionale, RR1_FAIL, confidence fail |

Nessuno dei tre ha entry/SL/TP/ATR o autorizzazione di ingresso. Sono stati aggiunti come WATCH bloccati, con outcome NON_TRADE, non come operazioni.

Brent, soia, oro, grano e rame non presentano una direzione valida e non hanno livelli. EUR/USD e GBP/USD risultano contesto FX non operativo: Yahoo LIVE da circa 5 secondi, mentre BiQuote era stale da circa 1.833 secondi. Non sono conteggiati come segnali commodity.

### Pre-alert Telegram #3710
- Generazione del monitor: 22:25:29.422938 UTC.
- API ACK #3710: 22:25:33.877068 UTC, round-trip 358 ms.
- Il corpo del messaggio non è conservato nel log: non è possibile attribuire con certezza strumenti o direzioni al messaggio. L'ACK API non dimostra consegna al dispositivo.
- Registrato come board pre-alert non attribuibile, NON_TRADE.

Il run riporta: `Recorded entries: 0`, `Updated open outcomes: 0`, `New feedback signals: 0`, `New additional live forecasts: 0`, `signals=0 open=0 closed=0`.

Configurazione stampata dal run, registrata senza modificarla: PAPER_TRADING_ONLY=1; MIN_ENTRY_PROBABILITY=40; MIN_ENTRY_QUALITY=30; MIN_ENTRY_CONFIDENCE=35; MIN_ENTRY_RR=2.5; MAX_ENTRY_STOP_ATR=2.5; SL_STRUCTURE_BUFFER_ATR=0.15; SL_MIN_ATR=0.80; MONITOR_INTERVAL_MINUTES=15; GAGARIN_FOREX_ON_DEMAND=0. Il run continua a mostrare i due FX solo come contesto ausiliario.

## 4. Journal e feedback GAGARIN

- `journal.csv`: 11 righe del 17 ottobre, tutte con “nessun segnale”.
- `paper_trade_log.csv`: una posizione WTI LONG legacy del 2026-10-08, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55; nessun fill o outcome dimostrato, provider/ticker/contratto mancanti.
- `data/paper_open.json` era già stato identificato come la stessa posizione WTI P0001, non un secondo trade.
- `commodities_prediction_log.json`: 981 record; ultimo timestamp 2026-09-15T15:45:04.462276Z; gli ultimi record sono PENDING e non provano esecuzione.
- `gagarin_feedback.csv`: non presente su main (404).
- `DATABASE_URL`: vuoto nel run; persistenza PostgreSQL non dimostrata.

## 5. Verifica del motore outcome e PR esistenti

Il file attivo `engine/feedback.py` su main ha blob SHA `41bec9bfab031c8dbf71121cd69d0e9b4c4f663f`. Il codice attuale:
- abbina gli stati per simbolo e timeframe, con fallback al solo simbolo se esiste un solo stato;
- non conserva né verifica quote_symbol, market_type, contract_month o contract_expiry;
- se SL e TP sono toccati nella stessa candela, assegna STOP;
- se più TP sono toccati nella stessa candela, usa `idx = max(hit_targets)`, scegliendo il target più alto senza prova dell'ordine intrabar.

### PR #192
[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) è OPEN, non draft e non merged. Head `295dba4b074e564a4c11aa3fca136a8e4360672c`; base `c93906a2a4b28d60fd58c600b51cd3c05929f89d`. Rispetto a main `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`, il confronto è diverged: 6 commit ahead, 3 behind.
- La PR aggiunge provider/ticker/mercato/scadenza e matching del contratto.
- La PR propone ESITO NON VERIFICABILE se SL e TP sono entrambi toccati nella stessa candela.
- Sei run CI associati al suo head risultano SUCCESS, ma sono del 5 novembre (primo run #41981315423 alle 06:34:25Z): non sono una verifica recente su main.
- La patch continua a usare `idx = max(hit_targets)`: il caso di più TP nella stessa candela non è risolto.

PR correlate:
- GAGARIN #97 (same-bar ambiguo), #98 (primo TP), #94 (coverage outcome): OPEN/DRAFT.
- GAGARIN #221 (rimozione rotte FX residue): OPEN/DRAFT; le sei suite recenti sul suo head `264e3ee3...` sono SUCCESS, ma main continua a mostrare 8 commodity + 2 FX ausiliari.
- GAGARIN #175 (webhook/polling): OPEN; il polling 409 su main resta l'ultima esecuzione osservata.
- SPUTNIK #145 (provenienza quotazioni): OPEN, non merged; il run #42311247999 continua a non esporre provider/timestamp/età del prezzo.
- SPUTNIK #144 (persistenza stato): OPEN, non merged; nel frattempo il workflow ha effettivamente persistito lo stato su main con commit `f503a7b...`.

## 6. Ledger PRAVDA e statistiche

File: `reports/pravda-signal-ledger-2026-11-06.csv`
- Record dati: 40.
- Firme uniche: 40.
- Duplicati: 0.
- Esito `ESITO_NON_VERIFICABILE`: 29 record.
- `NON_TRADE`: 11 record.
- Nuovi record aggiunti in questo audit: 5.
- Fill verificati: 0; SL verificati: 0; TP verificati: 0.
- Campione di trade con outcome verificabile: 0; win rate e average R: N/D.

I 29 record ESITO_NON_VERIFICABILE non sono 29 trade eseguiti: includono candidati NOT_EXECUTED e predizioni storiche senza prova di fill. I record NON_TRADE sono WATCH/pre-alert o artefatti non operativi.

Ledger blob SHA dopo aggiornamento: `ed76e1f4af5ed2ac586244527c99460a051345b2`.
Commit di aggiornamento ledger: `b41a76a92d68c0408a4ae503dfb232519eda054f`.

## 7. Fonti consultate, limiti e prossimo controllo

Fonti consultate:
- Actions e log: SPUTNIK #42311247999 e GAGARIN #42304574886; GAGARIN polling #42289526533.
- Actions CI e metadati PR: SPUTNIK #144/#145; GAGARIN #94/#97/#98/#175/#192/#221.
- Stato SPUTNIK `sputnik_state.json`, ledger PRAVDA, GAGARIN `journal.csv`, `paper_trade_log.csv`, `commodities_prediction_log.json`, `engine/feedback.py`.
- Nessun servizio a pagamento; nessun accesso Trading212; nessuna prova di consegna Telegram al dispositivo.

Limiti:
- Non sono state reperite candele successive dello stesso identico contratto futures per alcun candidato.
- Mancano ticker runtime, scadenze, timestamp/provider delle quotazioni e livelli operativi per il nuovo candidato SPUTNIK.
- GAGARIN non ha registrato nuove entrate o outcome; il feedback persistente non è leggibile dal repository e il database non era configurato nel run.
- Gli ACK Telegram dimostrano l'accettazione API, non la visualizzazione sul dispositivo.

Prossimo controllo:
1. Verificare la continuità dei monitor dopo i run #42311247999 e #42304574886.
2. Verificare quote fresche con ticker, provider, timestamp, mercato e scadenza.
3. Verificare che PR #192 venga riallineata a main e che il caso multi-TP intrabar sia trattato senza attribuire il target più alto.
4. Verificare il polling Telegram separatamente dall'invio outbound.
5. Aggiornare il ledger solo con nuove firme; valutare outcome solo su candele successive dello stesso contratto.

**Perimetro:** audit/documentazione soltanto. Nessun codice bot, strategia, filtro, punteggio o rischio modificato; nessun merge, deploy o rerun; nessun ordine reale; nessuna modifica a Render o segreti. PAPER ONLY.
