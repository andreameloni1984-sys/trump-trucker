# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Data controllo:** 7 novembre 2026, 12:18 UTC (13:18 Europe/Rome)  
**Modalità:** sola lettura dei repository, Actions, log e artefatti; aggiornati esclusivamente il rapporto PRAVDA e il ledger. PAPER ONLY.

## Sintesi esecutiva

- Ultima scansione mercato SPUTNIK verificata: **09:50:55 UTC**, run [#42361443562](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42361443562), SUCCESS. Età al controllo: **2h27m22s**.
- Ultima scansione GAGARIN verificata: **08:55:05 UTC**, run [#42357485498](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42357485498), SUCCESS. Età al controllo: **3h23m12s**.
- SPUTNIK ha inoltre eseguito il daily summary run [#42371347665](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42371347665) alle **12:11:08 UTC** e l'API Telegram ha confermato message_id **720** alle **12:11:16.8618648 UTC**. È una notifica riepilogativa, **non** una scansione di mercato. Il workflow dichiara cron 06:00 UTC: avvio osservato 6h11m08s dopo l'orario configurato. Il body del messaggio non è conservato nei log, quindi nessuno strumento o candidato può essergli attribuito.
- Nessun fill verificato; nessun esito SL/TP verificabile; nessuna statistica di performance calcolabile.

## 1. GitHub Actions e cadenza

### SPUTNIK

Workflow monitor: `.github/workflows/trump_tracker.yml`, cron `2-59/5 * * * *`. L'ultima run di mercato trovata fra le esecuzioni recenti è #42361443562 (09:50:55–09:51:08 UTC). La successiva run #42371347665 è il workflow distinto `daily-summary.yml`, non il collector. La run Telegram polling #42358078695 (09:03:26 UTC) è anch'essa un workflow separato.

La run monitor ha eseguito i test Telegram/intelligence; i log dei test contengono un message_id 731 simulato e messaggi con delivery non confermata: **esclusi** dal conteggio della produzione. I messaggi di produzione verificati sono #717, #718 e #719, con API ACK rispettivamente 436, 432 e 398 ms. Un ACK API non prova la visualizzazione sul dispositivo.

Il workflow monitor conserva ancora il passo `git push origin main` per `sputnik_state.json`. Il commit [1282aa3](https://github.com/andreameloni1984-sys/trump-trucker/commit/1282aa3cf75f491b71d5d68926e42fe0de2a6945) aggiorna lo stato alle 09:51:01 UTC e aggiunge due elementi intelligence. La PR #144 per spostare la persistenza da main è OPEN, non integrata.

### GAGARIN

Workflow monitor: `.github/workflows/gagarin-monitor.yml`, cron `*/15 * * * *`. L'ultima run schedule trovata è #42357485498 (08:55:05–08:55:23 UTC). Le numerose run successive visibili sono test push/PR, non scansioni programmate. Nessuna nuova schedule run GAGARIN è stata trovata nella finestra recente interrogata. La causa dell'interruzione non è dimostrata.

## 2. SPUTNIK — intelligence e messaggi

La run #42361443562 riporta SEC HTTP 403 (cooldown 21.600 secondi), White House RSS HTTPError, zero filing e due findings.

1. Item RSS `55dc05ab6915f760a77f4714`: pubblicato 03:12:47 UTC, rilevato 09:51:01.443735 UTC; latenza circa **6h38m14s**. Classificazione MEDIA / OTHER, NO_ANALOGUE. Non è un catalizzatore commodity dimostrato.
2. Item `ce679ecd83664e21e503141d`: pagina aggregata [TRUTH_ARCHIVE](https://www.trumpstruth.org/), senza URL individuale e senza timestamp di pubblicazione. Il record ha `PUBLIC_SOURCE_TEXT_PAGE_LEVEL` ma l'action/reaction lo classifica TRADE_ESCALATION con analogia tariffaria 2025. La pagina aggrega post differenti: l'analogia non prova un catalizzatore corrente. Lo stato persistito mostra `events: {}`.

Messaggi:
- #717: digest intelligence, API ACK 436 ms.
- #718: GOLD, WATCH/NEUTRAL, tecnica 5m unavailable, D-L-A NEUTRAL, score 70.
- #719: scheda CFD GOLD, NOT_EXECUTED; front-month continuo, scadenza esatta e indipendenza upstream non verificate.

Per #718/#719 mancano ticker runtime verificato, scadenza esatta, provider e timestamp della quotazione, entry, SL, TP e ATR. `GC=F` è mapping configurato, non identità di contratto provata. Score 70 non è validità operativa. Nessun trade.

### Daily summary #720

Il job #42371347665 ha confermato `message_id=720` via API. Il codice del workflow carica `sputnik_state.json` e costruisce un riepilogo WATCH, ma il log non conserva il body. Il ledger registra #720 come notifica non attribuibile, NON_TRADE, senza strumento, direzione, quotazione o livelli. Nessuna prova di visualizzazione sul dispositivo.

## 3. GAGARIN — quote, classificazioni e Telegram

La run #42357485498 ha classificato MARKET_CLOSED tutte le otto commodity e i due strumenti FX di contesto.

Quote Yahoo commodity:
- Brent 39.618,3 s (~11h00m18s);
- WTI 39.618,0 s;
- Oro 39.616,5 s;
- Argento 39.617,6 s;
- Rame 39.617,8 s;
- Soia 49.218,9 s (~13h40m19s);
- Grano 49.218,5 s;
- Mais 49.218,7 s.

EUR/USD e GBP/USD: provider BIQUOTE, età rispettivamente 39.619,4 s e 39.619,9 s. Le età sono riportate dal log; timestamp puntuale della quotazione, reference price, ticker runtime, market type e scadenza non sono esposti. La chiusura del sabato è coerente, ma le quote sono stale e non possono validare ingressi.

Candidati direzionali:
- WTI SHORT: probabilità 66, quality 57,5, confidence 37.
- Argento LONG: 59, quality 49,5, confidence 32.
- Mais LONG: 63, quality 52,5, confidence 35.

Tutti `PAPER_WATCH`, bloccati da MARKET_CLOSED/LIVE_DATA_NOT_FRESH, trigger non confermato o discordante e ulteriori controlli. Entry, SL, TP1–TP3 e ATR assenti. Non sono operazioni.

Telegram #3712: API SEND CONFIRMED, round-trip 443 ms. Il body non è conservato; non si attribuisce la board ai tre candidati. Il log riporta Recorded entries=0, Updated open outcomes=0, New feedback signals=0, New additional live forecasts=0 e `signals=0 open=0 closed=0`.

## 4. Journal e feedback GAGARIN

Artefatti letti su main:
- `journal.csv`: 11 righe del 17 ottobre, tutte con “nessun segnale”.
- `paper_trade_log.csv`: un solo record legacy WTI del 8 ottobre 16:23 UTC, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55; nota “Chiusura spot 6 ott 2026. Nessun esito.” Non contiene prova di fill, provider o contratto eseguito.
- `data/paper_open.json`: ticket P0001, lo stesso WTI legacy, stato OPEN, PnL null; non è un secondo trade.
- `position.json`: record legacy Heating Oil HO/USD LONG, aperto 15 settembre; non va confuso con P0001.
- `commodities_prediction_log.json`: 981 record, ultimo 15 settembre 2026; gli action label COMPRA ORA e gli status PENDING non sono fill.
- `gagarin_feedback.csv`: 404/NOT_FOUND nel repository pubblico.

Nel log monitor `DATABASE_URL` è vuoto. Il workflow dichiara che il journal operativo non viene committato nel repository pubblico e che la persistenza va riabilitata solo dopo storage privato verificato. Nessuna prova di backend durevole nel run esaminato.

## 5. Outcome engine e PR esistenti

Su main, `engine/feedback.py`:
- il record feedback non include identità completa ticker/provider/market/scadenza;
- l'ID usa simbolo, direzione, timeframe, livelli e timestamp barra;
- l'abbinamento delle candele è per simbolo + timeframe, con fallback se esiste un solo stato;
- se SL e TP vengono toccati nella stessa candela, il codice classifica STOP.

Questo non soddisfa la policy PRAVDA: il caso intrabar simultaneo deve essere `ESITO NON VERIFICABILE`, e il matching deve usare lo stesso identico strumento/contratto e provenienza dichiarata.

PR #192 è OPEN, non integrata; aggiunge mercato/contratto e trattamento non verificabile dello stesso-bar SL+TP. Il commento PRAVDA del 11:55 UTC resta aperto: il matching della branch non confronta ancora esplicitamente il provider del segnale con quello della serie successiva. Non sono state eseguite nuove modifiche o rerun.

Altre PR rilevanti:
- SPUTNIK #144 OPEN (persistenza fuori da main), #145 OPEN (provenienza quote), #148 OPEN (gate nuovi catalizzatori).
- GAGARIN #175 OPEN (webhook/polling 409), #192 OPEN (outcome/contratto), #202 DRAFT (PostgreSQL journal), #232 DRAFT e #233 DRAFT (identità e isolamento CFD).
- PR #233 resta basata su branch feature #207, non su main. Il precedente build Cloudflare del target `telegram-github-bridge/production` risultava FAILED alle 08:18 UTC; nessuna prova di deploy riuscito. Questo audit non ha modificato configurazioni Cloudflare.

## 6. Ledger PRAVDA

Il ledger giornaliero contiene **53 record, 53 firme uniche, zero duplicati**. L'ultima riga aggiunta è:
- firma `PRAVDA-SPUTNIK-DAILY-SUMMARY-RUN42371347665-MSG720`;
- record type `daily_watch_summary_notification_unresolved`;
- generazione run 12:11:08 UTC;
- invio/API ACK 12:11:16.8618648 UTC;
- Telegram message_id 720;
- outcome NON_TRADE.

La riga registra la notifica senza attribuirle uno strumento o un segnale che i log non documentano. Non sono stati aggiunti duplicati per #717–#719 o #3712: erano già presenti.

## 7. Esiti e statistiche

- Trade con fill verificato: **0**.
- SL verificati: **0**.
- TP verificati: **0**.
- Esiti cronologici verificabili sullo stesso contratto: **0**.
- Win rate e Average R: **N/D**.

Tutti i candidati WATCH/NOT_EXECUTED e il WTI legacy restano NON_TRADE o ESITO NON VERIFICABILE secondo la disponibilità delle prove. Non è stato effettuato alcun backtest.

## 8. Prossimo controllo

1. Verificare una nuova run schedule SPUTNIK di mercato, distinta dal daily summary.
2. Verificare la ripresa delle schedule GAGARIN ogni 15 minuti.
3. Alla riapertura dei mercati, richiedere timestamp, ticker, provider, mercato e scadenza della quotazione, oltre a OHLC successivi dello stesso contratto.
4. Ricontrollare main e PR #192 per il matching della provenienza e il trattamento same-bar.
5. Verificare il backend del journal solo tramite evidenza del runtime, senza leggere o modificare segreti.
6. Verificare che il polling Telegram non confligga con il webhook; nessuna consegna al dispositivo va dedotta dal solo API ACK.

**Vincoli rispettati:** nessun codice bot modificato; nessuna strategia, soglia, filtro o rischio modificato; nessun merge, deploy o rerun; nessun ordine reale; nessuna modifica a Render o segreti; nessun servizio a pagamento. PAPER ONLY.
