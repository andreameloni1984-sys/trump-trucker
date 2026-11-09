# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-09 05:03:57 UTC (06:03:57 Europe/Rome)**

## Sintesi

Verifica effettuata sui due repository, interrogando direttamente le prime 100 GitHub Actions più recenti di ciascun repository, i job log completi delle ultime run produttive, i workflow YAML su `main`, il ledger PRAVDA, i journal pubblici e le PR aperte.

**Non risultano nuove run schedule produttive dopo SPUTNIK collector #292, SPUTNIK polling #52 e GAGARIN monitor #171.** Le CI PR più recenti non sono scansioni di mercato. Nessun nuovo segnale è quindi eleggibile per il ledger.

Aggiornamento rilevante: la PR SPUTNIK #131 ha corretto il proprio commit dopo due CI fallite intermedie e ora ha entrambe le CI SUCCESS; resta però aperta e non integrata. GAGARIN #239 ha due CI SUCCESS, ma è ancora DRAFT e non popola il registry né fornisce quotazioni.

## 1. Ledger — integrità e statistiche

Ledger cumulativo ereditato dal branch precedente:
`reports/pravda-signal-ledger-2026-11-09.csv`

Blob SHA: `a5211b7e5515860443f3860b374e294cd7465bca`.

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

Il CSV è stato riletto con parser che rispetta i campi quotati. Le 98 firme e i 98 source ID sono unici. Nessuna riga aggiunta: le ultime osservazioni #743/#744/#745 e #3727 erano già registrate.

Win rate, average R e total R: **N/D**. Campione di fill verificati: zero.

## 2. GitHub Actions — elenco completo delle run recenti

Ho interrogato `actions/runs?per_page=100` per entrambi i repository e filtrato gli eventi `schedule`. Le run PR/push non sono state conteggiate come scansioni produttive.

### SPUTNIK

- [Collector #292](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537803167): schedule, avvio 2026-11-08 23:59:46 UTC, conclusione 23:59:58 UTC, SUCCESS; job `128905894291`.
- [Telegram polling #52](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537592091): schedule, avvio 23:56:54 UTC, conclusione 23:57:02 UTC, SUCCESS; job `128905228194`.
- Nessuna run schedule successiva compare nella prima pagina delle 100 run più recenti al cut-off.

Workflow letti da `main`:
- `.github/workflows/trump_tracker.yml`: cron `2-59/5 * * * *`.
- `.github/workflows/telegram-polling.yml`: cron `*/5 * * * *`.

Gap al cut-off 05:03:57 UTC:
- Collector: **5h04m11s** dall'avvio #292.
- Polling: **5h07m03s** dall'avvio #52.

Il collector workflow mantiene `permissions: contents: write` e, dopo l'analisi, committa `sputnik_state.json` su `main`. La run #292 ha effettivamente creato il commit `15f34dfe1e9866755bc2604e58ce8b582e34b5ac` alle 23:59:54 UTC. La PR #144 per spostare lo stato su un branch dedicato è ancora aperta.

### GAGARIN

- [Monitor #171](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42538235058): schedule, avvio 2026-11-09 00:04:51 UTC, conclusione 00:05:10 UTC, SUCCESS; job `128907219566`.
- Nessuna run schedule successiva compare nella prima pagina delle 100 run più recenti al cut-off.

Workflow `.github/workflows/gagarin-monitor.yml` letto da `main`: cron `*/15 * * * *`.

Gap al cut-off: **4h59m06s** dall'avvio #171.

La causa dei gap non è dimostrata. Non attribuisco i ritardi a filtri, mercati chiusi, provider o cause esterne senza log che lo provino.

## 3. SPUTNIK — log produttivo e messaggi

### Fonti e collector #292

Il log distingue correttamente i test dal runtime:
- Le righe OSError per WHITE_HOUSE, TRUTH_ARCHIVE e OGE sono nello step di test precedente a `python trump_tracker.py`; non le conto come errori del collector.
- Runtime SEC: HTTP 403, cooldown 21.600 secondi, filings 0.
- Estrazione transazioni: 0.
- White House RSS: HTTPError sull'endpoint `https://www.whitehouse.gov/feed/`.
- Public intelligence scan: 1 finding.
- Forwarding GAGARIN: 0 ms; URL e API key GAGARIN vuote nel job.
- Nessun nuovo filing o transazione.

Il finding TRUTH_ARCHIVE che ha preceduto la coppia GOLD #743/#744 era una snapshot page-level:
- event_id `14206ad67f74de2585209e6c`;
- URL `https://www.trumpstruth.org/`;
- titolo, published timestamp e permalink individuale assenti;
- rilevamento `2026-11-08T23:59:52.394955Z`;
- evidenza `PUBLIC_SOURCE_TEXT_PAGE_LEVEL`.

Non è un singolo post RSS datato. Il messaggio #743 dichiara `NO_DIRECTIONAL_NEWS`. La PR #150 affronta esattamente il difetto per cui una snapshot generica può riattivare una coppia di raccomandazioni dalla cronologia.

### Messaggi effettivi

| ID Telegram | Generazione UTC | Accettazione API UTC | Contenuto | Classificazione |
|---|---|---|---|---|
| #743 | 23:59:54.8425373 | 23:59:54.8438627 | GOLD, bias SHORT preliminare, momentum 5m -0,061%, nessuna notizia direzionale | NON_TRADE |
| #744 | 23:59:54.8439129 | 23:59:54.8449792 | GOLD EARLY_SETUP SHORT con livelli teorici | NOT_EXECUTED / NON_TRADE |
| #745 | 23:59:54.8450509 | 23:59:54.8454315 | Brief giornaliero informativo | NON_TRADE |

Il log riporta round-trip API di 401 ms, 396 ms e 364 ms. Sono conferme di accettazione Telegram API, non prove di visualizzazione sul dispositivo.

### #744 — livelli e limiti

- Direzione riportata: SHORT.
- Entry: **4069.1001**.
- SL: **4071.9929**.
- TP1: **4066.2073**.
- TP2: **4063.3145**.
- ATR: **1.9285**.
- Score: 100/100.
- D-L-A: `NEUTRAL / NO_DIRECTION (NOT_ASSESSED)`.
- Stato esplicito: `TRADE PAPER: NOT_EXECUTED`.
- NARWHAL: `NOT_CONFIGURED`.
- Il messaggio avverte che il riferimento è un future continuo front-month, con scadenza esatta e indipendenza upstream non verificate.

Il titolo dice CFD, il corpo indica future continuo. Ticker risolto, provider, timestamp/età della quotazione e scadenza esatta non sono esposti. I livelli sono esplicitamente non utilizzabili per entry/SL/TP. Non è possibile stabilire se fossero già superati né valutare SL/TP con candele successive dello stesso contratto. Score 100 non è prova di validità operativa.

### #745 — etichetta oraria

Il messaggio è stato accettato alle 23:59:54 UTC dell'8 novembre, cioè alle 00:59:54 CET del 9 novembre, ma il titolo registrato è `BRIEF ORE 05:00`. La PR #152 propone la dicitura `BRIEF GIORNALIERO`; non è integrata.

### PR SPUTNIK — stato aggiornato

- [PR #131 — endpoint White House RSS](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): OPEN, non draft, 3 commit avanti / 0 indietro rispetto a main; head `db73bdc92e312e58abe94585b83dc26ff9117966`. Due CI intermedie sul commit precedente sono fallite alle 04:52 UTC (#42564158237 e #42564154073); il commit successivo ha corretto la stringa URL. Le CI finali alle 04:53 UTC sono SUCCESS: ranking #42564218665 (184 test) e item-intelligence #42564218686 (45 test), 229 esecuzioni di test complessive. Il runtime #292 usa ancora il vecchio endpoint; l'effetto in produzione non è verificato.
- [PR #150 — non ripetere raccomandazioni senza nuovo item RSS](https://github.com/andreameloni1984-sys/trump-trucker/pull/150): OPEN, non draft, 1 avanti / 0 indietro; CI #42553788540 (185) e #42553788446 (46) SUCCESS, 231 test. Non integrata.
- [PR #152 — etichetta brief giornaliero](https://github.com/andreameloni1984-sys/trump-trucker/pull/152): OPEN, non draft, 3 avanti / 0 indietro; CI #42550701160 (185) e #42550701170 (46) SUCCESS, 231 test. Non integrata.
- [PR #147 — rimuovere handoff GAGARIN](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN, non draft, 4 avanti / 0 indietro; CI #42560177717 (177) e #42560177740 (44) SUCCESS, 221 test. Non integrata.
- [PR #144 — persistenza stato separata](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): ancora OPEN; la produzione continua a committare lo stato su main.

Le CI validano il branch, non il comportamento produttivo successivo. Nessuna di queste PR è stata integrata da PRAVDA.

## 4. GAGARIN — quotazioni e classificazione #171

Il log conferma `PAPER_TRADING_ONLY=1`, ma `DATABASE_URL` è vuota nel job. Anche `NARWHAL_API_KEY` è vuota.

Quotazioni riportate dal monitor:

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

Tutte le otto commodity risultano STALE. Le due coppie Forex hanno dati LIVE ma sono marcate come contesto non operativo. Il riepilogo non espone per le commodity ticker provider risolto, timestamp assoluto della candela, mercato e scadenza esatta.

WTI compare LONG nella classifica, ma è `PAPER_WATCH` e bloccato da `LIVE_DATA_NOT_FRESH`, `TRIGGER_NOT_CONFIRMED`, `TRIGGER_DIRECTION_MISMATCH`, `RR_FAIL` e `FINAL_CONFLUENCE_FAIL`. Non è un ingresso.

Risultati:
- Recorded entries: 0.
- Updated open outcomes: 0.
- New feedback signals: 0.
- New additional live forecasts: 0.
- `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`.

Telegram #3727 è stato accettato dall'API in 403 ms; il corpo non è conservato, quindi strumento, direzione e livelli non sono attribuibili. Non si afferma consegna al dispositivo.

## 5. GAGARIN — journal e artefatti

File letti direttamente da `main`:

- `commodities_prediction_log.json`: 981 record; ultimo `created_at` 2026-09-15T15:45:04.462276+00:00; 945 PENDING e 36 NEUTRALE. Le action includono 21 COMPRA ORA, 292 LONG — ASPETTARE CONFERMA, 15 SHORT — ASPETTARE CONFERMA, 576 ATTENDERE e 77 NON ENTRARE. Le 21 etichette COMPRA ORA sono PENDING, non fill.
- `commodities_monitor_state.json`: timestamp 2026-09-17T03:44:02.566153+00:00; best Benzina RBOB LONG, action ATTENDERE, entry_state BLOCKED, position null.
- `journal.csv`: 11 righe del 17 ottobre, tutte con esito “nessun segnale”.
- `paper_trade_log.csv`: un ticket WTI LONG `LEGACY_IMPORT`, OPEN, entry 96.24, stop 89.37, TP1 103.11; provider, ticker feed, timestamp quote, mercato/scadenza e outcome non presenti.
- `data/paper_open.json`: P0001 WTI LONG OPEN con gli stessi livelli legacy, PnL null.
- `position.json`: vecchia posizione Heating Oil LONG, entry 4.8844, SL 4.5418, TP1 5.4473, aperta il 15 settembre; nessuna prova di fill o riconciliazione con il monitor.
- `gagarin_feedback.csv`: HTTP 404, assente dal repository pubblico.

Il workflow `.github/workflows/gagarin-monitor.yml` dichiara che i journal privati non devono essere committati nel repository pubblico e che la persistenza sarà riattivata solo dopo deploy e verifica dello storage privato. Il valore vuoto di DATABASE_URL è dimostrato per la run #171, non per ogni possibile ambiente o secret.

I record legacy non sono conteggiati come trade verificati.

## 6. GAGARIN — outcome engine e PR

Su `main`, `engine/feedback.py`:
- associa gli stati alle righe tramite symbol e timeframe;
- non verifica provider, ticker quotato, mercato e scadenza del contratto;
- se la stessa candela OHLC tocca SL e TP, controlla prima SL e registra `STOP`.

Questo non rispetta la regola PRAVDA per un doppio tocco intrabar: con una sola candela OHLC l'ordine non è noto e l'esito deve essere non verificabile.

[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) è OPEN, non draft, 6 commit avanti e 6 indietro rispetto a main. Il branch confronta quote symbol, market type e identità futures month/expiry e propone `ESITO NON VERIFICABILE` per il doppio tocco. Ho riletto `_market_contract_match()`: non confronta il provider della riga con il provider dello stato/candele. Il rilievo è già presente nei commenti esistenti; nessun commento duplicato è stato aggiunto.

Altre PR:
- [PR #239 — prova esplicita tipo contratto/scadenza CFD](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/239): OPEN, DRAFT, 2 commit avanti / 0 indietro rispetto alla base PR #238. CI #42544260299 (SOYUZ GAGARIN Tests) e #42544260207 (Execution Layer Tests) SUCCESS. Non autentica un feed e il registry resta vuoto.
- [PR #238 — separazione app symbol, catalogue ticker/slug e feed symbol](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/238): OPEN, DRAFT, stacked; nessun prezzo o registry entry aggiunto.
- [PR #221 — universo operativo a otto commodity, rimozione route FX](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): OPEN, DRAFT; non integrata. Main/run #171 continua a mostrare dieci strumenti inclusi EUR/USD e GBP/USD come contesto.
- [PR #234 e #235 — journal CFD isolato e persistenza durevole](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/234) / [#235](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/235): entrambe DRAFT e stacked; nessuna persistenza durevole dimostrata su main.

## 7. Esiti e statistiche

- Fill verificati: 0.
- SL prima verificato: 0.
- TP prima verificato: 0.
- ESITO_NON_VERIFICABILE: 29 record storici/candidati senza identità e serie successive sufficienti.
- NON_TRADE: 69 notifiche, WATCH, bias preliminari, previsioni non eseguite e messaggi informativi.

Nessun prezzo spot o future continuo è stato sostituito a un contratto non identificato. Non è stato dichiarato che i livelli GOLD #744 siano stati raggiunti o superati. Nessun backtest è stato eseguito o inventato.

## 8. Fonti consultate

- GitHub Actions: [SPUTNIK #292](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537803167), [SPUTNIK polling #52](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537592091), [GAGARIN #171](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42538235058).
- Job logs completi: SPUTNIK job `128905894291`, polling `128905228194`, GAGARIN `128907219566`.
- Workflow YAML su main: `trump_tracker.yml`, `telegram-polling.yml`, `gagarin-monitor.yml`.
- Ledger PRAVDA: blob SHA `a5211b7e5515860443f3860b374e294cd7465bca`.
- Journal e artefatti GAGARIN sopra elencati.
- PR SPUTNIK #131, #144, #147, #150, #152.
- PR GAGARIN #192, #221, #234, #235, #238, #239.

## 9. Prossimo controllo

1. Verificare la prima nuova run schedule produttiva di SPUTNIK e GAGARIN; distinguere sempre collector/monitor da polling e CI.
2. Se #131 viene integrata, verificare il recupero White House RSS nel runtime, non soltanto nei test.
3. Dopo l'eventuale integrazione #150, controllare che una snapshot page-level senza titolo/data/permalink non generi la coppia recommendation/CFD.
4. Verificare quotazioni commodity fresche con ticker, provider, timestamp, mercato e scadenza espliciti.
5. Verificare il confronto provider nel branch #192 prima di considerare attendibile il feedback.
6. Verificare una scrittura e successiva lettura persistente del journal; non dedurla dal solo SUCCESS del workflow.

## 10. Ambito e sicurezza

Questo audit ha prodotto soltanto documentazione PRAVDA su un branch separato. Nessuna modifica a codice, strategia, filtri, punteggi o rischio. Nessun merge/deploy, ordine reale, modifica a secret o Render, servizio a pagamento o accesso Trading 212 dichiarato. Gli ACK Telegram provano solo accettazione API, non consegna/visualizzazione sul dispositivo.

**PAPER ONLY.**
