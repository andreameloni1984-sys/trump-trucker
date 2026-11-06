# PRAVDA — audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-06 00:46 UTC (01:46 Europe/Rome)**

## Sintesi

- **SPUTNIK:** un nuovo candidato GOLD LONG `EARLY_SETUP`, con livelli numerici ma `NOT_EXECUTED`; il mercato è dichiarato future continuo front-month, senza scadenza esatta e senza indipendenza upstream verificata.
- **GAGARIN:** nessun nuovo monitor schedulato dopo il run #421229 delle 22:36 UTC. I tre WATCH Brent/WTI/Argento già registrati restano non-trade.
- **Outcome:** nessun TP o SL verificabile; nessun campione di trade verificabile.
- **Ledger:** 30 record, 30 firme uniche, zero duplicati. È stato aggiunto un solo record, per il nuovo messaggio CFD SPUTNIK #703.

## 1. GitHub Actions — cronologia verificata

### SPUTNIK

Ultimo collector schedulato trovato tra i 100 run più recenti:
- [Run #42130911695](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42130911695), run #277.
- Creato/avviato: 2026-11-05 23:38:20 UTC.
- Concluso: 23:38:32 UTC, `success`.
- Job `sputnik`: tutti gli step elencati `success`.
- Il workflow su `main` dichiara cron `2-59/5 * * * *`.

Alle 00:46 UTC non risultano run schedulati del collector successivi a #42130911695 nella prima pagina di 100 run. Il gap è di circa 68 minuti rispetto all'ultimo collector. La causa non è dimostrata; non attribuisco il gap a saturazione, errore di GitHub o sospensione senza log specifici.

### GAGARIN

Ultimo run del workflow `gagarin-monitor.yml` trovato nella prima pagina di 100 Actions:
- [Run #42122929435](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42122929435), run #157.
- Creato/avviato: 2026-11-05 22:36:33 UTC.
- Concluso: 22:36:53 UTC, `success`.
- Job `Run Gagarin directly on GitHub`: tutti gli step `success`.
- Il workflow su `main` dichiara cron `*/15 * * * *`.

Non risultano successivi run del monitor schedulato o manuali nella cronologia esaminata fino alle 00:46 UTC. Il gap rispetto all'ultimo monitor è di circa 2 ore e 10 minuti. I run GAGARIN delle 00:19 UTC sono test di PR sul branch #207, non esecuzioni del monitor in produzione.

## 2. SPUTNIK — nuovo candidato GOLD LONG

Fonte: [log Actions #42130911695](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42130911695).

| Campo | Valore osservato |
|---|---|
| Record PRAVDA | `PRAVDA-SPUTNIK-CFD-RUN42130911695-20261105T233828Z-GOLD-LONG-4102.2002-4096.3502-4108.0502-4113.9001` |
| Generazione (timestamp log header CFD) | 2026-11-05 23:38:28.215106 UTC |
| Invio/ack API (timestamp log) | 2026-11-05 23:38:28.216541 UTC |
| Telegram message_id | 703; analisi correlata 702 |
| Strumento | GOLD |
| Ticker risolto | NON REGISTRATO |
| Mercato | FUTURES_CONTINUOUS_FRONT_MONTH |
| Scadenza | UNKNOWN |
| Provider | NON ESPOSTO |
| Timestamp/età quotazione | NON ESPOSTI |
| Direzione preliminare | LONG |
| Tecnica CFD focalizzata | N/D — NOT_ASSESSED |
| D-L-A | NEUTRAL / NO_DIRECTION |
| Allineamento notizie | NO_DIRECTIONAL_NEWS |
| Entry / SL | 4102.2002 / 4096.3502 |
| TP1 / TP2 | 4108.0502 / 4113.9001 |
| ATR | 3.9 |
| Score | 70/100 |
| Stato | EARLY_SETUP — NOT_EXECUTED |
| Outcome | ESITO NON VERIFICABILE |

L'analisi correlata #702 descrive momentum 5m positivo (+0,497% negli ultimi 15 minuti), ma specifica che non esiste un catalizzatore USA direzionale verificato. Nel messaggio CFD #703 la tecnica focalizzata è invece `NOT_ASSESSED` e D-L-A è `NO_DIRECTION`. Il punteggio 70 non costituisce validità operativa.

Il messaggio #703 mostra entry, SL, TP e ATR, ma avverte esplicitamente: front-month continuo, scadenza esatta e indipendenza upstream non verificate; non usare i livelli per entry/SL/TP. NARWHAL è `NOT_CONFIGURED`; l'indipendenza del cross-check SILV non è verificata. Non esiste una base per confrontare candele successive dello stesso contratto. Il candidato resta `NOT_EXECUTED`, non un trade.

Il log registra API acknowledgement per i messaggi 702 e 703 (round-trip dichiarati 479 ms e 365 ms). Questo dimostra accettazione API, non consegna sul dispositivo né esecuzione. Il messaggio di test 731 compare nella fase di regressione precedente al collector e non è conteggiato come notifica di mercato.

### Intelligence e handoff

Il collector registra `findings=1`, una correlazione da fonti pubbliche, zero filing e zero nuove operazioni documentate. Il record persistito con event_id `73e28085eb0315cd4aaa578d` è page-level: URL archivio generale, titolo e data di pubblicazione mancanti. I tag `AI_TECH` e `MEDIA` sono falsi positivi da sottostringhe `ai` in “fair” e `media` in “immediately”; non è un catalizzatore commodity e non entra nel ledger dei segnali.

Altri limiti live:
- SEC: HTTP 403, cooldown 21.600 secondi.
- White House RSS: `HTTPError`.
- Handoff SPUTNIK → GAGARIN disabilitato perché `GAGARIN_CLOUD_API_URL` e `GAGARIN_CLOUD_API_KEY` risultano vuoti.

### Persistenza su main

Lo stesso run #42130911695 ha ancora eseguito il vecchio step di persistenza su `main`: il log mostra `git push origin main` e `6b65f9b..9927456 main -> main`. Quindi la persistenza fuori da main proposta nella PR #140 non è ancora attiva.

- [PR #140 — stato su branch dedicato](https://github.com/andreameloni1984-sys/trump-trucker/pull/140): OPEN, non merged; il run CI #42127702651 ha eseguito 190 test con esito OK. La PR è basata sul main corrente e dichiara 3 commit avanti, 0 indietro.
- [PR #136 — provenienza e livelli continui](https://github.com/andreameloni1984-sys/trump-trucker/pull/136): OPEN, non merged. Il diff propone di etichettare i livelli di un continuous future o di un contratto privo di metadati come teorici/non operativi.
- [PR #139 — falsi tag AI/MEDIA](https://github.com/andreameloni1984-sys/trump-trucker/pull/139): OPEN, non merged. I due workflow CI sul suo head hanno esito success, ma il confronto con main attuale indica 3 commit avanti e 2 indietro; la correzione non è attiva su main.

PRAVDA ha aggiunto evidenza ai thread:
- [Commento audit su #136](https://github.com/andreameloni1984-sys/trump-trucker/pull/136#issuecomment-6673566375)
- [Commento audit su #140](https://github.com/andreameloni1984-sys/trump-trucker/pull/140#issuecomment-6673568647)

## 3. GAGARIN — ultimo monitor, WATCH e quotazioni

Fonte: [log Actions #42122929435](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42122929435).

Il run riporta `DATABASE_URL` vuoto e soglie runtime 40/30/35, R/R 2.5, `MAX_ENTRY_STOP_ATR=2.5`. Nessuna di queste soglie è stata modificata.

### Età quotazioni nel run

| Strumento | Provider | Età | Stato |
|---|---|---:|---|
| Brent | Yahoo | 2.216,3 s | STALE |
| WTI | Yahoo | 2.209,1 s | STALE |
| Argento | Yahoo | 2.223,8 s | STALE |
| Oro | Yahoo | 2.208,0 s | STALE |
| Rame | Yahoo | 2.221,0 s | STALE |
| Grano | Yahoo | 11.809,4 s | STALE |
| Soia | Yahoo | 11.809,7 s | STALE |
| Mais | Yahoo | 11.810,6 s | STALE |

EUR/USD e GBP/USD risultano LIVE su BiQuote (109,2 e 109,7 secondi), ma il log li classifica come Forex ausiliari, non segnali commodity.

### WATCH già registrati — nessun nuovo record

| Strumento | Direzione | Prob. | Qualità | Confidenza | Stato |
|---|---|---:|---:|---:|---|
| Brent | LONG | 59 | 52,5 | 32 | PAPER_WATCH, bloccato |
| WTI | LONG | 59 | 52,5 | 32 | PAPER_WATCH, bloccato |
| Argento | LONG | 59 | 49,5 | 32 | PAPER_WATCH, bloccato |

Tutti sono bloccati da dati stale, trigger non confermato e altri gate di conferma. Non hanno entry, SL, TP o ATR operativo. Sono già presenti nel ledger del 5 novembre e non vengono duplicati.

Il riepilogo WATCH ha ricevuto API acknowledgement con message_id 3699 alle 22:36:50.098848 UTC; generazione riportata alle 22:36:46.859765 UTC, circa 3,24 secondi prima. È prova di accettazione API, non consegna sul dispositivo.

Il journal del run riporta zero nuove paper entries, zero outcome aggiornati e zero nuovi feedback.

### Journal e feedback riletti

- `journal.csv`: 11 righe dati del 17 ottobre, tutte con “nessun segnale”.
- `paper_trade_log.csv`: una riga WTI LONG del 8 ottobre, `LEGACY_IMPORT`; provider, ticker eseguito, timestamp quote, mercato e scadenza non valorizzati.
- `data/paper_open.json`: P0001 WTI LONG con gli stessi livelli della riga legacy; è lo stesso artefatto logico, non un secondo trade. P&L nullo, stato OPEN non prova fill.
- `gagarin_feedback.csv`: path pubblico assente (404).
- La persistenza PostgreSQL non è dimostrata: `DATABASE_URL` è vuoto nel run.

### PR GAGARIN

- [PR #207 — strict CFD contract identity guard](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/207): OPEN e DRAFT, 9 commit, 2 file. Cinque workflow PR risultano success; il log dell'integration suite riporta 595 test passati in 2,36 s. È solo un confine di identità: richiede simbolo broker, contratto, scadenza, valuta e verifica manuale da schermata app; non recupera quotazioni, non dimostra un feed Trading 212 e non invia ordini.
- [PR #202 — journal PostgreSQL](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): OPEN/DRAFT; il run reale con `DATABASE_URL` vuoto non dimostra persistenza attiva.
- [PR #196 — sole otto commodities](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/196): OPEN/DRAFT; il run #421229 analizza 10 strumenti (8 commodities e 2 Forex ausiliari).
- [PR #192 — identità contratto/outcome ambigui](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, non merged.

PRAVDA ha registrato gli ultimi riscontri nei thread:
- [Commento audit su #196](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/196#issuecomment-6673569206)
- [Commento audit su #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202#issuecomment-6673569819)

## 4. Ledger e statistiche

Nuovo snapshot: `pravda-signal-ledger-2026-11-06.csv`.

- Record totali: **30**.
- Firme uniche: **30**.
- Duplicati: **0**.
- Nuovo record: un candidato SPUTNIK GOLD LONG `EARLY_SETUP / NOT_EXECUTED`.
- WATCH GAGARIN precedenti: mantenuti senza duplicati.
- TP verificati: **0**.
- SL verificati: **0**.
- Outcome verificabili: **0**.
- Win rate e rendimento medio: **N/D**.

Nessun backtest è stato prodotto. Non sono state usate quotazioni spot, futures continui o scadenze diverse per attribuire esiti. Per i candidati senza ticker/contratto/scadenza e timestamp quote non esiste una serie successiva ammissibile.

## 5. Prossimo controllo

1. Verificare se il collector SPUTNIK riprende la cadenza e se la persistenza su branch dedicato viene integrata; fino ad allora main continua a ricevere commit dello stato.
2. Verificare il prossimo monitor GAGARIN e registrare per ogni commodity ticker effettivo, provider, timestamp/età, mercato e scadenza.
3. Non valutare i tre WATCH GAGARIN né il GOLD SPUTNIK senza candele successive dello stesso identico strumento/contratto.
4. Verificare la configurazione del journal privato solo attraverso evidenza runtime; PRAVDA non legge né modifica secrets.
5. Verificare le PR #136/#139/#140 e #192/#196/#202/#207 dopo eventuali aggiornamenti o merge.

**Perimetro:** PRAVDA ha aggiornato soltanto gli artefatti documentali di audit e ha lasciato commenti probatori sulle PR esistenti. Nessun codice dei bot, strategia, filtro, punteggio o rischio modificato; nessun merge/deploy, ordine reale, accesso Trading212, modifica secrets o Render. Nessun servizio a pagamento. **PAPER ONLY.**
