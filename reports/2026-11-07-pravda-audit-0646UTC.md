# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Controllo:** 2026-11-07 06:46 UTC (07:46 Europe/Rome)  
**Perimetro:** GitHub Actions, log completi dei job, segnali e messaggi, ledger PRAVDA, journal pubblici, motore feedback, PR e CI. **PAPER ONLY**.

## Sintesi esecutiva

- Nessun nuovo monitor di mercato su `main` dopo SPUTNIK run **#42331705890** (02:57:24 UTC) e GAGARIN run **#42328183997** (02:13:56 UTC). Alla finestra di controllo i gap erano circa **3h49m SPUTNIK** e **4h32m GAGARIN**, nonostante cron ogni 5 e 15 minuti.
- Le ultime Actions di test non sono monitor di mercato: SPUTNIK PR #148 e GAGARIN PR #231/#204 hanno CI verdi, ma restano branch non integrati.
- SPUTNIK ha prodotto nuovamente GOLD #715/#716: stesso candidato EARLY_BIAS, nessun nuovo catalizzatore, nessun livello operativo e `NOT_EXECUTED`.
- GAGARIN ha prodotto tre WATCH direzionali nel monitor di sabato: WTI SHORT, Mais LONG, Argento LONG. Tutte le commodity erano `MARKET_CLOSED`; nessuna entry/SL/TP/ATR e nessuna autorizzazione di ingresso.
- Ledger del 7 novembre: **45 record, 45 firme uniche, zero duplicati**. Nessun nuovo record: i messaggi #715/#716 e il board #3711 erano già registrati.
- **0 fill verificati, 0 SL/TP verificati, win rate e average R N/D.** Non è disponibile un campione di trade con outcome verificabile.
- Nuovo rilievo di sicurezza operativa: PR draft #231 ha un commento Cloudflare che segnala un build del servizio `telegram-github-bridge/production` **fallito** sul commit `047abbc8` (stato aggiornato alle 06:50 UTC). PRAVDA non ha avviato né approvato quel build.

## 1. GitHub Actions e cron

### SPUTNIK
- Monitor: [run #42331705890](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42331705890), job #128279494938, SUCCESS, 02:57:24 UTC, checkout SHA `41fb6081c649f28378d2fe0dfed8aa18cffe9dff`.
- Cron su main: `2-59/5 * * * *`.
- Polling Telegram separato: [run #42329017675](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42329017675), SUCCESS, 02:23:33 UTC. Non è una scansione di mercato.
- Nessun successivo evento schedule del monitor nella finestra interrogata.

### GAGARIN
- Monitor: [run #42328183997](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42328183997), job #128268295697, SUCCESS, 02:13:56 UTC, checkout SHA `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`.
- Cron su main: `*/15 * * * *`.
- Polling Telegram: [run #42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549), FAILURE, 00:16:15 UTC. Il log conferma `409 — webhook is active; polling cannot run`. Token validation superata; fallisce `getUpdates`.
- La run polling è marcata `event=schedule` di sabato alle 00:16 UTC, fuori dal cron dichiarato `*/5 7-21 * * 1-5`. L'anomalia dei metadati è verificata; la causa non è dimostrata.
- Nessun successivo monitor schedule GAGARIN nella finestra interrogata.

## 2. SPUTNIK — messaggi #715/#716

Produzione del job #128279494938:
- Run iniziato alle 02:57:29.812865 UTC; scan intelligence 1.226 ms, `findings=0`.
- SEC CIK 0001849635: HTTP 403; `filings=0`.
- White House RSS configurato su `https://www.whitehouse.gov/feed/`: HTTPError.
- `0` filing nuovi, `0` nuove operazioni documentate, `0` nuove correlazioni pubbliche; allineamento `NO_DIRECTIONAL_NEWS`.
- `GAGARIN forwarding=0ms`: nessun handoff di produzione.

Messaggi effettivi:
- #715: GOLD, bias preliminare NEUTRAL, score/priorità 70, tecnica UNAVAILABLE, NO_DIRECTIONAL_NEWS, WATCH.
- #716: GOLD, bias CFD LONG solo tecnico, D-L-A NEUTRAL/NO_DIRECTION; EARLY_BIAS, `TRADE PAPER: NOT_EXECUTED`. Entry/SL/TP/ATR omessi perché non disponibile una quotazione futures fresca o ATR valido.
- Telegram API acceptance: #715 483 ms; #716 401 ms. L'ACK API non dimostra visualizzazione sul dispositivo né esecuzione.
- GC=F è mapping configurato; ticker runtime non confermato. Il messaggio dichiara front-month continuo, ma scadenza esatta e indipendenza upstream non verificate. Provider e timestamp della quotazione non esposti.

**Esito:** NON_TRADE / NOT_EXECUTED; nessun outcome finanziario valutabile. #715/#716 ripetono la tesi GOLD #713/#714 senza nuovo catalizzatore.

### Distinzione test/produzione
Il job esegue unit test prima del collector. Le righe di test con OSError simulati per WHITE_HOUSE/TRUTH_ARCHIVE/OGE, una “GAGARIN confirmation” e message_id=731 appartengono ai test, non alla produzione. Non sono state conteggiate come fonte live, handoff o invio reale. In produzione sono confermati solo SEC 403, White House RSS HTTPError, zero finding e forwarding GAGARIN a zero.

La precedente lettura di 500 elementi in `sputnik_state.json` resta l'ultima verifica disponibile: il file è grande e non è stato nuovamente leggibile in questo controllo. Non si dichiara una nuova verifica della persistenza.

## 3. GAGARIN — run #42328183997

### Dati
Tutte le otto commodity sono `MARKET_CLOSED`, provider YAHOO:

| Strumento | Età quota |
|---|---:|
| Brent | 15.267,6 s |
| WTI | 15.253,4 s |
| Soia | 24.853,0 s |
| Oro | 15.251,0 s |
| Grano | 24.852,7 s |
| Mais | 24.855,8 s |
| Argento | 15.252,1 s |
| Rame | 15.263,2 s |

Il sabato e il market status spiegano l'assenza di quotazioni correnti; l'età stale non prova da sola un guasto del provider. Ticker runtime, market type, scadenza e timestamp della singola quotazione non sono esposti nel riepilogo.

### Classifica
- Brent: nessuna direzione, 58/40/25; setup e livelli mancanti.
- WTI: SHORT, probabilità 66, quality 57,5, confidence 37; bloccato da dati non freschi, trigger non confermato e mismatch.
- Soia: nessuna direzione, 50/30/15.
- Oro: nessuna direzione, 50/30/15.
- Grano: nessuna direzione, 38/15/5.
- Mais: LONG, 63/52,5/35; bloccato da dati non freschi, trigger non confermato/mismatch e RR.
- Argento: LONG, 59/49,5/32; bloccato da dati non freschi, trigger non confermato/mismatch, RR1 e confidence.
- Rame: nessuna direzione, 50/30/15.

Tutte le righe sono `PAPER_WATCH`; nessuna ha entry, SL, TP o ATR operativi. EUR/USD e GBP/USD compaiono solo come `CONTESTO FX — NON OPERATIVO`; `GAGARIN_FOREX_ON_DEMAND=0`.

Board #3711: API accepted alle 02:14:13.6555025 UTC, 472 ms. Il corpo non è conservato, quindi non viene attribuito a WTI/Mais/Argento e non prova la consegna sul dispositivo. Le tre classificazioni WATCH hanno `sent_at` vuoto: non risultano alert individuali.

Il workflow main espone soglie runtime 40/30/35 e RR 2.5, stop ATR max 2.5, buffer 0.15, SL min ATR 0.80, monitor 15m. PRAVDA non ha modificato questi valori.

## 4. Journal e feedback GAGARIN

File pubblici su main:
- [journal.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/journal.csv): 11 righe del 17 ottobre, tutte `nessun segnale`.
- [paper_trade_log.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/paper_trade_log.csv): un WTI LONG `LEGACY_IMPORT`, entry 96.24, stop 89.37, TP1 103.11; nota “nessun esito”. Non prova un fill.
- [position.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/position.json): vecchia posizione Heating Oil LONG aperta il 15 settembre; nessuna prova indipendente di fill.
- `paper_open.json`: 404/assente.
- `gagarin_feedback.csv`: 404/assente.
- [commodities_prediction_log.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities_prediction_log.json): 981 record storici fino al 15 settembre; 945 PENDING, 36 NEUTRALE, 960 WAIT e 15 LONG. PENDING/COMPRA ORA non provano un fill.

Il run mostra `DATABASE_URL` vuoto, `Recorded entries=0`, `New feedback signals=0`, `New additional live forecasts=0`. Il workflow main dichiara i journal come dati privati e non li committa; il backend locale non costituisce persistenza durevole tra runner.

## 5. Motore outcome

Su main, [engine/feedback.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py):
- fingerprint e matching non includono l'identità completa di provider/ticker/mercato/scadenza;
- l'associazione delle candele avviene per simbolo/timeframe;
- SL e TP toccati nella stessa OHLC candle vengono classificati STOP;
- più TP toccati nella stessa candela vengono valutati con `idx=max(hit_targets)`, cioè il target più alto senza prova intrabar.

[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) aggiunge provider/ticker/market/contract month/expiry alla firma, controlla l'identità del contratto e rende SAME_CANDLE_SL_TP `ESITO NON VERIFICABILE`. Rimane però `idx=max(hit_targets)` anche sul branch. Il branch è 6 commit avanti e 3 indietro rispetto a main (diverged); CI verde sul branch non equivale a correzione attiva su main.

## 6. PR e correzioni già esistenti

| PR | Stato osservato | Rilievo |
|---|---|---|
| SPUTNIK #148 | OPEN, 2 suite SUCCESS | Gate contro raccomandazioni ripetute senza nuovo item/catalizzatore; non integrata. |
| SPUTNIK #147 | OPEN, 2 suite SUCCESS | Rimozione handoff GAGARIN; non integrata. |
| SPUTNIK #145 | OPEN, test SUCCESS | Provenienza quotazioni e log errori Yahoo; non integrata. |
| GAGARIN #231 | DRAFT, 31 commit ahead/0 behind, 4 suite SUCCESS | Consolidamento universo, Telegram, calendario e Governor; include Silver nel full scope. |
| GAGARIN #204 | DRAFT, 10 ahead/1 behind, 6 suite SUCCESS | Separa osservazioni manuali Trading 212 CFD dai futures Yahoo; non dichiara API/account access e non calcola livelli senza serie CFD dello stesso contratto. |
| GAGARIN #192 | OPEN, 6 ahead/3 behind, 6 suite SUCCESS | Identità contratti e ambiguità same-candle; resta il TP multiplo non ordinabile intrabar. |
| GAGARIN #223 | DRAFT, 10 ahead/0 behind, 5 suite SUCCESS | M5 osservativo ogni 5m su 7 strumenti, Silver escluso; nessun alert, entry, journal o ordine; nessun run live. |
| GAGARIN #225 | DRAFT, 2 ahead/0 behind, 5 suite SUCCESS | Offset monitor 7/22/37/52, mantiene 15m; non integrata. |
| GAGARIN #175 | OPEN, non integrata | Gestione 409 webhook con polling skipped, senza cancellare webhook o ack updates. |
| GAGARIN #202 / #200 | DRAFT | Persistenza PostgreSQL del journal e uso del medesimo store nel daily summary; DATABASE_URL resta vuoto nel run verificato. |
| GAGARIN #201 | DRAFT | Fallback Yahoo query1/query2 per quote stale; endpoint mirror dello stesso provider, non fonte indipendente. |
| GAGARIN #181 / #184 | OPEN, non integrate | Provenienza quote nel riepilogo e distinzione API acceptance/device delivery. |

### Rilievo Cloudflare
Le timeline di PR #204, #223 e #225 riportano build Cloudflare per `telegram-github-bridge/production` falliti. La timeline di PR #231 riporta il build per lo stesso servizio/target come *In progress* alle 06:47:57 UTC e poi **Deployment failed** alle 06:50 UTC sul commit `047abbc8` ([commento Cloudflare](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/231#issuecomment-6703548421)). PRAVDA non ha avviato questi build, non ha fatto merge/deploy e non ha accesso al pannello Cloudflare. I build production su branch draft richiedono verifica delle regole Git integration prima di ulteriori push.

### Perimetro Silver
La richiesta precedente di escludere Silver dalla scansione non risulta applicata al monitor completo: main ha ancora Argento nella classifica; PR #223 lo esclude soltanto dal nuovo M5 osservativo ma dichiara che resta nel wider universe; PR #231 include Silver nell'universo completo di otto strumenti. PRAVDA ha segnalato il mismatch nel commento [PR #231 #6703560974](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/231#issuecomment-6703560974). Nessuna modifica a strategia o codice è stata eseguita.

## 7. Ledger PRAVDA

CSV main: [pravda-signal-ledger-2026-11-07.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-07.csv), blob SHA `9c58b42b70c7aaf92a161b553c9eee8c1f2be52a`.

Parsing CSV completo:
- 45 righe dati; 45 firme uniche; zero duplicati.
- 37 record GAGARIN, 8 SPUTNIK.
- 29 `ESITO_NON_VERIFICABILE`; 16 `NON_TRADE`.
- Campione con fill verificato: 0; SL/TP verificati: 0; win rate e average R: N/D.
- Campi mancanti/NOT_RECORDED su 45 righe: sent_at 28; ticker 7; market_type 26; contract_expiry 37; provider 22; quote_timestamp 26; entry/SL/TP1 17 ciascuno; ATR 33. Molti record sono WATCH/NOT_EXECUTED/legacy, quindi i livelli mancanti non sono fill omessi: sono lacune di tracciabilità da distinguere per record type.

Nessuna nuova firma da aggiungere: il ledger resta invariato. Non sono stati ricostruiti backtest o outcome da prezzi non omogenei.

## 8. Fonti e prossimo controllo

Fonti consultate:
- GitHub Actions e log: SPUTNIK #42331705890; GAGARIN #42328183997; GAGARIN polling #42317191549; SPUTNIK polling #42329017675.
- File main: `trump_tracker.yml`, `gagarin-monitor.yml`, `telegram-polling.yml`, `engine/feedback.py`, `journal.csv`, `paper_trade_log.csv`, `position.json`, `commodities_prediction_log.json`, ledger PRAVDA.
- PR/CI: #145/#147/#148 SPUTNIK; #175/#181/#184/#192/#200/#201/#202/#204/#223/#225/#231 GAGARIN.

Prossimo controllo:
1. verificare la prima nuova esecuzione monitor su main e misurare il gap reale;
2. alla riapertura dei mercati, controllare quote fresche, ticker runtime, timestamp e scadenza dei contratti;
3. verificare su main la correzione del matching contratto e delle ambiguità TP multipli;
4. verificare persistenza journal solo se il backend privato risulta effettivamente configurato e disponibile;
5. controllare lo stato finale del build Cloudflare segnalato sulla PR #231 e la regola che lo ha avviato.

**PAPER ONLY.** Nessun ordine reale, nessun merge, nessun deploy o rerun avviato da PRAVDA; nessuna modifica a codice, strategia, filtri, punteggi, rischio, segreti, Render o account broker. Nessun accesso Trading 212 dichiarato.
