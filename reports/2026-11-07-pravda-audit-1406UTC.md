# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Data controllo:** 7 novembre 2026, 14:06:45 UTC (15:06:45 Europe/Rome)  
**Perimetro:** repository, GitHub Actions, log, journal, feedback, PR e artefatti pubblici.  
**Modalità:** PAPER ONLY. Nessuna modifica a codice, strategia, filtri, punteggi o rischio. Aggiornati soltanto il ledger PRAVDA e questo rapporto.

## Sintesi esecutiva

- Ultimo monitor di mercato SPUTNIK: **09:50:55 UTC**, run [#42361443562](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42361443562), SUCCESS. Età al controllo: **4h15m50s**.
- Ultimo monitor GAGARIN: **08:55:05 UTC**, run [#42357485498](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42357485498), SUCCESS. Età al controllo: **5h11m40s**.
- Nessun nuovo monitor di mercato successivo a quelle due run nelle esecuzioni programmate esaminate. I workflow restano configurati a 5 minuti (SPUTNIK) e 15 minuti (GAGARIN), ma gli intervalli osservati sono di diverse ore. La causa dei ritardi non è dimostrata.
- SPUTNIK ha eseguito un riepilogo giornaliero alle 12:11 UTC e Telegram ha confermato l'API con message_id **720**. Non è una scansione di mercato.
- GAGARIN ha eseguito il riepilogo giornaliero alle 12:58 UTC; il log stampa “Summary sent”, ma non conserva né valida `ok=true` o `result.message_id`. **Accettazione Telegram non verificata.**
- GAGARIN ha aggiornato il driver snapshot alle 13:37 UTC: run SUCCESS, ma EIA e USDA non hanno restituito dati utilizzabili.
- **Nessun fill verificato; nessun esito SL/TP verificabile; win rate e average R non calcolabili.**

## 1. GitHub Actions e cadenza

### SPUTNIK

| Run | Evento | Avvio UTC | Esito | Significato |
|---|---|---:|---|---|
| [#42361443562](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42361443562) | Monitor schedule | 09:50:55 | SUCCESS | Ultima scansione di mercato |
| [#42358078695](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42358078695) | Telegram polling | 09:03:26 | SUCCESS | Runner polling, non scansione mercato |
| [#42371347665](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42371347665) | Daily Summary | 12:11:08 | SUCCESS | Riepilogo, non scansione |

Il cron del monitor in `.github/workflows/trump_tracker.yml` è `2-59/5 * * * *`. Tra i due monitor più recenti, 02:57:24 e 09:50:55 UTC, sono trascorse **6h53m31s**. Il daily summary dichiara cron 06:00 UTC ma è partito alle 12:11:08: ritardo osservato **6h11m08s**.

Il daily summary ha registrato alle 12:11:16.8618648 UTC `message_id=720`, dopo validazione di `confirmed_message_id`. Questo dimostra l'accettazione da parte dell'API Telegram, non la visualizzazione sul dispositivo. Il corpo non è conservato, quindi non si attribuiscono strumenti o direzioni.

### GAGARIN

| Run | Evento | Avvio UTC | Esito | Significato |
|---|---|---:|---|---|
| [#42357485498](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42357485498) | Paper Monitor | 08:55:05 | SUCCESS | Ultima scansione di mercato |
| [#42374841686](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42374841686) | Daily Summary | 12:58:56 | SUCCESS | Riepilogo, ACK Telegram non verificato |
| [#42377815727](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42377815727) | FETCH DRIVERS | 13:37:29 | SUCCESS | Aggiornamento driver, non segnale |

Il cron monitor in `.github/workflows/gagarin-monitor.yml` è `*/15 * * * *`. Tra i monitor 02:13:56 e 08:55:05 UTC sono trascorse **6h41m09s**. Il daily summary dichiara cron 06:15 UTC ma è partito alle 12:58:56: ritardo osservato **6h43m56s**. Anche FETCH DRIVERS, cron 07:00 UTC, è partito alle 13:37:29: ritardo **6h37m29s**.

La run Daily Summary stampa `Summary sent` alle 12:59:03.358 UTC, ma il workflow attuale non interpreta il JSON Telegram né richiede un message_id positivo. Il body non è nei log: nessuno strumento o segnale può essergli attribuito.

## 2. SPUTNIK — intelligence e messaggi

### Stato persistito

Il blob corrente di `sputnik_state.json` è stato letto direttamente (1.396.735 byte):
- `updated_at=2026-11-07T09:51:01.503631Z`;
- 500 elementi in `intelligence_history`;
- `events={}` (zero eventi attivi);
- offset Telegram persistito.

L'item RSS più recente:
- ID `55dc05ab6915f760a77f4714`;
- URL individuale [statuses/43499](https://www.trumpstruth.org/statuses/43499);
- pubblicato 03:12:47 UTC, rilevato 09:51:01.443735 UTC;
- latenza **6h38m14.443s**;
- dominio MEDIA, `event_type=OTHER`, `NO_ANALOGUE`.

Non costituisce un catalizzatore commodity direzionale dimostrato.

Il secondo ID `ce679ecd83664e21e503141d` punta alla homepage generica di TRUTH_ARCHIVE, senza data di pubblicazione individuale. La classificazione `TRADE_ESCALATION` è page-level e non prova una nuova escalation.

### Log della run #42361443562

- SEC: HTTP 403, cooldown 21.600 secondi; filing=0.
- White House RSS: HTTPError.
- Nuove correlazioni pubbliche=2; nuove operazioni documentate=0.
- GAGARIN handoff disabilitato per assenza delle variabili API.

Messaggi API accettati:
- #717, digest intelligence, 436 ms;
- #718, analisi GOLD, 432 ms;
- #719, scheda CFD GOLD, 398 ms.

#718 riporta GOLD NEUTRAL, `NO_DIRECTIONAL_NEWS`, tecnica 5m non disponibile e decisione WATCH. #719 dichiara front-month continuo, scadenza esatta e indipendenza upstream non verificate. Nessuna entry, SL, TP o ATR utilizzabile. Il mapping GC=F non prova l'identità del contratto effettivo.

**Classificazione PRAVDA:** tre notifiche API-accepted, nessuna operazione. Il messaggio #731 nei test automatici è escluso dalla produzione.

### PR SPUTNIK

- [PR #144 — Persist SPUTNIK state outside main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN, non draft, **1 commit avanti / 0 indietro** rispetto a main. CI sul branch: 193 test ranking e 66 test Telegram menu, entrambi SUCCESS ([#42372850500](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42372850500), [#42372850529](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42372850529)). Il branch `sputnik-state` non esiste ancora (lettura branch API 404); la correzione non è integrata. Main continua a eseguire `git push origin main` per lo stato.
- [PR #148 — Stop repeating recommendations without a new catalyst](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN, **2 avanti / 14 indietro** rispetto al main corrente. Il gate item-level richiede evidence, event_id, URL e published, ma non esclude esplicitamente `event_type=OTHER`. La run attuale mostra il caso: item MEDIA/OTHER e successivi messaggi GOLD neutrali #718/#719. Il rilievo è già stato commentato da PRAVDA (#6706624290); non duplicato.
- [PR #145 — quote provenance](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN, non integrata.

## 3. GAGARIN — quotazioni, classificazioni e journal

### Ultimo monitor #42357485498

Tutte le commodity risultavano `MARKET_CLOSED`; i provider riportavano dati stale. Età delle quote:
- Brent 39.618,3 s (~11h00m18s), Yahoo;
- WTI 39.618,0 s (~11h00m18s), Yahoo;
- Oro 39.616,5 s (~11h00m16s), Yahoo;
- Argento 39.617,6 s (~11h00m18s), Yahoo;
- Rame 39.617,8 s (~11h00m18s), Yahoo;
- Soia 49.218,9 s (~13h40m19s), Yahoo;
- Grano 49.218,5 s (~13h40m19s), Yahoo;
- Mais 49.218,7 s (~13h40m19s), Yahoo.

Il monitor ha inoltre stampato EUR/USD e GBP/USD come `CONTESTO FX — NON OPERATIVO`, provider BiQuote: non li conto come commodity operative né come segnali.

### Classifica registrata

| Strumento | Direzione | Prob. | Quality | Confidence | Stato/blocco principale |
|---|---|---:|---:|---:|---|
| Brent | — | 58 | 40 | 25 | PAPER_WATCH; setup/livelli assenti |
| WTI | SHORT | 66 | 57,5 | 37 | PAPER_WATCH; stale, trigger non confermato e discordante |
| Soia | — | 30 | 0 | 0 | PAPER_WATCH; setup/livelli assenti |
| Oro | — | 30 | 0 | 0 | PAPER_WATCH; setup/livelli assenti |
| Grano | — | 38 | 15 | 5 | PAPER_WATCH; setup/livelli assenti |
| Argento | LONG | 59 | 49,5 | 32 | PAPER_WATCH; stale, trigger discordante, RR/confidence fail |
| Mais | LONG | 63 | 52,5 | 35 | PAPER_WATCH; stale, trigger discordante, RR1 fail |
| Rame | — | 40 | 15 | 5 | PAPER_WATCH; setup/livelli assenti |

Nessuno dei tre candidati direzionali ha entry, SL, TP o ATR operativo. Il board #3712 è stato accettato dall'API in 443 ms, ma il body non è conservato: non è possibile attribuirlo con certezza a WTI, Argento o Mais.

Il log dichiara:
`Recorded entries: 0`, `Updated open outcomes: 0`, `New feedback signals: 0`, `New additional live forecasts: 0`, `signals=0 open=0 closed=0`.

Il workflow main espone soglie 40/30/35, RR minimo 2,5, max stop 2,5 ATR, buffer 0,15 ATR e stop minimo 0,80 ATR. PRAVDA li registra senza modificarli.

### Journal e feedback

Artefatti pubblici riletti:
- `journal.csv`: 11 righe, tutte “nessun segnale”.
- `data/paper_open.json`: WTI P0001 LONG, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55, status OPEN, PnL null.
- `paper_trade_log.csv`: lo stesso P0001 come LEGACY_IMPORT; non è una seconda operazione.
- `position.json`: vecchia posizione Heating Oil HO/USD LONG, entry 4,8844, SL 4,5418, TP1 5,4473, TP2 5,6284, TP3 5,882, aperta il 15 settembre 2026.
- `commodities_prediction_log.json`: 981 record, 945 PENDING e 36 NEUTRALE; ultimo record 15 settembre 2026, RBOB LONG con action COMPRA ORA ma stato PENDING.
- `gagarin_feedback.csv`: 404 / non presente nel repository pubblico.

Il run monitor ha registrato `DATABASE_URL:` vuoto. In `engine/feedback.py`, PostgreSQL è selezionato solo se DATABASE_URL è non vuoto; il backend fallback è `LOCAL_CSV_NO_DATABASE_URL`. Non è dimostrata persistenza durevole. Le posizioni WTI e Heating Oil sono legacy: mancano fill verificato, ticker/contratto esatto, provider, timestamp quote e candele successive omogenee. **ESITO NON VERIFICABILE**, senza contarle come trade verificati.

### Driver snapshot del 7 novembre

[FETCH DRIVERS #42377815727](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42377815727) ha aggiornato [data/driver_snapshot.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/data/driver_snapshot.json), commit [69bb6d0](https://github.com/andreameloni1984-sys/commodity-news-scanner/commit/69bb6d070dc180f9fc671c4f87b3c5fd19be1009), `read_at=13:37:41Z`.

- EIA crude stocks WCRSTUS1: `no_data`.
- EIA natgas storage NW2_EPG0_SWO_R48_BCF: `no_data`.
- USDA world balance wheat/corn/soybeans: valori e date null.
- FRED dollar index: 121,6656, data 30 ottobre 2026.
- FRED 10y real rate: 2,60, data 5 novembre 2026.
- Inventories, curve, supply shock, refined, systematic flow, weather, harvest, season e hedging pressure restano UNKNOWN.

Il workflow è SUCCESS, ma la copertura driver è parziale. Non si deduce alcun bias di mercato dai campi UNKNOWN.

## 4. Outcome engine, PR e difetti dimostrati

### Outcome

Su main, `engine/feedback.py` conserva soltanto `data_source/data_status` e associa soprattutto per simbolo/timeframe. Non identifica provider, market type e scadenza in modo sufficiente; quando SL e TP sono toccati nella stessa candela, il codice main registra STOP anziché ESITO NON VERIFICABILE.

[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) aggiunge provider, quote ticker, market type e identità futures, oltre alla gestione ambigua same-bar SL/TP. È OPEN, **6 avanti / 4 indietro** rispetto al main corrente. Sul branch, `_market_contract_match` confronta quote symbol, market type e contract month/expiry, ma non confronta effettivamente il provider della serie successiva con quello del segnale, nonostante la docstring. Rilievo già commentato da PRAVDA (#6706619879), non duplicato.

### PR rilevanti

| PR | Stato | Confronto con main corrente | Nota audit |
|---|---|---:|---|
| GAGARIN #202 | DRAFT | 18 avanti / 2 indietro | PostgreSQL journal; non integrata |
| GAGARIN #200 | DRAFT | 8 avanti / 2 indietro | daily summary su store condiviso; non integrata |
| GAGARIN #190 | OPEN | 2 avanti / 4 indietro | richiede Telegram API ACK con message_id; non integrata |
| GAGARIN #175 | OPEN | non ricalcolato qui | polling webhook 409; non integrata |
| GAGARIN #221 | DRAFT | 14 avanti / 1 indietro | rimozione route FX residue |
| GAGARIN #222 | DRAFT | 6 avanti / 1 indietro | rimuove il session veto: modifica un filtro, non integrata |
| GAGARIN #231 | DRAFT | 31 avanti / 1 indietro | modifica ampia a Governor/Telegram/calendario |
| GAGARIN #232 | DRAFT | 4 avanti / 1 indietro | comandi CFD fail-closed, nessun feed broker |
| GAGARIN #233 | DRAFT | 21 avanti / 2 indietro | identità SPOT senza scadenza vs future con scadenza; nessun feed Trading 212 |
| GAGARIN #223 | DRAFT | 10 avanti / 1 indietro | scan M5 osservativa a 7 strumenti, non attiva |
| GAGARIN #225 | DRAFT | 2 avanti / 1 indietro | offset cron monitor, non attivo |

PRAVDA non ha richiesto merge e non ha cambiato filtri, strategia, punteggi o rischio. In particolare la PR #222 modifica un veto di sessione: resta non integrata e non viene promossa da questo audit.

### Telegram polling

La run [#42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549) è fallita alle 00:16:30 UTC con:
`getUpdates blocked by Telegram API error_code=409: webhook is active; polling cannot run while webhook mode is enabled.`
La PR #175 è ancora aperta. Non è dimostrata la risoluzione runtime.

### Nuovi rilievi comunicati ai reparti

- [PR #190 commento PRAVDA #6707993322](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/190#issuecomment-6707993322): il daily summary GAGARIN logga “Summary sent” senza interpretare `ok=true` e message_id; verde Actions non prova API acceptance.
- [PR #200 commento PRAVDA #6707993650](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/200#issuecomment-6707993650): il daily summary non passa DATABASE_URL né installa psycopg; non può leggere il medesimo store durevole del monitor.

I commenti sono rilievi di audit; nessun codice è stato modificato.

## 5. Ledger PRAVDA e statistiche

Il ledger è stato riletto, controllato per firma e source_record_id e aggiornato con una sola nuova osservazione: tentativo di daily summary GAGARIN run #42374841686, classificato `daily_watch_summary_notification_unresolved`. La riga conserva `sent_at=NOT_CONFIRMED`, nessun message_id, nessuno strumento e nessun prezzo.

- Record: **54**.
- Firme uniche: **54**.
- Source ID unici: **54**.
- Duplicati: **0**.
- Nuove osservazioni in questo controllo: **1**, notifica riepilogativa non verificata; **0 nuovi segnali di mercato**.

La nuova riga non è un trade. Il campione finanziario resta:
- fill verificati: **0**;
- SL verificati: **0**;
- TP verificati: **0**;
- outcome verificabili: **0**;
- win rate: **N/D**;
- average R: **N/D**.

Le lacune del ledger misto (include predizioni storiche, WATCH, intelligence e notifiche, non soltanto trade): timestamp invio mancanti 34; ticker mancanti/non esposti 26; market type mancanti/non esposti 44; scadenza non registrata 54; provider mancante/non attribuibile 37; timestamp quote mancante/non esposto 53; entry/SL/TP1 mancanti 26; ATR mancante 42. Questi valori non sono tassi di completezza dei soli trade, perché la maggioranza dei record non è un trade.

## 6. Fonti consultate

- GitHub Actions e log SPUTNIK: [monitor #42361443562](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42361443562), [polling #42358078695](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42358078695), [daily summary #42371347665](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42371347665).
- GitHub Actions e log GAGARIN: [monitor #42357485498](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42357485498), [daily summary #42374841686](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42374841686), [driver snapshot #42377815727](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42377815727), [polling failure #42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549).
- File main: `sputnik_state.json`, `gagarin-monitor.yml`, `daily-summary.yml`, `driver_snapshot.json`, `journal.csv`, `data/paper_open.json`, `paper_trade_log.csv`, `position.json`, `commodities_prediction_log.json`, `engine/feedback.py`.
- PR e commenti elencati nelle sezioni 2 e 4.
- Nessuna quotazione/candela successiva è stata usata per valutare un trade: non esistono fill e identità complete dello stesso contratto per i candidati esaminati. Nessun servizio a pagamento e nessun accesso Trading 212 sono stati utilizzati o dichiarati.

## 7. Prossimo controllo

1. Verificare una nuova run di mercato SPUTNIK distinta dal daily summary e la ripresa della cadenza 5m.
2. Verificare una nuova run monitor GAGARIN e, alla riapertura, quote fresche con ticker, provider, timestamp, mercato e scadenza.
3. Verificare il backend feedback con solo stato/contatori non sensibili; non leggere né modificare segreti.
4. Verificare API ACK Telegram esplicito per GAGARIN daily summary e risoluzione runtime del 409 polling.
5. Dopo eventuale integrazione autorizzata della PR #144, verificare il primo ciclo write/read del branch `sputnik-state`.
6. Valutare un eventuale fill PAPER soltanto su candele successive dello stesso identico strumento e contratto; altrimenti ESITO NON VERIFICABILE.

**Sicurezza:** nessun codice dei bot modificato; nessuna strategia, filtro, soglia, punteggio o rischio modificato; nessun merge, deploy, rerun, ordine reale, modifica Render o segreto. Nessun servizio a pagamento. PAPER ONLY.
