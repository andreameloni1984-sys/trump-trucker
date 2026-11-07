# PRAVDA — Audit SPUTNIK / GAGARIN
**Data controllo:** 7 novembre 2026, 23:06 UTC (8 novembre, 00:06 CET)  
**Ambito:** sola verifica; PAPER ONLY. Nessuna modifica a codice, strategia, filtri, punteggi o rischio.

## Esito sintetico
GAGARIN ha completato una scansione alle 23:03:58 UTC. SPUTNIK non ha una scansione di mercato successiva alle 20:07:24 UTC: alle 23:00:21 UTC è riuscito soltanto il workflow di polling Telegram, che ha trovato zero aggiornamenti pendenti. Polling e monitor di mercato non sono intercambiabili.

Non risultano trade con fill verificato né outcome SL/TP verificabili in questo controllo. Le notifiche Telegram sono accettazioni API, non prova di visualizzazione sul dispositivo.

## Storico PRAVDA
Ledger riletto, firme ricalcolate e cinque osservazioni nuove aggiunte, dopo aver controllato che non fossero già presenti:
- SPUTNIK: messaggi Telegram #723, #724 e #725 del run [#42409488950](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42409488950).
- GAGARIN: candidato Argento LONG in stato PAPER_WATCH e board Telegram #3717 del run [#42423479990](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42423479990).

**Conteggi dopo rilettura del file salvato:**
- Record: 66
- Firme uniche: 66
- Duplicati: 0
- Per bot: {"GAGARIN":46,"SPUTNIK":20}
- Per outcome: {"ESITO_NON_VERIFICABILE":29,"NON_TRADE":37}
- Fill verificati: 0
- SL/TP verificati: 0
- Win rate e average R: N/D (nessun campione con fill e contratto verificati)

Le notifiche WATCH/NO_DIRECTION sono classificate NON_TRADE, non come operazioni.

## SPUTNIK
Run di mercato più recente trovato tra le Actions recenti: [#42409488950](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42409488950), 7 novembre 20:07:13–20:07:24 UTC, conclusione SUCCESS, commit eseguito `96e34c290993820e4623332f17087c2258728b1c`. Job `sputnik` SUCCESS; nessun artifact Actions.

Risultato del log:
- SEC: HTTP 403, cooldown 21.600 secondi; 0 filing.
- White House RSS: HTTPError.
- Intelligence pubblica: 3 finding (due item RSS individuali e una correlazione page-level); il digest parla di 2 eventi item-level.
- Messaggio #723: digest “NOTIZIE → IPOTESI DI MERCATO”, esplicitamente non segnale confermato; API round-trip 388 ms.
- Messaggio #724: GOLD, bias NEUTRAL, priorità catalizzatore 60/100, tecnica 5m UNAVAILABLE, decisione WATCH/NO_DIRECTION; API 378 ms.
- Messaggio #725: GOLD, NO_DIRECTION, NOT_EXECUTED, score 60; front-month continuo senza scadenza esatta e senza indipendenza upstream verificata; NARWHAL non configurato; nessun livello operativo; API 368 ms.

I tre messaggi hanno un API ACK con message_id, non prova di visualizzazione sul telefono. Nessuno dei tre è un trade. Il polling [#42423194296](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42423194296), terminato alle 23:00:21 UTC, ha restituito `Pending updates: 0`; è polling, non scansione di mercato.

**Cadenza osservata:** scansioni di mercato recenti alle 15:57:48 e 20:07:13 UTC; intervallo 4h09m25s. Al controllo 23:06:57 UTC l'ultima scansione aveva circa 2h59m44s. Cron dichiarato: ogni 5 minuti. La causa del gap non è dimostrata.

## GAGARIN
Run più recente: [#42423479990](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42423479990), 23:03:38–23:03:58 UTC, SUCCESS, commit `69bb6d070dc180f9fc671c4f87b3c5fd19be1009`. Job `Run Gagarin directly on GitHub` SUCCESS; nessun artifact Actions.

Il log mostra 10 strumenti nel runtime: Soia, Grano, Brent, WTI, EUR/USD, Oro, Argento, Mais, Rame, GBP/USD. Tutti `MARKET_CLOSED`. Le quote Yahoo/BIQUOTE risultano stale:
- Cereali/soia: circa 100.133 secondi (27h49m).
- Metalli/petrolio e FX: circa 90.532–90.534 secondi (25h09m).

Argento è l'unico elemento con direzione nella classifica: LONG, probabilità 59, qualità 49,5, confidence 32, stato PAPER_WATCH. Ticker provider risolto, timestamp della quotazione, mercato/scadenza e prezzo non sono esposti; non ci sono entry, SL, TP o ATR. Non è un trade.

Riepilogo applicativo: `New feedback signals: 0`, `New additional live forecasts: 0`, `signals=0 open=0 closed=0`. Il messaggio Telegram #3717 è stato accettato dall'API (474 ms), ma il corpo non è conservato; non attribuisco il board ad Argento.

Il workflow espone `DATABASE_URL` vuoto. Il journal su main è fermo al 17 ottobre e contiene 11 righe “nessun segnale”; `paper_trade_log.csv` contiene un solo ticket legacy WTI P0001 senza prova di fill; `data/paper_open.json` contiene lo stesso P0001, contato una sola volta; `position.json` conserva la vecchia posizione HO/USD senza prova di fill; `gagarin_feedback.csv` non esiste su main. `commodities_prediction_log.json` è un archivio storico di predizioni, non prova di esecuzione.

**Cadenza osservata:** monitor alle 15:31:37, 19:38:07 e 23:03:38 UTC; intervalli 4h06m30s e 3h25m31s. Cron dichiarato: ogni 15 minuti. La causa dei gap non è dimostrata.

## PR e correzioni esistenti
Metadata GitHub aggiornato:
- GAGARIN #175 gestione webhook/polling: OPEN, non merged.
- GAGARIN #192 identità contratto/outcome: OPEN, non merged.
- GAGARIN #223 scansione M5 a sette strumenti senza Argento: OPEN/DRAFT.
- GAGARIN #219 rimozione EUR/USD e GBP/USD: OPEN, non merged.
- SPUTNIK #144 persistenza stato: OPEN, non merged.
- SPUTNIK #148 stop ripetizione raccomandazioni: OPEN, non merged.
- GAGARIN #235 persistenza journal CFD PAPER isolato: OPEN/DRAFT; non è attiva su main e non dimostra persistenza del journal commodity/futures.

Il runtime GAGARIN continua quindi a mostrare Argento e le due coppie FX. Le PR sono proposte, non correzioni integrate.

## Fonti consultate
- GitHub Actions runs e job logs dei due repository.
- Workflow `.github/workflows/trump_tracker.yml` e `.github/workflows/gagarin-monitor.yml`.
- Ledger PRAVDA, `journal.csv`, `paper_trade_log.csv`, `data/paper_open.json`, `position.json`, `commodities_prediction_log.json`; `gagarin_feedback.csv` restituisce 404.
- Metadata GitHub delle PR #144, #148, #175, #192, #219, #223 e #235.

## Lacune e prossimo controllo
1. SPUTNIK: verificare una nuova run di mercato separata dal polling; conservare ticker, provider, timestamp quotazione e scadenza esatta.
2. GAGARIN: alla riapertura dei mercati verificare freschezza e timestamp delle quotazioni; il run del weekend non consente outcome forward.
3. Non attribuire il board #3717 a un singolo strumento finché il corpo non è conservato.
4. Non calcolare outcome dei record legacy finché non esistono identità esatta del contratto, timestamp quote, fill e candele successive dello stesso contratto.

**Nessuna modifica al codice o ai workflow. Nessun merge/deploy, ordine reale, segreto o configurazione Render toccati. Nessun servizio a pagamento. PAPER ONLY.**
