# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-06 17:20 UTC (18:20 Europe/Rome)**

## Sintesi esecutiva

- Nessun nuovo collector di mercato SPUTNIK dopo [#42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412), avviato alle 11:31:39 UTC e concluso alle 11:31:53 UTC. Gap al cut-off: **5h48m**.
- Nessun nuovo monitor prezzi GAGARIN dopo [#42203497432](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42203497432), avviato alle 10:32:52 UTC e concluso alle 10:33:10 UTC. Gap al cut-off: **6h47m**.
- Le 100 Actions più recenti di ciascun repository sono state esaminate distinguendo monitor, polling, riepiloghi, fetch ausiliari e test PR. Nessuna esecuzione ausiliaria è stata conteggiata come monitor di mercato.
- È stato trovato un WATCH GAGARIN non ancora presente nel ledger: Grano SHORT, pre-alert Telegram message_id 3701. Registrato una sola volta come NON_TRADE, senza trasformarlo in ingresso.
- Ledger aggiornato e verificato: **33 record, 33 firme uniche, 0 duplicati**.
- Nessun fill, SL o TP verificabile. Campione di outcome verificabili: **0**; win rate e average R: **N/D**.
- Nessun codice bot, strategia, filtro, punteggio o rischio modificato. Nessun merge, deploy, rerun o ordine reale.

## 1. GitHub Actions e continuità

### SPUTNIK
- Ultimo collector schedule: [#42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412), branch main, SHA eseguito `fbcb0de2bfe921383eee7edff10c5d9cf3d306d2`.
- Job `sputnik`: SUCCESS; il log mostra 30 test di item intelligence completati con OK.
- Cron dichiarato in `.github/workflows/trump_tracker.yml`: `2-59/5 * * * *`.
- Al cut-off non compare un collector successivo nelle 100 Actions più recenti.
- [Daily Summary #42226158074](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42226158074) alle 13:31:21 UTC è un riepilogo, non un collector.
- [Telegram Polling #42206505491](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42206505491) alle 10:56:51 UTC è polling, non un collector.
- La causa del gap di schedulazione non è dimostrata.

### GAGARIN
- Ultimo monitor prezzi: [#42203497432](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42203497432), branch main, SHA eseguito `7ed290b971e780828934d80aa3b936043769eaf6`.
- Job monitor: SUCCESS, concluso alle 10:33:10 UTC.
- Cron dichiarato in `.github/workflows/gagarin-monitor.yml`: `*/15 * * * *`.
- Nelle 100 Actions più recenti non compare un monitor prezzi successivo.
- [Daily Summary #42232309653](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42232309653) alle 14:15:30 UTC e [FETCH DRIVERS #42235888213](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42235888213) alle 14:39:35 UTC sono workflow ausiliari, non monitor prezzi.
- [Telegram Polling #42236174265](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42236174265) alle 14:41:31 UTC è fallito. Il log di `telegram/polling_runner.py` riporta Telegram API 409: webhook attivo, polling non consentito. La PR #175 resta OPEN; il precedente commento di audit [#6688546557](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175#issuecomment-6688546557) documentava già lo stesso conflitto. Nessun nuovo commento duplicato aggiunto.

## 2. SPUTNIK — segnali e fonti

### GOLD LONG — messaggi #707/#708, un solo candidato
Fonte: [collector #42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412).

| Campo | Valore |
|---|---|
| Firma ledger | `PRAVDA-SPUTNIK-CFD-RUN42210907412-20261106T113148Z-GOLD-LONG-4075.8999-4074.2713-4077.5285-4079.1570` |
| Generazione CFD | 11:31:48.567717 UTC |
| ACK API Telegram CFD | 11:31:48.569094 UTC |
| Messaggi | #707 analisi; #708 CFD |
| Strumento | GOLD |
| Mapping configurato | GC=F; ticker runtime effettivo non confermato |
| Mercato / scadenza | future continuo front-month; scadenza esatta UNKNOWN |
| Provider / timestamp / età quota | non esposti |
| Direzione | LONG preliminare |
| Entry / SL | 4075.8999 / 4074.2713 |
| TP1 / TP2 | 4077.5285 / 4079.1570 |
| ATR / score | 1.0857 / 70 |
| Stato | EARLY_SETUP / NOT_EXECUTED; livelli esplicitamente non operativi |

Il messaggio #707 riporta momentum tecnico LONG a 5m (+0,064% negli ultimi 15m), ma #708 riporta tecnica NOT_ASSESSED, D-L-A NEUTRAL/NO_DIRECTION, swing con massimi/minimi decrescenti ed EMA non univoche. Nessun catalizzatore direzionale verificato. NARWHAL è NOT_CONFIGURED e l'indipendenza upstream SILV non è verificata.

Il log mostra ACK API con round-trip 549ms e 437ms: ciò prova l'accettazione API e l'assegnazione dei message_id, non la consegna al dispositivo né un'esecuzione. Il message_id 731 compare nel blocco dei test di regressione con round-trip 0ms e non è stato conteggiato come alert di mercato.

Il collector ha registrato SEC HTTP 403 con cooldown di 21600s, White House RSS HTTPError, 0 filing, 0 nuove operazioni documentate, 0 correlazioni pubbliche e findings=0. Il handoff GAGARIN non è stato eseguito nel run. Mancano ticker risolto, scadenza, provider runtime, timestamp/age della quota e candele successive dello stesso contratto.

**Esito GOLD LONG: ESITO NON VERIFICABILE.** NOT_EXECUTED, non è un trade.

### Persistenza stato SPUTNIK
Verifica diretta del contenuto GitHub di `sputnik_state.json` su main:
- aggiornato a `2026-11-06T11:31:46.900527Z`;
- 500 record in `intelligence_history`;
- 670 elementi in `intelligence_items`;
- 0 eventi attivi, 0 transazioni;
- offset Telegram 275590742, `telegram_active=true`.
- Commit di persistenza: [6b91525](https://github.com/andreameloni1984-sys/trump-trucker/commit/6b91525e9ded6611696290e641ff74c4863f05de).

Lo stato è quindi popolato e persistito; non risulta però aggiornato da un collector successivo alle 11:31:46 UTC.

## 3. GAGARIN — dati, WATCH, journal e feedback

### Monitor #42203497432
Il log espone `DATABASE_URL` vuoto nel run e `PAPER_TRADING_ONLY=1`. Il runtime dichiara 8 commodity operative e 2 strumenti FX ausiliari, per un totale di 10 strumenti.

Questa è una discrepanza verificata: `GAGARIN_FOREX_ON_DEMAND=0`, ma il log dichiara comunque EUR/USD e GBP/USD ausiliari; entrambi sono stati letti da BIQUOTE e marcati LIVE (età circa 187s). La presenza FX nel percorso runtime è segnalata al reparto tramite commento PRAVDA sulla PR #221.

Quotazioni delle otto commodity:
| Strumento | Provider | Età quota | Stato |
|---|---|---:|---|
| Grano | YAHOO | 622,4 s | STALE |
| Brent | YAHOO | 604,3 s | STALE |
| WTI | YAHOO | 601,2 s | STALE |
| Oro | YAHOO | 614,5 s | STALE |
| Argento | YAHOO | 606,0 s | STALE |
| Rame | YAHOO | 607,1 s | STALE |
| Mais | YAHOO | 622,4 s | STALE |
| Soia | YAHOO | 664,5 s | STALE |

I timestamp assoluti delle quotazioni non sono esposti. Tutte le otto commodity sono state quindi trattate come stale; nessun prezzo spot/future o contratto è stato assunto per analogia.

### Grano SHORT — WATCH pre-alert
Nuovo record aggiunto al ledger:
- Firma: `PRAVDA-GAGARIN-WATCH-RUN42203497432-20261106T103308Z-GRAIN-SHORT`.
- Prima emissione della classificazione: 10:33:08.038252 UTC; il timestamp di rendering del messaggio non è esposto separatamente.
- ACK API Telegram: 10:33:08.040786 UTC; message_id 3701; round-trip 509ms.
- Strumento: Grano; ticker, mercato e scadenza non esposti.
- Provider: YAHOO; età quota 622,4s; timestamp assoluto non esposto.
- Direzione: SHORT; Prob 63,0, Quality 52,5, Confidence 35,0.
- Entry, SL, TP, ATR e score operativo: non esposti.
- Stato: PAPER_WATCH, bloccato da LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, RR_FAIL e FINAL_CONFLUENCE_FAIL.
- Outcome: NON_TRADE.

Il WATCH board include il candidato direzionale Grano; il log conferma un solo invio di WATCH pre-alert. Il messaggio API accettato non prova la consegna al dispositivo. Non è un ingresso e non entra in statistiche di trade.

### Output operativo e feedback del run
- Nessuna entrata autorizzata.
- PAPER JOURNAL: Recorded entries = 0.
- SOYUZ FEEDBACK: Updated open outcomes = 0; New feedback signals = 0; New additional live forecasts = 0.
- Scorecard: `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0 outcomes={}`.

### Artefatti GAGARIN su main
- `journal.csv`: 11 righe dati, tutte del 2026-10-17, tutte con esito “nessun segnale”.
- `paper_trade_log.csv`: una sola posizione WTI LONG legacy del 2026-10-08, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55. È etichettata LEGACY_IMPORT / PAPER_ENTRY / OPEN; provider, contratto, scadenza e fill non sono documentati. Nota originale: nessun esito. Non è conteggiata come trade verificato.
- `commodities_prediction_log.json`: 981 record; ultimo `created_at` = 2026-09-15T15:45:04.462276Z. I record finali sono PENDING, anche quando l'action label è COMPRA ORA.
- `gagarin_feedback.csv`: non presente nel tree pubblico di main. Il modulo `engine/feedback.py` esiste e supporta CSV locale/PostgreSQL; il run log mostra `DATABASE_URL` vuoto e nessuna nuova riga/outcome. Il workflow dichiara che i journal privati non vanno committati e che la persistenza sarà riattivata dopo storage privato verificato. Non si assume accesso a dati privati non esposti.

## 4. PR e correzioni già esistenti

### SPUTNIK
- PR [#144](https://github.com/andreameloni1984-sys/trump-trucker/pull/144), persistenza stato fuori da main: OPEN, non merged. Head `e935bc3d...`; il run [#42258805887](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42258805887) sul relativo head ha test ranking SUCCESS. La base registrata della PR è precedente al main corrente, quindi verificare l'aggiornamento del branch prima di qualunque futura integrazione.
- PR [#143](https://github.com/andreameloni1984-sys/trump-trucker/pull/143), classificazione token/domains: OPEN, non merged; le suite ranking e item-intelligence [#42243656376](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42243656376) e [#42243656439](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42243656439) sono SUCCESS.

### GAGARIN
- PR [#221](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221), rimozione rotte FX residue: OPEN/DRAFT, head `74999010cf9a5dcb59d7214bb3a865eb25d24bc4`, base main `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`. Integration test [#42245355490](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42245355490) e execution test [#42245355476](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42245355476) SUCCESS. La conversazione PR contiene inoltre un avviso Cloudflare Workers di deployment fallito per `telegram-github-bridge` sul commit 74999010; è distinto dai test verdi e non dimostra un deploy GAGARIN riuscito.
- Commento di audit PRAVDA aggiunto a [PR #221](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221#issuecomment-6691014816), con evidenza runtime su FX ausiliario, quotazioni stale e feedback vuoto.
- PR [#175](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175) per webhook/polling: OPEN; conflitto 409 confermato dal run #42236174265.
- PR [#91](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/91), [#94](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/94), [#97](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/97) e [#98](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/98) per outcome cronologico, copertura e ambiguità same-bar risultano ancora OPEN/DRAFT; non sono integrate su main.

## 5. Ledger e statistiche

Ledger: [`reports/pravda-signal-ledger-2026-11-06.csv`](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-06.csv)
- Record: 33.
- Firme uniche: 33.
- Duplicati: 0.
- Per bot: GAGARIN 28; SPUTNIK 5.
- Per tipo: 21 historical_prediction_candidate; 1 legacy_paper_ticket; 6 watch_pre_alert; 5 cfd_early_setup_not_executed.
- Outcome: 27 ESITO_NON_VERIFICABILE; 6 NON_TRADE.
- Fill verificati: 0; SL verificati: 0; TP verificati: 0; outcome verificabili: 0.
- Win rate e average R: N/D.

Il nuovo Grano SHORT WATCH è stato aggiunto una sola volta. Le 21 predizioni PENDING, la posizione WTI legacy e i candidati SPUTNIK NOT_EXECUTED non sono stati trasformati in trade.

## 6. Fonti consultate

- GitHub Actions: ultime 100 esecuzioni di entrambi i repository; job details e log completi dei monitor #42210907412, #42203497432 e polling #42236174265.
- GitHub: branch main, tree ricorsivo, contenuti di `sputnik_state.json`, ledger PRAVDA, `journal.csv`, `paper_trade_log.csv`, `commodities_prediction_log.json`, `engine/feedback.py`, `main.py`, `telegram/signals.py` e workflow YAML.
- Metadati e discussioni PR #143, #144, #175, #221 e PR di outcome #91/#94/#97/#98.
- Nessun servizio a pagamento. Nessun accesso Trading212 dichiarato. Nessuna prova di consegna Telegram al dispositivo.

## 7. Prossimo controllo

1. Verificare se i monitor SPUTNIK e GAGARIN riprendono, controllando il commit effettivamente eseguito e non i soli riepiloghi.
2. Per ogni nuovo output salvare ticker runtime, mercato, scadenza, provider, timestamp/age quota, timestamp generazione e ACK API.
3. Per GAGARIN verificare che la scansione attiva non includa più EUR/USD/GBP/USD se la PR #221 viene integrata, e che i dati delle otto commodity siano freschi.
4. Verificare persistenza feedback e journal soltanto attraverso un artefatto o backend effettivamente osservabile; non inferire lo stato di storage privato.
5. Per ogni candidato operativo, confrontare esclusivamente candele successive dello stesso identico ticker/contratto e timeframe; prima barriera raggiunta = SL o TP, simultaneità intrabar non risolta = non attribuire un esito favorevole, dati mancanti = ESITO NON VERIFICABILE.

**Perimetro:** audit e aggiornamento del ledger/documentazione soltanto. Nessuna modifica al codice dei bot, alle strategie, ai filtri, ai punteggi o al rischio; nessun merge, deploy, rerun, ordine reale, modifica di segreti o Render. PAPER ONLY.
