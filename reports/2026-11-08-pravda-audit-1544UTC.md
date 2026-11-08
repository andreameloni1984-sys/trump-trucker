# PRAVDA — audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-08 15:44:34 UTC (16:44:34 Europe/Rome)**

## Sintesi esecutiva

Controllati entrambi i repository su `main`, le ultime GitHub Actions disponibili, i log dei job di produzione, i file di journal e feedback, lo snapshot dei driver GAGARIN, il motore di outcome e le PR pertinenti.

**Non è emerso alcun nuovo segnale operativo verificabile né alcun trade.** Le ultime attività sono test PR, un riepilogo giornaliero e un aggiornamento dei driver macro: nessuna di queste attività è una nuova scansione di mercato o un'esecuzione.

Nessun nuovo record è stato aggiunto al ledger: tutti gli eventi/messaggi attribuibili dell'ultima scansione SPUTNIK e GAGARIN erano già registrati. Il ledger è stato riletto e controllato senza modificarlo.

Repository osservati:
- SPUTNIK main: `045fe3113648478b0be8000212a548f6814e2405`
- GAGARIN main: `444a23e5d183660ebc655f04c4c79ed1370101b6`
- Ledger PRAVDA: blob SHA `27b5ff7b1e09c9f080622058237a03cad098907b`

## 1. Integrità del ledger

File: [pravda-signal-ledger-2026-11-08.csv](pravda-signal-ledger-2026-11-08.csv)

| Indicatore | Conteggio |
|---|---:|
| Record | 87 |
| SPUTNIK | 37 |
| GAGARIN | 50 |
| Firme uniche | 87 |
| Source ID unici | 87 |
| Duplicati firma | 0 |
| Duplicati source ID | 0 |
| `NON_TRADE` | 58 |
| `ESITO_NON_VERIFICABILE` | 29 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |

Win rate, average R e total R: **N/D**. I 29 record `ESITO_NON_VERIFICABILE` sono record storici senza esito dimostrabile, non 29 trade. I 58 `NON_TRADE` non entrano in alcuna statistica di performance.

L'ultima riga del ledger resta la risposta HTTP non validata del Daily Summary GAGARIN `run:42484703932/daily_summary/http_response`. Non è stata aggiunta una seconda riga per lo stesso evento.

## 2. SPUTNIK

### Ultima scansione di produzione

[SPUTNIK run #42467543117](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42467543117)
- GitHub run avviata: 09:31:31 UTC; processo SPUTNIK avviato nel log alle 09:31:36.449 UTC.
- Conclusione: SUCCESS.
- Ultimo polling GitHub Actions: [#42466478249](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42466478249), 09:16:25 UTC, SUCCESS.
- Non risultano scansioni collector successive nella lista delle ultime 30 run consultata fino al cut-off.

Log della scansione:
- SEC: HTTP 403; cooldown registrato di 21.600 secondi; zero filing.
- White House RSS `https://www.whitehouse.gov/feed/`: HTTPError.
- Scansione intelligence pubblica: 2 correlazioni; il messaggio notizie mostra un evento pubblico.
- Item Truth Archive `43524`: pubblicato alle 03:53:01 UTC, rilevato nel log alle 09:31:37.313 UTC. Ritardo: circa **5h38m36s**.
- Telegram #731: digest dell'item, non segnale.
- Telegram #732: GOLD, bias NEUTRAL, direzione tecnica 5m UNAVAILABLE, NO_DIRECTION; nessun prezzo di riferimento o livello.
- Telegram #733: GOLD, NO_DIRECTION, `NOT_EXECUTED`, score 100; nessuna quotazione futures fresca, entry, SL, TP o ATR.

#732 e #733 sono due messaggi della stessa analisi GOLD, non due setup indipendenti. Il messaggio #733 si intitola “ANALISI CFD”, ma il suo corpo dichiara un future continuo front-month e avverte che la scadenza esatta e l'indipendenza upstream non sono verificate. Non è quindi attribuibile a un CFD né a un contratto future con scadenza identificata. Il punteggio 100 non costituisce validità operativa.

Gli ACK API per i messaggi #731–#733 sono presenti nei log. Provano l'accettazione da parte dell'API Telegram, non la consegna o visualizzazione sul dispositivo.

### Riepilogo SPUTNIK

[Daily Summary #42480644139](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42480644139): SUCCESS, avvio 12:31:18 UTC. Il log conferma Telegram message_id=734 alle 12:31:25.243 UTC. È una notifica riepilogativa, non una scansione. Lo stato letto aveva zero transazioni; il corpo completo non è conservato nel log. Il record è già presente nel ledger.

### PR diagnostica SPUTNIK #145

[PR #145 — quote provenance e diagnostica Yahoo](https://github.com/andreameloni1984-sys/trump-trucker/pull/145):
- OPEN, non merged, non deployata.
- Head: `908feb56afd5cd7b45509c605da21add6e3d3c61`.
- GitHub la indica mergeable, stato `clean`.
- Nuove run PR del 8 novembre alle 14:19:28 UTC: [ranking tests #42489236939](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42489236939) SUCCESS e [Telegram/CFD tests #42489236937](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42489236937) SUCCESS. I log della PR riportano rispettivamente 186 e 68 test, 254 complessivi.

La patch aggiunge diagnostica per HTTPError/URLError e mostra nel messaggio la provenienza della quotazione già disponibile (provider, ticker, mercato, descrizione contratto, timestamp/età, bid/ask). Non cambia strategia, bias, livelli, filtri o rischio. È una correzione solo sul branch: non è ancora in produzione.

## 3. GAGARIN

### Ultimo monitor di produzione

[GAGARIN monitor #42467422750](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42467422750):
- Avvio: 09:29:58 UTC; conclusione 09:30:17 UTC.
- SUCCESS.
- Nessun monitor di produzione successivo compare nella lista delle ultime 30 run consultata fino al cut-off.

Il log mostra 10 strumenti: 8 commodity operative e 2 FX ausiliari. Tutti sono `MARKET_CLOSED`. Le età delle quote sono comprese fra **127.811,4 e 137.416,2 secondi** (circa 35h30m–38h10m):
- YAHOO: Soia, Brent, Argento, WTI, Grano, Mais, Oro e Rame;
- BIQUOTE: EUR/USD e GBP/USD.

Per tutti i candidati il log riporta blocchi per dati non freschi, setup/trigger non validi o non confermati, livelli mancanti e mancata confluenza. Risultato effettivo:
- Recorded entries: 0
- Updated open outcomes: 0
- New feedback signals: 0
- New additional live forecasts: 0
- `signals=0 open=0 closed=0`

Telegram #3719 è stato accettato dall'API con round-trip 527 ms, ma il corpo del messaggio non è conservato: non sono attribuibili strumento, ticker, direzione o livelli. Non è un trade.

Il workflow espone `DATABASE_URL` come secret, ma il valore risulta vuoto nel job. Il commento nel workflow dichiara che i journal PAPER non devono essere committati nel repository pubblico e che la persistenza resta disabilitata fino a quando lo storage privato D1 non sarà distribuito e verificato.

### Journal e feedback su main

File rilevati:
- `journal.csv`: 11 righe del 17 ottobre, tutte con “nessun segnale”.
- `paper_trade_log.csv`: una vecchia riga WTI LONG del 8 ottobre, `LEGACY_IMPORT`, con entry/SL/TP ma senza provider, timestamp della quotazione, ticker risolto, mercato/contratto di esecuzione o scadenza.
- `data/paper_open.json`: ticket WTI P0001 con stato OPEN, ma senza prova di fill o provenienza della quotazione.
- `position.json`: vecchia posizione Heating Oil LONG del 15 settembre, senza identità contrattuale e provenienza della quota.
- `gagarin_feedback.csv`: assente su main.

Questi artefatti legacy non sono riconciliati con il monitor corrente e non vengono contati come fill o operazioni verificate.

### Daily Summary GAGARIN

[Daily Summary #42484703932](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42484703932): SUCCESS, avvio 13:23:05 UTC. Lo script stampa “Summary sent” dopo il ritorno HTTP, ma non legge né valida il JSON Telegram (`ok=true` e `result.message_id`); non conserva un message ID. Non è quindi prova di ACK Telegram. Il workflow non passa `DATABASE_URL`; il feedback locale non è disponibile su main.

[PR #190 — Telegram API acknowledgement](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/190) è OPEN, non merged.

### Refresh dei driver macro

[FETCH DRIVERS #42487274361](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42487274361): SUCCESS, avvio 13:55:43 UTC. Lo snapshot `data/driver_snapshot.json` riporta `read_at=13:55:58Z`.

Dati contenuti:
- EIA crude stocks: `no_data`.
- EIA natural-gas storage: `no_data`.
- USDA wheat/corn/soybean balances: null.
- FRED dollar index: 121.6656, data 30 ottobre 2026.
- FRED 10-year real rate: 2,60, data 5 novembre 2026.
- Dollar e real rates: DOWN; inventories, curve, supply shock, refined products, systematic flow, weather, harvest, season e hedging pressure: UNKNOWN.
- EIA_API_KEY e FRED_API_KEY risultano vuote nel job.

È un aggiornamento macro parziale, non una scansione prezzi o un segnale.

## 4. Difetto dimostrato nel motore outcome GAGARIN

Su main, `engine/feedback.py`:
1. La firma del record usa symbol, direzione, timeframe, livelli e timestamp della barra; non include l'identità completa del mercato/contratto.
2. L'associazione delle candele successive usa symbol e timeframe, con fallback sul solo symbol se esiste un unico stato.
3. Non viene verificato provider, ticker risolto, mercato e scadenza prima di usare le candele.
4. Se una stessa candela OHLC tocca SL e uno o più TP, il codice controlla prima SL e registra `STOP`. OHLC non consente di ricostruire l'ordine intrabar: l'esito deve essere `ESITO NON VERIFICABILE`.

### PR #192

[PR #192 — identità contratto e outcome ambigui](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192):
- OPEN, non merged; GitHub indica `mergeable=true`, `mergeable_state=unstable`.
- Head: `295dba4b074e564a4c11aa3fca136a8e4360672c`.
- Sei run CI sul commit head risultano SUCCESS, ma risalgono al 5 novembre 2026 alle 06:34 UTC; non sono una verifica recente dopo le successive modifiche a main.

La patch del branch aggiunge ticker/mercato/contratto all'identità, richiede un'identità esplicita per futures e tratta il doppio touch SL/TP nella stessa candela come `ESITO NON VERIFICABILE`. **Resta una lacuna dimostrabile:** il provider è incluso nel fingerprint del segnale, ma `_market_contract_match()` non confronta `quote_provider` della riga con il provider della candela/stato corrente. Il branch quindi non soddisfa ancora integralmente il requisito PRAVDA di stesso provider. Il difetto è già stato segnalato nella discussione PR #192; nessun commento duplicato aggiunto.

Altre PR pertinenti, tutte ancora aperte e non integrate:
- [#200](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/200) e [#202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): riepilogo e persistenza feedback;
- [#212](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/212): universo di otto commodity;
- [#219](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219) e [#221](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): rimozione route FX;
- [#225](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225): offset cron monitor;
- [#237](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/237): draft impilata sulla #236, catalogo Trading 212; non prova accesso a feed o conto Trading 212.

L'universo stampato nell'ultimo monitor resta composto da otto commodity che includono Argento, più EUR/USD e GBP/USD ausiliari; non coincide con la delimitazione richiesta (Argento escluso, FX non operativi, Platino/Palladio da includere).

## 5. Cadenza osservata al cut-off

Cut-off: 15:44:34 UTC.

| Processo | Cron nel workflow | Ultima run | Gap al cut-off |
|---|---|---|---:|
| SPUTNIK collector | `2-59/5 * * * *` | 09:31:31 UTC | **6h13m03s** |
| SPUTNIK Telegram polling | `*/5 * * * *` | 09:16:25 UTC | **6h28m09s** |
| GAGARIN monitor | `*/15 * * * *` | 09:29:58 UTC | **6h14m36s** |
| GAGARIN driver refresh | `0 7 * * *` | 13:55:43 UTC | **6h55m43s** |

I daily summary sono partiti alle 12:31:18 UTC (SPUTNIK, cron 06:00: ritardo 6h31m18s) e 13:23:05 UTC (GAGARIN, cron 06:15: ritardo 7h08m05s). I test PR, i daily summary e il fetch dei driver non sono scansioni di mercato e non azzerano i gap dei collector/monitor. La causa dei ritardi non è dimostrata e non viene attribuita a un filtro orario senza prova.

## 6. Esiti e lacune

Nessun nuovo segnale con identità completa e livelli verificabili. Nessun fill dimostrato. Non sono state trovate candele successive riferibili allo stesso provider, ticker, mercato e contratto di un segnale operativo idoneo; pertanto nessun nuovo SL/TP può essere classificato.

Non sono stati usati spot per valutare futures, contratti continui come sostituti di scadenze esatte, score come validità operativa o `NOT_EXECUTED` come trade. Nessun backtest o risultato è stato inventato.

Fonti consultate:
- GitHub Actions SPUTNIK #42467543117, #42466478249, #42480644139, #42489236939, #42489236937;
- GitHub Actions GAGARIN #42467422750, #42484703932, #42487274361;
- log completi dei job di produzione e driver;
- ledger PRAVDA e report precedente;
- `trump_tracker.yml`, `telegram-polling.yml`, SPUTNIK `daily-summary.yml`;
- GAGARIN `gagarin-monitor.yml`, `daily-summary.yml`, `fetch-drivers.yml`;
- `engine/feedback.py`, `journal.csv`, `paper_trade_log.csv`, `position.json`, `data/paper_open.json`, `data/driver_snapshot.json`;
- metadati e patch PR #145, #190, #192, #200, #202, #212, #219, #221, #225 e #237.

## 7. Registrazione e prossimo controllo

- Ledger: invariato, 87 record, 87 firme uniche, 87 source ID unici, zero duplicati.
- Questo rapporto è un nuovo artefatto documentale PRAVDA; non modifica il codice dei bot.
- Prossimo controllo: verificare nuove run di produzione distinte da test/daily summary/driver fetch; controllare la ripresa della cadenza; acquisire segnali solo con provider, ticker, mercato, scadenza, quote timestamp, entry, SL, TP e ATR; valutare esclusivamente candele successive dello stesso identico contratto con esito SL prima, TP prima o `ESITO NON VERIFICABILE`.

**Perimetro:** nessun codice, strategia, filtro, punteggio o rischio modificato; nessun merge/deploy, ordine reale, modifica a secret o Render; nessun servizio a pagamento; nessun accesso a Trading212 dichiarato. Telegram: solo gli ACK API esplicitamente presenti nei log, nessuna consegna al dispositivo dichiarata. **PAPER ONLY.**
