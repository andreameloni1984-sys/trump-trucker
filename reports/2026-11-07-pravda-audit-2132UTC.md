# PRAVDA — Audit indipendente SPUTNIK / GAGARIN

**Cut-off:** 2026-11-07 21:32:56 UTC (22:32:56 Europe/Rome)  
**Modalità:** sola lettura dei bot e delle Actions; aggiornato soltanto questo rapporto PRAVDA. PAPER ONLY.

## 1. Sintesi esecutiva

- Il ledger PRAVDA resta a **61 record**, **61/61 firme uniche**, **61/61 source_record_id unici**, **zero duplicati**.
- Classificazione ledger: **29 ESITO_NON_VERIFICABILE**, **32 NON_TRADE**. Nessun fill verificato, nessun TP/SL verificato; win rate e average R restano **N/D**.
- Non ho aggiunto righe al ledger: i run più recenti non espongono un nuovo record di segnale completo. Le tre osservazioni SPUTNIK del commit delle 20:07 UTC sono già presenti nel ledger e sono intelligence non direzionale, non trade.
- Ho trovato run di monitor più recenti rispetto al rapporto precedente: SPUTNIK #42409488950 e GAGARIN #42407171354. Entrambi risultano SUCCESS, ma nessuno dei due ha artifact Actions; i log applicativi non sono recuperabili tramite l'interfaccia disponibile. SUCCESS del job non dimostra un segnale, una quotazione fresca o un invio Telegram.
- Entrambi i monitor hanno comunque avuto gap di oltre quattro ore, incompatibili con la cadenza cron dichiarata (SPUTNIK 5 minuti, GAGARIN 15 minuti).

## 2. Ledger — verifica indipendente

File: [pravda-signal-ledger-2026-11-07.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-07.csv)  
Blob SHA letto: `8a6f7ad5dcbe4a3e1f10a3afb879af7e7578bcef`.

Il CSV è stato riletto e analizzato rispettando i campi quotati. Risultato: 61 righe dati; 61 audit_signature distinte; 61 source_record_id distinti; nessun duplicato.

| Classificazione | Record |
|---|---:|
| GAGARIN | 44 |
| SPUTNIK | 17 |
| Historical prediction candidate | 21 |
| ESITO_NON_VERIFICABILE | 29 |
| NON_TRADE | 32 |
| Fill verificati | 0 |
| Outcome SL/TP verificati | 0 |

I 21 record storici GAGARIN hanno etichetta legacy `COMPRA ORA`, ma sono `PENDING`: 15 riportano LONG e 6 hanno il campo `operational_signal` assente. Mancano provider, timestamp della quotazione, market type e scadenza esatta. Non sono 21 trade e non sono prova di fill.

Non è possibile calcolare statistiche di performance su un campione verificabile: nessun segnale ha una sequenza successiva di candele dello stesso provider, ticker, mercato e contratto con identità sufficiente. Non attribuisco né TP né SL.

## 3. GitHub Actions — SPUTNIK

### Run più recente

[SPUTNIK #42409488950](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42409488950)  
- Schedule, main; avvio 20:07:13 UTC, completamento 20:07:24 UTC; job `sputnik` SUCCESS.
- Tutti gli step del job risultano SUCCESS, incluso `Run SPUTNIK (Render-independent)` e `Persist SPUTNIK state`.
- Artifact Actions: zero. Il log applicativo non è disponibile in questa verifica.

Il commit di persistenza [8c5dd9d](https://github.com/andreameloni1984-sys/trump-trucker/commit/8c5dd9d2173e999dfb3259a4d0916c807d953e67), creato da SPUTNIK Bot alle 20:07:20 UTC, modifica soltanto `sputnik_state.json`. Il diff mostra `events: {}` e tre nuove osservazioni in `intelligence_history`:
1. item RSS pubblicato alle 14:33:02 UTC, titolo generico di repost/quote, classificato OTHER / NO_ANALOGUE;
2. item RSS pubblicato alle 17:45:04 UTC su minacce di impeachment e indagine DOJ, classificato OTHER / NO_ANALOGUE;
3. snapshot page-level di TRUTH_ARCHIVE senza titolo e timestamp individuali; la classificazione per analogia ha `historical_matches=[]` e `NO_ANALOGUE`.

Sono tre osservazioni intelligence, non tre segnali commodity. Sono già incluse nel ledger; nessun nuovo record viene aggiunto.

### Ultimo run con log applicativo già ispezionato

[SPUTNIK #42388887315](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42388887315), 15:57:48–15:58:04 UTC:
- GOLD: bias NEUTRAL, `NO_DIRECTIONAL_NEWS`, tecnica 5m non disponibile, score 70, WATCH.
- Mapping configurato `GC=F`, ma ticker runtime, provider, timestamp quotazione e scadenza del continuo front-month non sono esposti.
- Entry, SL, TP e ATR assenti; `NOT_EXECUTED`.
- Telegram API ha accettato i messaggi #721 e #722. Sono notifiche NO_DIRECTION, non trade. Il message_id 731 era un test e non è contato.

Il polling [#42407099408](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42407099408), 19:37:12 UTC, è SUCCESS ma è un runner di polling, non una scansione di mercato e non prova un nuovo invio.

### Cadenza

Cron su main: `2-59/5 * * * *`. Run di mercato visibili:
- #42361443562 alle 09:50:55 UTC;
- #42388887315 alle 15:57:48 UTC: gap **6h06m53s**;
- #42409488950 alle 20:07:13 UTC: gap **4h09m25s**.

Al cut-off, l'ultimo monitor SPUTNIK aveva **1h25m43s**. Il cron configurato non corrisponde alla cadenza runtime osservata.

Il Daily Summary [#42371347665](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42371347665) è partito alle 12:11:08 UTC, **6h11m08s** dopo il cron delle 06:00. In questo caso il workflow ha verificato `ok=true` e `result.message_id=720`: API ACK dimostrato, visualizzazione sul dispositivo non dimostrata.

## 4. GitHub Actions — GAGARIN

### Run più recente

[Gagarin Paper Monitor #42407171354](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42407171354)  
- Schedule, main; avvio 19:38:07 UTC, completamento 19:38:24 UTC; job SUCCESS.
- Step `Run Gagarin analysis, paper journal, feedback and Telegram alerts` completato SUCCESS.
- Artifact Actions: zero. Non sono disponibili stdout/log applicativi del run.

Quindi non attribuisco a questo run strumenti, direzioni, prezzi, livelli o messaggi Telegram. Non è possibile stabilire se la freschezza dati sia migliorata rispetto al run precedente.

### Ultimo run con output applicativo ispezionabile

[GAGARIN #42386803148](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42386803148), 15:31:37–15:31:58 UTC:
- Otto commodity in `MARKET_CLOSED`.
- Yahoo quote age: circa 63.412 secondi (17h37m) per metalli/petrolio e 73.013 secondi (20h17m) per cereali.
- Argento era LONG/PAPER_WATCH, ma bloccato da `LIVE_DATA_NOT_FRESH`, trigger non confermato e mismatch direzionale; entry, SL, TP e ATR assenti.
- Score/probabilità non equivalgono ad autorizzazione operativa.
- Telegram board #3715 accettato dall'API, ma il corpo non è conservato: non è possibile attribuirlo con certezza ad Argento o a un'altra commodity.

### Cadenza

Cron main: `*/15 * * * *`. Run di mercato visibili:
- #42357485498 alle 08:55:05 UTC;
- #42386803148 alle 15:31:37 UTC: gap **6h36m32s**;
- #42407171354 alle 19:38:07 UTC: gap **4h06m30s**.

Al cut-off, l'ultimo monitor GAGARIN aveva **1h54m49s**. La frequenza effettiva non è quella dichiarata.

### Telegram e riepilogo

- Il workflow di polling dichiara `*/5 7-21 * * 1-5`. L'ultimo run GAGARIN documentato resta #42317191549, fallito il 7 novembre alle 00:16 UTC, fuori dalla finestra cron dichiarata; il precedente log esplicito registra Telegram API 409 per webhook attivo e `getUpdates` incompatibile. La PR #175 è ancora aperta.
- Daily Summary [#42374841686](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42374841686): avvio 12:58:56 UTC, **6h43m56s** dopo il cron delle 06:15. Il workflow stampa “Summary sent”, ma non interpreta la risposta JSON, non verifica `ok=true` e non richiede `result.message_id`. L'ACK Telegram non è dimostrato.
- Il polling e il daily summary sono workflow ausiliari: non vanno conteggiati come scansioni di mercato.

## 5. Journal, feedback e posizioni GAGARIN

Lettura dei file su main:

- `journal.csv`: 11 righe dati, tutte del 17 ottobre e tutte con esito testuale `nessun segnale`; non contiene trade.
- `paper_trade_log.csv`: una sola riga dati, import legacy WTI P0001, stato OPEN, entry 96.24, stop 89.37, TP1 103.11, TP2 106.55. I campi provider, quote timestamp, quote symbol, market type e contract expiry sono vuoti; nessuna prova di fill o PnL realizzato.
- `data/paper_open.json`: contiene lo stesso WTI P0001; non è un secondo trade.
- `position.json`: vecchia posizione Heating Oil, HO/USD LONG, aperta il 15 settembre alle 13:23:44 UTC; entry 4.8844, SL 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882. Mancano provider, ticker risolto, market type, scadenza e prova di fill. Outcome non verificabile.
- `commodities_prediction_log.json`: 981 record; ultimo `created_at` 2026-09-15 15:45:04 UTC. Gli ultimi record RBOB/Heating Oil hanno status PENDING e action `COMPRA ORA`, ma non contengono identità verificabile del contratto né provider/timestamp quotazione. Non sono trade.
- `gagarin_feedback.csv`: assente su main.

Il workflow monitor usa `permissions: contents: read` e non carica artifact; i file prodotti sul runner effimero non sono quindi uno storico cross-run dimostrato. Il workflow espone `DATABASE_URL`, ma nell'ultimo run con log applicativo leggibile (#42386803148) il valore era vuoto. Per il run #42407171354 non ho log sufficienti per verificare il valore. Il daily summary non passa `DATABASE_URL` al processo e usa il riepilogo locale. La persistenza non è dimostrata.

## 6. PR/correzioni già esistenti — stato verificato

### SPUTNIK
- [PR #144 — persistenza stato fuori da main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN, non merged, GitHub segnala `mergeable=false`; i due workflow di test sul head corrente sono SUCCESS.
- [PR #148 — non ripetere raccomandazioni senza nuovo catalizzatore](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN, non merged, `mergeable=false`; i due check sul head corrente sono SUCCESS.
- [PR #107 — provenienza quotazioni](https://github.com/andreameloni1984-sys/trump-trucker/pull/107): OPEN, non merged, `mergeable=false`. La mancanza di provider/ticker runtime/timestamp/scadenza resta visibile nell'ultimo output ispezionato.

### GAGARIN
- [PR #175 — conflitto webhook/polling](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): OPEN, non merged. Sette check su otto sono SUCCESS; `Workers Builds: telegram-github-bridge` è FAILURE.
- [PR #192 — identità esatta contratto e outcome ambiguo](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, non merged. Gli otto test/check applicativi sono SUCCESS, ma `Workers Builds: telegram-github-bridge` è FAILURE. Inoltre il commento PRAVDA #6706619879 segnala che sul head il confronto outcome non applica ancora il match esplicito del provider, nonostante il provider sia registrato nel fingerprint.
- [PR #202 — journal/feedback persistenti PostgreSQL](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): OPEN, DRAFT, non integrata.
- [PR #222 — rimozione veto intraday](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222): OPEN, DRAFT, non integrata.
- [PR #223 — scansione M5 a sette strumenti, Argento escluso](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): OPEN, DRAFT, non integrata. Main continua quindi a usare il percorso monitor già esistente, non questa scansione isolata.
- [PR #235 — journal persistente CFD PAPER isolato](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/235): OPEN, DRAFT, impilata su #234 e #233, non su main. Quattro check applicativi sono SUCCESS, il check Workers Build è FAILURE. È specifica per il ramo CFD Trading 212 isolato e non dimostra la persistenza del journal futures attivo su main.

## 7. Esito dell'audit

- Segnali operativi con fill verificato: **0**.
- Sequenze successive di candele dello stesso provider/ticker/mercato/contratto disponibili: **0**.
- Esiti SL prima / TP prima dimostrati: **0 / 0**.
- ESITO NON VERIFICABILE nel ledger: **29**.
- NON_TRADE nel ledger: **32**.
- Win rate e average R: **N/D**.

I difetti dimostrati da mantenere in evidenza sono: gap delle scansioni rispetto ai cron, assenza di artifact/log nei run più recenti, quote stale nell'ultimo run GAGARIN con output leggibile, identità incompleta dei contratti, journal non persistente dimostrato, polling GAGARIN in conflitto col webhook e daily summary GAGARIN senza ACK verificato.

## 8. Prossimo controllo

1. Acquisire stdout/artifact del prossimo monitor SPUTNIK e GAGARIN; senza output non attribuire segnali né assenza di segnali.
2. Misurare la cadenza dai run effettivi, non dal solo cron.
3. Per ogni nuovo candidato, richiedere provider, ticker risolto, market type, expiry/contract month, quote timestamp, entry, SL, TP e ATR.
4. Valutare outcome soltanto su candele successive dello stesso identico contratto; stessa candela con SL e TP entrambi toccati resta non verificabile.
5. Ricontrollare PR #175/#192 e la persistenza su main soltanto dopo integrazione e nuova evidenza runtime.

**Nessuna modifica a codice, strategia, filtri, punteggi o rischio. Nessun merge, deploy, ordine, accesso a segreti/Render o Trading 212. Nessuna consegna Telegram dedotta senza ACK. PAPER ONLY.**
