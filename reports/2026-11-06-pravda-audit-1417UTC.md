# PRAVDA — audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-06 14:17:40 UTC (15:17:40 Europe/Rome)**

## Sintesi esecutiva

- Nessun nuovo segnale individuale completo rispetto al ledger esistente.
- SPUTNIK: ultimo collector di mercato su main ancora il run **#42210907412**, avviato 11:31:39 UTC e concluso 11:31:53 UTC. Al cut-off: 2h46m01s senza un collector successivo.
- GAGARIN: ultimo monitor di mercato ancora il run **#42203497432**, avviato 10:32:52 UTC e concluso 10:33:10 UTC. Al cut-off: 3h44m48s senza un monitor successivo.
- I run più recenti di riepilogo giornaliero non sono monitor di mercato: SPUTNIK Daily Summary #42226158074 (13:31:21 UTC); GAGARIN Daily Summary #42232309653 (14:15:30 UTC).
- Ledger: 32 record, 32 firme uniche, zero duplicati. Nessuna modifica al CSV.
- Fill, TP, SL e outcome verificabili sul medesimo strumento/contratto: zero. Win rate e average R: N/D.

## 1. Cronologia GitHub Actions

### SPUTNIK

- Cron su main: `2-59/5 * * * *` (workflow `.github/workflows/trump_tracker.yml`).
- Ultimo collector di mercato nella prima pagina dei 100 run più recenti: [#42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412), run 279, avvio 11:31:39 UTC, job `127869016098`, completamento 11:31:53 UTC, SUCCESS.
- Collector precedente: [#42157892570](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42157892570), avvio 03:39:45 UTC. Gap fra i due collector: **7h51m54s**.
- Al cut-off, età dall'ultimo collector: **2h46m01s**.
- [Daily Summary #42226158074](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42226158074), 13:31:21–13:31:31 UTC, è un riepilogo e non un collector.
- Il run collector ha `findings=0`; WHITE_HOUSE, TRUTH_ARCHIVE e OGE riportano OSError; SEC HTTP 403; White House RSS HTTPError. `NARWHAL_API_KEY` è vuota. Il log mostra comunque messaggi Telegram API confermati, non prova di consegna al dispositivo.

### GAGARIN

- Cron su main: `*/15 * * * *` (workflow `.github/workflows/gagarin-monitor.yml`).
- Ultimo monitor di mercato nella prima pagina dei 100 run più recenti: [#42203497432](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42203497432), run 159, avvio 10:32:52 UTC, job `127844292744`, completamento 10:33:10 UTC, SUCCESS.
- Al cut-off, età dall'ultimo monitor: **3h44m48s**.
- [Daily Summary #42232309653](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42232309653), 14:15:30–14:15:39 UTC, è un riepilogo feedback. Il job esegue `summarize()` e invia un testo Telegram; stampa `Summary sent`, ma non espone message_id né esegue il monitor delle quotazioni. Non va contato come run di mercato.
- I commit main osservati: SPUTNIK `535cd65539aed3c4b2e1b0e84e9cbe6980c40bb6` (documentazione PRAVDA); GAGARIN `7ed290b971e780828934d80aa3b936043769eaf6`.

## 2. Segnale SPUTNIK già registrato — GOLD LONG

Messaggi #707 (analisi) e #708 (CFD) del run #42210907412 sono un'unica ipotesi e sono già presenti nel ledger una sola volta.

- Firma: `PRAVDA-SPUTNIK-CFD-RUN42210907412-20261106T113148Z-GOLD-LONG-4075.8999-4074.2713-4077.5285-4079.1570`.
- Generazione CFD: 2026-11-06 11:31:48.567717 UTC.
- ACK API #707: 11:31:48.567503 UTC; ACK API #708: 11:31:48.569094 UTC. ACK API non equivale a fill né prova consegna al dispositivo.
- Strumento: GOLD; mapping configurato GC=F, ticker runtime non confermato; mercato dichiarato future continuo front-month; scadenza UNKNOWN.
- Provider runtime, timestamp e anzianità della quotazione non esposti; Narwhal non configurato.
- Direzione preliminare LONG; entry 4075.8999; SL 4074.2713; TP1 4077.5285; TP2 4079.1570; ATR 1.0857; score 70; stato `EARLY_SETUP / NOT_EXECUTED`.
- Incoerenza interna: messaggio analisi LONG 5m (+0,064%/15m), ma messaggio CFD tecnica `NOT_ASSESSED`, D-L-A `NEUTRAL / NO_DIRECTION`, swing con massimi/minimi decrescenti ed EMA non univoche. Nessun catalizzatore direzionale verificato.
- I livelli sono esplicitamente dichiarati non utilizzabili sul future continuo senza scadenza e indipendenza upstream verificate.

**Esito: ESITO NON VERIFICABILE.** Nessun fill e nessuna candela successiva disponibile/identificata sul medesimo contratto e scadenza. Non si usa XAU/USD spot per attribuire TP/SL al future continuo.

## 3. GAGARIN — prezzi, candidati e journal

Nel monitor #42203497432 tutte le otto commodity erano stale su Yahoo:
- Grano 622,4 s; Brent 604,3 s; WTI 601,2 s; Oro 614,5 s; Argento 606,0 s; Rame 607,1 s; Mais 622,4 s; Soia 664,5 s.
- EUR/USD e GBP/USD erano LIVE su BiQuote, ma sono Forex ausiliario e non sostituiscono le quotazioni commodity.
- Il candidato Grano SHORT era `PAPER_WATCH` (probabilità 63, qualità 52,5, confidenza 35), bloccato da `LIVE_DATA_NOT_FRESH`, `TRIGGER_NOT_CONFIRMED`, `TRIGGER_DIRECTION_MISMATCH`, `RR_FAIL` e `FINAL_CONFLUENCE_FAIL`.
- Gli altri candidati non avevano livelli operativi completi. Output: `signals=0 open=0 closed=0`; outcome aggiornati 0; nuovi feedback 0.
- Telegram message 3701 è stato accettato dall'API (509 ms), come WATCH board, non trade.

Artefatti main:
- `journal.csv`: 11 righe del 17 ottobre, tutte `nessun segnale`.
- `paper_trade_log.csv`: un WTI LONG legacy del 8 ottobre, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55; provider/contratto/fill/outcome non dimostrati.
- `data/paper_open.json` P0001 contiene gli stessi livelli WTI: stessa posizione logica, non un secondo trade.
- `position.json`: Heating Oil LONG legacy del 15 settembre, senza provenienza sufficiente per outcome.
- `commodities_prediction_log.json`: 981 record, ultimo `created_at` 2026-09-15T15:45:04.462276Z; PENDING/COMPRA ORA non prova esecuzione.
- `gagarin_feedback.csv`: 404/non presente su main.
- Nel job `DATABASE_URL` e `NARWHAL_API_KEY` sono vuote; persistenza DB non dimostrata.

## 4. PR aperte e difetti già noti

SPUTNIK:
- [#141](https://github.com/andreameloni1984-sys/trump-trucker/pull/141) persistenza fuori da main: OPEN, non merged.
- [#136](https://github.com/andreameloni1984-sys/trump-trucker/pull/136) provenienza quote CFD: OPEN, non merged.
- [#138](https://github.com/andreameloni1984-sys/trump-trucker/pull/138) diagnostica gap schedulazione: OPEN, non merged.
- [#142](https://github.com/andreameloni1984-sys/trump-trucker/pull/142) calendario BLS/USDA: OPEN, non merged.

GAGARIN:
- [#181](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/181) provenienza quotazioni: OPEN.
- [#198](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/198) ripristino ranking baseline: OPEN/DRAFT.
- [#212](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/212) universo otto commodity: OPEN/DRAFT.
- [#217](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/217) rifiuto identità CFD scadute: OPEN/DRAFT.

Il file main `engine/prediction_ranker.py` conserva l'aggiustamento momentum fino a +8/−4 (blob SHA `7ebee56d2b439596c69531b3dc7c6664c9d4905b`); la PR #198 non è integrata. Nessuna modifica è stata fatta da PRAVDA.

## 5. Ledger e statistiche

Il CSV `reports/pravda-signal-ledger-2026-11-06.csv` è stato letto direttamente:
- 32 record, 32 firme uniche, zero duplicati.
- Nessun nuovo segnale individuale completo da aggiungere.
- Fill verificati 0; TP verificati 0; SL verificati 0; outcome verificabili sul contratto esatto 0.
- Win rate e average R: N/D.

## 6. Segnalazione al reparto SPUTNIK

Il nuovo gap è stato aggiunto come evidenza alla [PR #138](https://github.com/andreameloni1984-sys/trump-trucker/pull/138): ultimo collector #42210907412 alle 11:31:39 UTC; precedente #42157892570 alle 03:39:45 UTC; gap 7h51m54s; al cut-off nessun collector successivo e cron main ogni 5 minuti. La causa tecnica del gap resta non determinata: non attribuirla a coda, Telegram o test senza evidenza.

## Prossimo controllo

1. Separare collector/monitor dai Daily Summary, polling e CI.
2. Verificare la ripresa dei collector SPUTNIK ogni 5 minuti e dei monitor GAGARIN ogni 15.
3. Controllare ticker runtime, mercato, scadenza, provider, timestamp e freschezza delle quote.
4. Verificare storage/journal e integrazione effettiva delle PR, non soltanto CI verde.
5. Valutare outcome solo con candele successive dello stesso identico contratto e scadenza, rispettando la sequenza SL prima / TP prima.

**Perimetro:** questo audit modifica soltanto la documentazione PRAVDA e aggiunge un commento probatorio alla PR #138. Nessun codice o workflow dei bot, strategia, filtro, punteggio o rischio modificato; nessun merge/deploy, ordine reale, modifica a segreti/Render o servizio a pagamento. Nessuna affermazione di accesso Trading 212 o consegna Telegram al dispositivo. PAPER ONLY.
