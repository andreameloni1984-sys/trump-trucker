# PRAVDA — audit SPUTNIK / GAGARIN
**Cut-off: 2026-11-08 18:43:45 UTC (19:43:45 CET)**

## Perimetro e metodo
Verifica in sola lettura di:
- `andreameloni1984-sys/trump-trucker` — branch `main` a `b8df4c9e64bf22f27a43e248c8369312ab2cd3b7`.
- `andreameloni1984-sys/commodity-news-scanner` — branch `main` a `444a23e5d183660ebc655f04c4c79ed1370101b6`.

Consultati GitHub Actions recenti, log dei job, workflow YAML, ledger PRAVDA, file journal/posizione, `commodities/universe.py`, `engine/feedback.py`, metadati/diff/commenti delle PR. Nessuna modifica a codice, strategia, filtri, score, rischio, secret, Render, broker o ordini. Nessun servizio a pagamento.

## 1. Ledger — integrità e campione
File: [pravda-signal-ledger-2026-11-08.csv](pravda-signal-ledger-2026-11-08.csv)

Verifica diretta del CSV su `main`:
- 91 record dati;
- 91 firme `audit_signature` uniche;
- 91 `source_record_id` unici;
- 0 duplicati;
- SPUTNIK 40; GAGARIN 51;
- `NON_TRADE` 62; `ESITO_NON_VERIFICABILE` 29;
- fill verificati 0; SL verificati 0; TP verificati 0.

Non sono state aggiunte righe: gli eventi #735, #736, #737 e #3722 sono già nel ledger. Le nuove run consultate non hanno prodotto ulteriori record di mercato. La riga di test che menziona message_id=731 nel log SPUTNIK è output della suite di regressione, non un nuovo invio di produzione, quindi non è stata duplicata.

I 29 `ESITO_NON_VERIFICABILE` non sono 29 trade. Non esiste un campione di fill con prezzi successivi dello stesso identico strumento/contratto: win rate, R medio e rendimento restano N/D.

## 2. SPUTNIK — ultima scansione produttiva
[Run #289 — 42498971172](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42498971172) — schedule, SUCCESS, 16:15:37–16:15:47 UTC; job 128787341086.

Evidenze del log:
- SEC: HTTP 403, cooldown 21.600 secondi; zero filing.
- White House RSS: HTTPError sull'endpoint `https://www.whitehouse.gov/feed/`.
- TRUTH_ARCHIVE e OGE: errori OSError riportati nel log.
- scansione pubblica: `findings=2`, ma il messaggio distingue un item pubblico individuale e uno snapshot/page-level; il secondo non è contato come un nuovo post distinto.
- Item individuale: pubblicato 13:49:32 UTC, rilevato 16:15:42.637 UTC; ritardo 2h26m10,6s. Fonte: [Truth Archive item 43525](https://www.trumpstruth.org/statuses/43525). Classificazione OTHER / NO_ANALOGUE, senza mapping commodity né direzione.
- NARWHAL è abilitato come riferimento ma la chiave è vuota; il messaggio dichiara `NOT_CONFIGURED`.

Messaggi effettivi nella fase di produzione:
- #735 digest notizia, API Telegram confermata (round-trip 413 ms);
- #736 GOLD, bias NEUTRAL, tecnica 5m UNAVAILABLE, `NO_DIRECTIONAL_NEWS`, senza quotazione o livelli (377 ms);
- #737 GOLD, `NO_DIRECTION`, `NOT_EXECUTED`, score 100, nessuna quotazione futures fresca, nessun ticker/provider/timestamp/scadenza/entry/SL/TP/ATR (323 ms).

#736 e #737 sono due rappresentazioni della stessa analisi GOLD, non due setup. #737 si intitola “ANALISI CFD” ma il corpo dichiara `FUTURES_CONTINUOUS_FRONT_MONTH`; non è quindi una quotazione CFD identificata né un future con scadenza certa. Score 100 non è validità operativa. Gli ACK dimostrano accettazione API, non consegna/visualizzazione sul dispositivo.

Il log presenta anche una contraddizione già segnalata: “GAGARIN handoff disabled” e credenziali URL/key vuote, poi “GAGARIN confirmation received”, quindi di nuovo handoff disabled e forwarding 0 ms. Non prova un handoff esterno. Rilievo già registrato nel commento [PR #147, commento 6725075833](https://github.com/andreameloni1984-sys/trump-trucker/pull/147#issuecomment-6725075833).

Il collector ha eseguito regression tests prima del programma principale. Il message_id=731 stampato nella suite è test output e non un nuovo invio del collector #289.

### Polling Telegram SPUTNIK
[Run #50 — 42498116149](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42498116149) — 16:05:42 UTC, SUCCESS. Log: `Pending updates: 0`. Workflow [telegram-polling.yml](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/telegram-polling.yml) dichiara cron ogni 5 minuti.

## 3. GAGARIN — ultimo monitor produttivo
[Run #169 — 42499039797](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42499039797) — schedule, SUCCESS, 16:16:25–16:16:43 UTC; job 128787549596.

Dieci strumenti elencati, tutti `MARKET_CLOSED`. Età delle quote riportate:
- YAHOO: 152.198,7–161.802,8 secondi;
- BIQUOTE (EUR/USD e GBP/USD): circa 152.499–152.500 secondi.
Intervallo complessivo: circa 42,3–44,9 ore. Sono dati stale; il log non espone timestamp assoluto della quotazione, ticker provider risolto, mercato e scadenza del contratto. Non è possibile usare questi dati per un esito forward.

I blocker riportano dati non freschi, setup/trigger non validi o non confermati, entry/stop/TP1–TP3/stop-ATR/RR mancanti e altri controlli falliti. Riepilogo:
- Recorded entries: 0;
- Updated open outcomes: 0;
- New feedback signals: 0;
- `signals=0 open=0 closed=0`.

Telegram #3722 è stato accettato dall'API (406 ms), ma il corpo del messaggio non è conservato: strumento, ticker, direzione e livelli non sono attribuibili. L'ACK non prova consegna al dispositivo.

### Journal e persistenza
Il workflow [gagarin-monitor.yml](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml) dichiara cron ogni 15 minuti e commenta che i journal PAPER sono dati privati: non vanno committati nel repository pubblico; la persistenza sarà riattivata solo dopo deployment e verifica dello storage privato. Nel job #169 `DATABASE_URL` risulta vuota. `gagarin_feedback.csv` non è presente nella root di main.

Artefatti pubblici presenti:
- [journal.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/journal.csv): righe del 17 ottobre 2026, tutte con “nessun segnale”.
- [paper_trade_log.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/paper_trade_log.csv): WTI del 8 ottobre, marcato `LEGACY_IMPORT` / `OPEN`, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55; provider, ticker esecutivo, mercato/contratto, timestamp della quotazione, ATR e prova del fill assenti.
- [position.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/position.json): vecchia posizione Heating Oil LONG aperta il 15 settembre 2026, entry 4,8844, SL 4,5418, TP1 5,4473, TP2 5,6284, TP3 5,882.

Questi artefatti legacy non sono riconciliati con il monitor corrente che dichiara zero posizioni/entrate. Non vengono conteggiati come fill o trade verificati.

### Universo effettivo
[commodities/universe.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities/universe.py) dichiara 8 commodity operative: Oro, Argento, Rame, WTI, Brent, Grano, Mais e Soia; EUR/USD e GBP/USD restano due strumenti Forex ausiliari. Platino e Palladio non compaiono. Argento è ancora abilitato, nonostante la precedente richiesta di escluderlo per volatilità. Il codice attuale separa le otto commodity operative dal Forex ausiliario, ma `_select_run_universe()` in `main.py` restituisce tutti gli strumenti abilitati per ogni ciclo.

## 4. Difetto dimostrato nel feedback engine
File su main: [engine/feedback.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py).

Sul main corrente:
- il fingerprint del segnale usa symbol, direzione, timeframe, livelli e barra; non include provider, ticker risolto, mercato o scadenza;
- le candele successive vengono associate per symbol/timeframe, senza confronto di provider/ticker/mercato/scadenza;
- se una candela OHLC tocca contemporaneamente SL e TP, il codice controlla prima lo stop e registra `STOP`. L'ordine intrabar non è noto: secondo il protocollo PRAVDA deve risultare `ESITO NON VERIFICABILE`.

### PR #192 — correzione combinata
[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) è OPEN, non merged, non draft, mergeable=true. Compare diretto con main: 6 commit ahead / 0 behind; base SHA coincide con main corrente. I sei check associati al suo head risultano SUCCESS, ma le run sono del 5 novembre 2026, non un test di produzione e non una nuova run CI del cut-off.

La patch:
- aggiunge provider, ticker quotato, mercato, mese/scadenza e ATR al record/fingerprint;
- controlla ticker, mercato e identità del contratto futures;
- classifica il doppio tocco SL+TP nella stessa candela come `ESITO NON VERIFICABILE` senza R realizzato.

Lacuna ancora presente nella patch: `_market_contract_match()` non confronta `row.quote_provider` con il provider dello stato corrente. Il provider è nel fingerprint ma non nel matching delle candele. Il rilievo è già stato registrato nel commento [#6725075554](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6725075554); non è stato duplicato.

Altre PR rilevanti: [#202 persistenza journal](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202) e [#221 rimozione route FX](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221) restano draft/open; [#236](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/236) e [#237](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/237) sono draft per evidenza catalogo Trading 212, non provano accesso a quotazioni o broker.

## 5. Stato PR SPUTNIK e CI
- [PR #145 diagnostica quote Yahoo](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN, non merged; due run CI recenti #42505029428 e #42505029400 SUCCESS alle 17:27:10 UTC. Compare con main: 1 ahead / 1 behind.
- [PR #147 isolamento da GAGARIN](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN, non merged; run #42502648378 e #42502648241 SUCCESS alle 16:59:26 UTC. Compare: 1 ahead / 1 behind. Il main continua a eseguire il vecchio percorso handoff.
- [PR #148 anti-ripetizione](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN; compare 2 ahead / 23 behind.
- [PR #144 persistenza separata](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN; compare 1 ahead / 32 behind.

I test PR sono test di codice, non scansioni produttive né segnali di mercato.

## 6. Frequenza osservata vs cron
| Processo | Cron dichiarato | Ultime due run produttive consultate | Gap |
|---|---:|---|---:|
| SPUTNIK collector | ogni 5 min | #288 09:31:31 → #289 16:15:37 UTC | 6h44m06s |
| SPUTNIK polling | ogni 5 min | #49 09:16:25 → #50 16:05:42 UTC | 6h49m17s |
| GAGARIN monitor | ogni 15 min | #168 09:29:58 → #169 16:16:25 UTC | 6h46m27s |

Al cut-off, le ultime run produttive erano già ferme da circa 2h27–2h38. Nell'elenco recente delle Actions non compare una run schedule successiva; le run delle 16:59 e 17:27 sono test PR, non scansioni produttive. Il motivo dei gap non è dimostrato e non viene attribuito a un filtro orario.

Tra la run SPUTNIK #289 e il main attuale risultano quattro commit: due rapporti PRAVDA, aggiornamento del ledger e aggiornamento di `sputnik_state.json`; il confronto non mostra modifiche al codice applicativo in quel tratto. GAGARIN main coincide con lo SHA usato dal monitor #169.

## 7. Fonti e prossimo controllo
Fonti primarie consultate: Actions e log dei job linkati sopra; workflow `trump_tracker.yml`, `telegram-polling.yml`, `gagarin-monitor.yml`; ledger PRAVDA; file journal/posizione; `commodities/universe.py`; `engine/feedback.py`; metadati, diff, compare e commenti PR.

Prossimo controllo:
1. verificare che i cron generino nuove run produttive, distinguendole dai test PR;
2. alla riapertura dei mercati, controllare timestamp, età, provider, ticker risolto, mercato e scadenza delle nuove quotazioni;
3. verificare che ogni nuovo record includa entry/SL/TP/ATR e timestamp generazione/invio;
4. riconciliare i file legacy Heating Oil/WTI con lo stato PAPER corrente senza considerarli fill in assenza di prova;
5. verificare eventuale recepimento del confronto provider nella PR #192 e l'integrazione effettiva delle correzioni;
6. valutare SL prima, TP prima o `ESITO NON VERIFICABILE` solo con prezzi successivi dello stesso identico strumento e contratto.

**Conclusione:** nessuna nuova operazione verificabile. Il principale blocco è la combinazione di quote stale/mercati chiusi, scansioni non regolari, journal privato non persistito nel job corrente e outcome engine non ancora corretto su main. Nessun backtest o risultato di performance viene dichiarato. PAPER ONLY.
