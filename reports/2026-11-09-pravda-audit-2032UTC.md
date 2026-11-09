# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
## Controllo #19 — 9 novembre 2026, 21:32 CET (20:32 UTC)

## Esito sintetico

Verifica eseguita tramite GitHub REST: Actions filtrate per branch main ed evento schedule, log integrali dei job, file correnti di main, journal pubblici, metadata delle PR e ledger PRAVDA.

**Nessun nuovo segnale operativo rispetto al controllo #18. Il ledger resta a 106 record, 106 firme uniche, zero duplicati. Nessun fill, SL o TP verificato.**

Novità e precisazioni:
- SPUTNIK: ultimo collector schedule ancora #295, 16:02:05–16:02:23 UTC. Il run #294 delle 15:33 era PUSH. Nessun collector schedule successivo compare nella query GitHub per main/schedule.
- GAGARIN: ultimo monitor schedule ancora #173, 16:52:38–16:53:01 UTC. Nessun monitor schedule successivo compare nella query main/schedule.
- GAGARIN main è ora a 631727912b3a2022379a4460f4b6f756eba6991f. Il nuovo codice Render configura un loop di mercato ogni 5 minuti, ma la GitHub Action gagarin-monitor.yml resta a 15 minuti e MONITOR_INTERVAL_MINUTES=15. Non è stata verificata l'esecuzione/deploy Render.
- Il nuovo universo main contiene 13 strumenti; l'ultima scansione #173 precede i commit che hanno attivato i 13 strumenti e ne analizza ancora 8 commodity + EUR/USD e GBP/USD ausiliari. Nessuna scansione produttiva ha ancora verificato il nuovo universo.
- Il log SPUTNIK #295 conferma SEC HTTP 403, White House RSS HTTPError e un finding pubblico. Il log dice GAGARIN forwarding=0ms, ma non prova un handoff riuscito. La stringa “handoff disabled” compare nella sezione dei test unitari, non viene usata come prova del runtime.
- GAGARIN #173: tutte le 8 commodity sono STALE; EUR/USD e GBP/USD sono LIVE ma ausiliari. Zero entry e zero feedback.
- L'outcome engine su main continua a non conservare l'identità completa della quotazione e valuta STOP prima di TP. La PR #192 migliora il controllo del contratto e il doppio tocco, ma non confronta esplicitamente il provider.

Nessuna modifica applicativa, nessun merge/deploy, nessun ordine reale. PAPER ONLY.

## 1. Registro storico

Ledger letto dal branch precedente pravda/audit-2026-11-09-2007UTC e verificato con parser CSV:

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

SHA ledger: 41a1339c2047c86ad9026ab131d9a8015d0cd710. Nessuna riga aggiunta: nessun nuovo segnale è emerso.

Win rate, Average R e Total R: N/D. I record non sono tutti trade; NOT_EXECUTED, WATCH e PENDING non costituiscono fill.

Ledger: reports/pravda-signal-ledger-2026-11-09.csv (ereditato senza modifiche dal branch precedente).

## 2. SPUTNIK — Actions e fonti

Main SHA: 6c3095f1534550b0b4e77170f1428db833253c05.

Ultime esecuzioni schedule su main:
- Collector #295: 16:02:05–16:02:23 UTC, SUCCESS.
- Telegram polling #54: 15:43:25–15:43:37 UTC, SUCCESS.
- Daily summary #12: 14:48:35–14:48:43 UTC, SUCCESS.

Al cut-off 20:32:41 UTC:
- gap collector: 4 h 30 min 36 s;
- gap polling: 4 h 49 min 16 s;
- gap daily summary: 5 h 44 min 06 s.

Run #294 alle 15:33:04 UTC è PUSH, non schedule. Le CI della PR #156 non sono scansioni produttive.

Fonti:
- SPUTNIK #295: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42650624196
- SPUTNIK #294: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42645788987
- Polling #54: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42647513138
- Daily summary #12: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42638308297

### 2.1 Run #295 — raccolta e notifica

Il log runtime, distinto dalla sezione dei test unitari, riporta:
- SEC HTTP 403; cooldown 21.600 secondi; filing 0; transazioni 0.
- White House RSS endpoint https://www.whitehouse.gov/feed/ restituisce HTTPError.
- Scansione intelligence pubblica: 6.665 ms, un finding.
- GAGARIN forwarding: 0 ms; il log non conferma la consegna del catalizzatore a GAGARIN.
- Messaggi Telegram #752 e #753: API acceptance confermata, rispettivamente 590 ms e 608 ms. È ACK dell'API, non prova di visualizzazione sul dispositivo.

Precisazione metodologica: il messaggio “GAGARIN handoff disabled” e le risposte Telegram “delivery NOT confirmed” compaiono nella sezione dei test unitari eseguiti prima del runtime. Non vengono attribuiti automaticamente alla produzione. Il runtime registra solo forwarding=0ms, senza una prova positiva di handoff.

### 2.2 GOLD SHORT — #751, run #294

- Generazione/log card: 2026-11-09 15:33:13.053057 UTC.
- Telegram API ACK: 15:33:13.054567 UTC; round-trip 395 ms.
- Messaggio #750: analisi preliminare associata, non conteggiata separatamente.
- Strumento logico: GOLD.
- Ticker contrattuale: non risolto.
- Mercato: card titolata CFD, testo riferito a future continuo front-month.
- Scadenza: sconosciuta.
- Provider e timestamp/età quotazione: non esposti.
- Direzione: SHORT.
- Entry 4125.6001; SL 4128.3859; TP1 4122.8143; TP2 4120.0285; ATR 1.8572.
- D-L-A NEUTRAL / NO_DIRECTION; stato EARLY_SETUP / NOT_EXECUTED; score 100.
- NARWHAL non configurato; la card avverte di non usare i livelli.

Classificazione PRAVDA: NON_TRADE. Nessun outcome valutabile.

Fonte: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42645788987

### 2.3 GOLD LONG — #753, run #295

- Generazione/log card: 2026-11-09 16:02:18.5846468 UTC.
- Telegram API ACK: 16:02:18.5856255 UTC; round-trip 608 ms.
- Messaggio #752: analisi preliminare associata, non conteggiata separatamente.
- Strumento logico: GOLD.
- Ticker contrattuale: non risolto.
- Mercato: card CFD, testo riferito a future continuo front-month.
- Scadenza, provider e timestamp/età quotazione: assenti.
- Direzione: LONG; tecnica LONG (ALIGNS); D-L-A LONG (ALIGNS).
- Entry 4129.2998; SL 4126.9106; TP1 4131.689; TP2 4134.0781; ATR 1.5928.
- Stato EARLY_SETUP / NOT_EXECUTED; score 100.
- NARWHAL NOT_CONFIGURED; SPOT_VS_FUTURES_BASIS_CHECK_INDEPENDENCE_UNVERIFIED; indipendenza SILV non verificata.
- La card avverte: front-month continuo, scadenza e indipendenza upstream non verificate; non usare per entry/SL/TP.

Classificazione PRAVDA: NON_TRADE. Nessun outcome valutabile. Il livello non può essere confrontato con spot o con un future di scadenza diversa.

Fonte: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42650624196

### 2.4 PR SPUTNIK #156 — cronologia intelligence

Main trump_tracker.py conserva ancora tre accessi values()[-30:] (righe correnti circa 1627, 1643 e 1818). La cronologia è newest-first; il slicing seleziona la coda più vecchia. Il branch della PR ordina per detected_at e seleziona i 30 record più recenti.

PR #156 è OPEN, non integrata. Il branch rimuove i tre slicing errati; i due check CI osservati sono SUCCESS. Il difetto resta su main fino all'integrazione.

PR: https://github.com/andreameloni1984-sys/trump-trucker/pull/156

## 3. GAGARIN — Actions e configurazione corrente

Main SHA: 631727912b3a2022379a4460f4b6f756eba6991f.

Ultimo monitor schedule:
- #173: 16:52:38–16:53:01 UTC, SUCCESS, commit 50b25a80.
- #172: 06:34:18 UTC.
- Gap #172→#173: 10 h 18 min 20 s.
- Al cut-off 20:32:41 UTC il gap da #173 è 3 h 40 min 03 s.
- Nessun monitor schedule successivo a #173 nella query main/schedule.

Run #42688792974 alle 20:00:37 UTC è un push test/smoke, non una scansione di mercato. Il commit 631727 è stato creato alle 20:00:34 UTC; non esiste una scansione produttiva successiva che verifichi il nuovo codice.

Fonti:
- Monitor #173: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42659137635
- Push smoke #42688792974: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42688792974

### 3.1 Run #173 — dati e risultato

La run #173 ha usato il commit 50b25a80, precedente ai commit che hanno attivato il nuovo universo a 13 strumenti. Ha analizzato 8 commodity + EUR/USD e GBP/USD ausiliari.

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

EUR/USD BIQUOTE 176,2 s LIVE e GBP/USD BIQUOTE 176,9 s LIVE, ma entrambi ausiliari nel run #173.

Ambiente osservato:
- PAPER_TRADING_ONLY=1.
- DATABASE_URL vuota.
- soglie runtime 40/30/35, RR 2.5, max stop ATR 2.5.
- MONITOR_INTERVAL_MINUTES=15.
- NARWHAL_API_KEY vuota.

Risultato:
- Recorded entries: 0.
- Updated open outcomes: 0.
- New feedback signals: 0.
- New additional live forecasts: 0.
- signals=0, open=0, closed=0.

Messaggio #3734: API acceptance alle 16:52:57.447825 UTC, round-trip 556 ms. Il corpo non è conservato; strumento, ticker e direzione non attribuibili. Classificazione WATCH pre-alert / NON_TRADE.

### 3.2 Nuovo main: 13 strumenti e due cadenze diverse

Commit:
- b3bfb0df, 19:57:45 UTC: attiva 13 strumenti.
- 631727912, 20:00:34 UTC: rimuove il thread Invest AUTO e configura il loop market monitor nel Render runner a 5 minuti.

L'universo corrente in commodities/universe.py contiene:
- 8 commodity: Oro, Argento, Rame, WTI, Brent, Grano, Mais, Soia.
- EUR/USD, DAX, S&P 500, NVIDIA, Tesla.

Il telegram/render_runner.py configura position_monitor_loop con interval=5*60 e stampa “13 approved instruments”. È configurazione del codice; non prova che il nuovo processo sia stato distribuito o sia attivo su Render.

La GitHub Action .github/workflows/gagarin-monitor.yml resta invece:
- cron */15 * * * *;
- MONITOR_INTERVAL_MINUTES=15.

Quindi il monitor GitHub Actions resta a 15 minuti; il loop Render è configurato a 5 minuti, ma il runtime/deploy Render non è stato verificato. Non confondere il push test delle 20:00 con una scansione produttiva.

### 3.3 Telegram polling

La run #20, 16:58:05–16:58:21 UTC, è FAILURE. Il log conferma HTTP 409: webhook attivo, polling getUpdates incompatibile con webhook. La PR #175 è OPEN/non integrata.

- Run #20: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42660005021
- PR #175: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175

## 4. Journal e feedback GAGARIN

File verificati su main:
- commodities_prediction_log.json: 981 record, SHA 86df1b3eb1923f2a310b0acde7ca8a7e176c63a2.
- Ultimo record: Benzina RBOB, 2026-09-15 15:45:04.462276 UTC.
- Status: 945 PENDING, 36 NEUTRALE.
- Action: 77 NON ENTRARE, 576 ATTENDERE, 15 SHORT — ASPETTARE CONFERMA, 292 LONG — ASPETTARE CONFERMA, 21 COMPRA ORA.
- Le 21 COMPRA ORA sono PENDING, non fill.
- commodities_monitor_state.json: timestamp 2026-09-17 03:44:02 UTC.
- commodities_direction_state.json: ultime osservazioni pubbliche risalgono al 17 settembre.
- gagarin_feedback.csv: 404/non presente.
- DATABASE_URL vuota nel run #173; nessun artifact Actions.
- paper_trade_log.csv contiene un WTI LEGACY_IMPORT; data/paper_open.json contiene P0001 con gli stessi livelli. Sono lo stesso ticket legacy, non due trade.
- position.json contiene una vecchia posizione Heating Oil LONG del 15 settembre.

Il WTI legacy non ha prova di fill e P&L è null. La posizione Heating Oil non ha una catena di fill/quote/contratto/outcome. La persistenza durevole cross-run non è dimostrata.

## 5. Outcome engine — main e PR #192

### Main

engine/feedback.py su main:
- FIELDS non contengono quote_provider, quote_symbol, market_type, contract_month o contract_expiry.
- update_open_outcomes abbina per symbol/timeframe, con fallback per symbol singolo.
- controlla stop_hit prima di hit_targets.
- una candela che tocca SL e TP può essere registrata STOP.

Il main non è certificabile per statistiche di performance.

### PR #192

Il branch PR aggiunge campi provider, ticker quotato, market type, contract month e expiry; il matching verifica ticker, mercato e contratto future. La funzione update_open_outcomes sul branch gestisce il doppio tocco SL+TP nella stessa candela come ESITO NON VERIFICABILE.

Rimane però una lacuna dimostrata: _market_contract_match non confronta esplicitamente row.quote_provider con il provider della serie successiva, nonostante la docstring dichiari matching del provider. Inoltre la docstring iniziale del modulo continua a dire che il doppio tocco viene risolto come STOP, in contrasto con la funzione aggiornata.

PR #192 è OPEN e non integrata. La correzione non è quindi attiva su main.

PR: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192

### Persistenza PR #202

PR #202 è DRAFT. Il workflow main dichiara che la persistenza privata sarà riattivata dopo deploy/verifica D1, mentre la PR propone PostgreSQL. DATABASE_URL è vuota nel run #173; il feedback CSV non è presente. Nessuna prova di backend durevole.

PR: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202

## 6. Perimetro GAGARIN — PR #244

Main ha 13 strumenti attivi. PR #244 propone otto commodity, è DRAFT, mergeable=false, base SHA 5f523c6 (precedente all'attuale main) e i sette check CI osservati sono FAILURE. Non considero il perimetro a otto applicato o validato.

PR: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/244

## 7. Outcome dei segnali esaminati

- GOLD SHORT #751: NOT_EXECUTED, ticker/scadenza/provider mancanti → NON_TRADE; nessun esito.
- GOLD LONG #753: NOT_EXECUTED, future continuo senza scadenza/provider/timestamp → NON_TRADE; nessun esito.
- GAGARIN #3734: WATCH pre-alert senza corpo → non attribuibile; NON_TRADE.
- GAGARIN #173: nessuna entrata autorizzata e nessun nuovo feedback.

Non sono state reperite candele successive dello stesso identico strumento e contratto per i due GOLD. Non vengono usati prezzi spot, future continui o scadenze differenti per inferire SL/TP.

Statistiche su campioni verificabili: nessun fill verificato; win rate e R multipli N/D. Nessun backtest inventato.

## 8. Fonti e limiti

Fonti consultate:
- GitHub Actions API filtrata per main/event=schedule e main/event=push sui due repository.
- Log integrali dei job SPUTNIK #295, GAGARIN #173 e GAGARIN Telegram Polling #20.
- File main: trump_tracker.py, gagarin-monitor.yml, commodities/universe.py, telegram/render_runner.py, cloud_monitor.py, engine/feedback.py, journal JSON/CSV disponibili.
- PR #156, #175, #192, #202 e #244.
- Ledger PRAVDA cumulativo.

Limiti:
- Nessun artifact Actions per #295 e #173.
- Nessuna serie OHLC omogenea identificata per i contratti GOLD.
- Nessun provider/timestamp/expiry nelle card GOLD.
- Nessun corpo conservato per WATCH #3734.
- Nessun journal feedback durevole verificato.
- Nessuna verifica del runtime/deploy Render.
- Nessun accesso a Trading212 dichiarato.
- Telegram API ACK non equivale a prova di visualizzazione sul dispositivo.

## 9. Prossimo controllo

1. Verificare il prossimo collector schedule SPUTNIK e il prossimo monitor schedule GAGARIN.
2. Verificare una scansione GAGARIN sul main 631727, con il nuovo universo a 13 strumenti.
3. Distinguere il loop Render 5m dal workflow GitHub 15m.
4. Verificare quote fresche con timestamp assoluto, ticker, provider, mercato e scadenza.
5. Verificare l'esito del fix Telegram 409.
6. Completare il confronto esplicito del provider nella PR #192 e riallineare il branch al main.
7. Dimostrare la persistenza durevole del journal.
8. Valutare SL/TP soltanto su candele successive dello stesso identico strumento e contratto.

PAPER ONLY. Nessuna modifica a codice, strategia, filtri, punteggi, soglie o rischio; nessun merge/deploy, ordine reale, modifica secret o Render; nessun servizio a pagamento.
