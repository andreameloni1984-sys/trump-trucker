# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off:** 2026-11-07 19:54:44 UTC (20:54:44 Europe/Rome)  
**Modalità:** PAPER ONLY. Verifica in sola lettura; questo commit aggiunge soltanto il rapporto, non codice dei bot.

## 1. Sintesi

Ultimi monitor di mercato verificati direttamente in questa sessione:

| Bot | Run | Inizio UTC | Fine UTC | Età dal termine al cut-off | Stato |
|---|---:|---:|---:|---:|---|
| SPUTNIK | [#42388887315](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42388887315) | 15:57:48 | 15:58:04 | 3h56m40s | SUCCESS |
| GAGARIN | [#42386803148](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42386803148) | 15:31:37 | 15:31:58 | 4h22m46s | SUCCESS |

Ho riletto job e log e verificato che entrambi i run non hanno artifact Actions. La ricerca di report e artefatti disponibili non ha restituito monitor di mercato successivi. **Limite:** in questa sessione non è disponibile un endpoint per enumerare integralmente la cronologia Actions recente; non certifico quindi l'assenza assoluta di run successivi. Le età si riferiscono agli ultimi run che ho potuto verificare direttamente.

Il 7 novembre è sabato; GAGARIN ha dichiarato MARKET_CLOSED e quotazioni stale. Non ho richiesto quotazioni correnti fuori sessione né attribuito outcome a candele non identificabili.

## 2. SPUTNIK — run #42388887315

### Raccolta e catalizzatori
- SEC: HTTP 403, cooldown 21.600 secondi; 0 filing.
- White House RSS: HTTPError; operazioni documentate: 0.
- Intelligence pubblica: un finding TRUTH_ARCHIVE, ID `df6c3173377e2a283c05395c`.
- Il finding punta alla homepage generale dell'archivio, senza singolo post, titolo o timestamp individuale. È `PUBLIC_SOURCE_TEXT_PAGE_LEVEL`, classificato per analogia storica: non prova un catalizzatore commodity individuale e datato.
- Handoff verso GAGARIN disabilitato per assenza di configurazione cloud API; NARWHAL non configurato.

### GOLD — messaggi #721 e #722
- Generazione: 15:57:59.5632975 UTC; ultimo ACK API: 15:57:59.5658054 UTC.
- Telegram API: #721 confermato in 738 ms; #722 in 485 ms.
- Strumento logico GOLD; mapping configurato GC=F; mercato dichiarato futures continuous front-month.
- Ticker runtime, provider effettivo, timestamp/età quotazione e scadenza esatta non esposti.
- Bias NEUTRAL; tecnica 5m UNAVAILABLE; news alignment NO_DIRECTIONAL_NEWS.
- Score 70/100; WATCH / NO_DIRECTION; stato NOT_EXECUTED.
- Entry, SL, TP e ATR assenti.

Il log vieta di usare il continuous front-month per livelli operativi perché scadenza e indipendenza upstream non sono verificate. Score 70 non equivale a validità operativa. Nessun fill e nessuna sequenza di candele dello stesso contratto verificabili. L'ACK prova accettazione API, non visualizzazione sul dispositivo. Il message_id 731 compare nei test della run, non è un messaggio produttivo.

### Polling, riepilogo e persistenza
- Polling SPUTNIK [#42387284361](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42387284361), 15:37:31 UTC: SUCCESS, `Pending updates: 0`; è polling, non scansione.
- Daily Summary [#42371347665](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42371347665): cron 06:00 UTC, avvio 12:11:08 UTC, ritardo osservato 6h11m08s. API ha confermato message_id=720 alle 12:11:16.8618648 UTC. Corpo non conservato; nessuno strumento/direzione attribuito.
- Il workflow main mantiene `permissions: contents: write` e push di `sputnik_state.json` su main; il run #42388887315 ha creato [commit efaa67a](https://github.com/andreameloni1984-sys/trump-trucker/commit/efaa67a227abf8cebfb5eff2b64ad60bece10506).
- [PR #144](https://github.com/andreameloni1984-sys/trump-trucker/pull/144), persistenza fuori da main: OPEN, non merged. I check CI riportati nel precedente audit sono passati, ma non dimostrano il ciclo runtime di scrittura/lettura del branch dedicato.
- [PR #148](https://github.com/andreameloni1984-sys/trump-trucker/pull/148), stop alle raccomandazioni ripetute senza nuovo catalizzatore item-level: OPEN, non merged; correzione non attiva su main.

## 3. GAGARIN — run #42386803148

### Runtime e quotazioni
- PAPER_TRADING_ONLY=1; MONITOR_INTERVAL_MINUTES=15; soglie loggate 40/30/35 e RR 2.5.
- DATABASE_URL vuoto; NARWHAL_API_KEY vuoto.
- Otto commodity MARKET_CLOSED e stale su Yahoo:
  - Soia, Grano, Mais: circa 73.013 secondi (20h17m).
  - Brent, WTI, Oro, Argento, Rame: circa 63.412 secondi (17h37m).
- EUR/USD e GBP/USD erano contesto ausiliario BiQuote, anch'essi stale.
- Ticker risolto, prezzo, timestamp puntuale, market type e scadenza non esposti: impossibile associare candele successive allo stesso identico contratto.

### Classifica e messaggio
Argento è l'unico candidato direzionale: LONG, probabilità 59, quality 49,5, confidence 32. È PAPER_WATCH e bloccato da LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, CONFIDENCE_FAIL e FINAL_CONFLUENCE_FAIL. Entry, SL, TP e ATR assenti; nessun ingresso autorizzato.

Telegram API ha confermato il board #3715 alle 15:31:54.641895 UTC, round-trip 489 ms. Il corpo non è conservato: non attribuisco il board ad Argento o ad altro strumento. ACK API non prova visualizzazione sul dispositivo.

Il run riporta Recorded entries=0, Updated open outcomes=0, New feedback signals=0, New additional live forecasts=0, signals=0/open=0/closed=0; win_rate e avg_R N/D.

### Journal, feedback e posizioni legacy
- `journal.csv`: 11 righe del 17 ottobre, tutte “nessun segnale”.
- `paper_trade_log.csv`: una posizione legacy WTI P0001, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55.
- `data/paper_open.json`: riporta lo stesso P0001; è un solo ticket duplicato tra due artefatti, non due trade.
- Nota: “Chiusura spot 6 ottobre 2026. Nessun esito.” Mancano fill, provider, timestamp quotazione, ticker esecutivo completo, market type e scadenza. La chiusura spot non prova l'esito di un futures.
- `position.json`: Heating Oil LONG, entry 4,8844, SL 4,5418, TP1 5,4473, TP2 5,6284, TP3 5,882; apertura 15 settembre 2026. Provider, quotazione, contratto e fill non documentati.
- `gagarin_feedback.csv`: 404, assente dal repository pubblico consultato.
- DATABASE_URL vuoto nel run: persistenza condivisa tra esecuzioni non dimostrata.

WTI P0001 e Heating Oil restano ESITO NON VERIFICABILE. Non ho confrontato spot, continuous futures o scadenze diverse.

### Prediction log e Telegram
`commodities_prediction_log.json`: 981 record, ultimo creato il 15 settembre 2026 alle 15:45:04 UTC; 945 PENDING, 36 NEUTRALE; operational_signal: 960 WAIT, 15 LONG, 6 record senza campo. Predizioni storiche, PENDING e LONG non provano fill.

- Polling GAGARIN [#42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549), 00:16:15 UTC: FAILURE, Telegram API 409 — webhook attivo, `getUpdates` non consentito.
- [PR #175](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175), gestione del conflitto webhook/polling: OPEN, non integrata.
- Daily Summary [#42374841686](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42374841686): avvio 12:58:56 UTC rispetto al cron 06:15 UTC, ritardo osservato 6h43m56s. Il workflow stampa “Summary sent” dopo una risposta HTTP ma non verifica `ok=true` né `result.message_id`: accettazione Telegram non dimostrata.
- [PR #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202), persistenza journal PostgreSQL: OPEN/DRAFT.
- [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192), identità contratto/outcome ambiguo: OPEN, non merged.
- [PR #222](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222), rimozione veto intraday `session_ok`: OPEN, non integrata; il body non dichiara test verdi.
- [PR #30](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/30), paniere commodity: OPEN/DRAFT; Argento è ancora nel runtime verificato.
- [PR #233](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/233), identità spot/no-expiry: OPEN/DRAFT; non abilita un feed né un accesso Trading 212.

## 4. Ledger PRAVDA e statistiche

CSV riletto e analizzato con parser che rispetta i campi quotati:
- File: [pravda-signal-ledger-2026-11-07.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-07.csv)
- Blob SHA: `f13f1a087561f08b32b0abc94f17c209175ad513`.
- Record 58: SPUTNIK 14, GAGARIN 44.
- Firme `audit_signature` uniche 58/58; `source_record_id` unici 58/58; duplicati 0.
- Outcome registrati: 29 ESITO_NON_VERIFICABILE, 29 NON_TRADE.
- Fill verificati 0; SL verificati 0; TP verificati 0.
- Alcune predizioni storiche contengono entry/SL/TP, ma non prova di esecuzione.
- Campione di trade con outcome verificabile: 0; win rate e Average R: N/D.

I record dei run #42388887315 e #42386803148 erano già presenti nel ledger. Nessuna nuova riga: nessun nuovo segnale operativo, fill o outcome distinto emerso dai log esaminati. Ledger invariato.

## 5. Difetti dimostrati e correzioni già esistenti
1. SPUTNIK scrive ancora lo stato su main; PR #144 propone il branch dedicato ma non è merged.
2. SPUTNIK può ripetere raccomandazioni senza nuovo catalizzatore item-level; PR #148 non è attiva.
3. GAGARIN non dimostra persistenza tra runner: DATABASE_URL vuoto, feedback CSV assente; PR #202 aperta.
4. Polling GAGARIN incontra il conflitto webhook 409; PR #175 aperta.
5. Outcome GAGARIN non certificabile senza identità completa provider/ticker/mercato/scadenza; PR #192 aperta.
6. Veto `session_ok` ancora su main secondo la correzione proposta da PR #222; PR non integrata.
7. Paniere main include ancora Argento; PR #30 non integrata.
8. Daily Summary GAGARIN non dimostra ACK Telegram e non conserva il corpo del messaggio.

## 6. Prossimo controllo
- Verificare la cronologia Actions completa quando l'elenco run è interrogabile, distinguendo monitor, polling, daily summary, fetch driver e CI.
- Alla riapertura dei mercati: provider, ticker risolto, timestamp/età, market type e scadenza esatta per ogni candidato.
- Conservare corpo/hash messaggio e ACK API con message_id; non dedurre la consegna sul dispositivo.
- Verificare persistenza SPUTNIK dopo eventuale integrazione autorizzata PR #144 e persistenza GAGARIN solo con backend effettivamente configurato.
- Valutare SL/TP solo dopo fill documentato e candele successive dello stesso provider, ticker, mercato e contratto. Se SL e TP sono nella stessa candela senza sequenza intrabar dimostrabile: ESITO NON VERIFICABILE.

## 7. Fonti consultate
- Actions: SPUTNIK [monitor #42388887315](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42388887315), [polling #42387284361](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42387284361), [daily summary #42371347665](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42371347665); GAGARIN [monitor #42386803148](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42386803148), [polling #42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549), [daily summary #42374841686](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42374841686).
- Workflow main: `.github/workflows/trump_tracker.yml`, `.github/workflows/gagarin-monitor.yml`, `.github/workflows/daily-summary.yml`.
- Artefatti GAGARIN: `journal.csv`, `paper_trade_log.csv`, `data/paper_open.json`, `position.json`, `commodities_prediction_log.json`; `gagarin_feedback.csv` assente.
- PR: SPUTNIK #144/#148; GAGARIN #175/#192/#202/#222/#233/#30.

**Integrità:** nessun backtest inventato; nessun trade dedotto da WATCH, PENDING, score o NOT_EXECUTED; nessun confronto spot/futures o tra scadenze diverse. Nessuna strategia, filtro, punteggio o rischio modificato. Nessun merge, deploy, rerun, ordine reale, modifica a Render o segreti. Nessun servizio a pagamento o accesso Trading212 dichiarato. PAPER ONLY.
