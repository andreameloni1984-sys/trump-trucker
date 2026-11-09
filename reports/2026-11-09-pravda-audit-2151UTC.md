# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
## Controllo #20 — 9 novembre 2026, 22:51 CET (21:51 UTC)

## Esito sintetico

Verifica read-only dei due repository, dei log integrali delle Actions disponibili, dei file correnti su `main`, dei journal pubblici, dei metadati/diff delle PR e del ledger cumulativo.

**Nessun nuovo trade verificabile e nessuna nuova riga da aggiungere al ledger.** Il nuovo riscontro più rilevante è che il collector SPUTNIK #295 ha registrato un finding OGE page-level privo di titolo e timestamp di pubblicazione e, subito dopo, ha generato nuovamente una coppia di messaggi GOLD LONG (#752/#753) con `NO_DIRECTIONAL_NEWS`. La PR #150 contiene la correzione mirata ed è aggiornata sul main corrente con CI riuscita, ma non è integrata.

Per GAGARIN, il commit main #631727 ha effettivamente rimosso il thread automatico Invest e portato il monitor Render a 5 minuti; tuttavia il paniere main resta a 13 strumenti. La PR #248 propone il ripristino esatto degli otto strumenti commodity approvati ed ha 7/7 workflow CI riusciti, ma è ancora DRAFT/non integrata e il check Cloudflare sul branch è fallito. Nessuna scansione produttiva successiva al nuovo commit è stata verificata.

**Limite Actions:** il connettore GitHub disponibile permette di recuperare i job/log di run note e i run associati a commit PR, ma non espone un elenco paginato completo di tutte le run schedule di un workflow. Perciò #295 e #173 sono gli ultimi log produttivi integrali recuperati in questo controllo, non una prova assoluta che non esistano run successive.

Nessuna modifica applicativa, nessun merge/deploy, nessun ordine reale. PAPER ONLY.

## 1. Registro storico PRAVDA

Ledger letto dal branch precedente `pravda/audit-2026-11-09-2032UTC` e analizzato con parser CSV che rispetta i campi quotati.

- Record: **106**
- SPUTNIK: **50**
- GAGARIN: **56**
- Firme uniche: **106**
- Source ID unici: **106**
- Duplicati firma: **0**
- Duplicati source ID: **0**
- NON_TRADE: **77**
- ESITO_NON_VERIFICABILE: **29**
- Fill verificati: **0**
- SL verificati: **0**
- TP verificati: **0**

SHA ledger: `41a1339c2047c86ad9026ab131d9a8015d0cd710`. Nessuna riga aggiunta: gli eventi #751, #753 e #3734 erano già presenti e non sono comparsi nuovi segnali da registrare.

Win rate, Average R e Total R: **N/D**. I record non sono trade; NOT_EXECUTED, WATCH e PENDING non costituiscono fill.

Ledger: [CSV cumulativo](https://github.com/andreameloni1984-sys/trump-trucker/blob/pravda/audit-2026-11-09-2032UTC/reports/pravda-signal-ledger-2026-11-09.csv).

## 2. SPUTNIK — produzione, fonti e segnali

### 2.1 Run #295

Repository main SHA: `6c3095f1534550b0b4e77170f1428db833253c05`.

[Collector #295 — Actions](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42650624196)

- Evento: SCHEDULE.
- Avvio: 2026-11-09 16:02:05 UTC.
- Completamento: 16:02:23 UTC.
- Job: `sputnik`, SUCCESS.
- Job log: ID `129275664568`.

Riscontri del log runtime, distinti dai test unitari che precedono l'esecuzione:

- SEC: HTTP 403; cooldown 21.600 secondi; filing 0.
- White House RSS `https://www.whitehouse.gov/feed/`: HTTPError.
- Intelligence pubblica: 1 finding; durata 6.665 ms.
- GAGARIN forwarding: 0 ms; nessuna conferma di handoff riuscito.
- NARWHAL_REFERENCE_ENABLED=1, ma NARWHAL_API_KEY vuota.
- I messaggi Telegram #752 e #753 hanno API acceptance confermata; ciò non dimostra la visualizzazione sul dispositivo.

Il commit di persistenza [6c3095f](https://github.com/andreameloni1984-sys/trump-trucker/commit/6c3095f1534550b0b4e77170f1428db833253c05) aggiorna effettivamente `sputnik_state.json`: timestamp, offset Telegram, fingerprint OGE e `intelligence_history`.

**Precisazione:** la stringa “GAGARIN handoff disabled” appare nel blocco dei test unitari precedente al runtime, non va attribuita alla scansione produttiva. Il runtime registra solo `GAGARIN forwarding=0ms`; non c'è prova di consegna a GAGARIN.

### 2.2 Nuova riproduzione del problema page-level — GOLD LONG #752/#753

Nel diff di `sputnik_state.json` del run #295 è presente il finding:

- event_id: `d6b0ef156154af76e574dd50`
- fonte: OGE, URL `https://www.oge.gov/`
- evidence: `PUBLIC_SOURCE_TEXT_PAGE_LEVEL`
- title: vuoto
- published: vuoto
- detected_at: `2026-11-09T16:02:16.531408+00:00`
- event_type: OTHER
- historical evidence: NO_ANALOGUE

Il collector ha poi prodotto due messaggi collegati: #752 (analisi preliminare) e #753 (card CFD). Non vanno contati come due opportunità.

**Firma/ID ledger:** `run:42650624196/telegram_message:753`.

| Campo | Valore |
|---|---|
| Generazione card | 2026-11-09 16:02:18.5845249 UTC |
| Timestamp invio registrato | 16:02:18.5856255 UTC |
| Differenza generazione→invio registrato | circa 1,10 ms |
| API round-trip #752 / #753 | 590 ms / 608 ms |
| Strumento | GOLD |
| Ticker contrattuale | NOT_RESOLVED |
| Mercato dichiarato | titolo CFD; corpo FUTURES_CONTINUOUS_FRONT_MONTH |
| Scadenza | UNKNOWN |
| Provider / quote timestamp / quote age | non esposti |
| Prezzo di riferimento | non registrato |
| Direzione | LONG |
| Direzione tecnica | LONG 5m; D-L-A LONG — ALIGNS |
| Entry | 4129.2998 |
| SL | 4126.9106 |
| TP1 | 4131.689 |
| TP2 | 4134.0781 |
| TP3 | assente |
| ATR | 1.5928 |
| Score | 100 |
| Stato | NOT_EXECUTED |

Il messaggio #752 riporta momentum +0,031% negli ultimi 15 minuti e `NO_DIRECTIONAL_NEWS`. La card #753 avverte che il front-month è continuo, la scadenza esatta e l'indipendenza upstream non sono verificate e che i livelli non vanno usati.

**Classificazione PRAVDA: NON_TRADE.** Score 100 non certifica validità operativa; NOT_EXECUTED non è un fill. Non sono disponibili candele successive dello stesso ticker/contratto, quindi nessun esito SL/TP è attribuibile.

### 2.3 GOLD SHORT #750/#751, già registrato

**Firma:** `PRAVDA-SPUTNIK-CFD-RUN42645788987-20261109T153313Z-GOLD-SHORT-4125.6001-4128.3859-4122.8143-4120.0285`.

- Generazione #751: 15:33:13.053057 UTC.
- Invio registrato: 15:33:13.0545671 UTC.
- API round-trip: 395 ms.
- GOLD SHORT; entry 4125.6001; SL 4128.3859; TP1 4122.8143; TP2 4120.0285; ATR 1.8572; score 100; NOT_EXECUTED.
- Run #294 era PUSH, non SCHEDULE.
- Ticker e scadenza non risolti; provider e quote timestamp mancanti; D-L-A NEUTRAL; la card dice di non usare i livelli.

È già nel ledger e non viene duplicato. Esito: NON_TRADE, nessun forward OHLC dello stesso contratto.

### 2.4 Correzioni SPUTNIK già esistenti

- [PR #150 — impedire raccomandazioni ripetute da snapshot page-level](https://github.com/andreameloni1984-sys/trump-trucker/pull/150): OPEN, non merged, base main corrente; confronto 1 ahead / 0 behind; due workflow CI sul head corrente SUCCESS. Il fix riusa l'idoneità item-level del digest. Il run #295 costituisce una nuova riproduzione produttiva: OGE page-level senza data/permalink → GOLD LONG tecnico senza notizie direzionali. Commento PRAVDA aggiunto: [ID 6752498088](https://github.com/andreameloni1984-sys/trump-trucker/pull/150#issuecomment-6752498088).
- [PR #156 — selezionare i 30 record intelligence più recenti](https://github.com/andreameloni1984-sys/trump-trucker/pull/156): OPEN, 1 ahead / 0 behind, due CI SUCCESS. Corregge `values()[-30:]` su una cronologia newest-first; il difetto rimane su main.
- [PR #147 — rimuovere il coupling SPUTNIK→GAGARIN](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN/non integrata. Main conserva ancora il percorso opzionale e i riferimenti alle variabili di handoff; nessun handoff produttivo è provato dal run #295.

Cron dichiarato collector: `2-59/5 * * * *`. L'ultimo log integrale recuperato è #295; al controllo dista circa 5h49m. Non certifico l'assenza di run successive perché manca una query completa delle Actions schedule.

## 3. GAGARIN — main, universo e scansione

Repository main: `631727912b3a2022379a4460f4b6f756eba6991f`, commit 2026-11-09 20:00:34 UTC.

### 3.1 Modifica main #631727

Il diff conferma che main ha già:
- rimosso il thread Render `invest_auto_loop` che analizzava titoli MSFT/equity e interrogava l'integrazione Trading 212 Invest Demo;
- rimosso dal welcome/menu i vecchi comandi/profili 212;
- impostato `position_monitor_loop` a 5 minuti;
- mantenuto PAPER ONLY.

Questo non prova un deployment Render successivo al commit. Non è una scansione produttiva.

### 3.2 Universo main: 13, non otto

Il file corrente `commodities/universe.py` contiene 13 strumenti abilitati:

- 8 commodity: XAU/USD, XAG/USD, COPPER/USD, WTI/USD, BRENT/USD, WHEAT/USD, CORN/USD, SOYBEAN/USD;
- EUR/USD;
- DAX;
- SP500;
- NVDA;
- TSLA.

`operational_commodities()` restituisce tutti gli strumenti abilitati. Quindi FX/indici/azioni non sono solo documentazione: sono nel percorso operativo di main.

### 3.3 PR #248 — correzione a otto commodity

[PR #248](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/248):

- OPEN, DRAFT, non merged.
- Base SHA: main `6317279`; head `87367caf`.
- 17 commit, 13 file.
- Ripristina esattamente: Oro, Argento, Rame, WTI, Brent, Grano, Mais, Soia.
- Applica la stessa allowlist a universe, Governor, provider map, selector schedulato, Telegram e percorsi Cloud API.
- BiQuote resta riferimento CFD indipendente per i simboli supportati; non viene usato come fallback futures.
- 7/7 workflow GitHub sul head SUCCESS; il body PR riporta 570 test d'integrazione superati.
- Il bot Cloudflare ha però registrato un deployment failure sul branch PR alle 20:18 UTC. Non è un deploy Render e non prova un cambiamento in produzione.

La lista di otto corrisponde all'ultima selezione esplicita dell'utente, Argento incluso. La precedente indicazione di togliere Argento era riferita alla scansione rapida M5 e non va confusa automaticamente con la selezione complessiva successiva.

### 3.4 PR #249 — proposta superseded ma diff contraddittorio

[PR #249](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/249) ha body “SUPERSEDED — DO NOT MERGE” e rimanda alla #248. Il diff, però, continua ad aggiungere un documento e un JSON che dichiarano un paniere a 13 strumenti. Body e patch sono contraddittori.

Commento PRAVDA aggiunto: [ID 6752498767](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/249#issuecomment-6752498767). Non usare la #249 per autorizzare un universo a 13.

### 3.5 Due cadenze distinte

- Render `telegram/render_runner.py`: `interval = 5 * 60`.
- GitHub Actions `.github/workflows/gagarin-monitor.yml`: cron `*/15 * * * *`, `MONITOR_INTERVAL_MINUTES=15`.

Il codice Render a 5 minuti è su main, ma non è stata verificata l'esecuzione del servizio dopo il commit. La GitHub Action resta a 15 minuti.

### 3.6 Ultimo log produttivo integrale recuperato: #173

[Monitor #173 — Actions](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42659137635)

- Avvio: 2026-11-09 16:52:38 UTC.
- Completamento: 16:53:01 UTC.
- Commit eseguito: `50b25a80`, precedente al commit main #631727.
- Job: `Run Gagarin directly on GitHub`, SUCCESS.
- Job log: ID `129305621100`.

Questa scansione non verifica il nuovo universo a 13 né il nuovo commit 5m.

Quotazioni registrate nel run #173:

| Strumento | Provider | Età | Stato |
|---|---|---:|---|
| Rame | YAHOO | 604,7 s | STALE |
| Grano | YAHOO | 604,0 s | STALE |
| WTI | YAHOO | 601,8 s | STALE |
| Mais | YAHOO | 606,1 s | STALE |
| Soia | YAHOO | 603,5 s | STALE |
| Oro | YAHOO | 602,6 s | STALE |
| Brent | YAHOO | 605,0 s | STALE |
| Argento | YAHOO | 626,6 s | STALE |
| EUR/USD | BIQUOTE | 176,2 s | LIVE, ausiliario |
| GBP/USD | BIQUOTE | 176,9 s | LIVE, ausiliario |

Tutte le otto commodity erano stale. Il run ha registrato:
- Recorded entries: 0.
- Updated open outcomes: 0.
- New feedback signals: 0.
- New additional live forecasts: 0.
- `signals=0 open=0 closed=0`.

Telegram #3734 è stato accettato dall'API (556 ms), ma il corpo non è conservato: strumento, direzione e livelli non attribuibili. Firma già presente: `run:42659137635/telegram_watch_pre_alert:3734`. È un WATCH pre-alert, non un trade.

La run di test #42688792974 delle 20:00 è un job `test`, non un monitor di mercato. Non è stata recuperata una scansione produttiva successiva al commit #631727.

## 4. GAGARIN — journal e outcome engine

### 4.1 Prediction log

File main: [commodities_prediction_log.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities_prediction_log.json), SHA `86df1b3eb1923f2a310b0acde7ca8a7e176c63a2`.

- Record: 981.
- ID unici: 981.
- Duplicati ID: 0.
- PENDING: 945.
- NEUTRALE: 36.
- Azioni: NON ENTRARE 77; ATTENDERE 576; SHORT — ASPETTARE CONFERMA 15; LONG — ASPETTARE CONFERMA 292; COMPRA ORA 21.
- Ultimo record: 2026-09-15 15:45:04 UTC, Benzina RBOB, COMPRA ORA, PENDING.

Le 21 righe COMPRA ORA sono PENDING, non fill.

### 4.2 Altri archivi

- [paper_trade_log.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/paper_trade_log.csv): una riga WTI `LEGACY_IMPORT`, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55; P&L vuoto e nota “Nessun esito”. Nessuna prova di fill.
- [position.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/position.json): Heating Oil LONG legacy, aperta il 15 settembre, nessuna prova di chiusura/fill.
- `gagarin_feedback.csv`: non presente nel main pubblico.
- Nel log #173 `DATABASE_URL` è vuota.

Il workflow dichiara che i journal sono dati operativi privati e non vanno committati pubblicamente. La persistenza durevole cross-run non è però dimostrata. [PR #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202) propone PostgreSQL, ma è DRAFT/non integrata.

### 4.3 Outcome engine su main

File: [engine/feedback.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py), blob SHA `41bec9bfab031c8dbf71121cd69d0e9b4c4f663f`.

- FIELDS contiene `data_source` e `data_status`, ma non quote_provider, quote_symbol, market_type, contract_month o contract_expiry.
- Il signal_id è costruito da symbol, direction, timeframe, livelli e timestamp candela; non include provider/mercato/contratto.
- `update_open_outcomes` abbina per (symbol, timeframe), con fallback per symbol quando esiste un solo stato.
- Il codice valuta `stop_hit` prima di `hit_targets`: una candela che tocca SL e TP può essere classificata STOP.

La [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) aggiunge provenienza e identità contrattuale e tratta il doppio tocco come ESITO NON VERIFICABILE. Tuttavia:
- resta OPEN/non integrata;
- confronto attuale: 6 commit ahead / 10 behind main;
- `_market_contract_match` confronta ticker quotato, market type e contratto futures, ma non confronta esplicitamente il provider del segnale con quello dello stato successivo.

Non certificare performance finché il matching non è completo e la correzione non è verificata sul main corrente.

### 4.4 Telegram polling

[Polling #20 — Actions](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42660005021), job log ID `129308702941`, FAILURE.

Telegram diagnostic OK, ma `getUpdates` restituisce 409: webhook attivo e polling incompatibile.

[PR #175](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175) propone di saltare il polling senza cancellare webhook o confermare update. È OPEN/non integrata; confronto attuale 1 ahead / 7 behind main.

## 5. Pull Request e correzioni già presenti

| Repository | PR | Stato | Rilievo |
|---|---:|---|---|
| SPUTNIK | #150 | OPEN, CI 2/2 SUCCESS | Corregge trigger da snapshot page-level; nuova riproduzione #295 |
| SPUTNIK | #156 | OPEN, CI 2/2 SUCCESS | Corregge selezione dei 30 item intelligence più recenti |
| SPUTNIK | #147 | OPEN | Rimuove coupling opzionale verso GAGARIN; non integrata |
| GAGARIN | #248 | DRAFT, CI 7/7 SUCCESS | Correzione esatta universo a otto commodity; Cloudflare check fallito |
| GAGARIN | #249 | OPEN, SUPERSEDED | Body dice DO NOT MERGE, diff conserva configurazione a 13 |
| GAGARIN | #192 | OPEN, diverged 6/10 | Outcome identity e doppio tocco; provider equality ancora mancante |
| GAGARIN | #175 | OPEN, diverged 1/7 | Gestione Telegram 409 |
| GAGARIN | #202 | DRAFT | Persistenza PostgreSQL non integrata |
| GAGARIN | #243 | DRAFT | La rimozione del loop Invest AUTO è già su main via commit #631727; PR più ampia non integrata |

Nessuna PR è stata approvata o integrata da PRAVDA.

## 6. Esiti e statistiche

| Categoria | Conteggio |
|---|---:|
| Record ledger | 106 |
| Firme uniche | 106 |
| Duplicati | 0 |
| NON_TRADE | 77 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |

Non esistono campioni con fill e OHLC successivo dello stesso identico ticker/mercato/contratto/provider sufficienti per statistiche di performance.

- Win rate: N/D.
- Average R: N/D.
- Total R: N/D.

Nessun backtest o esito retrospettivo inventato.

## 7. Fonti consultate

- SPUTNIK Actions #295 e job log integrale; commit `6c3095f` e diff `sputnik_state.json`.
- GAGARIN Actions #173, Telegram Polling #20 e test #42688792974.
- Main files: `trump_tracker.yml`, `commodities/universe.py`, `gagarin-monitor.yml`, `telegram/render_runner.py`, `engine/feedback.py`.
- Journal pubblici: `commodities_prediction_log.json`, `paper_trade_log.csv`, `position.json`.
- PR #150, #147, #156, #248, #249, #192, #175, #202, #243 e relativi diff, metadata e check.

## 8. Prossimo controllo

1. Verificare il prossimo log collector SPUTNIK e se la PR #150 viene integrata; controllare che un finding page-level senza data/permalink non generi una nuova coppia GOLD.
2. Verificare che il fix #156 sia integrato prima di attribuire valore alla cronologia passata al recommender.
3. Verificare una scansione produttiva GAGARIN successiva al commit #631727 e all'eventuale integrazione #248; controllare che il paniere sia esattamente gli otto strumenti approvati.
4. Distinguere il loop Render a 5 minuti dalla GitHub Action a 15 minuti; nessun deploy Render dichiarato.
5. Verificare freschezza delle otto commodity e timestamp assoluto delle quotazioni.
6. Verificare la risoluzione Telegram 409 dopo l'eventuale aggiornamento della PR #175.
7. Verificare persistenza cross-run del journal solo dopo prova di storage durevole.
8. Verificare provider, quote ticker, market type, mese e scadenza prima di qualsiasi outcome; doppio tocco SL/TP nella stessa candela senza sequenza intrabar = ESITO NON VERIFICABILE.

## 9. Integrità e sicurezza

- Solo documentazione PRAVDA su branch dedicato.
- Ledger invariato: SHA `41a1339c2047c86ad9026ab131d9a8015d0cd710`.
- Nessuna modifica a `main` o al codice applicativo.
- Nessun merge, deploy, rerun, ordine reale, modifica a secret o Render.
- Nessun servizio a pagamento.
- Nessun accesso a Trading 212 dichiarato.
- API ACK Telegram non trattato come prova di visualizzazione sul dispositivo.
- PAPER ONLY.
