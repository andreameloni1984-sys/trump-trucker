# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-07 03:44:32 UTC (04:44:32 Europe/Rome)**  
**Perimetro: sola verifica e documentazione; PAPER ONLY.**

## Sintesi esecutiva

- Non risultano nuovi monitor di mercato dopo SPUTNIK run [#42331705890](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42331705890) alle 02:57:24 UTC e GAGARIN run [#42328183997](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42328183997) alle 02:13:56 UTC.
- Al cut-off, i monitor avevano rispettivamente 47m08s e 1h30m36s. I gap tra gli ultimi due monitor sono 3h36m49s per SPUTNIK e 3h48m40s per GAGARIN, nonostante cron dichiarati a 5 e 15 minuti.
- SPUTNIK ha ripetuto il candidato GOLD EARLY_BIAS #715/#716: nessun nuovo catalizzatore, nessun livello operativo, NOT_EXECUTED.
- GAGARIN ha mostrato tre classificazioni direzionali WATCH (WTI SHORT, Mais LONG, Argento LONG), tutte bloccate dai dati stale/mercato chiuso e senza livelli. Sono state aggiunte al ledger come osservazioni WATCH non operative, senza attribuire loro invii individuali.
- Il watch-board GAGARIN #3711 è stato accettato dall'API Telegram, ma il corpo non è conservato: resta non attribuibile ai singoli strumenti.
- Ledger giornaliero aggiornato da 42 a **45 record, 45 firme uniche, zero duplicati**. Nessun nuovo trade operativo.
- Fill verificati: 0. TP verificati: 0. SL verificati: 0. Campione di trade con outcome verificabile: 0.

## 1. GitHub Actions e continuità

### SPUTNIK

Workflow [trump_tracker.yml](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/trump_tracker.yml): cron `2-59/5 * * * *`.

- Ultimo monitor: [#42331705890](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42331705890), schedule, avvio 2026-11-07 02:57:24 UTC, conclusione SUCCESS alle 02:57:37 UTC.
- Precedente monitor: [#42311247999](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42311247999), 2026-11-06 23:20:35 UTC.
- Gap: 3h36m49s; età al cut-off: 47m08s.
- Il job ha superato i passi di test e collector; i test non sono conteggiati come scansioni di mercato.

Polling SPUTNIK separato: [#42329017675](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42329017675), 02:23:33 UTC, SUCCESS. Il log riporta `Pending updates: 0` e `Polling run completed`. È polling, non un monitor prezzi.

### GAGARIN

Workflow [gagarin-monitor.yml](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml): cron `*/15 * * * *`.

- Ultimo monitor: [#42328183997](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42328183997), schedule, avvio 2026-11-07 02:13:56 UTC, conclusione SUCCESS alle 02:14:17 UTC.
- Precedente monitor: [#42304574886](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42304574886), 2026-11-06 22:25:16 UTC.
- Gap: 3h48m40s; età al cut-off: 1h30m36s.
- Nessun successivo monitor di mercato compare nelle Actions consultate.

Le cadenze dichiarate non sono rispettate dagli intervalli osservati. Non è dimostrata la causa del ritardo: non attribuirlo a un filtro orario senza ulteriore evidenza.

## 2. SPUTNIK — GOLD #715/#716

Fonte: job log del run [#42331705890](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42331705890).

Un solo candidato collegato, due messaggi:
- analisi #715 generata alle 02:57:32.7750462 UTC; API ACK alle 02:57:32.7768518 UTC, round-trip 483 ms;
- scheda CFD #716 generata alle 02:57:32.7769354 UTC; API ACK alle 02:57:32.7788127 UTC, round-trip 401 ms.

Dati effettivi:
- strumento GOLD;
- mapping configurato GC=F, ticker runtime non confermato;
- mercato dichiarato: futures continuous front-month; scadenza esatta UNKNOWN;
- provider, timestamp e anzianità della quotazione non esposti;
- #715: bias NEUTRAL, tecnica UNAVAILABLE, NO_DIRECTIONAL_NEWS, priorità 70/100;
- #716: bias LONG, tecnica LONG/TECHNICAL_ONLY, D-L-A NEUTRAL/NO_DIRECTION, score 70;
- entry, SL, TP e ATR omessi;
- stato EARLY_BIAS / NOT_EXECUTED.

È una ripetizione della tesi GOLD #713/#714 del run precedente, non un nuovo setup indipendente. Il collector riporta findings=0, filings=0, nuove operazioni=0 e nuove correlazioni pubbliche=0. Lo score non dimostra un catalizzatore né validità operativa.

Il sistema ha correttamente omesso i livelli in assenza di quotazione futures fresca e ATR valido. Il messaggio avverte che front-month continuo e scadenza non identificata non sono utilizzabili per entry/SL/TP. API ACK prova l'accettazione della richiesta, non la visualizzazione sul dispositivo e non un'esecuzione.

Fonti:
- SEC: HTTP 403, cooldown 21.600 secondi, filings=0.
- White House RSS: HTTPError.
- Public intelligence scan: findings=0.
- Le righe simulate dei test (incluso message_id #731 e la stringa di conferma GAGARIN) precedono il collector e non sono produzione. Nel run il forwarding GAGARIN è disabilitato perché URL e API key non sono configurati.

### Persistenza SPUTNIK

Il commit [7abf631](https://github.com/andreameloni1984-sys/trump-trucker/commit/7abf6314c5f5aa4c0de2755825ba3b04a668c99a) aggiorna `sputnik_state.json`. Il diff verificato aggiorna `updated_at` e il timestamp di inizializzazione del feed; non mostra nuovi item nel collector delle 02:57. La persistenza del file è dimostrata, ma non equivale a nuovi catalizzatori.

PR [#147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147) per rimuovere l'handoff GAGARIN è OPEN e non merged. Le due suite sul branch sono verdi, ma il branch è basato su un main precedente e non modifica il runtime finché non viene integrato. PR [#145](https://github.com/andreameloni1984-sys/trump-trucker/pull/145) per la provenienza delle quotazioni è anch'essa OPEN; i campi runtime mancanti restano mancanti.

## 3. GAGARIN — monitor #42328183997

Il log riporta MARKET_CLOSED e fallback reason MARKET_CLOSED per tutte le otto commodity. Provider selezionato: Yahoo.

| Strumento | Provider | Quote age | Stato |
|---|---|---:|---|
| Brent | Yahoo | 15.267,6 s | MARKET_CLOSED |
| WTI | Yahoo | 15.253,4 s | MARKET_CLOSED |
| Soia | Yahoo | 24.853,0 s | MARKET_CLOSED |
| Oro | Yahoo | 15.251,0 s | MARKET_CLOSED |
| Grano | Yahoo | 24.852,7 s | MARKET_CLOSED |
| Mais | Yahoo | 24.855,8 s | MARKET_CLOSED |
| Argento | Yahoo | 15.252,1 s | MARKET_CLOSED |
| Rame | Yahoo | 15.263,2 s | MARKET_CLOSED |

Il 7 novembre è sabato: MARKET_CLOSED è coerente con la chiusura del mercato e non dimostra da solo un guasto del provider. Le quotazioni sono però stale; il run non espone ticker runtime, timestamp puntuale, mercato/contratto e scadenza.

### Tre classificazioni WATCH registrate nel ledger

Queste righe sono classificazioni del ranking, non ingressi e non invii individuali:

| Strumento | Direzione | Prob. | Quality | Confidence | Quote age | Blocchi principali |
|---|---|---:|---:|---:|---:|---|
| WTI | SHORT | 66 | 57,5 | 37 | 15.253,4 s | LIVE_DATA_NOT_FRESH, trigger non confermato, mismatch direzionale, final confluence |
| Mais | LONG | 63 | 52,5 | 35 | 24.855,8 s | LIVE_DATA_NOT_FRESH, trigger non confermato, mismatch direzionale, RR_FAIL |
| Argento | LONG | 59 | 49,5 | 32 | 15.252,1 s | LIVE_DATA_NOT_FRESH, trigger non confermato, mismatch direzionale, RR1_FAIL, confidence fail |

Per tutte e tre: ticker runtime, mercato, scadenza e timestamp puntuale della quotazione non esposti; entry, SL, TP e ATR assenti; nessun fill. Sono state aggiunte al ledger con `outcome=NON_TRADE`, non come trade e non come outcome finanziario.

### Watch-board #3711

- generazione specifica del messaggio non esposta; il run timestamp è 02:14:09.817324 UTC;
- Telegram API ACK alle 02:14:13.6555025 UTC, round-trip 472 ms, message_id 3711;
- il body non è conservato nel log, quindi il messaggio non è attribuibile con certezza a WTI, Mais o Argento;
- è registrato separatamente come board non attribuibile, senza duplicare le tre classificazioni.

Il riepilogo del run: `Recorded entries: 0`, `Updated open outcomes: 0`, `New feedback signals: 0`, `New additional live forecasts: 0`, `signals=0 open=0 closed=0`.

EUR/USD e GBP/USD compaiono solo come contesto FX non operativo tramite BiQuote, anch'essi MARKET_CLOSED/stale. Non sono stati conteggiati come commodity operative.

## 4. Journal e persistenza GAGARIN

Il job log espone `DATABASE_URL:` vuoto. Il codice main di `engine/feedback.py` seleziona quindi il backend locale CSV quando DATABASE_URL è assente. Il workflow dichiara esplicitamente che i journal PAPER sono dati operativi privati e non vengono committati nel repository; la persistenza privata sarà riattivata solo dopo deployment e verifica del database.

Artefatti pubblici riletti:
- `journal.csv`: 11 righe del 17 ottobre, tutte “nessun segnale”;
- `paper_trade_log.csv`: una riga legacy WTI LONG del 8 ottobre, senza provider/contratto/fill/outcome;
- `data/paper_open.json`: P0001, la stessa posizione WTI legacy, non un secondo trade;
- `position.json`: vecchia posizione Heating Oil LONG aperta il 15 settembre, senza prova indipendente di fill;
- `commodities_monitor_state.json` e `commodities_direction_state.json`: snapshot datati 17 settembre;
- `gagarin_feedback.csv`: assente dal repository pubblico.

Non è stato attribuito un outcome alle posizioni legacy. Il CSV locale su runner effimero e non persistito non è un journal durevole.

## 5. Motore outcome e PR già esistenti

### Main GAGARIN

Il file [engine/feedback.py su main](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py) ancora:
- identifica il segnale con symbol, direction, timeframe, livelli e timestamp barra, senza identità completa del contratto e provenienza della quotazione;
- abbina candele per symbol + timeframe, con fallback symbol-only quando esiste un solo stato;
- parte da candele strettamente successive alla entry bar;
- se SL e TP sono nella stessa candela assegna STOP;
- se più TP sono toccati nella stessa candela usa `idx=max(hit_targets)`, cioè il target più alto, senza prova dell'ordine intrabar.

### PR #192

[PR #192 — exact-contract e outcome audit](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192):
- OPEN, non merged; head 295dba4b074e564a4c11aa3fca136a8e4360672c;
- base c93906a2a4b28d60fd58c600b51cd3c05929f89d; main corrente fba34bef94ac8968f7d31e3ee70ade8efe3fd51c è avanti di 3 commit;
- introduce ticker/provider/timestamp, mercato e scadenza, matching del contratto e ESITO NON VERIFICABILE per SL+TP nella stessa candela;
- nel branch resta `idx=max(hit_targets)`: se più target sono toccati nella stessa OHLC candle, il target specifico non è dimostrabile;
- le 8 run CI del branch sono del 5 novembre e verdi; non dimostrano integrazione né test contro il main corrente.

### PR #175 — Telegram webhook

[PR #175](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175) è OPEN, non merged. Il branch gestisce il 409 come webhook attivo, salta il polling e non rimuove il webhook. Le 7 run CI del branch alle 01:39 UTC del 7 novembre sono verdi.

Su main, il polling [#42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549) delle 00:16:15 UTC è fallito: il log mostra API 409, webhook attivo e getUpdates non consentito. Nessun run runtime successivo dimostra la correzione su main.

La stessa esecuzione è etichettata `event=schedule` alle 00:16 di sabato, mentre il workflow [telegram-polling.yml](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/telegram-polling.yml) dichiara `*/5 7-21 * * 1-5` UTC. Discrepanza confermata, causa non stabilita.

Altre PR osservate: #224 calendario economico OPEN; #223 scansione M5 draft; #221 rimozione rotte FX draft; #219 rimozione EUR/USD e GBP/USD OPEN. Nessuna è conteggiata come integrata su main.

## 6. Ledger e statistiche

Nuovo ledger giornaliero: [pravda-signal-ledger-2026-11-07.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-07.csv).

- record: **45**;
- firme uniche: **45**;
- duplicati: **0**;
- outcome labels: 29 ESITO_NON_VERIFICABILE e 16 NON_TRADE;
- aggiunte in questo audit: 3 classificazioni GAGARIN WATCH (WTI, Mais, Argento);
- nessun nuovo setup operativo e nessun fill dimostrato.

Statistiche esclusivamente su trade con fill e outcome verificabile:
- fill verificati: 0;
- TP verificati: 0;
- SL verificati: 0;
- campione verificabile: 0;
- win rate: N/D;
- average R: N/D.

Le 45 righe sono osservazioni, candidati WATCH, predizioni legacy e notifiche; non sono 45 trade. Nessun backtest è stato prodotto.

## 7. Fonti consultate

- GitHub Actions SPUTNIK [monitor #42331705890](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42331705890), [polling #42329017675](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42329017675).
- GitHub Actions GAGARIN [monitor #42328183997](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42328183997), [polling #42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549).
- Workflow YAML, job log completi, tree main, ledger precedente e artefatti journal pubblici.
- PR SPUTNIK #147/#145; PR GAGARIN #192/#175/#224/#223/#221/#219.
- Commit di persistenza SPUTNIK [7abf631](https://github.com/andreameloni1984-sys/trump-trucker/commit/7abf6314c5f5aa4c0de2755825ba3b04a668c99a).

## 8. Prossimo controllo

1. Verificare nuovi monitor e calcolare nuovamente i gap reali rispetto ai cron.
2. Alla riapertura dei mercati, controllare se le otto commodity ottengono quote fresche, con ticker, timestamp, mercato e scadenza.
3. Verificare l'integrazione su main delle correzioni outcome e webhook; fino ad allora i difetti restano aperti.
4. Verificare che il journal GAGARIN disponga di persistenza durevole prima di considerare affidabili i conteggi.
5. Valutare outcome soltanto con fill e candele successive dello stesso identico strumento/contratto; SL/TP simultanei o più target nella stessa OHLC candle restano non verificabili senza dati intrabar.

**Nessuna modifica al codice dei bot, alle strategie, ai filtri, ai punteggi o al rischio. Nessun merge, deploy, rerun, ordine reale, modifica a Render o ai segreti. Nessun accesso Trading212 dichiarato. PAPER ONLY.**
