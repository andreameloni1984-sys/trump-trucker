# PRAVDA — audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-08 13:25:22 UTC (14:25:22 Europe/Rome)**

## Sintesi

Verificate le ultime GitHub Actions di produzione, i log integrali dei job, i file di stato e journal versionati, il ledger PRAVDA, i workflow YAML e le PR già aperte.

**Nessun nuovo segnale operativo verificabile.** L'unico nuovo evento registrato nel ledger è una notifica GAGARIN Daily Summary: il job ha stampato `Summary sent`, ma non ha conservato né validato il corpo JSON del Bot API e non espone un message_id. È quindi registrata come `NON_TRADE`, non come consegna Telegram confermata.

## 1. Ledger e statistiche

Ledger aggiornato: [pravda-signal-ledger-2026-11-08.csv](pravda-signal-ledger-2026-11-08.csv).

- Record: **87**
- Firme uniche: **87**
- Source ID unici: **87**
- Duplicati: **0**
- SPUTNIK: **37**
- GAGARIN: **50**
- `NON_TRADE`: **58**
- `ESITO_NON_VERIFICABILE`: **29**
- Fill verificati: **0**
- SL verificati: **0**
- TP verificati: **0**
- Win rate, average R, total R: **N/D**

L'ultima riga aggiunta è `run:42484703932/daily_summary/http_response`, firma `PRAVDA-GAGARIN-DAILY-SUMMARY-RUN42484703932-HTTP-RESPONSE`. È una notifica riepilogativa senza strumento, direzione, quotazione, livelli o ID Telegram. Non è un trade.

I 29 record non verificabili restano tali: non sono stati promossi a trade e non sono stati valutati con prezzi di strumenti/contratti non identificati.

## 2. SPUTNIK — collector, messaggi e fonti

### Ultima scansione di produzione

[GitHub Actions SPUTNIK #42467543117](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42467543117), job `128690443372`, avvio **09:31:31 UTC**, conclusione SUCCESS alle 09:31:41 UTC. Nessun artifact allegato.

Il job ha eseguito 30 test di regressione, tutti superati. Nella parte produttiva del log:
- SEC: HTTP 403, cooldown dichiarato 21.600 secondi, zero filing/operazioni estratte.
- White House RSS `https://www.whitehouse.gov/feed/`: HTTPError.
- Scansione intelligence pubblica: 2 correlazioni rilevate; un item nuovo riportato nel digest.
- GAGARIN handoff disabilitato: `GAGARIN_CLOUD_API_URL` e `GAGARIN_CLOUD_API_KEY` non configurati.
- La fonte dell'item è PUBLIC_RSS, URL archivio [Trump's Truth item 43524](https://www.trumpstruth.org/statuses/43524), pubblicato alle **03:53:01 UTC** e rilevato alle **09:31:37.313495 UTC**: ritardo **5h38m36s**. Dominio classificato MEDIA, event type OTHER, nessuna mappatura commodity/direzione.

### Messaggi Telegram attribuiti dal log

| ID | Generazione/log | ACK API | Contenuto e classificazione PRAVDA |
|---|---|---|---|
| #731 | 09:31:37.313495Z | 09:31:38.5640305Z | Digest notizia pubblica; non è segnale. Ritardo generazione→ACK circa 1,25 s. |
| #732 | 09:31:38.5641237Z | 09:31:38.5655282Z | GOLD, bias NEUTRAL, priorità catalizzatore 100/100, tecnica 5m UNAVAILABLE, NO_DIRECTION; nessun prezzo/entry/SL/TP/ATR. |
| #733 | 09:31:38.5655719Z | 09:31:38.5664615Z | GOLD, NO_DIRECTION, NOT_EXECUTED, score 100; nessun prezzo/entry/SL/TP/ATR. Il titolo dice CFD, il corpo dice future continuo front-month, scadenza esatta non verificata. |

#732 e #733 sono due messaggi della stessa analisi GOLD, non due setup. L'ACK Telegram prova l'accettazione API e non la consegna sul dispositivo. Il rischio 1,0% stampato nel messaggio #733 non è esposizione eseguita.

### Riepilogo SPUTNIK

[Daily Summary #42480644139](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42480644139): avvio 12:31:18 UTC, SUCCESS. Il cron nel workflow è 06:00 UTC: ritardo osservato **6h31m18s**. Il log conferma Telegram API message_id **#734** alle 12:31:25.2431545Z. Lo stato remoto caricato riportava transactions=0 e updated_at=09:31:37.340241Z; il codice seleziona il ramo “Nessun candidato in watch oggi”. Il corpo non è conservato nel log: il testo è ricostruito da codice e stato, non da una copia del messaggio. #734 è già nel ledger e non è duplicato.

[Telegram Polling #42466478249](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42466478249): avvio 09:16:25 UTC, SUCCESS, pending updates=0. Il workflow ha cron ogni 5 minuti. Il collector principale imposta `SPUTNIK_TELEGRAM_POLLING=0` e dichiara un listener dedicato attivo; non sono disponibili log del listener esterno, quindi non si presume che il polling complessivo sia fermo.

## 3. GAGARIN — monitor, quote e journal

### Ultimo monitor di produzione

[GitHub Actions GAGARIN #42467422750](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42467422750), job `128690080067`, avvio **09:29:58 UTC**, conclusione SUCCESS alle 09:30:17 UTC. Nessun artifact allegato.

Il log mostra:
- `DATABASE_URL` vuota;
- soglie effettivamente passate al job: probabilità 40, qualità 30, confidenza 35, RR 2,5, max stop 2,5 ATR;
- 8 commodity operative più EUR/USD e GBP/USD ausiliari;
- tutte le 10 voci stampate come MARKET_CLOSED;
- YAHOO stale: età da **127.811,4 a 137.416,2 secondi** (circa 35h30m–38h10m);
- BIQUOTE stale: EUR/USD 128.113,0 s e GBP/USD 128.113,6 s (circa 35h35m);
- timestamp assoluti delle quote, ticker provider risolti, mercato e scadenze non esposti.

Strumenti mostrati: Soia, Brent, Argento, WTI, Grano, EUR/USD, Mais, Oro, Rame, GBP/USD. Il paniere commodity osservato contiene Argento e non mostra Platino/Palladio: non coincide con quello richiesto (Argento escluso, Platino e Palladio inclusi).

Esito del monitor:
- Recorded entries: 0
- Updated open outcomes: 0
- New feedback signals: 0
- New additional live forecasts: 0
- `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`

Il WATCH pre-alert Telegram **#3719** è confermato nel log, round-trip 527 ms; il corpo non è conservato, quindi strumento/direzione/livelli non sono attribuibili.

### Daily Summary GAGARIN

[Daily Summary #42484703932](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42484703932): avvio **13:23:05 UTC**, SUCCESS, nessun artifact. Il cron è 06:15 UTC: ritardo osservato **7h08m05s**. Alle 13:23:11.441557Z il log stampa “Summary sent”.

Il workflow non legge la risposta JSON Telegram, non verifica `ok=true` e non registra `result.message_id`: si può attestare solo che `urlopen` è ritornato senza eccezione, non un ACK Telegram verificato né la consegna al dispositivo. Il corpo non è loggato.

Il workflow non passa `DATABASE_URL`; la funzione `summarize()` legge `gagarin_feedback.csv` locale. Il file non esiste nel tree di main e non c'è database configurato nel job: il riepilogo usa quindi una lista feedback vuota. Il record della notifica è stato aggiunto al ledger con stato `HTTP_RESPONSE_RECEIVED_API_BODY_NOT_VALIDATED`.

### Journal e persistenza

File main consultati:
- `journal.csv`: letture datate 17 ottobre, tutte “nessun segnale”.
- `paper_trade_log.csv`: WTI LONG del 8 ottobre marcato LEGACY_IMPORT, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55; campi provider/ticker/time quote/mercato/scadenza/esito vuoti.
- `data/paper_open.json`: ticket WTI P0001 ancora OPEN, senza provenienza contrattuale o P&L.
- `position.json`: Heating Oil LONG del 15 settembre, non riconciliato con lo stato corrente.
- `commodities_monitor_state.json`, `commodities_prediction_log.json`, `commodities_direction_state.json`: artefatti legacy di settembre, non prova di posizioni correnti.

Il monitor dichiara zero posizioni aperte. Gli artefatti legacy non sono fill verificati e restano fuori dalle statistiche.

## 4. Difetti dimostrati e PR esistenti

### GAGARIN outcome engine su main

In `engine/feedback.py`:
- FIELDS conserva symbol/timeframe e livelli, ma non provider, ticker di esecuzione, market type e scadenza;
- `update_open_outcomes()` abbina gli stati per symbol/timeframe, non per identità completa del provider/contratto;
- se una stessa candela tocca SL e TP, il codice controlla prima SL e registra STOP. OHLC non prova l'ordine intrabar: per il protocollo PRAVDA deve restare ESITO NON VERIFICABILE.

[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) è ancora OPEN, non merged, 6 commit ahead e 4 behind rispetto a main. Sei workflow di test associati al suo head risultano SUCCESS (run del 5 novembre), ma il commento Cloudflare Workers del 5 novembre segnala deployment FAILURE. Il rilievo sul confronto provider mancante nella funzione di matching è già registrato nel commento PRAVDA #6706619879. La PR non è in produzione.

Altre PR GAGARIN ancora aperte: #200 e #202 (persistenza/riepilogo), #219 (rimozione FX), #221 (rimozione route FX, draft), #225 (offset cron, draft), #237 (draft, impilata sulla branch della #236 e non direttamente su main). Nessuna è stata integrata da questo audit.

### SPUTNIK

- [PR #131](https://github.com/andreameloni1984-sys/trump-trucker/pull/131) endpoint White House: OPEN, mergeable; i due test PR #42479427517 e #42479427775 sono SUCCESS. La run di produzione #42467543117 ha ancora usato il vecchio endpoint e ha registrato HTTPError. La correzione non è in produzione.
- [PR #147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147) separazione dal handoff GAGARIN e [PR #148](https://github.com/andreameloni1984-sys/trump-trucker/pull/148) anti-ripetizione: entrambe OPEN e non integrate.

## 5. Cadenza osservata

Cut-off 13:25:22 UTC; gap dalla più recente run produttiva visibile:
- SPUTNIK collector, cron 2-59/5: ultima 09:31:31, gap **3h53m51s**.
- SPUTNIK GitHub Telegram polling, cron */5: ultima 09:16:25, gap **4h08m57s**.
- GAGARIN monitor, cron */15: ultima 09:29:58, gap **3h55m24s**.

I due daily summary sono workflow distinti, non scansioni di mercato. Le singole run sono SUCCESS, ma la cadenza osservata non corrisponde a quella dichiarata. La causa dei ritardi non è dimostrata; non attribuirli a un filtro orario senza prova.

## 6. Esiti e limiti

Non è disponibile un segnale con fill/entry verificato e identità completa di ticker, provider, mercato e contratto, seguito da candele dello stesso identico contratto. Nessun nuovo SL/TP può essere classificato. Non si è usato spot per valutare futures né un contratto continuo per sostituire una scadenza specifica.

Fonti consultate: GitHub Actions e log dei job sopra linkati; workflow YAML SPUTNIK collector, Telegram polling e daily summary; workflow GAGARIN monitor e daily summary; ledger PRAVDA; file journal/stato GAGARIN; `engine/feedback.py` e `state_store.py`; metadati e discussioni delle PR elencate.

## 7. Registrazione e prossimo controllo

- Ledger aggiornato con una sola nuova riga GAGARIN, source ID univoco `run:42484703932/daily_summary/http_response`.
- Verifica post-scrittura: **87 record / 87 firme uniche / 87 source ID unici / 0 duplicati**.
- Commit ledger: `991a5e637e74324375d4cb6058cb7be304a823d3`.
- Main GAGARIN osservato al cut-off: `69bb6d070dc180f9fc671c4f87b3c5fd19be1009`.

Prossimo controllo: distinguere nuove scansioni di produzione da daily summary/test PR; verificare se la cadenza riprende; acquisire log/artifact con corpo e ID Telegram; richiedere quote fresche e identità provider/ticker/mercato/scadenza prima di registrare un setup; valutare outcome soltanto con candele successive dello stesso contratto.

**Perimetro rispettato:** nessun codice, strategia, filtro, punteggio o rischio modificato; nessun merge/deploy, ordine reale, modifica a secret o Render, servizio a pagamento o accesso Trading212 dichiarato. Telegram: API ACK solo dove il log lo prova; nessuna consegna al dispositivo dichiarata. PAPER ONLY.
