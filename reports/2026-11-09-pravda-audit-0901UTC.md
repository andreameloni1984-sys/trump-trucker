# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Audit cut-off: 2026-11-09 09:01:57 UTC (10:01:57 Europe/Rome)**

## Esito sintetico

Sono state interrogate le ultime 100 GitHub Actions di ciascun repository, recuperati i log completi delle ultime run produttive disponibili, letti i workflow cron, verificati i journal pubblici e lo stato delle PR rilevanti.

**Non risultano nuove run produttive dopo SPUTNIK #293 / polling #53 e GAGARIN #172.** Le CI delle PR non sono scansioni di mercato.

Non è emerso un nuovo segnale eleggibile per il ledger. Il ledger cumulativo resta invariato.

## 1. Ledger PRAVDA

File cumulativo già pubblicato:
- `reports/pravda-signal-ledger-2026-11-09.csv`
- Branch sorgente: `pravda/audit-2026-11-09-0737UTC`

Verifica CSV con parser a gestione delle virgolette:
- 103 record dati (104 righe logiche inclusa intestazione)
- SPUTNIK: 48
- GAGARIN: 55
- 103 `audit_signature` uniche
- 103 `source_record_id` unici
- 0 duplicati
- 74 `NON_TRADE`
- 29 `ESITO_NON_VERIFICABILE`
- 0 fill verificati
- 0 SL verificati
- 0 TP verificati

Nessuna nuova riga aggiunta: gli ultimi record sono già i messaggi SPUTNIK #746–#748, la candidata Soia e il WATCH GAGARIN #3728. Le statistiche di performance restano N/D: campione di trade verificati = 0. Non sono calcolabili win rate, average R o total R.

## 2. SPUTNIK — run produttiva #293

Run: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770
Job log: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770/job/129006852221
Completamento: 2026-11-09 06:01:50 UTC — SUCCESS.

### Raccolta e ritardi delle notizie
- SEC: HTTP 403; cooldown registrato 21.600 s; 0 filing.
- Transazioni: 0.
- White House: il runtime usa ancora `https://www.whitehouse.gov/feed/`, che restituisce HTTPError.
- Il collector dichiara 3 nuove correlazioni pubbliche, ma il digest espone 2 soli eventi item-level.

Eventi item-level nel digest:
1. Quote post, pubblicato 2026-11-08 23:41:05 UTC, permalink https://www.trumpstruth.org/statuses/43530. Rilevato nel collector alle 2026-11-09 06:01:46.575 UTC: ritardo circa **6 h 20 min 41 s**.
2. Post S.5653, pubblicato 2026-11-09 00:05:49 UTC, permalink https://www.trumpstruth.org/statuses/43532. Stato persistito indica detection 2026-11-09 06:01:46.562743 UTC: ritardo circa **5 h 55 min 58 s**.

Il ritardo di ingestione rende tardiva la correlazione notizia→mercato; il post S.5653 non contiene un annuncio tariffario. La PR #154 corregge l'analogia commerciale automatica basata sulla sola menzione della Cina.

### Messaggi effettivi
| ID | Generazione UTC | Invio/API UTC | Contenuto | Classificazione PRAVDA |
|---|---|---|---|---|
| #746 | 06:01:48.171 | 06:01:48.172 | Digest informativo, 2 eventi | NON_TRADE |
| #747 | 06:01:48.172 | 06:01:48.173 | GOLD LONG preliminare, tecnica 5m, momentum +0,077%/15m, NO_DIRECTIONAL_NEWS; nessun livello | NON_TRADE |
| #748 | 06:01:48.173 | 06:01:48.174 | GOLD LONG EARLY_SETUP con livelli, esplicitamente NOT_EXECUTED | NON_TRADE |

Messaggio #748:
- Entry 4133.2002
- SL 4130.5859
- TP1 4135.8145
- TP2 4138.4289
- ATR 1.7429
- score 100/100 (non è prova di validità operativa)

Difetti verificati nel log:
- Titolo CFD, corpo `FUTURES_CONTINUOUS_FRONT_MONTH`.
- Ticker/strumento esatto non risolto; scadenza UNKNOWN.
- Provider e timestamp quotazione non esposti.
- NARWHAL_REFERENCE_ENABLED=1 ma NARWHAL_API_KEY vuota; messaggio `NOT_CONFIGURED`.
- Indipendenza upstream del confronto SPOT/FUTURES non verificata; componenti dichiarate da SILV.
- Il messaggio #747 riporta LONG 5m, mentre la card #748 riporta TECNICA N/D e D-L-A NEUTRAL/NO_DIRECTION.

Quindi #748 è NOT_EXECUTED, non un trade. Senza ticker, mercato/scadenza e serie prezzi successive dello stesso contratto non si può stabilire se i livelli siano stati raggiunti o superati. Nessun outcome SL/TP attribuibile.

Telegram API round-trip: #746 563 ms, #747 313 ms, #748 322 ms. Sono ACK API; non provano la visualizzazione sul dispositivo. Il log dichiara polling Actions disabilitato e listener dedicato attivo, ma non fornisce una prova indipendente di salute continuativa del listener.

### PR SPUTNIK
- PR #154, classifier China/tariff: OPEN, non merged, 2 commit avanti e 0 indietro rispetto a main; ranking e item-intelligence CI SUCCESS (run #42577454924 e #42577454907). https://github.com/andreameloni1984-sys/trump-trucker/pull/154
- PR #153, propagazione direzione tecnica alla card CFD: OPEN, non merged, 2 avanti e 0 indietro; entrambe le CI SUCCESS. https://github.com/andreameloni1984-sys/trump-trucker/pull/153
- PR #131 White House RSS: ancora OPEN; il runtime #293 continua a usare il vecchio endpoint. https://github.com/andreameloni1984-sys/trump-trucker/pull/131
- La run #293 ha persistito `sputnik_state.json` con commit automatico `8bdf7ab16ec3bfd23d5f3160a4e87dffbfd35396`; nessuna modifica applicativa fatta da PRAVDA.

## 3. GAGARIN — run produttiva #172

Run: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716
Job log: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716/job/129017049476
Completamento: 2026-11-09 06:34:37 UTC — SUCCESS.

### Quotazioni al momento della run
Tutte le 8 commodity hanno provider YAHOO e stato STALE:
- Soia 659,4 s
- Brent 603,0 s
- WTI 602,9 s
- Argento 609,5 s
- Grano 648,2 s
- Rame 613,7 s
- Oro 622,4 s
- Mais 686,3 s

EUR/USD e GBP/USD sono BIQUOTE LIVE a circa 273 s, ma il report li classifica come contesto FX non operativo.

Il log non espone per la candidata Soia il timestamp assoluto della quotazione, il ticker Yahoo effettivamente risolto, il tipo di mercato e la scadenza del contratto.

### Candidata e notifica
- Candidata Soia: ticker logico `SOYBEAN/USD`, SHORT, generata 06:34:30.263983 UTC.
- Provider YAHOO, quote age 659,4 s.
- Stato PAPER_WATCH / BLOCKED.
- Blocchi: LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, FINAL_CONFLUENCE_FAIL.
- Entry, SL, TP e ATR assenti; nessun invio di un segnale operativo.

Telegram #3728: API SEND CONFIRMED alle 06:34:34.113191 UTC, round-trip 478 ms; il corpo del messaggio non è conservato, quindi strumento/direzione/livelli non sono attribuibili. ACK API non equivale a prova di visualizzazione sul dispositivo.

Esito del motore:
- Recorded entries: 0
- Updated open outcomes: 0
- New feedback signals: 0
- New additional live forecasts: 0
- signals=0, open=0, closed=0
- win_rate=N/D, avg_R=N/D, total_R=0.0

### Configurazione effettiva del job
Il workflow main espone:
- PAPER_TRADING_ONLY=1
- MIN_ENTRY_PROBABILITY=40
- MIN_ENTRY_QUALITY=30
- MIN_ENTRY_CONFIDENCE=35
- MIN_ENTRY_RR=2.5
- DATABASE_URL vuota nell'ambiente del job #172.

I valori 40/30/35 sono quelli del workflow effettivamente eseguito; sono diversi dalle soglie 62/55/60 annotate in precedenti specifiche. PRAVDA non ha modificato alcuna soglia.

### Journal e feedback
Letture dirette da main:
- `journal.csv`: 11 righe storiche del 17 ottobre, senza segnali operativi.
- `paper_trade_log.csv`: WTI LONG LEGACY_IMPORT, senza esito; non è prova di fill.
- `data/paper_open.json`: WTI P0001 OPEN legacy; non è prova di fill.
- `position.json`: vecchia posizione Heating Oil LONG del 15 settembre; non è prova di fill.
- `gagarin_feedback.csv`: 404, file assente.
- `commodities_prediction_log.json`: il contenuto recuperabile in testa al file mostra previsioni storiche del 10 settembre; l'ultimo conteggio già verificato era 981 record. In #172 non sono state aggiunte nuove previsioni.

La persistenza durevole del journal non è dimostrata.

### Universo Argento — rettifica e stato PR
Il main attuale contiene ancora XAG/USD abilitato, insieme alle altre 7 commodity e a EUR/USD/GBP/USD di contesto. La PR #241 propone di disabilitare XAG dalla scansione e dal Governor.

L'ultima istruzione diretta dell'utente disponibile a PRAVDA è di escludere Argento/XAG dalla scansione attiva perché troppo volatile. La nota GitHub #6734854568 che affermava il contrario non era supportata da una nuova istruzione diretta; PRAVDA ha inserito la rettifica di perimetro nel commento #6736254808:
https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/241#issuecomment-6736254808

PR #241:
- OPEN, DRAFT, non merged.
- Head `eba9748df31644310437dd9c930284d0c9f70408`, 8 commit avanti e 0 indietro rispetto a main.
- GitHub Actions: 4 workflow SUCCESS e `SOYUZ GAGARIN Tests` FAILURE: 2 failed, 569 passed. Falliscono `test_removed_commodities_are_not_resolved[argento]` e `[silver]`: il resolver restituisce ancora la commodity XAG disabilitata invece di `None`.
- Il check Cloudflare Workers è un controllo esterno, non una GitHub Action, e risulta FAILURE.

PR #221 è DRAFT, 14 avanti e 3 indietro; rimuove EUR/USD e GBP/USD ma conserva XAG, quindi non risolve l'esclusione di Argento richiesta. Nessuna delle due PR è integrata.

### Outcome engine — PR #192
PR #192 è OPEN, non merged, divergente da main: 6 commit avanti e 6 indietro.
https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192

Il branch aggiunge provider/ticker/market/contract al fingerprint e classifica correttamente il doppio tocco SL+TP nella stessa candela come `ESITO NON VERIFICABILE`. Tuttavia, nella funzione `_market_contract_match()` il confronto effettivo copre quote_symbol, market_type e contract_month/expiry, ma non confronta `row.quote_provider` con il provider della serie successiva. Una serie di un provider diverso potrebbe quindi passare se simbolo/mercato/scadenza coincidono. Il difetto è già documentato nei commenti #6706619879 e #6725075554; nessun commento duplicato aggiunto.

## 4. Continuità GitHub Actions

Le ultime 100 run per repository sono state esaminate; le ultime run programmate disponibili sono:

| Processo | Ultima run completata UTC | Frequenza workflow | Gap al cut-off |
|---|---|---:|---:|
| SPUTNIK collector #293 | 06:01:51 | cron `2-59/5 * * * *` | 3 h 00 min 06 s |
| SPUTNIK polling #53 | 05:55:56 | cron `*/5 * * * *` | 3 h 06 min 01 s |
| GAGARIN monitor #172 | 06:34:37 | cron `*/15 * * * *` | 2 h 27 min 20 s |

Non risultano run schedule successive nelle ultime 100 esecuzioni consultate. Le CI PR e i push non sono scansioni produttive. La causa dei gap non è dimostrata.

## 5. Fonti e limiti

Fonti consultate:
- GitHub Actions run list (ultime 100) dei due repository.
- Job logs SPUTNIK #293, polling #53, GAGARIN #172.
- Workflow cron `trump_tracker.yml`, `telegram-polling.yml`, `gagarin-monitor.yml`.
- PR e check-runs #154, #153, #131, #241, #221, #192.
- Main files `commodities/universe.py`, `engine/data.py`, `engine/feedback.py`, `journal.csv`, `paper_trade_log.csv`, `position.json`, `data/paper_open.json`, `commodities_prediction_log.json`.
- Ledger cumulativo PRAVDA, branch audit 07:37 UTC.

Lacune decisive:
- Nessun segnale eseguito verificato.
- Nessuna serie OHLC successiva identificata per il medesimo ticker/mercato/contratto dei livelli SPUTNIK.
- Nessun timestamp assoluto della quotazione né scadenza esatta per GOLD #748 e candidata Soia.
- Corpo Telegram #3728 non conservato.
- Nessun journal feedback persistente leggibile per GAGARIN.
- Provider equality non implementata nella PR #192.
- Ritardi dei workflow non spiegati.

## 6. Prossimo controllo

1. Verificare nuove run produttive e la continuità dei cron.
2. Verificare che il prossimo segnale SPUTNIK esponga provider, timestamp quote, ticker e scadenza del contratto.
3. Verificare la correzione classifier #154 e il passaggio tecnico #153 dopo eventuale merge, senza anticiparne l'esito.
4. Seguire la PR #241: risolvere i due test del resolver XAG e verificare l'esclusione effettiva su main solo dopo integrazione autorizzata.
5. Completare il confronto provider nel motore outcome #192.
6. Verificare una scrittura e successiva lettura del journal GAGARIN.
7. Valutare gli esiti soltanto con prezzi successivi dello stesso identico strumento e contratto, rispettando la sequenza SL/TP o ESITO NON VERIFICABILE.

**PAPER ONLY.** Nessuna modifica a codice applicativo, strategia, filtri, punteggi o rischio; nessun merge/deploy, ordine reale, intervento su secret/Render, servizio a pagamento, accesso Trading212 o prova di consegna Telegram al dispositivo.
