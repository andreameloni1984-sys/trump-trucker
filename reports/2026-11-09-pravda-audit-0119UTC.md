# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-09 01:19:53 UTC (02:19:53 Europe/Rome)**

## Sintesi

Audit svolto sui due repository, sulle ultime GitHub Actions schedulate, sui job log completi, sui workflow, sul ledger PRAVDA, sugli artefatti journal/feedback e sulle PR aperte.

**Nessuna nuova run produttiva è comparsa dopo SPUTNIK #292 e GAGARIN #171.** Le esecuzioni più recenti visibili sono test di PR, non scansioni di mercato. Non sono emersi nuovi segnali da aggiungere al ledger.

Il nuovo elemento tecnico è GAGARIN PR #239: aggiunge una verifica esplicita delle prove sul tipo di contratto e sulla scadenza. È ancora DRAFT, impilata su PR #238, senza registry popolato né feed quotazioni. I test associati sono SUCCESS, ma non è una correzione in produzione.

## 1. Ledger e integrità

Ledger cumulativo ereditato dal precedente branch:
[pravda-signal-ledger-2026-11-09.csv](pravda-signal-ledger-2026-11-09.csv)

SHA blob del CSV: `a5211b7e5515860443f3860b374e294cd7465bca`.

| Indicatore | Valore |
|---|---:|
| Record | 98 |
| SPUTNIK | 45 |
| GAGARIN | 53 |
| Firme uniche | 98 |
| Source ID unici | 98 |
| Duplicati firma | 0 |
| Duplicati source ID | 0 |
| NON_TRADE | 69 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |

Le ultime quattro registrazioni restano SPUTNIK #743, #744, #745 e GAGARIN #3727, tutte già presenti. Nessuna nuova riga è stata aggiunta e il CSV non è stato modificato.

Le statistiche di performance restano N/D: non esiste un campione di fill verificati. Nessun esito può essere ricavato da prezzi spot, futures continui o contratti con scadenza non identificata.

## 2. GitHub Actions — continuità

### SPUTNIK
- Ultima run schedulata: [#292](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537803167), ID `42537803167`, SUCCESS.
- Avvio: 2026-11-08 23:59:46 UTC; completamento: 23:59:58 UTC.
- Ultimo polling schedulato: [#52](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537592091), ID `42537592091`, SUCCESS, avvio 23:56:54 UTC.
- Al cut-off: collector fermo da circa **1h20m07s**; polling da **1h22m59s**.
- Workflow su main: cron `2-59/5 * * * *`.

### GAGARIN
- Ultimo monitor schedulato: [#171](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42538235058), ID `42538235058`, SUCCESS.
- Avvio: 2026-11-09 00:04:51 UTC; completamento: 00:05:10 UTC.
- Al cut-off: monitor fermo da circa **1h15m02s**.
- Workflow su main: cron `*/15 * * * *`.

Le run PR più recenti — SPUTNIK test alle 23:36 UTC e GAGARIN test alle 01:11 UTC — non sono monitor produttivi. L'assenza di nuove run schedulate è quindi confermata dalla prima pagina dei run recenti; la causa del gap non è dimostrata.

## 3. SPUTNIK — run #292 e messaggi

Job log: [SPUTNIK #292](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537803167), job ID `128905894291`.

### Runtime effettivo
Le righe OSError e i messaggi di conferma GAGARIN presenti prima di `python trump_tracker.py` appartengono ai test automatici, non al collector runtime. Nel runtime:
- SEC: HTTP 403; cooldown registrato 21.600 secondi.
- Filing: 0.
- Transazioni: 0.
- White House RSS: HTTPError sull'endpoint `https://www.whitehouse.gov/feed/`.
- Intelligence scan: 1 finding; il messaggio GOLD dichiara `NO_DIRECTIONAL_NEWS`.
- GAGARIN forwarding: 0 ms; URL e API key di handoff vuote nell'ambiente della run.

### Messaggi
**#743 — GOLD EARLY_BIAS**
- Generazione: 23:59:54.8425373 UTC.
- API Telegram accepted: 23:59:54.8438627 UTC; round-trip 401 ms.
- Bias SHORT preliminare, tecnica SHORT 5m, momentum riportato -0,061% negli ultimi 15 minuti.
- Notizie direzionali: assenti.
- Nessun ticker risolto, mercato/scadenza, provider, timestamp della quotazione, entry, SL, TP o ATR.
- Stato: ipotesi preliminare, non ingresso confermato; NON_TRADE.

**#744 — GOLD EARLY_SETUP**
- Generazione: 23:59:54.8439129 UTC.
- API Telegram accepted: 23:59:54.8449792 UTC; round-trip 396 ms.
- Direzione stampata SHORT; D-L-A simultaneamente NEUTRAL / NO_DIRECTION / NOT_ASSESSED.
- Entry 4069.1001; SL 4071.9929; TP1 4066.2073; TP2 4063.3145; ATR 1.9285.
- Stato esplicito: `NOT_EXECUTED`; score 100/100 non è validità operativa.
- Titolo: analisi CFD; corpo: future continuo front-month. Scadenza esatta, ticker risolto, provider e timestamp della quotazione assenti; NARWHAL non configurato; indipendenza del controllo spot/futures non verificata.
- I livelli sono conservati come valori stampati, ma non sono utilizzabili per un outcome: manca l'identità esatta della serie/contratto e non sono disponibili candele successive corrispondenti.
- Classificazione: NON_TRADE, non STOP e non TP.

**#745 — brief informativo**
- Generazione: 23:59:54.8450509 UTC.
- API Telegram accepted: 23:59:54.8454315 UTC; round-trip 364 ms.
- Etichetta `BRIEF ORE 05:00`, ma invio alle 23:59:54 UTC (00:59:54 Europe/Rome).
- Non è un segnale di mercato.
- [Issue #151](https://github.com/andreameloni1984-sys/trump-trucker/issues/151) è aperta e documenta la discrepanza dell'etichetta oraria.

Per tutti e tre gli ACK, il log prova l'accettazione dell'API Telegram, non la visualizzazione sul dispositivo.

### Persistenza SPUTNIK su main
Il workflow attuale ha `permissions: contents: write` e uno step `Persist SPUTNIK state` che committa `sputnik_state.json` direttamente su main. Il job #292 ha effettivamente creato e spinto il commit `15f34dfe1e9866755bc2604e58ce8b582e34b5ac` alle 23:59:56 UTC. È una persistenza di stato automatica del bot, non un intervento PRAVDA sul codice. Le PR di persistenza fuori da main restano aperte.

## 4. GAGARIN — run #171, dati e journal

Job log: [GAGARIN #171](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42538235058), job ID `128907219566`.

### Quotazioni e blocchi
La run analizza 8 commodity operative più EUR/USD e GBP/USD ausiliari.

| Strumento | Provider | Età registrata | Esito dati |
|---|---|---:|---|
| Oro | YAHOO | 611 s | STALE |
| Argento | YAHOO | 655 s | STALE |
| Rame | YAHOO | 643 s | STALE |
| WTI | YAHOO | 604 s | STALE |
| Brent | YAHOO | 605,4 s | STALE |
| Grano | YAHOO | 189.906,5 s | STALE |
| Mais | YAHOO | 189.909,6 s | STALE |
| Soia | YAHOO | 189.906,8 s | STALE |
| EUR/USD | BIQUOTE | 6,3 s | LIVE |
| GBP/USD | BIQUOTE | 6,9 s | LIVE |

Tutte le commodity sono bloccate da `LIVE_DATA_NOT_FRESH`; mancano setup/trigger validi e livelli operativi. EUR/USD e GBP/USD hanno quote fresche ma sono classificati `CONTESTO FX — NON OPERATIVO`, con trigger non confermato, mismatch direzionale e RR insufficiente. La classifica non equivale ad autorizzazione.

La run dichiara:
- Recorded entries: 0.
- Updated open outcomes: 0.
- New feedback signals: 0.
- New additional live forecasts: 0.
- `signals=0 open=0 closed=0`.

Messaggio #3727: Telegram API accepted alle 00:05:07.2828735 UTC, round-trip 403 ms; corpo non conservato, quindi strumento, ticker, direzione e livelli non attribuibili. Non è un trade.

### Journal e archivio
- `DATABASE_URL` è vuota nel job #171.
- Il workflow `gagarin-monitor.yml` dichiara che i journal sono dati operativi privati e non devono essere committati nel repository pubblico; la persistenza verrà riattivata solo dopo storage privato verificato.
- `journal.csv`: 11 righe del 17 ottobre, tutte senza segnale.
- `paper_trade_log.csv`: un WTI LONG `LEGACY_IMPORT` del 8 ottobre, senza esito e senza prova di fill.
- `position.json`: vecchia posizione Heating Oil LONG aperta il 15 settembre; non è riconciliata con un fill verificato.
- `commodities_prediction_log.json`: 981 ID unici; ultimo `created_at` 2026-09-15 15:45:04 UTC. Stati: 945 PENDING, 36 NEUTRALE. Azioni: 21 COMPRA ORA (tutte PENDING), 292 LONG attendere conferma, 15 SHORT attendere conferma, 576 ATTENDERE, 77 NON ENTRARE. Campo `operational_signal`: 960 WAIT, 15 LONG, 6 assente.
- Nessuno di questi record storici dimostra un ordine o un fill. Le 21 etichette COMPRA ORA non vengono convertite in trade retroattivi.

Argento è ancora presente nel monitor completo su main. PR #223, ancora DRAFT, propone un monitor M5 osservativo separato a sette strumenti senza Argento; non rimuove Argento dal monitor completo. PR #221 per rimuovere le route Forex è anch'essa aperta/DRAFT; il monitor main continua a stampare le due coppie ausiliarie.

## 5. Outcome engine — difetto confermato

Su main, `engine/feedback.py` conserva il vecchio schema: la firma non contiene provider/ticker di quotazione/mercato/scadenza e il codice tratta il doppio tocco SL+TP nella stessa candela in modo conservativo come STOP. Questo non soddisfa il protocollo PRAVDA, che richiede `ESITO NON VERIFICABILE` quando l'ordine intrabar non è conoscibile.

PR #192 è OPEN, non integrata; confronto con main corrente: 6 commit avanti e 6 indietro. Sul branch la firma include provider, quote symbol, market type e identità contratto, e il doppio tocco diventa `ESITO NON VERIFICABILE`. Tuttavia `_market_contract_match()` confronta quote symbol, market type e, per futures, mese/scadenza, ma **non confronta esplicitamente il provider della serie successiva con il provider del segnale**. Il difetto già segnalato resta quindi valido.

## 6. PR e correzioni già esistenti

### SPUTNIK
- [PR #150](https://github.com/andreameloni1984-sys/trump-trucker/pull/150): OPEN, non draft; 2 commit avanti e 2 indietro rispetto al main corrente. Propone di non ripetere il recommender senza un nuovo item RSS eleggibile. Le CI sul suo head risultano SUCCESS (46 test intelligence + 185 ranking), ma la PR non è integrata.
- [PR #131](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): OPEN, non draft; 1 avanti e 1 indietro. Propone il nuovo endpoint White House `/news/feed/`; CI SUCCESS (45 + 184). Il runtime #292 usa ancora `/feed/` e registra HTTPError: la correzione non è in produzione.
- [PR #147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN; 1 avanti e 9 indietro. Separazione GAGARIN non integrata.
- [PR #145](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN; 1 avanti e 11 indietro. Diagnostica/provenienza quotazioni non integrata.
- [PR #144](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): persistenza separata ancora aperta.
- [Issue #151](https://github.com/andreameloni1984-sys/trump-trucker/issues/151): discrepanza etichetta brief ancora aperta.

### GAGARIN
- [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN; 6 avanti/6 indietro; correzione outcome non integrata e provider match incompleto.
- [PR #239](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/239): OPEN/DRAFT, 2 commit avanti rispetto alla base #238. Richiede prove esplicite per tipo contratto e scadenza, anche per SPOT/no-expiry. Le CI sul head 7a7218a risultano SUCCESS: SOYUZ GAGARIN #1960 e Execution Layer #3833. Il registry resta vuoto; non viene aggiunto un feed o una quotazione.
- [PR #238](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/238) e #237: OPEN/DRAFT, separano app symbol, catalogue ticker/slug e feed symbol; nessuna voce verificata nel registry.
- [PR #234](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/234) e [PR #235](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/235): OPEN/DRAFT, journal CFD PAPER isolato e persistenza durevole non integrati.
- [PR #225](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225): OPEN/DRAFT, offset del cron monitor; main conserva `*/15`.
- [PR #223](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): OPEN/DRAFT, M5 osservativo a sette strumenti; non è un segnale né un feed CFD.
- [PR #222](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222): MERGED; rimosso il veto intraday `session_ok`, ma restano i controlli indipendenti di mercato, freschezza, trigger, RR e rischio.

## 7. Esiti e statistiche

- Nuovi segnali operativi: 0.
- Nuovi fill verificati: 0.
- Nuovi esiti SL/TP: 0.
- Nuovi esiti non verificabili aggiunti: 0.
- Campione verificabile: 0.

Non è possibile classificare #744 con i prezzi successivi perché il messaggio non identifica un ticker/contratto/scadenza/provider esatti. Non sono stati usati prezzi spot generici, futures continui o scadenze differenti come surrogati.

## 8. Fonti consultate

- GitHub Actions SPUTNIK #292 e Telegram Polling #52, con log job completi.
- GitHub Actions GAGARIN #171, con log job completo.
- Workflow main: `.github/workflows/trump_tracker.yml` e `.github/workflows/gagarin-monitor.yml`.
- Ledger PRAVDA cumulativo e rapporto precedente.
- `commodities_prediction_log.json`, `journal.csv`, `paper_trade_log.csv`, `position.json`.
- `engine/feedback.py` su main e sul branch PR #192.
- Metadati, confronti commit e CI delle PR elencate sopra.
- Issue SPUTNIK #151.

## 9. Prossimo controllo

1. Verificare la prima nuova run schedulata di SPUTNIK e GAGARIN; distinguere sempre schedule run da CI PR.
2. Verificare se SPUTNIK #150 e #131 vengono aggiornate/integrate e se il runtime recupera davvero il nuovo RSS.
3. Controllare l'evoluzione di GAGARIN #192 e #239, senza confondere test superati con produzione.
4. Attendere quotazioni commodity fresche con provider, timestamp, ticker, mercato e scadenza espliciti.
5. Verificare persistenza del journal solo con prova effettiva di scrittura e successiva lettura.
6. Aggiungere al ledger soltanto nuovi record identificabili; valutare outcome solo con candele successive dello stesso identico contratto.

**Sicurezza:** nessun codice applicativo, strategia, filtro, punteggio o rischio modificato da PRAVDA; nessun merge, deploy, ordine reale, modifica a secret o Render; nessun servizio a pagamento. Nessun accesso a Trading 212 o consegna Telegram al dispositivo dichiarati. PAPER ONLY.
