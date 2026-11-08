# PRAVDA — Audit indipendente SPUTNIK / GAGARIN

**Cut-off:** 8 novembre 2026, 03:34 UTC (04:34 Europe/Rome)  
**Perimetro:** sola verifica di repository, GitHub Actions, log, journal, feedback, ledger e PR. PAPER ONLY.

## Esito sintetico

Sono state esaminate le ultime scansioni di mercato direttamente recuperabili per entrambi i bot. Nessuna ha prodotto un trade con fill verificato. Non sono disponibili candele successive riferite allo stesso identico strumento e contratto con cui attribuire SL prima, TP prima o un esito positivo/negativo.

Il ledger è stato aggiornato con i due messaggi di produzione SPUTNIK #729 e #730. Il candidato Argento e il board Telegram GAGARIN #3718 erano già registrati e non sono stati duplicati.

| Indicatore ledger | Valore |
|---|---:|
| Record totali | **81** |
| SPUTNIK | 33 |
| GAGARIN | 48 |
| Firme audit uniche | 81 |
| Source ID unici | 81 |
| Duplicati | **0** |
| NON_TRADE | 52 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | **0** |
| SL/TP verificati | **0** |
| Win rate / Average R | N/D |

I 29 record non verificabili non sono 29 trade: comprendono soprattutto previsioni storiche PENDING e un ticket legacy senza prova di fill. Le 52 righe NON_TRADE sono osservazioni, messaggi, WATCH, intelligence o candidati bloccati. Non è stato calcolato alcun backtest.

## 1. SPUTNIK

### Ultimo monitor di mercato

[GitHub Actions #42439632866](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42439632866) — evento `schedule`, avvio 2026-11-08 02:41:59 UTC, conclusione 02:42:14 UTC, SUCCESS. Il job `sputnik` è riuscito; non sono stati pubblicati artifact Actions.

Log effettivo:
- SEC: HTTP 403, cooldown 21.600 secondi; 0 filing.
- White House RSS: HTTPError.
- Scansione intelligence pubblica: 0 findings.
- Forwarding GAGARIN: 0 ms; nessun catalizzatore inoltrato.
- GOLD: bias NEUTRAL, nessuna notizia direzionale, tecnica 5m UNAVAILABLE, decisione WATCH.
- Nessun prezzo con provenienza verificabile, entry, SL, TP o ATR.

### Messaggi Telegram di produzione

| ID | Generazione (log UTC) | ACK API (log UTC) | Contenuto | Classificazione PRAVDA |
|---|---|---|---|---|
| #729 | 02:42:09.8056950 | 02:42:09.8067022 | GOLD NEUTRAL; priorità catalizzatore 100/100; tecnica 5m indisponibile | NO_DIRECTION / NON_TRADE |
| #730 | 02:42:09.8067468 | 02:42:09.8078059 | GOLD CFD; NO_DIRECTION; NOT_EXECUTED; score 100 | NON_TRADE |

Entrambi hanno un ACK positivo dell'API Telegram: round-trip dichiarato 414 ms per #729 e 392 ms per #730. L'ACK dimostra l'accettazione API, non la visualizzazione sul dispositivo.

**Incoerenza temporale da segnalare:** i timestamp delle righe di log che riportano il corpo e l'ACK distano circa 1 ms, mentre il round-trip dichiarato è di 414/392 ms. I timestamp di generazione e ACK sono stati conservati come riportati, ma non è possibile riconciliare da questi log il tempo reale generazione-invio. Non si deve usare la differenza fra le due righe come latenza end-to-end.

Il messaggio #730 dichiara front-month continuo senza scadenza esatta e indipendenza upstream non verificate; NARWHAL non è configurato. Non esistono livelli operativi. Il valore score 100 e la riga rischio 1,0% non rappresentano validità operativa né esposizione eseguita.

Il messaggio #731 compare nella sezione dei test di regressione prima dell'avvio del collector: è un risultato di test, non un invio di produzione, ed è escluso dal ledger.

### Stato persistito

Il job ha eseguito lo step di persistenza e creato/pushato il commit [8074ec2](https://github.com/andreameloni1984-sys/trump-trucker/commit/8074ec2867c3afa3cd38424a53269a858cc5b0da). Il diff di `sputnik_state.json` aggiorna `updated_at` e l'inizializzazione del feed; non dimostra nuovi findings. La persistenza continua a scrivere su `main`; la PR #144, che propone di spostarla, resta aperta.

I 30 test di regressione eseguiti nel monitor sono passati. I successivi run PR #42443154899 e #42443154902 per la PR #148 sono anch'essi SUCCESS, ma sono test, non scansioni di mercato. La PR #148 è ancora aperta e non integrata.

## 2. GAGARIN

### Ultimo monitor di mercato

[GitHub Actions #42438806862](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42438806862) — evento `schedule`, avvio 2026-11-08 02:30:08 UTC, conclusione 02:30:28 UTC, SUCCESS. Nessun artifact Actions.

Il workflow dichiara `PAPER_TRADING_ONLY=1`, `MONITOR_INTERVAL_MINUTES=15`, soglie runtime 40/30/35 e RR 2,5. `DATABASE_URL` e `NARWHAL_API_KEY` risultano vuoti nel run.

### Quotazioni e candidato

Il runtime riporta 8 commodity operative e EUR/USD e GBP/USD come contesto Forex ausiliario. Tutti gli strumenti risultano `MARKET_CLOSED` e tutte le quotazioni stale:

| Strumento | Provider | Età riportata |
|---|---|---:|
| Soia | Yahoo | 112.523,9 s (~31h15m24s) |
| Grano | Yahoo | 112.523,6 s (~31h15m24s) |
| Mais | Yahoo | 112.523,8 s (~31h15m24s) |
| Brent | Yahoo | 102.923,4 s (~28h35m23s) |
| WTI | Yahoo | 102.923,3 s (~28h35m23s) |
| Oro | Yahoo | 102.921,8 s (~28h35m22s) |
| Argento | Yahoo | 102.922,9 s (~28h35m23s) |
| Rame | Yahoo | 102.923,1 s (~28h35m23s) |
| EUR/USD | BiQuote | 102.924,5 s (~28h35m25s) |
| GBP/USD | BiQuote | 102.925,1 s (~28h35m25s) |

Il log non espone timestamp esatto della candela, ticker provider risolto, prezzo di riferimento, tipo mercato o scadenza per il candidato.

Argento è l'unico candidato commodity direzionale:
- LONG; probabilità 59, qualità 49,5, confidence 32.
- Stato PAPER_WATCH, non autorizzato.
- Blocchi: LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, CONFIDENCE_FAIL, FINAL_CONFLUENCE_FAIL.
- Nessuna entry, SL, TP o ATR.

Riepilogo runtime: `signals=0`, `open=0`, `closed=0`, `Recorded entries=0`, `Updated open outcomes=0`, `New feedback signals=0`.

Il board Telegram #3718 ha ricevuto ACK API (560 ms), ma il corpo non è conservato e non viene attribuito ad Argento. Il record era già nel ledger: nessun duplicato aggiunto.

## 3. Journal e feedback GAGARIN

Lettura attuale dei file su `main`:
- `journal.csv`: 11 righe, tutte del 17 ottobre e con esito “nessun segnale”.
- `paper_trade_log.csv`: un solo ticket legacy WTI, entry 96,24, stop 89,37, TP 103,11/106,55; import legacy, nessuna prova di fill, nessun esito.
- `data/paper_open.json`: contiene P0001 con gli stessi livelli del ticket WTI; è la stessa posizione, non una seconda operazione.
- `position.json`: vecchia posizione Heating Oil HO/USD del 15 settembre, senza prova di fill e senza identità completa del contratto.
- `commodities_prediction_log.json`: 981 record; ultimo 2026-09-15 15:45:04 UTC. Stati: 945 PENDING e 36 NEUTRALE; operational_signal: 960 WAIT, 15 LONG, 6 assenti. Le etichette LONG/COMPRA ORA non provano esecuzione.
- `gagarin_feedback.csv`: 404 Not Found.

Nessuno dei record legacy può essere valutato SL/TP senza prova di fill, timestamp e strumento/contratto esatti e prezzi successivi coerenti.

## 4. Cadenza delle GitHub Actions

Workflow attuali:
- SPUTNIK `.github/workflows/trump_tracker.yml`: cron `2-59/5 * * * *`.
- GAGARIN `.github/workflows/gagarin-monitor.yml`: cron `*/15 * * * *`.

Ultimi due monitor di mercato:
- SPUTNIK: #42426077974 (23:37:18 UTC del 7 novembre) → #42439632866 (02:41:59 UTC dell'8 novembre): 3h04m41s fra gli avvii.
- GAGARIN: #42423479990 (23:03:38 UTC del 7 novembre) → #42438806862 (02:30:08 UTC dell'8 novembre): 3h26m30s fra gli avvii.

Al cut-off, dall'ultima conclusione erano trascorsi circa 52 minuti per SPUTNIK e 1h04m per GAGARIN. Le run di polling Telegram e i test PR non sono monitor di mercato. Le liste Actions recenti non mostrano un monitor schedule successivo ai due run sopra.

## 5. PR e correzioni già esistenti

### SPUTNIK
- [#144 — persistenza stato fuori da main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN, non mergeata; il run corrente ha ancora scritto lo stato su main.
- [#145 — provenienza quotazioni e diagnostica Yahoo](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN.
- [#147 — rimozione accoppiamento GAGARIN](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN.
- [#148 — evitare raccomandazioni ripetute](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN; i due check PR più recenti consultati sono SUCCESS, ma non è integrata.

### GAGARIN
- [#175 — conflitto webhook/polling](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): OPEN.
- [#181 — provenienza esatta quotazioni](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/181): OPEN.
- [#190 — ACK API riepilogo Telegram](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/190): OPEN.
- [#192 — identità esatta contratto e outcome cronologico](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN.
- [#219 — rimozione EUR/USD e GBP/USD dall'universo](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219): OPEN.
- [#222, #223, #235](https://github.com/andreameloni1984-sys/commodity-news-scanner/pulls): OPEN/DRAFT, non integrate.
- [#236 — pagine catalogo ufficiale come evidenza identità CFD](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/236): OPEN/DRAFT.
- [#237 — associazione della pagina catalogo al simbolo broker esatto](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/237): OPEN/DRAFT. La PR documenta un difetto dimostrato nel branch della #236: il test positivo abbina lo slug `CRUDE.NOV26` al simbolo fixture `TEST-WTI-2026-11-27`, e il validatore accetta la pagina di un simbolo diverso. La #237 propone il confronto esatto fra slug canonico e broker_symbol. È un difetto del branch draft #236, non una correzione presente su main. I due check associati al branch #237 risultano SUCCESS.

Nessuna PR è stata mergeata da PRAVDA.

## 6. Fonti consultate

- [SPUTNIK Actions — run #42439632866](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42439632866)
- [GAGARIN Actions — run #42438806862](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42438806862)
- [SPUTNIK workflow](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/trump_tracker.yml)
- [GAGARIN workflow](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml)
- Journal, ticket legacy, posizione, prediction log e feedback su `main`.
- Ledger PRAVDA precedente e aggiornato.
- PR e check run elencati nella sezione precedente.

## 7. Prossimo controllo

1. Verificare una nuova run schedule di mercato distinta da polling, daily summary e test PR.
2. Verificare la cadenza reale di entrambi i monitor, senza dedurla dal solo cron.
3. Alla riapertura dei mercati, acquisire per ogni candidato ticker risolto, tipo mercato, scadenza, provider, timestamp OHLC e prezzo di riferimento.
4. Per ogni eventuale trade, richiedere prova di fill e valutare in sequenza temporale le candele dello stesso contratto: SL prima, TP prima o ESITO NON VERIFICABILE.
5. Verificare le correzioni quando risultano effettivamente integrate su main.

**Modifiche di questo audit:** due sole nuove righe ledger, per i messaggi SPUTNIK #729 e #730, e questo rapporto. Nessun codice, workflow, strategia, filtro, punteggio, rischio, segreto o configurazione Render modificati. Nessun merge, deploy o ordine reale. Nessun accesso a Trading212 e nessuna consegna Telegram al dispositivo dichiarati.
