# PRAVDA — audit SPUTNIK / GAGARIN
**Cut-off: 2026-11-08 18:00 UTC (19:00 CET)**

## Sintesi

Verifica indipendente dei log di produzione consultabili, del ledger PRAVDA, dei journal/feedback, dei workflow e delle PR aperte. Nessuna modifica al codice, alla strategia, ai filtri, ai punteggi o al rischio.

- Ledger esistente: **91 record**, **91 firme uniche**, **91 source ID unici**, **0 duplicati**.
- Esiti nel ledger: **62 NON_TRADE**, **29 ESITO_NON_VERIFICABILE**.
- Fill verificati: **0**; SL verificati: **0**; TP verificati: **0**.
- Win rate, average R e total R: **N/D**.
- Nessuna nuova riga aggiunta: i record SPUTNIK #735–#737 e GAGARIN #3722 erano già presenti.
- Nessun backtest o risultato è stato inventato.

Ledger: [pravda-signal-ledger-2026-11-08.csv](pravda-signal-ledger-2026-11-08.csv)

## 1. Controllo del ledger e record storici

Il CSV su main è stato riletto e analizzato: 91 righe dati; audit_signature e source_record_id sono entrambi unici.

I 21 record `historical_prediction_candidate` provengono da `commodities_prediction_log.json` e non sono esecuzioni:
- 19 previsioni RBOB (`RB/USD`);
- 2 previsioni Heating Oil (`HO/USD`);
- timestamp di generazione tra il 10 e il 15 settembre 2026;
- tutte in stato `PENDING`, con esito `ESITO_NON_VERIFICABILE`;
- nessun provider, timestamp della quotazione, mercato o scadenza registrati; invio Telegram non registrato;
- 15 righe del 10 settembre non hanno ATR; le 6 del 15 settembre riportano ATR.

I livelli numerici entry/SL/TP presenti non bastano a ricostruire la serie storica corretta: senza provider, ticker risolto, mercato e scadenza non è lecito abbinare prezzi successivi. Questi 21 record restano previsioni storiche, non trade.

Altri artefatti GAGARIN:
- `paper_trade_log.csv`: WTI LONG del 8 ottobre, `LEGACY_IMPORT`, senza provider, quote timestamp, mercato/scadenza o PnL.
- `data/paper_open.json`: WTI P0001 marcato OPEN.
- `position.json`: vecchia posizione Heating Oil LONG aperta il 15 settembre.
- `journal.csv`: righe del 17 ottobre con “nessun segnale”.
- `gagarin_feedback.csv`: assente su main.

Questi artefatti legacy non sono riconciliati con il monitor corrente e non provano un fill.

## 2. SPUTNIK — produzione e notifiche

Run consultata: [#42498971172](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42498971172), job #128787341086, SUCCESS. Il log colloca l'avvio del collector alle 16:15:41.809 UTC e la fine del processo alle 16:15:44 circa.

Evidenze:
- SEC CIK 0001849635: HTTP 403, cooldown 21.600 secondi, zero filing.
- White House RSS configurato su `https://www.whitehouse.gov/feed/`: HTTPError.
- Nel log compaiono anche errori OSError per TRUTH_ARCHIVE, OGE e WHITE_HOUSE.
- Il collector riporta `findings=2`, ma il digest contiene un solo item pubblico individuale verificabile; lo snapshot pagina archivio non ha un ID individuale e non viene contato come un secondo post.
- Item [Trump's Truth #43525](https://www.trumpstruth.org/statuses/43525): pubblicato 13:49:32 UTC, rilevato 16:15:42.637 UTC; ritardo **2h26m10,6s**. Classificazione OTHER, NO_ANALOGUE, nessun mapping commodity, direzione, quotazione o livello.

Messaggi live del collector:
- #735: digest informativo, API ACK 413 ms.
- #736: GOLD NEUTRAL; tecnica 5m indisponibile, nessun dato direzionale e nessuna quotazione/livello; API ACK 377 ms.
- #737: GOLD, `NOT_EXECUTED`, score 100, bias NEUTRAL; nessuna quotazione futures fresca, NARWHAL non configurato, future continuo front-month senza scadenza esatta. Nessun entry/SL/TP/ATR; API ACK 323 ms.

I messaggi #736 e #737 sono due rappresentazioni della stessa analisi GOLD, non due setup. Score 100 non è validità operativa. L'etichetta “ANALISI CFD” del #737 è incompatibile con il corpo che dichiara un future continuo senza scadenza: non è possibile identificare un CFD o un contratto future esatto.

Il log della stessa run contiene anche un ACK #731 con round-trip 0 ms nella fase precedente all'avvio di `python trump_tracker.py`, durante i test di regressione. È un output del test, non un nuovo invio di produzione; non è stato aggiunto al ledger né contato come duplicato.

### Handoff SPUTNIK → GAGARIN

Il log stampa:
1. “GAGARIN handoff disabled; GAGARIN_CLOUD_API_URL/API_KEY not configured”;
2. subito dopo “GAGARIN confirmation received for 1 catalyst event(s)”;
3. poi ancora handoff disabled e forwarding=0 ms.

URL e key vuoti e forwarding 0 ms non provano un invio API. La frase “confirmation received” è però incoerente con lo stato disabilitato e potrebbe riferirsi a stato precedente/cache. Rilievo registrato nella discussione della [PR #147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147), commento #6725075833.

### Persistenza SPUTNIK su main

Il workflow main `trump_tracker.yml` concede `contents: write` e termina con `git push origin main`. La run #42498971172 ha effettivamente creato il commit [71b4b22](https://github.com/andreameloni1984-sys/trump-trucker/commit/71b4b22fe23b17cac782a9a3a9b44a4f1354a7cb) aggiornando `sputnik_state.json` su main. La PR #144 per spostare la persistenza è ancora aperta; rispetto al main corrente il branch è divergente (1 commit avanti, 31 indietro). Nessuna modifica è stata eseguita da PRAVDA.

## 3. GAGARIN — monitor, prezzi e feedback

Run consultata: [#42499039797](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42499039797), job #128787549596, SUCCESS; log circa 16:16:29–16:16:40 UTC.

Il log dichiara 10 strumenti analizzati: 8 commodity operative e 2 FX ausiliari. Tutti risultano `MARKET_CLOSED`.
- YAHOO: quote age da 152.198,7 a 161.802,8 secondi (circa **42h16m–44h56m**).
- BIQUOTE per EUR/USD e GBP/USD: circa 152.499–152.500 secondi (circa **42h21m**).
- Il log non espone timestamp assoluto della quotazione, ticker risolto, mercato e scadenza del contratto.

Risultato del monitor:
- Recorded entries: 0
- Updated open outcomes: 0
- New feedback signals: 0
- `signals=0 open=0 closed=0`

Telegram #3722 è stato accettato dall'API in 406 ms, ma il corpo non è conservato: nessuna attribuzione affidabile a strumento/direzione/livelli. ACK API non prova la visualizzazione sul dispositivo.

### Persistenza e riepilogo giornaliero

Il workflow `gagarin-monitor.yml` dichiara `DATABASE_URL: secrets.DATABASE_URL`, ma il valore risulta vuoto nel runtime. Di conseguenza il feedback non può usare il backend PostgreSQL e `gagarin_feedback.csv` non è presente su main.

La run Daily Summary [#42484703932](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42484703932) stampa “Summary sent” dopo la risposta HTTP, ma il workflow non legge/valida il JSON Telegram (`ok=true` e `result.message_id`); non esiste prova dell'ACK applicativo né il corpo del messaggio. Il daily-summary workflow non passa inoltre DATABASE_URL al processo di riepilogo.

### Driver macro

`data/driver_snapshot.json` è stato letto alle 13:55:58 UTC:
- EIA crude stocks e gas storage: `no_data`;
- WASDE wheat/corn/soybeans: valori null;
- FRED dollar index: data 30 ottobre 2026;
- real rate 10Y: data 5 novembre 2026;
- la maggior parte delle variabili rimane UNKNOWN.

È contesto macro parziale, non una quotazione né un segnale operativo.

## 4. Difetto del motore outcome GAGARIN

Su main, `engine/feedback.py` (blob `41bec9bfab031c8dbf71121cd69d0e9b4c4f663f`) presenta difetti dimostrati:
- il fingerprint usa symbol, direzione, timeframe, livelli e timestamp barra, ma non provider, ticker risolto, mercato e scadenza;
- il matching delle candele successive usa symbol/timeframe, con fallback sul solo symbol;
- non viene verificata l'identità del provider/mercato/contratto;
- se una candela OHLC tocca sia SL sia TP, il codice controlla prima SL e registra STOP. OHLC non permette di stabilire l'ordine intrabar.

La [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) propone fingerprint con provider/ticker/mercato/scadenza e `ESITO NON VERIFICABILE` per la stessa candela ambigua. È OPEN, non merged; il branch è 6 commit avanti e 5 indietro rispetto al main corrente. I sei workflow CI sul suo head storico risultano SUCCESS.

Ulteriore difetto rilevato nel branch #192: `_market_contract_match()` confronta quote_symbol, market_type e mese/scadenza futures, ma non confronta il provider del record con quello dello stato/candele. Il provider è incluso nel fingerprint ma non nel controllo di corrispondenza delle candele. Rilievo registrato nel commento #6725075554 della PR #192.

## 5. PR e CI consultate

### SPUTNIK
- [PR #145 — quote provenance/Yahoo diagnostics](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN, non merged, 1 avanti/0 indietro; CI #42505029428 (186 test) e #42505029400 (68 test) SUCCESS. Totale 254 test; non prova una quotazione live.
- [PR #147 — rimozione handoff GAGARIN](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN, non merged, 1 avanti/0 indietro; CI #42502648241 e #42502648378 SUCCESS (44+177 test).
- [PR #131 — endpoint White House](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): OPEN, non merged, branch divergente 1 avanti/9 indietro; il main continua a usare il vecchio endpoint, come dimostra il run.
- [PR #148 — anti-ripetizione](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN, non merged, divergente 2 avanti/22 indietro.
- [PR #144 — persistenza off-main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN, non merged, divergente 1 avanti/31 indietro.

### GAGARIN
- [PR #192 — identità contratto/outcome ambiguo](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, non merged, 6 avanti/5 indietro; correzione utile ma manca il confronto provider nel matching.
- [PR #221 — universo otto commodity e rimozione FX](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): DRAFT/OPEN, 14 avanti/2 indietro; sei workflow CI SUCCESS. Non è produzione.
- [PR #231 — Governor, calendario economico, contesto White House/Trump e routing cereali](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/231): DRAFT/OPEN, 31 avanti/2 indietro; quattro workflow CI SUCCESS. Non è produzione.
- [PR #200](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/200) e [PR #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): DRAFT/OPEN, persistenza feedback/journal non integrata.
- Le PR Trading 212 #236/#237 riguardano prove di identità del catalogo, non un feed quotazioni né accesso all'account; non sono state usate per valutare prezzi.

## 6. Cadenza GitHub Actions e limiti di osservabilità

Cron letti dai workflow main:
- SPUTNIK collector: `2-59/5 * * * *`;
- SPUTNIK Telegram polling: `*/5 * * * *`;
- GAGARIN monitor: `*/15 * * * *`.

Ultime run complete con log interrogabili in questo controllo:
- SPUTNIK collector #42498971172: 16:15:41 UTC; al cut-off 18:00, gap circa **1h44m**.
- SPUTNIK polling #42498116149: 16:05:45 UTC; gap circa **1h54m**. SUCCESS, `Pending updates: 0`.
- GAGARIN monitor #42499039797: 16:16:29 UTC; gap circa **1h43m**.

Il connettore GitHub disponibile in questo controllo ha consentito di recuperare log di run specifiche e CI delle PR, ma non ha esposto un elenco completo e paginabile di tutte le run schedule successive. I gap sono quindi misurati dall'ultima run completa interrogata: non si dichiara come fatto assoluto che non esistano run successive non consultabili. Le singole run citate sono SUCCESS; questo non dimostra il rispetto della cadenza cron.

## 7. Prossimo controllo

1. Interrogare la prossima run schedule completa di SPUTNIK e GAGARIN, distinguendola da test, daily summary e refresh driver.
2. Verificare il ritorno dei mercati e quote fresche con timestamp assoluto, provider, ticker risolto, mercato e scadenza.
3. Conservare il corpo o un hash dei messaggi Telegram insieme a message_id e timestamp, senza equiparare ACK API a consegna al dispositivo.
4. Verificare le PR esistenti e che le correzioni siano effettivamente su main prima di attribuire loro effetti in produzione.
5. Per ogni eventuale segnale idoneo, valutare solo candele successive dello stesso provider/ticker/mercato/contratto: SL prima, TP prima, oppure ESITO NON VERIFICABILE.

## Perimetro

PRAVDA ha aggiunto commenti di audit alle PR #147 (commento #6725075833) e #192 (commento #6725075554). Nessun file di codice è stato modificato. Nessun merge/deploy, ordine reale, modifica a secret o Render, servizio a pagamento o accesso a Trading 212. Nessuna consegna Telegram al dispositivo dichiarata. **PAPER ONLY.**
