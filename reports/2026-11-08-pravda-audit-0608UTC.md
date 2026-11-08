# PRAVDA — Audit indipendente SPUTNIK / GAGARIN

**Cut-off:** 8 novembre 2026, 06:08:08 UTC (07:08:08 Europe/Rome)  
**Perimetro:** GitHub Actions schedule, log di produzione, journal/feedback, stato persistito, ledger, PR aperte. PAPER ONLY. Nessuna modifica a codice, strategia, filtri, punteggi o rischio.

## Esito sintetico

Non risultano nuove scansioni di mercato su `main` dopo i monitor delle 02:42 UTC (SPUTNIK) e 02:30 UTC (GAGARIN). Le esecuzioni SPUTNIK delle 05:20 UTC sono test di pull request, non scansioni di mercato.

Il ledger del giorno resta a **81 record**, senza duplicati. Non sono emersi nuovi segnali operativi da aggiungere.

| Indicatore | Totale | SPUTNIK | GAGARIN |
|---|---:|---:|---:|
| Record ledger | 81 | 33 | 48 |
| NON_TRADE | 52 | 26 | 26 |
| ESITO_NON_VERIFICABILE | 29 | 7 | 22 |
| Firme uniche | 81 | — | — |
| Source ID unici | 81 | — | — |
| Duplicati | 0 | — | — |
| Fill verificati | **0** | 0 | 0 |
| SL/TP verificati | **0** | 0 | 0 |

I 29 record non verificabili non sono 29 operazioni: comprendono previsioni storiche PENDING, ticket legacy senza fill e notifiche WATCH/analisi senza direzione o senza corpo attribuibile. Non esiste un campione di trade eseguiti con identità strumento/contratto e candele successive verificabili. Win rate e average R restano N/D; nessun backtest è stato inventato.

Ledger consultato e invariato: [pravda-signal-ledger-2026-11-08.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-08.csv).

## 1. SPUTNIK

### Ultimo monitor di mercato su main

[Actions #42439632866](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42439632866) — workflow `trump_tracker.yml`, evento schedule, avvio 02:41:59 UTC, conclusione 02:42:14 UTC, SUCCESS, nessun artifact.

Al cut-off sono trascorsi **3h25m54s** dalla conclusione. Il precedente monitor era #42426077974, avvio 7 novembre 23:37:18 UTC: intervallo fra gli avvii **3h04m41s**, nonostante cron configurato ogni 5 minuti.

### Log e fonti

- SEC: HTTP 403; cooldown impostato a 21.600 secondi; zero filing.
- White House RSS: HTTPError.
- Scansione intelligence pubblica: zero finding.
- Nessun catalizzatore inoltrato a GAGARIN.
- Le righe di test del collector riportano fonti WHITE_HOUSE, TRUTH_ARCHIVE e OGE non disponibili nel contesto di test; non sono finding di produzione.
- GOLD: bias NEUTRAL, nessuna notizia direzionale, tecnica 5m non disponibile, decisione WATCH.
- Nessun ticker risolto, provider/ora della quotazione, mercato/scadenza, entry, SL, TP o ATR verificabili.

### Telegram

Il log di produzione conferma API acceptance per:
- #729, GOLD NEUTRAL / WATCH, generato 02:42:09.805695 UTC, ACK log 02:42:09.806702 UTC.
- #730, GOLD CFD NO_DIRECTION / NOT_EXECUTED, generato 02:42:09.806747 UTC, ACK log 02:42:09.807806 UTC.

I round-trip dichiarati sono 414 ms e 392 ms. Gli timestamp log generazione/ACK differiscono di circa 1 ms, quindi la latenza end-to-end non è ricostruibile in modo coerente. L'ACK API non dimostra visualizzazione sul dispositivo. Il message_id #731 compare nel test di regressione e non va contato come invio di produzione.

### Stato e correzioni

Il commit [8074ec2](https://github.com/andreameloni1984-sys/trump-trucker/commit/8074ec2867c3afa3cd38424a53269a858cc5b0da) aggiorna `sputnik_state.json` su `main` alle 02:42:08 UTC. La persistenza è quindi ancora legata a main; PR #144 per spostare lo stato fuori da main resta aperta.

Il run ha superato i test di delivery e item intelligence eseguiti prima del collector. I run PR #42450417214 e #42450417210, conclusi SUCCESS alle 05:21 UTC circa, sono test della PR #148 e non monitor di mercato.

## 2. GAGARIN

### Ultimo monitor di mercato su main

[Actions #42438806862](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42438806862) — workflow `gagarin-monitor.yml`, evento schedule, avvio 02:30:08 UTC, conclusione 02:30:28 UTC, SUCCESS, nessun artifact.

Al cut-off sono trascorsi **3h37m40s** dalla conclusione. Il precedente monitor #42423479990 era partito il 7 novembre alle 23:03:38 UTC: intervallo fra gli avvii **3h26m30s**, contro un cron configurato ogni 15 minuti.

### Dati e candidato

Il log contiene otto commodity (Soia, Grano, Brent, WTI, Oro, Argento, Mais, Rame) e due coppie FX ausiliarie (EUR/USD, GBP/USD). Non compaiono Platino e Palladio in questa scansione.

Tutte le righe sono `MARKET_CLOSED` e le quotazioni sono stale:
- Soia, Grano e Mais: Yahoo, circa 112.524 secondi (31h15m).
- Brent, WTI, Oro, Argento e Rame: Yahoo, circa 102.923 secondi (28h35m).
- EUR/USD e GBP/USD: BiQuote, circa 102.924–102.925 secondi.

Il timestamp esatto della candela, il ticker provider risolto, il mercato/scadenza e il prezzo di riferimento non sono esposti per il candidato.

Argento è l'unico candidato direzionale: LONG, probabilità 59, qualità 49,5, confidence 32, stato PAPER_WATCH. È bloccato da LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, CONFIDENCE_FAIL e FINAL_CONFLUENCE_FAIL. Entry, SL, TP e ATR assenti. È una previsione WATCH non autorizzata, non un trade.

Il riepilogo runtime è `signals=0 open=0 closed=0`; feedback nuovi 0. Telegram message #3718 è stato accettato dall'API in 560 ms come WATCH pre-alert, ma il corpo non è conservato e non si può attribuire ad Argento o ad altra direzione.

### Journal e stato persistito

- `journal.csv`: 11 righe datate 17 ottobre, tutte “nessun segnale”.
- `paper_trade_log.csv`: un solo ticket legacy WTI P0001, LONG, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55. Mancano signal ID, provider, ticker quotazione, timestamp, mercato/scadenza e prova di fill.
- `data/paper_open.json`: P0001 risulta OPEN, mentre il monitor attuale conta `open=0`. Discrepanza tra stato legacy e runtime; non prova esecuzione.
- `position.json`: vecchia posizione Heating Oil HO/USD del 15 settembre, senza prova di fill e senza identità completa del contratto.
- `commodities_prediction_log.json`: 981 record, 945 PENDING e 36 NEUTRALE; ultimo record 15 settembre. Le etichette LONG/COMPRA ORA e score elevati non provano esecuzione.
- `commodities_monitor_state.json` e `commodities_direction_state.json`: ultimi timestamp del 17 settembre, quindi non rappresentano il monitor attuale.
- Nessun artifact Actions nel run attuale; il workflow dichiara che i journal privati non vanno committati nel repository pubblico e che la persistenza va riattivata dopo verifica dello storage privato.

Non attribuire outcome al ticket WTI P0001 o alla posizione Heating Oil: mancano fill, identità esatta del contratto e candele successive dello stesso contratto.

### Difformità di universo

L'Argento continua ad apparire nel monitor principale, nonostante la richiesta di escluderlo dalla scansione. La PR #223 propone un runner M5 separato di sette strumenti che esclude l'Argento, ma è ancora draft e specifica che l'Argento resta nel più ampio universo commodity. La PR #219 per togliere EUR/USD e GBP/USD dall'universo canonico è aperta e non integrata; il run su main continua quindi a mostrare le due coppie FX ausiliarie.

## 3. PR e correzioni aperte — nessuna integrata in questo audit

### SPUTNIK
- [#148 — stop alle raccomandazioni ripetute senza nuovo catalizzatore](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN, non draft, mergeable. I due check più recenti (#42450417214 e #42450417210) sono SUCCESS. Correzione utile, ma non integrata su main.
- [#144 — persistenza stato fuori da main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN, non draft; main continua a ricevere commit di stato.
- [#145 — provenienza quote e diagnostica errori Yahoo](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN, non draft.
- [#147 — rimozione handoff GAGARIN da SPUTNIK](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN, non draft.

### GAGARIN
- [#181 — esposizione provenienza esatta delle quotazioni](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/181): OPEN, non draft.
- [#192 — identità esatta contratto e gestione ambiguità outcome](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, non draft.
- [#219 — rimozione EUR/USD e GBP/USD dall'universo](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219): OPEN, non draft.
- [#223 — scansione M5 separata a sette strumenti, Argento escluso](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): OPEN, draft; non sostituisce il monitor principale.
- [#225 — offset del cron GAGARIN](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225): OPEN, draft.
- [#235 — persistenza journal CFD Trading 212](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/235): OPEN, draft e specifica al ramo CFD Trading 212; non la considero soluzione per il journal futures del monitor principale.

## 4. Esiti, limiti e prossime verifiche

**Esiti verificabili:** zero fill; zero SL/TP; zero trade con outcome ricostruibile. I 52 NON_TRADE restano non-trade; i 29 ESITO_NON_VERIFICABILE restano tali. Nessuna percentuale di successo calcolabile.

**Difetti dimostrati da segnalare ai reparti:**
1. Mancata cadenza reale dei monitor rispetto ai cron configurati.
2. SPUTNIK senza fonti pubbliche utilizzabili nel run (SEC 403, White House HTTPError) e senza direzione/quotazione verificabile.
3. GAGARIN opera con tutte le quotazioni stale nel run domenicale; Argento ancora presente nel monitor principale.
4. Identità esatta provider/ticker/mercato/scadenza e timestamp candela non disponibili nel messaggio/record del candidato.
5. Journal legacy e conteggio runtime incoerenti (WTI P0001 OPEN nel file ma `open=0` nel monitor).
6. Corpo del WATCH pre-alert Telegram GAGARIN non conservato; non attribuibile.
7. PR che affrontano provenienza, persistenza, cron e outcome sono ancora aperte.

**Prossimo controllo:** verificare le successive run schedule effettive (non i test PR), esaminare nuovi log e artefatti, e aggiungere al ledger solo record nuovi con firma unica. Per qualsiasi segnale direzionale, richiedere ticker/contratto/scadenza, provider e timestamp quote, entry/SL/TP/ATR e prova del messaggio; per l'outcome usare esclusivamente candele successive dello stesso identico contratto, in ordine cronologico. Se uno di questi elementi manca, lasciare ESITO_NON_VERIFICABILE.

**Modifiche effettuate in questo audit:** creato soltanto questo rapporto. Ledger invariato perché non sono emersi nuovi record eleggibili. Nessuna modifica a codice, configurazione, strategia, rischio, segreti o Render; nessun merge, deploy o ordine reale.
