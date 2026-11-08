# PRAVDA — audit SPUTNIK / GAGARIN
**Cut-off: 2026-11-08 19:49:39 UTC (20:49:39 CET)**

## Perimetro e metodo

Verifica in sola lettura dei repository:
- SPUTNIK: `andreameloni1984-sys/trump-trucker`, `main` a `f04411e196d5037db60c9a0975315b5445be4f71`.
- GAGARIN: `andreameloni1984-sys/commodity-news-scanner`, `main` a `444a23e5d183660ebc655f04c4c79ed1370101b6`.

Consultati: ultime 100 GitHub Actions per repository, job e log delle ultime run produttive, artifact list, workflow YAML, ledger CSV, journal legacy, universo strumenti, `engine/feedback.py`, metadati/diff/CI/commenti delle PR pertinenti.

Nessuna modifica a codice, strategia, filtri, score, rischio, secret, Render, broker o ordini. Nessun servizio a pagamento. L'unica scrittura di questo controllo è il presente rapporto Markdown; il ledger non è stato modificato.

## 1. Ledger — integrità, esiti e completezza

File: [pravda-signal-ledger-2026-11-08.csv](pravda-signal-ledger-2026-11-08.csv)  
Blob SHA verificato: `64ddc4b5d26bb2b6d22b418d92c81ec9e7f7bb50`.

Parsing CSV RFC4180 e controllo delle chiavi:
- 91 record dati;
- SPUTNIK: 40;
- GAGARIN: 51;
- 91 `audit_signature` uniche;
- 91 `source_record_id` unici;
- 0 duplicati;
- `NON_TRADE`: 62;
- `ESITO_NON_VERIFICABILE`: 29;
- fill verificati: 0;
- SL verificati: 0;
- TP verificati: 0.

I 29 record non verificabili sono composti da 21 previsioni storiche, 1 ticket legacy, 6 setup CFD non eseguiti e 1 early-bias non eseguito. Non sono 29 trade. Nessun campione di fill ha prezzi successivi dello stesso identico strumento e contratto: win rate, R medio e rendimento restano N/D.

Tra i 29 record `ESITO_NON_VERIFICABILE`, i campi mancanti/non risolti risultano:
- timestamp di invio: 22;
- ticker esatto: 2;
- mercato: 21;
- scadenza: 29;
- provider: 24;
- timestamp quotazione: 27;
- ATR: 17;
- entry/SL/TP1: 1 ciascuno.

Il ledger già contiene gli eventi delle ultime run consultate: SPUTNIK #735/#736/#737 e GAGARIN #3722. Non sono emersi nuovi segnali o messaggi attribuibili a un nuovo record di mercato; nessuna riga aggiunta.

## 2. SPUTNIK — ultima scansione produttiva e nuovi test PR

### Ultima run produttiva

[SPUTNIK run #289 — 42498971172](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42498971172)  
Schedule, SUCCESS, 2026-11-08 16:15:37–16:15:47 UTC; job `128787341086`. Artifact: nessuno.

Dal log:
- SEC: HTTP 403, cooldown 21.600 secondi; nessun filing recuperato;
- White House RSS: HTTPError su `https://www.whitehouse.gov/feed/`;
- TRUTH_ARCHIVE e OGE: OSError ripetuti;
- scansione pubblica: `findings=2`, ma un elemento è un item individuale e l'altro uno snapshot/page-level; quest'ultimo non è contato come nuovo post separato;
- item individuale [Truth Archive #43525](https://www.trumpstruth.org/statuses/43525): pubblicato 13:49:32 UTC, rilevato 16:15:42.637 UTC; ritardo 2h26m10,6s. Classificazione OTHER / NO_ANALOGUE, senza mapping a commodity, direzione o livelli.

Messaggi di produzione:
- #735: digest notizia, API Telegram accettata; 413 ms;
- #736: GOLD NEUTRAL, tecnica 5m indisponibile, nessuna direzione, nessuna quotazione o livello; 377 ms;
- #737: GOLD `NOT_EXECUTED`, score 100, ma nessuna quotazione futures fresca, ticker/provider/timestamp/scadenza risolti, entry, SL, TP o ATR; 323 ms.

#736 e #737 sono due rappresentazioni della stessa analisi GOLD, non due setup indipendenti. Il titolo #737 dice CFD, ma il corpo dichiara `FUTURES_CONTINUOUS_FRONT_MONTH`: senza ticker e scadenza esatti non è né un CFD identificato né un future negoziabile identificato. Score 100 non è validità operativa. Gli ACK API non provano consegna/visualizzazione sul dispositivo.

Il log contiene output di test con `message_id=731` e round-trip 0ms / delivery NOT confirmed: è output della suite di regressione, non un nuovo invio di produzione. Non è stato aggiunto al ledger.

### Polling Telegram

[SPUTNIK polling run #50 — 42498116149](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42498116149): SUCCESS alle 16:05:42 UTC; log `Pending updates: 0`. Non risultano run schedule successive nell'elenco recente consultato.

### PR #147 — miglioramento concreto, ancora non in produzione

[PR #147 — rimozione handoff GAGARIN da SPUTNIK](https://github.com/andreameloni1984-sys/trump-trucker/pull/147):
- OPEN, non merged, non draft;
- head `8b27db788421fb90e18f4435e593a64aa88d51fc`;
- confronto diretto con main: 1 commit ahead / 0 behind;
- diff: rimuove le variabili `GAGARIN_CLOUD_API_URL/API_KEY` dal workflow, elimina il forwarding HTTP e il formatter di conferma GAGARIN, sostituisce i test del vecchio handoff con un test che verifica l'assenza del collegamento;
- CI sul nuovo head, 8 novembre 19:39 UTC: ranking #42516132799 = 177 test SUCCESS; item intelligence #42516132879 = 44 test SUCCESS. Totale 221 test SUCCESS.

È un miglioramento di isolamento ben documentato e ora riallineato a main. Non è però integrato: la run produttiva #289 è stata eseguita sul vecchio main e mostra ancora la sequenza incoerente “handoff disabled” / “confirmation received” / “handoff disabled”, con forwarding 0ms. Il commento PRAVDA #6725075833 aveva già segnalato questa contraddizione; non viene duplicato.

Altra PR: [#145 diagnostica quote Yahoo](https://github.com/andreameloni1984-sys/trump-trucker/pull/145) resta OPEN; confronto con main: 1 ahead / 2 behind. Le CI recenti del suo head (#42505029428 e #42505029400) sono SUCCESS, ma non sono run produttive.

## 3. GAGARIN — monitor, quotazioni e journal

### Ultima run produttiva

[GAGARIN monitor run #169 — 42499039797](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42499039797)  
Schedule, SUCCESS, 2026-11-08 16:16:25–16:16:43 UTC; job `128787549596`. Artifact: nessuno.

Il log elenca 10 strumenti, tutti `MARKET_CLOSED`:
- YAHOO quote age: 152.198,7–161.802,8 secondi (circa 42,3–44,9 ore);
- BIQUOTE per EUR/USD e GBP/USD: circa 152.499–152.500 secondi (circa 42,4 ore).

Non sono esposti timestamp assoluti delle quote, ticker provider risolti, mercato e scadenza contrattuale. I blocker includono dati non freschi, setup/trigger non validi o non confermati e livelli entry/stop/TP/ATR/RR mancanti.

Riepilogo effettivo:
- Recorded entries: 0;
- Updated open outcomes: 0;
- New feedback signals: 0;
- `signals=0 open=0 closed=0`.

Telegram #3722 è stato accettato dall'API in 406 ms, ma il corpo non è conservato: non è possibile attribuirlo a strumento, direzione o livelli. L'ACK non prova consegna al dispositivo.

### Persistenza e artefatti legacy

Nel job #169 `DATABASE_URL` è vuota. Il file `gagarin_feedback.csv` non esiste su main (404). Nessun artifact è allegato alla run.

Artefatti pubblici:
- [paper_trade_log.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/paper_trade_log.csv): WTI del 2026-10-08 16:23 UTC, `LEGACY_IMPORT`, entry 96,24, stop 89,37, TP1 103,11, TP2 106,55. Mancano provider/ticker esecutivo, mercato/contratto, timestamp quote, ATR e prova del fill.
- [position.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/position.json): Heating Oil `HO/USD` LONG, aperto 2026-09-15 13:23:44 UTC, entry 4,8844, stop 4,5418, TP1 5,4473, TP2 5,6284, TP3 5,882. Non è riconciliato con lo stato corrente.
- [journal.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/journal.csv): 11 righe del 17 ottobre, tutte con “nessun segnale”.

Questi record legacy non provano fill né posizioni correnti e non vengono usati per calcolare performance.

### Universo effettivo

[commodities/universe.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities/universe.py) contiene otto commodity (Oro, Argento, Rame, WTI, Brent, Grano, Mais, Soia) e due strumenti Forex ausiliari (EUR/USD, GBP/USD). Platino e Palladio non sono presenti; Argento resta abilitato, nonostante la precedente richiesta di escluderlo. Il paniere runtime non coincide quindi con la selezione richiesta.

## 4. Outcome engine — difetto su main e stato della PR #192

File main: [engine/feedback.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py), blob SHA `41bec9bfab031c8dbf71121cd69d0e9b4c4f663f`.

Sul main:
- il fingerprint usa symbol, direzione, timeframe, livelli e barra, ma non provider/ticker/mercato/scadenza;
- il matching delle candele usa symbol/timeframe senza identità di provider, ticker, mercato e contratto;
- quando una candela OHLC tocca contemporaneamente SL e TP, il codice controlla prima lo stop e registra STOP. L'ordine intrabar non è conoscibile: protocollo PRAVDA richiede `ESITO NON VERIFICABILE`.

[PR #192 — outcome e identità contrattuale](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192):
- OPEN, non merged, non draft;
- head `295dba4b074e564a4c11aa3fca136a8e4360672c`;
- confronto con main: 6 commit ahead / 5 behind (divergente);
- sei CI sul suo head SUCCESS, ma tutte del 5 novembre 06:34 UTC, non una verifica recente né una run produttiva.

La patch corregge il doppio tocco SL+TP nella stessa candela a `ESITO NON VERIFICABILE` e introduce matching di ticker, mercato e identità del future. Resta però una lacuna: `_market_contract_match()` non confronta esplicitamente `row.quote_provider` con il provider della serie di candele. Il provider compare nel fingerprint, ma non nel matching. Rilievo già presente nel commento PRAVDA #6725075554; non duplicato.

Altre correzioni già esistenti:
- [PR #202 persistenza journal PostgreSQL](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): OPEN, draft, non integrata;
- [PR #221 rimozione route FX](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): OPEN, draft, non integrata.

## 5. Frequenza osservata rispetto ai cron

I workflow YAML dichiarano:
- SPUTNIK collector: ogni 5 minuti (`2-59/5 * * * *`);
- SPUTNIK polling: ogni 5 minuti;
- GAGARIN monitor: ogni 15 minuti.

Nelle ultime 100 Actions consultate non compaiono run schedule successive alle seguenti:
- SPUTNIK collector #289: 16:15:37 UTC; gap al cut-off 3h34m02s;
- SPUTNIK polling #50: 16:05:42 UTC; gap 3h43m57s;
- GAGARIN monitor #169: 16:16:25 UTC; gap 3h33m14s.

Le nuove CI SPUTNIK delle 19:39 sono test di PR, non scansioni produttive. La causa dei gap non è dimostrata e non viene attribuita a un filtro orario.

## 6. Conclusione e prossimo controllo

Nessuna nuova operazione verificabile e nessun nuovo record da aggiungere. Il ledger resta integro (91 firme uniche, zero duplicati). Nessun risultato di performance può essere calcolato.

Priorità del prossimo controllo:
1. verificare nuove run schedule produttive, distinguendole dalle CI;
2. verificare che PR #147 venga eventualmente integrata e che la produzione non mostri più il vecchio handoff;
3. alla riapertura dei mercati, verificare freschezza e timestamp assoluto delle quote, provider, ticker, mercato e scadenza;
4. verificare la persistenza privata del journal e la riconciliazione dei vecchi artefatti;
5. verificare che PR #192 includa anche il controllo provider e sia riallineata al main;
6. classificare gli esiti solo come SL prima, TP prima o `ESITO NON VERIFICABILE`, usando prezzi successivi dello stesso identico contratto.

**PAPER ONLY.** Nessun merge/deploy, nessun ordine reale, nessuna modifica a codice, strategia, filtri, score, rischio, secret o Render. Nessun accesso a Trading212 dichiarato. Gli ACK Telegram provano solo l'accettazione API, non la consegna al dispositivo.
