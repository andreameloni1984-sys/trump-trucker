# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-09 00:43 UTC (01:43 Europe/Rome)**

## Sintesi

Sono state esaminate le ultime esecuzioni produttive disponibili, i relativi job log, i workflow, gli artefatti di journal/feedback, il ledger precedente e le PR aperte.

**Nuovo esito:** quattro notifiche/artefatti sono stati aggiunti allo storico come NON_TRADE. Non è stato individuato alcun nuovo fill né alcun esito SL/TP verificabile.

## 1. Ledger PRAVDA

File cumulativo aggiornato: [pravda-signal-ledger-2026-11-09.csv](pravda-signal-ledger-2026-11-09.csv).

| Indicatore | Valore |
|---|---:|
| Record | 98 |
| SPUTNIK | 45 |
| GAGARIN | 53 |
| Firme uniche | 98 |
| Source ID unici | 98 |
| Duplicati | 0 |
| NON_TRADE | 69 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |

Le quattro nuove righe sono identificabili senza ambiguità tramite run ID e Telegram message ID:
- SPUTNIK run 42537803167, messaggio 743;
- SPUTNIK run 42537803167, messaggio 744;
- SPUTNIK run 42537803167, messaggio 745;
- GAGARIN run 42538235058, messaggio 3727.

I messaggi 743 e 744 sono due comunicazioni della stessa analisi GOLD, non due operazioni. Il 745 è un brief informativo; il 3727 è un WATCH pre-alert senza corpo conservato. Tutti e quattro sono NON_TRADE. Nessun nuovo record è stato classificato come fill.

### Dettaglio dei nuovi record

**SPUTNIK #743 — bias preliminare GOLD**
- Generazione: 2026-11-08 23:59:54.8425373 UTC.
- API Telegram accepted: 23:59:54.8438627 UTC; round-trip 401 ms.
- Bias SHORT; tecnica SHORT 5m; momentum indicato a -0,061% negli ultimi 15 minuti.
- Allineamento notizie: NO_DIRECTIONAL_NEWS.
- Nessun ticker risolto, provider, timestamp della quotazione, mercato/contratto esatto o livelli operativi.
- Stato: EARLY_BIAS, non ingresso confermato; NON_TRADE.

**SPUTNIK #744 — GOLD EARLY_SETUP**
- Generazione: 2026-11-08 23:59:54.8439129 UTC.
- API Telegram accepted: 23:59:54.8449792 UTC; round-trip 396 ms.
- Direzione dichiarata: SHORT; entry 4069.1001; SL 4071.9929; TP1 4066.2073; TP2 4063.3145; ATR 1.9285.
- Stato esplicito: NOT_EXECUTED.
- Il titolo dice CFD, mentre il corpo dichiara future continuo front-month; scadenza esatta non verificata.
- NARWHAL non configurato; provider, ticker effettivo e timestamp della quotazione non esposti; indipendenza del controllo spot/futures non verificata.
- Il D-L-A è contemporaneamente indicato come NEUTRAL / NO_DIRECTION / NOT_ASSESSED, in contrasto con il bias SHORT del messaggio 743.
- Score 100 non rende il setup operativo. I livelli non possono essere valutati con candele successive perché manca l'identità della serie e del contratto.
- Esito: NON_TRADE, non STOP e non TP.

**SPUTNIK #745 — brief informativo**
- API Telegram accepted: 2026-11-08 23:59:54.8454315 UTC; round-trip 364 ms.
- Il titolo riporta “BRIEF ORE 05:00”, ma l'invio osservato corrisponde alle 00:59:54 Europe/Rome del 9 novembre.
- Il brief riporta analoghi storici e assenza di operazioni Form 4 documentate; non è un segnale di mercato.
- Il disallineamento tra etichetta 05:00 e ora effettiva è stato segnalato al reparto con [issue #151](https://github.com/andreameloni1984-sys/trump-trucker/issues/151).

**GAGARIN #3727 — WATCH pre-alert**
- API Telegram accepted: 2026-11-09 00:05:07.2828735 UTC; round-trip 403 ms.
- Il corpo del messaggio non è conservato nel job log.
- Strumento, ticker, mercato, scadenza, provider, direzione e livelli non attribuibili.
- La stessa run dichiara zero entrate e zero nuovi forecast.
- Esito: NON_TRADE.

Per tutti gli ACK Telegram si attesta soltanto l'accettazione dell'API; non è stata verificata la visualizzazione sul dispositivo.

## 2. SPUTNIK — run produttiva #292

[GitHub Actions #292](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537803167) — SUCCESS, avviata 2026-11-08 23:59:46 UTC e conclusa alle 23:59:58 UTC.

Job: `sputnik`, job ID 128905894291.
- 30 test di regressione superati.
- Nel blocco di test compaiono OSError simulati per WHITE_HOUSE, TRUTH_ARCHIVE e OGE e un test di handoff GAGARIN; tali righe precedono il comando `python trump_tracker.py` e non sono errori runtime da attribuire al collector.
- Nel runtime effettivo: SEC HTTP 403 con cooldown 21.600 secondi; filing 0; estrazione transazioni 0; White House RSS `https://www.whitehouse.gov/feed/` HTTPError.
- Intelligence scan: 1 finding, ma nessun catalizzatore USA direzionale dichiarato nel messaggio GOLD.
- GAGARIN forwarding: 0 ms; URL e API key di handoff vuote nel runtime. La “confirmation received” compare nei test, non come conferma di un handoff produttivo.
- Telegram API accepted per i messaggi 743, 744 e 745.

### Persistenza SPUTNIK

Lo step “Persist SPUTNIK state” ha creato il commit `15f34dfe1e9866755bc2604e58ce8b582e34b5ac` e lo ha spinto su `main` alle 23:59:56 UTC. Il workflow corrente committa quindi `sputnik_state.json` direttamente su main. La separazione della persistenza proposta in PR #144 non risulta dimostrata in produzione.

### Polling SPUTNIK

[Polling #52](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537592091) — SUCCESS, 23:56:54–23:57:02 UTC. Il log riporta `Pending updates: 0`. Non risultano aggiornamenti pendenti; ciò non certifica la consegna sul dispositivo.

### PR SPUTNIK

- [#149](https://github.com/andreameloni1984-sys/trump-trucker/pull/149): MERGED; brief spostato al primo scan, non a un'ora fissa. Il testo continua però a mostrare “ORE 05:00”; issue #151 aperta per chiarire l'etichetta.
- [#150](https://github.com/andreameloni1984-sys/trump-trucker/pull/150): OPEN; 2 commit avanti e 2 indietro rispetto al main attuale; due CI PR SUCCESS. Evita di ripetere raccomandazioni senza nuovo item RSS; non integrata.
- [#131](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): OPEN; 1 avanti e 1 indietro; due CI PR SUCCESS. Propone `/news/feed/`, ma il runtime #292 usa ancora `/feed/` e riceve HTTPError.
- [#147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147) e [#145](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): ancora aperte; separazione GAGARIN e diagnostica delle quotazioni non dimostrate su main.

## 3. GAGARIN — run produttiva #171

[GitHub Actions #171](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42538235058) — SUCCESS, avviata 2026-11-09 00:04:51 UTC e conclusa alle 00:05:10 UTC.

Job ID 128907219566. Configurazione osservata: PAPER_TRADING_ONLY=1; MONITOR_INTERVAL_MINUTES=15; MIN_ENTRY_PROBABILITY=40, MIN_ENTRY_QUALITY=30, MIN_ENTRY_CONFIDENCE=35, MIN_ENTRY_RR=2.5. Nessuna modifica PRAVDA a tali parametri.

### Quotazioni e blocchi

Otto commodity sono classificate STALE da YAHOO:
- Soia: 189.906,8 secondi (circa 52,75 ore);
- Grano: 189.906,5 secondi;
- Mais: 189.909,6 secondi;
- Argento: 655,0 secondi;
- Oro: 611,0 secondi;
- Brent: 605,4 secondi;
- WTI: 604,2 secondi;
- Rame: 643,1 secondi.

Per tutte il log indica `ALL_PROVIDER_CANDLES_STALE` e blocco `LIVE_DATA_NOT_FRESH`. Il log espone l'età ma non il timestamp assoluto della quotazione né un ticker/contratto completo.

EUR/USD e GBP/USD risultano LIVE tramite BIQUOTE, rispettivamente 6,3 e 6,9 secondi; sono però “CONTESTO FX — NON OPERATIVO”, bloccati da trigger non confermato, mismatch di direzione e RR1 fail.

WTI compare LONG in classifica, ma resta PAPER_WATCH ed è bloccato da dati non freschi, trigger non confermato/mismatch e RR fail. Nessun setup supera i blocchi.

### Journal e feedback

La run dichiara:
- Recorded entries: 0;
- Updated open outcomes: 0;
- New feedback signals: 0;
- New additional live forecasts: 0;
- signals=0, open=0, closed=0.

Nel runtime `DATABASE_URL` è vuota. `gagarin_feedback.csv` restituisce 404 su main. Il workflow dichiara che i journal paper non devono essere pubblicati nel repository pubblico e che la persistenza sarà riattivata dopo verifica dello storage privato.

Artefatti pubblici ancora presenti:
- `journal.csv`: 11 righe del 17 ottobre, tutte “nessun segnale”;
- `paper_trade_log.csv`: un WTI LONG del 8 ottobre marcato LEGACY_IMPORT/OPEN, senza provider, quotazione o outcome;
- `position.json`: vecchia posizione Heating Oil LONG del 15 settembre;
- `commodities_monitor_state.json`: timestamp 17 settembre, stato storico non corrente.

Questi record legacy non provano fill e non sono stati conteggiati come operazioni.

### Archivio previsioni

`commodities_prediction_log.json` contiene 981 record: 945 PENDING e 36 NEUTRALE. Le etichette action includono 21 “COMPRA ORA”, tutte PENDING; tuttavia solo 15 hanno `operational_signal=LONG`, mentre 6 hanno il campo assente. Score/action non equivalgono a esecuzione o outcome.

## 4. Motore outcome e identità contrattuale

Su main, `engine/feedback.py` controlla prima lo stop e poi i target: una candela OHLC che tocca entrambi viene registrata STOP. L'ordine intrabar non è ricavabile da OHLC; secondo il protocollo PRAVDA deve restare ESITO NON VERIFICABILE.

[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) è OPEN, 6 commit avanti e 6 indietro rispetto a main; sei CI associate al branch risultano SUCCESS. La PR introduce campi provider/ticker/mercato/scadenza e il trattamento `SAME_CANDLE_SL_TP_AMBIGUITY` come ESITO NON VERIFICABILE.

Rimane però una lacuna dimostrata: nella funzione `_market_contract_match()` del branch #192 si confrontano quote symbol, market type e contract month/expiry, ma non si confronta effettivamente `quote_provider` della riga con il provider dello stato/candele. Il provider entra nella firma del segnale, ma non nel matching delle serie successive.

[PR #238](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/238) è DRAFT e punta a un branch feature, non direttamente a main; il confronto con main mostra 25 commit avanti e 4 indietro per il branch base. Il registry CFD contiene `instruments: []`; il modulo dichiara che non recupera quotazioni né autentica la provenienza del feed. È scaffolding d'identità, non prova di accesso o feed Trading 212.

## 5. Frequenza effettiva delle Actions

Workflow configurati:
- SPUTNIK collector: cron `2-59/5`;
- SPUTNIK polling: `*/5`;
- GAGARIN monitor: `*/15`.

Ultime due run produttive osservate:
- SPUTNIK #291 20:35:50 UTC → #292 23:59:46 UTC: gap 3h23m56s;
- polling #51 20:27:04 UTC → #52 23:56:54 UTC: gap 3h29m50s;
- GAGARIN #170 20:41:00 UTC → #171 00:04:51 UTC: gap 3h23m51s.

Al cut-off dell'audit erano trascorsi circa 43m23s dal collector SPUTNIK, 46m15s dal polling e 38m18s dal monitor GAGARIN. Le CI delle PR non sono scansioni produttive. La causa dei gap non è dimostrata.

## 6. Esiti e statistiche

Non è disponibile alcun campione di fill verificati. Nessuna candela successiva è stata abbinata con certezza allo stesso provider, ticker, mercato e contratto del messaggio #744; per gli altri nuovi record non esiste neppure una proposta di trade. Non si attribuiscono SL o TP.

- Fill verificati: 0.
- SL verificati: 0.
- TP verificati: 0.
- Win rate, average R e total R: N/D.

I 29 record storici ESITO_NON_VERIFICABILE restano tali. I quattro nuovi record sono NON_TRADE.

## 7. Fonti consultate

- [SPUTNIK run #292 e job log](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537803167)
- [SPUTNIK polling #52](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537592091)
- [GAGARIN monitor #171 e job log](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42538235058)
- [SPUTNIK workflow](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/trump_tracker.yml)
- [SPUTNIK polling workflow](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/telegram-polling.yml)
- [GAGARIN monitor workflow](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml)
- [GAGARIN feedback engine su main](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py)
- [GAGARIN PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192)
- [GAGARIN PR #238](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/238)
- [SPUTNIK issue #151](https://github.com/andreameloni1984-sys/trump-trucker/issues/151)

## 8. Prossimo controllo

1. Verificare le successive run programmate e misurare nuovamente i gap.
2. Verificare che il nuovo endpoint White House sia effettivamente usato in produzione dopo un'eventuale integrazione.
3. Richiedere per ogni candidato GOLD ticker, provider, timestamp quotazione, mercato e scadenza coerenti; non valutare i livelli #744 prima di tali prove.
4. Verificare il recepimento del provider matching nella PR #192 e la sua integrazione.
5. Verificare che il journal privato abbia prova di scrittura e successiva lettura, non soltanto una variabile configurata.
6. Riconciliare i record legacy soltanto con prove di esecuzione e serie prezzi esatta.

**Perimetro rispettato:** nessun codice applicativo modificato; nessuna strategia, filtro, punteggio o rischio modificato; nessun merge/deploy, ordine reale, modifica a secret o Render. Nessun servizio a pagamento. Nessun accesso Trading 212 o consegna Telegram sul dispositivo dichiarati. PAPER ONLY.
