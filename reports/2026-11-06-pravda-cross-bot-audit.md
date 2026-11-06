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


---

# Addendum PRAVDA — 2026-11-06 01:44 UTC (02:44 Europe/Rome)

## Sintesi del controllo successivo

- Nessun nuovo segnale di mercato distinto e documentato è stato aggiunto.
- Il ledger rimane a **30 record, 30 firme uniche, zero duplicati**.
- Nessun TP/SL verificabile; nessun campione di trade verificabile.
- Il candidato SPUTNIK GOLD LONG del run #42130911695 e i tre WATCH GAGARIN del run #42122929435 restano i record più recenti già presenti nel ledger.
- Non sono stati usati prezzi spot o futures con scadenza diversa per attribuire outcome.

## SPUTNIK — PR di persistenza e stato produzione

### PR #141 e PR #140

- PR #141 [Persist SPUTNIK state off main](https://github.com/andreameloni1984-sys/trump-trucker/pull/141): **OPEN, non merged**.
- Head: `d3e2c37a789d82fd06af2e342df78f4e943c77aa`; base main: `dfb6cf507f544048f8c7edfa42250136b2ab2ee5`.
- Run CI [#42140454236](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42140454236): COMPLETED/SUCCESS; job `tests`, **190 test passati**, inclusi i sei test del workflow per restore/persistenza sul branch dedicato.
- PR #140 è CLOSED senza merge ed è dichiarata superseded da #141: [PR #140](https://github.com/andreameloni1984-sys/trump-trucker/pull/140).
- La ricerca paginata dei branch contenenti `sputnik-state` non ha trovato un branch esatto chiamato `sputnik-state`; sono presenti solo branch di lavoro `fix/...`.
- Il workflow di produzione attuale su main, `.github/workflows/trump_tracker.yml`, contiene ancora `git push origin main`. La correzione di #141 è quindi testata ma non attiva in produzione.
- Il log del run #42140454236 è un log CI. Gli output interni del test runner, inclusa una riga con `message_id=731`, non sono un nuovo messaggio di mercato né prova di invio live.

PRAVDA ha aggiunto una nota probatoria nel thread: [commento su #141](https://github.com/andreameloni1984-sys/trump-trucker/pull/141#issuecomment-6674631699).

### PR #139 — classificazione AI/MEDIA

La PR resta aperta. Il body continua a riportare CI pending; non è stata verificata una nuova esecuzione CI completata sul suo head. Il falso positivo del post 43490 resta presente su main finché la correzione non viene integrata. Nessuna nuova correlazione commodity viene attribuita a quel record.

### Ultimo segnale SPUTNIK già registrato

Il GOLD LONG del run #42130911695 resta `EARLY_SETUP / NOT_EXECUTED`. D-L-A è `NEUTRAL / NO_DIRECTION`, tecnica CFD focalizzata `NOT_ASSESSED`, notizie `NO_DIRECTIONAL_NEWS`. I livelli numerici derivano da un future continuo front-month senza ticker risolto, provider, timestamp/età della quotazione o scadenza esatta. Il message_id 703 prova soltanto l'accettazione API. Nessun outcome ammissibile.

## GAGARIN — CI, journal e provenienza

### PR #207 — validazione identità CFD

Head verificato: commit `03b88c0aac1c5867f4afec70fa648761bbec93fe`, che rifiuta valori booleani per entry/stop/take-profit prima della conversione numerica (in Python `bool` è sottoclasse di `int`).

I cinque workflow GitHub Actions associati al commit risultano COMPLETED/SUCCESS:
- Public Event Brain: #42142362977;
- PAPER: #42142362920;
- NEWS alert: #42142362836;
- SOYUZ GAGARIN Tests: #42142363407;
- Execution Layer: #42142363021.

Il log dell'integration suite riporta **598 passed in 2.20s**. La PR resta OPEN/DRAFT: correzione validata sul branch, non attiva su main e non prova di feed CFD o accesso al broker.

La conversazione della PR registra un deployment Cloudflare Workers fallito per `telegram-github-bridge` alle 01:16 UTC del 6 novembre. È uno stato di integrazione esterno, non una GitHub Action del monitor GAGARIN e non prova di consegna Telegram o di deployment riuscito del bot. PRAVDA non ha avviato quel deployment.

PRAVDA ha registrato la verifica nel thread: [commento su #207](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/207#issuecomment-6674632713).

### Journal e feedback riletti

- `journal.csv`: 11 righe dati, tutte del 17 ottobre e tutte con esito testuale `nessun segnale`.
- `paper_trade_log.csv`: una riga WTI LONG del 2026-10-08 16:23 UTC, marcata `LEGACY_IMPORT`; entry 96.24, SL 89.37, TP1 103.11, TP2 106.55. Mancano provider, ticker risolto, timestamp/età quote, mercato e scadenza; la nota cita una chiusura spot del 6 ottobre. Nessun fill o outcome verificabile.
- `data/paper_open.json`: P0001 WTI LONG con gli stessi livelli della riga legacy. È lo stesso artefatto logico, non una seconda posizione; `OPEN` e P&L nullo non dimostrano un fill.
- `position.json`: Heating Oil `HO/USD` LONG aperto il 2026-09-15 13:23:44 UTC, entry 4.8844, SL 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882. Mancano provider, timestamp quote, mercato, scadenza, ATR e stato esplicito. Rimane un artefatto legacy non certificabile, non un nuovo segnale.
- `gagarin_feedback.csv`: 404 / non presente nel repository pubblico.
- `commodities_prediction_log.json`: 981 record; ultimo `created_at` 2026-09-15 15:45:04 UTC. 21 righe `COMPRA ORA`, di cui 6 senza la chiave `operational_signal`. Sono previsioni storiche, non prove di esecuzione.

### PR GAGARIN da tenere aperte

- [#202 — journal PostgreSQL](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): OPEN. Rilevata discrepanza da risolvere: il commento nel workflow main `gagarin-monitor.yml` dichiara che la persistenza sarà riattivata dopo verifica di storage privato **D1**, mentre la PR propone **PostgreSQL**/`gagarin_state`/`DATABASE_URL`. Il workflow mappa `secrets.DATABASE_URL`, ma il valore del secret non è leggibile da PRAVDA. L'ultimo log di produzione già esaminato riportava DATABASE_URL vuoto; la persistenza durevole non è provata.
- [#196 — sole otto commodities](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/196): OPEN; non integrata.
- [#192 — fingerprint contratto esatto e collisione SL/TP intrabar](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN; non integrata.
- [#195 — BiQuote CFD reference-only](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/195): OPEN/DRAFT; riferimento separato per oro, argento, WTI e Brent, non feed futures di esecuzione e non copre rame/agricoli.
- [#201 — fallback endpoint Yahoo quando stale](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/201): OPEN; il secondo endpoint è un mirror dello stesso provider, non una fonte indipendente.
- [#204](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/204) e [#206](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/206): OPEN; separazione dei comandi CFD manuali dai futures.
- [#207](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/207): OPEN/DRAFT; identity guard CFD.

PRAVDA ha segnalato la discrepanza D1/PostgreSQL nel thread: [commento su #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202#issuecomment-6674632181).

### Limite cronologia Actions

Il connettore GitHub disponibile consente di leggere i job/log di run noti e i workflow associati a commit PR, ma in questo controllo non espone l'elenco completo paginato dei run schedulati di produzione. I cinque run #421423... sono CI della PR #207, non il monitor GAGARIN in produzione. Il più recente monitor di produzione con log completo già verificato resta #42122929435 (22:36 UTC del 5 novembre); non affermo che non siano esistiti run successivi non accessibili tramite questo percorso.

## Ledger e outcome

- Ledger riletto: **30 righe dati, 30 ID unici, zero duplicati**.
- Nessun nuovo segnale distinto; nessuna modifica al CSV.
- TP verificati: 0; SL verificati: 0; outcome verificabili: 0.
- Win rate e rendimento medio: N/D.
- Nessun backtest. Non sono state attribuite candele di spot, continuous futures non identificati o scadenze differenti.

## Prossimo controllo

1. Verificare il primo collector SPUTNIK successivo all'eventuale merge di #141 e accertare che scriva solo su `sputnik-state`, mai su main.
2. Verificare un nuovo run schedulato GAGARIN e acquisire per ogni commodity ticker risolto, provider, timestamp/età, mercato e scadenza.
3. Verificare che il backend del journal sia scelto e documentato coerentemente (D1 oppure PostgreSQL) e che la persistenza sia provata da un run reale senza leggere o modificare secrets.
4. Non attribuire TP/SL finché non esistono prezzi successivi dello stesso identico strumento e contratto.

**Perimetro:** soli artefatti documentali e commenti di audit PR. Nessun codice dei bot, strategia, filtro, punteggio o rischio modificato; nessun merge/deploy avviato da PRAVDA, ordine reale, accesso Trading212, modifica secrets o Render. Nessun servizio a pagamento. **PAPER ONLY.**


---

# Addendum PRAVDA — 2026-11-06 03:08 UTC (04:08 Europe/Rome)

## Sintesi del controllo

- Nuovo monitor GAGARIN verificato: run **#42152866979**, schedulato, SUCCESS.
- Il run non contiene nuove previsioni live, nuove entrate o nuovi feedback. Le otto commodities sono tutte stale.
- SPUTNIK non ha un nuovo collector schedulato successivo al run **#42130911695** delle 23:38:20 UTC del 5 novembre, nella prima pagina dei 100 run Actions più recenti consultata alle 03:08 UTC.
- Nessun nuovo segnale distinto da aggiungere al ledger.
- Ledger invariato: **30 record, 30 firme uniche, zero duplicati**.
- TP/SL verificati: 0; campione di trade verificabile: 0.

## 1. GAGARIN — monitor #42152866979

Fonte: [Actions #42152866979](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42152866979).

- Evento: `schedule`.
- Creato/avviato: 2026-11-06 02:50:37 UTC.
- Concluso: 02:50:59 UTC.
- Workflow: `.github/workflows/gagarin-monitor.yml`.
- Job `Run Gagarin directly on GitHub`: SUCCESS; tutti gli step completati.
- Commit main eseguito: `7ed290b971e780828934d80aa3b936043769eaf6`.

### Quote

Il log espone provider e anzianità, ma non timestamp assoluto della quotazione, ticker risolto, prezzo, mercato e scadenza esatta.

| Strumento | Provider | Età | Stato |
|---|---|---:|---|
| Brent | Yahoo | 638,9 s | STALE |
| Soia | Yahoo | 629,1 s | STALE |
| WTI | Yahoo | 619,8 s | STALE |
| Oro | Yahoo | 608,7 s | STALE |
| Grano | Yahoo | 628,9 s | STALE |
| Rame | Yahoo | 610,7 s | STALE |
| Argento | Yahoo | 609,6 s | STALE |
| Mais | Yahoo | 641,0 s | STALE |
| EUR/USD | BiQuote | 54,7 s | LIVE, contesto FX non operativo |
| GBP/USD | BiQuote | 55,6 s | LIVE, contesto FX non operativo |

Tutte le otto commodities hanno motivo di fallback `ALL_PROVIDER_CANDLES_STALE`. Le due coppie FX non sono quotazioni sostitutive delle commodities.

### Ranking e autorizzazione

Il ranking riporta otto commodities con etichetta `PAPER_WATCH`, ma non segnali operativi:

- Brent: Prob 48, Q 30, C 15.
- Soia: Prob 58, Q 40, C 25.
- WTI: Prob 40, Q 15, C 5.
- Oro: Prob 40, Q 15, C 5.
- Grano: Prob 58, Q 40, C 25.
- Rame: Prob 58, Q 40, C 25.
- Argento: Prob 40, Q 15, C 5.
- Mais: Prob 48, Q 30, C 15.

I blocchi riportano `LIVE_DATA_NOT_FRESH`, `NO_VALID_SETUP`, `TRIGGER_NOT_CONFIRMED`, `INVALID_SETUP_DIRECTION`, `ENTRY_MISSING`, `STOP_MISSING`, `TP1/TP2/TP3_MISSING`, `STOP_ATR_MISSING`, `RR_MISSING` e `CONFIDENCE_FAIL`; per WTI, oro e argento compare anche `QUALITY_FAIL`. Non ci sono entry, SL, TP o ATR operativi. Le righe Forex sono esplicitamente `CONTESTO FX — NON OPERATIVO`.

Il log dichiara:
- `Recorded entries: 0`;
- `Updated open outcomes: 0`;
- `New feedback signals: 0`;
- `New additional live forecasts (WATCH/other): 0`;
- `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`.

Il messaggio Telegram `message_id=3700` ha ricevuto conferma API alle 02:50:56.104429 UTC, round-trip 498 ms. È il riepilogo/pre-alert generale: il medesimo log dichiara zero nuove live forecasts. L'ack API non prova la consegna sul dispositivo e non trasforma le righe di ranking in segnali o trade.

### Persistenza e configurazione

Nel run `DATABASE_URL` è vuoto. `PAPER_TRADING_ONLY=1`; soglie runtime osservate: probabilità 40, qualità 30, confidenza 35, R/R 2,5, stop massimo 2,5 ATR, buffer strutturale 0,15 ATR e SL minimo 0,80 ATR. Non sono state modificate.

La persistenza privata del journal non è dimostrata; il run non registra nuove entrate né feedback.

## 2. GAGARIN — cadenza Actions e polling

Il workflow main dichiara cron `*/15 * * * *`. Il run #42152866979 delle 02:50:37 UTC è l'ultimo monitor schedulato trovato nella prima pagina dei 100 run più recenti. Il monitor schedulato precedente è #42122929435 delle 22:36:33 UTC del 5 novembre: intervallo tra i due run circa 4 ore e 14 minuti. Alle 03:08 UTC non risultava ancora il run atteso delle 03:05 nella pagina consultata. La causa del gap non è dimostrata.

Il polling è separato dal monitor:
- [Run polling #42145493753](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42145493753): FAILURE.
- Log alle 01:41:37 UTC: Telegram API error 409, webhook attivo; `getUpdates` non può funzionare contemporaneamente al webhook.
- Non è un fallimento del monitor di mercato #42152866979.

## 3. SPUTNIK — ultimo collector e PR di persistenza

Ultimo collector schedulato trovato: [run #42130911695](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42130911695), 2026-11-05 23:38:20–23:38:32 UTC, SUCCESS. Il workflow main dichiara cron `2-59/5 * * * *`; nella prima pagina dei 100 run più recenti non risultano collector schedulati successivi fino al cut-off 03:08 UTC. L'ultimo polling schedulato separato trovato è #42125254302 delle 22:53:29 UTC del 5 novembre. La causa dei gap non è dimostrata.

Il candidato GOLD LONG del run #42130911695 è già nel ledger e non viene duplicato:
- generazione: 23:38:28.215106 UTC;
- messaggi API-accepted: #702 e #703;
- entry 4102.2002, SL 4096.3502, TP1 4108.0502, TP2 4113.9001, ATR 3.9;
- stato `EARLY_SETUP / NOT_EXECUTED`;
- D-L-A `NEUTRAL / NO_DIRECTION`, tecnica CFD `NOT_ASSESSED`, notizie `NO_DIRECTIONAL_NEWS`;
- future continuo front-month senza ticker risolto, provider, timestamp/età quote e scadenza esatta.
I livelli sono esplicitamente dichiarati non utilizzabili operativamente. Non esistono candele successive ammissibili dello stesso identico contratto. L'ack API non dimostra consegna sul dispositivo o esecuzione.

Il file main `.github/workflows/trump_tracker.yml` contiene ancora il passo `git push origin main` nella persistenza dello stato. La correzione non è ancora attiva:
- [PR #141](https://github.com/andreameloni1984-sys/trump-trucker/pull/141): OPEN, non merged, non draft; head `88565d17fe0b57afb1b18aafc5186c72154b7247`, base main `dd15aa87c2348d8b5ecb6ab732516ee972fc80d9`.
- [Run CI #42151438743](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42151438743): SUCCESS; log `Ran 190 tests in 0.564s`. È CI PR, non collector live.
- PR #140 è chiusa senza merge e sostituita da #141.
- [PR #139](https://github.com/andreameloni1984-sys/trump-trucker/pull/139) resta OPEN/non merged; il body riporta CI pending. La correzione dei falsi tag `ai`/ `media` non è attiva su main.

## 4. GAGARIN — correzioni già esistenti

- [PR #207](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/207): OPEN/DRAFT, non merged. Il run di integrazione [#42150575073](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42150575073) riporta **601 test superati in 2,67 s**. Identity guard isolato: non fornisce quotazioni, non dimostra un feed Trading 212 e non autorizza ordini.
- [PR #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): OPEN/DRAFT, non merged; journal PostgreSQL proposto ma `DATABASE_URL` vuoto nel run reale.
- [PR #196](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/196): OPEN/DRAFT, non merged; resta la discrepanza tra otto commodities e due righe FX di contesto nel monitor.
- [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, non merged; identità contratto e ambiguità intrabar non sono ancora attive su main.

## 5. Ledger e outcome

- Ledger riletto: **30 record, 30 ID unici, zero duplicati**.
- Nessun nuovo segnale distinto: CSV lasciato invariato.
- Nessun WATCH di ranking GAGARIN aggiunto: il run dichiara zero nuove live forecasts e non contiene direzioni/livelli operativi.
- TP verificati: 0; SL verificati: 0; outcome verificabili: 0.
- Win rate e rendimento medio: N/D.
- Nessun backtest. Nessun prezzo spot, future continuo non identificato o contratto con scadenza diversa è stato usato per attribuire outcome.

## 6. Prossimo controllo

1. Verificare il primo collector SPUTNIK successivo e accertare se #141 è stata integrata; finché non lo è, main continua a contenere la persistenza diretta su main.
2. Verificare i prossimi run monitor GAGARIN e se riprende la cadenza di 15 minuti.
3. Per ogni futura commodity acquisire ticker risolto, mercato/contratto/scadenza, provider, timestamp assoluto della quotazione e sua età.
4. Verificare il journal privato solo con evidenza runtime, senza leggere o modificare secrets.
5. Non attribuire TP/SL finché non esistono prezzi successivi dello stesso identico strumento e contratto.

**Perimetro:** aggiornato soltanto questo rapporto documentale. Nessun CSV modificato perché non sono emersi nuovi segnali; nessun codice, strategia, filtro, punteggio o rischio modificato. Nessun merge/deploy, ordine reale, accesso Trading212, modifica secrets o Render. Nessun servizio a pagamento. **PAPER ONLY.**


---

# Addendum PRAVDA — 2026-11-06 03:16 UTC (04:16 Europe/Rome)

## Esito del controllo

- Nessun nuovo segnale operativo distinto emerso nei run di produzione consultati.
- Ledger invariato: **30 record, 30 firme uniche, 0 duplicati**.
- TP verificati: **0**; SL verificati: **0**; campione di trade verificabile: **0**.
- Non è stato aggiunto alcun record WATCH/ranking al ledger, perché non rappresenta un trade né un nuovo segnale operativo autorizzato.

## GAGARIN — monitor #42152866979

Run schedulato [#42152866979](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42152866979):
- creato/avviato 2026-11-06 02:50:37 UTC;
- concluso 02:50:59 UTC, `success`;
- job `Run Gagarin directly on GitHub`, tutti gli step completati con successo.

Il log completo del job [127680000039](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42152866979) conferma `PAPER_TRADING_ONLY=1`, `DATABASE_URL` vuoto, `NARWHAL_REFERENCE_ENABLED=1` ma `NARWHAL_API_KEY` vuota.

### Prezzi

Tutte le otto commodities sono `STALE`, con provider Yahoo e motivo di fallback `ALL_PROVIDER_CANDLES_STALE`:

| Strumento | Età osservata | Provider |
|---|---:|---|
| Brent | 638,9 s | Yahoo |
| WTI | 619,8 s | Yahoo |
| Oro | 608,7 s | Yahoo |
| Argento | 609,6 s | Yahoo |
| Rame | 610,7 s | Yahoo |
| Grano | 628,9 s | Yahoo |
| Mais | 641,0 s | Yahoo |
| Soia | 629,1 s | Yahoo |

EUR/USD (54,7 s) e GBP/USD (55,6 s) sono `LIVE` su BiQuote, ma restano contesto FX ausiliario: non sostituiscono le quotazioni delle commodities e non sono stati contati come segnali operativi.

### Ranking e autorizzazione

Il run mostra otto righe commodity `PAPER_WATCH` ma nessun setup valido. I blocchi riportati includono `LIVE_DATA_NOT_FRESH`, `NO_VALID_SETUP`, `TRIGGER_NOT_CONFIRMED`, `ENTRY_MISSING`, `STOP_MISSING`, `TP1/TP2/TP3_MISSING`, `STOP_ATR_MISSING` e `RR_MISSING`; confidenza/confluenza falliscono inoltre sui candidati. Non sono presenti entry, SL, TP o ATR operativi. Le due coppie FX compaiono solo nel controllo provider e non nel ranking delle otto commodities.

Il journal del run dichiara:
- `Recorded entries: 0`;
- `Updated open outcomes: 0`;
- `New feedback signals: 0`;
- `New additional live forecasts: 0`;
- `signals=0 open=0 closed=0`.

Telegram ha restituito `message_id=3700` alle 02:50:56.104429 UTC, con round-trip 498 ms. È un acknowledgement API del riepilogo WATCH, non un trade, non un nuovo segnale e non prova di consegna sul dispositivo.

### Journal pubblico riletto

- `paper_trade_log.csv`: una riga WTI LONG del 2026-10-08 16:23 UTC, `LEGACY_IMPORT`, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55. I campi provider, ticker quote, timestamp quote, valuta/unità, mercato e dati di esecuzione sono vuoti; la nota cita una chiusura spot del 6 ottobre. Nessuna prova di fill o outcome.
- `data/paper_open.json`: P0001 WTI LONG con gli stessi livelli; è lo stesso artefatto logico della riga legacy, non una seconda posizione. `OPEN` e P&L null non dimostrano esecuzione.
- `position.json`: Heating Oil `HO/USD` LONG del 15 settembre, entry 4.8844, SL 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882; mancano provider, timestamp quote, mercato, scadenza, ATR e prova di fill.
- `journal.csv`: 11 righe del 17 ottobre, tutte con esito `nessun segnale`.
- `gagarin_feedback.csv`: non presente nel branch pubblico (404).

Il monitor schedulato precedente era #42122929435, avviato il 5 novembre alle 22:36:33 UTC. Tra i due monitor verificati intercorrono circa 4 ore e 14 minuti, nonostante il cron `*/15 * * * *`. Alle 03:16 UTC non risulta un monitor successivo a #42152866979 nella prima pagina dei run Actions consultata. Non attribuisco una causa al gap.

## SPUTNIK — collector e polling sono due workflow distinti

Ultimo collector schedulato individuato: [#42130911695](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42130911695), avviato 2026-11-05 23:38:20 UTC e concluso 23:38:32 UTC con `success`. Il job [127606975615](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42130911695) è stato riletto.

Il collector continua a produrre il candidato GOLD LONG già registrato:
- generazione 23:38:28.215106 UTC;
- messaggio CFD 703, analisi correlata 702;
- entry 4102.2002, SL 4096.3502, TP1 4108.0502, TP2 4113.9001, ATR 3.9;
- `EARLY_SETUP / NOT_EXECUTED`;
- mercato `FUTURES_CONTINUOUS_FRONT_MONTH`, scadenza UNKNOWN;
- ticker risolto, provider, timestamp/età della quotazione non esposti;
- D-L-A `NEUTRAL / NO_DIRECTION`, tecnica CFD focalizzata `NOT_ASSESSED`, notizie `NO_DIRECTIONAL_NEWS`;
- NARWHAL non configurato; indipendenza upstream non verificata.

I messaggi 702 e 703 risultano API-accepted (479 ms e 365 ms nel log); ciò non prova esecuzione né consegna sul dispositivo. Il messaggio 731 è prodotto dai test di regressione, non dal collector live. Le righe `OSError` per WHITE_HOUSE/TRUTH_ARCHIVE/OGE compaiono nella fase di test; nel collector live sono invece documentati SEC HTTP 403 con cooldown 21.600 s e White House RSS `HTTPError`.

È stato inoltre verificato il run schedulato [SPUTNIK Telegram Polling #42154936378](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42154936378), avviato 03:10:49 UTC e concluso 03:10:57 UTC con `success`. Il job polling è distinto dal collector: il suo successo non dimostra che sia stato eseguito un nuovo ciclo intelligence o prodotto un nuovo segnale. Il log mostra l'avvio di `telegram/polling_runner.py`, ma non fornisce una conferma positiva di nuovi aggiornamenti processati.

Nella cronologia Actions più recente consultata, #42130911695 resta l'ultimo evento `schedule` del workflow `.github/workflows/trump_tracker.yml`. Il cron dichiarato è `2-59/5 * * * *`; il gap supera 3 ore e 38 minuti. La causa resta non dimostrata. Il polling delle 03:10 non va confuso con il collector.

## PR e correzioni già esistenti

Stato GitHub consultato al cut-off:
- SPUTNIK [#141](https://github.com/andreameloni1984-sys/trump-trucker/pull/141): OPEN, non merged, non draft; CI [#42151438743](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42151438743) SUCCESS. Il workflow su main continua tuttavia a contenere la persistenza con `git push origin main`; correzione non attiva in produzione.
- SPUTNIK [#139](https://github.com/andreameloni1984-sys/trump-trucker/pull/139) e [#136](https://github.com/andreameloni1984-sys/trump-trucker/pull/136): OPEN, non merged.
- GAGARIN [#207](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/207): OPEN/DRAFT. I cinque workflow associati al suo head risultano SUCCESS (run #42150574967, #42150575034, #42150575016, #42150575073, #42150575058). I test CI non equivalgono a integrazione su main.
- GAGARIN [#202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202) e [#196](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/196): OPEN/DRAFT; [#192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, non merged.

Il workflow GAGARIN su main dichiara ancora cron ogni 15 minuti e mappa `DATABASE_URL` da secret, ma il log reale stampa il valore vuoto. PRAVDA non legge né modifica secrets.

## Esiti e prossimo controllo

- Nessun nuovo segnale operativo da aggiungere al ledger.
- Nessun TP/SL attribuibile: non sono disponibili candele successive dello stesso ticker, mercato e scadenza; i candidati privi di identità esatta del contratto restano `ESITO NON VERIFICABILE`.
- Nessun backtest, win rate o rendimento è stato inventato.
- Prossimo controllo: verificare la ripresa dei run collector SPUTNIK e monitor GAGARIN, la freschezza delle otto commodities e la presenza runtime di provider/ticker/contratto/scadenza/timestamp quote; controllare eventuali merge delle PR solo dopo che compaiano su main.

**Perimetro:** nessuna modifica al codice, strategia, filtri, punteggi o rischio; nessun merge/deploy, ordine reale, accesso Trading212, modifica a secrets o Render; nessun servizio a pagamento. Solo documentazione di audit. **PAPER ONLY.**

---

# Addendum PRAVDA — 2026-11-06 04:36 UTC (05:36 Europe/Rome)

## Sintesi

- Nuovo candidato SPUTNIK registrato: GOLD SHORT, run **#42157892570**, messaggio CFD **706**.
- È `EARLY_SETUP / NOT_EXECUTED`, non un trade.
- Telegram API ha accettato il messaggio 706 con round-trip di 464 ms; il processo SPUTNIK ha impiegato 3,134 s. Il ritardo non è nel rendering/invio del messaggio.
- Il post associato (event 43491) riporta pubblicazione 23:18:52 UTC del 5 novembre e compare per la prima volta nel collector osservato alle 03:39:53 UTC del 6 novembre: circa **261 minuti** dopo.
- La cronologia Actions filtrata per `event=schedule` mostra gap di oltre quattro ore nei due collector/monitor, nonostante i cron configurati a 5 e 15 minuti.
- Ledger aggiornato: **31 record, 31 firme uniche, zero duplicati**. TP/SL verificati: 0; trade con esito verificabile: 0.

## 1. SPUTNIK — run #42157892570

Fonte: [Actions #42157892570](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42157892570), job **127696303672**.

- Evento Actions: `schedule`; avvio 03:39:45 UTC, conclusione 03:39:59 UTC, SUCCESS.
- Cron su main: `2-59/5 * * * *`.
- Collector precedente: [#42130911695](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42130911695), 23:38:20–23:38:32 UTC del 5 novembre.
- Gap tra i due collector: **4h 01m 25s**. Nella cronologia schedule-filtered non compaiono invocazioni collector intermedie.
- Il run precedente #42130911695 non contiene l'event 43491; il run #42157892570 lo mostra per la prima volta nell'output pubblico.

### Latenza misurata nel run

- Public intelligence scan: 1.088 ms.
- Notification stage: 1.885 ms.
- Total Python run: 3.134 ms.
- Messaggio digest notizie 704: API accepted, round-trip 470 ms.
- Analisi mercato 705: API accepted, round-trip 468 ms.
- Analisi CFD 706: API accepted, round-trip 464 ms.
- La conferma API non prova la consegna sul dispositivo.

Il processo interno è quindi terminato in pochi secondi. La differenza tra pubblicazione della notizia e prima comparsa nel collector è circa 261m02s. Le evidenze non distinguono se la causa sia la mancata invocazione schedulata, la disponibilità tardiva del feed o entrambe. I run osservati hanno `created_at` uguale a `run_started_at`: non c'è prova di attesa in coda. Il passo dei test di regressione è presente nel workflow live, ma il log lo completa rapidamente; non spiega un ritardo di un'ora.

### Nuovo record GOLD SHORT

Firma: `PRAVDA-SPUTNIK-CFD-RUN42157892570-20261106T033953Z-GOLD-SHORT-4059.2-4062.0286-4056.3713-4053.5427`.

| Campo | Valore |
|---|---|
| Generazione (log) | 03:39:53.953549 UTC |
| Conferma API | 03:39:53.954740 UTC |
| Telegram message_id | 706 |
| Strumento | GOLD |
| Ticker | GC=F è la mappatura configurata; chiave effettivamente selezionata non emessa |
| Mercato | FUTURES_CONTINUOUS_FRONT_MONTH |
| Scadenza | UNKNOWN |
| Provider | non esposto nel run; codice prevede fallback Yahoo Finance chart 1m futures, ma il ramo effettivo non è confermato |
| Timestamp/età quote | non esposti nel messaggio/log |
| Direzione | SHORT |
| Entry / SL | 4059.2 / 4062.0286 |
| TP1 / TP2 | 4056.3713 / 4053.5427 |
| ATR | 1.8857 |
| Stato | EARLY_SETUP / NOT_EXECUTED |
| Score | 70/100, non prova di validità operativa |
| Outcome | ESITO NON VERIFICABILE |

Il messaggio dichiara tecnica 5m SHORT, D-L-A SHORT (ALIGNS), momentum 15m -0,039% e `NO_DIRECTIONAL_NEWS`. Riporta anche NARWHAL `NOT_CONFIGURED`, indipendenza upstream SILV non verificata e avvertenza esplicita che il future continuo non ha scadenza verificata e che i livelli non devono essere usati.

### Screenshot XAUUSD fornito dall'utente

Lo screenshot mostra XAUUSD spot con bid 4040,60 e ask 4041,45 alle 05:06 locali (04:06 UTC), circa 26 minuti dopo la conferma API del messaggio 706. Il bid è 18,60 (circa 0,46%) sotto l'entry teorica 4059,20, ma il confronto è solo descrittivo perché il mercato non coincide. La candela selezionata reca l'etichetta 03:15 e close 4070,95; il timezone del grafico non è esposto. Se 03:15 è ora locale della piattaforma, la candela precede l'avviso delle 04:39 locali di circa 84 minuti: è un indizio concreto di movimento già avviato, non una misura certa del ritardo del feed. Tuttavia XAUUSD spot non è lo stesso strumento/contratto del future continuo GOLD e non può essere usato per attribuire TP o SL. Non è un outcome certificato.

### Difetto di auditabilità e PR esistente

Nel codice `sputnik_cfd.py`, `build_cfd_signal` conserva nel dizionario `quote_time`, `quote_provider`, `quote_symbol`, `quote_age_seconds`, `quote_market_type` e descrizione contratto. La funzione `format_cfd_signal` non li stampa. Il messaggio mostra livelli numerici, ma non la provenienza necessaria per verificarli.

La [PR #136](https://github.com/andreameloni1984-sys/trump-trucker/pull/136) propone già di mostrare provider/ticker/timestamp/età/mercato/scadenza e di etichettare i livelli di future continuo come teorici/non operativi. È ancora OPEN e non integrata. PRAVDA ha aggiunto evidenza del run #42157892570 al thread: [commento #6677077815](https://github.com/andreameloni1984-sys/trump-trucker/pull/136#issuecomment-6677077815).

### Classificazione notizia

L'event 43491 è stato etichettato `AI_TECH` su main, ma il testo riguarda elezioni e mercato azionario; il tag deriva dalla sottostringa `ai` in “AGAIN”. La [PR #139](https://github.com/andreameloni1984-sys/trump-trucker/pull/139) corregge il matching dei token brevi. Il branch ha avuto due run finali SUCCESS alle 03:57:43 UTC (#42159626799 e #42159626686), dopo due tentativi precedenti falliti alle 03:57:23; la PR resta OPEN/non merged, quindi la correzione non è ancora attiva su main.

## 2. SPUTNIK — stato del workflow e PR

Il workflow main continua a:
- eseguire test di regressione prima del collector;
- usare `concurrency.queue: max` e `cancel-in-progress: false`;
- persistere `sputnik_state.json` con `git push origin main`.

La [PR #141](https://github.com/andreameloni1984-sys/trump-trucker/pull/141) propone di togliere i test dal ciclo live e spostare lo stato su `sputnik-state`; è OPEN, non merged. La [PR #138](https://github.com/andreameloni1984-sys/trump-trucker/pull/138) aggiunge diagnostica dei gap schedule; è OPEN, non merged. PRAVDA ha pubblicato aggiornamenti probatori nei thread #138 e #136. Nessuna modifica di codice o merge è stata eseguita da PRAVDA.

## 3. GAGARIN — monitor, prezzi e cadenza

Fonte: [Actions #42152866979](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42152866979), job **127680000039**.

- Ultimo monitor schedulato nel feed Actions: 02:50:37–02:50:59 UTC, SUCCESS.
- Monitor precedente: [#42122929435](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42122929435), 22:36:33–22:36:53 UTC del 5 novembre.
- Gap tra avvii: **4h 14m 04s**.
- Cron attuale su main: `*/15 * * * *`; `MONITOR_INTERVAL_MINUTES=15`.
- Alle 04:36 UTC non risulta un monitor schedulato successivo al run delle 02:50 nella cronologia Actions filtrata per `event=schedule`.

### Chiarimento storico della cadenza

La [PR #145](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/145) fu integrata il 2 novembre alle 18:58:22 UTC con cadenza 5 minuti. Il commit [6038ad1](https://github.com/andreameloni1984-sys/commodity-news-scanner/commit/6038ad1f2f16689067a4c54e5c59492f276f6ac8), del 3 novembre alle 12:47:29 UTC, ripristinò il monitor completo a 15 minuti e rimosse il cron del workflow aggressivo duplicato. Il commit documenta GDELT HTTP 429 e la scelta di non aumentare la pressione sulle fonti. Quindi la cadenza 5m della PR #145 non è quella attualmente attiva su main.

### Freschezza ultimo run

Tutte le otto commodities risultano Yahoo STALE:
- Brent 638,9 s;
- Soia 629,1 s;
- WTI 619,8 s;
- Oro 608,7 s;
- Grano 628,9 s;
- Rame 610,7 s;
- Argento 609,6 s;
- Mais 641,0 s.

EUR/USD e GBP/USD sono LIVE su BiQuote (54,7 e 55,6 s), ma sono contesto FX ausiliario, non quotazioni commodity. Il monitor ha prodotto solo ranking `PAPER_WATCH`, con blocchi `LIVE_DATA_NOT_FRESH`, trigger/setup/livelli mancanti. Journal: 0 nuove entrate, 0 outcome aggiornati, 0 feedback. Telegram message_id 3700 è stato accettato dall'API; non è un trade.

Il run stampa `DATABASE_URL` vuoto e `NARWHAL_API_KEY` vuota, benché `NARWHAL_REFERENCE_ENABLED=1`. La persistenza PostgreSQL e il riferimento Narwhal non sono dimostrati.

Il polling Telegram GAGARIN [#42145493753](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42145493753) è FAILURE per errore 409 (webhook attivo); è un workflow separato e non va confuso con il monitor di mercato.

### Segnalazione al reparto GAGARIN

PRAVDA ha aggiunto evidenza dei gap e delle quotazioni stale nel thread della [PR #145](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/145), commento [#6677069785](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/145#issuecomment-6677069785). La raccomandazione documentale è valutare una corsia M5/LUBJANKA leggera e separata dal monitor provider-heavy e dalle fonti news/GDELT; non ripristinare alla cieca la scansione completa ogni 5 minuti. Nessun codice è stato cambiato.

## 4. Outcome e statistiche

- Ledger: **31 record, 31 firme uniche, zero duplicati**.
- Nuovo record: un candidato SPUTNIK GOLD SHORT, `NOT_EXECUTED`.
- Trade con esecuzione dimostrata: 0.
- TP verificati: 0; SL verificati: 0.
- Outcome verificabili: 0.
- Win rate / average R: N/D.
- Nessun backtest e nessun prezzo spot o contratto diverso è stato usato per attribuire un risultato.

## 5. Fonti e prossimo controllo

Fonti consultate: Actions schedule-filtered dei due repository; job log #42157892570, #42130911695 e #42152866979; workflow YAML su main; codice `sputnik_cfd.py` e `main.py`; PR #136, #138, #139, #141, #145, #196, #202, #207; commit GAGARIN #6038ad1; ledger PRAVDA; screenshot XAUUSD fornito dall'utente.

Prossimo controllo:
1. Verificare la ripresa effettiva delle invocazioni schedule SPUTNIK (5m) e GAGARIN (15m), senza confondere polling con collector/monitor.
2. Acquisire per ogni segnale provider effettivo, ticker selezionato, timestamp/età quote, mercato e scadenza esatta.
3. Verificare le PR #136/#138/#139/#141 e l'eventuale corsia leggera GAGARIN solo quando le modifiche risultano su main.
4. Valutare outcome solo con candele successive dello stesso identico strumento e contratto.

**Perimetro:** aggiornati solo ledger/rapporto documentali e commenti di audit su PR esistenti. Nessun codice, strategia, filtro, punteggio o rischio modificato; nessun merge/deploy, ordine reale, accesso Trading212, modifica secrets o Render. Nessun servizio a pagamento. **PAPER ONLY.**



---

## Addendum PRAVDA — 2026-11-06 05:34 UTC

### Nuova fotografia delle GitHub Actions

Consultata la prima pagina dei 100 run più recenti di ciascun repository e filtrati gli eventi `schedule`, senza confondere i workflow di polling o i test PR con i collector/monitor di mercato.

**SPUTNIK**
- Workflow `.github/workflows/trump_tracker.yml`: cron `2-59/5 * * * *`.
- Ultimo collector schedulato: [#42157892570](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42157892570), 2026-11-06 03:39:45–03:39:59 UTC, SUCCESS.
- Collector schedulato precedente: [#42130911695](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42130911695), 2026-11-05 23:38:20–23:38:32 UTC, SUCCESS.
- Gap tra avvii: 4h 01m 25s. Alle 05:34 UTC non risulta un collector schedulato successivo; tempo dall'ultimo avvio: 1h 54m 48s.
- Il run #42157892570 ha `created_at == run_started_at`, durata circa 14 secondi. Non c'è evidenza di coda per quel run.
- Il workflow su main esegue ancora `python -m unittest tests/test_telegram_delivery.py tests/test_sputnik_item_intelligence.py -v` prima del collector. I test iniziano alle 03:39:50.472 UTC; la scansione intelligence termina alle 03:39:52.025 UTC. Il test step osservato non spiega un ritardo di un'ora.
- Il workflow mantiene `concurrency.queue: max`, `cancel-in-progress: false` e la persistenza `git push origin main`.
- Una volta avviato, il collector invia i messaggi 704/705/706 con round-trip API di circa 470/468/464 ms. L'API ha confermato gli ID; ciò non prova la consegna sul dispositivo.
- La scansione ha registrato 2 findings; SEC ha restituito HTTP 403 e il feed White House HTTPError. La fonte effettivamente responsabile del ritardo di pubblicazione/visibilità dell'evento non è isolata.

**PR #141 SPUTNIK**
- Stato alle 05:34 UTC: OPEN, non merged, non draft.
- Head `33e9c93313724f9582756a6a8ab70d4f77664649`.
- Run CI [#42167340000](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42167340000): SUCCESS, 190 test.
- La PR rimuove i test dal collector live e sposta la persistenza su `sputnik-state`; non modifica il cron e non garantisce che GitHub generi gli eventi schedule.
- PR #138 resta OPEN e stacked su #137; non modifica cron/concurrency, ma aggiunge diagnostica read-only dei gap.

**GAGARIN**
- Workflow `.github/workflows/gagarin-monitor.yml`: cron `*/15 * * * *`, `MONITOR_INTERVAL_MINUTES=15`.
- Ultimo monitor schedulato: [#42152866979](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42152866979), 2026-11-06 02:50:37–02:50:59 UTC, SUCCESS.
- Monitor schedulato precedente: [#42122929435](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42122929435), 2026-11-05 22:36:33–22:36:53 UTC.
- Gap tra avvii: 4h 14m 04s. Alle 05:34 UTC non risulta un monitor schedulato successivo; tempo dall'ultimo avvio: 2h 43m 56s.
- Il job è durato circa 22 secondi: il runtime del monitor non spiega da solo il gap multi-orario.
- Tutte le otto commodities erano Yahoo STALE, età 608,7–641,0 secondi. EUR/USD e GBP/USD LIVE su BiQuote sono ausiliari e non sostituiscono le quotazioni commodity.
- Ranking: otto righe PAPER_WATCH, nessun setup operativo; entry/SL/TP/ATR operativi assenti.
- Journal del run: 0 nuove entrate, 0 feedback, 0 nuove live forecasts; `DATABASE_URL` vuoto. Telegram message_id 3700 accettato dall'API, non prova di consegna al dispositivo.
- Il log del run non contiene righe LUBJANKA/interceptor/early-move; lo stato M5 non è verificabile dal log di produzione.
- Polling GAGARIN [#42145493753](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42145493753) è un workflow separato, FAILURE per HTTP 409 webhook attivo; non è un monitor di mercato.

### Journal e feedback riletti

- `paper_trade_log.csv`: una sola riga WTI legacy dell'8 ottobre, senza provider/ticker effettivo/timestamp quote/contratto/esito.
- `data/paper_open.json`: P0001 WTI LONG, stessa posizione legacy; non va contata due volte.
- `journal.csv`: 11 righe del 17 ottobre, tutte `nessun segnale`.
- `gagarin_feedback.csv`: non presente su main (404).
- `position.json` nel percorso `data/position.json`: non presente su main (404).
- Il codice feedback deduplica per signal ID e usa le candele successive, ma senza feedback file persistente e senza identità esatta del contratto non ci sono outcome da certificare.

### PR GAGARIN rilevanti

- PR #145 è CLOSED/MERGED, ma il commit successivo [6038ad1](https://github.com/andreameloni1984-sys/commodity-news-scanner/commit/6038ad1f2f16689067a4c54e5c59492f276f6ac8) ha riportato il monitor provider-heavy a 15 minuti dopo evidenze GDELT 429; il main attuale resta a 15m.
- PR #180 (logging LUBJANKA) è OPEN, non merged; il run attuale non espone righe LUBJANKA.
- PR #202 (journal PostgreSQL) è OPEN/DRAFT, non merged; il run reale continua a mostrare DATABASE_URL vuoto.
- PR #207 (identity guard CFD) è OPEN/DRAFT, non merged.
- PR #197 LUBJANKA handoff risulta CLOSED senza merge.

### Segnali e outcome

- Ledger invariato: 31 record, 31 firme uniche, zero duplicati.
- Nessun nuovo segnale distinto rispetto all'ultimo record GOLD SHORT SPUTNIK (run #42157892570, message 706).
- GOLD SHORT resta `NOT_EXECUTED`; entry 4059.2, SL 4062.0286, TP1 4056.3713, TP2 4053.5427, ATR 1.8857. Future continuo GC=F configurato, ma runtime quote source/timestamp/age e scadenza esatta non esposti. Esito NON VERIFICABILE.
- I prezzi XAUUSD dello screenshot utente sono spot/CFD e non vengono usati per assegnare TP/SL al future continuo.
- Trade con esecuzione dimostrata: 0. TP verificati: 0. SL verificati: 0. Outcome verificabili: 0. Win rate e average R: N/D.

### Segnalazioni PRAVDA

- Commento aggiornato su [SPUTNIK PR #138](https://github.com/andreameloni1984-sys/trump-trucker/pull/138#issuecomment-6677840123): gap schedule aggiornati, runtime 14s, test pre-collector non spiegano il ritardo, causa del trigger mancante non determinata.
- Commento aggiornato su [GAGARIN PR #180](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/180#issuecomment-6677840580): gap monitor, quotazioni stale e assenza di telemetria LUBJANKA nel run corrente.

### Conclusione

I dati dimostrano gap reali nelle invocazioni schedule e quotazioni commodity stale. Non dimostrano che la fase di analisi o Telegram richieda un'ora: nei run osservati, dopo l'avvio, SPUTNIK ha completato in circa 14 secondi e GAGARIN in circa 22 secondi. La causa precisa dei trigger schedule mancanti e l'eventuale ritardo di disponibilità delle fonti esterne restano NON DETERMINATI.

PRAVDA non modifica codice, workflow, strategia, filtri, punteggi o rischio. Nessun merge/deploy, ordine reale, modifica secrets/Render o servizio a pagamento. PAPER ONLY.


---

## Addendum PRAVDA — 2026-11-06 06:38 UTC

### 1. GitHub Actions: ultimo run di mercato e gap osservato

Consultata la prima pagina dei 100 run più recenti per ciascun repository; i workflow di test PR e Telegram polling sono stati separati dai collector/monitor di mercato.

**SPUTNIK**
- Workflow live su `main`: `.github/workflows/trump_tracker.yml`, cron `2-59/5 * * * *`.
- Ultimo collector schedulato: [#42157892570](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42157892570), 2026-11-06 03:39:45–03:39:59 UTC, SUCCESS.
- Collector precedente: [#42130911695](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42130911695), 2026-11-05 23:38:20–23:38:32 UTC.
- Gap tra gli avvii: **4h 01m 25s**.
- Al cut-off 06:38:14 UTC non compare un collector schedulato successivo; tempo dall'ultimo avvio: **2h 58m 29s**.
- Il run #42157892570 ha `created_at == run_started_at`: il suo log non dimostra attesa in coda. Non si può attribuire il gap a una causa precisa.
- Il workflow su `main` contiene ancora i due unittest prima della scansione, `concurrency.queue: max`, `cancel-in-progress: false` e persistenza con `git push origin main`.
- La scansione live, una volta avviata, ha richiesto 3.134 ms; intelligence 1.088 ms; notification stage 1.885 ms. Telegram API round-trip 470/468/464 ms per i messaggi 704/705/706. L'API ha accettato i messaggi; non è prova di consegna sul dispositivo.
- Il test step del collector ha eseguito 30 test in 0.033 s. Il message_id 731 compare nel blocco di test e **non** è un nuovo messaggio di mercato.
- Nella parte live: SEC HTTP 403 con cooldown 21.600 s; White House RSS HTTPError; intelligence scan con 2 findings e 1 nuovo evento pubblico. Il post 43491 risulta pubblicato alle 23:18:52 UTC del 5 novembre e osservato nell'output alle 03:39:53.951 UTC del 6 novembre, circa **261 minuti** dopo. GAGARIN cloud handoff disabilitato perché URL/chiave non configurati; `NARWHAL_API_KEY` vuota.

**GAGARIN**
- Workflow live su `main`: `.github/workflows/gagarin-monitor.yml`, cron `*/15 * * * *`, `MONITOR_INTERVAL_MINUTES=15`.
- Ultimo monitor schedulato: [#42152866979](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42152866979), 2026-11-06 02:50:37–02:50:59 UTC, SUCCESS.
- Monitor precedente: [#42122929435](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42122929435), 2026-11-05 22:36:33–22:36:53 UTC.
- Gap tra gli avvii: **4h 14m 04s**.
- Al cut-off 06:38:14 UTC non compare un monitor successivo; tempo dall'ultimo avvio: **3h 47m 37s**.
- Il job è durato circa 22 secondi: il runtime non spiega da solo il gap.
- Il polling Telegram [#42145493753](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42145493753) è un workflow distinto e fallisce con HTTP 409 (webhook attivo); non è un monitor di mercato.

### 2. GAGARIN: prezzi, ranking e Telegram

Il run #42152866979 dichiara **10 strumenti analizzati: 8 commodities operative e 2 Forex ausiliari**. Le otto commodities sono tutte Yahoo STALE:
- Brent 638,9 s;
- WTI 619,8 s;
- Oro 608,7 s;
- Argento 609,6 s;
- Rame 610,7 s;
- Grano 628,9 s;
- Mais 641,0 s;
- Soia 629,1 s.

EUR/USD e GBP/USD sono LIVE su BiQuote (54,7 e 55,6 s), ma sono contesto FX ausiliario e non sostituiscono le quotazioni commodity. Il log non espone i timestamp esatti delle candele né la scadenza dei contratti.

Le otto righe di ranking sono `PAPER_WATCH`, con blocchi di setup/trigger e livelli mancanti. Non risultano entry, SL, TP o ATR operativi. Journal del run: 0 nuove entrate, 0 outcome aggiornati, 0 nuovi feedback e 0 nuove live forecasts. `DATABASE_URL` e `NARWHAL_API_KEY` sono vuoti nel runner, pur essendo abilitati i rispettivi flag.

Telegram API ha accettato un solo WATCH board, message_id **3700**. Il log non conserva il corpo del messaggio. Il formatter `format_watch_board` seleziona al massimo tre candidati in base a bias/score o piano LUBJANKA; pertanto non è possibile ricostruire dal run quali strumenti siano effettivamente comparsi nel messaggio. **Non aggiungo otto record individuali al ledger**: sarebbero attribuzioni non dimostrate. L'API acceptance non prova la consegna sul dispositivo.

Il log non contiene righe di telemetria LUBJANKA. Ciò rende non verificabile dal run se l'interceptor abbia osservato barre, rilevato eventi o scartato dati stale; non prova che il modulo non sia stato eseguito.

### 3. Journal e feedback GAGARIN riletti su main

- `paper_trade_log.csv`: una riga WTI LONG legacy del 2026-10-08, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55; provider, ticker effettivo, timestamp quote, contratto/scadenza ed esito mancanti.
- `data/paper_open.json`: P0001 WTI LONG con gli stessi livelli; è la stessa posizione legacy, non una seconda operazione.
- `journal.csv`: 11 righe del 17 ottobre, tutte “nessun segnale”.
- Root `position.json`: record legacy Heating Oil LONG, HO/USD, aperto 2026-09-15 13:23:44 UTC; entry 4.8844, SL 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882. Non contiene provider, timestamp quote, mercato/contratto, scadenza o prova di esecuzione. Non è lo stesso record WTI P0001.
- `data/position.json`: assente (404).
- `gagarin_feedback.csv`: assente su main (404).
- `commodities_prediction_log.json`: 981 record; ultimo timestamp 2026-09-15 15:45:04 UTC; 21 azioni storiche “COMPRA ORA”, 6 record senza la chiave `operational_signal`. Non sono prove di esecuzione o outcome.

### 4. PR e test recenti — non equivalgono a correzioni in produzione

- SPUTNIK [PR #141](https://github.com/andreameloni1984-sys/trump-trucker/pull/141): OPEN, non merged; CI [#42167340000](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42167340000) SUCCESS, 190 test. Propone di rimuovere i test dal collector live e spostare la persistenza su branch dedicato. Il workflow di `main` resta quello descritto sopra: la correzione non è attiva.
- SPUTNIK [PR #138](https://github.com/andreameloni1984-sys/trump-trucker/pull/138): OPEN e stacked su #137; diagnostica dei gap, non modifica la schedulazione GitHub.
- SPUTNIK [PR #136](https://github.com/andreameloni1984-sys/trump-trucker/pull/136) e [#139](https://github.com/andreameloni1984-sys/trump-trucker/pull/139): OPEN, non integrate; provenienza quote e correzione dei falsi domini restano non attive su main.
- GAGARIN [PR #196](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/196): aggiornata alle 06:25 UTC, OPEN/DRAFT; sette workflow CI SUCCESS, suite integrazione **574 passed**. La modifica restringe l'universo alle otto commodities, ma non è su main e non modifica il cron.
- GAGARIN [PR #180](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/180): OPEN, non merged; propone telemetria LUBJANKA, assente nel log di produzione esaminato.
- GAGARIN [PR #207](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/207): OPEN/DRAFT; 604 test superati sul branch, ma non crea un feed ufficiale né un adapter di quotazione.
- GAGARIN [PR #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): OPEN/DRAFT; persistenza PostgreSQL non verificata. Il run reale mostra `DATABASE_URL` vuoto; il workflow main dichiara che la persistenza sarà riattivata dopo storage privato D1, mentre la PR propone PostgreSQL: la discrepanza resta aperta.

### 5. Segnali, outcome e statistiche

- Ledger invariato: **31 record, 31 firme uniche, zero duplicati**. Il record più recente è già il candidato SPUTNIK GOLD SHORT del run #42157892570, message_id 706.
- GOLD SHORT #706: entry 4059.2, SL 4062.0286, TP1 4056.3713, TP2 4053.5427, ATR 1.8857, stato `EARLY_SETUP / NOT_EXECUTED`. Ticker configurato GC=F, ma provider runtime, timestamp/età quote e scadenza esatta non sono esposti. Outcome: **ESITO NON VERIFICABILE**.
- I prezzi XAUUSD dello screenshot utente sono spot/CFD e non vengono usati per attribuire TP/SL al future continuo.
- Trade con esecuzione dimostrata: **0**; TP verificati: **0**; SL verificati: **0**; outcome verificabili: **0**. Win rate e average R: **N/D**.
- Nessun nuovo segnale distinto aggiunto in questo controllo. Il WATCH board GAGARIN #3700 non è scomposto in record per strumento perché il suo corpo non è conservato nel log.

### 6. Fonti consultate e prossimo controllo

Fonti: cronologia GitHub Actions (prime 100 esecuzioni recenti per repository); job log SPUTNIK #42157892570 e GAGARIN #42152866979; workflow YAML su main; `main.py`, `telegram/signals.py`, `commodities/universe.py`; `paper_trade_log.csv`, `data/paper_open.json`, `journal.csv`, root `position.json`, `commodities_prediction_log.json`; PR #136/#138/#139/#141 SPUTNIK e #180/#196/#202/#207 GAGARIN.

Prossimo controllo:
1. Verificare il primo nuovo collector SPUTNIK e il primo nuovo monitor GAGARIN, senza confondere test PR o polling Telegram con run di mercato.
2. Verificare la freschezza delle otto quotazioni commodity e conservare timestamp quote, ticker effettivo, mercato e scadenza.
3. Verificare se le PR #141, #196 e #180 vengono effettivamente integrate; i test verdi sui branch non sono produzione.
4. Acquisire il corpo/identità per strumento dei WATCH board Telegram, così da non dover inferire i candidati dai soli ranking.
5. Attribuire outcome solo con candele successive dello stesso identico contratto e rispettando la sequenza SL/TP.

**Perimetro:** aggiornamento esclusivamente documentale. Nessuna modifica a codice, workflow, strategia, filtri, punteggi o rischio; nessun merge/deploy, ordine reale, modifica secrets/Render o servizio a pagamento. PAPER ONLY.


---

## PRAVDA addendum — verifica repository e job log 2026-11-06 07:17 UTC

### Limite della cronologia Actions in questo controllo
Il connettore GitHub disponibile in questa sessione consente di leggere i job e i log quando il run ID è noto, ma non espone un'azione per elencare/paginare tutti i workflow run del repository. Ho quindi riletto i due job noti (#42157892570 SPUTNIK e #42152866979 GAGARIN), ma **non posso certificare che siano gli ultimi run schedulati assoluti** né affermare che dopo di essi non ne siano partiti altri. I gap temporali riportati sotto sono riferiti agli ultimi run direttamente verificabili nei materiali già disponibili, non a una lista Actions aggiornata completa.

### SPUTNIK — workflow main e persistenza
- Riletto `.github/workflows/trump_tracker.yml` su main (blob `fb6b635b3730afde76d1332b24ce964780349467`): cron `2-59/5 * * * *`; `concurrency.queue: max`; `cancel-in-progress: false`; i test Telegram/regressione sono ancora eseguiti prima di `python trump_tracker.py`; lo step `Persist SPUTNIK state` esegue ancora `git push origin main`.
- Il commit di produzione `4360e5554b1664c5a8b90e71b79c1d491b87e9ca` (06/11 03:39:54 UTC) è stato riletto: modifica solo `sputnik_state.json`, aggiornato alle 03:39:52 UTC. Conferma che il percorso di persistenza su main è stato effettivamente eseguito dal collector; non è una correzione della cadenza.
- Job #42157892570: SUCCESS. I messaggi 704/705/706 hanno ricevuto conferma API in circa 470/468/464 ms; il processo Python ha impiegato circa 3,134 s, l'intelligence pubblica 1,088 s e la fase notifiche 1,885 s. I test iniziali sono eseguiti nel collector live.
- Il log espone SEC HTTP 403, White House RSS HTTPError e `NARWHAL_API_KEY` vuota. Il post 43491 è stato rilevato circa 261 minuti dopo la pubblicazione. La classificazione `AI_TECH` è errata: il testo è politico/mercato azionario e il match deriva dal frammento "ai" in "AGAIN"; la correzione è proposta in PR #139, ancora OPEN.
- PR #141 e #138 restano OPEN/non integrate; #136 e #139 restano OPEN. PR #138 è diagnostica e non cambia cron/concurrency. Il fatto che il processo noto duri pochi secondi non dimostra la causa dei gap di schedule.

### GAGARIN — workflow, tempi e dati
- Riletto `.github/workflows/gagarin-monitor.yml` su main (blob `24c4852263c06a522a3db7bfa81f46065cb31fcc`): cron `*/15 * * * *`, timeout 10 minuti, monitor completo provider-heavy. La frequenza di cinque minuti non è attiva su main.
- Job #42152866979: SUCCESS. Le otto commodities risultano tutte Yahoo STALE, età 608,7–641,0 secondi; EUR/USD e GBP/USD LIVE su BiQuote sono solo contesto FX ausiliario. Le durate per strumento riportate nel log sono circa 62–869 ms di fetch e 65–872 ms di engine; l'analisi dell'universo è 2.972 ms. Il runtime breve non spiega da solo il gap tra run.
- Il log stampa `DATABASE_URL` vuota in tutte le occorrenze rilevate. Il journal riporta 0 nuove entrate, 0 outcome aggiornati, 0 nuovi feedback e 0 nuove previsioni live. Telegram ha accettato message_id 3700 (round-trip 498 ms); non è prova di consegna sul dispositivo.
- Il corpo del WATCH board 3700 non è conservato nel log: non è possibile attribuire con certezza i singoli strumenti inviati. Non aggiungo otto record dal solo ranking.
- Il codice main contiene la chiamata a LUBJANKA M5, ma il log del monitor non stampa i relativi metadati; lo stato dell'interceptor in quel run resta non verificabile. PR #180 OPEN propone solo telemetria.
- Commit main GAGARIN verificati: `c93906a` (etichetta esplicita del contesto stale LUBJANKA), `409e719` (annotazione dei conflitti direzionali GAGARIN/LUBJANKA) e `7ed290b` (rimozione dei gate intraday FX; non cambia il cron commodity). PR #169 (telemetria analisi) e #170 (round-trip API Telegram) sono MERGED; il round-trip non misura la consegna al dispositivo.
- PR #196, #180, #202 e #207 restano OPEN (alcune DRAFT); i test sui branch non sono correzioni in produzione.

### Riconciliazione journal e ledger
- Il ledger è stato riletto: 31 record, 31 firme uniche, zero duplicati. Ripartizione: 21 historical_prediction_candidate, 5 watch_pre_alert, 4 cfd_early_setup_not_executed, 1 legacy_paper_ticket. Questi 31 record **non sono 31 trade**.
- Il record Heating Oil del prediction log (`Heating Oil|2026-09-15T13:15:00+00:00|LONG|PULLBACK + RIPARTENZA`) ha generazione 13:23:44.529091 UTC e livelli 4.8844/4.5418/5.4473/5.6284/5.882; `position.json` riporta gli stessi livelli e `opened_at` 13:23:44.547184 UTC. Sono artefatti temporalmente e numericamente coincidenti: **non aggiungo una seconda firma**. Il file posizione non prova da solo un fill, né identifica provider/mercato/scadenza.
- Il ticket WTI legacy di `paper_trade_log.csv` e P0001 in `data/paper_open.json` sono la stessa posizione, non due trade; restano senza prova di fill e senza identità contrattuale sufficiente.
- Le 21 previsioni storiche del prediction log non riportano sent timestamp, provider, quote timestamp, mercato e scadenza; 6 non hanno `operational_signal`. Non si usano per calcolare win rate.

### Esito statistico e prossima verifica
- Nuovi segnali distinti dimostrati in questo controllo: 0.
- Trade con fill verificato: 0; TP verificati: 0; SL verificati: 0; outcome verificabili: 0. Win rate e average R: N/D.
- Il GOLD SHORT SPUTNIK #706 resta `NOT_EXECUTED` con `ESITO_NON_VERIFICABILE`: future continuo front-month, expiry e timestamp/provider/età della quote non esposti. Lo screenshot XAUUSD spot non è una serie dello stesso contratto.
- Prossimo controllo: ottenere una lista Actions completa/paginata; verificare il primo run schedulato successivo di ciascun bot; controllare freshness e quote provenance; verificare integrazione reale delle PR; non attribuire outcome senza candele successive dello stesso identico contratto.

**Perimetro:** sola documentazione PRAVDA. Nessun codice/workflow, strategia, filtro, punteggio o rischio modificato; nessun merge/deploy, ordine reale, modifica a secrets/Render o servizio a pagamento. PAPER ONLY.
