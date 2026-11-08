# PRAVDA — Audit indipendente SPUTNIK / GAGARIN

**Cut-off:** 8 novembre 2026, 04:50:01 UTC (05:50:01 Europe/Rome)  
**Perimetro:** sola verifica di GitHub Actions, log, journal/feedback, stato persistito, ledger e PR. PAPER ONLY. Nessuna modifica ai bot.

## Esito sintetico

Dall'ultimo audit delle 03:34 UTC non risultano nuove scansioni di mercato per nessuno dei due bot. Sono comparsi nuovi test PR, ma non vanno confusi con monitor di mercato.

Il ledger esistente è stato riletto e ricontrollato: 81 record, 81 firme uniche, 81 source ID unici, zero duplicati. Non sono emersi nuovi segnali da aggiungere; il ledger resta invariato.

| Indicatore | Valore |
|---|---:|
| Record nel ledger | **81** |
| SPUTNIK | 33 |
| GAGARIN | 48 |
| Firme uniche | 81 |
| Source ID unici | 81 |
| Duplicati | **0** |
| NON_TRADE | 52 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | **0** |
| SL/TP verificati | **0** |
| Win rate / Average R | N/D |

I 29 record ESITO_NON_VERIFICABILE non equivalgono a 29 trade: comprendono previsioni storiche PENDING e record legacy senza prova di fill. Non è disponibile un campione di operazioni eseguite con candele successive dello stesso identico strumento e contratto. Nessun backtest o risultato finanziario è stato inventato.

Ledger consultato: [pravda-signal-ledger-2026-11-08.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-08.csv).

## 1. SPUTNIK

### Ultimo monitor di mercato

[GitHub Actions #42439632866](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42439632866) — evento `schedule`, avvio 2026-11-08 02:41:59 UTC, conclusione 02:42:14 UTC, SUCCESS. Il job è terminato; nessun artifact Actions.

Log di produzione:
- SEC: HTTP 403, cooldown 21.600 secondi, zero filing.
- White House RSS: HTTPError.
- Scansione intelligence pubblica: zero finding.
- Forwarding GAGARIN: nessun catalizzatore inoltrato.
- GOLD: bias NEUTRAL, tecnica 5m UNAVAILABLE, decisione WATCH.
- Nessuna quotazione con provenienza verificabile, entry, SL, TP o ATR.

Nel log compaiono anche output di test prima dell'avvio del collector. Le righe di test con API round-trip 0 ms e message_id 731 non sono invii di produzione e non sono conteggiate come segnali.

### Messaggi di produzione

| Telegram ID | Generazione (UTC, log) | ACK API (UTC, log) | Contenuto | Esito audit |
|---|---|---|---|---|
| #729 | 02:42:09.8056950 | 02:42:09.8067022 | GOLD NEUTRAL, priorità catalizzatore 100/100, tecnica 5m indisponibile | NO_DIRECTION / NON_TRADE |
| #730 | 02:42:09.8067468 | 02:42:09.8078059 | GOLD CFD, NO_DIRECTION, NOT_EXECUTED, score 100 | NON_TRADE |

L'API Telegram ha confermato i due messaggi; i round-trip dichiarati sono 414 ms e 392 ms. L'ACK prova l'accettazione API, non la visualizzazione sul dispositivo.

Le righe di log con timestamp di generazione e ACK distano circa 1 ms, in contrasto con il round-trip dichiarato di circa 400 ms. La latenza end-to-end non è quindi ricostruibile con certezza da quei due timestamp.

Il messaggio #730 indica futures front-month continuo senza scadenza esatta verificata, provenienza della quotazione non esposta e NARWHAL non configurato. Score e rischio riportati non costituiscono validità operativa né prova di esposizione. Non sono presenti livelli utilizzabili.

### Stato e test

Il commit [8074ec2](https://github.com/andreameloni1984-sys/trump-trucker/commit/8074ec2867c3afa3cd38424a53269a858cc5b0da) dimostra che lo step di persistenza ha aggiornato `sputnik_state.json` su `main` alle 02:42:08 UTC. Il diff aggiorna `updated_at` e l'inizializzazione del feed; non aggiunge nuovi finding.

I 30 test di regressione del monitor sono passati. Successivamente, i run PR [#42443154899](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42443154899) e [#42443154902](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42443154902) sono entrambi SUCCESS e appartengono alla PR #148: sono test, non scansioni di mercato.

## 2. GAGARIN

### Ultimo monitor di mercato

[GitHub Actions #42438806862](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42438806862) — evento `schedule`, avvio 2026-11-08 02:30:08 UTC, conclusione 02:30:28 UTC, SUCCESS. Nessun artifact Actions.

Il workflow dichiara `PAPER_TRADING_ONLY=1`, intervallo 15 minuti, soglie runtime 40/30/35 e RR 2,5. Nel run `DATABASE_URL` e `NARWHAL_API_KEY` sono vuoti.

### Quotazioni e candidato

Il run analizza dieci voci: otto commodity e EUR/USD e GBP/USD come contesto ausiliario. Tutte sono `MARKET_CLOSED` e le quotazioni sono stale.

| Strumento | Provider | Età riportata |
|---|---|---:|
| Soia, Grano, Mais | Yahoo | circa 112.524 s (31h15m) |
| Brent, WTI, Oro, Argento, Rame | Yahoo | circa 102.923 s (28h35m) |
| EUR/USD, GBP/USD | BiQuote | circa 102.925 s (28h35m) |

Il log non espone per il candidato un ticker provider risolto, timestamp esatto della candela, mercato/scadenza, prezzo di riferimento e livelli operativi.

Argento è l'unico candidato direzionale:
- LONG; probabilità 59, qualità 49,5, confidence 32.
- Stato PAPER_WATCH, non autorizzato.
- Blocchi: LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, CONFIDENCE_FAIL e FINAL_CONFLUENCE_FAIL.
- Entry, SL, TP e ATR assenti.

Riepilogo del run: `signals=0 open=0 closed=0`, zero nuovi feedback e zero nuove previsioni live. Il messaggio Telegram #3718 ha ricevuto ACK API in 560 ms, ma il corpo non è conservato: non viene attribuito ad Argento.

### Journal e persistenza

Lettura dei file su `main`:
- `journal.csv`: 11 righe del 17 ottobre, tutte con esito “nessun segnale”.
- `paper_trade_log.csv`: ticket legacy WTI P0001, entry 96,24, SL 89,37, TP 103,11/106,55; nessuna prova di fill e nessuna provenienza completa della quotazione.
- `data/paper_open.json`: lo stesso P0001 ha stato OPEN nel file, ma il monitor riporta `open=0`. È una discrepanza fra stato legacy persistito e conteggio runtime; non prova un trade eseguito.
- `position.json`: vecchia posizione Heating Oil HO/USD del 15 settembre, senza prova di fill e senza identità completa del contratto.
- `commodities_monitor_state.json` e `commodities_direction_state.json`: timestamp di settembre, non aggiornati dal monitor attuale.
- `commodities_prediction_log.json`: 981 record, ultimo 15 settembre; 945 PENDING e 36 NEUTRALE. Le etichette LONG/COMPRA ORA non dimostrano esecuzione.
- `gagarin_feedback.csv`: 404 Not Found.

Non attribuire outcome al WTI P0001 o a Heating Oil: mancano fill, identità esatta del contratto e candele successive coerenti.

## 3. Cadenza GitHub Actions

Workflow su `main`:
- SPUTNIK `.github/workflows/trump_tracker.yml`: cron `2-59/5 * * * *`.
- GAGARIN `.github/workflows/gagarin-monitor.yml`: cron `*/15 * * * *`.

Ultimi due monitor di mercato:
- SPUTNIK: #42426077974 avviato 7 novembre 23:37:18 UTC → #42439632866 avviato 8 novembre 02:41:59 UTC: **3h04m41s** fra gli avvii.
- GAGARIN: #42423479990 avviato 7 novembre 23:03:38 UTC → #42438806862 avviato 8 novembre 02:30:08 UTC: **3h26m30s** fra gli avvii.

Al cut-off 04:50:01 UTC, dall'ultima conclusione erano trascorsi circa **2h07m47s** per SPUTNIK e **2h19m33s** per GAGARIN. Le run di polling Telegram e i test PR non sono state conteggiate come monitor di mercato. Nelle 50 run più recenti consultate non compare una scansione schedule successiva ai due monitor indicati.

## 4. PR e correzioni già esistenti

### SPUTNIK
- [#148 — evitare raccomandazioni ripetute senza nuovo catalizzatore](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN, non draft, mergeable; i due check PR più recenti consultati sono SUCCESS. La diff restringe le raccomandazioni a item pubblici individuali, datati e con permalink e rimuove il vecchio blocco di raccomandazione basato sulla storia. Non è integrata su `main`.
- [#144 — persistenza fuori da main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN, non draft, mergeable; il monitor attivo continua però a scrivere su `main`.
- [#145 — provenienza quotazioni](https://github.com/andreameloni1984-sys/trump-trucker/pull/145) e [#147 — rimozione handoff GAGARIN](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN, non integrate.

### GAGARIN
- [#236 — accettare pagine ufficiali Trading 212 come evidenza identità CFD](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/236): OPEN, draft, non su main.
- [#237 — vincolare URL catalogo al broker_symbol esatto](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/237): OPEN, draft e basata sul branch della #236, non su main. La correzione aggiunge il controllo che lo slug finale della pagina ufficiale coincida esattamente con `broker_symbol`. I run di test sul commit della #237 sono SUCCESS, ma la correzione resta in una catena di PR draft.
- [#175 — conflitto webhook/polling](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175), [#181 — provenienza quotazioni](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/181), [#192 — identità contratti/outcome cronologico](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192), [#219 — rimozione Forex ausiliario](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219): OPEN, non integrate.
- [#202 — journal persistente](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202), [#223 — scansione M5 senza Argento](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223), [#225 — offset cron monitor](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225) e [#235 — journal CFD PAPER isolato](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/235): draft, non integrate.

## 5. Lacune e prossimo controllo

Priorità:
1. Verificare nuove run schedule effettive, separandole da polling e test.
2. Per ogni futuro candidato GAGARIN registrare ticker provider, timestamp OHLC, tipo mercato e scadenza; non associare pagine catalogo a simboli diversi.
3. Conservare body e ACK API Telegram insieme, mantenendo distinti timestamp di generazione, invio e risposta.
4. Riconciliare il ticket WTI P0001 legacy con il conteggio runtime senza presumere un fill.
5. Attribuire SL/TP solo dopo prova di fill e con prezzi/candele dello stesso identico contratto, rispettando l'ordine temporale.

**Modifiche PRAVDA:** nessuna nuova riga nel ledger, perché non sono emersi nuovi segnali o messaggi di produzione non già registrati. È stato creato soltanto questo rapporto di audit. Nessun codice, workflow, strategia, filtro, punteggio o rischio modificato; nessun merge, deploy, ordine reale, segreto o configurazione Render toccati. Nessun accesso Trading212 o consegna Telegram al dispositivo dichiarati.
