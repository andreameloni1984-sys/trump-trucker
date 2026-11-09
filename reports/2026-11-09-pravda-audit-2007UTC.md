# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
## Controllo #18 — 9 novembre 2026, 21:07 CET (20:07 UTC)

## Esito sintetico

Audit eseguito sui run GitHub Actions filtrati per evento `schedule`, sui log dei job, sui file correnti di `main`, sui journal pubblici e sulle PR aperte.

**Nessun nuovo segnale operativo è emerso dopo SPUTNIK #295 e GAGARIN #173. Il ledger resta invariato: 106 record, 106 firme uniche, zero duplicati. Nessun fill, SL o TP è verificato.**

Novità principali:
- SPUTNIK: l'ultimo collector schedulato resta #295 delle 16:02:05 UTC; il successivo run #294 delle 15:33 era PUSH, non schedule. Il fix di selezione degli ultimi item intelligence è nella PR #156, con due CI SUCCESS, ma non è integrato. Su main restano tre accessi `values()[-30:]` che selezionano la coda più vecchia della cronologia newest-first.
- GAGARIN: l'ultimo monitor schedulato resta #173 delle 16:52:38 UTC. Il push main delle 20:00 ha eseguito test e smoke test, non una scansione di mercato.
- GAGARIN: main è ora a `631727912b3a2022379a4460f4b6f756eba6991f`. Il codice Render configura il position monitor a 5 minuti e rimuove il thread Invest AUTO, ma la GitHub Action `gagarin-monitor.yml` conserva cron 15 minuti e `MONITOR_INTERVAL_MINUTES=15`. Il deploy/runtime Render non è stato verificato.
- GAGARIN: main contiene 13 strumenti abilitati (8 commodity + EUR/USD, DAX, S&P 500, NVIDIA e Tesla). La PR #244 propone 8 commodity, ma è DRAFT e i sette workflow CI osservati sono FAILURE.
- GAGARIN: il modulo diagnostico intraday della PR #245 è già presente su main con lo stesso blob SHA e viene chiamato da `engine/gagarin.py`; la PR resta comunque OPEN/DRAFT.
- Il journal GAGARIN non è durevole: DATABASE_URL vuota nel run #173, nessun artifact, feedback CSV 404 e prediction log fermo al 15 settembre.
- Il motore outcome su main non conserva l'identità completa della quotazione e può classificare STOP una candela che tocca anche TP.

Nessuna modifica applicativa, nessun merge/deploy, nessun ordine reale. PAPER ONLY.

## 1. Registro storico PRAVDA

Ledger letto dal branch precedente `pravda/audit-2026-11-09-1823UTC`.

- Record: 106
- SPUTNIK: 50
- GAGARIN: 56
- Firme uniche: 106
- Source ID unici: 106
- Duplicati firma: 0
- Duplicati source ID: 0
- NON_TRADE: 77
- ESITO_NON_VERIFICABILE: 29
- Fill verificati: 0
- SL verificati: 0
- TP verificati: 0

SHA ledger invariato: `41a1339c2047c86ad9026ab131d9a8015d0cd710`.

Nessuna riga aggiunta. I messaggi preliminari #750/#752 restano associati alle rispettive card #751/#753 e non sono contati come segnali autonomi. Il WATCH GAGARIN #3734 resta non attribuibile e non operativo.

Win rate, Average R e Total R: N/D. Non esiste un campione di fill con outcome verificato.

Ledger: [CSV cumulativo — 106 record](https://github.com/andreameloni1984-sys/trump-trucker/blob/pravda/audit-2026-11-09-1823UTC/reports/pravda-signal-ledger-2026-11-09.csv)

## 2. SPUTNIK — Actions e continuità

Repository main SHA: `6c3095f1534550b0b4e77170f1428db833253c05`.

Ultimi run schedule restituiti dall'endpoint GitHub Actions:
- Collector #295: 2026-11-09 16:02:05–16:02:23 UTC, SUCCESS.
- Telegram polling #54: 15:43:25–15:43:37 UTC, SUCCESS.
- Daily summary #12: 14:48:35–14:48:43 UTC, SUCCESS.
- Collector #294: 15:33:04–15:33:17 UTC, evento PUSH, non schedule.

Al cut-off 20:07 UTC:
- gap collector dal run schedule #295: 4 h 05 min 07 s;
- gap polling dal run #54: 4 h 23 min 47 s;
- gap daily summary dal run #12: 5 h 18 min 37 s.

Le CI della PR #156 alle 18:38 UTC non sono run produttivi. Non compare una nuova scansione schedule successiva a #295 nell'elenco `event=schedule` consultato.

Fonti:
- [SPUTNIK #295](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42650624196)
- [SPUTNIK #294](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42645788987)
- [Polling #54](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42647513138)
- [Daily summary #12](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42638308297)

### 2.1 GOLD SHORT — messaggio #751, run #294

- Generazione/card nel log: 2026-11-09 15:33:13.0531509 UTC.
- Telegram API ACK nel log: 15:33:13.0545671 UTC; round-trip dichiarato dal client: 395 ms.
- Messaggio preliminare #750: stesso run, card compagna, non conteggiata separatamente.
- Strumento logico: GOLD.
- Ticker contrattuale: non risolto.
- Mercato: card titolata CFD, testo dichiara future continuo front-month.
- Scadenza: sconosciuta.
- Provider: non esposto.
- Timestamp/età quotazione: assenti.
- Direzione: SHORT.
- Stato: EARLY_SETUP / NOT_EXECUTED.
- Score: 100/100, non è prova di validità operativa.
- Entry: 4125.6001.
- SL: 4128.3859.
- TP1: 4122.8143.
- TP2: 4120.0285.
- ATR: 1.8572.
- D-L-A: NEUTRAL / NO_DIRECTION.
- NARWHAL: NOT_CONFIGURED.
- La card dichiara: front-month continuo, scadenza esatta e indipendenza upstream non verificate; non usare per entry/SL/TP.
- Controllo SPOT/FUTURES: indipendenza non verificata.

Fonte: [SPUTNIK #294 — log Actions](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42645788987).

Classificazione PRAVDA: **NON_TRADE**. Nessun outcome valutabile.

### 2.2 GOLD LONG — messaggio #753, run #295

- Generazione/card nel log: 2026-11-09 16:02:18.5846468 UTC.
- Telegram API ACK nel log: 16:02:18.5856255 UTC; round-trip dichiarato dal client: 608 ms.
- Messaggio preliminare #752: stesso run, card compagna, non conteggiata separatamente.
- Strumento logico: GOLD.
- Ticker contrattuale: non risolto.
- Mercato: card titolata CFD, testo dichiara future continuo front-month.
- Scadenza: sconosciuta.
- Provider: non esposto.
- Timestamp/età quotazione: assenti.
- Direzione: LONG.
- Stato: EARLY_SETUP / NOT_EXECUTED.
- Score: 100/100, non è prova di validità operativa.
- Entry: 4129.2998.
- SL: 4126.9106.
- TP1: 4131.689.
- TP2: 4134.0781.
- ATR: 1.5928.
- D-L-A: LONG / ALIGNS.
- NARWHAL: NOT_CONFIGURED.
- La card dichiara: front-month continuo, scadenza esatta e indipendenza upstream non verificate; non usare per entry/SL/TP.
- Controllo SPOT/FUTURES: indipendenza non verificata.

Fonte: [SPUTNIK #295 — log Actions](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42650624196).

Classificazione PRAVDA: **NON_TRADE**. Nessun outcome valutabile.

### 2.3 Correzione SPUTNIK #156 — selezione cronologia

Main `trump_tracker.py` conserva ancora `values()[-30:]` nei tre punti delle righe 1627, 1643 e 1818. La PR #156 documenta che `intelligence_history` è newest-first; dopo il limite di 500 record, la coda selezionata è quindi quella più vecchia.

La PR aggiunge ordinamento esplicito per `detected_at` decrescente e seleziona i 30 item più recenti. I due workflow PR #42675822129 e #42675822281 risultano SUCCESS sul head `9afe7077`. La PR resta OPEN, non integrata; main continua a usare il vecchio slicing.

- [PR #156](https://github.com/andreameloni1984-sys/trump-trucker/pull/156)
- [CI ranking #42675822281](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42675822281)
- [CI item intelligence #42675822129](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42675822129)

Commento audit registrato: [#6750288615](https://github.com/andreameloni1984-sys/trump-trucker/pull/156#issuecomment-6750288615).

### 2.4 Handoff e persistenza

Nel run #295 il test/log indica forwarding SPUTNIK→GAGARIN disabilitato per URL/API key assenti. Non viene trattato come errore di mercato; non esiste prova di un feed catalizzatori condiviso. Lo stato SPUTNIK ha invece un commit di persistenza GitHub riuscito: [commit 6c3095f](https://github.com/andreameloni1984-sys/trump-trucker/commit/6c3095f1534550b0b4e77170f1428db833253c05).

## 3. GAGARIN — Actions e scansioni

Repository main corrente: `631727912b3a2022379a4460f4b6f756eba6991f`.

Ultimo monitor schedule verificato:
- #173, 2026-11-09 16:52:38–16:53:01 UTC, SUCCESS.
- La run precedente #172 era alle 06:34:18 UTC: gap #172→#173 di 10 h 18 min 20 s.
- Al cut-off 20:07 UTC il gap dall'avvio di #173 è 3 h 14 min 34 s.
- Non compare un successivo monitor schedule nella query `event=schedule`.

Il push main #42688792974 alle 20:00:37 UTC non è un monitor di mercato: job `test`, 27 test passati, smoke test `python -m soyuz_gagarin.main` con output `PAPER_WATCH / ASSET_NOT_IN_UNIVERSE`. Le altre run main di test #42688793113, #42688793217, #42688793593 e #42688793102 sono CI, non scansioni produttive.

Fonti:
- [GAGARIN monitor #173](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42659137635)
- [GAGARIN main smoke #42688792974](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42688792974)
- [GAGARIN news tests #42688793593](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42688793593)

### 3.1 Run #173 — quotazioni e stato

La run #173 usava il commit `50b25a80` e ha analizzato 10 strumenti (8 commodity + EUR/USD e GBP/USD ausiliari). Età delle otto commodity:

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

EUR/USD BIQUOTE 176,2 s LIVE e GBP/USD BIQUOTE 176,9 s LIVE, ma non erano ingressi operativi.

- Recorded entries: 0.
- New feedback signals: 0.
- New additional live forecasts: 0.
- Updated open outcomes: 0.
- signals=0, open=0, closed=0.

Messaggio #3734: API ACK alle 16:52:57.447 UTC, round-trip 556 ms; il corpo non è conservato. Strumento, ticker, direzione e livelli non attribuibili. Classificazione: WATCH pre-alert / NON_TRADE.

### 3.2 Modifiche recenti main e discrepanza di cadenza

Il commit main `631727912`:
- rimuove la funzione/thread Invest AUTO dal Render runner (diff di `telegram/render_runner.py`: 72 righe rimosse);
- configura nel codice `position_monitor_loop` con `interval = 5 * 60` e messaggio "13 approved instruments";
- dichiara nel research log monitor mercato a 5 minuti.

Ma `.github/workflows/gagarin-monitor.yml` su main conserva:
- cron `*/15 * * * *`;
- `MONITOR_INTERVAL_MINUTES=15`;
- commento che il monitor provider-heavy resta a 15m fino a verifica della capacità rate-limit.

Quindi i due runtime sono diversi: codice Render 5m, GitHub Actions 15m. Il deploy/runtime Render successivo non è stato verificato; non è stato selezionato alcun workspace Render e non è stata eseguita alcuna modifica.

### 3.3 Universo operativo su main e PR #244

`commodities/universe.py` su main contiene 13 strumenti:
- 8 commodity: Oro, Argento, Rame, WTI, Brent, Grano, Mais, Soia;
- EUR/USD, DAX, S&P 500, NVIDIA, Tesla.

`main.py` seleziona `enabled_commodities()`. Il monitor #173 è precedente al commit 631727 e non ha ancora verificato il nuovo universo a 13 strumenti.

La PR #244 propone di restringere tutti i percorsi alle otto commodity. È DRAFT/OPEN, basata su main SHA precedente `5f523c6f` (main corrente 63172791, 3 commit avanti) e i sette workflow PR del 18:15 UTC risultano FAILURE:
- #42672436065 Execution Layer;
- #42672435217 Telegram menu;
- #42672435296 Public Event Brain;
- #42672435798 NEWS alert;
- #42672435414 SOYUZ PAPER;
- #42672435706 commodity trade-plan;
- #42672435748 GAGARIN tests.

Non considero il perimetro a otto applicato o validato.

Commento audit registrato: [#6750290129](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/244#issuecomment-6750290129).

### 3.4 Indicatori intraday — PR #245 già presenti su main

Il file `engine/intraday_indicators.py` ha lo stesso blob SHA su main e sul branch PR: `8e803f1dbebb1ce13dc928db5cbefdfc57227ef9`. `engine/gagarin.py` su main chiama già `calculate_intraday_context` dopo `load_data`.

La PR #245 resta OPEN/DRAFT, ma cinque workflow PR risultano SUCCESS. Il codice main calcola EMA 10/50/200, Bollinger 20/2, VWAP proxy ancorato al giorno UTC e POC approssimato da istogramma volume. Il research log li definisce diagnostici, senza nuova via di segnale o cambi a soglie/rischio. Non è una prova di deploy o di risultato di trading.

- [PR #245](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/245)
- [CI GAGARIN tests #42684119806](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42684119806)
- [CI PAPER #42684119755](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42684119755)

Commento audit registrato: [#6750291376](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/245#issuecomment-6750291376).

### 3.5 Journal e feedback

Prediction log main:
- 981 record;
- 981 ID unici, zero duplicati;
- PENDING 945;
- NEUTRALE 36;
- nessun OPEN/CLOSED;
- ultimo record: `2026-09-15T15:45:04.462276+00:00`.

Distribuzione action nel prediction log:
- NON ENTRARE: 77;
- ATTENDERE: 576;
- SHORT — ASPETTARE CONFERMA: 15;
- LONG — ASPETTARE CONFERMA: 292;
- COMPRA ORA: 21 (tutte PENDING).

Questi sono forecast storici, non trade eseguiti.

Altri artefatti:
- `paper_trade_log.csv`: una riga WTI `LEGACY_IMPORT`, senza prova di fill/outcome;
- `data/paper_open.json`: WTI P0001 OPEN, stessi livelli legacy;
- `position.json`: Heating Oil LONG del 15 settembre, senza outcome verificato;
- `gagarin_feedback.csv`: 404;
- `DATABASE_URL`: vuota nel run #173;
- artifact Actions del run #173: nessuno.

La persistenza durevole non è dimostrata. Non conto WTI P0001 e WTI LEGACY_IMPORT come due operazioni distinte: si riferiscono allo stesso ticket legacy.

### 3.6 Telegram polling 409

Run #20 [#42660005021](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42660005021), alle 16:58:05 UTC:
- token validation: SUCCESS;
- Telegram diagnostic: SUCCESS;
- getUpdates: API 409, webhook già attivo;
- polling job: FAILURE.

PR #175 contiene la gestione `WebhookActiveError`, ma resta OPEN/non integrata. Il confronto tra head PR `7bb944f3` e main `63172791` è diverged: 7 commit ahead, 1 behind. La correzione non è quindi presente su main.

### 3.7 Outcome engine su main

Blob main `engine/feedback.py`: `41bec9bfab031c8dbf71121cd69d0e9b4c4f663f`.

Il campo FIELDS non conserva `quote_provider`, `quote_symbol`, `market_type`, `contract_month` o `contract_expiry`. Il matching successivo usa `(symbol, timeframe)` e fallback per symbol singolo. Il codice valuta `stop_hit` prima di `hit_targets`; una candela che tocca SL e TP può essere classificata STOP.

PR #192 propone matching contrattuale e `ESITO NON VERIFICABILE` per lo stesso-bar SL/TP, ma il suo head `295dba4b` è diverged rispetto a main: 10 commit ahead, 6 behind. La PR non è integrata e non certifica il main corrente.

Commento audit registrato: [#6750290763](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6750290763).

## 4. Esiti e statistiche

Segnali/candidate operativi esaminati:
- SPUTNIK GOLD SHORT #751: NOT_EXECUTED, NON_TRADE.
- SPUTNIK GOLD LONG #753: NOT_EXECUTED, NON_TRADE.
- GAGARIN #3734: WATCH pre-alert, corpo non conservato, strumento non attribuibile, NON_TRADE.
- GAGARIN main smoke test #42688792974: test-only, `ASSET_NOT_IN_UNIVERSE`, non è un segnale.

Non sono state reperite candele/prezzi successivi dello stesso ticker contrattuale, mercato, scadenza e provider per i due GOLD. Le card dichiarano future continuo front-month senza scadenza esatta e provider/timestamp mancanti. Pertanto non è possibile valutare SL prima, TP prima o livello già superato: **ESITO NON VERIFICABILE** per i livelli, mentre lo stato operativo resta NOT_EXECUTED/NON_TRADE.

Statistiche su campione verificabile:
- Fill verificati: 0.
- SL verificati: 0.
- TP verificati: 0.
- Win rate: N/D.
- Average R: N/D.
- Total R: N/D.

Non è stato inventato alcun backtest.

## 5. Segnalazioni audit registrate

- SPUTNIK PR #156: commento #6750288615 — selezione cronologia ancora errata su main, fix CI-green ma non integrato.
- GAGARIN issue #186: commento #6750289196 — codice Render 5m vs GitHub Actions 15m e assenza di nuova scan.
- GAGARIN PR #244: commento #6750290129 — universo main 13 vs PR otto commodity, CI fallite e branch non aggiornato.
- GAGARIN PR #192: commento #6750290763 — identità provider/contratto e doppio tocco ancora difettosi su main.
- GAGARIN PR #245: commento #6750291376 — modulo indicatori già presente su main nonostante PR aperta.

## 6. Fonti consultate

GitHub:
- run list `event=schedule` dei due repository;
- job logs SPUTNIK #294/#295;
- job log GAGARIN #173, polling #20 e smoke #42688792974;
- artifacts del run #173 (lista vuota);
- file main: `trump_tracker.py`, `commodities/universe.py`, `main.py`, `engine/gagarin.py`, `engine/feedback.py`, `engine/intraday_indicators.py`, `telegram/render_runner.py`, `.github/workflows/gagarin-monitor.yml`, `.github/workflows/soyuz.yml`, `GAGARIN_RESEARCH_LOG.md`;
- PR #156, #175, #192, #225, #244, #245 e relativi CI/diff;
- prediction log, paper_trade_log.csv, paper_open.json e position.json.

Limitazioni:
- nessuna fonte di prezzo/candele con identità contrattuale esatta per i due GOLD;
- nessun artifact monitor GAGARIN #173;
- nessun feedback CSV o storage durevole verificato;
- nessuna verifica indipendente di deployment/log Render (nessun workspace selezionato; nessuna modifica eseguita);
- ACK Telegram prova soltanto l'accettazione API, non la visualizzazione sul dispositivo;
- nessun accesso a Trading 212 dichiarato.

## 7. Prossimo controllo

1. Verificare la prossima run schedule SPUTNIK e il fix #156 solo dopo eventuale integrazione.
2. Verificare una nuova run schedule GAGARIN dopo il commit 631727; distinguere monitor Render 5m e GitHub Actions 15m.
3. Verificare il perimetro effettivo: 13 strumenti su main contro otto commodity nella PR #244.
4. Controllare le quotazioni con provider, ticker, mercato, timestamp assoluto e scadenza.
5. Dimostrare la persistenza journal e feedback.
6. Completare matching provider/contratto e gestione same-candle nella PR #192.
7. Verificare gestione webhook 409 nella PR #175.
8. Valutare SL/TP solo con candele successive dello stesso identico strumento e contratto.

**PRAVDA — PAPER ONLY. Nessuna modifica al codice applicativo, strategia, filtri, punteggi, soglie o rischio. Nessun merge, deploy, ordine reale, modifica a secret o Render.**
