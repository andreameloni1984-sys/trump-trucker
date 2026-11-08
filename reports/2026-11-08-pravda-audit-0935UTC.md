# PRAVDA — Audit incrementale SPUTNIK / GAGARIN

**Cut-off:** 8 novembre 2026, 09:34:57 UTC (10:34:57 Europe/Rome)  
**Perimetro:** main dei due repository, ultime GitHub Actions di produzione, stato persistito, ledger PRAVDA, journal pubblici, codice feedback/outcome e PR aperte. Sola verifica. PAPER ONLY.

## 1. Esito sintetico

- **SPUTNIK:** collector run [#42467543117](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42467543117), avvio 09:31:31 UTC, completamento 09:31:41 UTC, SUCCESS. Il successivo commit di persistenza [35f601f](https://github.com/andreameloni1984-sys/trump-trucker/commit/35f601f9ba1d5748473119235a0eda180c86a554) conferma un nuovo item RSS; nessun artifact della run.
- **GAGARIN:** monitor run [#42467422750](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42467422750), avvio 09:29:58 UTC, completamento 09:30:17 UTC, SUCCESS; nessun artifact.
- Il log testuale completo dei job non è esposto dal connettore GitHub usato in questo controllo. Sono verificabili metadati, step, file persistiti e commit; non sono verificabili body Telegram, numero di segnali, conteggio feedback o provider/quote della run GAGARIN più recente.
- Ledger aggiornato in modo incrementale: **82 record** — SPUTNIK 34, GAGARIN 48; **82 firme e 82 source ID unici; zero duplicati**. Aggiunto un solo item SPUTNIK datato e identificato, classificato NON_TRADE.
- Classificazione: **53 NON_TRADE, 29 ESITO_NON_VERIFICABILE**. Fill verificati 0; SL verificati 0; TP verificati 0. Win rate, average R e total R: **N/D**. Nessuna statistica di performance è calcolabile su un campione con esiti verificati pari a zero.
- Nessun backtest. Nessun merge, deploy, ordine, accesso a broker o modifica a strategia/rischio.

## 2. SPUTNIK — nuovo item e produzione

### Nuova evidenza persistita

Il commit di stato [35f601f](https://github.com/andreameloni1984-sys/trump-trucker/commit/35f601f9ba1d5748473119235a0eda180c86a554), prodotto dopo la run #288, registra:

- event ID: `f3dd016d2288efc8d1a89d79`;
- fonte: PUBLIC_RSS, feed Trump’s Truth archive;
- URL archivio: https://www.trumpstruth.org/statuses/43524;
- post originale: https://truthsocial.com/@realDonaldTrump/117578791772773790;
- titolo: “Quote post from November 8, 2026”;
- pubblicazione: 03:53:01 UTC;
- rilevazione: 09:31:37.313495 UTC;
- ritardo pubblicazione→rilevazione: **5h38m36s**;
- dominio classificato: MEDIA; event_type OTHER; historical reaction NO_ANALOGUE.

Non è un catalizzatore direzionale: nessuna commodity mappata, nessun ticker, mercato, scadenza, quotazione, provider, timestamp prezzo, direzione, entry, SL, TP o ATR. È registrato nel ledger come `intelligence_item_not_market_signal`, outcome NON_TRADE. Non è stato registrato come messaggio Telegram: nessun message_id/sent_at dimostrato per questo item.

Il commit contiene anche una scansione page-level di TRUTH_ARCHIVE (`00bbab8fa0cf521697a3f652`) senza timestamp di pubblicazione e con evidenza PAGE_LEVEL. Non è contata come nuovo item datato né come segnale.

### Cadenza e Telegram

- Il workflow collector dichiara cron `2-59/5`; la run #287 è partita alle 02:41:59 UTC e la #288 alle 09:31:31 UTC: **gap 6h49m32s**, non 5 minuti.
- Il polling Telegram dichiara `*/5`; run #48 alle 02:20:16 UTC e #49 alle 09:16:25 UTC: **gap 6h56m09s**.
- Le run #288 e polling #49 sono SUCCESS. Questo prova il completamento dei job, non la consegna al dispositivo. Per la #288 non è disponibile un message_id verificabile.
- La persistenza continua a scrivere `sputnik_state.json` su `main`: il commit #35f601f lo dimostra. PR [#144](https://github.com/andreameloni1984-sys/trump-trucker/pull/144), che sposta lo stato su branch dedicato, è ancora OPEN e non merged.
- Il workflow main continua a passare `GAGARIN_CLOUD_API_URL` e `GAGARIN_CLOUD_API_KEY` al collector. PR [#147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147) rimuove l'handoff e i riferimenti, ma resta OPEN/non merged. Il branch è 5 commit ahead e 2 behind main; le due CI sul suo head sono SUCCESS ([ranking #42463175953](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42463175953), [item intelligence #42463175954](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42463175954)).
- PR [#148](https://github.com/andreameloni1984-sys/trump-trucker/pull/148), per non ripetere raccomandazioni senza un nuovo item RSS, resta OPEN/non merged; branch 2 ahead e 5 behind main. CI ranking e item-intelligence sul suo head sono SUCCESS ([#42450417214](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42450417214), [#42450417210](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42450417210)).
- PR [#145](https://github.com/andreameloni1984-sys/trump-trucker/pull/145) per provenance quote Yahoo resta OPEN/non merged: la provenienza completa non è dimostrata sul main corrente.

## 3. GAGARIN — run, journal e integrità degli esiti

### Run e cadenza

- Workflow main `.github/workflows/gagarin-monitor.yml`: cron effettivo dichiarato `*/15 * * * *`, non 5 minuti.
- Run #167: 02:30:08 UTC; run #168: 09:29:58 UTC. Gap osservato: **6h59m50s**, molto superiore ai 15 minuti dichiarati.
- La run #168 ha completato tutti gli step, incluso “Run Gagarin analysis, paper journal, feedback and Telegram alerts”, con SUCCESS. Nessun artifact. Il log dettagliato non è leggibile nel connettore: non attribuisco un segnale, un messaggio Telegram o una consegna senza body/message_id.
- Main è ancora al commit [69bb6d0](https://github.com/andreameloni1984-sys/commodity-news-scanner/commit/69bb6d070dc180f9fc671c4f87b3c5fd19be1009), del 7 novembre 13:37:42 UTC. Nessuna nuova persistenza pubblica del journal è stata osservata dopo quel commit.

### Artefatti pubblici

- `journal.csv`: righe del 17 ottobre con “nessun segnale”; non è un registro di fill.
- `paper_trade_log.csv`: un solo record legacy WTI del 8 ottobre, LONG, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55. `signal_id`, provider, ticker di quotazione, timestamp quote, valuta/unità, mercato, provider di esecuzione e ticker esecutivo sono vuoti; scadenza non registrata.
- `data/paper_open.json`: ticket P0001 ancora marcato OPEN con gli stessi livelli, PAPER ONLY, `promoted=null`. Non è prova di ordine o fill; non è verificabile come contratto/mercato esatto e non va conteggiato come trade con esito.
- `commodities_monitor_state.json` è datato 17 settembre; `commodities_prediction_log.json` contiene predizioni legacy del 10 settembre, molte con WAIT/PENDING e senza provenance completa. Nessuno di questi file dimostra un segnale operativo attuale.

### Difetti di audit dimostrati sul main

Nel codice attuale `engine/feedback.py`:

1. `signal_id` è derivato da symbol, direction, timeframe, entry, stop, TP e timestamp candela; non include provider, ticker quotazione, market type, contratto/scadenza.
2. `update_open_outcomes()` abbina le candele per symbol/timeframe, non per provider + ticker + mercato + contratto + expiry. Quindi il codice main non garantisce che i prezzi successivi appartengano allo stesso identico strumento/contratto richiesto da PRAVDA.
3. Se la stessa candela tocca SL e TP, il codice attuale registra STOP prima di valutare i target. La sequenza intrabar non è nota: secondo il criterio PRAVDA il caso deve restare ESITO NON VERIFICABILE, non SL certo.

Correzione già proposta in [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): fingerprint con provider/ticker/market/contract/expiry, matching same-contract e classificazione `SAME_CANDLE_SL_TP_AMBIGUITY` come non verificabile. PR OPEN/non merged. Sul suo head risultano SUCCESS le sei CI (Execution Layer, NEWS alert, Public Event Brain, trade-plan, PAPER, SOYUZ GAGARIN Tests), ma il branch è divergente: 6 commit ahead e 4 behind main. Va riallineato e riesaminato; nessuna correzione è considerata in produzione.

Altre correzioni già esistenti:
- [PR #91](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/91): ordinamento cronologico delle osservazioni per lo scorecard NEWS; OPEN/draft.
- [PR #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): journal PAPER durevole PostgreSQL e dedupe cross-run; OPEN/draft.
- [PR #200](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/200): usa lo stesso DATABASE_URL/driver nel daily summary; OPEN/draft.
- [PR #94](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/94): copertura esiti/evaluation status; OPEN/draft.

Il monitor workflow passa `DATABASE_URL`, ma il daily-summary workflow non lo passa. Il codice feedback può usare PostgreSQL solo se la variabile è presente e la connessione riesce; altrimenti ricade sul CSV locale. Non ho letto né modificato secret o database e non posso confermare quale backend sia stato effettivamente usato dalla run #168.

### Universo e quote

Il file main `commodities/universe.py` include Oro, Argento, Rame, WTI, Brent, Grano, Mais, Soia, EUR/USD e GBP/USD. Non include Platino e Palladio e mantiene Argento e FX: il paniere effettivo non coincide con quello richiesto (Oro, Rame, Platino, Palladio, WTI, Brent, Grano, Mais, Soia). PR [#212](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/212) è ancora OPEN/draft e riguarda la rimozione delle coppie FX; non dimostra ancora l'allineamento completo del paniere.
 
PR [#236](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/236) e [#237](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/237) trattano prove di identità del catalogo CFD e associazione simbolo esatto; sono OPEN/draft e non implementano un feed di quotazioni né forniscono candele broker. Nessun accesso Trading212 è stato usato o dichiarato.

L'ultimo dettaglio GAGARIN disponibile nel ledger, dalla run #42438806862, era un candidato Argento LONG/PAPER_WATCH bloccato: Yahoo age 102922.9 secondi (~28h35m), timestamp assoluto, mercato/expiry e reference price non esposti, nessun entry/SL/TP/ATR e zero entry registrate. Non lo considero segnale operativo e non ne calcolo un esito.

## 4. Storico e statistiche

Il ledger è stato aggiornato con un solo record SPUTNIK per event ID `f3dd016d2288efc8d1a89d79`. Firma/source ID univoci: nessun duplicato.

| Metrica | Conteggio |
|---|---:|
| Record totali ledger | 82 |
| SPUTNIK | 34 |
| GAGARIN | 48 |
| NON_TRADE | 53 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |
| Win rate / average R / total R | N/D |

Le 29 righe ESITO_NON_VERIFICABILE non sono 29 trade; i record NOT_EXECUTED/WAIT/WATCH e gli item news-only non sono trade. Non esistono campioni verificabili da cui ricavare performance.

## 5. Fonti consultate e limiti

- GitHub Actions runs/jobs: SPUTNIK #42467543117, polling #42466478249; GAGARIN #42467422750.
- Commit/state SPUTNIK: 35f601f9ba1d5748473119235a0eda180c86a554.
- Workflow: `trump_tracker.yml`, `telegram-polling.yml`, `gagarin-monitor.yml`, `daily-summary.yml`.
- Ledger PRAVDA 2026-11-08, report precedente 08:35 UTC, `sputnik_state.json` via diff commit, `journal.csv`, `paper_trade_log.csv`, `data/paper_open.json`, `commodities_monitor_state.json`, `commodities_prediction_log.json`.
- Codice: `engine/feedback.py`, `state_store.py`, `main.py`, `commodities/universe.py`.
- PR e CI: SPUTNIK #144/#145/#147/#148; GAGARIN #91/#94/#192/#200/#202/#212/#236/#237.
- Non disponibili: log completi dei due job più recenti tramite connettore, body Telegram, database privato, quote/candele successive con identità esatta del contratto. Nessun servizio a pagamento o broker consultato.

## 6. Prossimo controllo

Verificare le prossime run reali e la loro distanza temporale; acquisire body e message_id Telegram dai log senza attribuzioni per inferenza; per ogni eventuale segnale richiedere provider, quote timestamp, ticker, mercato e expiry prima di collegare le candele successive. Rivalutare PR #192 dopo riallineamento e verificare se le correzioni sono state effettivamente integrate su main. Nessun merge/deploy eseguito.
