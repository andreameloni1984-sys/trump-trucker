# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 8 novembre 2026, 21:12 UTC (22:12 Europe/Rome)**

## Sintesi

Sono stati letti direttamente i log completi delle ultime GitHub Actions produttive, i workflow correnti, il ledger PRAVDA, i journal pubblici, l'archivio delle previsioni e le PR rilevanti.

**Nuovi record:** 3 notifiche verificate via risposta API Telegram: SPUTNIK #741 e #742; GAGARIN #3726. Sono tutte classificate `NON_TRADE`. I messaggi #741 e #742 sono due notifiche della stessa analisi GOLD, non due opportunità distinte.

**Nessun trade con fill verificato.** Nessun esito SL/TP valutabile: mancano identità completa del contratto, quotazione successiva omogenea e/o livelli operativi validi.

## 1. Ledger

File: [pravda-signal-ledger-2026-11-08.csv](pravda-signal-ledger-2026-11-08.csv)

Verifica dopo l'aggiornamento:

| Indicatore | Valore |
|---|---:|
| Record | 94 |
| SPUTNIK | 42 |
| GAGARIN | 52 |
| Firme uniche | 94 |
| Source ID unici | 94 |
| Duplicati firma | 0 |
| Duplicati source ID | 0 |
| NON_TRADE | 65 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |

I conteggi riguardano record/notifiche auditati, non 94 trade. I due messaggi SPUTNIK #741/#742 sono collegati alla medesima analisi GOLD. Win rate, average R e total R restano **N/D**.

### Nuovi record

| ID / firma | Bot | Generazione UTC | Invio/ACK UTC | Strumento | Stato | Esito |
|---|---|---|---|---|---|---|
| `run:42520937991/telegram_message:741` | SPUTNIK | 20:35:58.6648949 | 20:35:58.6659378 | GOLD, ticker non risolto | WATCH / NO_DIRECTION | NON_TRADE |
| `run:42520937991/telegram_message:742` | SPUTNIK | 20:35:58.6659887 | 20:35:58.6670675 | GOLD, future continuo front-month; scadenza ignota | NOT_EXECUTED / NO_DIRECTION | NON_TRADE |
| `run:42521363444/telegram_watch_pre_alert:3726` | GAGARIN | non esposto | 20:41:14.9990102 | non attribuibile | WATCH pre-alert | NON_TRADE |

Per #741/#742 l'API Telegram ha risposto rispettivamente in 497 ms e 444 ms. Per #3726 il log riporta 337 ms. Sono conferme API, non prove di visualizzazione sul dispositivo.

## 2. SPUTNIK — run produttiva #291

[GitHub Actions #42520937991](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42520937991) — schedule, SUCCESS. Avvio 20:35:50 UTC; il collector parte alle 20:35:56.053 UTC e completa in circa 2,6 secondi.

Evidenze del vero step produttivo `python trump_tracker.py`:

- SEC CIK 0001849635: HTTP 403, cooldown 21.600 secondi; zero filing.
- White House RSS: HTTPError.
- TRUTH_ARCHIVE e OGE: OSError.
- Risultato raccolta: 0 filing, 0 transazioni, 0 correlazioni pubbliche.
- `GAGARIN_CLOUD_API_URL` e `GAGARIN_CLOUD_API_KEY` risultano vuoti nel runtime; forwarding 0 ms.
- `NARWHAL_API_KEY` vuota; NARWHAL reference non configurato.
- Analisi GOLD: bias NEUTRAL, tecnica 5m UNAVAILABLE, `NO_DIRECTIONAL_NEWS`, WATCH, nessuna entry/SL/TP/ATR.
- Il messaggio #742 è etichettato “ANALISI CFD”, ma il corpo dichiara future continuo front-month, scadenza esatta e indipendenza upstream non verificate. La quotazione futures fresca è assente; non è utilizzabile per livelli operativi.

Il valore 100/100 è priorità/score mostrato dall'analisi, non una direzione e non una prova di validità operativa. #742 dichiara esplicitamente `NOT_EXECUTED`.

### Correzione metodologica sui log SPUTNIK

Le righe “GAGARIN handoff disabled” e “GAGARIN confirmation received” osservate nei run #289 e #291 sono nel precedente step di unit test, non nello step produttivo. Sono output di test/fixture. Ho quindi ritirato l'attribuzione precedente e aggiornato i due commenti già esistenti sulla [PR #147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): [commento corretto](https://github.com/andreameloni1984-sys/trump-trucker/pull/147#issuecomment-6725075833) e [commento precedente corretto](https://github.com/andreameloni1984-sys/trump-trucker/pull/147#issuecomment-6725069750).

Il vero runtime mostra forwarding 0 ms e nessuna conferma GAGARIN. Non c'è prova di handoff esterno.

### Polling Telegram

[Run #51](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42520176845), avviata alle 20:27:04 UTC, SUCCESS. Il runner one-shot ha riportato `Pending updates: 0`. Non è una prova di consegna dei messaggi #741/#742 al dispositivo.

### PR SPUTNIK

- [PR #149](https://github.com/andreameloni1984-sys/trump-trucker/pull/149) è MERGED alle 20:25:23 UTC: rimosso il confronto con l'ora fissa per il daily brief; il riepilogo viene inviato alla prima scansione riuscita del giorno. Non cambia la logica di direzione.
- [PR #147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147) è OPEN, non integrata. Confronto rispetto al main osservato: 1 commit avanti / 3 indietro. I 221 test precedentemente superati non sostituiscono una nuova verifica sul main corrente.
- [PR #145](https://github.com/andreameloni1984-sys/trump-trucker/pull/145) è OPEN; 1 avanti / 5 indietro rispetto al main corrente. La diagnostica Yahoo/provenienza non è ancora su main.

Il workflow SPUTNIK usa cron `2-59/5 * * * *`, ma l'intervallo fra le ultime due run schedule consultate (#289 alle 16:15:37 e #291 alle 20:35:50 UTC) è **4h20m13s**. La run push #290 non è una scansione schedule e non va conteggiata come tale.

## 3. GAGARIN — run produttiva #170

[GitHub Actions #42521363444](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42521363444) — schedule, SUCCESS. Avvio 20:41:00 UTC; il motore riporta timestamp interno 20:41:12.654 UTC.

### Quotazioni e blocchi

Dieci strumenti analizzati: otto commodity operative e due Forex ausiliari.

- Commodity: YAHOO; Forex ausiliari: BIQUOTE.
- Tutti e 10 risultano `MARKET_CLOSED`.
- Età quote registrata: circa **168.074–177.678 secondi**, cioè **46,7–49,4 ore**.
- Il log non espone timestamp assoluto della quotazione, ticker provider risolto, mercato/contratto o scadenza; l'età da sola non basta a ricostruire con certezza il timestamp.
- Ogni voce è bloccata almeno da `LIVE_DATA_NOT_FRESH`; compaiono inoltre `NO_VALID_SETUP`, `TRIGGER_NOT_CONFIRMED`, direzione/setup non valido e entry, stop, TP1/2/3, stop ATR e RR mancanti. Alcuni strumenti hanno anche i rispettivi gate probability/quality/confidence non superati.

La classifica riporta soltanto `PAPER_WATCH` (EUR/USD e GBP/USD: “CONTESTO FX — NON OPERATIVO”). Nessuna entrata autorizzata.

Riepilogo letterale:
- Recorded entries: 0
- Updated open outcomes: 0
- New feedback signals: 0
- New additional live forecasts: 0
- `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`

Telegram #3726 è confermato dall'API in 337 ms, ma il corpo del messaggio non è nel log: non è attribuibile a una commodity o a una direzione.

### Journal e archivio storico

File letti su main:

- `journal.csv`: 11 righe del 17 ottobre, tutte con “nessun segnale”.
- `paper_trade_log.csv`: un record WTI LONG del 8 ottobre, marcato `LEGACY_IMPORT` e `OPEN`; entry 96.24, stop 89.37, TP1 103.11. Provider, timestamp quota, mercato, scadenza ed esito mancano. Non è prova di fill.
- `position.json`: vecchia posizione Heating Oil LONG del 15 settembre, entry 4.8844, stop 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882. Nessun provider/contratto/quotazione verificabile; non è riconciliata con il monitor corrente.
- `commodities_prediction_log.json`: **981** record dal 10 al 15 settembre, 981 ID unici; 945 PENDING e 36 NEUTRALE. Azioni: 21 “COMPRA ORA” (tutte PENDING; 19 RBOB e 2 Heating Oil), 292 LONG “aspettare conferma”, 15 SHORT “aspettare conferma”, 576 ATTENDERE, 77 NON ENTRARE. I 21 “COMPRA ORA” non sono esecuzioni.
- Nell'intero archivio predittivo non risultano campi provider, quote provider/ticker, timestamp quota, market type, contract expiry o execution provider; ATR è valorizzato soltanto in 6 record. I record non sono quindi riconciliabili con candele dello stesso contratto.
- `gagarin_feedback.csv` non è presente nella root pubblica. Il workflow passa `DATABASE_URL` da un GitHub Secret, ma il log non espone il valore né una conferma di scrittura DB: non affermo che il secret sia vuoto. La persistenza privata non è dimostrata da questa run.

Il paniere operativo mostrato nel log contiene Oro, Argento, Rame, WTI, Brent, Grano, Mais e Soia; EUR/USD e GBP/USD sono ausiliari. Argento è ancora presente; Platino e Palladio non compaiono nel monitor corrente.

### PR GAGARIN e difetto outcome

- [PR #222](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222) è MERGED alle 20:24:56 UTC. Rimuove `session_ok` come hard veto intraday nel Governor; lascia indipendenti market-open effettivo, freschezza quote, qualità dati, contratto, liquidità, volatilità, trigger e rischio. È una modifica già integrata dal repository, non fatta da PRAVDA. La run #170, su main aggiornato, resta comunque bloccata da mercato chiuso e dati stale.
- [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) è OPEN e non integrata; confronto con main: 6 commit avanti / 6 indietro. Il branch gestisce il doppio tocco SL+TP nella stessa candela come `ESITO NON VERIFICABILE` e controlla ticker/mercato/scadenza. Tuttavia `_market_contract_match()` non confronta `quote_provider` del record con il provider dello stato/candele: il docstring lo promette, ma il controllo manca. Il rilievo è già presente nei commenti PRAVDA [#6706619879](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6706619879) e [#6725075554](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6725075554); non ho aggiunto duplicati.

Su `main`, `engine/feedback.py` documenta ancora che il doppio tocco viene risolto conservativamente come STOP e controlla `stop_hit` prima dei target. Questo non prova la sequenza intrabar: il risultato corretto per quel caso è non verificabile.

Il monitor GAGARIN usa cron `*/15 * * * *`; le ultime due run schedule consultate (#169 alle 16:16:25 e #170 alle 20:41:00 UTC) distano **4h24m35s**. Il cron dichiarato non coincide con la frequenza osservata.

## 4. Esiti e statistiche

Nessun record nuovo ha entry, SL, TP, ATR, provider, ticker risolto, timestamp quota e contratto sufficienti a iniziare una valutazione prospettica. I nuovi tre record sono notifiche NON_TRADE.

Per i 29 record storici `ESITO_NON_VERIFICABILE`, non è stata prodotta una nuova sequenza di prezzi omogenea che consenta di decidere SL prima o TP prima. Nessun backtest o risultato è stato inventato.

## 5. Fonti consultate

- Run SPUTNIK #291: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42520937991
- Run SPUTNIK polling #51: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42520176845
- Run GAGARIN #170: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42521363444
- Workflow SPUTNIK: https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/trump_tracker.yml
- Workflow GAGARIN: https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml
- GAGARIN feedback engine: https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py
- Journal/legacy files: `journal.csv`, `paper_trade_log.csv`, `position.json`, `commodities_prediction_log.json` nel repository GAGARIN.
- PR esaminate: SPUTNIK #145/#147/#149; GAGARIN #192/#222.

## 6. Prossimo controllo

1. Verificare nuove run schedule e misurare nuovamente i gap.
2. Alla riapertura dei mercati, controllare provider, ticker effettivo, timestamp quota, market type e scadenza prima di accettare qualsiasi setup.
3. Verificare che #147/#145 e #192 siano riallineate e integrate solo dai rispettivi responsabili; PRAVDA non effettua merge.
4. Verificare la persistenza privata del journal tramite evidenza esplicita di lettura/scrittura, senza esporre secret.
5. Riconciliare i record legacy solo quando esistono candele successive dello stesso identico strumento/contratto.

**PAPER ONLY.** Nessun ordine reale, nessun accesso a Trading212 dichiarato, nessuna consegna Telegram al dispositivo dichiarata, nessun servizio a pagamento, nessuna modifica a secret/Render. PRAVDA non ha modificato codice, strategia, filtri, punteggi o rischio. Sono stati aggiornati soltanto il ledger, questo rapporto e due commenti PR esistenti per correggere un'attribuzione metodologica errata.
