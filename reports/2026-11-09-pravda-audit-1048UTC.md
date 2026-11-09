# PRAVDA — Audit indipendente SPUTNIK / GAGARIN

**Cut-off: 9 novembre 2026, 10:48:59 UTC (11:48:59 Europe/Rome)**

## Sintesi

Verificati direttamente:
- le prime 100 GitHub Actions più recenti di ciascun repository e le ultime run di tipo `schedule`;
- i log completi dei job produttivi SPUTNIK #293, Telegram Polling #53 e GAGARIN #172;
- i workflow e i cron su `main`;
- lo stato SPUTNIK persistito;
- journal, paper log, position, prediction log e monitor state GAGARIN;
- le PR #131, #153, #154, #192, #239, #240 e #241, inclusi diff, stato e CI rilevanti.

**Non risultano nuove run produttive dopo SPUTNIK #293 / Polling #53 e GAGARIN #172.** Le CI delle PR e i push sul branch di una PR non sono scansioni di mercato.

Non è emerso alcun nuovo segnale produttivo da aggiungere al ledger. Nessun trade eseguito è verificabile.

## 1. Ledger cumulativo PRAVDA

Ledger ereditato senza modifiche:
- File: `reports/pravda-signal-ledger-2026-11-09.csv`
- Blob SHA: `1acbe2994b6147a4d2fdd39108cf46f499fd6265`
- Record dati: **103**; colonne: **33**.
- SPUTNIK: **48**; GAGARIN: **55**.
- `audit_signature` uniche: **103**; duplicati: **0**.
- `source_record_id` unici: **103**; duplicati: **0**.
- `NON_TRADE`: **74**.
- `ESITO_NON_VERIFICABILE`: **29**.
- Fill verificati: **0**; SL verificati: **0**; TP verificati: **0**.

I 29 `ESITO_NON_VERIFICABILE` non sono 29 trade: comprendono previsioni storiche/candidate prive di identità contrattuale o di una serie successiva omogenea. Le statistiche di performance sono N/D: il campione di trade eseguiti e verificabili è **zero**.

Ultimi record già presenti:
- SPUTNIK #746, #747 e #748.
- GAGARIN candidata SOYBEAN/USD SHORT bloccata.
- GAGARIN WATCH pre-alert #3728 non attribuibile.

Nessuna riga aggiunta e nessuna duplicazione.

## 2. GitHub Actions e continuità

Ultime run programmate riscontrate nella prima pagina (100 elementi) delle Actions:

| Processo | Ultima run | Completamento UTC | Stato | Tempo trascorso al cut-off |
|---|---|---:|---|---:|
| SPUTNIK collector | #293 — [run](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770) | 06:01:51 | SUCCESS | 4h47m08s |
| SPUTNIK Telegram polling | #53 — [run](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570062235) | 05:55:56 | SUCCESS | 4h53m03s |
| GAGARIN Paper Monitor | #172 — [run](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716) | 06:34:37 | SUCCESS | 4h14m22s |

Cron letti dai workflow su main:
- SPUTNIK collector: `2-59/5 * * * *`.
- SPUTNIK polling: `*/5 * * * *`.
- GAGARIN monitor: `*/15 * * * *`.

I gap osservati non rispettano le frequenze dichiarate. La causa non è dimostrata e non viene ipotizzata.

## 3. SPUTNIK — run produttiva #293

- Run: [SPUTNIK #293](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770)
- Job: [sputnik / 129006852221](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770/job/129006852221)
- Avvio: 06:01:41 UTC; completamento: 06:01:51 UTC; SUCCESS.
- Il job ha persistito `sputnik_state.json` su main con commit `8bdf7ab16ec3bfd23d5f3160a4e87dffbfd35396`. Questo è un commit automatico di stato del workflow, non una modifica PRAVDA.

### Fonti e ritardi

Dal log produttivo:
- SEC: HTTP 403; cooldown 21.600 secondi; filing=0.
- Transazioni: 0.
- White House RSS: il runtime usa ancora `https://www.whitehouse.gov/feed/`, che restituisce HTTPError.
- Public intelligence scan: 3 findings; digest con 2 eventi RSS individuali e una correlazione page-level TRUTH_ARCHIVE.

Lo stato persistito su main riporta `updated_at=2026-11-09T06:01:46.594274Z`, `events=0` e 500 elementi in `intelligence_history`.

Eventi individuali:
1. Quote post #43530: pubblicato 8 novembre 2026 alle 23:41:05 UTC; rilevato alle 06:01:46.562982 UTC. Ritardo: **6h20m41.6s**. [Permalink](https://www.trumpstruth.org/statuses/43530). Classificazione `OTHER / NO_ANALOGUE`.
2. Post S.5653 #43532: pubblicato 9 novembre 2026 alle 00:05:49 UTC; rilevato alle 06:01:46.562743 UTC. Ritardo: **5h55m57.6s**. [Permalink](https://www.trumpstruth.org/statuses/43532).

Il record S.5653 è classificato su main come `TRADE_ESCALATION` e collegato all'analogia `china_tariff_escalation_2025_10`, con direzioni storiche tra cui OIL DOWN. Il testo recuperato riguarda permitting/indipendenza energetica e contiene una menzione generica della Cina, non un annuncio tariffario. La classificazione/analogia è quindi non supportata dal contenuto specifico.

La correlazione TRUTH_ARCHIVE associata è page-level: URL della homepage, titolo e data di pubblicazione vuoti. Non è un nuovo post individuale verificabile.

### Messaggi effettivi e livelli

| ID | Generazione UTC | ACK/API UTC | Contenuto | Stato PRAVDA |
|---|---|---|---|---|
| #746 | 06:01:48.1711626 | 06:01:48.1720275 | Digest informativo, 2 item-level events | NON_TRADE |
| #747 | 06:01:48.1720811 | 06:01:48.1731760 | GOLD LONG preliminare; tecnica LONG 5m; momentum +0,077%/15m; NO_DIRECTIONAL_NEWS | NON_TRADE |
| #748 | 06:01:48.1732205 | 06:01:48.1742253 | GOLD LONG EARLY_SETUP con livelli numerici | NOT_EXECUTED / NON_TRADE |

Messaggio #748:
- Entry: **4133.2002**
- SL: **4130.5859**
- TP1: **4135.8145**
- TP2: **4138.4289**
- ATR: **1.7429**
- Score: **100**
- Stato esplicito: **NOT_EXECUTED**.

Difetti verificati nel messaggio:
- Titolo CFD, corpo riferito a `FUTURES_CONTINUOUS_FRONT_MONTH`.
- Ticker contrattuale risolto non esposto; scadenza esatta UNKNOWN.
- Provider, timestamp della quotazione, età della quotazione e prezzo di riferimento non esposti.
- NARWHAL non configurato.
- Il messaggio #747 mostra direzione tecnica LONG 5m; la card #748 stampa `TECNICA: N/D` e `D-L-A: NEUTRAL / NO_DIRECTION`.
- La card avverte di non usare i livelli per un ingresso.

**Non è un trade.** Senza ticker/mercato/scadenza/provider e senza una serie successiva dello stesso contratto non è possibile stabilire SL prima, TP prima o livelli già superati. Gli ACK API e i round-trip registrati (563ms, 313ms, 322ms) provano la risposta API con message ID, non la visualizzazione sul dispositivo.

### PR SPUTNIK già esistenti

- [PR #154](https://github.com/andreameloni1984-sys/trump-trucker/pull/154): OPEN, non draft, 2 commit; ranking e item-intelligence CI SUCCESS. Richiede parole esplicite su tariffe/trade war prima di assegnare `TRADE_ESCALATION`; include regression sul contenuto S.5653. Non integrata: la classificazione errata resta su main.
- [PR #153](https://github.com/andreameloni1984-sys/trump-trucker/pull/153): OPEN, non draft, 2 commit; ranking e Telegram-menu CI SUCCESS. Propaga la direzione tecnica 5m alla card CFD. Non integrata: la discrepanza #747/#748 resta in produzione.
- [PR #131](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): OPEN, non integrata. Il branch propone `/news/feed/`, ma il log #293 dimostra che main usa ancora il vecchio endpoint.
- [PR #150](https://github.com/andreameloni1984-sys/trump-trucker/pull/150): OPEN; correzione anti-ripetizione legata a nuovi item RSS, non ancora in produzione.

Nessuna nuova segnalazione duplicata aperta da PRAVDA.

## 4. GAGARIN — run produttiva #172

- Run: [GAGARIN #172](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716)
- Job: [Run Gagarin directly on GitHub / 129017049476](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716/job/129017049476)
- Avvio: 06:34:18 UTC; completamento: 06:34:37 UTC; SUCCESS.
- `PAPER_TRADING_ONLY=1`.
- `DATABASE_URL` vuota nel job.
- Soglie effettivamente caricate: Probability 40, Quality 30, Confidence 35, RR 2.5, Max Stop ATR 2.5. PRAVDA non modifica questi valori.

### Quotazioni

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
| EUR/USD | BIQUOTE | 273,0 s | LIVE, ausiliario |
| GBP/USD | BIQUOTE | 273,6 s | LIVE, ausiliario |

Il log non espone timestamp assoluti delle singole quotazioni, ticker feed risolti, market type e scadenza. Le età non vengono trasformate in timestamp assoluti.

### Candidata Soia SHORT

- Simbolo logico: `SOYBEAN/USD`; ticker feed esatto non esposto.
- Provider: YAHOO; età: 659,4 secondi; timestamp assoluto non esposto.
- Market type e scadenza: non esposti.
- Direzione: SHORT.
- Probability 63,0; Quality 55,5; Confidence 35,0.
- Stato: `PAPER_WATCH`.
- Blocchi: `LIVE_DATA_NOT_FRESH`, `TRIGGER_NOT_CONFIRMED`, `TRIGGER_DIRECTION_MISMATCH`, `FINAL_CONFLUENCE_FAIL`.
- Entry, SL, TP e ATR: assenti; nessun invio operativo.

È una candidata bloccata, non un segnale eseguito e non un trade.

### Telegram #3728 e riepilogo

- Message ID #3728; API SEND CONFIRMED alle 06:34:34.1131912 UTC; round-trip 478ms.
- Il corpo del pre-alert non è conservato nel job log: strumento, direzione, provider e livelli non sono attribuibili.
- Il log riporta: Recorded entries 0; Updated open outcomes 0; New feedback signals 0; New additional live forecasts 0; `signals=0 open=0 closed=0`.

L'ACK API non prova la visualizzazione sul dispositivo.

### Journal, feedback e previsioni

File pubblici su main:
- `journal.csv`: 11 righe del 17 ottobre, tutte senza segnali.
- `paper_trade_log.csv`: un WTI LONG `LEGACY_IMPORT` del 8 ottobre; entry 96.24, SL 89.37, TP1 103.11. Mancano provider, timestamp quota, mercato/scadenza e prova di fill.
- `data/paper_open.json`: WTI P0001 `OPEN`, legacy, P&L null; non è prova di fill.
- `position.json`: vecchia posizione Heating Oil LONG aperta il 15 settembre, senza identità/provider/quotazione contrattuale.
- `commodities_monitor_state.json`: ultimo timestamp 17 settembre.
- `commodities_prediction_log.json`: 981 record; ultimo `created_at` 15 settembre 2026 15:45:04 UTC; 945 PENDING e 36 NEUTRALE. Le 21 righe `COMPRA ORA` sono tutte PENDING; 960 righe hanno `operational_signal=WAIT`, 15 LONG e 6 senza campo.

Il workflow dichiara che i paper journal sono dati privati e non devono essere committati nel repository pubblico. La DATABASE_URL è vuota e il run non ha prodotto artifact scaricabili: la persistenza privata esterna non è verificabile da questo audit. Non si dichiara che un eventuale storage privato non esista; si registra soltanto che non è dimostrato.

### Universo Argento e PR #241

Su main l'universo e il log #172 includono ancora Argento/XAG.

[PR #241](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/241) è OPEN e DRAFT, 8 commit avanti e 0 indietro rispetto a main. Il branch disabilita XAG e lo rimuove dalle route attive, ma la CI di integrazione del suo head `eba9748df31644310437dd9c930284d0c9f70408` fallisce: **2 failed, 569 passed**. I due test falliti sono gli alias `argento` e `silver`: `_resolve_commodity()` restituisce ancora l'oggetto Argento con `enabled=False` invece di `None`.

La PR non è integrata; il monitor produttivo #172 ha quindi ancora analizzato Argento. Il thread della PR contiene note di perimetro non coerenti tra loro: questo audit registra lo stato tecnico, senza promuovere né modificare l'universo.

[PR #240](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/240) è OPEN/DRAFT e propone di ridurre limiti di freschezza da 1200 a 600 secondi. È una modifica a soglie/filtri; PRAVDA non la promuove e non cambia alcun parametro.

## 5. Outcome engine e identità contrattuale

### PR #192 — feedback/outcome

Su main `engine/feedback.py`:
- il fingerprint di `_signal_record()` usa symbol, direzione, timeframe, livelli e candela, senza provider/mercato/scadenza;
- se una stessa candela OHLC tocca SL e TP, il codice controlla `stop_hit` prima dei target e registra STOP.

Questo non soddisfa il protocollo PRAVDA: con una sola candela OHLC l'ordine intrabar è ignoto; l'esito corretto è `ESITO NON VERIFICABILE`.

Il branch [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) aggiunge provider e identità contrattuale al fingerprint e gestisce il doppio tocco come `SAME_CANDLE_SL_TP_AMBIGUITY`. Tuttavia `_market_contract_match()` confronta quote symbol, market type, contract month/expiry, **ma non confronta l'uguaglianza del provider** tra segnale e serie successiva. La PR è OPEN, non integrata. Il difetto provider è già presente nei commenti esistenti: nessuna segnalazione duplicata.

### PR #239 — scadenza CFD

[PR #239](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/239) è OPEN/DRAFT e ha come base un branch feature, non main. Nel branch, `_verified_expiry()` controlla formato YYYY-MM-DD e validità di calendario, ma non rifiuta una scadenza future già passata. Il difetto è già documentato nel commento esistente. Il registry resta vuoto; non è dimostrato un feed CFD autenticato o una quotazione broker.

## 6. Esiti e statistiche

- Trade eseguiti verificabili: **0**.
- Fill verificati: **0**.
- SL prima: **0**.
- TP prima: **0**.
- Doppio tocco risolto con sequenza intrabar: **0**.
- Metriche win rate / average R / total R: **N/D**.

SPUTNIK #748 ha livelli numerici ma `NOT_EXECUTED`, ticker/contratto/provider/quote time non identificati: nessun esito di trade. La candidata Soia GAGARIN è bloccata, senza livelli e con quote stale: nessun esito. #3728 non è attribuibile.

Non sono stati eseguiti backtest né ricostruzioni di prezzi spot/futures o scadenze diverse.

## 7. Fonti consultate

- GitHub Actions e log: SPUTNIK [#293](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770), polling [#53](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570062235), GAGARIN [#172](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716).
- Stato SPUTNIK: `sputnik_state.json` su main; record RSS #43530 e #43532.
- Journal e stato GAGARIN: `journal.csv`, `paper_trade_log.csv`, `data/paper_open.json`, `position.json`, `commodities_prediction_log.json`, `commodities_monitor_state.json`.
- Workflow cron: `.github/workflows/trump_tracker.yml`, `.github/workflows/telegram-polling.yml`, `.github/workflows/gagarin-monitor.yml`.
- PR e diff: #131, #153, #154, #192, #239, #240, #241; CI run #42574224863 per il fallimento PR #241.

## 8. Prossimo controllo

1. Verificare le prossime run schedule effettive, non le CI delle PR.
2. Verificare se SPUTNIK integra il feed White House corretto e non applica l'analogia tariffaria a S.5653.
3. Verificare la propagazione della direzione tecnica nella card CFD.
4. Controllare quote commodity fresche con timestamp assoluto, ticker feed, market type e scadenza.
5. Verificare l'esito dei test alias e lo stato della PR #241; non presumere che la modifica sia in produzione.
6. Verificare il matching provider nella PR #192 e il rifiuto delle scadenze future già passate nella #239.
7. Dimostrare la persistenza del journal con una scrittura e successiva lettura verificabili.
8. Valutare eventuali SL/TP solo con candele successive dello stesso identico strumento, provider, mercato e contratto; se SL e TP cadono nella stessa candela OHLC, usare `ESITO NON VERIFICABILE`.

---

**Perimetro rispettato:** nessuna modifica al codice applicativo, strategia, filtri, punteggi o rischio; nessun merge/deploy, ordine reale, modifica a secret o Render. Nessun servizio a pagamento. PAPER ONLY.
