# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-06 16:08 UTC (17:08 Europe/Rome)**

## Sintesi esecutiva

- Nessun nuovo collector di mercato SPUTNIK dopo [#42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412), avviato alle 11:31:39 UTC.
- Nessun monitor prezzi GAGARIN trovato nelle 100 Actions più recenti dopo [#42203497432](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42203497432), avviato alle 10:32:52 UTC.
- Il ledger PRAVDA resta a 32 record e 32 firme uniche; zero duplicati e nessun nuovo record da aggiungere.
- Nessun fill, SL o TP verificabile. Win rate e average R restano N/D.
- Novità CI: SPUTNIK PR #144 ha superato il test ranking sul commit più recente; GAGARIN PR #221 ha superato sia test integrazione sia test execution. Entrambe le PR sono ancora aperte; PR #221 è draft e basata sulla PR #220, non su main.
- Nessun codice bot modificato da PRAVDA; nessun merge, deploy o rerun.

## 1. GitHub Actions: monitor reali distinti dai workflow ausiliari

Controllate le 100 esecuzioni più recenti per repository, filtrando per evento, nome e workflow.

### SPUTNIK
- Ultimo collector schedule: [#42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412), 2026-11-06 11:31:39 UTC, SUCCESS, commit `fbcb0de2bfe921383eee7edff10c5d9cf3d306d2`.
- Cut-off 16:08 UTC: 4h36m senza un nuovo collector nella lista esaminata.
- Cron dichiarato nel workflow: `2-59/5 * * * *`.
- [Daily Summary #42226158074](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42226158074) alle 13:31:21 UTC è un riepilogo, non il collector.
- [Telegram Polling #42206505491](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42206505491) alle 10:56:51 UTC è polling, non il collector.
- La causa del gap non è dimostrata.

### GAGARIN
- Ultimo monitor prezzi noto: [#42203497432](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42203497432), 2026-11-06 10:32:52 UTC, SUCCESS, commit `7ed290b971e780828934d80aa3b936043769eaf6`.
- Main attuale al controllo: `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`; il monitor non era eseguito su questo commit.
- Cut-off 16:08 UTC: 5h35m senza un nuovo monitor prezzi nelle 100 Actions più recenti.
- Cron dichiarato: `*/15 * * * *`.
- [Daily Summary #42232309653](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42232309653), [FETCH DRIVERS #42235888213](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42235888213) e [Telegram Polling #42236174265](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42236174265) non sono monitor prezzi. Il polling fallisce con API 409: webhook attivo, polling non consentito.
- La causa del gap monitor non è dimostrata.

## 2. Nuove verifiche CI e PR

### SPUTNIK PR #144 — persistenza stato
[PR #144](https://github.com/andreameloni1984-sys/trump-trucker/pull/144) è OPEN, non merged, non draft, head `8646794ea9a086e81c57086fb9c73f15c19677b0`, base main `c9174be4d5af493683b4b05828708e1a63f0c3d1`.
- [Run #42247726537](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42247726537): FAILURE sul commit precedente `f0a0c238...`.
- [Run #42247768085](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42247768085): SUCCESS sul commit successivo `8646794e...`; job `tests` e step `Run ranking tests` verdi.
- Il risultato verde dimostra il test su quel commit, non l'integrazione o il funzionamento in produzione. La PR resta aperta.

### GAGARIN PR #221 — rimozione rotte FX residue
[PR #221](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221) è OPEN e DRAFT; head `74999010cf9a5dcb59d7214bb3a865eb25d24bc4`, base PR #220 `1b2127da35e88310b5cfd272e7b753bbb0ac8cb3`, quindi stacked e non direttamente basata su main.
- [SOYUZ GAGARIN Tests #42245355490](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42245355490): SUCCESS, job integration tests verde.
- [Execution Layer Tests #42245355476](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42245355476): SUCCESS, job execution safety tests verde.
- Questi risultati sono un progresso rispetto ai precedenti fallimenti della PR #220, ma non dimostrano che le modifiche siano su main né che il monitor prezzi sia ripartito.
- La PR #220 resta OPEN/DRAFT. La PR #175 resta OPEN; il conflitto webhook/polling visto nel run #42236174265 non è quindi dimostrato come risolto su main.

## 3. Segnali e prezzi: valutazione indipendente

### SPUTNIK — GOLD LONG
Il ledger contiene un candidato completo collegato ai messaggi #707/#708 del collector #42210907412:
- Generazione CFD: 11:31:48.567717 UTC.
- ACK API Telegram: 11:31:48.569094 UTC. È prova di accettazione API, non consegna al dispositivo.
- Strumento GOLD; mapping configurato GC=F; ticker effettivo runtime non confermato.
- Mercato future continuo front-month; scadenza esatta UNKNOWN.
- Provider runtime, timestamp e anzianità della quotazione non esposti.
- Bias LONG preliminare; entry 4075.8999; SL 4074.2713; TP1 4077.5285; TP2 4079.1570; ATR 1.0857; score 70.
- Stato `EARLY_SETUP / NOT_EXECUTED`.

La lettura LONG del messaggio analisi #707 non è coerente con la scheda CFD #708: tecnica NOT_ASSESSED, D-L-A NEUTRAL/NO_DIRECTION e struttura non univoca. Nessun catalizzatore direzionale confermato. I livelli sono esplicitamente non operativi senza contratto e quotazione tracciabili.

**Esito: ESITO NON VERIFICABILE.** Non è un trade e non viene incluso in statistiche di rendimento.

### GAGARIN
- `journal.csv`: 11 righe, tutte datate 2026-10-17 e con “nessun segnale”.
- `paper_trade_log.csv`: una posizione WTI LONG legacy del 2026-10-08, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55; provider, ticker di mercato, contratto/scadenza e fill assenti. Esito non verificabile.
- `commodities_prediction_log.json`: 981 record; ultimo timestamp 2026-09-15T15:45:04.462276Z. Ultimi record PENDING; anche l'etichetta COMPRA ORA non prova esecuzione.
- `gagarin_feedback.csv` non disponibile nel controllo precedente; non è stata trovata evidenza nuova che attesti feedback persistente.
- Nel monitor #42203497432 le otto commodity risultavano stale (circa 601–665 secondi); grano SHORT era WATCH e bloccato da dati non freschi, trigger non confermato/mismatch e RR insufficiente. Gli altri strumenti non avevano livelli operativi completi.
- Nessun nuovo monitor prezzi ha fornito nuove quotazioni o candele successive da valutare.

## 4. Ledger senza duplicati e statistiche

File: `reports/pravda-signal-ledger-2026-11-06.csv`
- Blob SHA: `cfcd19a244cb38e0bb6549de5f191ce68277575a`.
- Record dati: 32.
- Firme uniche: 32.
- Duplicati: 0.
- Il GOLD LONG #707/#708 è una sola firma e una sola riga.
- Nuovi record da aggiungere in questo controllo: 0.
- Fill verificati: 0; TP verificati: 0; SL verificati: 0; outcome verificabili: 0.
- Win rate e average R: N/D (campione verificabile nullo).

Le predizioni legacy e la posizione WTI importata non vengono conteggiate come trade eseguiti.

## 5. Fonti consultate

- GitHub Actions, ultimi 100 run per ciascun repository e job dei run CI citati.
- Stato branch `main` e metadati PR #144, #221, #220 e #175.
- SPUTNIK: `reports/pravda-signal-ledger-2026-11-06.csv`, `sputnik_state.json` (contenuto vuoto su main al controllo), log del run #42210907412.
- GAGARIN: `journal.csv`, `paper_trade_log.csv`, `commodities_prediction_log.json`, log del monitor #42203497432 e del polling #42236174265.
- Nessun servizio a pagamento; nessun accesso Trading212 dichiarato; nessuna prova di consegna Telegram al dispositivo.

## 6. Lacune e prossimo controllo

1. Verificare la ripresa del collector SPUTNIK e del monitor GAGARIN, confrontando ogni run con il commit main effettivamente eseguito.
2. Per ogni segnale futuro acquisire ticker runtime, mercato, scadenza, provider, timestamp/age della quota e timestamp API ACK.
3. Conservare candele successive dello stesso identico contratto e timeframe per la sequenza SL-first/TP-first.
4. Verificare la persistenza di stato SPUTNIK e la risoluzione del conflitto webhook/polling GAGARIN solo dopo evidenza su main.
5. Aggiornare il ledger soltanto in presenza di una nuova firma e dei campi identificativi sufficienti; mai deduplicare per solo nome strumento o direzione.

**Perimetro:** audit e documentazione soltanto. Nessuna modifica al codice dei bot, strategia, filtri, punteggi o rischio; nessun merge, deploy, rerun, ordine reale, modifica di segreti o Render. PAPER ONLY.
