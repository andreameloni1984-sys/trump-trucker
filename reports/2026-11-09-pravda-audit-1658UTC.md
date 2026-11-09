# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
## Controllo #15 — 9 novembre 2026, 17:58 CET (16:58 UTC)

## Esito sintetico

Controllati i run produttivi, i log dei job, i workflow YAML su main, i journal/feedback pubblici, il codice dell'outcome engine e le Pull Request pertinenti.

Due nuove registrazioni sono state aggiunte al ledger, senza duplicare i messaggi collegati:
- SPUTNIK run #295: una sola opportunità GOLD LONG, registrata tramite la card CFD #753; l'analisi #752 è il messaggio compagno.
- GAGARIN run #173: un WATCH pre-alert Telegram #3734 senza corpo conservato e quindi senza attribuzione a uno strumento.

Nessuna delle due è un trade eseguito. Nessun esito SL/TP è verificabile o attribuibile.

## 1. Registro PRAVDA

Ledger precedente letto dal branch `pravda/audit-2026-11-09-1544UTC`: 104 righe dati, 104 firme uniche, 104 source ID unici, nessun duplicato.

Dopo l'aggiunta delle due nuove registrazioni:
- Record totali: 106
- Firme uniche: 106
- Source ID unici: 106
- SPUTNIK: 50
- GAGARIN: 56
- Esiti NON_TRADE: 77
- Esiti ESITO_NON_VERIFICABILE: 29

Le righe nuove hanno firma e Source ID univoci:
- `run:42650624196/telegram_message:753`
- `run:42659137635/telegram_watch_pre_alert:3734`

Le statistiche di performance restano N/D: 0 fill verificati, 0 SL verificati, 0 TP verificati. I record NON_TRADE e le previsioni storiche PENDING non sono operazioni.

## 2. SPUTNIK — collector schedule #295

Run: [SPUTNIK #295](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42650624196)

- Evento: `schedule`
- Avvio: 2026-11-09 16:02:05 UTC
- Fine: 16:02:23 UTC
- Conclusione: SUCCESS
- SHA main: `a9603cadff2ddc2f2a9603c00b014ac56a45c291`
- Cron su main: `2-59/5 * * * *`

La precedente run collector schedulata era #293, avviata alle 06:01:41 UTC. La #294 delle 15:33:04 UTC era `event=push`, non schedule. Il gap tra #293 e #295 è 10h00m24s. Alle 16:58 UTC non risultano run collector schedule successive a #295: è provata una ripresa isolata, non il rispetto continuativo del cron a 5 minuti.

### Fonti e qualità della raccolta

Nel run #295:
- SEC: HTTP 403, cooldown 21.600 secondi;
- filing: 0;
- transazioni: 0;
- White House RSS `https://www.whitehouse.gov/feed/`: HTTPError;
- scansione intelligence pubblica: 6.665 ms, un finding;
- forwarding verso GAGARIN: 0 ms.

Non attribuisco un contenuto specifico al singolo finding perché il log produttivo non ne espone un permalink individuale. I messaggi di test che simulano OSError sulle fonti non sono conteggiati come errori di produzione.

### Nuovo candidato GOLD — messaggi #752/#753

I due messaggi sono collegati alla stessa opportunità e vengono registrati una sola volta tramite #753.

**Analisi #752**
- Strumento logico: GOLD
- Bias: LONG
- Direzione tecnica: LONG 5m
- Momentum 15m: +0,031%
- Notizie direzionali: NO_DIRECTIONAL_NEWS
- Stato: EARLY_BIAS

**Card CFD #753**
- Direzione: LONG
- D-L-A: LONG (ALIGNS)
- Entry: 4129.2998
- SL: 4126.9106
- TP1: 4131.689
- TP2: 4134.0781
- ATR: 1.5928
- Score/priorità: 100
- Stato: NOT_EXECUTED

La precedente contraddizione direzionale osservata nei messaggi GOLD #747/#748 non si ripete in questo run: analisi e D-L-A sono entrambi LONG. Questo non dimostra da solo che la PR #153 sia stata integrata: la PR risulta ancora aperta.

**Limiti bloccanti per l'outcome**
- La card è intitolata CFD ma dichiara future continuo front-month.
- Scadenza esatta non verificata.
- Ticker contrattuale non risolto.
- Provider, timestamp e age della quotazione non esposti.
- Prezzo di riferimento non esposto.
- NARWHAL_NOT_CONFIGURED.
- Indipendenza del controllo SPOT/FUTURES non verificata.
- La card avverte esplicitamente di non usare i livelli.

Telegram API ha confermato l'accettazione di #752 in 590 ms e #753 in 608 ms. È un ACK API, non prova di visualizzazione sul dispositivo e non prova di esecuzione.

La run ha completato il passo di persistenza di `sputnik_state.json`: il log mostra commit `6c3095f` e push su main riuscito. Il contenuto del file non è stato leggibile tramite il connettore in questo controllo; quindi certifico il commit/push del passo, non il contenuto semantico dello stato.

**Classificazione PRAVDA:** NOT_EXECUTED / NON_TRADE. Nessuna candela successiva dello stesso contratto è disponibile; nessun risultato SL/TP attribuito.

## 3. GAGARIN — monitor schedule #173

Run: [GAGARIN Monitor #173](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42659137635)

- Evento: `schedule`
- Avvio: 2026-11-09 16:52:38 UTC
- Fine: 16:53:01 UTC
- Conclusione: SUCCESS
- SHA main: `50b25a80d6792be913c2bcf5a117ede68dd52b59`
- Cron su main: `*/15 * * * *`

La precedente run monitor schedulata era #172 alle 06:34:18 UTC. Il gap è 10h18m20s. La #173 prova una ripresa isolata, non una copertura regolare a 15 minuti.

### Quotazioni del run #173

| Strumento | Provider | Età | Stato |
|---|---|---:|---|
| Rame | YAHOO | 604,7 s | STALE |
| Grano | YAHOO | 604,0 s | STALE |
| WTI | YAHOO | 601,8 s | STALE |
| Mais | YAHOO | 606,1 s | STALE |
| Soia | YAHOO | 603,5 s | STALE |
| Oro | YAHOO | 602,6 s | STALE |
| Brent | YAHOO | 605,0 s | STALE |
| Argento | YAHOO | 626,6 s | STALE |
| EUR/USD | BIQUOTE | 176,2 s | LIVE, contesto non operativo |
| GBP/USD | BIQUOTE | 176,9 s | LIVE, contesto non operativo |

Gli age sono quelli stampati nel run #173, non quotazioni attuali al momento del rapporto. I timestamp assoluti, i ticker provider risolti e le scadenze contrattuali non sono stampati.

### Classifica e autorizzazione

EUR/USD è primo in classifica con LONG, probability 68, quality 57,5, confidence 45, ma è marcato `CONTESTO FX — NON OPERATIVO` e bloccato da trigger non confermato, direction mismatch, RR fail e final confluence fail.

Tutte le otto commodity risultano PAPER_WATCH, con dati stale e senza setup/trigger valido. Entry, SL, TP e ATR non sono disponibili.

Il log conclude:
- NESSUNA ENTRATA AUTORIZZATA;
- Recorded entries: 0;
- Updated open outcomes: 0;
- New feedback signals: 0;
- New additional live forecasts: 0;
- signals=0, open=0, closed=0.

Telegram API ha confermato WATCH pre-alert #3734 in 556 ms. Il corpo del messaggio non è conservato nel log: non attribuisco strumento, direzione, ticker o livelli. La registrazione è quindi un evento WATCH non attribuibile, non un segnale operativo e non un trade.

### Configurazione runtime

Il job #173 mostra:
- PAPER_TRADING_ONLY=1;
- DATABASE_URL vuota;
- MIN_ENTRY_PROBABILITY=40;
- MIN_ENTRY_QUALITY=30;
- MIN_ENTRY_CONFIDENCE=35;
- MIN_ENTRY_RR=2.5;
- MAX_ENTRY_STOP_ATR=2.5.

Nessuna soglia è stata modificata.

## 4. GAGARIN — polling Telegram fallito, difetto già tracciato

Run: [Telegram Polling #20](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42660005021)

- Evento: schedule
- Avvio: 16:58:05 UTC
- Fallimento: 16:58:19 UTC
- Step: `Run polling runner`
- Telegram token validation: SUCCESS
- Telegram diagnostic: SUCCESS
- `getUpdates`: API error 409, webhook attivo; polling non consentito in modalità webhook.

Il conflitto è riprodotto su main. La PR #175 contiene già la gestione specifica `WebhookActiveError`: saltare il polling senza cancellare il webhook e senza ack degli update. È OPEN, non integrata e basata su una revisione precedente di main.

Commento di audit aggiunto alla PR #175: [nuova evidenza run #20](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175#issuecomment-6746165769).

## 5. Journal, feedback e outcome engine GAGARIN

Verifiche sui file main:
- `commodities_prediction_log.json`: 981 record, 981 ID unici, 945 PENDING, 36 NEUTRALE; ultimo record del 15 settembre 2026 alle 15:45:04 UTC.
- `paper_trade_log.csv`: una riga WTI LEGACY_IMPORT del 8 ottobre; provider, contratto, timestamp quote, ATR e outcome mancanti.
- `data/paper_open.json`: WTI P0001 OPEN legacy, P&L null; non è prova di fill.
- `position.json`: vecchia posizione Heating Oil del 15 settembre.
- `journal.csv`: 11 righe del 17 ottobre, tutte “nessun segnale”.
- `gagarin_feedback.csv`: 404, non presente su main.

Il record WTI nel paper_trade_log e P0001 in paper_open riportano gli stessi livelli e sembrano riferirsi allo stesso ticket legacy; non vengono contati come due operazioni. Nessuno dei due ha prova di fill.

Il workflow dichiara che i journal PAPER sono dati privati e non vanno committati nel repository pubblico. Nel run #173 DATABASE_URL è vuota e non sono presenti artifact di run: la persistenza durevole del feedback non è dimostrata.

### Difetto outcome engine confermato su main

Il file `engine/feedback.py` su main:
- definisce campi feedback senza provider, mercato o scadenza contrattuale;
- abbina le serie tramite symbol e timeframe;
- nel caso di una stessa candela che tocca SL e TP, controlla prima `stop_hit` e registra `STOP`.

Questo non soddisfa la regola PRAVDA: quando la sequenza intrabar non è ricostruibile, l'esito deve essere ESITO NON VERIFICABILE; inoltre non è dimostrato il matching dello stesso provider/contratto.

La PR #192 propone parte delle correzioni ma resta OPEN e non integrata. Nessun esito storico è stato ricalcolato.

### Universo

Il file `commodities/universe.py` su main contiene Oro, Argento, Rame, WTI, Brent, Grano, Mais e Soia, oltre a EUR/USD e GBP/USD come contesto ausiliario. Argento è ancora abilitato nel codice e compare nel run #173. La PR #241 è chiusa senza merge; non è una correzione attiva.

## 6. Pull Request e correzioni esistenti

Stato verificato:
- SPUTNIK #153: OPEN, non merged; la contraddizione direzionale non si ripete nel run #295, ma non dichiaro la PR integrata.
- SPUTNIK #154: OPEN, non merged; classificazione tariffaria S.5653 ancora da verificare in una nuova produzione con item individuale.
- SPUTNIK #155: OPEN, non merged; diagnostica cadence proposta ma non attiva su main.
- GAGARIN #175: OPEN, non merged; fix del conflitto webhook/polling già proposto.
- GAGARIN #192: OPEN, non merged; outcome/exact-contract fix non attivo su main.
- GAGARIN #202: OPEN DRAFT; persistenza PostgreSQL proposta, non attiva.
- GAGARIN #225: OPEN DRAFT; cron offset non attivo.
- GAGARIN #239 e #242: OPEN DRAFT; identità CFD/scadenza non attiva.
- GAGARIN #243: OPEN DRAFT; rimozione runtime Trading 212 proposta, non integrata.
- GAGARIN #241: CLOSED senza merge; Argento resta attivo su main.

Commenti di audit aggiunti, senza modifiche al codice:
- SPUTNIK PR #155: [gap tra collector schedule #293 e #295](https://github.com/andreameloni1984-sys/trump-trucker/pull/155#issuecomment-6746164936).
- GAGARIN PR #175: [polling 409 su run #20](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175#issuecomment-6746165769).
- GAGARIN issue #186: [gap tra monitor #172 e #173](https://github.com/andreameloni1984-sys/commodity-news-scanner/issues/186#issuecomment-6746166793).

## 7. Statistiche e classificazione

Campione di operazioni eseguite e verificabili: 0.

- Win rate: N/D.
- Average R: N/D.
- Total R: N/D.
- Fill verificati: 0.
- SL verificati: 0.
- TP verificati: 0.

I due nuovi record sono NON_TRADE:
- GOLD #753: NOT_EXECUTED, livelli non utilizzabili e contratto non identificato.
- GAGARIN #3734: WATCH pre-alert senza corpo conservato, non attribuibile.

Non sono state scaricate o confrontate candele successive per questi eventi: mancano ticker/provider/scadenza sufficienti a garantire lo stesso identico strumento e contratto.

## 8. Fonti consultate

- GitHub Actions SPUTNIK run #295 e job log.
- GitHub Actions GAGARIN monitor #173 e job log.
- GitHub Actions GAGARIN Telegram Polling #20 e job log.
- Workflow YAML main: `.github/workflows/trump_tracker.yml`, `.github/workflows/gagarin-monitor.yml`, `.github/workflows/telegram-polling.yml`.
- File main: `sputnik_state.json` (passo di commit/push confermato dal log; contenuto non leggibile dal connettore), `commodities_prediction_log.json`, `paper_trade_log.csv`, `data/paper_open.json`, `position.json`, `journal.csv`, `engine/feedback.py`, `commodities/universe.py`, `telegram/polling_runner.py`.
- PR e discussioni #153, #154, #155, #175, #192, #202, #225, #239, #241, #242, #243; issue #186.

Nessun servizio a pagamento, nessun feed Trading212, nessun ordine reale. Gli ACK Telegram sono trattati soltanto come accettazione API, non come consegna sul dispositivo.

## 9. Prossimo controllo

1. Verificare la prossima run schedule SPUTNIK dopo #295 e misurare il gap reale.
2. Verificare la prossima run GAGARIN dopo #173 e controllare se le otto commodity diventano fresche.
3. Verificare la gestione del webhook 409 dopo l'eventuale integrazione della PR #175.
4. Controllare se il journal privato acquisisce una persistenza verificabile; oggi DATABASE_URL è vuota e non ci sono artifact.
5. Richiedere per ogni candidato ticker provider, timestamp quote, market type e scadenza esatti.
6. Non classificare SL/TP senza candele successive dello stesso provider e dello stesso contratto; doppio tocco intrabar resta ESITO NON VERIFICABILE.
7. Verificare le PR esistenti senza duplicare commenti o modificare strategia, filtri, score o rischio.

---

**PRAVDA — PAPER ONLY.** Nessun codice applicativo modificato, nessun merge, deploy, ordine reale, intervento su secret o Render.
