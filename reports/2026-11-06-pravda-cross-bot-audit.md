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
