# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-06 19:36:24 UTC (20:36:24 Europe/Rome)**

## Sintesi esecutiva

- Nessun nuovo collector SPUTNIK dopo [#42270098789](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42270098789), schedule alle 18:22:24 UTC. Età al cut-off: 1h14m.
- Nessun nuovo monitor prezzi GAGARIN dopo [#42263910777](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42263910777), schedule alle 17:41:19 UTC. Età al cut-off: 1h55m05s.
- Le cadenze configurate restano 5 minuti SPUTNIK e 15 minuti GAGARIN; le esecuzioni osservate non rispettano la frequenza.
- Nessun nuovo segnale di mercato da aggiungere al ledger.
- Ledger: **35 record, 35 firme uniche, 0 duplicati**. Esiti registrati: 28 `ESITO_NON_VERIFICABILE`, 7 `NON_TRADE`.
- Nessun fill, SL o TP verificato; campione di trade verificabili = 0, quindi win rate e average R = N/D.
- Nuovi sviluppi CI: SPUTNIK PR #146 e GAGARIN PR #224 hanno suite verdi; entrambe restano aperte e non integrate. GAGARIN PR #223 propone una scansione M5 a sette strumenti con argento escluso, ma è draft e non attiva su main.
- PRAVDA ha aggiunto un commento di audit alla PR GAGARIN #91 sul difetto dimostrato di identità contratto nel forward-outcome matching. Nessuna modifica al codice dei bot.

## 1. GitHub Actions e continuità

Branch main osservati al controllo:
- SPUTNIK: `fecfb6bfd68e94a73824439b26efce794521a03f`.
- GAGARIN: `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`.

### SPUTNIK

- Ultimo collector schedule: [#42270098789](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42270098789), 18:22:24–18:22:35 UTC, SUCCESS, eseguito sul commit `88d4333691bdf81a2fdabfb929756470e084aadd`.
- Collector precedente: [#42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412), 11:31:39 UTC. Gap: **6h50m45s**.
- Cron presente in `.github/workflows/trump_tracker.yml`: `2-59/5 * * * *`.
- Nessun collector schedule successivo alle 18:22 nelle 100 Actions più recenti. Telegram Polling #42265633569 alle 17:52:46 e PR checks non sono collector di mercato.
- Il run #42270098789 ha completato test, collector e persistenza di stato con SUCCESS. Questo non dimostra che il collector sia ripartito con cadenza regolare.

### GAGARIN

- Ultimo monitor schedule: [#42263910777](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42263910777), 17:41:19–17:41:37 UTC, SUCCESS, commit main `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`.
- Monitor precedente: [#42203497432](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42203497432), 10:32:52 UTC. Gap: **7h08m27s**.
- Cron presente in `.github/workflows/gagarin-monitor.yml`: `*/15 * * * *`; `MONITOR_INTERVAL_MINUTES=15`; `PAPER_TRADING_ONLY=1`.
- Nessun monitor schedule successivo alle 17:41 nelle 100 Actions più recenti. I run di test PR #223/#224 non sono monitor di mercato.
- Il workflow dichiara che la persistenza dei journal pubblici è disabilitata finché lo storage privato non sia verificato.

Non attribuisco i gap a una causa tecnica non dimostrata.

## 2. SPUTNIK — sei candidati CFD nel ledger

Tutti i sei record sono `cfd_early_setup_not_executed`, non trade. Tutti sono GOLD su future continuo front-month; scadenza esatta UNKNOWN. Il mapping `GC=F` è configurato in alcune esecuzioni, ma il ticker effettivamente risolto non è esposto in modo consistente. Provider runtime, timestamp e age della quotazione non sono disponibili in questi alert; dove compare Yahoo 1m futures è soltanto un fallback di codice, non la prova del ramo runtime usato.

| Run / messaggio | Generazione UTC | Invio/API ACK UTC | Bias | Entry | SL | TP1 | TP2 | ATR |
|---|---|---|---|---:|---:|---:|---:|---:|
| [#42010313054](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42010313054) / #698 | 2026-11-05 10:23:40.296 | 10:23:40.297 | LONG | 4134.2002 | 4132.2287 | 4136.1717 | 4138.1432 | 1.3143 |
| [#42081626022](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42081626022) / send non confermato | 2026-11-05 18:10:17.484 | NON CONFERMATO | SHORT | 4111.7998 | 4114.8533 | 4108.7463 | 4105.6928 | 2.0357 |
| [#42130911695](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42130911695) / #703 | 2026-11-05 23:38:28.215 | 23:38:28.217 | LONG | 4102.2002 | 4096.3502 | 4108.0502 | 4113.9001 | 3.9000 |
| [#42157892570](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42157892570) / #706 | 2026-11-06 03:39:53.954 | 03:39:53.955 | SHORT | 4059.2 | 4062.0286 | 4056.3713 | 4053.5427 | 1.8857 |
| [#42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412) / #708 | 2026-11-06 11:31:48.568 | 11:31:48.569 | LONG | 4075.8999 | 4074.2713 | 4077.5285 | 4079.1570 | 1.0857 |
| [#42270098789](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42270098789) / #712 | 2026-11-06 18:22:32.111 | 18:22:32.113 | SHORT | 4069.3 | 4071.7536 | 4066.8465 | 4064.3929 | 1.6357 |

Osservazioni:
- #698: il ledger registra conflitto di direzione; provider/ticker runtime e timestamp quota mancanti.
- L'invio CFD del run #42081626022 non è confermato: connection reset. Non è prova di consegna.
- #703: `NO_DIRECTIONAL_NEWS`, D-L-A `NO_DIRECTION`, focused technique `NOT_ASSESSED`; livelli non operativi.
- #706: il post pubblico 43491 è stato pubblicato alle 23:18:52 UTC del 5 novembre e rilevato nel collector del 6 novembre alle 03:39:53 UTC: circa **4h21m di ritardo**. Uno screenshot XAUUSD spot presente nello storico è solo contesto; non è lo stesso future/contratto e non viene usato per valutare TP/SL.
- #708: analisi preliminare LONG, ma scheda CFD con tecnica `NOT_ASSESSED` e D-L-A `NEUTRAL/NO_DIRECTION`; struttura non univoca.
- #712: bias preliminare SHORT, ma scheda CFD mostra tecnica LONG e D-L-A LONG in contrasto. Nessuna notizia direzionale; livelli esplicitamente non operativi senza scadenza e provenienza verificata.
- Tutti i messaggi con API ACK provano solo accettazione Telegram API/message_id, non consegna al dispositivo né esecuzione. #712 è stato accettato in circa 311 ms.

### Stato intelligence SPUTNIK

Il file `sputnik_state.json` su main è stato letto direttamente:
- aggiornato `2026-11-06T18:22:30.578530Z`;
- 500 elementi in `intelligence_history`;
- `events=0`;
- `telegram_active=true`;
- offset Telegram presente.

Due item pubblici recenti:
- [Post 43495](https://www.trumpstruth.org/statuses/43495): pubblicato 12:01:50 UTC, rilevato 18:22:30.542 UTC, circa **6h20m40s** dopo. Il testo usa “GOLD” in senso metaforico parlando di Super Intelligence/AI, ma il dominio registrato è `METALS`; event type `OTHER`, `NO_ANALOGUE`. L'analisi di mercato ha comunque riportato `NO_DIRECTIONAL_NEWS`: non è diventato un catalizzatore operativo.
- [Post 43496](https://www.trumpstruth.org/statuses/43496): pubblicato 18:05:27 UTC, rilevato 18:22:30.542 UTC, circa **17m04s** dopo; classificato `POLITICAL_CAMPAIGN`, senza analogo storico.

Il falso positivo semantico di 43495 è distinto dal problema dei token brevi. Il commento PRAVDA esistente su [PR #143](https://github.com/andreameloni1984-sys/trump-trucker/pull/143#issuecomment-6693183634) lo segnala già; non è stato duplicato.

## 3. GAGARIN — WATCH, dati stale e artefatti legacy

### Ultimo monitor e pre-alert

Nel run [#42263910777](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42263910777):
- tutte le otto commodity del paniere operativo risultano YAHOO STALE, età **601.8–615.7 secondi**;
- EUR/USD e GBP/USD compaiono come contesto ausiliario BIQUOTE LIVE (~94s), marcato non operativo; non sono conteggiati come commodity signals;
- nessuna entrata journal, nessun nuovo feedback signal, nessun outcome aggiornato e nessuna forecast aggiuntiva;
- Telegram API ha accettato il watch-board #3709 alle 17:41:35.207 UTC, circa 436 ms dopo la preparazione. Il body del messaggio non è conservato nel log: strumento e direzione non sono attribuibili con certezza. La riga Argento LONG visibile nella classifica non prova che #3709 fosse un alert specifico sull'argento.

Il flag `GAGARIN_FOREX_ON_DEMAND=0` è nel workflow main, ma il monitor continua a includere EUR/USD e GBP/USD come contesto ausiliario. I commenti PRAVDA già presenti su [PR #221](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221#issuecomment-6693184324) documentano il comportamento.

### Artefatti main

- `journal.csv`: 11 righe, tutte del 17 ottobre, tutte con “nessun segnale”.
- `paper_trade_log.csv`: un solo ticket legacy WTI LONG del 8 ottobre; entry 96.24, SL 89.37, TP1 103.11, TP2 106.55. Nota riferisce una chiusura spot del 6 ottobre; non esiste prova di fill, ticker/mercato/contratto di esecuzione o timestamp intraday della quota. `data/paper_open.json` contiene lo stesso P0001 WTI OPEN, non un secondo trade.
- `position.json`: vecchia posizione Heating Oil LONG aperta il 15 settembre; entry 4.8844, SL 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882. Non c'è prova indipendente di fill o di contratto/provider; non viene conteggiata come trade verificato.
- `commodities_prediction_log.json`: 981 record, ultimo `created_at` 2026-09-15T15:45:04.462276Z. I record finali sono `PENDING`; anche l'etichetta `COMPRA ORA` non prova esecuzione.
- `commodities_monitor_state.json`: timestamp 2026-09-17T03:44:02Z, quindi artefatto storico e non stato del monitor del 6 novembre.
- `gagarin_feedback.csv`: non presente su main (404). Il workflow dichiara la persistenza pubblica disabilitata in attesa di storage privato verificato.

### Difetto dimostrato nel tracker outcome

Su main, `engine/feedback.py`:
- registra `symbol`, `timeframe` e `data_source`, ma non mercato, contract ID/scadenza, provider della quota o timestamp della quota;
- `update_open_outcomes()` abbina gli stati per `(symbol, timeframe)`, con fallback per il solo symbol se esiste un solo stato;
- filtra correttamente le candele strettamente successive all'entry bar e, se SL e TP cadono nella stessa candela, sceglie conservativamente SL.

La regola temporale è utile, ma il matching non prova che le candele siano dello stesso contratto/scadenza. Un simbolo continuo/rollato potrebbe quindi associare dati di un contratto diverso. Questo non soddisfa il requisito di identità esatta. PRAVDA ha registrato il rilievo su [PR #91](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/91#issuecomment-6693672608); la PR è draft e basata su un commit storico, non su main.

## 4. Ledger e statistiche

File: [`reports/pravda-signal-ledger-2026-11-06.csv`](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-06.csv)
- Blob SHA: `0bf31f047b157129bf9329d1727f0078e9082e61`.
- Record: 35; firme uniche: 35; duplicati: 0.
- Distribuzione: 6 candidati CFD SPUTNIK `NOT_EXECUTED`; 21 predizioni storiche GAGARIN `PENDING`; 1 ticket WTI legacy; 6 WATCH pre-alert GAGARIN; 1 watch-board #3709 non attribuibile.
- Outcome ledger: 28 `ESITO_NON_VERIFICABILE`, 7 `NON_TRADE`.
- Fill verificati: 0; SL verificati: 0; TP verificati: 0; outcome cronologici verificabili: 0.
- Win rate e average R: N/D (nessun trade con fill e percorso prezzi verificati).

Nessuna candela successiva dello stesso identico strumento e contratto è disponibile per classificare SL-first o TP-first. Non sono stati usati spot, contratti con scadenze diverse o prezzi non timestampati per stimare esiti.

## 5. PR e correzioni già esistenti

### SPUTNIK
- [PR #146 — alert individuali e calendario economico](https://github.com/andreameloni1984-sys/trump-trucker/pull/146): OPEN, non merged; ranking e item-intelligence tests verdi sui run #42280773210 e #42280772835.
- [PR #145 — diagnostica errori quote Yahoo futures](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN, non merged; ranking e Telegram-menu tests verdi #42277907846/#42277907845.
- [PR #107 — provenienza quote CFD](https://github.com/andreameloni1984-sys/trump-trucker/pull/107): OPEN, non merged; base branch storico, commento PRAVDA già presente con evidenza del run #42270098789.
- [PR #143 — falsi domini da token brevi](https://github.com/andreameloni1984-sys/trump-trucker/pull/143): OPEN, non merged; ranking e item-intelligence tests verdi #42243656376/#42243656439, ma il caso semantico “GOLD” metaforico resta distinto e già segnalato.

### GAGARIN
- [PR #224 — calendario economico, briefing e alert evento](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/224): OPEN, non merged, non draft; sei suite verdi (#42280705809, #42280705823, #42280705827, #42280705847, #42280705941, #42280706223). I run sono test PR, non monitor live.
- [PR #223 — scansione M5 a sette strumenti, argento escluso](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): OPEN/DRAFT, non merged; cinque suite principali verdi (#42277864644, #42277864646, #42277864667, #42277864761, #42277864842). Il bot Cloudflare ha riportato un deploy fallito del servizio `telegram-github-bridge`; è un esito separato dai test di analisi. Su main il monitor precedente includeva ancora otto commodity, quindi l'esclusione dell'argento non è attiva.
- [PR #222 — rimozione session veto](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222): OPEN/DRAFT, non merged.
- [PR #221 — rimozione rotte FX residue](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): OPEN/DRAFT, non merged; il contesto FX ausiliario è ancora visibile nel monitor main.
- [PR #219 — rimozione EUR/USD e GBP/USD dall'universo](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219): OPEN, non merged.
- [PR #218 — validazione timestamp/age BiQuote](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/218) e [PR #217 — identità contratti CFD Trading 212](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/217): entrambe OPEN/DRAFT, non integrate.
- [PR #202 — persistenza journal/feedback](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): OPEN/DRAFT, non integrata.

Nessuna PR è stata approvata, unita o distribuita da PRAVDA.

## 6. Fonti consultate e limiti

Fonti:
- GitHub Actions: ultime 100 esecuzioni per repository; dettagli run/job #42270098789, #42263910777 e test PR citati.
- GitHub main: workflow `.github/workflows/trump_tracker.yml`, `.github/workflows/gagarin-monitor.yml`; SPUTNIK `sputnik_state.json`; GAGARIN journal, paper logs, monitor state, prediction log e `engine/feedback.py`.
- Ledger PRAVDA e rapporti precedenti.
- Item pubblici SPUTNIK 43495/43496.
- Commenti e metadati delle PR citate.

Limiti:
- I log Actions completi non sono disponibili come artefatto scaricabile in questo audit; sono stati usati run metadata, job/step metadata e artefatti già registrati nel ledger.
- Nessun feed prezzi gratuito è stato interrogato in questo controllo; inoltre ticker runtime e scadenza mancano, quindi non è possibile selezionare in modo sicuro candele dello stesso identico contratto.
- Nessun accesso Trading212 è stato verificato; nessuna consegna Telegram al dispositivo è dichiarata.
- Nessun servizio a pagamento usato.

## 7. Prossimo controllo

1. Verificare se parte un nuovo collector SPUTNIK e un nuovo monitor GAGARIN, distinguendo schedule, polling, riepiloghi e PR tests.
2. Per ogni nuovo candidato richiedere ticker runtime, market type, expiry/contract ID, provider, quote timestamp/age e messaggio/API ACK.
3. Verificare la coerenza fra bias preliminare, tecnica e D-L-A prima di trattare i livelli come operativi.
4. Per GAGARIN verificare freshness sulle otto commodity e che l'argento sia escluso solo dopo evidenza su main.
5. Verificare che il feedback tracker non abbini candele di contratti diversi; finché contract identity manca, mantenere `ESITO_NON_VERIFICABILE`.
6. Aggiungere al ledger solo nuove firme; non duplicare i messaggi collegati e non promuovere WATCH/PENDING/NOT_EXECUTED a trade.

**Perimetro rispettato:** audit e documentazione soltanto. Nessuna modifica a codice bot, strategia, filtri, punteggi o rischio; nessun merge, deploy o rerun; nessun ordine reale; nessuna modifica a segreti, Render o servizi esterni. PAPER ONLY.
