# PRAVDA — audit indipendente SPUTNIK / GAGARIN
**Cut-off operativo: 2026-11-08 14:19:52 UTC (15:19:52 Europe/Rome)**

## Sintesi

Controllati i due repository, le GitHub Actions recenti, i log completi dei job rilevanti, il ledger PRAVDA, il codice di feedback GAGARIN, il nuovo snapshot dei driver e le PR aperte.

**Nessun nuovo segnale operativo verificabile e nessun nuovo trade.** Non è stata aggiunta alcuna riga al ledger: le novità osservate sono test di PR, un aggiornamento del solo snapshot macro GAGARIN e una notifica riepilogativa già registrata nel ledger precedente. Non sono candele/prezzi di esecuzione e non possono essere valutate come segnali.

## 1. Ledger — verifica d'integrità

File: [pravda-signal-ledger-2026-11-08.csv](pravda-signal-ledger-2026-11-08.csv)

- SHA del blob ledger: `27b5ff7b1e09c9f080622058237a03cad098907b`
- Record: **87**
- SPUTNIK: **37**
- GAGARIN: **50**
- Firme uniche: **87**
- Source ID unici: **87**
- Duplicati firma: **0**
- Duplicati source ID: **0**
- `NON_TRADE`: **58**
- `ESITO_NON_VERIFICABILE`: **29**
- Fill verificati: **0**
- SL verificati: **0**
- TP verificati: **0**
- Win rate / average R / total R: **N/D**

Il ledger è stato riletto e analizzato riga per riga. L'ultima riga resta la notifica GAGARIN Daily Summary `run:42484703932/daily_summary/http_response`, già registrata. Nessuna riga nuova: i test PR e il refresh dei driver non sono segnali.

## 2. SPUTNIK — produzione ferma, miglioramento diagnostico solo su PR

### Ultime esecuzioni

- [Collector SPUTNIK #42467543117](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42467543117): avvio 09:31:31 UTC, conclusione 09:31:41 UTC, SUCCESS. È ancora l'ultima scansione di produzione trovata.
- [Telegram Polling #42466478249](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42466478249): avvio 09:16:25 UTC, SUCCESS, pending updates=0. Il collector imposta `SPUTNIK_TELEGRAM_POLLING=0` e dichiara un listener dedicato attivo; non sono disponibili i log del listener esterno, quindi il suo stato attuale non è certificato.
- [Daily Summary #42480644139](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42480644139): avvio 12:31:18 UTC, SUCCESS; Telegram API conferma message_id=734. È una notifica riepilogativa, non una scansione. Lo stato caricato aveva transactions=0; il testo esatto non è conservato nel log.

### Contenuto dell'ultima scansione

Il log del collector conferma:
- SEC: HTTP 403, cooldown 21.600 secondi, zero filing raccolti.
- White House RSS `https://www.whitehouse.gov/feed/`: HTTPError.
- Truth Archive item 43524: pubblicato alle 03:53:01 UTC, rilevato alle 09:31:37.313495 UTC; ritardo **5h38m36s**.
- Messaggio Telegram #731: digest notizia, non segnale.
- #732: GOLD, NEUTRAL, tecnica 5m UNAVAILABLE, NO_DIRECTION; nessun prezzo, entry, SL, TP o ATR.
- #733: GOLD, NOT_EXECUTED, score 100; il titolo lo chiama CFD ma il corpo dichiara future continuo front-month, scadenza esatta non verificata. Nessuna quotazione fresca o livello operativo.

#732 e #733 sono due messaggi della stessa analisi, non due setup. Gli ACK Telegram #731–#733 dimostrano l'accettazione API, non la visualizzazione sul dispositivo.

### Nuova PR diagnostica #145

[PR #145 — quote provenance e diagnostica Yahoo](https://github.com/andreameloni1984-sys/trump-trucker/pull/145) è **OPEN, non merged**. Confronto attuale: 1 commit avanti e 0 indietro da main; modifica soltanto `sputnik_cfd.py` e `tests/test_sputnik_cfd.py`.

Sul nuovo head `908feb56afd5cd7b45509c605da21add6e3d3c61`:
- [Ranking tests #42489236939](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42489236939): **186 test SUCCESS**.
- [Telegram menu/CFD tests #42489236937](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42489236937): **68 test SUCCESS**.
- Totale: **254 test SUCCESS**, inclusi i test HTTP 403 e URLError.

La PR aggiunge il log della causa degli errori Yahoo e rende visibili nel messaggio provider, ticker risolto, mercato, descrizione contratto, timestamp/età e bid/ask già disponibili nel segnale. Non modifica bias, livelli, score, filtri o rischio. È un miglioramento concreto, ma non è ancora in produzione perché la PR è aperta.

## 3. GAGARIN — refresh macro riuscito, monitor prezzi ancora assente

### Ultimo monitor di produzione

[Monitor GAGARIN #42467422750](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42467422750): avvio 09:29:58 UTC, conclusione 09:30:17 UTC, SUCCESS. Nessun monitor successivo compare nella lista aggiornata delle run.

Il log mostra:
- `DATABASE_URL` vuota nel job;
- 8 commodity operative e EUR/USD/GBP/USD ausiliari;
- dieci voci stampate come `MARKET_CLOSED`;
- YAHOO stale: **127.811–137.416 secondi** (circa 35h30m–38h10m);
- BIQUOTE stale per EUR/USD e GBP/USD: circa 128.113 secondi;
- ticker provider risolti, timestamp assoluti delle quote, mercato e scadenze non esposti.

Strumenti nel log: Soia, Brent, Argento, WTI, Grano, Mais, Oro, Rame, EUR/USD e GBP/USD. Il paniere operativo stampato mantiene Argento e non mostra Platino/Palladio; le coppie FX restano ausiliarie. Questo non coincide con l'ultima delimitazione richiesta dall'utente (Argento escluso, FX non operativi, Platino/Palladio da includere).

Esito:
- Recorded entries: 0
- Updated open outcomes: 0
- New feedback signals: 0
- `signals=0 open=0 closed=0`

Il messaggio WATCH #3719 è confermato dal log API (527 ms), ma il corpo non è conservato: nessuna attribuzione a strumento o direzione. Non è un trade.

### Nuovo refresh dei driver macro

[FETCH COMMODITY DRIVERS #42487274361](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42487274361): avvio 13:55:43 UTC, conclusione 13:56:02 UTC, SUCCESS. Ha aggiornato `data/driver_snapshot.json` con commit main `444a23e5d183660ebc655f04c4c79ed1370101b6`.

L'aggiornamento è reale ma **non è una quotazione di mercato né una scansione segnali**:
- EIA crude stocks: no_data.
- EIA natural-gas storage: no_data.
- USDA wheat/corn/soybean balances: null.
- FRED dollar index: 121.6656, data 2026-10-30.
- FRED 10y real rate: 2.60, data 2026-11-05.
- Variabili inventories, curve, supply shock, refined products, systematic flow, weather, harvest, season e hedging pressure: UNKNOWN.
- Dollar e real rates: DOWN.

Nel job EIA_API_KEY e FRED_API_KEY erano vuote; i dati FRED disponibili provengono dal CSV pubblico. Nessun valore mancante è stato inventato. Questo refresh migliora la datazione del file macro, ma non risolve l'assenza di quotazioni fresche del monitor.

### Daily Summary GAGARIN

[Daily Summary #42484703932](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42484703932): SUCCESS, ma il workflow stampa `Summary sent` senza leggere/validare il JSON Bot API e senza conservare `message_id`. Non è prova di ACK Telegram. Il workflow non passa DATABASE_URL e il feedback locale non è persistente/configurato: il riepilogo non è dimostrato basato su uno storico condiviso.

## 4. Outcome engine GAGARIN — difetto ancora in main

Il file `engine/feedback.py` sul main GAGARIN (`444a23e5d183660ebc655f04c4c79ed1370101b6`) continua a:
- identificare il segnale principalmente con symbol/direction/timeframe/livelli/bar timestamp;
- abbinare le candele successive per symbol e timeframe, senza identità completa provider/ticker/mercato/scadenza;
- classificare STOP quando una candela OHLC tocca contemporaneamente SL e TP, perché il controllo SL precede quello dei target.

L'ordine intrabar non è ricostruibile da una singola candela OHLC: il caso deve restare `ESITO NON VERIFICABILE`.

[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) resta OPEN e non mergeable. Il confronto aggiornato con main (`444a23e`) è **6 commit ahead / 5 behind**. I test verdi del branch sono vecchi e non attestano l'integrazione. Rimane valido il rilievo già scritto nel commento [PRAVDA #6706619879](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6706619879): il guard del branch non confronta esplicitamente il provider tra segnale e candela successiva. Nessun commento duplicato aggiunto.

Altre PR pertinenti ancora aperte:
- [#200](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/200) e [#202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): riepilogo/persistenza feedback;
- [#212](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/212): universo commodity;
- [#219](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219) e [#221](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): rimozione route FX;
- [#223](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): scansione M5 isolata;
- [#225](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225): offset cron;
- [#237](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/237): draft impilata sulla branch #236, non su main.

## 5. Cadenza osservata al cut-off

| Processo | Cron dichiarato | Ultima run | Gap al cut-off |
|---|---:|---:|---:|
| SPUTNIK collector | ogni 5 min | 09:31:31 UTC | **4h48m21s** |
| SPUTNIK GitHub polling | ogni 5 min | 09:16:25 UTC | **5h03m27s** |
| GAGARIN monitor | ogni 15 min | 09:29:58 UTC | **4h49m54s** |

Il refresh macro GAGARIN delle 13:55, i daily summary e i test PR non sono scansioni di mercato e non azzerano questi gap. La causa della mancata cadenza non è dimostrata; non viene attribuita a un filtro orario senza evidenza.

## 6. Esiti, fonti e limiti

Non sono disponibili nuovi segnali con entry/fill verificato e identità completa di provider, ticker, mercato e contratto seguiti da candele dello stesso identico contratto. Nessun nuovo SL/TP può essere classificato. Non è stato usato spot per valutare futures né un front-month continuo come sostituto di una scadenza specifica.

Fonti consultate:
- GitHub Actions SPUTNIK #42467543117, #42466478249, #42480644139, #42489236939, #42489236937;
- GitHub Actions GAGARIN #42467422750, #42484703932, #42487274361;
- log completi dei relativi job;
- ledger PRAVDA e report precedente;
- `data/driver_snapshot.json`, `engine/feedback.py`, workflow GAGARIN monitor/daily summary e workflow SPUTNIK collector;
- metadati, diff, CI e discussioni PR #145, #192, #237.

## 7. Registrazione e prossimo controllo

- Ledger: **nessuna modifica**; 87 righe, 87 firme uniche, 87 source ID unici, zero duplicati.
- Nuovo rapporto: questo file, solo documentazione di audit.
- Prossimo controllo: verificare nuove run di produzione distinte da test, daily summary e fetch macro; controllare la ripresa della cadenza; ottenere quote fresche con provider/ticker/mercato/scadenza e timestamp; registrare un segnale soltanto se esiste un record identificabile; valutare SL prima, TP prima o `ESITO NON VERIFICABILE` usando candele successive dello stesso identico contratto.

**Perimetro:** nessun codice, strategia, filtro, punteggio o rischio modificato; nessun merge/deploy, ordine reale, modifica a secret o Render; nessun servizio a pagamento; nessun accesso Trading212 dichiarato. Telegram: ACK API solo dove esplicitamente registrato, nessuna consegna al dispositivo dichiarata. **PAPER ONLY.**
