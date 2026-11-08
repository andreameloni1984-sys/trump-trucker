# PRAVDA — Audit incrementale SPUTNIK / GAGARIN

**Cut-off:** 8 novembre 2026, 07:39:18 UTC (08:39:18 Europe/Rome)  
**Perimetro:** ultime evidenze di produzione disponibili, ledger, journal/feedback, workflow e PR già aperte. Sola verifica; PAPER ONLY.

## 1. Esito sintetico

- Ultimi collector di produzione con log integrale verificato: SPUTNIK [#42439632866](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42439632866), concluso 02:42:14 UTC; GAGARIN [#42438806862](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42438806862), concluso 02:30:28 UTC.
- Al cut-off sono trascorsi rispettivamente **4h57m04s** e **5h08m50s** dall'ultima run verificata. I cron su main restano 5 minuti per SPUTNIK e 15 minuti per GAGARIN. I run PR SPUTNIK #42450417210 e #42450417214 (05:20 UTC circa) sono CI, non scansioni di mercato.
- Non è stata identificata una successiva run schedule di produzione nelle evidenze consultabili. Il collegamento GitHub disponibile consente di leggere run note e relativi log, ma non ha esposto in questo controllo l'elenco completo delle run successive: il gap è quindi misurato dall'ultima run verificata, senza dichiarare come fatto assoluto l'assenza di ogni eventuale run non interrogabile.
- Ledger 8 novembre: **81 record**, SPUTNIK 33, GAGARIN 48; **81 firme uniche**, 81 source ID unici, zero duplicati.
- Esiti ledger: 52 `NON_TRADE`, 29 `ESITO_NON_VERIFICABILE`. Fill verificati 0; SL verificati 0; TP verificati 0. Win rate e average R: **N/D**. I 29 record non verificabili non sono 29 trade.
- Nessun nuovo record eleggibile emerso in questo controllo; ledger invariato.

## 2. SPUTNIK — ultima produzione verificata

**Run:** [#42439632866](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42439632866), schedule, avvio 02:41:59 UTC, completamento 02:42:14 UTC, SUCCESS, nessun artifact.

### Fonti e raccolta
- SEC: HTTP 403; cooldown 21.600 secondi; filings=0.
- White House RSS: HTTPError.
- Scansione intelligence pubblica: findings=0.
- Nessuna nuova operazione/correlazione e nessun handoff a GAGARIN.
- Nel run le variabili GAGARIN_CLOUD_API_URL e GAGARIN_CLOUD_API_KEY sono vuote; il forwarding risulta disabilitato. La PR #147 per rimuovere il coupling resta aperta.

### Messaggi — una sola analisi GOLD, due messaggi collegati

| Source ID / firma | Generazione UTC | ACK API registrato UTC | Strumento / direzione | Identità mercato e dati |
|---|---|---|---|---|
| `run:42439632866/telegram_message:729` | 02:42:09.8056950 | 02:42:09.8067022 | GOLD, NEUTRAL, WATCH | Ticker non risolto; mercato non registrato; provider, timestamp/età quote, prezzo, expiry non esposti; entry/SL/TP/ATR assenti |
| `run:42439632866/telegram_message:730` | 02:42:09.8067468 | 02:42:09.8078059 | GOLD, NEUTRAL, NO_DIRECTION / NOT_EXECUTED | Futures continuous front-month; scadenza esatta UNKNOWN; provider/ticker runtime/timestamp/età quote non esposti; NARWHAL NOT_CONFIGURED; entry/SL/TP/ATR assenti |

Il messaggio #729 dichiara tecnica 5m UNAVAILABLE e NO_DIRECTIONAL_NEWS. Il #730 mostra score 100/100 ma dichiara NO_DIRECTION e NOT_EXECUTED: lo score non è una conferma operativa. Entrambi appartengono alla stessa analisi GOLD e sono contati come un solo candidato, non due segnali distinti. Il message_id #731 compare nei test di regressione ed è escluso dalla produzione.

L'API Telegram ha accettato #729 e #730; il log riporta round-trip 414 ms e 392 ms. I timestamp di generazione e ACK nel log differiscono però di circa 1 ms, incompatibili con i round-trip dichiarati: la latenza end-to-end non è ricostruibile con certezza. L'ACK API non prova la visualizzazione sul dispositivo.

### Difetti e correzioni già aperte
- Main continua a inviare una coppia GOLD dalla history persistita anche con findings=0 e zero nuove correlazioni. PR [#148](https://github.com/andreameloni1984-sys/trump-trucker/pull/148) è OPEN, non merged; i due workflow CI sul suo head sono SUCCESS (46 test item-intelligence e 185 ranking). La branch sopprime la ripetizione quando non ci sono nuovi item RSS individuali datati, ma il filtro attuale verifica evidence/event_id/url/published e non richiede una classificazione di catalizzatore effettivo: un item `event_type=OTHER` può ancora soddisfare il filtro. Questo rilievo era già stato segnalato nella discussione PR il 7 novembre.
- PR [#144](https://github.com/andreameloni1984-sys/trump-trucker/pull/144) per persistenza dello stato fuori da main: OPEN, non merged. Il run #42439632866 ha scritto `sputnik_state.json` tramite commit [8074ec2](https://github.com/andreameloni1984-sys/trump-trucker/commit/8074ec2867c3afa3cd38424a53269a858cc5b0da).
- PR [#145](https://github.com/andreameloni1984-sys/trump-trucker/pull/145) per provenienza quote/diagnostica Yahoo: OPEN, non merged.
- PR [#147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147) per rimuovere l'handoff GAGARIN: OPEN, non merged.

## 3. GAGARIN — ultima produzione verificata

**Run:** [#42438806862](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42438806862), schedule, avvio 02:30:08 UTC, completamento 02:30:28 UTC, SUCCESS, nessun artifact.

### Quotazioni e universo effettivo
Il log mostra otto commodity: Soia, Grano, Brent, WTI, Oro, Argento, Mais, Rame; EUR/USD e GBP/USD restano righe ausiliarie non operative. Tutte le commodity sono `MARKET_CLOSED` e le quote Yahoo sono stale:
- Soia, Grano, Mais: circa 112.524 secondi (31h15m).
- Brent, WTI, Oro, Argento, Rame: circa 102.923 secondi (28h35m).
- FX ausiliario BiQuote: circa 102.924–102.925 secondi.

È domenica: MARKET_CLOSED è coerente con il calendario di mercato e non prova da solo un guasto provider. Le quote sono comunque inutilizzabili come dati freschi. Il log non espone il ticker provider risolto, il timestamp assoluto della quote, il prezzo di riferimento, il tipo di mercato o la scadenza.

### Candidato direzionale e pre-alert

| Source ID / firma | Generazione UTC | Invio/ACK UTC | Strumento / direzione | Provider e identità |
|---|---|---|---|---|
| `run:42438806862/classification:Argento` | 02:30:25.6902087 | Non attribuito | Argento, LONG, PAPER_WATCH / NOT_AUTHORIZED | Yahoo; età 102.922,9 s; ticker provider, quote timestamp, prezzo, mercato e scadenza non esposti; entry/SL/TP/ATR assenti |
| `run:42438806862/telegram_watch_board/message:3718` | Non esposta | 02:30:25.6916281 | WATCH board, direzione/strumento non attribuibili | Corpo del messaggio non conservato; nessun livello o contratto attribuibile |

Argento aveva probabilità 59, qualità 49,5 e confidence 32; era bloccato da LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, CONFIDENCE_FAIL e FINAL_CONFLUENCE_FAIL. È un candidato WATCH, non un ingresso e non un trade. Il pre-alert #3718 è stato accettato dall'API (round-trip dichiarato 560 ms), ma senza body non si può attribuire al candidato Argento; non c'è prova di visualizzazione sul dispositivo.

Riepilogo runtime: `signals=0 open=0 closed=0`; recorded entries=0; updated outcomes=0; new feedback signals=0; new additional live forecasts=0.

### Journal, feedback e persistenza
- `journal.csv`: 11 righe, tutte del 17 ottobre e tutte “nessun segnale”.
- `paper_trade_log.csv`: un ticket legacy WTI P0001 LONG (entry 96,24; SL 89,37; TP1 103,11; TP2 106,55), senza signal ID, fill, provider, ticker, timestamp quote, mercato o scadenza.
- `data/paper_open.json`: P0001 è marcato OPEN, mentre il monitor #42438806862 riporta open=0. È una discrepanza legacy/runtime, non prova di esecuzione.
- `commodities_prediction_log.json`: 981 record, 945 PENDING e 36 NEUTRALE; ultimo record 15 settembre. PENDING, LONG/COMPRA ORA e score non provano un fill.
- `gagarin_feedback.csv`: assente su main (404).
- Nel job #42438806862 `DATABASE_URL` è vuoto; il backend ricade sul CSV locale del runner, non su uno storage durevole verificato. Il workflow dichiara che i journal privati non vengono committati nel repository pubblico. Nessun artifact è stato prodotto.

### Difetto dimostrato nel motore outcome su main
`engine/feedback.py` su main non conserva provider, ticker quotazione, mercato, scadenza o timestamp quote nel record di feedback. La firma del segnale usa symbol/direzione/timeframe/livelli/bar timestamp; l'abbinamento delle candele successive avviene per symbol+timeframe, non per identità esatta del contratto. Inoltre, se una candela OHLC tocca sia SL sia TP, main assegna STOP per convenzione: non dimostra la sequenza intrabar richiesta. In tali casi l'esito corretto per l'audit è ESITO_NON_VERIFICABILE.

PR [#192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) introduce provider/ticker/market/contract nel journal e il matching esatto, oltre a rendere non verificabile il caso SL+TP nella stessa candela. È OPEN e non merged; il confronto con main corrente mostra 6 commit ahead e 4 behind. La branch conserva quote_provider ma il controllo `_market_contract_match` non confronta effettivamente il provider del segnale con quello dello stato successivo: il requisito di provenienza resta incompleto. Le sei run CI sul vecchio head del 5 novembre risultano SUCCESS, ma non dimostrano integrazione né validazione contro il main corrente. Il difetto era già stato segnalato nella discussione PR.

PR [#181](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/181) per esporre la provenienza nel riepilogo dati è ancora OPEN e non merged.

## 4. Cadenza, calendario e correzioni GAGARIN

- Workflow main [gagarin-monitor.yml](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml): cron `*/15 * * * *`. Ultima run verificata 02:30:08 UTC; precedente #42423479990 avviata il 7 novembre 23:03:38 UTC: gap 3h26m30s.
- Workflow main SPUTNIK [trump_tracker.yml](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/trump_tracker.yml): cron `2-59/5 * * * *`. Tra #42426077974 (7 novembre 23:37:18 UTC) e #42439632866 (8 novembre 02:41:59 UTC) il gap è 3h04m41s.
- PR [#225](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225) propone di spostare il cron GAGARIN a 7,22,37,52 mantenendo 15 minuti; è OPEN e draft, non attiva su main. Il confronto con main corrente mostra 2 commit ahead / 1 behind.
- Il calendario economico non è attivo su main: `economic_calendar.py` non esiste su main e il percorso Telegram di `main.py` non chiama il calendario.
- PR #224 è chiusa senza merge; PR #228 è chiusa come superseded; PR [#231](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/231) è la bozza consolidata OPEN, non merged, che contiene il calendario. Quattro run CI della branch sono SUCCESS, ma non sono run di produzione.
- PR #231 dichiara però otto commodity (Gold, Silver, Copper, WTI, Brent, Wheat, Corn, Soybean): include Silver ed esclude Platinum/Palladium, quindi non coincide con il paniere scelto (Gold, Copper, Platinum, Palladium, WTI, Brent, Wheat, Corn, Soybean). PRAVDA ha aggiunto un commento di audit alla PR #231 per registrare la difformità e il fatto che il calendario non è ancora su main.
- PR #219 per rimuovere EUR/USD e GBP/USD è ancora OPEN; PR #223 propone una scansione M5 separata a sette strumenti, è OPEN/draft e non sostituisce il monitor principale. PR #175 per il conflitto polling/webhook Telegram resta OPEN; la correzione non risulta integrata su main.

## 5. Valutazione outcome e statistiche

Nessun record recente presenta insieme prova di fill, ticker/provider esatto, mercato e scadenza identificati, timestamp quote e candele successive dello stesso identico contratto. Nessun esito SL-first o TP-first è quindi verificabile.

| Metrica ledger 8 novembre | Valore |
|---|---:|
| Record totali | 81 |
| SPUTNIK / GAGARIN | 33 / 48 |
| Firme audit uniche / source ID unici | 81 / 81 |
| Duplicati | 0 |
| NON_TRADE | 52 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | 0 |
| SL verificati / TP verificati | 0 / 0 |
| Win rate / Average R | N/D / N/D |

Non ho trasformato WATCH, PAPER_WATCH, PENDING o NOT_EXECUTED in trade. Non ho confrontato spot con futures, né contratti/scadenze diverse. Nessun backtest o risultato finanziario è stato inventato.

## 6. Fonti consultate e prossimo controllo

Fonti: GitHub Actions e log integrali #42439632866 e #42438806862; workflow YAML main dei due repository; ledger giornaliero 8 novembre; `journal.csv`, `paper_trade_log.csv`, `data/paper_open.json`, `commodities_prediction_log.json`, `engine/feedback.py`, `main.py`; PR SPUTNIK #144/#145/#147/#148 e PR GAGARIN #175/#181/#192/#219/#223/#224/#225/#228/#231/#235. Gli ultimi due collector non hanno prodotto artifact.

Prossimo controllo:
1. verificare le successive run schedule di produzione su main, separate da CI/PR;
2. acquisire per ogni eventuale segnale ticker runtime, provider, quote timestamp/age, mercato e scadenza, entry/SL/TP/ATR e timestamp invio;
3. valutare gli outcome soltanto con candele successive dello stesso identico strumento e contratto; SL e TP nella stessa candela restano ESITO_NON_VERIFICABILE;
4. ricontare firme e source ID prima di ogni append; non aggiungere righe duplicate;
5. ricontrollare le PR già aperte dopo eventuali aggiornamenti/merge, senza anticipare il loro effetto in produzione.

**Modifiche di questo controllo:** aggiunto questo rapporto incrementale; ledger invariato perché non sono emersi nuovi record. Nessuna modifica a codice, strategia, filtri, punteggi o rischio; nessun merge, deploy, ordine reale, modifica segreti/Render o accesso a Trading212. Nessuna consegna Telegram al dispositivo dichiarata.
