# PRAVDA — Audit SPUTNIK / GAGARIN
**Data controllo:** 7 novembre 2026, 18:42:38 UTC (19:42:38 Europe/Rome)  
**Modalità:** PAPER ONLY — sola lettura dei bot; nessun ordine, merge, deploy, rerun o modifica di codice.

## 1. Sintesi

| Bot | Ultimo monitor di mercato | Avvio UTC | Fine UTC | Età al controllo | Risultato |
|---|---:|---:|---:|---:|---|
| SPUTNIK | [#42388887315](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42388887315) | 15:57:48 | 15:58:04 | 2h44m34s | SUCCESS |
| GAGARIN | [#42386803148](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42386803148) | 15:31:37 | 15:31:58 | 3h10m40s | SUCCESS |

Entrambi i run hanno concluso il job, ma nessuno ha prodotto artifact Actions. Non risultano monitor di mercato più recenti nelle run schedule interrogate.

### Cadenza effettiva rispetto al cron

- SPUTNIK dichiara `2-59/5 * * * *` (ogni 5 minuti). Il precedente monitor era #42361443562, avviato alle 09:50:55 UTC: intervallo tra gli avvii **6h06m53s**.
- GAGARIN dichiara `*/15 * * * *` (ogni 15 minuti). Il precedente monitor era #42357485498, avviato alle 08:55:05 UTC: intervallo tra gli avvii **6h36m32s**.

La causa dei vuoti di schedulazione non è dimostrata. Il successo di un workflow ausiliario, di polling o di un riepilogo non equivale a una scansione di mercato.

## 2. SPUTNIK — run #42388887315

### Raccolta e catalizzatore
- SEC: **HTTP 403**, cooldown 21.600 secondi; 0 filing.
- Estrazione operazioni: 0 record.
- White House RSS: HTTPError.
- Intelligence pubblica: 1 finding.
- Handoff verso GAGARIN: disabilitato perché `GAGARIN_CLOUD_API_URL` e `GAGARIN_CLOUD_API_KEY` non sono configurati.
- NARWHAL: chiave non configurata.

Il finding è `df6c3173377e2a283c05395c`, fonte TRUTH_ARCHIVE, homepage generale `https://www.trumpstruth.org/`. Titolo e timestamp individuale di pubblicazione sono vuoti; evidenza `PUBLIC_SOURCE_TEXT_PAGE_LEVEL`; classificazione `TRADE_ESCALATION` per analogia storica. Non è un post identificato e datato, né un catalizzatore commodity verificato.

### GOLD — messaggi Telegram #721 e #722
- Generazione: 2026-11-07 15:57:59.5632975 UTC.
- Ultimo ACK Telegram registrato: 15:57:59.5658054 UTC.
- Messaggi API accettati: #721 (738 ms) e #722 (485 ms).
- Strumento logico: GOLD; mapping configurato GC=F.
- Mercato dichiarato: futures continuous front-month.
- Ticker runtime, provider effettivo, timestamp/età della quotazione e scadenza esatta: non esposti.
- Bias NEUTRAL; tecnica 5m UNAVAILABLE; news alignment NO_DIRECTIONAL_NEWS.
- Score 70/100; decisione WATCH / NO_DIRECTION; stato NOT_EXECUTED.
- Entry, SL, TP e ATR: assenti.

Il log avverte di non usare il continuous front-month per livelli operativi: scadenza e indipendenza upstream non verificate. Lo score 70 non è un segnale operativo. Non esistono fill né candele successive identificabili sullo stesso contratto. L'ACK Telegram prova l'accettazione API, non la visualizzazione sul dispositivo.

### Polling e persistenza
- Polling SPUTNIK [#42387284361](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42387284361), 15:37:31 UTC: SUCCESS, `Pending updates: 0`. È polling, non una scansione.
- Il workflow produttivo su main mantiene `permissions: contents: write` e `git push origin main`. Il run #42388887315 ha effettivamente creato il commit [efaa67a](https://github.com/andreameloni1984-sys/trump-trucker/commit/efaa67a227abf8cebfb5eff2b64ad60bece10506) e lo ha spinto su main.
- [PR #144](https://github.com/andreameloni1984-sys/trump-trucker/pull/144) — persistenza fuori da main: OPEN, non merged. I due check aggiornati sono SUCCESS: ranking #42395679151 (193 test) e Telegram/menu #42395679172 (66 test). Il confronto con main corrente mostra 1 commit avanti e 1 indietro; la modifica non è ancora attiva.
- [PR #148](https://github.com/andreameloni1984-sys/trump-trucker/pull/148) — evitare raccomandazioni ripetute: OPEN, non merged; 2 commit avanti e 22 indietro rispetto al main corrente. La correzione non è attiva su main.

## 3. GAGARIN — run #42386803148

### Dati e classificazione
Configurazione runtime: PAPER ONLY; MONITOR_INTERVAL_MINUTES=15; soglie loggate 40/30/35 e RR 2.5. DATABASE_URL è vuoto.

Tutte le otto commodity risultano `MARKET_CLOSED` e con quotazioni Yahoo stale:
- Soia, Grano e Mais: circa 73.013 secondi (20h17m).
- Brent, WTI, Oro, Argento e Rame: circa 63.412 secondi (17h37m).
- EUR/USD e GBP/USD, ausiliari FX, sono stale con provider BiQuote.

Ticker risolto, prezzo, timestamp puntuale della quotazione, market type e scadenza non sono esposti. Non è quindi possibile associare candele successive allo stesso identico strumento/contratto.

L'unico candidato direzionale commodity è Argento LONG (Prob 59, Quality 49,5, Confidence 32), bloccato da LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, CONFIDENCE_FAIL e FINAL_CONFLUENCE_FAIL. Entry, SL, TP e ATR assenti. Nessuna entrata autorizzata.

Argento è ancora presente nel paniere runtime a otto commodity, nonostante la precedente richiesta di escluderlo. [PR #30](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/30), che configura il paniere, è OPEN/DRAFT e non mergeable: non è attiva su main.

### Journal, feedback e Telegram
Il run riporta:
- Recorded entries: 0.
- Updated open outcomes: 0.
- New feedback signals: 0.
- New additional live forecasts: 0.
- signals=0, open=0, closed=0; win_rate e avg_R N/D.

Telegram ha accettato il board #3715 alle 15:31:54.641895 UTC, round-trip 489 ms. Il corpo del board non è conservato: non attribuisco con certezza il messaggio ad Argento o a un altro strumento.

Artefatti main:
- `journal.csv`: 11 righe, tutte annotazioni di nessun segnale.
- `paper_trade_log.csv`: una sola posizione legacy WTI P0001; è duplicata come riferimento in `data/paper_open.json`, non va contata due volte.
- `data/paper_open.json`: WTI LONG, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55, status OPEN.
- Nota del ticket legacy: “Chiusura spot 6 ottobre 2026. Nessun esito.” Manca la prova di fill e il riferimento spot non identifica il contratto futures.
- `position.json`: Heating Oil LONG, entry 4,8844, SL 4,5418, TP1 5,4473, TP2 5,6284, TP3 5,882, apertura 15 settembre 2026; provider, quotazione, contratto e fill non documentati.
- `commodities_prediction_log.json`: 981 record, 945 PENDING e 36 NEUTRALE; ultimo record creato il 15 settembre 2026.
- `gagarin_feedback.csv`: non presente nel repository consultato.
- DATABASE_URL vuoto: non è dimostrata una persistenza durevole condivisa tra monitor e riepilogo.

WTI P0001 e Heating Oil restano **ESITO NON VERIFICABILE**. Non sono state cercate o confrontate candele di spot, continuous futures o contratti diversi.

### Polling e riepilogo
- Ultimo polling GAGARIN disponibile [#42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549), 00:16:15 UTC: FAILURE. Log esplicito: Telegram API 409, webhook attivo, polling `getUpdates` non consentito.
- [PR #175](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175), gestione del conflitto webhook/polling: OPEN, non merged.
- Daily Summary [#42374841686](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42374841686), avviato 12:58:56 UTC rispetto al cron 06:15 UTC (ritardo osservato 6h43m56s). Il log stampa “Summary sent”, ma il workflow non verifica `ok=true` né `result.message_id`: consegna API non confermata.
- [PR #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202), persistenza PostgreSQL: OPEN/DRAFT; non attiva.
- [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192), identità contratto e outcome cronologico: OPEN, non merged.
- [PR #222](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222), rimozione del veto intraday `session_ok`: OPEN/DRAFT; non attiva su main.

## 4. Ledger PRAVDA

File: [pravda-signal-ledger-2026-11-07.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-07.csv)  
Blob SHA: `f13f1a087561f08b32b0abc94f17c209175ad513`.

| Indicatore | Risultato |
|---|---:|
| Record | 58 |
| SPUTNIK | 14 |
| GAGARIN | 44 |
| Firme uniche | 58 |
| Source ID unici | 58 |
| Duplicati firma / source ID | 0 / 0 |
| ESITO_NON_VERIFICABILE | 29 |
| NON_TRADE | 29 |
| Fill verificati | 0 |
| SL/TP verificati | 0 |
| Win rate / Average R | N/D / N/D |

I record dei monitor #42388887315 e #42386803148 sono già presenti nel ledger. Non è stata aggiunta alcuna riga: nessun nuovo segnale o fill distinto da registrare. WATCH, score, storico PENDING e NOT_EXECUTED non sono stati contati come trade.

## 5. Prossimi controlli

1. Verificare che riprendano i monitor di mercato, separandoli da polling, riepiloghi e test.
2. Alla riapertura dei mercati richiedere ticker effettivo, provider, timestamp/età, market type e scadenza esatta per ogni quotazione.
3. Registrare i corpi o hash dei messaggi Telegram e l'ACK API con message_id; non dedurre la consegna sul dispositivo.
4. Verificare il ciclo di persistenza SPUTNIK fuori da main solo dopo l'integrazione autorizzata della PR #144.
5. Verificare la persistenza GAGARIN tra due run consecutivi quando sarà disponibile un backend configurato.
6. Valutare SL/TP solo dopo un fill documentato e su candele dello stesso provider, strumento e contratto; se SL e TP cadono nella stessa candela senza sequenza intrabar dimostrabile, mantenere ESITO NON VERIFICABILE.

## 6. Limiti e integrità

Nessun backtest inventato. Nessun esito dedotto da spot contro futures o da scadenze diverse. Nessuna strategia, filtro, punteggio o rischio modificato. Nessun codice modificato; questo commit aggiunge soltanto il presente rapporto. Nessun merge/deploy, rerun, ordine reale, modifica a segreti o Render. Nessun accesso a Trading212 o servizio a pagamento dichiarato. PAPER ONLY.
