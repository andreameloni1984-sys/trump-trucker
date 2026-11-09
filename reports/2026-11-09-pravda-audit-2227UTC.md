# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
## Controllo #21 — 9 novembre 2026, 23:27 CET (22:27 UTC)

## Esito sintetico

Verifica read-only dei due repository, dei commit recenti su `main`, dei log integrali delle GitHub Actions disponibili, dei file di configurazione, dei journal pubblici, delle PR aperte e del ledger PRAVDA precedente.

**Nessun nuovo segnale operativo verificabile e nessuna nuova riga da aggiungere al ledger.** È stata invece verificata una correzione GAGARIN importante: la PR #248 è basata esattamente sull'attuale `main`, è 17 commit avanti / 0 indietro e i sette workflow associati risultano tutti SUCCESS; la suite principale riporta 570 test superati. La correzione non è ancora integrata. Su `main` l'universo resta a 13 strumenti.

È stata inoltre rettificata una precedente attribuzione di fonte nel caso SPUTNIK #295: il log non dimostra che il finding runtime provenisse da OGE.

## 1. Storico PRAVDA — integrità e duplicati

Ledger cumulativo letto dal branch precedente:

- File: `reports/pravda-signal-ledger-2026-11-09.csv`
- Blob SHA: `41a1339c2047c86ad9026ab131d9a8015d0cd710`
- Colonne: 33
- Record dati: **106**
- SPUTNIK: **50**
- GAGARIN: **56**
- Firme `audit_signature` uniche: **106**
- `source_record_id` unici: **106**
- Duplicati firma: **0**
- Duplicati source ID: **0**

Classificazione registrata:
- `NON_TRADE`: 77
- `ESITO_NON_VERIFICABILE`: 29

Il ledger non è stato modificato. Nessun nuovo record perché i log di produzione esaminati non hanno introdotto un nuovo segnale operativo distinto. I record `NOT_EXECUTED`, `WATCH`, `PENDING` e gli score non sono stati conteggiati come trade.

Statistiche di performance: **N/D**. Fill verificati 0; SL verificati 0; TP verificati 0. Non è disponibile un campione di operazioni eseguite con serie OHLC dello stesso ticker, mercato, provider e contratto.

## 2. SPUTNIK — main e Actions disponibili

Repository: `andreameloni1984-sys/trump-trucker`

Ultimo commit main restituito dalla ricerca commit:
- `6c3095f1534550b0b4e77170f1428db833253c05`
- messaggio: `chore: persist Sputnik state`
- timestamp: 2026-11-09 16:02:18 UTC.

Ultimo log produttivo completo recuperato in questa verifica:
- Collector run #295, run ID `42650624196`
- job `sputnik`, job ID `129275664568`
- avvio circa 16:02:09.982 UTC; completamento del run 16:02:23 UTC
- evento SCHEDULE; job SUCCESS.

Il connettore GitHub disponibile in questa sessione consente di recuperare i job/log di run noti e i run associati a commit, ma non espone un elenco repository-wide di tutte le Actions. Pertanto #295 è l'ultimo collector produttivo di cui è stato recuperato qui il log integrale; **non si afferma che sia necessariamente l'ultima esecuzione schedule assoluta**. La ricerca dei commit non ha mostrato un commit main successivo a quello delle 16:02, ma questo non esclude run schedule senza commit.

### 2.1 Log runtime #295

Sequenza effettiva nel job:
- SEC: HTTP 403; cooldown 21.600 secondi; filing 0.
- Estrazione transazioni: 0 record.
- White House RSS `https://www.whitehouse.gov/feed/`: HTTPError.
- Scansione intelligence pubblica: 6.665 ms, `findings=1`.
- Forwarding GAGARIN: 0 ms.
- Il job mostra `GAGARIN_CLOUD_API_URL` e `GAGARIN_CLOUD_API_KEY` vuote.
- La singola correlazione pubblica non è identificata nel log con item ID, permalink e timestamp di pubblicazione.

### 2.2 Rettifica di provenienza OGE

Nel precedente commento PRAVDA #6752498088 era stata attribuita al runtime una finding OGE page-level. Riesaminando il log completo, le righe ripetute `source OGE unavailable: OSError` compaiono prima dell'avvio di `python trump_tracker.py`, nel blocco precedente del job, insieme a output di test/mock. Non dimostrano un finding OGE del runtime.

Nel runtime, dopo `run started`, sono documentati SEC 403, White House RSS HTTPError, `public intelligence scan=6665ms | findings=1` e `GAGARIN forwarding=0ms`. L'identità della finding non è esposta. La classificazione corretta è quindi **FONTE/ITEM NON ATTRIBUIBILE DAL LOG**. È stata pubblicata una rettifica esplicita sulla PR #150: commento #6753198168.

Resta separata e valida la prova storica del run #292 relativa al record TRUTH_ARCHIVE page-level, documentata nel commento #6729715267. Non viene trasferita automaticamente al run #295.

### 2.3 Messaggi GOLD #752 / #753

Il runtime #295 ha prodotto:
- #752: analisi preliminare GOLD LONG.
- #753: card CFD GOLD LONG, stato `NOT_EXECUTED`.

Dati esposti nella card #753:
- generazione log: 2026-11-09 16:02:18.5846468 UTC;
- invio/API acceptance: 16:02:18.5856255 UTC;
- Entry 4129.2998;
- SL 4126.9106;
- TP1 4131.689;
- TP2 4134.0781;
- ATR 1.5928;
- score/priority 100;
- direzione LONG;
- `NO_DIRECTIONAL_NEWS`;
- fonte visualizzata: `PUBLIC_RSS | WHITE_HOUSE`;
- tesi: LONG preliminare, non ingresso confermato.

La card non espone provider, ticker contrattuale risolto, timestamp/età della quotazione, prezzo di riferimento o scadenza. Il testo fa riferimento a future continuo front-month e avverte che i livelli non sono utilizzabili finché la quotazione non sia fresca e l'ATR verificato. Il titolo CFD e il riferimento a future continuo non costituiscono prova di identità della stessa serie.

API round-trip riportato: #752 590 ms; #753 608 ms. È prova di accettazione API, non di visualizzazione sul dispositivo né di esecuzione.

Classificazione PRAVDA: **NON_TRADE / ESITO NON VALUTABILE**. Nessun confronto SL/TP è consentito senza ticker, mercato, provider, timestamp e scadenza esatti e senza candele successive della medesima serie.

Il precedente GOLD SHORT #751 resta `NOT_EXECUTED`, con D-L-A NEUTRAL e identiche lacune di provenienza; non è un trade.

### 2.4 PR SPUTNIK

- PR #150 — gate item-level contro raccomandazioni ripetute da snapshot page-level: OPEN, non integrata. Il caso #295 non consente di attribuire la finding a OGE; la correzione resta rilevante per richiedere item individuale, permalink e data di pubblicazione.
- PR #156 — ordinamento cronologia intelligence: OPEN, non integrata. Su main `trump_tracker.py` conserva ancora `values()[-30:]` nei comandi `/strumento` e `/segnale`; la correzione proposta ordina per `detected_at` e seleziona i record più recenti.
- I confronti main/head eseguiti per i branch esaminati: PR #150 e #156 risultano ciascuna 1 commit avanti / 0 indietro rispetto al main corrente al momento del confronto. Nessun merge effettuato.
- Nessun forwarding GAGARIN è dimostrato dal run #295: URL e key vuote e forwarding 0 ms.

## 3. GAGARIN — main, universo e frequenze

Repository: `andreameloni1984-sys/commodity-news-scanner`

Ultimo commit main restituito dalla ricerca:
- `631727912b3a2022379a4460f4b6f756eba6991f`
- messaggio: `Run Gagarin market-only scans every five minutes`
- timestamp: 2026-11-09 20:00:34 UTC.

Il commit precedente `b3bfb0dfacd0fcb1c90d7e2f2d477070abe48110` aveva attivato un universo a 13 strumenti.

### 3.1 Universo main verificato

Il file `commodities/universe.py` su main contiene 13 simboli abilitati:
- XAU/USD, XAG/USD, COPPER/USD, WTI/USD, BRENT/USD, WHEAT/USD, CORN/USD, SOYBEAN/USD;
- EUR/USD, DAX, SP500, NVDA, TSLA.

Il file `telegram/render_runner.py` su main imposta `position_monitor_loop` a 5 minuti e stampa `13 approved instruments`. Questo è codice/configurazione su GitHub, non prova che il servizio Render sia stato distribuito o sia attivo.

Il workflow GitHub Actions `.github/workflows/gagarin-monitor.yml` conserva invece:
- cron `*/15 * * * *`;
- `MONITOR_INTERVAL_MINUTES=15`;
- commento che il monitor provider-heavy resta a 15 minuti finché la capacità rate-limit non è verificata.

Quindi: Render runner configurato 5m; GitHub Actions monitor completo configurato 15m. Nessun accesso o modifica a Render effettuato.

### 3.2 PR #248 — correzione esatta a otto commodity

PR #248: `GAGARIN: restore the exact eight-commodity universe`.

Verifiche dirette:
- stato OPEN; non integrata;
- head `87367cafbcf37546d7736c13f228a0086703d598`;
- base main `631727912b3a2022379a4460f4b6f756eba6991f);
- confronto: **17 commit ahead / 0 behind**, merge-base identico al main corrente;
- file universe nel branch PR contiene esattamente: XAU/USD, XAG/USD, COPPER/USD, WTI/USD, BRENT/USD, WHEAT/USD, CORN/USD, SOYBEAN/USD;
- diff include universo, data routing, selettore scheduled, Telegram, Render runner e regressioni sui percorsi attivi.

I sette workflow associati al commit PR sono tutti `completed / success`:
- SOYUZ GAGARIN Tests — run 42691005230;
- GAGARIN Telegram menu tests — 42691004603;
- SOYUZ GAGARIN PAPER — 42691004605;
- Gagarin Execution Layer Tests — 42691004836;
- Gagarin NEWS alert tests — 42691004617;
- Commodity trade-plan tests — 42691004468;
- Gagarin Public Event Brain Tests — 42691004549.

Il log della suite principale riporta **570 passed in 4.22s**. Il job ha testato il merge ref temporaneo `f4d67c137c42e8d9b7c3241e6b6a6d952f74f60b` (PR head combinato con main). È una prova CI sulla correzione, non prova di produzione o deploy.

Un commento automatico sulla PR segnala un deployment failure di `telegram-github-bridge` su Cloudflare Workers. È un componente distinto dal monitor GAGARIN e non dimostra né un deploy Render né un fallimento del monitor; nessun deploy è stato avviato da PRAVDA.

PR #249 è esplicitamente marcata `SUPERSEDED — DO NOT MERGE` e dichiara che l'universo confermato è esattamente otto commodity; rimanda alla PR #248. Non va usata per autorizzare 13 strumenti.

È stato aggiunto il commento PRAVDA #6753183758 alla PR #248 con confronto, lista esatta, sette CI verdi e distinzione dal deployment Cloudflare.

## 4. GAGARIN — ultima scansione produttiva con log integrale disponibile

Run #173, run ID `42659137635`, job ID `129305621100`:
- avvio 2026-11-09 16:52:38 UTC;
- completamento 16:53:01 UTC;
- commit di esecuzione `50b25a80d6792be913c2bcf5a117ede68dd52b59`;
- job SUCCESS;
- esecuzione precedente nota #172 alle 06:34:18 UTC: gap osservato 10h18m20s.

Come per SPUTNIK, l'Actions connector non ha esposto una lista completa repository-wide di tutte le run schedule; #173 è l'ultima scansione produttiva il cui log integrale è stato recuperato qui, non prova che nessuna run successiva esista.

### 4.1 Quote e stato operativo del run #173

Quote al momento della scansione:
- Rame YAHOO STALE 604,7 s;
- Grano YAHOO STALE 604,0 s;
- WTI YAHOO STALE 601,8 s;
- Mais YAHOO STALE 606,1 s;
- Soia YAHOO STALE 603,5 s;
- Oro YAHOO STALE 602,6 s;
- Brent YAHOO STALE 605,0 s;
- Argento YAHOO STALE 626,6 s.

Tutte le otto commodity stale. EUR/USD e GBP/USD risultavano BIQUOTE LIVE rispettivamente 176,2 s e 176,9 s, ma erano strumenti ausiliari nel run #173, non segnali commodity autorizzati.

Blocchi sulle commodity: `LIVE_DATA_NOT_FRESH`, `NO_VALID_SETUP`, `TRIGGER_NOT_CONFIRMED`, livelli mancanti e `FINAL_CONFLUENCE_FAIL`.

Riepilogo runtime:
- Recorded entries: 0;
- Updated open outcomes: 0;
- New feedback signals: 0;
- New additional live forecasts: 0;
- signals=0, open=0, closed=0;
- win_rate=N/D, avg_R=N/D, total_R=0.0.

Il log mostra `DATABASE_URL` vuota e `PAPER_TRADING_ONLY=1`.

Telegram #3734: API `SEND CONFIRMED`, round-trip 556 ms; corpo non conservato. Strumento, direzione e livelli non attribuibili. È un WATCH pre-alert, non un trade.

## 5. GAGARIN — journal e feedback

File `commodities_prediction_log.json` su main:
- 981 record;
- 981 record unici per l'ID disponibile;
- PENDING 945;
- NEUTRALE 36.
Azioni: NON ENTRARE 77; ATTENDERE 576; SHORT — ASPETTARE CONFERMA 15; LONG — ASPETTARE CONFERMA 292; COMPRA ORA 21. Tutti i 21 `COMPRA ORA` risultano PENDING: non sono fill né trade eseguiti.

`paper_trade_log.csv` su main contiene una sola riga:
- 2026-10-08 16:23 UTC;
- Petrolio WTI, symbol WTI, LONG;
- entry 96.24, SL 89.37, TP1 103.11, TP2 106.55;
- `data_status=LEGACY_IMPORT`, `legacy_status=OPEN`;
- signal_id vuoto, provider/ticker/quote timestamp/market type vuoti;
- nota: nessun esito.
Non esiste prova di fill. La posizione `position.json` è un vecchio Heating Oil LONG aperto il 15 settembre 2026, anch'esso senza prova di esecuzione o outcome verificato. Non sono stati trattati come operazioni certificate.

`gagarin_feedback.csv` non è presente su main (404). `DATABASE_URL` è vuota nel log #173. La persistenza cross-run del journal non è dimostrata.

### 5.1 Outcome engine su main

Blob corrente `engine/feedback.py`: `41bec9bfab031c8dbf71121cd69d0e9b4c4f663f`.

Conferme dal file:
- FIELDS contiene `data_source` e `data_status`, ma non campi separati per provider, quote ticker, market type, contract month o expiry;
- signal ID basato su symbol, direction, timeframe, livelli e timestamp candela;
- matching successivo per `(symbol, timeframe)`, con fallback per symbol se esiste un solo candidato;
- la docstring e il codice attribuiscono precedenza a STOP quando una stessa candela tocca SL e TP.

Questo non soddisfa la regola PRAVDA. Doppio tocco SL/TP nella stessa OHLC senza sequenza intrabar ricostruibile deve essere **ESITO NON VERIFICABILE**, senza R realizzato. Inoltre occorre confrontare esattamente provider, ticker, mercato e contratto/scadenza prima di usare le candele successive.

PR #192 contiene la correzione proposta, ma è OPEN/non integrata e il suo branch non è allineato al main corrente. I commenti PRAVDA precedenti (#6750290763 e #6706619879) documentano il mancato confronto esplicito del provider nel matcher del branch PR. Nessuna statistica di performance è certificata.

## 6. Telegram GAGARIN

Polling run #20, ID `42660005021`, job `129308702941`:
- token validation SUCCESS;
- `getUpdates` FAILURE;
- Telegram API 409: `webhook is active; polling cannot run while webhook mode is enabled`.

PR #175 propone di riconoscere il conflitto e saltare il polling senza cancellare il webhook e senza ack degli update. È OPEN/non integrata. L'errore #20 è una prova di fallimento del polling; non prova che il webhook non consegni messaggi, né che la consegna sul dispositivo sia avvenuta.

## 7. Segnali esaminati e outcome

| Evento | Bot | Direzione/stato | Livelli | Identità serie | Outcome |
|---|---|---|---|---|---|
| #751 GOLD | SPUTNIK | SHORT, NOT_EXECUTED | entry 4125.6001; SL 4128.3859; TP1 4122.8143; TP2 4120.0285; ATR 1.8572 | ticker, provider, quote timestamp, mercato/expiry non verificati | NON_TRADE |
| #753 GOLD | SPUTNIK | LONG preliminare, NOT_EXECUTED | entry 4129.2998; SL 4126.9106; TP1 4131.689; TP2 4134.0781; ATR 1.5928 | ticker, provider, quote timestamp, mercato/expiry non verificati | NON_TRADE |
| #3734 WATCH | GAGARIN | direzione non attribuibile | nessuno conservato | corpo non conservato | NON_TRADE |
| WTI legacy | GAGARIN | LONG, LEGACY_IMPORT / OPEN | entry 96.24; SL 89.37; TP1 103.11; TP2 106.55 | signal ID/provider/contratto mancanti | nessun fill; ESITO NON VERIFICABILE |

Nessun caso consente la classificazione SL prima o TP prima. Nessuna serie successiva è stata usata perché l'identità strumento/contratto non è completa o il record non è un trade.

## 8. Segnalazioni PRAVDA effettuate in questo controllo

1. Commento di rettifica sulla PR SPUTNIK #150: #6753198168 — ritiro dell'attribuzione OGE al runtime #295; fonte/identità del finding non esposta.
2. Commento sulla PR GAGARIN #248: #6753183758 — confronto 17 ahead / 0 behind, paniere esatto a otto, sette workflow CI SUCCESS, 570 test superati, distinzione dal failure Cloudflare.

Non sono stati modificati codice, workflow, journal, segreti, Render o configurazioni operative. Nessun merge, rerun, deploy o ordine.

## 9. Fonti consultate

### SPUTNIK
- Actions #295: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42650624196
- main commit: https://github.com/andreameloni1984-sys/trump-trucker/commit/6c3095f1534550b0b4e77170f1428db833253c05
- PR #150: https://github.com/andreameloni1984-sys/trump-trucker/pull/150
- PR #156: https://github.com/andreameloni1984-sys/trump-trucker/pull/156
- commento rettifica #6753198168: https://github.com/andreameloni1984-sys/trump-trucker/pull/150#issuecomment-6753198168

### GAGARIN
- Actions #173: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42659137635
- Telegram Polling #20: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42660005021
- main commit: https://github.com/andreameloni1984-sys/commodity-news-scanner/commit/631727912b3a2022379a4460f4b6f756eba6991f
- PR #248: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/248
- PR #249 superseded: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/249
- PR #192: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192
- PR #175: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175
- workflow monitor: https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml
- universe main: https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities/universe.py
- feedback main: https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py
- prediction log: https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities_prediction_log.json
- paper trade log: https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/paper_trade_log.csv
- position legacy: https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/position.json

## 10. Lacune e prossimo controllo

Priorità:
1. Verificare la prima scansione GAGARIN produttiva dopo un'eventuale integrazione della PR #248: esattamente otto commodity, nessun FX/indice/equity nei percorsi operativi.
2. Verificare quote fresche con timestamp assoluto, provider, ticker quotato, mercato, contratto e scadenza.
3. Verificare che Render sia effettivamente aggiornato prima di attribuire al runtime il loop 5m; il codice su GitHub da solo non prova il deploy.
4. Dimostrare la persistenza del journal tra due run indipendenti.
5. Allineare e validare l'outcome engine su provider/ticker/market/contract/expiry e doppio tocco intrabar non verificabile.
6. Verificare una nuova run del polling Telegram; mantenere separati polling e webhook.
7. Per SPUTNIK, recuperare il singolo item con permalink e publication timestamp prima di attribuire un catalizzatore; verificare le PR #150 e #156 su una successiva run produttiva.
8. Ottenere un elenco completo e aggiornato delle Actions schedule per entrambi i repository: l'interfaccia GitHub disponibile in questo audit non ha esposto la lista repository-wide delle run.

## Verdetto

**106 record, 106 firme uniche, 106 source ID unici, zero duplicati. Zero fill verificati, zero SL/TP verificati, performance N/D.**

PR #248 è la correzione GAGARIN più matura verificata in questo controllo (7/7 workflow, 570 test), ma main resta a 13 strumenti finché non sarà integrata. SPUTNIK #295 ha generato GOLD LONG preliminare senza catalizzatore direzionale verificato e senza provenienza contrattuale sufficiente; il finding non è attribuibile a OGE dal log.

PAPER ONLY. Nessun codice applicativo modificato, nessuna strategia/filtro/punteggio/soglia/rischio modificati, nessun merge/deploy/ordine reale, nessuna modifica a secret o Render, nessun accesso a Trading212 dichiarato.
