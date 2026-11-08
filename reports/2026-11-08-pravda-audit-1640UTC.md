# PRAVDA — audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-08 16:40:11 UTC (17:40:11 Europe/Rome)**

## Sintesi esecutiva

Controllati i due repository su `main`, le ultime GitHub Actions di produzione e i relativi log completi, i file di stato, il ledger PRAVDA, i journal/feedback GAGARIN, il codice di valutazione outcome e le PR pertinenti.

**Nuova evidenza:** entrambi i motori hanno completato una nuova run domenica 8 novembre:
- SPUTNIK [run #42498971172](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42498971172), SUCCESS, avviata alle 16:15:37 UTC.
- GAGARIN [run #42499039797](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42499039797), SUCCESS, avviata alle 16:16:25 UTC.

Nessuna delle due ha prodotto un'operazione eseguibile o un fill verificabile. SPUTNIK ha rilevato un item pubblico, ma senza mapping direzionale a una commodity; GAGARIN ha trovato tutti gli strumenti con mercato chiuso e quotazioni stale.

Sono state aggiunte **4 righe nuove** al ledger: tre record SPUTNIK (#735, #736, #737) e un WATCH pre-alert GAGARIN (#3722). Il page-level snapshot TRUTH_ARCHIVE della stessa scansione SPUTNIK non è stato contato come riga separata perché non ha identità individuale e può duplicare l'item pubblico già registrato.

## 1. Integrità dello storico

Ledger: [pravda-signal-ledger-2026-11-08.csv](pravda-signal-ledger-2026-11-08.csv)

| Indicatore | Conteggio |
|---|---:|
| Record complessivi | 91 |
| SPUTNIK | 40 |
| GAGARIN | 51 |
| Firme uniche | 91 |
| Source ID unici | 91 |
| Duplicati firma | 0 |
| Duplicati source ID | 0 |
| NON_TRADE | 62 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |

Win rate, average R e total R: **N/D**. I 29 record `ESITO_NON_VERIFICABILE` sono record storici privi di esito dimostrabile, non necessariamente 29 trade. I 62 `NON_TRADE` non entrano nelle statistiche di performance. Nessun nuovo record è stato classificato come trade.

### Nuovi record inseriti

| Record | Identificativo | Classificazione | Esito |
|---|---|---|---|
| SPUTNIK | event_id `1502eca09bd530d4145496b7`, Telegram #735 | item PUBLIC_RSS senza mapping commodity | NON_TRADE |
| SPUTNIK | run #42498971172 / message #736 | GOLD NEUTRAL, NO_DIRECTION | NON_TRADE |
| SPUTNIK | run #42498971172 / message #737 | GOLD, NOT_EXECUTED; corpo identifica future continuo, non CFD verificato | NON_TRADE |
| GAGARIN | run #42499039797 / message #3722 | WATCH pre-alert senza corpo conservato e senza attribuzione strumento | NON_TRADE |

Per #736 e #737 i due messaggi descrivono la stessa analisi GOLD: sono due messaggi distinti, ma **non due setup indipendenti**. Score 100 e priorità catalizzatore 100/100 non sono validità operativa. Il messaggio #737 dichiara esplicitamente `NOT_EXECUTED`, assenza di quotazione futures fresca e livelli omessi.

## 2. SPUTNIK — nuova scansione #42498971172

Run: [SPUTNIK #42498971172](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42498971172)  
Job log: job `128787341086` — SUCCESS.  
Commit eseguito dalla scansione: `5780f8c83fbd30f526ffbede79d8799c7270743f`.

Tempi rilevati:
- run avviata: 16:15:37 UTC;
- processo SPUTNIK avviato: 16:15:41.809910 UTC;
- scan intelligence pubblica: 744 ms;
- notifica stage: 1.350 ms;
- run complessiva: 2.235 ms.

### Fonti e item pubblico

- SEC: HTTP 403, cooldown `retry_in=21600s`, filing recuperati: 0.
- White House RSS `https://www.whitehouse.gov/feed/`: HTTPError.
- Public intelligence scan: 2 finding/correlazioni; 1 nuovo evento pubblico individuale verificabile.
- Item [Trump's Truth #43525](https://www.trumpstruth.org/statuses/43525), pubblicato alle 13:49:32 UTC e rilevato alle 16:15:42.637185 UTC: ritardo **2h26m10.6s**.
- Item classificato `OTHER`, domini `SPACE` e `RATES_MACRO`, evidenza storica `NO_ANALOGUE`; nessun mapping a commodity, nessuna direzione, nessun prezzo o livello.
- La stessa scansione ha registrato una pagina TRUTH_ARCHIVE a livello di sito, senza permalink/data individuale. È stata trattata come evidenza di copertura, non come un secondo evento di mercato.

### Messaggi Telegram con ACK API

- #735: digest dell'item pubblico; API round-trip 413 ms.
- #736: GOLD, bias NEUTRAL, tecnica 5m UNAVAILABLE, `NO_DIRECTIONAL_NEWS`; API round-trip 377 ms.
- #737: GOLD, `NO_DIRECTION`, `NOT_EXECUTED`, score 100; NARWHAL reference `NOT_CONFIGURED`; future continuo front-month con scadenza esatta e indipendenza upstream non verificate; API round-trip 323 ms.

I log riportano `delivery confirmed` e i rispettivi message ID: questo prova l'ACK dell'API Telegram, non la visualizzazione sul dispositivo. Non ci sono entry, SL, TP, ATR o quotazioni utilizzabili per #736/#737.

### Handoff e persistenza

Nel runtime della scansione:
- `GAGARIN_CLOUD_API_URL` vuota;
- `GAGARIN_CLOUD_API_KEY` vuota;
- handoff SPUTNIK → GAGARIN esplicitamente disabilitato;
- `NARWHAL_API_KEY` vuota, quindi nessun riferimento prezzo Narwhal.

La scansione ha poi committato `sputnik_state.json` direttamente su `main`: commit [`71b4b22fe23b17cac782a9a3a9b44a4f1354a7cb`](https://github.com/andreameloni1984-sys/trump-trucker/commit/71b4b22fe23b17cac782a9a3a9b44a4f1354a7cb), con `updated_at=16:15:42.666484Z` e i nuovi event ID nella history. Questo conferma che il workflow di produzione continua a scrivere stato su `main`; la PR #144 per spostare la persistenza fuori da main è ancora aperta.

### Polling Telegram

[SPUTNIK Telegram Polling #42498116149](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42498116149): SUCCESS alle 16:05:42 UTC; il runner one-shot ha elaborato `Pending updates: 0`. Non è una scansione di mercato e non prova la consegna dei messaggi #735–#737.

## 3. GAGARIN — nuova scansione #42499039797

Run: [GAGARIN monitor #42499039797](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42499039797)  
Job log: job `128787549596` — SUCCESS.  
Main al momento del run: `444a23e5d183660ebc655f04c4c79ed1370101b6`.

Configurazione runtime verificata:
- `PAPER_TRADING_ONLY=1`;
- soglie stampate: probabilità 40, qualità 30, confidenza 35, RR 2.5;
- `MONITOR_INTERVAL_MINUTES=15`;
- `DATABASE_URL` vuota;
- `NARWHAL_API_KEY` vuota.

### Quotazioni e classificazioni

Il processo è partito alle 16:16:37.650727 UTC. Il log riporta 10 strumenti (8 commodity operative e 2 FX ausiliari):
Soia, Brent, Argento, WTI, Grano, EUR/USD, Mais, Oro, Rame, GBP/USD.

Tutti risultano `MARKET_CLOSED`. Età quote:
- YAHOO, commodity: da 152.198,7 a 161.802,8 secondi (circa **42h17m–44h57m**);
- BIQUOTE, EUR/USD e GBP/USD: circa 152.499–152.500 secondi (circa **42h22m**).

I log non espongono timestamp assoluto della quotazione, ticker provider risolto, prezzo di riferimento, mercato esatto o scadenza. I candidati sono bloccati da `LIVE_DATA_NOT_FRESH`, setup/trigger non validi o non confermati, direzione non valida e livelli mancanti. Entry, SL, TP1/2/3, ATR e RR non sono disponibili.

Riepilogo effettivo:
- Recorded entries: 0
- Updated open outcomes: 0
- New feedback signals: 0
- New additional live forecasts: 0
- `signals=0 open=0 closed=0`

Telegram #3722: `SEND CONFIRMED`, API round-trip 406 ms. Il corpo del WATCH pre-alert non è conservato; non è possibile attribuirlo a un singolo strumento o direzione. Il ledger registra quindi solo una notifica non attribuibile, NON_TRADE. ACK API non equivale a consegna al dispositivo.

### Journal, feedback e driver

Su main:
- `journal.csv`: 11 righe del 17 ottobre, tutte con esito “nessun segnale”.
- `paper_trade_log.csv`: vecchio WTI LONG del 8 ottobre, `LEGACY_IMPORT`; mancano provider, quote timestamp, ticker risolto, mercato/contratto di esecuzione e scadenza.
- `data/paper_open.json`: ticket WTI P0001 ancora marcato OPEN, senza prova di fill.
- `position.json`: vecchio Heating Oil LONG del 15 settembre, senza identità contrattuale/provenienza quota.
- `gagarin_feedback.csv`: assente nel tree di main.

Questi artefatti legacy non sono riconciliati con il monitor corrente e non sono conteggiati come fill. La persistenza condivisa non è dimostrata: `DATABASE_URL` è vuota nel job.

Lo snapshot driver resta quello letto alle 13:55:58 UTC: EIA crude e gas senza dati, WASDE wheat/corn/soybeans null; FRED dollar index datato 30 ottobre e real rate 10Y datato 5 novembre. È contesto macro parziale, non un segnale né una quotazione.

Il log runtime mostra Argento nell'universo e due FX ausiliari; non mostra Platino e Palladio. La PR #212 che propone il restringimento dell'universo è ancora draft/open, non integrata.

## 4. Difetto outcome GAGARIN confermato su main

File: [`engine/feedback.py`](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py), blob `41bec9bfab031c8dbf71121cd69d0e9b4c4f663f`.

Il codice corrente:
1. genera il fingerprint da symbol, direzione, timeframe, livelli e timestamp barra; non include identità completa di provider, mercato e scadenza;
2. associa le candele successive per symbol/timeframe, con fallback sul solo symbol se c'è un solo stato;
3. non verifica provider, ticker risolto, mercato e scadenza prima di usare le candele;
4. controlla SL prima dei target: se la stessa candela OHLC tocca SL e TP, registra `STOP`.

OHLC non permette di ricostruire l'ordine intrabar. In quel caso PRAVDA deve registrare `ESITO NON VERIFICABILE`, non STOP.

### PR già esistenti

- GAGARIN [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, non merged; head `295dba4b...`, base `c93906a2...`; GitHub indica mergeable ma `mergeable_state=unstable`. Non è in produzione. La correzione non è stata verificata su main.
- GAGARIN [PR #97](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/97): draft/open per i tocchi simultanei SL/TP.
- GAGARIN [PR #212](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/212): draft/open per l'universo richiesto.
- GAGARIN [PR #200](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/200) e [PR #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): draft/open per feedback e persistenza condivisa.
- GAGARIN [PR #190](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/190): OPEN per ACK Telegram del daily summary.

SPUTNIK:
- [PR #145](https://github.com/andreameloni1984-sys/trump-trucker/pull/145) quote provenance/Yahoo diagnostics: OPEN, non merged; GitHub al controllo restituisce `mergeable=false`, `mergeable_state=unknown`. I test precedentemente superati sono sul branch PR, non sulla produzione.
- [PR #147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147) indipendenza da GAGARIN: OPEN, non merged; handoff è ancora presente nel workflow ma disabilitato in runtime per URL/key vuoti.
- [PR #148](https://github.com/andreameloni1984-sys/trump-trucker/pull/148) anti-ripetizione, [PR #131](https://github.com/andreameloni1984-sys/trump-trucker/pull/131) White House RSS e [PR #144](https://github.com/andreameloni1984-sys/trump-trucker/pull/144) persistenza off-main: tutte OPEN, non integrate.

I difetti provider/contratto e l'ambiguità SL/TP sono già documentati nelle PR esistenti; non sono stati aggiunti commenti duplicati.

## 5. Cadenza GitHub Actions

Cron letti dai workflow:
- SPUTNIK collector: `2-59/5 * * * *`;
- SPUTNIK polling: `*/5 * * * *`;
- GAGARIN monitor: `*/15 * * * *`.

| Processo | Ultima run | Run precedente | Gap tra le due run | Gap al cut-off |
|---|---|---|---:|---:|
| SPUTNIK collector | 16:15:37 UTC | 09:31:31 UTC | 6h44m06s | 24m34s |
| SPUTNIK polling | 16:05:42 UTC | 09:16:25 UTC | 6h49m17s | 34m29s |
| GAGARIN monitor | 16:16:25 UTC | 09:29:58 UTC | 6h46m27s | 23m46s |

Le run sono SUCCESS, ma i gap osservati non rispettano la cadenza dichiarata. Al cut-off non risultava un'altra scansione successiva. Il fatto che il mercato fosse chiuso spiega i dati stale GAGARIN, non il mancato polling delle notizie SPUTNIK. La causa dei gap non è dimostrata e non viene attribuita a un filtro orario.

## 6. Esiti, limiti e fonti

Nessun nuovo segnale operativo con entry/SL/TP/ATR e identità contrattuale completa. Nessun fill. Nessuna candela successiva riferibile allo stesso identico provider/ticker/mercato/scadenza di un nuovo trade idoneo. Nessun nuovo SL/TP verificabile.

Non sono stati usati spot per valutare futures, continuous futures come sostituti di una scadenza, score come validità operativa o `NOT_EXECUTED` come trade. Nessun backtest o risultato è stato inventato.

Fonti consultate:
- GitHub Actions SPUTNIK #42498971172 e polling #42498116149; log job `128787341086` e `128784755699`.
- GitHub Actions GAGARIN #42499039797; log job `128787549596`.
- Commit SPUTNIK state [71b4b22](https://github.com/andreameloni1984-sys/trump-trucker/commit/71b4b22fe23b17cac782a9a3a9b44a4f1354a7cb).
- Item pubblico [Trump's Truth #43525](https://www.trumpstruth.org/statuses/43525); archive [Trump's Truth](https://www.trumpstruth.org/).
- Workflow `trump_tracker.yml`, `telegram-polling.yml`, GAGARIN `gagarin-monitor.yml`.
- GAGARIN `engine/feedback.py`, `journal.csv`, `paper_trade_log.csv`, `data/paper_open.json`, `position.json`, `data/driver_snapshot.json`.
- PR #145, #147, #148, #131, #144 SPUTNIK; PR #192, #97, #190, #200, #202, #212 GAGARIN.

## 7. Registrazione e prossimo controllo

- Ledger aggiornato con 4 righe nuove; 91 record, 91 firme uniche, 91 source ID unici, zero duplicati.
- Commit ledger: `1b886478f078f447f619e7a3474f41d8a4e0acf4`.
- Questo rapporto è un artefatto documentale PRAVDA separato; nessun codice dei bot è stato modificato.

Prossimo controllo:
1. verificare nuove run di produzione distinte da test, polling e driver refresh;
2. verificare se riprende la cadenza 5m/15m;
3. acquisire messaggi e log completi con timestamp generazione/invio;
4. richiedere identità esatta provider/ticker/mercato/scadenza e quote timestamp per ogni eventuale segnale;
5. valutare soltanto candele successive dello stesso identico contratto, con esito SL prima, TP prima oppure `ESITO NON VERIFICABILE`.

**Perimetro:** nessun codice, strategia, filtro, punteggio o rischio modificato; nessun merge/deploy, ordine reale, modifica ai secret o Render; nessun servizio a pagamento; nessun accesso a Trading212 dichiarato. Telegram: solo ACK API esplicitamente presenti nei log, nessuna consegna al dispositivo dichiarata. **PAPER ONLY.**
