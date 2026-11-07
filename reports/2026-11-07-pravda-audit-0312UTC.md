# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-07 03:12 UTC (04:12 Europe/Rome)**  
**Perimetro: sola verifica e documentazione; PAPER ONLY.**

## Sintesi esecutiva

- Nuovo collector SPUTNIK: [run #42331705890](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42331705890), avviato alle 02:57:24 UTC, SUCCESS. È l'unico monitor di mercato SPUTNIK osservato dopo il precedente run delle 23:20:35 UTC: gap tra i due collector **3h36m49s**. Al cut-off il run più recente aveva circa 15m05s.
- Nuovo monitor GAGARIN: [run #42328183997](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42328183997), avviato alle 02:13:56 UTC, SUCCESS. Il precedente monitor era delle 22:25:16 UTC: gap **3h48m40s**. Al cut-off il monitor aveva circa 58m33s; non risultano ulteriori run di mercato nelle Actions recenti.
- SPUTNIK ha ripetuto un candidato GOLD LONG EARLY_BIAS (#715/#716), ma senza nuova evidenza pubblica, quotazione futures fresca, ATR o livelli. È una **ripetizione della tesi precedente**, non un nuovo setup indipendente e non un trade.
- GAGARIN ha inviato il watch-board #3711. Il corpo non è conservato; le righe WTI/Mais/Argento restano PAPER_WATCH, senza entry/SL/TP/ATR. Tutte le otto commodity risultano **MARKET_CLOSED**, con quotazioni Yahoo vecchie di circa 4h14m–6h54m. Il sistema ha correttamente bloccato le entrate.
- Nessun fill, TP o SL verificabile; nessun outcome di mercato certificabile. Campione di trade con outcome verificabile: **0**.
- Ledger aggiornato da 40 a **42 record**, 42 firme uniche, zero duplicati: due nuove osservazioni-notifica, senza aggiungere un nuovo setup operativo.
- Nessun codice dei bot modificato; nessun merge, deploy, rerun o ordine reale.

## 1. GitHub Actions e continuità

### SPUTNIK

Workflow .github/workflows/trump_tracker.yml, cron dichiarato '2-59/5 * * * *'.

Run di mercato più recente:
- [#42331705890](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42331705890), evento schedule, run #282, avvio 2026-11-07 02:57:24 UTC, SUCCESS.
- Il precedente collector era [#42311247999](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42311247999), 2026-11-06 23:20:35 UTC.
- Tra i due collector: 3h36m49s; nonostante la cadenza nominale di 5 minuti, le Actions recenti non dimostrano continuità.
- Il job ha eseguito 30 test unitari prima del collector: 30 OK. Le righe di test non sono produzione.

Polling SPUTNIK separato:
- [#42329017675](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42329017675), 02:23:33 UTC, SUCCESS; log: remote state loaded, pending updates=0. È polling Telegram, non una scansione mercato.

### GAGARIN

Workflow .github/workflows/gagarin-monitor.yml, cron dichiarato '*/15 * * * *'.

Run più recente:
- [#42328183997](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42328183997), evento schedule, run #162, avvio 2026-11-07 02:13:56 UTC, SUCCESS.
- Il precedente monitor era [#42304574886](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42304574886), 2026-11-06 22:25:16 UTC.
- Gap tra i due monitor: 3h48m40s; al cut-off sono trascorsi 58m33s dal run più recente. Non risultano monitor prezzi successivi nelle Actions recenti.
- I test PR, il polling e i run ausiliari non sono conteggiati come monitor di mercato.

## 2. SPUTNIK — candidato GOLD #715/#716

Fonte: [run #42331705890](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42331705890).

**Un solo candidato collegato**, due messaggi:
- Analisi #715, generata nel log alle 02:57:32.7750462 UTC; API ACK alle 02:57:32.7768518 UTC, round-trip 483 ms.
- Scheda CFD #716, generata nel log alle 02:57:32.7769354 UTC; API ACK alle 02:57:32.7788127 UTC, round-trip 401 ms.
- L'ACK API non prova la visualizzazione sul dispositivo né un'esecuzione.

Dati:
- strumento: GOLD;
- ticker configurato: GC=F; ticker runtime non confermato;
- mercato dichiarato: future continuo front-month; scadenza esatta UNKNOWN;
- provider, timestamp e anzianità della quotazione: NOT_EXPOSED;
- NARWHAL: NOT_CONFIGURED (chiave assente);
- #715: bias preliminare NEUTRAL, tecnica UNAVAILABLE (5m), NO_DIRECTIONAL_NEWS, priorità 70/100;
- #716: bias LONG, setup EARLY_BIAS, tecnica LONG/TECHNICAL_ONLY, D-L-A NEUTRAL/NO_DIRECTION, score 70;
- entry, SL, TP e ATR: omessi;
- stato: EARLY_BIAS / NOT_EXECUTED.

La ragione dichiarata per non emettere livelli è corretta: quotazione futures fresca o ATR valido non disponibili. Il messaggio avverte inoltre che il front-month continuo non ha scadenza esatta e non va usato per entry/SL/TP.

**Ripetizione, non nuovo setup:** il candidato #715/#716 ripete sostanzialmente il GOLD EARLY_BIAS #713/#714 del run #42311247999. Nel collector attuale: findings=0, filings=0, nuove operazioni=0, nuove correlazioni pubbliche=0. Non è identificato un nuovo catalizzatore individuale collegato allo score 70. La discrepanza tra analisi #715 NEUTRAL/UNAVAILABLE e scheda #716 LONG/TECHNICAL_ONLY con D-L-A neutrale resta una direzione non confermata.

### Errori fonte e distinzione test/produzione

Nel collector di produzione:
- SEC: HTTP 403, cooldown 21.600 secondi;
- White House RSS: HTTPError;
- zero filing, zero nuove operazioni, zero nuove correlazioni.

Importante: il log prima del comando python trump_tracker.py contiene output dei test unitari, inclusi un messaggio simulato #731 e la stringa “GAGARIN confirmation received”. Queste righe precedono l'avvio del collector di produzione e **non sono prova di un handoff reale**. Nel run di produzione si legge invece: handoff GAGARIN disabilitato perché GAGARIN_CLOUD_API_URL e GAGARIN_CLOUD_API_KEY sono vuoti. Nessuna conferma GAGARIN esterna è dimostrata.

### Stato persistente SPUTNIK

Il run ha creato e pushato il commit [7abf631](https://github.com/andreameloni1984-sys/trump-trucker/commit/7abf6314c5f5aa4c0de2755825ba3b04a668c99a), con messaggio chore: persist Sputnik state; push su main riuscito.
Lettura del blob corrente sputnik_state.json:
- 1.395.898 caratteri;
- 500 chiavi in intelligence_history;
- events vuoto;
- updated_at=2026-11-07T02:57:31.194056Z;
- Telegram offset 275590742, telegram_active=true.
- massimo detected_at nell'history: 2026-11-06T23:20:41.409462Z; nessun nuovo item nel collector 02:57.

La persistenza è dimostrata; 500 elementi di history non equivalgono a 500 catalizzatori individuali verificati.

## 3. GAGARIN — monitor #42328183997

Fonte: [run #42328183997](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42328183997).

Il log riporta MARKET_CLOSED e fallback reason MARKET_CLOSED per tutte le otto commodity. Provider selezionato: Yahoo. Ticker runtime, timestamp puntuale della quotazione, mercato/contratto e scadenza non sono esposti.

| Strumento | Provider | Quote age | Stato |
|---|---|---:|---|
| Brent | Yahoo | 15.267,6 s (~4h14m) | MARKET_CLOSED |
| WTI | Yahoo | 15.253,4 s (~4h14m) | MARKET_CLOSED |
| Soia | Yahoo | 24.853,0 s (~6h54m) | MARKET_CLOSED |
| Oro | Yahoo | 15.251,0 s (~4h14m) | MARKET_CLOSED |
| Grano | Yahoo | 24.852,7 s (~6h54m) | MARKET_CLOSED |
| Mais | Yahoo | 24.855,8 s (~6h54m) | MARKET_CLOSED |
| Argento | Yahoo | 15.252,1 s (~4h14m) | MARKET_CLOSED |
| Rame | Yahoo | 15.263,2 s (~4h14m) | MARKET_CLOSED |

La classificazione visibile:
- WTI SHORT: probability 66, quality 57,5, confidence 37, PAPER_WATCH;
- Mais LONG: 63 / 52,5 / 35, PAPER_WATCH;
- Argento LONG: 59 / 49,5 / 32, PAPER_WATCH;
- Brent, Soia, Oro, Grano e Rame senza direzione operativa nel ranking.

I blocchi includono dati non freschi/mercato chiuso, setup non valido, trigger non confermato, mismatch direzionale e livelli mancanti. Nessuno dei candidati ha entry, SL, TP o ATR operativo completo. Non sono trade.

### Forex ausiliario

Il run analizza anche EUR/USD e GBP/USD come CONTESTO FX — NON OPERATIVO, pur con GAGARIN_FOREX_ON_DEMAND=0:
- provider nel run: BiQuote;
- entrambi MARKET_CLOSED, age rispettivamente 15.552,6s e 15.553,2s;
- nessuna operatività Forex.

### Watch board #3711

- message_id 3711;
- Telegram API ACK alle 02:14:13.6555025 UTC, round-trip 472 ms;
- timestamp di generazione specifico del messaggio non esposto; il timestamp di run è 02:14:09.817324 UTC;
- il corpo del board non è conservato nel log: non si può attribuire il messaggio a WTI, Mais o Argento individualmente.
- New additional live forecasts=0, Recorded entries=0, New feedback signals=0, signals=0 open=0 closed=0.

API ACK non equivale a prova di visualizzazione sul dispositivo. Il board è registrato come notifica WATCH non attribuibile, non come trade.

### Soglie effettive del run

Ambiente osservato: PAPER_TRADING_ONLY=1, MIN_ENTRY_PROBABILITY=40, MIN_ENTRY_QUALITY=30, MIN_ENTRY_CONFIDENCE=35, MIN_ENTRY_RR=2.5, MAX_ENTRY_STOP_ATR=2.5, SL_STRUCTURE_BUFFER_ATR=0.15, SL_MIN_ATR=0.80. PRAVDA non ha modificato alcun valore.

## 4. Journal, feedback e stato GAGARIN

Artefatti letti su main:
- journal.csv: 11 righe del 17 ottobre 2026, tutte con “nessun segnale”.
- paper_trade_log.csv: una riga legacy WTI LONG del 2026-10-08, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55; nessun provider/contratto/fill/outcome documentato.
- data/paper_open.json: posizione P0001, lo stesso WTI LONG legacy; non è un secondo trade. paper_only=true.
- position.json: Heating Oil LONG, entry 4.8844, SL 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882, aperta 2026-09-15 13:23:44 UTC; nessuna prova indipendente di fill.
- commodities_prediction_log.json: 981 record; ultimo creato 2026-09-15 15:45:04 UTC, status PENDING. PENDING non prova un trade.
- commodities_monitor_state.json: timestamp 2026-09-17 03:44:02 UTC, best Benzina RBOB, LONG, action ATTENDERE, entry_state BLOCKED; snapshot legacy non aggiornato dal run corrente.
- gagarin_feedback.csv: assente dal root di main.
- DATABASE_URL: vuoto nel run. Il workflow dichiara che i journal paper sono dati privati e non vengono committati nel repository pubblico; persistenza riattivabile solo dopo storage D1 privato verificato.

Non sono stati assegnati outcome a WTI P0001 o Heating Oil: mancano prova di fill, identità del contratto e candele successive dello stesso contratto.

## 5. Motore outcome e correzioni già esistenti

### Main GAGARIN

Il file engine/feedback.py su main:
- identifica i record con symbol, direction, timeframe, livelli e timestamp barra, ma non incorpora nel record l'identità completa del contratto, la scadenza e la provenienza della quotazione;
- abbina le candele per symbol + timeframe, con fallback symbol-only quando esiste un solo stato;
- parte da candele strettamente successive alla entry bar;
- se SL e TP sono nella stessa candela assegna STOP;
- se più TP sono toccati nella stessa candela seleziona idx=max(hit_targets), cioè il target più alto, senza prova dell'ordine intrabar.

### PR #192

[PR #192 — Exact contract e outcome audit](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192):
- OPEN, non draft, non merged;
- head 295dba4b074e564a4c11aa3fca136a8e4360672c;
- base c93906a2a4b28d60fd58c600b51cd3c05929f89d;
- main corrente fba34bef94ac8968f7d31e3ee70ade8efe3fd51c è avanti di 3 commit rispetto alla base della PR.
- Il branch introduce campi ticker/provider/timestamp, mercato e scadenza, e rifiuta mismatch di contratto; tratta SL+TP nella stessa candela come ESITO NON VERIFICABILE.
- Difetto residuo confermato nel branch: idx=max(hit_targets) resta presente; se più target sono raggiunti nella stessa candela, il target specifico non è dimostrabile.
- Non è integrata su main; non si attribuisce al bot in produzione.

### PR #175 Telegram polling

[PR #175 — Handle active Telegram webhook](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175):
- OPEN, non draft, non merged; head 7bb944f39440718426bc22923ce640a50cbc3fbe, base main corrente fba34bef94ac8968f7d31e3ee70ade8efe3fd51c.
- Il branch gestisce il 409 come WebhookActiveError, registra polling skipped e lascia il webhook attivo.
- Le suite CI su quel branch alle 01:39 UTC risultano SUCCESS.
- L'ultimo polling GAGARIN osservato su main, [run #42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549) alle 00:16:15 UTC, è fallito con Telegram API 409: webhook attivo, polling non consentito.
- Nessun polling runtime successivo prova ancora la correzione su main.

Altre PR GAGARIN:
- [#224 calendario economico e alert](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/224): OPEN, non merged.
- [#223 scansione M5 a sette strumenti](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): OPEN, draft.
- [#221 rimozione rotte Forex residue](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): OPEN, draft.

### SPUTNIK

- [PR #147 — rimozione handoff GAGARIN](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN, non merged; test ranking e item-intelligence sul branch sono verdi. Main conserva ancora il codice di handoff opzionale, ma nel run 02:57 URL e API key erano assenti e il forwarding è stato disabilitato.
- [PR #145 — provenienza quotazioni](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN, non merged. Il run corrente continua a non esporre ticker runtime, provider e timestamp della quotazione futures.
- La stringa di “GAGARIN confirmation received” e il messaggio #731 appaiono nel blocco di test del job, non nella produzione. Non sono conteggiati come handoff o alert reali.

## 6. Ledger e statistiche

Ledger aggiornato:
- prima: 40 record / 40 firme;
- dopo: **42 record / 42 firme uniche / 0 duplicati**.
- aggiunti solo:
  1. osservazione ripetuta SPUTNIK GOLD #715/#716, collegata al candidato #713/#714 precedente, NON_TRADE;
  2. watch-board GAGARIN #3711, strumento non attribuibile dal body/log, NON_TRADE.
- nessun nuovo setup operativo distinto.

Distribuzione dei campi outcome nel ledger: 29 ESITO_NON_VERIFICABILE, 13 NON_TRADE. Queste sono etichette dei record, non 29 o 13 operazioni.

Statistiche esclusivamente su trade con fill e outcome verificabile:
- fill verificati: 0;
- TP verificati: 0;
- SL verificati: 0;
- campione verificabile: 0;
- win rate: N/D;
- average R: N/D.

Nessun backtest, nessuna candela spot usata per giudicare futures, nessun contratto/scadenza inferito.

## 7. Fonti consultate

- GitHub Actions SPUTNIK: [run #42331705890](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42331705890), job log e [polling #42329017675](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42329017675).
- GitHub Actions GAGARIN: [monitor #42328183997](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42328183997), [polling #42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549).
- File e artefatti main: sputnik_state.json, commodities_monitor_state.json, commodities_direction_state.json, journal.csv, paper_trade_log.csv, data/paper_open.json, position.json, commodities_prediction_log.json, telegram_listener_state.json, engine/feedback.py e workflow YAML.
- PR: SPUTNIK #147/#145; GAGARIN #192/#175/#224/#223/#221.

## 8. Prossimo controllo

1. Verificare che SPUTNIK torni a eseguire i collector a intervalli regolari e che il nuovo run produca una fonte individuale con timestamp verificabile.
2. Verificare la ripresa del monitor GAGARIN dopo la riapertura dei mercati; non trattare il normale stato MARKET_CLOSED del sabato come prova di guasto provider.
3. Controllare su main l'integrazione delle PR #192 e #175; fino ad allora i difetti restano aperti.
4. Verificare quote timestamp, ticker runtime, mercato e scadenza prima di valutare qualsiasi outcome.
5. Non attribuire outcome alle posizioni legacy senza prova di fill e candele dello stesso contratto.

**Nessuna modifica al codice, alle strategie, ai filtri, ai punteggi o al rischio. Nessun merge, deploy, rerun, ordine reale, modifica a Render o ai segreti. Nessun accesso Trading212 dichiarato. PAPER ONLY.**
