# PRAVDA — Audit incrementale SPUTNIK / GAGARIN

**Cut-off:** 8 novembre 2026, 12:42:17 UTC (13:42:17 Europe/Rome)  
**Perimetro:** GitHub Actions di produzione, log integrali dei job, stato SPUTNIK, ledger PRAVDA, journal/file PAPER GAGARIN, codice di feedback su `main`, PR aperte e relativi check. Verifica documentale indipendente. PAPER ONLY.

## 1. Esito sintetico

- Nessun nuovo segnale operativo verificato in questo controllo.
- Il ledger precedente aveva 85 record, 85 firme uniche e 85 source ID unici. Ho aggiunto un solo record per la nuova notifica di riepilogo SPUTNIK Telegram #734, classificata `NON_TRADE` e non come segnale: totale **86 record, 86 firme uniche, 86 source ID unici, zero duplicati**.
- Distribuzione aggiornata: **SPUTNIK 37 record; GAGARIN 49**. Esiti registrati: **57 `NON_TRADE`, 29 `ESITO_NON_VERIFICABILE`**. I 29 record non verificabili non sono 29 trade.
- Fill verificati: **0**; SL verificati: **0**; TP verificati: **0**. Campione per win rate/R: **0**. Win rate, average R e total R restano N/D.
- Nessun artifact allegato alle ultime run di produzione esaminate. I log dei job sono la prova primaria.
- Nessun prezzo/candela successivo è stato usato per attribuire un esito: i record recenti non hanno livelli operativi e/o identità completa ticker/mercato/contratto/provider.

## 2. SPUTNIK — collector, messaggi e riepilogo

### Ultimo collector di produzione

- Run [#42467543117](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42467543117), workflow `SPUTNIK`, run #288, `main`, SHA `1ec9e96892edab84606294b0d80965faf3c8317` al momento della run; job `sputnik` ID `128690443372`, SUCCESS, nessun artifact.
- Avvio collector: **09:31:31 UTC**. Al cut-off delle 12:42:17 UTC non risultava un collector più recente: gap **3h10m46s**, nonostante il cron su main `2-59/5 * * * *`.
- Ultimo polling Telegram: run [#42466478249](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42466478249), avvio **09:16:25 UTC**, SUCCESS. Al cut-off gap **3h25m52s**, nonostante cron `*/5 * * * *`.
- Le run di test PR delle 12:16 UTC non sono scansioni di produzione e non colmano i gap.

### Evidenze del collector #288

- SEC: HTTP 403, cooldown `21600s`; nessun filing recuperato nella run.
- White House RSS configurato su `https://www.whitehouse.gov/feed/`: `HTTPError`.
- Item Truth Archive event ID `f3dd016d2288efc8d1a89d79`: pubblicato alle **03:53:01 UTC**, rilevato alle **09:31:37.313495 UTC**, ritardo **5h38m36s**. Fonte primaria registrata: `https://www.trumpstruth.org/statuses/43524`; feed `https://www.trumpstruth.org/feed`. Classificazione `MEDIA / OTHER / NO_ANALOGUE`; nessuna commodity, direzione, quotazione o livello. È intelligence, non segnale.
- Telegram #731: digest dell'item pubblico, API ACK alle **09:31:38.5640305 UTC**, round-trip 366 ms.
- Telegram #732: GOLD, bias NEUTRAL / `NO_DIRECTION`; tecnica 5m non disponibile; nessuna notizia direzionale; nessun ticker/provider/prezzo/mercato/scadenza/entry/SL/TP/ATR verificabili. API ACK alle **09:31:38.5655282 UTC**, round-trip 325 ms.
- Telegram #733: GOLD, `NO_DIRECTION`, `NOT_EXECUTED`, score 100. Il titolo lo presenta come CFD, ma il corpo dichiara `FUTURES_CONTINUOUS_FRONT_MONTH`; scadenza esatta e indipendenza upstream non verificate. NARWHAL reference non configurato; quotazione fresca assente; nessun entry/SL/TP/ATR. Lo score non prova validità operativa. API ACK alle **09:31:38.5664615 UTC**, round-trip 304 ms.
- #732 e #733 sono due rappresentazioni della stessa analisi GOLD, non due setup. Nessuno dei tre messaggi #731–#733 è un trade. Gli ACK dimostrano accettazione API, non consegna sul dispositivo.

### Nuovo riepilogo #734

- Run [#42480644139](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42480644139), workflow `SPUTNIK Daily Summary`, run #11, `main` SHA `c963bef6ce1b611f12a449ba7377127f4efbfce7`, avvio **12:31:18 UTC**, SUCCESS; job `Send daily opportunity summary`, ID `128731607505`, nessun artifact.
- Il workflow ha cron `0 6 * * *`; avvio osservato 12:31:18 UTC, cioè **6h31m18s** dopo l'orario cron delle 06:00 UTC.
- Il file `sputnik_state.json` letto dal workflow riporta `updated_at=2026-11-08T09:31:37.340241Z`, `transactions` vuoto e `events` vuoto. `telegram/sputnik_watch.py` costruisce WATCH leggendo `transactions`; con zero transazioni la funzione restituisce stringa vuota e il workflow sceglie il ramo 'Nessun candidato in watch oggi'.
- Il job non stampa il corpo effettivo. La classificazione senza candidati è quindi ricostruita dal codice e dallo stato caricato, non da una copia del messaggio. Il log conferma API `message_id=734` alle **12:31:25.2431545 UTC**. Non è un segnale né una scansione di mercato; l'ACK non prova la visualizzazione sul dispositivo.
- Il record #734 è stato aggiunto al ledger come `daily_watch_summary_notification_unresolved / NON_TRADE`, con `generated_at_utc=NOT_EXPOSED` e timestamp di ACK separato. Nessun record di segnale è stato aggiunto.

### PR SPUTNIK rilevanti

- [PR #131 — nuovo endpoint White House RSS](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): OPEN, non merged, base `main` SHA `c963bef6`, head `58fa0dc3`, 1 commit ahead / 0 behind, mergeable. Check sul nuovo head: `tests` SUCCESS e `item-intelligence` SUCCESS (run #42479427517 e #42479427775). La modifica sostituisce `/feed/` con `/news/feed/`; il collector produttivo #288 ha ancora eseguito il vecchio main e registrato HTTPError. Il nuovo endpoint non è ancora stato verificato in una scansione di produzione.
- [PR #147 — separazione SPUTNIK/GAGARIN](https://github.com/andreameloni1984-sys/trump-trucker/pull/147) e [PR #148 — stop raccomandazioni ripetute](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): entrambe OPEN e non integrate su main al cut-off.

## 3. GAGARIN — monitor, quote, journal e feedback

### Ultimo monitor di produzione

- Run [#42467422750](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42467422750), workflow `Gagarin Paper Monitor (GitHub Actions)`, run #168, branch `main`, SHA `69bb6d070dc180f9fc671c4f87b3c5fd19be1009`; job ID `128690080067`, SUCCESS, nessun artifact.
- Avvio: **09:29:58 UTC**. Al cut-off non risultava una run di produzione successiva: gap **3h12m19s**, nonostante il cron `*/15 * * * *`.
- La run precedente era #42438806862, avviata alle 02:30:08 UTC: gap fra le due run **6h59m50s**. Non è dimostrata la causa dei gap.

### Quotazioni e blocchi

- Il log elenca dieci strumenti: Soia, Brent, Argento, WTI, Grano, EUR/USD, Mais, Oro, Rame e GBP/USD.
- Tutti risultano `MARKET_CLOSED`; età dichiarata delle quote fra **127.811,4 e 137.416,2 secondi** (circa 35h30m–38h10m al momento della scansione). Provider: YAHOO per le commodity e BIQUOTE per EUR/USD e GBP/USD.
- Il job non espone per questi record ticker provider risolto, timestamp assoluto della quota, prezzo di riferimento, market type o scadenza. L'età in secondi non basta a identificare un contratto.
- I candidati sono bloccati da `LIVE_DATA_NOT_FRESH` e da setup/trigger/livelli mancanti. La run registra `Recorded entries: 0`, `Updated open outcomes: 0`, `New feedback signals: 0` e `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`.
- Telegram #3719: API SEND CONFIRMED alle **09:30:14.1243054 UTC**, round-trip 527 ms. Il corpo non è conservato nel log: strumento, ticker, direzione e livelli non attribuibili. Nessun trade.
- I parametri stampati dal job sono probabilità 40, qualità 30, confidenza 35, RR 2.5, stop massimo 2.5 ATR e SL minimo 0.80 ATR. PRAVDA non li ha modificati.

### Journal e posizioni legacy

- `journal.csv`: 11 righe di analisi del **17 ottobre 2026**, tutte con esito 'nessun segnale'; nessun trade recente documentato.
- `paper_trade_log.csv`: un record WTI LONG del **8 ottobre 2026**, marcato `LEGACY_IMPORT`, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55. Mancano provider, ticker provider, timestamp/prezzo della quotazione, market type, scadenza e risultato. Non è prova di fill.
- `data/paper_open.json`: ticket `P0001` WTI LONG, status OPEN, senza provenienza della quotazione/contratto e senza P&L. `position.json`: vecchia posizione Heating Oil LONG aperta il **15 settembre 2026**, entry 4.8844, SL 4.5418, TP1 5.4473. La run corrente dichiara zero posizioni aperte e zero segnali: questi artefatti legacy non sono riconciliati e restano esclusi dalle statistiche.
- Nel tree di main non è presente un `gagarin_feedback.csv` versionato. Il job mostra `DATABASE_URL` vuota a ogni fase; il codice `state_store.py` restituisce nessuna connessione se la variabile è vuota. La persistenza PostgreSQL condivisa non è dimostrata.

### Difetto dimostrato nell'outcome su main

- `engine/feedback.py` su main costruisce i record con `symbol` e `timeframe`, ma non conserva nel campo record provider, ticker di esecuzione, market type o scadenza del contratto.
- `update_open_outcomes()` abbina le candele per `(symbol, timeframe)` e, come fallback, per il solo symbol quando esiste un solo stato. Non verifica provider, ticker effettivo, mercato o scadenza: non soddisfa il requisito di identità contrattuale esatta.
- La funzione filtra correttamente le candele con timestamp successivo all'entry bar, ma se una candela tocca SL e TP nello stesso OHLC, controlla prima lo stop e registra `STOP` (`engine/feedback.py`, righe 228–230 e 282–295). L'OHLC non rivela la sequenza intrabar: secondo il protocollo PRAVDA quel caso deve restare `ESITO NON VERIFICABILE`, non SL verificato.

### PR GAGARIN già esistenti

- [PR #97 — ambiguità SL/TP sulla stessa candela](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/97): OPEN/DRAFT, non integrata e `mergeable=false`. Il commento PRAVDA #6696418074 ha già registrato il difetto su main.
- [PR #192 — identità contratto e outcome](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, non merged. Compare aggiornato con main: **6 commit ahead / 4 behind**. Sul branch `_market_contract_match` confronta quote symbol, market type e per i futures month/expiry, ma non confronta il provider del segnale con quello delle candele; il rilievo è già registrato nel commento PRAVDA #6706619879. Check sul branch: 8 check di test SUCCESS, ma il check `Workers Builds: telegram-github-bridge` è FAILURE; non descrivere quindi la PR come interamente verde.
- [PR #237](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/237) è OPEN/DRAFT e impilata sulla branch della [PR #236](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/236), non direttamente su main. I test sul suo head hanno quattro check di test SUCCESS e un check Workers Build FAILURE. Il contenuto riguarda l'identità nel catalogo Trading 212: non prova disponibilità di un feed CFD, una quotazione o accesso a Trading 212. Il chiarimento sulla distinzione slug/catalogo e simbolo di feed è già nel commento PRAVDA #6719046626.
- [PR #219 — rimozione EUR/USD e GBP/USD](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219), [PR #212 — universo commodity ristretto](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/212), [PR #225 — offset cron monitor](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225), [PR #200](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/200) e [PR #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202) restano OPEN e non integrate.
- Il main osservato continua a riportare Argento ed EUR/USD/GBP/USD e non mostra Platino/Palladio: il set effettivo non coincide con il paniere commodity selezionato. Le PR aperte non modificano il comportamento di produzione.

## 4. Ledger e statistiche

- Ledger: [pravda-signal-ledger-2026-11-08.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-08.csv).
- Prima dell'aggiornamento: 85 record, 85 firme uniche, 85 source ID unici, zero duplicati.
- Aggiunta una sola riga per il messaggio Telegram #734, che è una notifica di riepilogo senza candidato, `NON_TRADE`. Il corpo non è conservato; generazione marcata `NOT_EXPOSED`, ACK API separato. Nessun duplicato.
- Totale dopo aggiornamento: **86 record / 86 firme uniche / 86 source ID unici / 0 duplicati**; SPUTNIK 37, GAGARIN 49; `NON_TRADE` 57; `ESITO_NON_VERIFICABILE` 29.
- Fill, SL e TP verificati: tutti **0**. Win rate, average R e total R: **N/D**. `NOT_EXECUTED`, WATCH, score e notifiche non vengono contati come trade.

## 5. Fonti consultate

- SPUTNIK Actions: [collector #42467543117](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42467543117), [Telegram polling #42466478249](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42466478249), [daily summary #42480644139](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42480644139).
- GAGARIN Actions: [monitor #42467422750](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42467422750), [monitor precedente #42438806862](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42438806862).
- File SPUTNIK: `sputnik_state.json`, `telegram/sputnik_watch.py`, `.github/workflows/trump_tracker.yml`, `.github/workflows/daily-summary.yml`, ledger PRAVDA.
- File GAGARIN: `journal.csv`, `paper_trade_log.csv`, `position.json`, `data/paper_open.json`, `engine/feedback.py`, `state_store.py`, `.github/workflows/gagarin-monitor.yml`.
- PR e check: SPUTNIK #131/#147/#148; GAGARIN #97/#192/#200/#202/#212/#219/#225/#236/#237.

## 6. Lacune e prossimo controllo

1. Verificare nuove run di produzione, separandole dai test PR e dai daily summary; documentare gli orari reali rispetto ai cron.
2. Per ogni nuovo segnale richiedere ID/firma, timestamp generazione e richiesta/ACK, ticker esatto, provider, quote timestamp/prezzo, market type, scadenza o esplicita identità no-expiry, direzione, entry, SL, TP e ATR.
3. Riconciliare gli artefatti legacy WTI/Heating Oil con un registro PAPER durevole prima di considerarli posizioni; non attribuire loro esiti senza provenienza contrattuale.
4. Non valutare gli outcome finché il dato successivo non è dello stesso ticker, provider, mercato e contratto. Se SL e TP sono toccati nella stessa candela, `ESITO NON VERIFICABILE`.
5. Verificare la nuova White House RSS solo dopo un run di produzione su main; il test PR non è una prova di fetch live.

**Sicurezza e perimetro:** nessun codice o strategia modificati; solo ledger/documentazione PRAVDA aggiornati nel repository SPUTNIK. Nessun merge/deploy, ordine reale, modifica a secret o Render, servizio a pagamento o accesso Trading 212 dichiarato. Telegram: solo API ACK dove presente, non prova di consegna al dispositivo. PAPER ONLY.