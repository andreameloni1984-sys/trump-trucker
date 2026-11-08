# PRAVDA — Audit incrementale SPUTNIK / GAGARIN

**Cut-off:** 8 novembre 2026, 10:48:29 UTC (11:48:29 Europe/Rome)  
**Perimetro:** ultime GitHub Actions su main, log completi dei job, artefatti e journal pubblici, ledger PRAVDA, workflow, codice feedback e PR aperte. Verifica indipendente; PAPER ONLY.

## 1. Esito sintetico

- **Nessun nuovo segnale direzionale operativo** nelle ultime run di produzione esaminate.
- **SPUTNIK:** collector #288, 09:31:31–09:31:41 UTC, SUCCESS; 30 test di regressione superati. Il log completo è ora disponibile e conferma tre messaggi Telegram accettati dall'API: #731 (digest notizie), #732 (analisi GOLD) e #733 (analisi GOLD etichettata CFD ma descritta nel corpo come future front-month continuo). Nessuno contiene un trade valido.
- **GAGARIN:** monitor #168, 09:29:58–09:30:17 UTC, SUCCESS. Tutti i dieci strumenti risultano MARKET_CLOSED e con quotazioni stale; zero entrate, zero nuovi feedback e zero esiti aggiornati. Telegram API ha accettato un WATCH pre-alert #3719, ma il corpo del messaggio non è conservato.
- **Nessun artifact** allegato alle due run. Il log dei job, recuperato direttamente, permette però di verificare i contenuti essenziali sopra descritti.
- Ledger aggiornato: **85 record**, 85 firme uniche e 85 source ID unici, zero duplicati. Conteggio: **56 NON_TRADE**, **29 ESITO_NON_VERIFICABILE**; fill verificati 0, SL verificati 0, TP verificati 0. Win rate, average R e total R: **N/D**.
- Nessun backtest, nessun merge/deploy, nessun ordine reale, nessuna modifica a strategia, filtri, punteggi o rischio.

## 2. SPUTNIK — run #288 e messaggi

Run: [Actions #42467543117](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42467543117)  
Job: `sputnik`, ID `128690443372`. Nessun artifact.

### Fonti e item pubblico

- SEC: HTTP 403; cooldown applicato di 21.600 secondi; zero filing recuperati.
- White House RSS: HTTPError.
- Public scan: 707 ms, due correlazioni registrate nello stato; il digest operativo mostra **un item pubblico datato**.
- Item: “Quote post from November 8, 2026”, PUBLIC_RSS, dominio MEDIA, event_type OTHER, historical reaction NO_ANALOGUE.
- Pubblicazione: **03:53:01 UTC**; rilevazione: **09:31:37.313495 UTC**; ritardo: **5h38m36s**.
- Fonte: [Trump’s Truth archive item](https://www.trumpstruth.org/statuses/43524); il record è già presente nel ledger con event ID `f3dd016d2288efc8d1a89d79`.

Non è un catalizzatore direzionale: nessuna commodity mappata, ticker, mercato, scadenza, quotazione, provider, prezzo, direzione o livello. Resta **NON_TRADE**.

### Messaggi Telegram verificati nei log

| ID | Generazione (UTC) | ACK API (UTC) | Contenuto verificato | Classificazione |
|---|---|---|---|---|
| 731 | 09:31:37.313495 (rilevazione item) | 09:31:38.5640305 | Digest con l'item PUBLIC_RSS sopra | INTELLIGENCE_ONLY / NON_TRADE |
| 732 | 09:31:38.5641237 | 09:31:38.5655282 | GOLD; bias NEUTRAL; direzione tecnica 5m UNAVAILABLE; NO_DIRECTIONAL_NEWS; nessun livello | WATCH / NON_TRADE |
| 733 | 09:31:38.5655719 | 09:31:38.5664615 | GOLD; NO_DIRECTION; NOT_EXECUTED; score 100; quotazione fresca assente; nessun livello | NON_TRADE |

I log riportano round-trip API rispettivamente 366 ms, 325 ms e 304 ms. I timestamp di ACK dimostrano l'accettazione API, non la consegna al dispositivo. Non uso la differenza tra timestamp delle righe di log come misura indipendente del tempo di rete.

**Anomalia di classificazione sul messaggio #733:** il titolo è “ANALISI CFD”, ma il corpo dichiara `FUTURES_CONTINUOUS_FRONT_MONTH`, senza scadenza esatta verificata. Ticker, provider e timestamp della quotazione non sono esposti; NARWHAL è NOT_CONFIGURED. Non lo classifico come prezzo CFD né come contratto futures identificato. Il punteggio 100 non prova validità operativa.

Il messaggio #732 e il #733 sono due rappresentazioni della stessa analisi GOLD, non due setup indipendenti. Entrambi sono registrati nel ledger come NON_TRADE.

### Cadenza

- Workflow collector: cron `2-59/5`. Run #287 alle 02:41:59 UTC e #288 alle 09:31:31 UTC: gap **6h49m32s**.
- Al cut-off 10:48:29 UTC, dalla #288 erano trascorsi **1h16m58s** senza una nuova run.
- Telegram polling: cron `*/5`. Run #48 alle 02:20:16 e #49 alle 09:16:25: gap **6h56m09s**; al cut-off gap **1h32m04s**.
- I job sono SUCCESS, ma la cadenza effettiva osservata non rispetta quella dichiarata. Non è dimostrata la causa del ritardo.

La run #288 ha persistito lo stato con commit [35f601f](https://github.com/andreameloni1984-sys/trump-trucker/commit/35f601f9ba1d5748473119235a0eda180c86a554), continuando a scrivere `sputnik_state.json` su main.

## 3. GAGARIN — run #168, quotazioni e feedback

Run: [Actions #42467422750](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42467422750)  
Job: `Run Gagarin directly on GitHub`, ID `128690080067`. Nessun artifact.

### Dati di mercato riportati dal log

Il run dichiara UTC di analisi `2026-11-08T09:30:10.225114Z`. Tutti i dieci strumenti sono marcati MARKET_CLOSED. Le età delle quotazioni sono circa **35h30m–38h10m**. Il timestamp assoluto del dato, il ticker provider risolto, il prezzo e la scadenza contrattuale non sono stampati: non li ricostruisco per inferenza.

| Strumento riportato | Provider | Quote age (secondi) | Stato |
|---|---|---:|---|
| Soia | YAHOO | 137413.3 | MARKET_CLOSED / STALE |
| Brent | YAHOO | 127827.9 | MARKET_CLOSED / STALE |
| Argento | YAHOO | 127812.5 | MARKET_CLOSED / STALE |
| WTI | YAHOO | 127813.8 | MARKET_CLOSED / STALE |
| Grano | YAHOO | 137413.1 | MARKET_CLOSED / STALE |
| EUR/USD | BIQUOTE | 128113.0 | MARKET_CLOSED / STALE |
| Mais | YAHOO | 137416.2 | MARKET_CLOSED / STALE |
| Oro | YAHOO | 127811.4 | MARKET_CLOSED / STALE |
| Rame | YAHOO | 127823.7 | MARKET_CLOSED / STALE |
| GBP/USD | BIQUOTE | 128113.6 | MARKET_CLOSED / STALE |

La classifica riporta solo PAPER_WATCH o contesto FX non operativo; nessun ticker con identità contrattuale completa, direzione autorizzata, entry, SL, TP o ATR. Il run riporta:
- Recorded entries: 0
- Updated open outcomes: 0
- New feedback signals: 0
- New additional live forecasts: 0
- `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`

Telegram: **message_id 3719**, ACK API alle **09:30:14.1243054 UTC**, round-trip 527 ms, WATCH pre-alert accepted. Il corpo del messaggio non è presente nel log: strumento, ticker, direzione e livelli sono NON ATTRIBUTABLE. L'ACK non prova consegna al dispositivo.

### Universo e persistenza

Il log descrive 8 commodity operative più EUR/USD e GBP/USD ausiliari. Nell'elenco compare Argento, mentre non compaiono Platino e Palladio: il paniere osservato non coincide con quello richiesto. Nessun segnale è stato generato in questa run, quindi la discrepanza non produce un trade da valutare.

- `DATABASE_URL` è vuota nell'ambiente del job; non è dimostrato l'uso di PostgreSQL.
- `journal.csv` contiene soltanto letture del 17 ottobre con “nessun segnale”.
- `paper_trade_log.csv` contiene un record legacy WTI del 8 ottobre: LONG, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55; mancano signal ID, ticker provider, provider, quote timestamp, mercato e scadenza.
- `data/paper_open.json` conserva P0001 come OPEN, con gli stessi livelli. Non è prova di fill o esecuzione e non può essere valutato come trade.
- `commodities_monitor_state.json` è datato 17 settembre; `commodities_daily_report_state.json` è datato 10 settembre e riporta evaluated=0, total_readings=25, pending=24.
- `commodities_prediction_log.json` è un archivio storico di previsioni PENDING, non prova di segnali correnti né di esecuzioni.

## 4. Integrità del feedback e PR già esistenti

Sul main GAGARIN, `engine/feedback.py`:
1. costruisce il signal ID da symbol, direction, timeframe, livelli e timestamp candela, senza provider, ticker esatto, market type, contratto o expiry;
2. associa le candele successive per symbol/timeframe, senza vincolo sull'identità completa del contratto;
3. se una stessa candela tocca SL e TP, registra STOP prima dei target, benché l'ordine intrabar non sia noto.

La [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) propone già fingerprint e matching più rigorosi e la classificazione dell'ambiguità intrabar come non verificabile. È OPEN, non merged; il branch è 6 commit ahead e 4 behind main. Le sei CI sul suo head risultano SUCCESS, ma la correzione non è in produzione.

Altre PR GAGARIN ancora aperte:
- [#200](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/200) e [#202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): persistenza feedback/journal; entrambe draft.
- [#212](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/212): universo commodity; draft.
- [#181](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/181): provenance quote.
- [#184](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/184): distinzione ACK Telegram/consegna.

PR SPUTNIK ancora OPEN/non merged:
- [#147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): rimozione handoff GAGARIN; due CI sul head SUCCESS.
- [#148](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): soppressione raccomandazioni ripetute; due CI sul head SUCCESS.
- [#144](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): persistenza stato fuori da main.
- [#145](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): provenance quote Yahoo.
- [#142](https://github.com/andreameloni1984-sys/trump-trucker/pull/142): calendario macro BLS/USDA; OPEN e attualmente non mergeable.

## 5. Storico, statistiche e regole di conteggio

Ledger: [pravda-signal-ledger-2026-11-08.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-08.csv)  
Commit ledger: `5e0e89c6adf35a9a647c59b51a4ae0effffef729`.

| Metrica | Conteggio |
|---|---:|
| Record | 85 |
| SPUTNIK | 36 |
| GAGARIN | 49 |
| Firme uniche | 85 |
| Source ID unici | 85 |
| Duplicati | 0 |
| NON_TRADE | 56 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |
| Campione con outcome verificabile | 0 |

I tre nuovi record sono i messaggi SPUTNIK #732/#733 e il WATCH pre-alert GAGARIN #3719. Il record intelligence SPUTNIK già esistente è stato aggiornato con l'ACK del digest #731, senza creare una seconda riga per lo stesso item. #732 e #733 sono marcati come output complementari della stessa analisi. #3719 resta non attribuibile. Tutti sono NON_TRADE.

Le 29 righe ESITO_NON_VERIFICABILE sono record storici con dati insufficienti, non trade. Nessuna candela successiva è stata associata a un'identità strumento/contratto completa e verificata; non è quindi corretto dichiarare SL prima, TP prima, win rate o rendimento.

## 6. Fonti e limiti

- GitHub Actions: SPUTNIK #42467543117 e Telegram polling #42466478249; GAGARIN #42467422750.
- Log job completi: SPUTNIK job 128690443372; GAGARIN job 128690080067.
- File main consultati: `sputnik_state.json`, `journal.csv`, `paper_trade_log.csv`, `data/paper_open.json`, `commodities_prediction_log.json`, `commodities_monitor_state.json`, `commodities_daily_report_state.json`, `engine/feedback.py`, workflow YAML.
- PR e CI: SPUTNIK #142/#144/#145/#147/#148; GAGARIN #181/#184/#192/#200/#202/#212.
- Nessun accesso a Trading212 o broker, nessun servizio a pagamento, nessuna lettura o modifica di secret, Render o database privati. Telegram è verificato soltanto come ACK API, non come consegna al dispositivo.
- Nessun prezzo/candela futura con provider e contratto esatti è disponibile per valutare i record recenti.

## 7. Prossimo controllo

1. Verificare se riprendono le run pianificate e misurare nuovamente gli intervalli reali, senza attribuire una causa non provata.
2. Per ogni nuovo output, conservare body, timestamp, message ID, ticker provider, market type, expiry, provider e quote timestamp prima di tentare un outcome.
3. Rivalutare PR #192 soltanto dopo riallineamento con main; controllare che la correzione sia effettivamente integrata prima di considerarla attiva.
4. Non calcolare statistiche di performance finché non esiste un campione con identità contrattuale completa e percorso prezzi successivo verificabile.

**Modifiche eseguite da PRAVDA:** solo aggiornamento del ledger e creazione di questo rapporto documentale su SPUTNIK. Nessun codice, strategia, filtro, punteggio, rischio, PR, secret o deployment modificato. PAPER ONLY.
