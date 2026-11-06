# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-06 19:05:38 UTC (20:05:38 Europe/Rome)**

## Sintesi esecutiva

- SPUTNIK ha effettuato un collector alle 18:22:24 UTC dopo un gap di 6h50m45s rispetto al collector precedente. Non risulta un altro collector successivo nel controllo delle 100 Actions più recenti.
- GAGARIN ha effettuato un monitor alle 17:41:19 UTC dopo un gap di 7h08m27s rispetto al monitor precedente. Non risulta un altro monitor prezzi successivo nel controllo delle 100 Actions più recenti.
- Sono stati aggiunti due record al ledger: un candidato CFD SPUTNIK GOLD SHORT `NOT_EXECUTED` e un pre-alert WATCH GAGARIN con contenuto del messaggio non conservato.
- Ledger aggiornato e riletto: **35 record, 35 firme uniche, zero duplicati**.
- Nessun fill, SL o TP verificato; nessuna candela successiva dello stesso identico contratto disponibile. Win rate e average R restano N/D.
- Nessuna modifica al codice dei bot, nessun merge/deploy, nessun ordine reale. Solo aggiornamento del ledger/rapporto e commenti di audit su PR esistenti.

## 1. GitHub Actions e continuità dei monitor

### SPUTNIK

- Ultimo collector: [run #42270098789](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42270098789), schedule, 2026-11-06 18:22:24 UTC, concluso 18:22:35 UTC, SUCCESS.
- Commit eseguito dal collector: `0439dca9cfa0e349c3cb2237fd4aeb78bd110f00`; il run ha scritto `sputnik_state.json` su `main`.
- Collector precedente: [#42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412), avvio 11:31:39 UTC. Gap tra collector: **6h50m45s**.
- Al cut-off il collector più recente aveva 43m14s. Le 100 Actions più recenti non mostrano un altro collector schedule dopo le 18:22; il polling Telegram e i test PR sono workflow distinti e non sono monitor di mercato.
- Il workflow dichiara una cadenza di 5 minuti, ma le esecuzioni osservate non la rispettano. La causa tecnica del gap non è dimostrata.

Il run esegue 30 test automatici prima del collector. Il messaggio #731 appare nel blocco di test con risposta Telegram simulata; **non è una notifica di produzione e non è stato contato**. I messaggi del collector reale sono #710 (digest), #711 (analisi) e #712 (CFD).

### GAGARIN

- Ultimo monitor: [run #42263910777](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42263910777), schedule, 2026-11-06 17:41:19 UTC, concluso 17:41:37 UTC, SUCCESS, commit main `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`.
- Monitor precedente: [#42203497432](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42203497432), avvio 10:32:52 UTC. Gap tra monitor: **7h08m27s**.
- Al cut-off il monitor più recente aveva 1h24m19s. Nelle 100 Actions più recenti non compare un altro monitor prezzi.
- Il workflow dichiara `MONITOR_INTERVAL_MINUTES=15`; il ritmo osservato non rispetta la cadenza. Non attribuisco il gap a una causa non provata.
- Il run ha completato l'analisi, ma non ha registrato nuove entrate né aggiornato outcome.

## 2. SPUTNIK — candidato GOLD SHORT, non eseguito

Fonte: [Actions #42270098789](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42270098789).

### Identificazione e invio

- Record unico: `PRAVDA-SPUTNIK-CFD-RUN42270098789-20261106T182232Z-GOLD-SHORT-4069.3-4071.7536-4066.8465-4064.3929`.
- Strumento: GOLD.
- Ticker configurato: GC=F; **ticker risolto dal runtime non esposto**.
- Mercato: future continuo front-month; scadenza esatta UNKNOWN.
- Provider, timestamp e anzianità della quotazione: non esposti nel run/alert.
- Generazione CFD: 18:22:32.111256 UTC; API ACK #712: 18:22:32.112773 UTC (round-trip dichiarato 311 ms).
- Messaggio di analisi collegato #711: API ACK 18:22:32.110085 UTC (300 ms); digest #710: 377 ms.
- Gli ACK dimostrano accettazione API e assegnazione message_id, **non** consegna al dispositivo né esecuzione.

### Contenuto del candidato

| Campo | Valore |
|---|---:|
| Bias preliminare | SHORT |
| Direzione tecnica CFD | LONG — CONTRASTS |
| D-L-A | LONG — CONTRASTS |
| Entry stampata | 4069.3 |
| SL stampato | 4071.7536 |
| TP1 | 4066.8465 |
| TP2 | 4064.3929 |
| ATR | 1.6357 |
| Score | 70/100 |
| Stato | EARLY_SETUP / NOT_EXECUTED |

La scheda #711 dice SHORT tecnico a 5m e momentum -0,020% negli ultimi 15 minuti; la scheda CFD #712 mostra invece tecnica LONG e D-L-A LONG, entrambi in contrasto con il bias SHORT. L'allineamento notizie è `NO_DIRECTIONAL_NEWS`. Il messaggio segnala esplicitamente che il mercato è contro il bias.

La scheda avverte: front-month continuo, scadenza esatta e indipendenza upstream non verificate; non usare i livelli come entry/SL/TP. NARWHAL è NOT_CONFIGURED; l'indipendenza upstream SILV non è verificata; anche il controllo basis spot/futures è dichiarato non indipendente. I numeri stampati non diventano per questo livelli operativi validati.

**Esito: ESITO NON VERIFICABILE.** Mancano provider runtime, timestamp/age della quota, ticker risolto, scadenza esatta e candele successive dello stesso contratto. Non è un trade.

### Fonti intelligence e ritardi

Il collector riporta 4 nuove correlazioni, ma il digest presenta 2 nuovi item pubblici verificabili:
- [Item 43495](https://www.trumpstruth.org/statuses/43495): pubblicato 12:01:50 UTC, rilevato 18:22:30.541789 UTC; ritardo circa **6h20m40s**. Il testo parla di Super Intelligence/AI e usa “They are GOLD” in senso figurato; lo state lo tagga `METALS`, ma l'evento è `OTHER` senza analogo storico. È un falso positivo semantico di dominio, non un catalizzatore oro verificato.
- [Item 43496](https://www.trumpstruth.org/statuses/43496): pubblicato 18:05:27 UTC, rilevato 18:22:30.541519 UTC; ritardo circa **17m04s**. È un endorsement politico/RNC, non un catalizzatore commodity dimostrato.

Il run registra SEC HTTP 403 con cooldown 21.600 secondi, White House RSS HTTPError, zero filing e zero nuove operazioni documentate. Due degli altri record nello state sono risposte page-level TRUTH_ARCHIVE/OGE, non item di mercato. Il handoff SPUTNIK→GAGARIN è disabilitato perché `GAGARIN_CLOUD_API_URL/API_KEY` non sono configurati.

Lo state su main al termine del run riporta `updated_at=18:22:30.578530Z`, 500 record `intelligence_history`, zero eventi attivi e Telegram offset 275590742. La persistenza su main è quindi dimostrata; la PR #144 che propone il branch dedicato non è ancora integrata.

## 3. GAGARIN — monitor, quotazioni e WATCH

Fonte: [Actions #42263910777](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42263910777).

### Freschezza dati

Le otto commodity operative sono tutte `STALE`, provider YAHOO, con fallback `ALL_PROVIDER_CANDLES_STALE`:

| Strumento | Provider | Età quota |
|---|---|---:|
| Oro | YAHOO | 602,3 s |
| WTI | YAHOO | 603,4 s |
| Brent | YAHOO | 609,5 s |
| Grano | YAHOO | 608,6 s |
| Mais | YAHOO | 615,7 s |
| Argento | YAHOO | 613,1 s |
| Soia | YAHOO | 601,8 s |
| Rame | YAHOO | 602,3 s |

Il log non espone per queste righe timestamp assoluto della quota, ticker runtime, mercato o scadenza.

Il workflow imposta `GAGARIN_FOREX_ON_DEMAND=0`, ma il run dichiara ancora 8 commodity operative più 2 Forex ausiliari:
- EUR/USD: BIQUOTE LIVE, age 94,3 s;
- GBP/USD: BIQUOTE LIVE, age 94,8 s.

Sono esplicitamente classificati `CONTESTO FX — NON OPERATIVO`; non li ho conteggiati come commodity o segnali. La loro presenza nel percorso ausiliario è comunque ancora visibile su main.

### Classifica e pre-alert

Argento è l'unica riga commodity direzionale visibile nella classifica: LONG, Prob 59,0, Quality 49,5, Confidence 32,0, `PAPER_WATCH`. È bloccato da `LIVE_DATA_NOT_FRESH`, `TRIGGER_NOT_CONFIRMED`, `TRIGGER_DIRECTION_MISMATCH`, `RR_FAIL`, `CONFIDENCE_FAIL` e `FINAL_CONFLUENCE_FAIL`. Non sono esposti entry, SL, TP o ATR utilizzabili.

Il run registra:
- `PAPER JOURNAL — Recorded entries: 0`;
- feedback: updated open outcomes 0, new feedback signals 0, new additional live forecasts 0;
- `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`.

Telegram ha accettato il pre-alert WATCH message_id 3709 alle 17:41:35.207004 UTC, round-trip 436 ms. Il corpo del messaggio non è conservato nel log. Il codice su main genera il watch board da `operational_results` con `min_score=40`, includendo direzioni con opportunity score sufficiente oppure piani LUBJANKA condizionali. Per questo il messaggio #3709 è stato registrato come **WATCH_BOARD_PRE_ALERT_UNRESOLVED**: Argento LONG è la sola candidata commodity direzionale visibile, ma non è dimostrabile che sia l'unico contenuto del messaggio. Il message_id non prova consegna al dispositivo. È un pre-alert, non un'entrata.

### Configurazione osservata

Il run espone `PAPER_TRADING_ONLY=1`, `MIN_ENTRY_PROBABILITY=40`, `MIN_ENTRY_QUALITY=30`, `MIN_ENTRY_CONFIDENCE=35`, `MIN_ENTRY_RR=2.5`, `MAX_ENTRY_STOP_ATR=2.5`, `MONITOR_INTERVAL_MINUTES=15`. Questi sono i valori effettivi stampati nell'ambiente del run; PRAVDA non li ha modificati.

## 4. Journal, feedback e artefatti GAGARIN

- `journal.csv`: 11 righe, tutte datate 2026-10-17 e con esito “nessun segnale”; nessun nuovo record dal monitor del 6 novembre.
- `paper_trade_log.csv`: un ticket WTI legacy del 2026-10-08, LONG, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55. Mancano provider, timestamp quota, ticker di esecuzione, mercato/contratto, scadenza e prova di fill; la nota dice “chiusura spot 6 ott 2026. Nessun esito”.
- `data/paper_open.json`: posizione P0001 WTI LONG, stessi livelli e allocation 14, status OPEN, `paper_only=true`. È la stessa linea legacy del ticket WTI nel paper_trade_log, non un secondo trade; nessuna prova indipendente di fill.
- `position.json`: Heating Oil LONG, opened_at 2026-09-15 13:23:44.547184 UTC, entry 4.8844, SL 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882. Corrisponde per strumento e livelli alla predizione Heating Oil delle 13:15 nel prediction log (created_at 13:23:44.529091 UTC), ma non ha un corrispondente fill nel paper_trade_log/journal né provider, contratto o scadenza. Trattato come stato legacy collegato alla predizione, non come fill verificato.
- `commodities_prediction_log.json`: 981 record; ultimo created_at 2026-09-15 15:45:04.462276 UTC. Gli ultimi record sono `PENDING`; anche l'etichetta `COMPRA ORA` non prova esecuzione.
- `commodities_monitor_state.json`: timestamp 2026-09-17 03:44:02 UTC.
- `commodities_direction_state.json`: aggiornamenti più recenti del 17 settembre.
- `commodities_daily_selection.json`: data 2026-09-11.
- `gagarin_feedback.csv` e varianti controllate non esistono su main; `DATABASE_URL` è vuoto nel run. Il riepilogo feedback corrente conferma zero aggiornamenti.

Questi artefatti non consentono di ricostruire un outcome cronologico affidabile né di verificare la sequenza SL-first/TP-first.

## 5. PR e correzioni già esistenti

### SPUTNIK

- [PR #144 — persistenza stato su branch dedicato](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN, non merged. Ultimo head `e414e423...`; [run #42274962167](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42274962167) SUCCESS, ranking suite 190 test. La correzione non è attiva su main: il collector #42270098789 ha ancora scritto `sputnik_state.json` su main, commit `0439dca...`.
- [PR #143 — falsi domain label da token brevi](https://github.com/andreameloni1984-sys/trump-trucker/pull/143): OPEN; i test della branch sono verdi, ma non coprono il caso semantico “They are GOLD” in contesto AI. Commento PRAVDA pubblicato.
- [PR #107 — provenienza quote CFD](https://github.com/andreameloni1984-sys/trump-trucker/pull/107): OPEN; il nuovo run conferma che provider/ticker runtime/timestamp/age/expiry non sono esposti. Commento PRAVDA con evidenza #712 pubblicato.

### GAGARIN

- [PR #221 — rimozione rotte FX residue](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): OPEN/DRAFT. Head `74999010...`; [#42245355490](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42245355490) e [#42245355476](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42245355476) SUCCESS sul suo head. Non è integrata; il monitor main continua a mostrare FX ausiliario e otto commodity stale. Commento PRAVDA di follow-up pubblicato.
- [PR #222 — rimozione del veto session_ok](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222): OPEN/DRAFT. Sei check sul head `152a6bbb...` risultano SUCCESS (SOYUZ GAGARIN, execution, NEWS, trade-plan, public-event brain e PAPER). La PR rimuove il gate `session_ok` da Governor/adapter/bridge; non è integrata e non risolve le quotazioni stale.
- [PR #175 — gestione webhook Telegram](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): OPEN. L'ultimo polling schedule disponibile [#42236174265](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42236174265) è fallito con API 409 webhook attivo; nessuna prova di risoluzione su main.
- PR outcome chronology [#91](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/91), [#94](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/94), [#97](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/97) e [#98](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/98) restano aperte/draft; non ho usato codice non integrato per attribuire outcome.

## 6. Ledger PRAVDA e statistiche

File: [`reports/pravda-signal-ledger-2026-11-06.csv`](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-06.csv)

- Record: **35**.
- Firme uniche: **35**.
- Duplicati: **0**.
- Distribuzione: GAGARIN 29; SPUTNIK 6.
- Tipi: 21 historical prediction candidate; 1 legacy paper ticket; 6 watch pre-alert; 6 CFD early setup non eseguiti; 1 watch-board pre-alert con contenuto non conservato.
- Outcome: 28 `ESITO_NON_VERIFICABILE`; 7 `NON_TRADE`.
- Fill verificati: 0; SL verificati: 0; TP verificati: 0; outcome verificabili: 0.
- Win rate: N/D; average R: N/D. Nessuna statistica di rendimento è calcolata su predizioni PENDING, WATCH, NOT_EXECUTED o stati legacy senza fill.

Nuovi record aggiunti:
1. SPUTNIK GOLD SHORT #712, collegato all'analisi #711; `NOT_EXECUTED`, livelli non operativi e contratto non identificato.
2. GAGARIN WATCH board #3709; contenuto non conservato, nessuna entrata, classificato `NON_TRADE`.

Commit aggiornamento ledger: `dcd85adad4d5b3982f2e0669bb95a251300e9803`.

## 7. Lacune e prossimo controllo

1. Verificare se i monitor riprendono una cadenza regolare; non considerare Daily Summary, polling, FETCH DRIVERS o test PR come monitor prezzi.
2. Per SPUTNIK acquisire ticker runtime, provider, timestamp/age, mercato e scadenza esatta; verificare l'allineamento bias/tecnica/D-L-A prima di considerare qualsiasi livello.
3. Per GAGARIN ottenere quotazioni fresche per tutte le otto commodity, timestamp assoluti e ticker/contratto; mantenere FX separato dal paniere operativo.
4. Conservare il corpo del watch board e un ID per ogni candidato, oltre agli ACK Telegram; l'ACK API non equivale a consegna al dispositivo.
5. Rendere disponibili journal/feedback persistenti e prove di fill per gli stati legacy; non promuovere `PENDING` o `OPEN` a trade verificato senza evidenza.
6. Valutare SL/TP solo con candele successive dello stesso identico ticker e contratto, in sequenza temporale; in assenza di ciò mantenere `ESITO NON VERIFICABILE`.

## Perimetro e sicurezza

PAPER ONLY. Nessun ordine reale, accesso Trading212 o consegna Telegram al dispositivo dichiarati. Nessun servizio a pagamento, segreto o Render modificato. Nessun codice, strategia, filtro, punteggio o rischio modificato da PRAVDA. Nessun merge, deploy o rerun. Le sole scritture sono il ledger e questo rapporto; i tre commenti di audit sono stati aggiunti alle PR #107, #143 e #221.
