# PRAVDA — Audit incrementale SPUTNIK / GAGARIN

**Cut-off:** 8 novembre 2026, 06:42:38 UTC (07:42:38 Europe/Rome)  
**Perimetro:** nuove GitHub Actions rispetto al controllo 06:08 UTC, log di produzione, ledger, journal/feedback, stato persistito e PR aperte. PAPER ONLY.

## Esito sintetico

Dall'ultimo audit non è comparsa alcuna nuova scansione di mercato su `main`. Gli ultimi collector restano SPUTNIK #42439632866 (02:42:14 UTC) e GAGARIN #42438806862 (02:30:28 UTC). I run SPUTNIK #42450417210 e #42450417214 delle 05:20 UTC sono test CI della PR #148, non scansioni di mercato.

Il ledger `reports/pravda-signal-ledger-2026-11-08.csv` è stato riletto e ricontato:
- 81 record: SPUTNIK 33, GAGARIN 48;
- 81 firme uniche e 81 source ID unici; 0 duplicati;
- 52 `NON_TRADE`, 29 `ESITO_NON_VERIFICABILE`;
- fill verificati 0; SL/TP verificati 0.

Nessun record nuovo è eleggibile per il ledger. Win rate e average R restano N/D: campione di trade con fill e contratto identificato = 0. I 29 esiti non verificabili non sono trade e non entrano nelle statistiche.

## 1. GitHub Actions — cadenza effettiva

### SPUTNIK
- Workflow main: `.github/workflows/trump_tracker.yml`, cron dichiarato `2-59/5 * * * *`.
- Ultimo collector: [#42439632866](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42439632866), schedule, avvio 02:41:59, completamento 02:42:14 UTC, SUCCESS, nessun artifact.
- Collector precedente: [#42426077974](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42426077974), avvio 7 novembre 23:37:18 UTC; intervallo fra gli avvii 3h04m41s.
- Al cut-off sono trascorse 4h00m24s dalla conclusione dell'ultimo collector.
- I test PR #42450417210 e #42450417214 sono SUCCESS, ma non sostituiscono il collector schedule.

### GAGARIN
- Workflow main: `.github/workflows/gagarin-monitor.yml`, cron dichiarato `*/15 * * * *`.
- Ultimo monitor: [#42438806862](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42438806862), schedule, avvio 02:30:08, completamento 02:30:28 UTC, SUCCESS, nessun artifact.
- Monitor precedente: [#42423479990](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42423479990), avvio 7 novembre 23:03:38 UTC; intervallo fra gli avvii 3h26m30s.
- Al cut-off sono trascorse 4h12m10s dalla conclusione dell'ultimo monitor.

**Difetto confermato:** SUCCESS descrive l'esito del job, non il rispetto della cadenza prevista. Entrambi i collector hanno intervalli effettivi di ore contro cron di 5 e 15 minuti. Non attribuisco la causa a un singolo fattore senza evidenza; gli eventi schedule risultano mancanti o ritardati nella cronologia disponibile.

## 2. SPUTNIK — run #42439632866

### Raccolta fonti
- SEC: HTTP 403, cooldown 21.600 secondi, `filings=0`.
- White House RSS: HTTPError.
- Scansione intelligence pubblica: `findings=0`.
- Nessun catalizzatore inoltrato a GAGARIN.
- Il workflow continua a passare al processo i riferimenti ai secret `GAGARIN_CLOUD_API_URL` e `GAGARIN_CLOUD_API_KEY`; la PR #147 che rimuove l'accoppiamento è ancora aperta. Nel run non è avvenuto alcun handoff perché non c'erano finding.

### Messaggi Telegram registrati
| ID | Generazione UTC | Strumento | Direzione/stato | Dati mancanti |
|---|---|---|---|---|
| #729 | 02:42:09.805695 | GOLD | NEUTRAL / WATCH | ticker risolto, provider, timestamp quote, mercato/scadenza, entry, SL, TP, ATR |
| #730 | 02:42:09.806747 | GOLD | NEUTRAL / NOT_EXECUTED | ticker risolto, provider, timestamp quote, scadenza esatta, entry, SL, TP, ATR |

L'API Telegram ha confermato i message ID #729 e #730; i round-trip riportati sono rispettivamente 414 ms e 392 ms. Tuttavia i timestamp di generazione e conferma nel log differiscono di circa 1 ms: non sono coerenti con quei round-trip e non consentono di ricostruire una latenza end-to-end affidabile. API acceptance non equivale a prova di visualizzazione sul dispositivo.

#730 descrive un front-month continuo con scadenza esatta non verificata; NARWHAL risulta NOT_CONFIGURED. Il punteggio/priorità 100 non è validità operativa. #729 e #730 sono due messaggi sulla stessa analisi GOLD, non due setup distinti. Il message_id #731 appare nel test di regressione del job e va escluso dai messaggi di produzione.

Nessun livello operativo o candela successiva dello stesso contratto disponibile: nessun outcome valutabile.

## 3. GAGARIN — run #42438806862

### Mercato e quotazioni
Il log mostra otto commodity (Soia, Grano, Brent, WTI, Oro, Argento, Mais, Rame) e due coppie FX ausiliarie (EUR/USD, GBP/USD). Tutti i mercati sono `MARKET_CLOSED` e tutte le quotazioni sono stale:
- Soia, Grano, Mais: Yahoo, circa 112.524 secondi (31h15m);
- Brent, WTI, Oro, Argento, Rame: Yahoo, circa 102.923 secondi (28h35m);
- EUR/USD e GBP/USD: BiQuote, circa 102.924–102.925 secondi.

### Unico candidato direzionale
- Record: `run:42438806862/classification:Argento`.
- Generato: 02:30:25.6902087 UTC.
- Strumento logico: Argento / XAG/USD; ticker provider risolto non esposto.
- Provider: Yahoo; età quote 102.922,9 secondi; timestamp esatto della quotazione non esposto.
- Mercato e scadenza: non registrati; nessun prezzo di riferimento.
- Direzione: LONG; probabilità 59, qualità 49,5, confidence 32.
- Stato: `PAPER_WATCH`, bloccato da mercato chiuso, dato stale, trigger non confermato, mismatch direzionale, confidence e confluence.
- Entry, SL, TP e ATR: assenti.

È un candidato WATCH bloccato, non un segnale operativo e non un trade. Non si può valutare un esito.

### Telegram
Il pre-alert #3718 è stato accettato dall'API con round-trip dichiarato di 560 ms. Il corpo del messaggio non è conservato: strumento e direzione non sono attribuibili. Il timestamp registrato come invio è quello della conferma API, non il momento esatto della richiesta. Nessuna prova di consegna sul dispositivo.

Riepilogo del run: `signals=0 open=0 closed=0`; nessun feedback nuovo. Nessun artifact Actions.

## 4. Journal, feedback e stato GAGARIN

- `journal.csv`: 11 righe dati, tutte del 17 ottobre e tutte senza segnale.
- `paper_trade_log.csv`: un solo ticket legacy WTI P0001, LONG, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55. Mancano signal ID, fill, provider, ticker quotazione, timestamp, mercato e scadenza.
- `data/paper_open.json`: P0001 è marcato OPEN, mentre il monitor #42438806862 riporta `open=0`. È una discrepanza di stato legacy/runtime, non prova di esecuzione.
- `position.json`: vecchia posizione Heating Oil HO/USD del 15 settembre; identità completa del contratto e prova di fill assenti.
- `commodities_prediction_log.json`: 981 record, 945 PENDING e 36 NEUTRALE; ultimo record 15 settembre 2026. LONG/COMPRA ORA e score non provano esecuzione.
- `gagarin_feedback.csv`: non trovato (404).
- Nessuna candela successiva è stata associata a P0001 o alla posizione Heating Oil con corrispondenza certa di provider, ticker e contratto. Entrambi restano `ESITO_NON_VERIFICABILE`.

## 5. Universo effettivo e correzioni già aperte

Il run main non corrisponde al paniere scelto: include Argento, non mostra Platino e Palladio, e mantiene EUR/USD e GBP/USD come righe ausiliarie. Il paniere richiesto è Oro, Rame, Platino, Palladio, WTI, Brent, Grano, Mais e Soia, con Argento escluso.

### SPUTNIK
- [PR #148 — evitare raccomandazioni ripetute senza nuovo catalizzatore](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN, non draft, mergeable; test CI #42450417210 e #42450417214 SUCCESS. Non integrata su main.
- [PR #144 — persistenza stato fuori da main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN, non integrata.
- [PR #145 — provenienza quote e diagnostica errori Yahoo](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN; GitHub riporta mergeable=false.
- [PR #147 — rimozione handoff GAGARIN da SPUTNIK](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN, non integrata.

### GAGARIN
- [PR #181 — provenienza esatta delle quotazioni nel log](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/181): OPEN.
- [PR #192 — identità esatta contratto e gestione candele ambigue SL/TP](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN.
- [PR #219 — rimozione EUR/USD e GBP/USD dall'universo](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219): OPEN.
- [PR #223 — scansione M5 separata di sette strumenti, Argento escluso](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): OPEN, draft; osservazione soltanto, senza livelli, journal o Telegram. Non include Platino/Palladio e non sostituisce il monitor completo.
- [PR #225 — offset del cron GAGARIN](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225): OPEN, draft; il cron main resta `*/15`.
- [PR #235 — persistenza journal CFD Trading 212](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/235): OPEN, draft, specifica al ramo CFD Trading 212; non risolve il journal futures del monitor esaminato.

## 6. Statistiche, limiti e prossimo controllo

**Esiti verificabili nel campione:** 0 fill, 0 stop verificati, 0 target verificati, 0 trade con outcome ricostruibile. Win rate e average R: N/D. Nessun backtest o risultato sintetico è stato prodotto.

**Difetti dimostrati da mantenere aperti:**
1. Cadenza reale dei collector non conforme ai cron dichiarati.
2. Fonti SEC e White House non utilizzabili nel run SPUTNIK; nessun finding direzionale.
3. Quotazioni GAGARIN tutte stale nel run domenicale.
4. Ticker risolto, timestamp quote, mercato e scadenza non esposti per il candidato Argento.
5. Universo main difforme dal paniere scelto.
6. Stato legacy P0001 OPEN in conflitto con `open=0` runtime; nessuna prova di fill.
7. Corpo del pre-alert #3718 non conservato e non attribuibile.
8. PR per provenienza, contratto, universo e scheduler ancora aperte.

**Prossimo controllo:** interrogare solo le successive run schedule di produzione su main, distinguendole da CI/PR, e acquisire i log integrali. Aggiungere al ledger solo nuove firme/source ID. Per ogni direzione richiedere provider, ticker effettivo, mercato/scadenza, timestamp quote, entry/SL/TP/ATR e prova del messaggio; valutare SL/TP soltanto con candele successive dello stesso identico contratto, rispettando la sequenza temporale. Se manca un elemento essenziale, lasciare `ESITO_NON_VERIFICABILE`.

**Modifiche di questo controllo:** aggiunto solo questo rapporto incrementale. Ledger invariato perché non sono emersi nuovi record eleggibili. Nessuna modifica a codice, strategia, filtri, punteggi, rischio, segreti o Render; nessun merge, deploy, ordine reale o accesso a Trading212.
