# PRAVDA — Audit indipendente #14
## SPUTNIK / GAGARIN
**Cut-off: 9 novembre 2026, 15:44:36 UTC (16:44:36 CET)**

## Sintesi esecutiva

- **SPUTNIK:** nuova esecuzione collector #294, ma avviata da evento `push`, non dal cron. Ha prodotto un nuovo candidato GOLD SHORT (#750/#751). La card con livelli è `NOT_EXECUTED`, non è un trade e non ha identità contrattuale/provenienza quotazione sufficienti.
- **GAGARIN:** nessuna nuova esecuzione programmata del monitor dopo #172 delle 06:34:18 UTC. Il push su main delle 15:32 ha eseguito soltanto un job di test, non il monitor.
- **PRAVDA:** 104 record, 104 firme uniche, 104 source ID unici, zero duplicati. Il nuovo candidato #751 è stato registrato una sola volta; #750 è trattato come messaggio di analisi collegato, non come secondo trade.
- **Esiti:** zero fill verificati, zero SL verificati, zero TP verificati. Win rate e R-multiples restano N/D.

Nessuna modifica al codice applicativo, strategia, filtri, punteggi o rischio. Nessun merge/deploy, nessun ordine reale, nessun intervento su segreti o Render. PAPER ONLY.

---

## 1. Registro storico

Ledger cumulativo aggiornato:
- Record: **104**
- SPUTNIK: **49**
- GAGARIN: **55**
- Firme uniche: **104**
- Source ID unici: **104**
- Duplicati firma: **0**
- Duplicati source ID: **0**
- `NON_TRADE`: **75**
- `ESITO_NON_VERIFICABILE`: **29**
- Fill verificati: **0**
- Stop verificati: **0**
- Target verificati: **0**

Le 75 righe NON_TRADE e le 29 righe ESITO_NON_VERIFICABILE sono record di audit, non 104 operazioni. Le 29 righe non verificabili non sono 29 trade persi.

### Nuova riga inserita

- Firma: `PRAVDA-SPUTNIK-CFD-RUN42645788987-20261109T153313Z-GOLD-SHORT-4125.6001-4128.3859-4122.8143-4120.0285`
- Source ID: `run:42645788987/telegram_message:751`
- Generazione/log card: `2026-11-09T15:33:13.053057Z`
- ACK API: `2026-11-09T15:33:13.0545671Z`
- Messaggio Telegram: #751; messaggio preliminare collegato #750
- Stato: `EARLY_SETUP / NOT_EXECUTED`
- Esito: `NON_TRADE`

Il messaggio #750 è conservato nella nota della stessa riga come analisi preliminare collegata. Non viene contato due volte.

---

## 2. SPUTNIK — Actions e continuità

### Esecuzioni verificate

| Run | Evento | Avvio UTC | Risultato | Valutazione |
|---|---|---|---|---|
| [#293](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770) | schedule | 06:01:41 | SUCCESS | Ultimo collector schedulato |
| [#294](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42645788987) | push | 15:33:04 | SUCCESS | Collector eseguito su push, non su cron |
| [Polling #53](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570062235) | schedule | 05:55:47 | SUCCESS | Precedente polling |
| [Polling #54](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42647513138) | schedule | 15:43:25 | SUCCESS | Pending updates: 0 |
| [Daily summary #12](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42638308297) | schedule | 14:48:35 | SUCCESS | ACK Telegram #749 |

Il workflow collector su main dichiara cron `2-59/5 * * * *`. La run #294 è stata generata da `push`; non dimostra che il cron collector sia ripreso. Al cut-off, l'ultima run collector schedulata (#293) risaliva a **9h42m55s** prima.

Il polling #54 è una nuova esecuzione schedulata, ma arriva dopo un gap di **9h47m38s** rispetto al polling #53. Il log #54 riporta `Pending updates: 0`: una singola ripresa non dimostra una cadenza regolare.

Il daily summary #12 è partito alle 14:48:35 UTC mentre il workflow dichiara cron alle 06:00 UTC: ritardo di circa **8h48m35s**. L'API ha confermato il messaggio #749 alle 14:48:40.945 UTC; il corpo non è stampato nel log, quindi non viene classificato come segnale.

### Run #294 — nuovo candidato GOLD SHORT

La run #294 è partita alle 15:33:04 UTC e ha terminato il job collector con successo. Il log mostra:

**Messaggio #750 — analisi preliminare**
- Strumento: GOLD
- Bias: SHORT
- Direzione tecnica: SHORT (5m)
- Momentum: -0,005% negli ultimi 15 minuti
- Allineamento notizie: `NO_DIRECTIONAL_NEWS`
- Stato: `EARLY_BIAS`
- Nessun catalizzatore USA direzionale verificato

**Messaggio #751 — card CFD collegata**
| Campo | Valore |
|---|---:|
| Entry | 4125.6001 |
| SL | 4128.3859 |
| TP1 | 4122.8143 |
| TP2 | 4120.0285 |
| ATR | 1.8572 |
| Score | 100 |
| Stato | EARLY_SETUP / NOT_EXECUTED |

La card #751 presenta nuovamente una contraddizione:
- #750 dichiara direzione tecnica SHORT (5m);
- #751 riporta `TECNICA: N/D (NOT_ASSESSED)`;
- #751 riporta `D-L-A: NEUTRAL / NO_DIRECTION`.

La card dichiara inoltre:
- titolo CFD ma riferimento a future continuo front-month;
- scadenza esatta non verificata;
- indipendenza upstream non verificata;
- NARWHAL `NOT_CONFIGURED`;
- componenti SILV con indipendenza non verificata;
- ticker contrattuale risolto, provider, timestamp/età quotazione e prezzo di riferimento non esposti;
- avvertenza esplicita di non usare i livelli per l'ingresso.

**Classificazione PRAVDA: NON_TRADE.** Score 100 non prova validità operativa. `NOT_EXECUTED` non è un fill. Senza ticker/contratto/provider e candele successive dello stesso contratto non è possibile stabilire SL prima, TP prima o livello già superato.

Telegram API:
- #750: ACK confermato, round-trip 528 ms;
- #751: ACK confermato, round-trip 395 ms.

Gli ACK provano l'accettazione API, non la visualizzazione sul dispositivo né l'esecuzione.

### Fonti SPUTNIK

Nel log runtime #294:
- SEC: HTTP 403, cooldown 21.600 secondi, zero filing;
- White House RSS sul vecchio endpoint: HTTPError;
- allineamento notizie GOLD: NO_DIRECTIONAL_NEWS.

Le righe OSError di WHITE_HOUSE/TRUTH_ARCHIVE/OGE appaiono nella fase dei test automatici prima del collector; non vengono attribuite come errori runtime del collector.

Il job #294 ha anche eseguito `git add sputnik_state.json`, creato il commit di persistenza e completato il push su main dopo rebase. È prova di persistenza dello stato per quella run, non prova di continuità del cron.

### PR SPUTNIK

- [PR #153 — propagazione direzione tecnica CFD](https://github.com/andreameloni1984-sys/trump-trucker/pull/153): OPEN, non integrata. Il difetto è stato riprodotto una seconda volta con #750/#751; commento PRAVDA [#6744436872](https://github.com/andreameloni1984-sys/trump-trucker/pull/153#issuecomment-6744436872).
- [PR #155 — diagnostica cadence](https://github.com/andreameloni1984-sys/trump-trucker/pull/155): OPEN, non integrata. Commento PRAVDA con la distinzione schedule/push e i gap: [#6744437665](https://github.com/andreameloni1984-sys/trump-trucker/pull/155#issuecomment-6744437665).
- [PR #154 — evitare analogia tariffaria da generiche menzioni della Cina](https://github.com/andreameloni1984-sys/trump-trucker/pull/154): OPEN, non integrata.
- [PR #131 — endpoint White House RSS](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): OPEN, non integrata.

---

## 3. GAGARIN — ultima produzione e dati

### Actions

- [Monitor #172](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716): schedule, avvio 06:34:18 UTC, conclusione 06:34:37 UTC, SUCCESS.
- [Push main #42645749040](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42645749040): avvio 15:32:50 UTC, job unico `test`, SUCCESS. È una suite di test, non una scansione di mercato.
- Il workflow [gagarin-monitor.yml](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml) conserva cron `*/15 * * * *`.
- Non risultano nuove run schedule del monitor dopo #172. Al cut-off il monitor era fermo da circa **9h10m18s**.

### Quotazioni della run #172

| Strumento | Provider | Età | Stato |
|---|---|---:|---|
| Soia | YAHOO | 659,4 s | STALE |
| Brent | YAHOO | 603,0 s | STALE |
| WTI | YAHOO | 602,9 s | STALE |
| Argento | YAHOO | 609,5 s | STALE |
| Grano | YAHOO | 648,2 s | STALE |
| Rame | YAHOO | 613,7 s | STALE |
| Oro | YAHOO | 622,4 s | STALE |
| Mais | YAHOO | 686,3 s | STALE |
| EUR/USD | BIQUOTE | 273,0 s | LIVE, contesto non operativo |
| GBP/USD | BIQUOTE | 273,6 s | LIVE, contesto non operativo |

Sono età riferite alla run delle 06:34 UTC, non quotazioni aggiornate alle 16:44 CET. I timestamp assoluti delle quotazioni non sono esposti.

### Candidata Soia SHORT

- Ticker logico: SOYBEAN/USD
- Provider: YAHOO, età 659,4 s
- Direzione: SHORT
- Probability 63; Quality 55,5; Confidence 35
- Stato: PAPER_WATCH
- Blocchi: LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, FINAL_CONFLUENCE_FAIL
- Entry, SL, TP e ATR: assenti

È una candidata bloccata, non un trade. Il riepilogo della run riporta zero entry registrate, zero nuovi feedback e `signals=0 open=0 closed=0`.

Il pre-alert Telegram #3728 è stato accettato dall'API in 478 ms, ma il corpo non è conservato: nessuna attribuzione di strumento o direzione.

### Journal e feedback

Verifica dei file su main:
- `commodities_prediction_log.json`: 981 record, 981 ID unici, zero duplicati; ultimo record 15 settembre 2026 15:45:04 UTC.
- Status: 945 PENDING, 36 NEUTRALE.
- Campo operativo: 960 WAIT, 15 LONG, 6 assenti.
- 21 record con azione COMPRA ORA, tutti PENDING: non sono fill.
- `journal.csv`: 11 righe datate 17 ottobre, tutte senza segnale.
- `paper_trade_log.csv`: una riga WTI LEGACY_IMPORT, con livelli storici ma senza provider/contratto/timestamp quotazione e senza P&L.
- `data/paper_open.json`: WTI P0001 OPEN legacy, P&L null; non è prova di fill.
- Nel job #172 `DATABASE_URL` è vuota.

### Difetto dimostrato nell'outcome engine su main

Il file [engine/feedback.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py) su main:
- non conserva nel record provider, quote timestamp, market type e contract expiry;
- abbina le serie soprattutto tramite symbol e timeframe, senza identità completa provider/contratto;
- se una candela tocca SL e TP nello stesso intervallo, controlla prima `stop_hit` e registra STOP.

Quest'ultimo comportamento non rispetta la regola PRAVDA: con sequenza intrabar ignota l'esito deve essere ESITO NON VERIFICABILE, non STOP automatico. La [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) propone correzioni, ma è OPEN e non integrata; il main resta difettoso.

### Universo

[commodities/universe.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities/universe.py) su main contiene ancora Argento e le due coppie Forex. La PR #241 per disabilitare Argento risulta **CLOSED senza merge**; quindi l'esclusione non è attiva su main. La PR #223 riguarda una scansione M5 separata e non sostituisce il monitor principale.

---

## 4. PR GAGARIN — nuova PR #243

[PR #243 — rimozione runtime Trading 212 e comandi broker](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/243)

Stato verificato:
- OPEN, DRAFT, non merged;
- head `08ec51fc08f17227c49ed8b1c5f34b818aa7c834`;
- 9 commit, 8 file modificati, 55 aggiunte e 322 cancellazioni;
- 7 workflow GitHub Actions sul latest head risultano SUCCESS.

La diff:
- rimuove il loop Invest/Trading 212 dal runner Render;
- rimuove le credenziali T212 dal workflow manuale `soyuz.yml`;
- rimuove i comandi broker e la vecchia tastiera personalizzata;
- lascia attivi webhook Telegram, invio messaggi/alert e comandi commodity come `/classifica` e `/analisi` (oltre al monitor manuale delle posizioni).

Quindi non elimina Telegram nel suo complesso: elimina il vecchio percorso broker e la relativa pulsantiera. È coerente con un GAGARIN orientato alla direzione commodity senza dipendenza runtime da Trading 212.

**La PR non è integrata:** su main il vecchio percorso resta. Il commento Cloudflare del 15:41:17 UTC segnala un build/deployment check fallito per il commit #243; non è prova di un deploy riuscito e non è stata eseguita alcuna operazione di deploy da PRAVDA.

Altre PR:
- [#242 — rifiuto scadenze CFD passate](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/242): OPEN/DRAFT, non integrata.
- [#225 — offset cron monitor](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225): OPEN/DRAFT, non integrata.
- [#192 — matching outcome](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, non integrata.
- [#241 — esclusione Argento](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/241): CLOSED senza merge.

---

## 5. Esiti e statistiche

| Metrica | Risultato |
|---|---:|
| Record ledger | 104 |
| Duplicati | 0 |
| Nuovo candidato aggiunto | 1 (SPUTNIK #751) |
| Nuovi trade eseguiti verificati | 0 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |
| Campione di trade verificabili | 0 |
| Win rate / average R | N/D |

Nessun backtest è stato eseguito o inventato. Per GOLD #751 e Soia #172 mancano identità completa del contratto e/o dati successivi omogenei. Non è possibile stabilire SL prima, TP prima o livelli già superati.

---

## 6. Fonti consultate

**SPUTNIK**
- Actions #294, #293, polling #54/#53, daily summary #12.
- Workflow `trump_tracker.yml`, `telegram-polling.yml`, `daily-summary.yml`.
- `sputnik_state.json` persistence step nel log #294.
- PR #153, #154, #155 e #131.

**GAGARIN**
- Actions monitor #172 e push main #42645749040.
- Workflow `gagarin-monitor.yml` e `gagarin.yml`.
- `commodities/universe.py`, `engine/feedback.py`, `commodities_prediction_log.json`, `journal.csv`, `paper_trade_log.csv`, `data/paper_open.json`.
- PR #192, #225, #241, #242 e #243.

---

## 7. Prossimo controllo

1. Verificare una nuova run **schedule** del collector SPUTNIK, distinta da push/manuale.
2. Verificare se il polling SPUTNIK mantiene una cadenza regolare dopo #54.
3. Verificare la prossima run schedule del monitor GAGARIN; distinguere sempre i job test dai monitor produttivi.
4. Controllare nuove quotazioni commodity con timestamp assoluto, ticker e contratto.
5. Verificare se PR #153 risolve la propagazione della direzione tecnica nella card CFD.
6. Verificare la diagnostica cadence proposta in PR #155.
7. Verificare lo stato della PR #243 e l'eventuale build Cloudflare, senza assumere che CI significhi deploy.
8. Verificare la persistenza reale del journal e completare provider/contratto/doppio-touch nell'outcome engine.

**PRAVDA — PAPER ONLY. Nessun merge, deploy, ordine reale o modifica ai repository applicativi.**
