# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-09 14:51:39 UTC (15:51:39 CET)**

## Perimetro e metodo

Verifica read-only tramite GitHub REST/connector sui repository:

- [SPUTNIK — andreameloni1984-sys/trump-trucker](https://github.com/andreameloni1984-sys/trump-trucker)
- [GAGARIN — andreameloni1984-sys/commodity-news-scanner](https://github.com/andreameloni1984-sys/commodity-news-scanner)

Consultati: ultime 100 Actions per repository; metadati, job e log delle run produttive rilevanti; run del daily summary; PR aperte e relativi check; commit di main; workflow, universo, prediction log, journal, paper positions e motore feedback; ledger PRAVDA precedente.

Nessun feed a pagamento, accesso broker, secret, Render, merge, deploy o ordine. Nessuna modifica al codice applicativo.

## 1. Registro cumulativo PRAVDA

Ledger ereditato senza modifiche:

- File: `reports/pravda-signal-ledger-2026-11-09.csv`
- Blob SHA: `1acbe2994b6147a4d2fdd39108cf46f499fd6265`
- Record: **103**
- Firme uniche: **103**
- Source ID unici: **103**
- Duplicati: **0**
- Nuovi segnali operativi da aggiungere: **0**

Il nuovo messaggio SPUTNIK #749 è un daily summary, non un segnale: non viene aggiunto al ledger dei segnali.

Statistiche operative:
- Fill verificati: **0**
- SL verificati: **0**
- TP verificati: **0**
- Campione di trade verificabili: **0**
- Win rate / average R / total R: **N/D**

Non esistono candele successive con identità completa di strumento, mercato, provider e contratto per certificare gli esiti dei livelli SPUTNIK #748 o della candidata GAGARIN Soia.

## 2. GitHub Actions — distinzione tra collector e summary

### SPUTNIK

| Workflow | Ultima run schedule | Esito | Intervallo al cut-off |
|---|---|---|---:|
| Collector `trump_tracker.yml` | [#293](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770), 06:01:41–06:01:51 UTC | SUCCESS | **8h49m58s** |
| Telegram polling | [#53](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570062235), 05:55:47–05:55:56 UTC | SUCCESS | **8h55m52s** |
| Daily summary | [#12](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42638308297), 14:48:35–14:48:43 UTC | SUCCESS | 3m04s |

Precisazione importante: dopo il collector #293 è stata eseguita una schedule del **daily summary #12**. Non è una nuova scansione di mercato e non dimostra che il collector sia ripartito.

Il job del daily summary registra un ACK Telegram Bot API:
- message_id **749**;
- timestamp log: **2026-11-09 14:48:40.945 UTC**.

Il corpo del messaggio non è riportato nel log. #749 resta quindi un evento informativo non attribuibile a uno strumento e non un segnale. L'ACK API non prova la visualizzazione sul dispositivo.

Le ultime 100 Actions consultate non mostrano un collector o polling schedule successivo alle run sopra indicate.

Workflow main: [trump_tracker.yml](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/trump_tracker.yml). Cron collector: `2-59/5 * * * *`. Il workflow conserva ancora `contents: write` e persiste `sputnik_state.json` su main. La PR #155 di diagnostica cadence e le PR di persistenza separata non sono integrate.

### GAGARIN

| Workflow | Ultima run schedule | Esito | Intervallo al cut-off |
|---|---|---|---:|
| Paper Monitor | [#172](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716), 06:34:18–06:34:37 UTC | SUCCESS | **8h17m21s** |
| Daily summary | [#10](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42484703932), 8 nov, 13:23:05 UTC | SUCCESS | Nessuna run successiva trovata |

Il monitor main resta configurato a `*/15 * * * *`; la proposta offset #225 non è integrata. Le ultime 100 Actions consultate non mostrano un monitor schedule successivo a #172.

## 3. SPUTNIK — segnali e fonti effettivamente esaminati

Run produttiva: [SPUTNIK #293](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770), main SHA `15f34dfe1e9866755bc2604e58ce8b582e34b5ac`, SUCCESS.

Il log live registra:
- SEC HTTP 403; cooldown 21.600 secondi; zero filing;
- White House RSS ancora sul vecchio endpoint `https://www.whitehouse.gov/feed/`, con HTTPError;
- due item-level Truth Archive nel digest;
- tre correlazioni pubbliche dichiarate, ma solo due eventi individuali attribuibili dal digest.

Gli OSError WHITE_HOUSE/TRUTH_ARCHIVE/OGE che compaiono prima del collector appartengono ai test regressivi mockati, non vanno conteggiati come errori del fetch live.

### Ritardo degli item

| Item | Pubblicazione | Rilevamento | Ritardo |
|---|---|---|---:|
| Truth Archive #43530 | 8 nov 23:41:05 UTC | 9 nov 06:01:46.594 UTC | circa 6h20m42s |
| Truth Archive #43532 / S.5653 | 9 nov 00:05:49 UTC | 9 nov 06:01:46.563 UTC | circa 5h55m58s |

Il post #43532 parla di permitting per pipeline, miniere e centrali e cita la Cina nel contesto dei data center. Lo stato persistito su main lo classifica tuttavia `TRADE_ESCALATION` e gli associa l'analogia tariffaria cinese 2025, con direzione storica negativa per il petrolio. La comparabilità dell'analogia non è supportata dal testo del post.

La correzione è già proposta nella [PR #154](https://github.com/andreameloni1984-sys/trump-trucker/pull/154), con due CI SUCCESS, ma la PR è OPEN e non integrata. La [PR #131](https://github.com/andreameloni1984-sys/trump-trucker/pull/131) sul nuovo endpoint White House è anch'essa OPEN: il run #293 conferma che main usa ancora il vecchio endpoint.

### Messaggi Telegram #746–#748

| ID | Generato UTC | Inviato UTC | Classificazione |
|---|---|---|---|
| #746 | 06:01:48.1711626 | 06:01:48.1720275 | Digest informativo, NON_TRADE |
| #747 | 06:01:48.1720811 | 06:01:48.1731760 | GOLD LONG tecnico 5m, EARLY_BIAS, NON_TRADE |
| #748 | 06:01:48.1732205 | 06:01:48.1742253 | GOLD EARLY_SETUP, NOT_EXECUTED |

#747:
- direzione tecnica LONG 5m;
- momentum 15m +0,077%;
- news alignment `NO_DIRECTIONAL_NEWS`;
- nessuna entry/SL/TP/ATR;
- score 100 non equivale a validità operativa.

#748:
- strumento logico: GOLD;
- ticker esatto: NOT_RESOLVED;
- titolo CFD, corpo riferito a future continuo front-month;
- scadenza: UNKNOWN;
- provider e timestamp della quotazione: NOT_EXPOSED;
- entry 4133.2002;
- SL 4130.5859;
- TP1 4135.8145;
- TP2 4138.4289;
- ATR 1.7429;
- stato esplicito `NOT_EXECUTED`;
- NARWHAL NOT_CONFIGURED;
- D-L-A NEUTRAL/NO_DIRECTION;
- la card non conserva la direzione tecnica LONG 5m presente in #747.

Il messaggio dichiara che scadenza esatta e indipendenza upstream non sono verificate e che i livelli non devono essere usati per l'ingresso. Senza provider, timestamp, ticker e contratto esatti non si può controllare se entry/SL/TP siano stati già superati né valutare un esito.

La discrepanza di propagazione tecnica è trattata dalla [PR #153](https://github.com/andreameloni1984-sys/trump-trucker/pull/153), OPEN, due CI SUCCESS, non integrata.

### Correzioni SPUTNIK

- [PR #155 — cadence diagnostics](https://github.com/andreameloni1984-sys/trump-trucker/pull/155): OPEN, non integrata; ranking **185 test SUCCESS**, item-intelligence **46 test SUCCESS**. Aggiunge osservabilità sulle ultime 20 run, non può garantire che GitHub emetta gli eventi schedule mancanti.
- [PR #154 — China/tariff classifier](https://github.com/andreameloni1984-sys/trump-trucker/pull/154): OPEN, CI SUCCESS; non in produzione.
- [PR #153 — direzione tecnica CFD](https://github.com/andreameloni1984-sys/trump-trucker/pull/153): OPEN, CI SUCCESS; non in produzione.
- [PR #131 — White House RSS](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): OPEN, non in produzione.
- [PR #145 — quote provenance Yahoo](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN; il messaggio #748 continua a non esporre provider e timestamp.

## 4. GAGARIN — quotazioni e candidata

Run produttiva: [GAGARIN #172](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716), main SHA `e7f5d2f890e8df52fcdc230bf4f0c16fd3266e56`, SUCCESS, `PAPER_TRADING_ONLY=1`.

### Quotazioni riportate dal log

| Strumento | Provider | Età | Stato |
|---|---|---:|---|
| Soia | YAHOO | 659,4 s | STALE |
| Brent | YAHOO | 603,0 s | STALE |
| WTI | YAHOO | 602,9 s | STALE |
| Argento | YAHOO | 609,5 s | STALE |
| Grano | YAHOO | 648,2 s | STALE |
| Rame | YAHOO | 613,7 s | STALE |
| Oro | YAHOO | 622,4 s | STALE |
| Mais | YAHOO | 686,3 s | STALE |
| EUR/USD | BIQUOTE | 273,0 s | LIVE, contesto |
| GBP/USD | BIQUOTE | 273,6 s | LIVE, contesto |

Sono età rilevate alle 06:34 UTC, non quotazioni correnti al cut-off. Il log non espone timestamp assoluti, ticker Yahoo risolti e scadenza dei contratti commodity.

### Candidata Soia SHORT

- record generato: 06:34:30.263983 UTC;
- ticker logico: SOYBEAN/USD;
- provider: YAHOO;
- età quota: 659,4 s, STALE;
- timestamp assoluto, ticker provider, mercato e scadenza: non esposti;
- direzione: SHORT;
- probability 63, quality 55,5, confidence 35;
- entry, SL, TP e ATR: assenti;
- stato: PAPER_WATCH, NOT_AUTHORIZED.

Blocchi: `LIVE_DATA_NOT_FRESH`, `TRIGGER_NOT_CONFIRMED`, `TRIGGER_DIRECTION_MISMATCH`, `FINAL_CONFLUENCE_FAIL`.

È una candidata bloccata, non un trade.

Il motore ha registrato:
`Recorded entries: 0`
`New feedback signals: 0`
`signals=0 open=0 closed=0`

Il messaggio #3728 ha ricevuto ACK Bot API alle 06:34:34.1131912 UTC (478 ms), ma il corpo non è conservato. Strumento, direzione e livelli non sono attribuibili; non è una prova di consegna sul dispositivo.

## 5. Journal, feedback e posizioni legacy GAGARIN

Verifiche dirette su main:

### Prediction log

File: [commodities_prediction_log.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities_prediction_log.json)

- 981 record;
- 981 ID unici, zero duplicati;
- 945 PENDING;
- 36 NEUTRALE;
- ultimo record creato: **2026-09-15 15:45:04.462276 UTC**;
- l'ultimo record è Benzina RBOB LONG, azione COMPRA ORA, ma stato PENDING.

Le etichette COMPRA ORA e score elevati non provano esecuzione o fill.

### Altri artefatti

- [journal.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/journal.csv): 11 vecchie righe del 17 ottobre, tutte `nessun segnale`.
- [paper_trade_log.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/paper_trade_log.csv): un record WTI `LEGACY_IMPORT`, 8 ottobre, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55; la nota dice “Chiusura spot 6 ott 2026. Nessun esito.” Nessun contratto, provider, timestamp quota o fill verificato.
- [data/paper_open.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/data/paper_open.json): WTI P0001 LONG OPEN, P&L null, record legacy.
- [position.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/position.json): Heating Oil LONG, aperta il 15 settembre, senza identità completa del contratto o provenienza della quota.
- `gagarin_feedback.csv`: HTTP 404 / file non presente su main.
- Nel job #172 `DATABASE_URL` è vuota.

Nessuno dei record WTI/Heating Oil è contato come fill o trade verificato. La persistenza durevole del journal non è dimostrata.

### Configurazione effettiva del monitor

Dal workflow main:
- PAPER_TRADING_ONLY=1;
- probability 40;
- quality 30;
- confidence 35;
- RR 2,5;
- max stop ATR 2,5;
- monitor 15 minuti.

Le soglie runtime 40/30/35 differiscono dalle precedenti specifiche GAGARIN annotate 62/55/60; la divergenza viene registrata, non modificata.

### Universo main

`commodities/universe.py` contiene otto commodity operative: Oro, Argento, Rame, WTI, Brent, Grano, Mais, Soia; EUR/USD e GBP/USD sono ausiliari Forex. Platino e Palladio non sono presenti nel file main.

La [PR #241](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/241) propone di disabilitare Argento, ma resta DRAFT e la CI d'integrazione fallisce:
- `test_removed_commodities_are_not_resolved[argento]`;
- `test_removed_commodities_are_not_resolved[silver]`;
- risultato: **2 failed, 569 passed**.

Il resolver restituisce ancora l'oggetto Argento disabilitato. Il monitor #172 ha quindi ancora analizzato Argento. La PR non è integrata.

## 6. Outcome engine — verifica del codice e PR

Su main `engine/feedback.py`:
- il record feedback non contiene quote provider, quote symbol, market type, contract month o expiry;
- il matching corrente usa symbol/timeframe;
- se la stessa candela OHLC tocca SL e TP, il codice controlla prima `stop_hit` e registra STOP.

La [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) corregge la parte di ambiguità:
- aggiunge provider, quote ticker, market type e contratto al fingerprint;
- richiede ticker/mercato e identità futures esplicita;
- doppio tocco nella stessa candela diventa `ESITO NON VERIFICABILE`.

Rimane però una lacuna dimostrata: `_market_contract_match()` confronta quote symbol, market type, contract month ed expiry, ma **non confronta l'uguaglianza del provider** tra segnale e serie successiva. Il provider entra nel fingerprint, non nel controllo forward. PR #192 è OPEN e il branch è 6 commit avanti e 6 indietro rispetto a main.

### Identità CFD e scadenze

- [PR #239](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/239): richiede prova esplicita di contract type ed expiry; DRAFT, branch stacked.
- [PR #242](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/242): nuova correzione che rifiuta date di scadenza passate. CI: **626 test SUCCESS** e **3 test execution SUCCESS**. È però DRAFT, stacked su #239/#238/#237 e 4 commit indietro rispetto a main. Nessuna modifica è in produzione; il registry non dimostra un feed CFD disponibile.
- [PR #225](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225): offset cron `7,22,37,52`, 5 CI SUCCESS, ma branch 2 avanti e 3 indietro rispetto a main.
- [PR #221](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): rimozione route FX, DRAFT, 14 avanti e 3 indietro.
- [PR #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): journal PostgreSQL durevole, DRAFT, 18 avanti e 4 indietro.

Test verdi su branch non equivalgono a integrazione o comportamento produttivo.

## 7. Esiti e statistiche

| Categoria | Verificato |
|---|---:|
| Nuovi segnali operativi in questo controllo | 0 |
| Nuovi record ledger | 0 |
| Fill | 0 |
| SL prima | 0 |
| TP prima | 0 |
| Esiti su contratto identico | 0 |
| Esiti non verificabili / non trade | Tutti i candidati esaminati |

Non viene attribuito un risultato al GOLD #748 perché è NOT_EXECUTED e non ha identità/quotazione completa. La candidata Soia è stata bloccata e non ha livelli. Il WTI LEGACY_IMPORT e Heating Oil non hanno prove di fill. Nessun backtest o win rate viene inventato.

## 8. Lacune e prossimo controllo

1. Verificare una nuova run schedule del collector SPUTNIK, distinta dal daily summary.
2. Verificare il nuovo endpoint White House solo dopo integrazione #131.
3. Controllare la classificazione S.5653 dopo integrazione #154.
4. Verificare la propagazione della direzione tecnica nella card CFD dopo #153.
5. Richiedere provider, ticker esatto, timestamp, mercato e scadenza per ogni livello GOLD.
6. Verificare la ripresa del monitor GAGARIN e quotazioni commodity fresche.
7. Verificare l'esclusione effettiva di Argento dopo correzione dei due test.
8. Completare il confronto provider nella PR #192 e mantenere la gestione cronologica del doppio tocco.
9. Dimostrare la persistenza del journal con scrittura e successiva lettura; il runner effimero e il file CSV mancante non bastano.
10. Valutare SL/TP soltanto su candele successive dello stesso identico strumento e contratto.

## 9. Pubblicazione e integrità

Questo rapporto viene aggiunto al branch documentale PRAVDA derivato dal precedente audit `pravda/audit-2026-11-09-1241UTC`.

Il ledger è ereditato senza modifiche: 103 righe, 103 firme uniche, 103 source ID unici, zero duplicati.

Nessun commento duplicato è stato aggiunto alle PR: i difetti sul classifier, provider matching, journal, Silver e cadence sono già documentati nei rispettivi thread.

PAPER ONLY. Nessun codice applicativo, strategia, filtro, punteggio o rischio modificato. Nessun merge, deploy, ordine reale, secret o Render modificato. Nessun servizio a pagamento. Nessun accesso a Trading212 dichiarato.
