# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-09 09:45:10 UTC (10:45:10 Europe/Rome)**

## Esito sintetico

Verificate le ultime 100 GitHub Actions di entrambi i repository, i job log delle ultime scansioni produttive, i workflow cron, i file pubblici di stato/journal, il ledger PRAVDA e le PR tecniche rilevanti.

**Non risultano nuove scansioni produttive dopo SPUTNIK #293 / Telegram Polling #53 e GAGARIN #172.** Le CI delle PR non sono scansioni di mercato.

Non è emerso un nuovo segnale da aggiungere. Il ledger resta invariato: 103 record, 103 firme uniche, zero duplicati. Nessun fill, SL o TP verificato.

## 1. Ledger storico

Ledger cumulativo ereditato senza modifiche:
- `reports/pravda-signal-ledger-2026-11-09.csv`
- SHA blob: `1acbe2994b6147a4d2fdd39108cf46f499fd6265`
- 103 record dati; 33 colonne.
- SPUTNIK 48; GAGARIN 55.
- 103 `audit_signature` uniche.
- 103 `source_record_id` unici.
- 74 `NON_TRADE`; 29 `ESITO_NON_VERIFICABILE`.
- 0 fill verificati; 0 SL verificati; 0 TP verificati.

Nessuna riga aggiunta: le ultime notifiche SPUTNIK #746–#748, la candidata Soia e il WATCH GAGARIN #3728 sono già registrati. Win rate, average R e total R restano N/D perché il campione di operazioni eseguite e verificabili è zero.

## 2. GitHub Actions e continuità

Ultime run programmate riscontrate nella prima pagina (100 elementi) dell'API Actions:

| Processo | Ultima run | Completamento UTC | Stato | Gap al cut-off |
|---|---|---:|---|---:|
| SPUTNIK collector | #293 — [run](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770) | 06:01:51 | SUCCESS | 3h43m19s |
| SPUTNIK Telegram polling | #53 — [run](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570062235) | 05:55:56 | SUCCESS | 3h49m14s |
| GAGARIN Paper Monitor | #172 — [run](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716) | 06:34:37 | SUCCESS | 3h10m33s |

Cron letti dai workflow:
- SPUTNIK collector: `2-59/5 * * * *`.
- SPUTNIK polling: `*/5 * * * *`.
- GAGARIN monitor: `*/15 * * * *`.

Sono presenti CI successive sulle PR, ma nessuna è una scansione produttiva. La causa dei gap non è dimostrata e non viene ipotizzata.

## 3. SPUTNIK — run produttiva #293

Job log: [job 129006852221](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770/job/129006852221).

### Raccolta fonti
- SEC: HTTP 403; cooldown 21.600 secondi; 0 filing.
- Estrazione transazioni: 0.
- White House: il runtime usa ancora `https://www.whitehouse.gov/feed/`, che restituisce HTTPError.
- Scan pubblico: 3 correlazioni dichiarate; digest con 2 eventi item-level.
- GAGARIN cloud handoff disabilitato: `GAGARIN_CLOUD_API_URL` e `GAGARIN_CLOUD_API_KEY` vuoti.
- NARWHAL è abilitato come riferimento, ma `NARWHAL_API_KEY` è vuota.

Eventi nel digest:
1. Quote post pubblicato 2026-11-08 23:41:05 UTC, permalink [43530](https://www.trumpstruth.org/statuses/43530), rilevato dal collector circa 2026-11-09 06:01:46.575 UTC: ritardo circa 6h20m41s.
2. Post S.5653 pubblicato 2026-11-09 00:05:49 UTC, permalink [43532](https://www.trumpstruth.org/statuses/43532), detection persistita circa 06:01:46.563 UTC: ritardo circa 5h55m58s.

Il post S.5653 riguarda permitting/indipendenza energetica e non costituisce, da solo, un annuncio tariffario.

### Messaggi effettivi

| ID | Generazione UTC | ACK/API UTC | Contenuto | Stato PRAVDA |
|---|---|---|---|---|
| #746 | 06:01:48.171 | 06:01:48.172 | Digest informativo, 2 eventi | NON_TRADE |
| #747 | 06:01:48.172 | 06:01:48.173 | GOLD LONG preliminare, tecnica LONG 5m, momentum +0,077%/15m, NO_DIRECTIONAL_NEWS | NON_TRADE |
| #748 | 06:01:48.173 | 06:01:48.174 | GOLD LONG EARLY_SETUP con livelli | NOT_EXECUTED / NON_TRADE |

#748:
- Entry 4133.2002
- SL 4130.5859
- TP1 4135.8145
- TP2 4138.4289
- ATR 1.7429
- Score 100/100

Difetti verificati nel messaggio:
- Titolo CFD, corpo riferito a future continuo front-month.
- Ticker/strumento contrattuale esatto non risolto; scadenza esatta non verificata.
- Provider e timestamp della quotazione non esposti.
- Il messaggio #747 mostra direzione tecnica LONG 5m; la card #748 mostra `TECNICA: N/D` e `D-L-A: NEUTRAL / NO_DIRECTION`.
- Il messaggio dichiara esplicitamente `NOT_EXECUTED` e avverte di non usare i livelli per un ingresso.

Gli ACK Telegram confermano la risposta API per gli ID #746–#748, non la visualizzazione sul dispositivo. Senza identità ticker/mercato/scadenza e prezzi successivi dello stesso contratto non si può classificare SL prima, TP prima o livello già superato: **ESITO NON VERIFICABILE come ipotesi di prezzo; nessun trade da valutare**.

### PR SPUTNIK
- [PR #154](https://github.com/andreameloni1984-sys/trump-trucker/pull/154): OPEN, non draft, 2 commit; CI ranking e item-intelligence SUCCESS. Corregge l'analogia tariffaria automatica su una generica menzione della Cina. Non integrata, quindi non ancora validata in produzione.
- [PR #153](https://github.com/andreameloni1984-sys/trump-trucker/pull/153): OPEN, non draft, 2 commit; CI ranking e Telegram menu SUCCESS. Propaga la direzione tecnica 5m nella card CFD. Non integrata.
- [PR #131](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): correzione endpoint White House ancora non dimostrata in produzione.

## 4. GAGARIN — run produttiva #172

Job log: [job 129017049476](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716/job/129017049476).

Il log riporta 8 commodity operative e 2 Forex ausiliari. Età quote al momento dell'analisi:

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
| EUR/USD | BIQUOTE | 273,0 s | LIVE, ausiliario |
| GBP/USD | BIQUOTE | 273,6 s | LIVE, ausiliario |

Il log non espone il timestamp assoluto della singola quotazione, il ticker feed risolto né la scadenza del contratto. Le età non vengono trasformate in timestamp esatti.

### Candidata Soia
- Simbolo logico: SOYBEAN/USD.
- Direzione: SHORT.
- Probability 63,0; Quality 55,5; Confidence 35,0.
- Stato: PAPER_WATCH.
- Blocchi: LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, FINAL_CONFLUENCE_FAIL.
- Entry, SL, TP e ATR: assenti.

Non è un segnale operativo e non è un trade. Il messaggio #3728 ha ACK API in 478 ms, ma il corpo non è conservato: non gli viene attribuito uno strumento.

Riepilogo del job:
- Recorded entries: 0.
- Updated open outcomes: 0.
- New feedback signals: 0.
- New additional live forecasts: 0.
- signals=0, open=0, closed=0.

### Universo e perimetro Argento
Il file `commodities/universe.py` su main contiene otto commodity (XAU, XAG, rame, WTI, Brent, grano, mais, soia) e due Forex ausiliari; il log #172 conferma otto commodity operative.

La discussione della PR #241 contiene due note di scope in conflitto: una alle 09:06 UTC dice di escludere XAG, quella successiva alle 09:10 UTC, dallo stesso account, ribadisce otto commodity includendo Argento. Per l'audit prevale cronologicamente la nota più recente: **XAG è incluso nel perimetro corrente documentato**. La [PR #241](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/241), che lo disabilita, resta DRAFT e non va considerata recepita.

Sul branch PR #241 la CI d'integrazione è FAILURE: 2 test falliti, 569 passati. I due test `argento` e `silver` falliscono perché il resolver restituisce l'oggetto XAG disabilitato invece di `None`. Altri quattro workflow associati risultano SUCCESS. Nessuna modifica è stata fatta da PRAVDA.

## 5. Journal, feedback e posizioni legacy GAGARIN

File pubblici verificati su main:
- `commodities_prediction_log.json`: 981 record; PENDING 945, NEUTRALE 36; ultimo `created_at` 2026-09-15 15:45:04 UTC. Le 21 righe con action `COMPRA ORA` sono tutte PENDING; non sono fill.
- `commodities_monitor_state.json`: timestamp 2026-09-17 03:44:02 UTC.
- `commodities_direction_state.json`: aggiornamenti più recenti del 17 settembre.
- `journal.csv`: 11 righe del 17 ottobre, tutte con esito “nessun segnale”.
- `paper_trade_log.csv`: una riga WTI `LEGACY_IMPORT` del 8 ottobre, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55, status OPEN e PnL vuoto. I campi quote provider/symbol/timestamp/market sono vuoti.
- `data/paper_open.json`: WTI P0001 LONG OPEN con gli stessi livelli legacy.
- `position.json`: vecchia posizione Heating Oil LONG, aperta il 15 settembre, senza identità provider/contratto.

Queste posizioni legacy non dimostrano un fill e non vengono conteggiate come trade.

`gagarin_feedback.csv` non è presente nel tree pubblico. Il workflow `gagarin-monitor.yml` dichiara che i journal sono dati operativi privati e non vanno committati nel repository pubblico; la persistenza verrà riattivata dopo deploy e verifica di storage privato D1. Nel job #172 `DATABASE_URL` è vuota. Non è stato possibile verificare il contenuto di uno storage privato.

### Configurazione runtime
Il workflow main imposta:
- MIN_ENTRY_PROBABILITY 40
- MIN_ENTRY_QUALITY 30
- MIN_ENTRY_CONFIDENCE 35
- MIN_ENTRY_RR 2.5
- MAX_ENTRY_STOP_ATR 2.5
- MONITOR_INTERVAL_MINUTES 15
- PAPER_TRADING_ONLY=1

Sono i valori osservati nel job, non una modifica PRAVDA. La divergenza rispetto a soglie precedentemente annotate va mantenuta come rilievo di configurazione; nessuna soglia è stata cambiata.

## 6. Outcome engine e identità contrattuale

### Main GAGARIN
`engine/feedback.py` su main:
- non include provider, market type e scadenza nei campi del record feedback;
- la docstring dichiara che un tocco ambiguo SL/TP nella stessa candela viene risolto conservativamente come STOP.

Questo non soddisfa il protocollo PRAVDA: con una singola candela OHLC che tocca entrambi i livelli l'esito deve essere ESITO NON VERIFICABILE.

### PR #192
[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) è OPEN, non integrata. Il branch aggiunge provider, quote timestamp, quote symbol, market type e contract month/expiry al record e tratta il doppio tocco come non verificabile. Tuttavia `_market_contract_match()` confronta quote symbol, market type e scadenza/mese, ma **non confronta l'uguaglianza del provider** tra segnale e serie di candele successive. Il difetto è già documentato nei commenti PRAVDA esistenti; nessun commento duplicato aggiunto.

### PR #239
[PR #239](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/239) è OPEN e DRAFT. Le prove esplicite per tipo contratto e scadenza sono un miglioramento, ma il branch `_verified_expiry()` valida formato e data di calendario senza rifiutare una scadenza già trascorsa. Un future scaduto potrebbe quindi superare la validazione se i flag di evidenza sono veri. Rilievo già presente nel commento esistente; nessuna modifica applicata.

## 7. Fonti consultate

- GitHub Actions API, ultime 100 run per repository.
- Log completi dei job SPUTNIK #293 e GAGARIN #172.
- Log del job CI fallito della PR #241.
- Workflow `trump_tracker.yml`, `telegram-polling.yml`, `gagarin-monitor.yml`.
- File main GAGARIN: `config.py`, `commodities/universe.py`, `commodities_prediction_log.json`, `commodities_monitor_state.json`, `commodities_direction_state.json`, `journal.csv`, `paper_trade_log.csv`, `position.json`, `data/paper_open.json`, `engine/feedback.py`.
- PR #154, #153, #241, #192, #239 e relativi diff/commenti/CI.
- Ledger cumulativo PRAVDA del branch audit 09:01 UTC.

Non sono stati usati servizi a pagamento, feed broker autenticati o prezzi esterni per simulare un outcome. Nessun accesso a Trading212 è stato dichiarato.

## 8. Lacune e prossimo controllo

1. Attendere e verificare nuove run produttive, non CI di PR.
2. Per SPUTNIK, ottenere ticker/mercato/scadenza esatti e provider/timestamp della quotazione prima di valutare #748.
3. Verificare il nuovo collector White House solo dopo integrazione e successiva run produttiva.
4. Per GAGARIN, acquisire timestamp assoluto, ticker feed, market type e scadenza delle quotazioni; al momento sono disponibili solo provider ed età.
5. Verificare la persistenza privata solo quando sarà configurata e leggibile; al momento DATABASE_URL è vuota.
6. Correggere/validare provider equality in #192 e scadenze passate in #239 prima di considerare certificabile l'outcome engine.
7. Non attribuire esiti alle posizioni legacy né ai messaggi NOT_EXECUTED.
8. Mantenere il perimetro XAG secondo la nota più recente nella discussione PR #241, senza modifiche da parte di PRAVDA.

**Verdetto:** 103 record, zero duplicati, zero fill verificati, zero SL/TP verificati. Nessuna statistica di performance calcolabile. Nessuna modifica a codice, strategia, filtri, punteggi o rischio; nessun merge/deploy, ordine reale, intervento su secret o Render.
