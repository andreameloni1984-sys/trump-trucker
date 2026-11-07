# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Data controllo:** 7 novembre 2026, 17:14 UTC (18:14 Europe/Rome)  
**Modalità:** PAPER ONLY — audit in sola lettura; nessun ordine, merge, deploy o rerun.

## 1. Perimetro e limite di enumerazione Actions

Sono stati recuperati i log completi dei seguenti monitor:

| Bot | Run | Inizio UTC | Fine UTC | Stato |
|---|---:|---:|---:|---|
| SPUTNIK | [#42388887315](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42388887315) | 15:57:48 | 15:58:04 | SUCCESS |
| GAGARIN | [#42386803148](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42386803148) | 15:31:37 | 15:31:58 | SUCCESS |

Alla data del controllo, questi sono gli ultimi monitor di mercato con log completo direttamente recuperato in questa verifica: età rispettivamente circa 1h16m e 1h42m. L'interfaccia GitHub disponibile in questa sessione consente di leggere run note, job, log e artifact, ma non espone una funzione di enumerazione completa delle run recenti. Perciò non si afferma che non possano esistere run successivi senza commit di stato. Entrambi i run esaminati non hanno artifact Actions associati.

Gli altri workflow osservati (polling, daily summary, fetch drivers e test PR) non sono stati conteggiati come scansioni di mercato.

## 2. SPUTNIK — run #42388887315

### Raccolta
- Test di regressione: 30 superati.
- SEC: HTTP 403; cooldown di 21.600 secondi; 0 filing.
- White House RSS: HTTPError.
- Raccolta intelligence pubblica: 1 finding.
- 0 operazioni documentate.
- Handoff GAGARIN disabilitato: GAGARIN_CLOUD_API_URL e GAGARIN_CLOUD_API_KEY non configurati.
- NARWHAL_API_KEY vuoto.

Il finding persistito nel commit [efaa67a](https://github.com/andreameloni1984-sys/trump-trucker/commit/efaa67a227abf8cebfb5eff2b64ad60bece10506) è:
- ID: `df6c3173377e2a283c05395c`;
- fonte: TRUTH_ARCHIVE;
- URL: homepage generale trumpstruth.org;
- titolo e timestamp di pubblicazione: vuoti;
- evidenza: `PUBLIC_SOURCE_TEXT_PAGE_LEVEL`;
- classificazione: `TRADE_ESCALATION` assegnata per analogia storica.

È un record page-level, non un singolo post datato né un catalizzatore commodity verificato.

### GOLD — messaggi #721 e #722
- strumento: GOLD;
- mapping configurato: GC=F;
- mercato dichiarato: futures continuous front-month;
- ticker runtime, provider effettivo, timestamp/prezzo della quotazione e scadenza esatta: non esposti/non verificati;
- NARWHAL: NOT_CONFIGURED;
- bias: NEUTRAL;
- tecnica 5m: UNAVAILABLE;
- score: 70/100;
- decisione: WATCH / NO_DIRECTION;
- stato: NOT_EXECUTED;
- entry, SL, TP e ATR: assenti.

Il log specifica di non usare il front-month continuo per entry/SL/TP perché scadenza e indipendenza upstream non sono verificate. Telegram API ha confermato #721 (738 ms) e #722 (485 ms). Il message_id 731 compare soltanto nei test ed è escluso dalla produzione. ACK API non prova la visualizzazione sul dispositivo.

### Persistenza SPUTNIK
Il job esegue ancora `git push origin main` dopo aver committato `sputnik_state.json`. Il commit efaa67a è quindi una scrittura di stato runtime su main. La ricerca dei branch non ha trovato un branch esatto `sputnik-state`; sono emersi soltanto branch `fix/*` con nomi simili. PR #144 è OPEN, non merged; PR #148 è OPEN, non merged. La separazione della persistenza e il gate sui nuovi catalizzatori non sono quindi dimostrati attivi su main.

Resta valido il rilievo sulla PR #148: il run ha generato una coppia GOLD neutrale pur avendo come nuovo elemento persistito una correlazione page-level non individualmente datata. I test del job includono fixture e non vanno confusi con finding di produzione.

## 3. GAGARIN — run #42386803148

### Configurazione runtime osservata
- PAPER_TRADING_ONLY=1.
- MONITOR_INTERVAL_MINUTES=15.
- soglie loggate: probabilità 40, quality 30, confidence 35, RR 2.5.
- DATABASE_URL: vuoto in tutti i blocchi ambiente osservati.
- NARWHAL_API_KEY: vuoto.

Le soglie sono riportate come prova della configurazione del run, non come valutazione della qualità dei segnali.

### Quotazioni e classificazione

Tutte le otto commodity erano `MARKET_CLOSED`. Provider Yahoo; ticker risolto, timestamp puntuale, prezzo, market type e scadenza non sono stati emessi nel log.

| Strumento | Età quota | Prob. | Quality | Confidence | Direzione |
|---|---:|---:|---:|---:|---|
| Soia | 73.012,9 s (~20h17m) | 50 | 30 | 15 | nessuna |
| Grano | 73.012,7 s | 38 | 15 | 5 | nessuna |
| Brent | 63.412,6 s (~17h37m) | 38 | 15 | 5 | nessuna |
| WTI | 63.412,5 s | 38 | 15 | 5 | nessuna |
| Oro | 63.411,6 s | 40 | 15 | 5 | nessuna |
| Argento | 63.412,3 s | 59 | 49,5 | 32 | LONG |
| Mais | 73.012,7 s | 48 | 30 | 15 | nessuna |
| Rame | 63.412,4 s | 38 | 15 | 5 | nessuna |

Argento è l'unico candidato direzionale, ma è `PAPER_WATCH`, bloccato da LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, CONFIDENCE_FAIL e FINAL_CONFLUENCE_FAIL. Non ha entry, SL, TP o ATR. Nessun ingresso è stato autorizzato.

Il board Telegram #3715 è stato accettato dall'API in 489 ms; il corpo non è conservato e non è possibile attribuirlo con certezza ad Argento. Il monitor riporta:
- Recorded entries: 0;
- Updated open outcomes: 0;
- New feedback signals: 0;
- New additional live forecasts: 0;
- signals=0 open=0 closed=0.

### Universo e Argento
Il file main `commodities/universe.py` abilita ancora Argento (XAG/USD). La PR #30 propone di disabilitarlo, ma resta DRAFT, non merged e non mergeable. L'esclusione non è attiva su main. PRAVDA non ha cambiato il paniere.

### Journal e posizioni legacy
Lettura diretta degli artefatti main:
- `journal.csv`: 11 righe, tutte annotazioni “nessun segnale”;
- `data/paper_open.json`: WTI P0001, LONG, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55, stato OPEN;
- `paper_trade_log.csv`: la stessa posizione WTI P0001, import legacy;
- `position.json`: Heating Oil LONG, entry 4,8844, SL 4,5418, TP1 5,4473, TP2 5,6284, TP3 5,882;
- `gagarin_feedback.csv`: non presente nel repository consultato.

WTI P0001 è una sola posizione descritta in due artefatti, non due trade. Per entrambe le posizioni legacy mancano prova di fill, ticker esecutivo, provider, timestamp della quotazione, mercato/contratto e scadenza. Esito: ESITO NON VERIFICABILE. Non sono state valutate candele di strumenti o contratti non identificati.

## 4. Journal e motore outcome su main

Il monitor espone DATABASE_URL vuoto; il workflow dichiara che la persistenza resta sospesa fino alla disponibilità di storage privato D1. La PR #202 propone invece PostgreSQL/DATABASE_URL. Questa discrepanza D1 vs PostgreSQL è ancora aperta e il backend durevole non è verificato.

Il file main `engine/feedback.py`:
- registra gli ingressi canonici PAPER_ENTRY/PAPER_SIGNAL, non ogni WATCH;
- identifica le righe con symbol/direction/timeframe/livelli/bar timestamp;
- abbina le serie successive per symbol e timeframe, senza verificare provider, market type e scadenza;
- classifica STOP quando SL e TP sono toccati nella stessa candela.

Quindi il main non soddisfa ancora la policy PRAVDA di identità esatta del contratto e di `ESITO NON VERIFICABILE` per lo stesso-bar SL+TP. PR #192 resta OPEN e non merged; il rilievo sulla mancata verifica del provider nel matching della PR è ancora aperto.

## 5. Daily Summary e Telegram

Il workflow GAGARIN `.github/workflows/daily-summary.yml` invia la richiesta HTTP ma stampa “Summary sent” senza analizzare il JSON Telegram, senza richiedere `ok=true` e senza validare un `result.message_id` positivo. L'ultimo run Daily Summary esaminato (#42374841686) non dimostra quindi un ACK API. La PR #190 propone la validazione ma è ancora OPEN e non merged. Non è prova di consegna al dispositivo.

## 6. PR esaminate
- SPUTNIK #144: OPEN, non merged — persistenza stato su branch separato.
- SPUTNIK #148: OPEN, non merged — gate nuove raccomandazioni/catalizzatori.
- GAGARIN #192: OPEN, non merged — identità contratto e outcome.
- GAGARIN #202: OPEN, DRAFT — PostgreSQL journal; disallineamento con D1 nel workflow.
- GAGARIN #190: OPEN, non merged — ACK Telegram Daily Summary.
- GAGARIN #30: OPEN, DRAFT, non mergeable — esclusione Argento proposta ma non attiva su main.

## 7. Ledger e statistiche

Il ledger esistente è stato riletto, non modificato perché non sono emersi nuovi segnali o notifiche univocamente distinti rispetto all'ultimo audit:
- record: 58;
- firme `audit_signature` uniche: 58;
- `source_record_id` unici: 58;
- duplicati: 0;
- GAGARIN: 44 record;
- SPUTNIK: 14 record.

Il ledger contiene predizioni storiche, WATCH, pre-alert, intelligence, notifiche non attribuibili e un ticket legacy; non sono 58 trade.

Statistiche su operazioni verificabili:
- fill verificati: 0;
- SL verificati: 0;
- TP verificati: 0;
- outcome verificabili: 0;
- win rate: N/D;
- average R: N/D.

Nessuna performance o backtest è stato inventato.

## 8. Fonti consultate e limiti
- log completo job SPUTNIK run #42388887315;
- log completo job GAGARIN run #42386803148;
- job e artifact list dei due run (nessun artifact);
- commit SPUTNIK efaa67a e stato su main;
- ledger PRAVDA esistente (blob SHA f13f1a087561f08b32b0abc94f17c209175ad513);
- journal.csv, data/paper_open.json, paper_trade_log.csv, position.json, commodities/universe.py, data/driver_snapshot.json;
- engine/feedback.py e workflow gagarin-monitor.yml / daily-summary.yml;
- PR #144, #148, #192, #202, #190, #30 e relativi commenti.

Limiti: nessun feed prezzo a pagamento usato; nessun accesso Trading 212; nessuna prova di consegna Telegram sul dispositivo; nessuna serie di candele successive con provider/ticker/mercato/scadenza coincidenti con un segnale operativo; nessun fill PAPER recente.

## 9. Prossimo controllo
1. Recuperare le successive run Actions di mercato e verificare gli intervalli reali 5/15 minuti.
2. Verificare che la persistenza SPUTNIK non scriva più su main dopo un'eventuale correzione integrata.
3. Verificare che SPUTNIK non emetta raccomandazioni dalla sola cronologia o da pagine archivio non individuali.
4. Alla riapertura, verificare per ogni candidato GAGARIN ticker risolto, provider, timestamp/prezzo, market type e scadenza.
5. Verificare storage privato e coerenza D1/PostgreSQL prima di certificare il journal.
6. Verificare ACK Telegram Daily Summary con `ok=true` e message_id positivo.
7. Verificare l'effettiva esclusione Argento solo dopo che il cambiamento sarà su main.
8. Attendere un fill PAPER documentato; valutare solo candele successive dello stesso identico strumento e contratto.

**Nessun codice dei bot, strategia, filtro, punteggio o rischio è stato modificato. Nessun merge, deploy, rerun, ordine reale, modifica a Render o ai segreti. È stato pubblicato soltanto questo rapporto di audit.**

**PAPER ONLY.**
