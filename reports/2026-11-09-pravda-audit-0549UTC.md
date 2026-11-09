# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-09 05:49:58 UTC (06:49:58 Europe/Rome)**

## Sintesi

Verifica eseguita su entrambi i repository tramite GitHub Contents, commit, PR, log completi dei job già identificati, workflow YAML, journal e ledger PRAVDA. Sono stati controllati anche gli artifact delle run produttive note: nessun artifact allegato.

**Nessun nuovo segnale produttivo eleggibile rispetto al ledger cumulativo di 98 record.** Gli ultimi messaggi verificati restano SPUTNIK #743/#744/#745 e GAGARIN #3727; sono già registrati. Il CSV non è stato modificato.

Limite di questa esecuzione: il connettore GitHub disponibile ha permesso di recuperare job/log per run note, ma non un nuovo elenco completo e paginato di tutte le Actions. I gap sotto sono calcolati dall'ultima run produttiva verificabile, non sono prova assoluta dell'assenza di ulteriori run. Il controllo precedente delle Actions, alle 05:03:57 UTC, non aveva trovato run schedule successive; i main HEAD consultati restano quelli delle run note.

## 1. Ledger — integrità e completezza

Branch cumulativo ereditato: `pravda/audit-2026-11-09-0503UTC`.
Ledger: `reports/pravda-signal-ledger-2026-11-09.csv`.
Blob SHA: `a5211b7e5515860443f3860b374e294cd7465bca`.

Rilettura CSV con parser che rispetta i campi quotati:

| Indicatore | Valore |
|---|---:|
| Record | 98 |
| SPUTNIK | 45 |
| GAGARIN | 53 |
| audit_signature uniche | 98 |
| source_record_id unici | 98 |
| Duplicati firma | 0 |
| Duplicati source ID | 0 |
| NON_TRADE | 69 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |

Nessuna riga aggiunta: gli ultimi record #743, #744, #745 e #3727 sono già presenti.

Copertura campi sul totale di 98 righe (i conteggi di assenza includono record informativi per i quali il campo può non essere applicabile):
- timestamp generazione assente/non esposto: 7;
- timestamp invio assente/non esposto: 32;
- strumento non attribuibile: 8;
- ticker assente/non risolto: 30;
- mercato non esposto: 59;
- scadenza non verificata/non applicabile: 54;
- provider non esposto: 47;
- timestamp quotazione assente/non esposto: 75;
- entry, SL o TP1 assenti: 69 ciascuno;
- ATR assente: 85.

Win rate, average R e total R: **N/D**. Campione di fill verificati: zero. I 29 esiti non verificabili non sono 29 trade; includono previsioni legacy e record privi di identità/serie sufficienti.

## 2. GitHub Actions — ultime run produttive verificabili

### SPUTNIK collector

- [Run #292](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537803167), job `128905894291`.
- Avvio: 2026-11-08 23:59:46 UTC; conclusione: 23:59:58 UTC; SUCCESS.
- Main eseguito: `15f34dfe1e9866755bc2604e58ce8b582e34b5ac`.
- Cron su main `.github/workflows/trump_tracker.yml`: `2-59/5 * * * *`.
- Al cut-off: 5h50m12s dall'avvio della run #292.

### SPUTNIK polling

- [Run #52](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537592091), job `128905228194`.
- Avvio: 2026-11-08 23:56:54 UTC; conclusione: 23:57:02 UTC; SUCCESS.
- Cron `.github/workflows/telegram-polling.yml`: `*/5 * * * *`.
- Log: `Pending updates: 0`; prova soltanto che il polling non aveva aggiornamenti pendenti, non di consegna/visualizzazione dei messaggi.
- Al cut-off: 5h53m04s dall'avvio.

### GAGARIN monitor

- [Run #171](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42538235058), job `128907219566`.
- Avvio: 2026-11-09 00:04:51 UTC; conclusione: 00:05:10 UTC; SUCCESS.
- Main eseguito: `e7f5d2f890e8df52fcdc230bf4f0c16fd3266e56`.
- Cron `.github/workflows/gagarin-monitor.yml`: `*/15 * * * *`; `MONITOR_INTERVAL_MINUTES=15`.
- Al cut-off: 5h45m07s dall'avvio.

Le run PR/CI non sono state conteggiate come scansioni di mercato. Le run #292 e #171 non hanno artifact allegati. Non è stata dimostrata la causa dei gap; non li attribuisco a filtri, mercato chiuso o provider.

## 3. SPUTNIK — log, segnali e provenienza

### Fonti e collector #292

Il log completo distingue i test dal runtime:
- Le righe OSError per WHITE_HOUSE, TRUTH_ARCHIVE e OGE precedono il comando `python trump_tracker.py` e appartengono allo step di regression test: non sono conteggiate come errori del collector.
- Runtime SEC: HTTP 403, cooldown 21.600 secondi, filings 0.
- Estrazione transazioni: 0.
- White House RSS: HTTPError sull'endpoint main `https://www.whitehouse.gov/feed/`.
- Public intelligence scan: 1 finding.
- `GAGARIN_CLOUD_API_URL` e `GAGARIN_CLOUD_API_KEY` vuote nel job; forwarding 0 ms.
- `NARWHAL_API_KEY` vuota nel job.

Il finding TRUTH_ARCHIVE che precede #743/#744 è una snapshot page-level, non un post individuale:
- event_id `14206ad67f74de2585209e6c`;
- URL `https://www.trumpstruth.org/`;
- titolo, published timestamp e permalink individuale assenti;
- detected_at `2026-11-08T23:59:52.394955Z`;
- evidence `PUBLIC_SOURCE_TEXT_PAGE_LEVEL`.

### Messaggi effettivi

| ID | Generazione UTC | Accettazione API UTC | Contenuto | Stato audit |
|---|---|---|---|---|
| #743 | 23:59:54.8425373 | 23:59:54.8438627 | GOLD bias SHORT preliminare, momentum 5m -0,061%, NO_DIRECTIONAL_NEWS | NON_TRADE |
| #744 | 23:59:54.8439129 | 23:59:54.8449792 | GOLD EARLY_SETUP SHORT con livelli numerici | NOT_EXECUTED / NON_TRADE |
| #745 | 23:59:54.8450509 | 23:59:54.8454315 | Brief giornaliero informativo | NON_TRADE |

I tempi API registrati sono 401 ms, 396 ms e 364 ms. Sono conferme di accettazione API, non prova di visualizzazione sul dispositivo.

### #744 — livelli e limiti

- Direzione riportata: SHORT.
- Entry 4069.1001; SL 4071.9929; TP1 4066.2073; TP2 4063.3145; ATR 1.9285.
- Score 100/100: non prova di validità operativa.
- D-L-A: `NEUTRAL / NO_DIRECTION (NOT_ASSESSED)`.
- Stato esplicito: `TRADE PAPER: NOT_EXECUTED`.
- NARWHAL: `NOT_CONFIGURED`.
- Il corpo identifica un future continuo front-month e avverte che scadenza esatta e indipendenza upstream non sono verificate; il titolo dice CFD.
- Ticker risolto, provider, timestamp/età della quotazione e scadenza esatta non sono esposti nel messaggio.

Il codice main `sputnik_cfd.py` conserva metadati della quotazione nel segnale, ma `format_cfd_signal()` non stampa provider, ticker risolto, timestamp/età, market type o scadenza. Non è possibile stabilire se i livelli fossero già superati né valutare SL/TP: manca una serie successiva dello stesso identico contratto. Non viene attribuito alcun esito.

### #745 — etichetta oraria

Il brief è stato accettato alle 23:59:54 UTC dell'8 novembre, cioè alle 00:59:54 CET del 9 novembre, ma il titolo è `BRIEF ORE 05:00`. [Issue #151](https://github.com/andreameloni1984-sys/trump-trucker/issues/151) è OPEN. [PR #152](https://github.com/andreameloni1984-sys/trump-trucker/pull/152) propone `BRIEF GIORNALIERO`, ma non è integrata.

### PR SPUTNIK — stato e CI sul rispettivo head

- [#131 — endpoint White House RSS](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): OPEN, non draft, 3 commit avanti / 0 indietro da main; head `db73bdc92e312e58abe94585b83dc26ff9117966`. CI ranking #42564218665 SUCCESS (184 test) e item-intelligence #42564218686 SUCCESS (45 test). Il runtime #292 usa ancora il vecchio endpoint; effetto produttivo non verificato.
- [#150 — bloccare raccomandazioni ripetute senza nuovo RSS item](https://github.com/andreameloni1984-sys/trump-trucker/pull/150): OPEN, non draft, 1 avanti / 0 indietro. CI #42553788540 e #42553788446 SUCCESS (231 test complessivi). Non integrata.
- [#152 — etichetta brief giornaliero](https://github.com/andreameloni1984-sys/trump-trucker/pull/152): OPEN, non draft, 3 avanti / 0 indietro. CI #42550701160 e #42550701170 SUCCESS (231 test). Non integrata.
- [#147 — rimuovere handoff GAGARIN](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN, non draft, 4 avanti / 0 indietro. CI #42560177717 e #42560177740 SUCCESS (221 test). Non integrata; main mantiene ancora il wiring opzionale, anche se nel run #292 URL/key erano vuote e forwarding era 0 ms.
- [#145 — esporre provenienza quote e log errori Yahoo](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN, non draft, ma branch divergente rispetto al main attuale: 1 commit avanti / 11 indietro. Non considerare la correzione pronta per integrazione senza riallineamento.
- [#144 — persistenza stato fuori da main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN, non draft, 1 avanti / 42 indietro rispetto al main attuale. Main continua a committare `sputnik_state.json` direttamente su main; la PR è molto indietro.

## 4. GAGARIN — dati, classificazione e journal

### Monitor #171

Il log conferma `PAPER_TRADING_ONLY=1`, `DATABASE_URL` vuota e `NARWHAL_API_KEY` vuota.

| Strumento | Provider | Età | Stato |
|---|---|---:|---|
| Soia | YAHOO | 189.906,8 s | STALE |
| Argento | YAHOO | 655,0 s | STALE |
| Oro | YAHOO | 611,0 s | STALE |
| Grano | YAHOO | 189.906,5 s | STALE |
| Mais | YAHOO | 189.909,6 s | STALE |
| Brent | YAHOO | 605,4 s | STALE |
| WTI | YAHOO | 604,2 s | STALE |
| Rame | YAHOO | 643,1 s | STALE |
| GBP/USD | BIQUOTE | 6,9 s | LIVE, contesto non operativo |
| EUR/USD | BIQUOTE | 6,3 s | LIVE, contesto non operativo |

Le otto commodity sono STALE; le due coppie Forex sono LIVE ma non operative. Per le commodity il riepilogo non espone ticker provider risolto, timestamp assoluto della candela, mercato e scadenza.

WTI compare LONG / PAPER_WATCH, ma è bloccato da `LIVE_DATA_NOT_FRESH`, `TRIGGER_NOT_CONFIRMED`, `TRIGGER_DIRECTION_MISMATCH`, `RR_FAIL` e `FINAL_CONFLUENCE_FAIL`. Nessun ingresso autorizzato.

Risultati: Recorded entries 0; Updated open outcomes 0; New feedback signals 0; New additional live forecasts 0; `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`.

Telegram #3727 è stato accettato dall'API in 403 ms, ma il corpo non è conservato: nessuno strumento o direzione può essergli attribuito.

### Journal e previsioni

File letti direttamente da main:
- `commodities_prediction_log.json`: 981 record; ultimo created_at `2026-09-15T15:45:04.462276+00:00`; 945 PENDING e 36 NEUTRALE. Action: 21 COMPRA ORA, 292 LONG — ASPETTARE CONFERMA, 15 SHORT — ASPETTARE CONFERMA, 576 ATTENDERE, 77 NON ENTRARE. Tutte le 21 COMPRA ORA sono PENDING; 15 hanno `operational_signal=LONG`, 6 non hanno operational_signal. Nessuna è prova di fill.
- `commodities_monitor_state.json`: timestamp `2026-09-17T03:44:02.566153+00:00`; best Benzina RBOB LONG ma action ATTENDERE, entry_state BLOCKED, position null.
- `journal.csv`: 11 righe del 17 ottobre, tutte “nessun segnale”.
- `paper_trade_log.csv`: un WTI LONG `LEGACY_IMPORT`, OPEN, entry 96.24, stop 89.37, TP1 103.11; provider, ticker feed, timestamp quote, mercato/scadenza e outcome assenti. Nota archivistica: nessun esito.
- `data/paper_open.json`: P0001 WTI LONG OPEN legacy con gli stessi livelli, PnL null.
- `position.json`: vecchia Heating Oil LONG, entry 4.8844, SL 4.5418, TP1 5.4473, aperta il 15 settembre; nessuna prova di fill o riconciliazione con il monitor.
- `gagarin_feedback.csv`: HTTP 404, assente dal repository pubblico.

Il workflow `.github/workflows/gagarin-monitor.yml` dichiara che i journal privati non devono essere committati nel repository pubblico e che la persistenza sarà riattivata dopo deploy e verifica dello storage privato. Il valore vuoto di DATABASE_URL è provato per la run #171, non per ogni possibile ambiente. I record legacy non sono conteggiati come trade verificati.

## 5. GAGARIN — outcome engine

Su main `engine/feedback.py`:
- il fingerprint del segnale usa symbol, direzione, timeframe, livelli e timestamp barra; non include provider, ticker risolto, mercato e scadenza;
- l'associazione delle candele successive usa symbol e timeframe, senza identità completa del provider/contratto;
- se una candela tocca SL e TP, il codice controlla prima SL e registra STOP.

La [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) è OPEN, non draft, 6 commit avanti / 6 indietro. Il branch aggiunge quote provider/symbol, market type, contract month/expiry al fingerprint e gestisce il doppio tocco SL/TP come `ESITO NON VERIFICABILE`. Sei CI associate al suo head risultano SUCCESS.

Resta però dimostrato un difetto nel branch: `_market_contract_match()` confronta quote symbol, market type e, per i futures, contract month/expiry, ma **non confronta row.quote_provider con il provider corrente**. Un diverso provider può quindi passare se symbol/mercato/contratto coincidono. Il rilievo è già nei commenti PR #192 [#6706619879](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6706619879) e [#6725075554](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6725075554); nessun commento duplicato aggiunto.

## 6. GAGARIN — universo, cron e CFD

- Main `main.py::_select_run_universe()` restituisce ancora `enabled_commodities()`; run #171 analizza 10 strumenti (otto commodity e due Forex ausiliari).
- [PR #221](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221) è OPEN/DRAFT, 14 commit avanti / 3 indietro; sei CI sul suo head SUCCESS. Il branch seleziona `operational_commodities()` e rimuove le route FX, ma il suo universo di otto commodity include ancora **Argento**.
- [PR #223](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223) è OPEN/DRAFT e propone un osservatore M5 a sette strumenti che esclude Argento. Il suo stesso scope è observation-only: non genera entry/SL/TP, non scrive il journal e non invia alert Telegram; non rimuove Argento dal monitor provider-heavy. Cinque CI sul suo head SUCCESS.
- Per rendere esplicito questo mismatch rispetto alla precedente istruzione di escludere Argento dalle scansioni GAGARIN, PRAVDA ha aggiunto un solo commento audit alla [PR #221](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221#issuecomment-6733328967). Nessun codice o filtro è stato modificato.
- [PR #225](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225), offset del cron a 7,22,37,52 mantenendo 15 minuti, è ancora OPEN/DRAFT; main resta `*/15`.
- [PR #222](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222) è già MERGED: rimuove il veto intraday di sessione dal Governor. Non rimuove i controlli indipendenti su dati stale/mercato chiuso.
- [PR #239](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/239) è OPEN/DRAFT, stacked su #238; due CI SUCCESS. Richiede evidenza esplicita di tipo contratto/scadenza anche per SPOT senza scadenza, ma non autentica un feed e il registry resta vuoto.
- [PR #238](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/238) separa app symbol, catalogue ticker/slug e feed symbol; registry vuoto, nessun feed.
- [PR #234/#235](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/234) / [#235](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/235) propongono journal CFD PAPER isolato e persistenza durevole; entrambe DRAFT e non integrate.

Nessun feed CFD Trading 212 verificato. Nessun accesso a Trading 212 dichiarato.

## 7. Esiti e statistiche

- Fill verificati: 0.
- SL prima verificato: 0.
- TP prima verificato: 0.
- 29 record `ESITO_NON_VERIFICABILE` nel ledger: non sono automaticamente trade.
- 69 record `NON_TRADE`.
- Nessun prezzo spot o future continuo sostituito a un contratto non identificato.
- Nessuna valutazione del raggiungimento/superamento dei livelli GOLD #744: manca la provenienza e la scadenza esatta.
- Nessun backtest inventato.

## 8. Fonti consultate

- GitHub Actions e job log: [SPUTNIK #292](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537803167), [SPUTNIK polling #52](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537592091), [GAGARIN #171](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42538235058).
- Workflow main: `trump_tracker.yml`, `telegram-polling.yml`, `gagarin-monitor.yml`.
- Codice main: `sputnik_cfd.py`, `main.py`, `engine/feedback.py`, `paper_trade_journal.py`, `commodities/universe.py`.
- Artefatti GAGARIN: `commodities_prediction_log.json`, `commodities_monitor_state.json`, `journal.csv`, `paper_trade_log.csv`, `data/paper_open.json`, `position.json`; `gagarin_feedback.csv` non trovato (404).
- PR SPUTNIK #131, #144, #145, #147, #150, #152; Issue #151.
- PR GAGARIN #192, #221, #222, #223, #225, #234, #235, #238, #239.
- Ledger cumulativo, blob SHA `a5211b7e5515860443f3860b374e294cd7465bca`.

## 9. Prossimo controllo

1. Ottenere un nuovo elenco completo delle Actions e distinguere schedule collector/monitor, polling, push e CI.
2. Verificare la prima nuova scansione produttiva successiva alle run #292/#171.
3. Dopo l'eventuale merge #131, verificare il recupero White House RSS nel runtime.
4. Dopo l'eventuale merge #150, verificare che una snapshot page-level senza item/date/permalink non generi la coppia GOLD.
5. Verificare che SPUTNIK esponga provider, ticker, timestamp/età, mercato e scadenza prima di trattare livelli come verificabili.
6. Verificare quotazioni commodity fresche GAGARIN e riconciliare l'universo completo, inclusa l'esclusione di Argento richiesta.
7. Verificare il confronto provider nel branch #192 prima di considerare attendibile il feedback.
8. Verificare una scrittura e successiva lettura del journal persistente; non dedurla dal solo SUCCESS della run.
9. Valutare SL/TP solo con prezzi successivi dello stesso identico ticker, provider, mercato e contratto.

## 10. Ambito e sicurezza

Questo aggiornamento ha prodotto un solo commento audit sulla PR #221 e un rapporto Markdown su branch separato. Il ledger non è stato modificato. Nessuna modifica al codice, strategia, filtri, punteggi o rischio. Nessun merge/deploy, ordine reale, modifica a secret o Render, servizio a pagamento o accesso Trading 212. Gli ACK Telegram provano soltanto accettazione API, non consegna/visualizzazione sul dispositivo.

**PAPER ONLY.**
