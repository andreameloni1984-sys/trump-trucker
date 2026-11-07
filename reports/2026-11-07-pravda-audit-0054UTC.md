# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-07 00:54 UTC (01:54 Europe/Rome)**

## Sintesi esecutiva

- Nessun nuovo monitor di mercato dopo SPUTNIK [#42311247999](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42311247999) (23:20:35 UTC) e GAGARIN [#42304574886](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42304574886) (22:25:16 UTC).
- Al cut-off: circa 1h34m senza nuovo monitor SPUTNIK e 2h29m senza nuovo monitor GAGARIN.
- GAGARIN Telegram Polling [#42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549) è fallito nello step `Run polling runner` dopo la validazione del token.
- Ledger PRAVDA: 40 righe dati, 40 firme uniche, zero duplicati. Nessun nuovo segnale da aggiungere in questo controllo.
- Nessun fill, SL o TP verificato; campione di outcome verificabili = 0; win rate e average R = N/D.
- SPUTNIK PR #147 ha due suite verdi ma resta aperta. GAGARIN PR #192 resta aperta/non integrata; il suo ramo migliora l'identità contratto e l'ambiguità SL/TP simultanei, ma conserva una scelta non dimostrata del TP più alto se più target cadono nella stessa candela.

## 1. Repository, branch e monitor

### SPUTNIK
- Repository: [andreameloni1984-sys/trump-trucker](https://github.com/andreameloni1984-sys/trump-trucker)
- Main al controllo: `cf13453062e230f88cab9b61cd3ffbc0e1624bad`.
- Ultimo monitor schedule nelle 100 Actions consultate: [#42311247999](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42311247999), avvio 23:20:35 UTC, completamento 23:20:46 UTC, SUCCESS, eseguito su SHA `efe601a7af853660da1eca4d4a512533a9a72550`.
- Cut-off 00:54 UTC: 1h33m38s dal monitor.
- Workflow `.github/workflows/trump_tracker.yml`: cron `2-59/5 * * * *`. Nessun altro run schedule SPUTNIK compare dopo #42311247999; le nuove esecuzioni PR non sono monitor di mercato.

### GAGARIN
- Repository: [andreameloni1984-sys/commodity-news-scanner](https://github.com/andreameloni1984-sys/commodity-news-scanner)
- Main al controllo: `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`.
- Ultimo monitor schedule: [#42304574886](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42304574886), avvio 22:25:16 UTC, completamento 22:25:35 UTC, SUCCESS, eseguito sullo stesso SHA main.
- Cut-off 00:54 UTC: 2h28m57s dal monitor.
- Workflow `.github/workflows/gagarin-monitor.yml`: cron `*/15 * * * *`; il workflow dichiara PAPER ONLY e specifica che i journal operativi sono privati e non vengono committati nel repository pubblico.
- Nessun monitor prezzi successivo compare nelle 100 Actions consultate.

Le cadenze configurate non sono rispettate nei run effettivamente osservati. Non attribuisco una causa tecnica senza log che la dimostrino.

## 2. SPUTNIK — candidato GOLD #713/#714

Fonte: collector [#42311247999](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42311247999), record già presente nel ledger.

| Campo | Valore verificato |
|---|---|
| Firma | `PRAVDA-SPUTNIK-CFD-RUN42311247999-20261106T232043Z-GOLD-LONG-EARLY-BIAS` |
| ID sorgente | Messaggi #713 (analisi) e #714 (CFD), un solo candidato |
| Generazione CFD | 2026-11-06 23:20:43.370895 UTC |
| ACK API | 2026-11-06 23:20:43.3721907 UTC |
| Telegram message_id | 714 |
| Strumento | GOLD |
| Ticker | GC=F è il mapping configurato; ticker runtime non confermato |
| Mercato | Future continuo front-month |
| Scadenza | UNKNOWN |
| Provider / timestamp quota | Non esposti; NARWHAL non configurato e provider runtime non registrato |
| Direzione | Bias CFD LONG; analisi #713 preliminare NEUTRAL, tecnica UNAVAILABLE; CFD #714 LONG TECHNICAL_ONLY e D-L-A NEUTRAL/NO_DIRECTION |
| Entry / SL / TP / ATR | Non disponibili |
| Score | 70; non prova validità operativa |
| Stato | EARLY_BIAS / NOT_EXECUTED |
| Esito | ESITO NON VERIFICABILE |

Nessun livello è stato emesso perché mancavano quotazione futures fresca o ATR valido. Non è un trade. L'ACK Telegram (round-trip 383 ms) prova l'accettazione API, non la consegna al dispositivo. Il log segnala un solo finding pubblico, SEC HTTP 403, errore White House RSS e OSError per fonti WHITE_HOUSE/TRUTH_ARCHIVE/OGE; la correlazione TRUTH_ARCHIVE è a livello pagina e non identifica un singolo post con titolo/timestamp. Il message_id 731 stampato dai test di regressione è simulato ed è escluso.

### Persistenza SPUTNIK

La lettura diretta GitHub Contents API di `sputnik_state.json` su main conferma:
- 500 elementi in `intelligence_history`;
- `updated_at=2026-11-06T23:20:41.952764Z`;
- zero eventi attivi;
- offset Telegram 275590742 e `telegram_active=true`.

La persistenza del run è anche documentata dal commit [f503a7b](https://github.com/andreameloni1984-sys/trump-trucker/commit/f503a7b507868dcfb5bf4f76ca81aadbf906372e). Questo corregge la precedente lettura vuota effettuata prima del completamento di quel run.

## 3. GAGARIN — classificazioni WATCH del monitor #42304574886

Le tre righe visibili sono classificazioni bloccate, non alert individuali confermati e non trade. Ticker esatto, mercato, scadenza, timestamp provider e livelli non sono esposti.

| Strumento | Direzione | Provider | Età quota al monitor | Prob. / Quality / Confidence | Stato |
|---|---|---|---:|---|---|
| Petrolio WTI | SHORT | Yahoo | 1533,2 s (~25m33s) | 66 / 57,5 / 37 | PAPER_WATCH, stale, trigger non confermato e mismatch |
| Mais | LONG | Yahoo | 11135,9 s (~3h05m36s) | 63 / 52,5 / 35 | PAPER_WATCH, stale, mismatch, RR_FAIL |
| Argento | LONG | Yahoo | 1531,7 s (~25m32s) | 59 / 49,5 / 32 | PAPER_WATCH, stale, mismatch, RR1_FAIL e confidence fail |

Entry, SL, TP, ATR e prezzo di riferimento non disponibili. Il monitor segnala che tutte le otto commodity erano stale; le età esatte delle altre cinque non sono registrate nelle righe del ledger.

### Watch board Telegram #3710

- Generazione: 22:25:29.422938 UTC.
- ACK API: 22:25:33.877068 UTC, message_id 3710.
- Tempo complessivo generazione→ACK: circa 4,45 secondi; round-trip API riportato: 358 ms.
- Corpo del messaggio assente dal log; strumento, direzione e mapping ai candidati non attribuibili con certezza.
- Stato: WATCH_BOARD / NON_TRADE.
- L'ACK API non prova consegna al dispositivo.

Il monitor registra zero nuove entrate, zero outcome aggiornati e zero nuove righe feedback.

## 4. GAGARIN — journal, feedback e posizioni legacy

- `journal.csv`: 11 righe, tutte datate 2026-10-17 e con “nessun segnale”.
- `paper_trade_log.csv`: una posizione WTI legacy del 2026-10-08, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55; nota dichiara nessun esito. Provider, contratto, fill e scadenza non documentati.
- `data/paper_open.json`: P0001 è la stessa posizione WTI legacy, non un secondo trade.
- `position.json`: vecchia posizione Heating Oil, senza prova indipendente di fill.
- `commodities_prediction_log.json`: 981 record; ultimo creato 2026-09-15T15:45:04.462276Z. I record finali sono `PENDING`; anche `COMPRA ORA` non dimostra esecuzione.
- `gagarin_feedback.csv`: assente dal repository pubblico (Contents API 404). Il workflow monitor spiega che i journal sono dati privati e la persistenza sarà riattivata solo dopo deploy/verifica di storage privato D1.

Non sono disponibili candele successive abbinate allo stesso ticker/mercato/contratto per valutare TP-first o SL-first. Le posizioni legacy e le predizioni PENDING non sono incluse in statistiche di trade eseguiti.

## 5. Verifica del motore outcome: main contro PR #192

### Main attuale

Il file `engine/feedback.py` su main:
- abbina gli stati per `symbol + timeframe`, con fallback simbolo solo se esiste un solo stato;
- non richiede identità del mercato e del contratto/scadenza;
- valuta solo candele con timestamp strettamente successivo alla entry bar;
- se SL e uno o più TP sono toccati nella stessa candela, assegna STOP;
- se più TP sono toccati nella stessa candela, usa `idx=max(hit_targets)`, cioè il target più alto senza prova dell'ordine intrabar.

Questa logica non soddisfa lo standard PRAVDA per l'identità del contratto e per l'ambiguità intrabar.

### PR #192

[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) è OPEN, non merged. Head `295dba4b074e564a4c11aa3fca136a8e4360672c`; base `c93906a2a4b28d60fd58c600b51cd3c05929f89d`, diverso dal main corrente `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`.
- I sei workflow CI sul relativo head del 5 novembre alle 06:34 UTC risultano SUCCESS.
- Il ramo aggiunge market/contract checks e rende `ESITO NON VERIFICABILE` il caso SL+TP nella stessa candela.
- Rimane `idx=max(hit_targets)` per più TP nella stessa candela: non dimostra quale target sia stato raggiunto per primo.
- I test verdi su quel vecchio head non dimostrano integrazione o compatibilità con il main corrente.

Commento PRAVDA aggiornato: [PR #192 — issuecomment-6699958308](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6699958308).

## 6. Telegram polling: nuova esecuzione fallita e anomalia schedule

Run [#42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549):
- evento GitHub: `schedule`;
- creato 2026-11-07 00:16:15 UTC, sabato;
- token validation: SUCCESS;
- step `Run polling runner`: FAILURE.

Il dettaglio log dell'ultima esecuzione non è stato recuperabile in questo audit, quindi non attribuisco automaticamente a questo run l'errore 409. Il precedente run [#42289526533](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42289526533) aveva invece registrato esplicitamente Telegram API 409 (webhook attivo, polling `getUpdates` incompatibile).

Anomalia da verificare: il run #42317191549 è marcato `schedule` alle 00:16 UTC di sabato, mentre il file `.github/workflows/telegram-polling.yml` sullo stesso main SHA dichiara `*/5 7-21 * * 1-5`. Il timestamp/evento non è coerente con la finestra cron dichiarata. La causa non è determinata.

Commento PRAVDA aggiornato: [PR #175 — issuecomment-6699958013](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175#issuecomment-6699958013). PR #175 resta OPEN e non integrata.

## 7. PR e correzioni esistenti

### SPUTNIK
- [PR #147 — rimuovere handoff GAGARIN e mantenere SPUTNIK indipendente](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN, non merged; head `668a17aaeaead4cab403653e1288c22c58343f54`, base main `cf13453062e230f88cab9b61cd3ffbc0e1624bad`. Ranking tests [#42318832066](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42318832066) e item-intelligence tests [#42318832108](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42318832108): entrambi SUCCESS.
- [PR #145 — quote provenance/Yahoo diagnostics](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN, non merged.
- [PR #146 — alert individuali e calendario economico](https://github.com/andreameloni1984-sys/trump-trucker/pull/146): OPEN, non merged.
- Il run #42311247999 ha registrato handoff GAGARIN disabilitato perché cloud URL/key mancanti; PR #147 è una correzione proposta, non ancora attiva.

### GAGARIN
- [PR #192 — exact contract/outcome audit](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, non merged; dettagli sopra.
- [PR #175 — webhook/polling](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): OPEN, non merged; ultimo polling fallito.
- [PR #221 — rimozione rotte FX residue](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): OPEN/DRAFT; head `264e3ee3b5fad50c97c1b5575bb34162daefc695`, base main corrente. Le suite CI sul relativo commit del 6 novembre alle 22:41 UTC risultano verdi, ma la modifica non è su main.
- [PR #223 — scansione M5 isolata a sette strumenti, argento escluso](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): OPEN/DRAFT, non attiva su main.
- [PR #224 — calendario economico e alert eventi](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/224): OPEN, non merged.

## 8. Ledger PRAVDA e statistiche

File: [reports/pravda-signal-ledger-2026-11-06.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-06.csv)
- Blob SHA: `ed76e1f4af5ed2ac586244527c99460a051345b2`.
- Record dati: 40.
- Firme uniche: 40.
- Duplicati: 0.
- Bot: 7 record SPUTNIK, 33 record GAGARIN.
- Esiti ledger: 29 `ESITO_NON_VERIFICABILE`, 11 `NON_TRADE`.
- Nuovi segnali da aggiungere in questo audit: 0.
- Fill verificati: 0; SL verificati: 0; TP verificati: 0.
- Campione verificabile di trade: 0; win rate e average R: N/D.

Le 29 righe non verificabili includono 21 predizioni storiche e candidati non eseguiti; non rappresentano 29 trade. Le 11 righe NON_TRADE comprendono WATCH/pre-alert. Score, probabilità e label `COMPRA ORA` non provano un fill.

## 9. Fonti consultate

- GitHub Actions, ultime 100 esecuzioni per repository, distinguendo schedule, polling e test PR.
- Metadati job e step per SPUTNIK #42311247999, GAGARIN #42304574886 e polling #42317191549.
- Branch main, PR #147, #145, #146, #192, #175, #221, #223 e #224.
- SPUTNIK: `sputnik_state.json`, ledger PRAVDA e log collector #42311247999.
- GAGARIN: `journal.csv`, `paper_trade_log.csv`, `commodities_prediction_log.json`, `engine/feedback.py`, workflow monitor e polling.
- Nessun servizio a pagamento; nessun accesso Trading212 dichiarato; nessuna prova di consegna Telegram al dispositivo.

## 10. Lacune e prossimo controllo

1. Verificare un nuovo monitor di mercato per entrambi i bot e confrontare il timestamp reale con le cadenze cron dichiarate.
2. Verificare perché il polling GAGARIN ha un run `schedule` fuori dalla finestra cron e perché lo step polling continua a fallire.
3. Ottenere quotazioni fresche GAGARIN con ticker, mercato, contratto/scadenza, provider e timestamp.
4. Verificare che la PR #192 venga aggiornata sul main corrente e che i multi-TP nella stessa candela non vengano promossi al target più alto senza sequenza intrabar.
5. Per ogni futuro candidato SPUTNIK, richiedere ticker runtime, mercato, scadenza e quote provenance; non usare livelli di un future continuo non identificato.
6. Aggiungere al ledger soltanto nuove firme reali; valutare TP-first/SL-first solo su candele successive dello stesso identico strumento e contratto.

**Perimetro:** audit/documentazione e commenti di verifica PR soltanto. Nessuna modifica al codice dei bot, strategia, filtri, score o rischio; nessun merge, deploy, rerun, ordine reale, modifica a segreti o Render. PAPER ONLY.
