# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-09 03:27:11 UTC (04:27:11 Europe/Rome)**

## Sintesi

Audit eseguito leggendo le ultime 100 run Actions disponibili per ciascun repository, i log completi dei job produttivi più recenti, workflow su `main`, ledger PRAVDA, archivio previsioni, journal pubblici e PR aperte.

**Nessuna nuova esecuzione produttiva dopo SPUTNIK #292, polling #52 e GAGARIN #171 è presente nell'elenco delle run consultato. Nessun nuovo segnale da aggiungere al ledger.** Le ultime notifiche restano SPUTNIK #743/#744/#745 e GAGARIN #3727; sono già registrate.

Nuova evidenza rilevante: SPUTNIK #292 ha generato la coppia GOLD #743/#744 dopo un finding TRUTH_ARCHIVE di tipo page-level, senza titolo, data di pubblicazione o permalink individuale. La PR #150 aggiunge ora un controllo item-level per impedire che snapshot generici riattivino raccomandazioni basate sulla cronologia; è testata, ma non integrata.

## 1. Ledger e integrità

Ledger cumulativo ereditato e ricontrollato: [pravda-signal-ledger-2026-11-09.csv](pravda-signal-ledger-2026-11-09.csv).

SHA blob: `a5211b7e5515860443f3860b374e294cd7465bca`.

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

Nessuna riga aggiunta: #743, #744, #745 e #3727 sono già presenti. Le PR e le CI non sono segnali e non generano righe di trade.

Win rate, average R e total R: **N/D**, perché il campione di fill verificati è zero.

### Completezza campi (98 record misti; i campi non sono applicabili a tutti i messaggi)

Valori vuoti o marcati NOT_RECORDED / NOT_EXPOSED / NOT_ATTRIBUTABLE / NOT_APPLICABLE / UNKNOWN:
- timestamp invio non utilizzabile: 32;
- ticker non utilizzabile: 65;
- market type non utilizzabile: 80;
- scadenza esatta non utilizzabile: 98;
- provider non utilizzabile: 50;
- timestamp quotazione non utilizzabile: 96;
- entry, SL e TP1 non valorizzati: 69 ciascuno;
- ATR non valorizzato: 85.

Questi conteggi includono messaggi informativi e NON_TRADE: non vanno letti come 98 setup operativi incompleti. Per ogni segnale operativo, tuttavia, l'identità del contratto e la provenienza della quotazione devono essere esplicite.

## 2. SPUTNIK — ultima produzione e segnali

Run [#292](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537803167), job `128905894291`, SUCCESS. Avvio run 2026-11-08 23:59:46 UTC; completamento 23:59:58 UTC. Il log del job va da 23:59:49 a 23:59:56 UTC.

### Finding e fonti

La PR #150 documenta il finding:
- event_id `14206ad67f74de2585209e6c`;
- evidenza `PUBLIC_SOURCE_TEXT_PAGE_LEVEL`;
- URL `https://www.trumpstruth.org/`;
- titolo e published timestamp vuoti;
- nessun permalink individuale;
- rilevamento `2026-11-08T23:59:52.394955Z`.

Il finding è uno snapshot di pagina, non un singolo post RSS datato. La coppia GOLD #743/#744 è stata comunque generata. È il difetto che la PR #150 tenta di chiudere.

Nel runtime #292:
- SEC: HTTP 403, cooldown 21.600 secondi; filings 0.
- White House RSS: HTTPError sull'endpoint `https://www.whitehouse.gov/feed/`.
- Public intelligence scan: 1 finding.
- Il messaggio #743 riporta `NO_DIRECTIONAL_NEWS`.
- Le righe OSError WHITE_HOUSE/TRUTH_ARCHIVE/OGE compaiono nello step dei test prima dell'avvio di `trump_tracker.py`: non sono conteggiate come errori del collector runtime.

### Messaggi effettivi

| ID Telegram | Generazione UTC | Accettazione API UTC | Contenuto | Classificazione PRAVDA |
|---|---|---|---|---|
| #743 | 23:59:54.8425373 | 23:59:54.8438627 | GOLD, SHORT preliminare; momentum 5m -0,061%; nessuna notizia direzionale | NON_TRADE |
| #744 | 23:59:54.8439129 | 23:59:54.8449792 | GOLD EARLY_SETUP SHORT | NOT_EXECUTED / NON_TRADE |
| #745 | 23:59:54.8450509 | 23:59:54.8454315 | Brief giornaliero informativo | NON_TRADE |

Round-trip API: 401 ms (#743), 396 ms (#744), 364 ms (#745). È prova di accettazione API, non di visualizzazione sul dispositivo.

**#744 — livelli registrati, ma non verificabili come trade**
- Entry 4069.1001
- SL 4071.9929
- TP1 4066.2073
- TP2 4063.3145
- ATR 1.9285
- Stato esplicito: `NOT_EXECUTED`.

Il titolo dichiara CFD, il corpo dichiara future continuo front-month e avverte che scadenza esatta e indipendenza upstream non sono verificate. Ticker risolto, provider, timestamp/età della quotazione e scadenza non sono disponibili. D-L-A è riportato NEUTRAL / NO_DIRECTION / NOT_ASSESSED. Non è possibile controllare se entry o livelli fossero già superati, né cercare SL/TP successivi dello stesso contratto. Score 100 non prova validità operativa.

**#745 — etichetta oraria**
Il brief è stato accettato alle 23:59:54 UTC (00:59:54 CET), ma il titolo nel log è `BRIEF ORE 05:00`. [Issue #151](https://github.com/andreameloni1984-sys/trump-trucker/issues/151) è ancora OPEN. [PR #152](https://github.com/andreameloni1984-sys/trump-trucker/pull/152) cambia il titolo in BRIEF GIORNALIERO; non è integrata.

### Correzioni SPUTNIK

- [PR #150](https://github.com/andreameloni1984-sys/trump-trucker/pull/150): OPEN, non draft; 1 commit avanti / 0 indietro rispetto a main; head `1b4b92ed84094e9d22ace456987bddb94a65eec2`. CI head 2026-11-09 02:58:19 UTC: ranking #651 SUCCESS (185 test) e item-intelligence #261 SUCCESS (46 test), totale 231. Il diff estrae la stessa eleggibilità item-level del digest e impedisce la coppia recommendation/CFD se lo scan contiene solo page-level o record senza permalink. Non aggiunge fonti, score, mapping o rischio. Non è integrata.
- [PR #152](https://github.com/andreameloni1984-sys/trump-trucker/pull/152): OPEN, non draft; 3 avanti / 0 indietro; CI #650 e #260 SUCCESS (185 + 46). Solo etichetta/docstring e regressione; non integrata.
- [PR #131](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): endpoint White House alternativo proposto, non integrato; il runtime #292 usa ancora `/feed/` e registra HTTPError.
- [PR #147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): separazione dal handoff GAGARIN ancora OPEN.
- [PR #144](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): persistenza separata ancora OPEN. Il workflow main mantiene `contents: write` e committa `sputnik_state.json` su main; ultimo commit main osservato `15f34dfe1e9866755bc2604e58ce8b582e34b5ac` (23:59:54 UTC).

Workflow [SPUTNIK](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/trump_tracker.yml): cron `2-59/5 * * * *`. Ultima run schedule consultata #292 alle 23:59:46 UTC. Nessuna successiva run schedule nel listing delle ultime 100 Actions.

Workflow [Telegram polling](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/telegram-polling.yml): cron ogni 5 minuti. Ultima run schedule consultata #52, avviata 23:56:54 UTC e completata 23:57:02 UTC.

## 3. GAGARIN — ultima produzione, quotazioni e journal

Run [#171](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42538235058), job `128907219566`, SUCCESS. Avvio 2026-11-09 00:04:51 UTC; completamento 00:05:10 UTC. Il job mostra `DATABASE_URL` vuota in tutti gli step consultati.

### Quotazioni osservate nel job #171

| Strumento | Provider | Età al controllo | Stato |
|---|---|---:|---|
| Oro | YAHOO | 611,0 s | STALE |
| Argento | YAHOO | 655,0 s | STALE |
| Rame | YAHOO | 643,1 s | STALE |
| WTI | YAHOO | 604,2 s | STALE |
| Brent | YAHOO | 605,4 s | STALE |
| Grano | YAHOO | 189.906,5 s | STALE |
| Mais | YAHOO | 189.909,6 s | STALE |
| Soia | YAHOO | 189.906,8 s | STALE |
| EUR/USD | BIQUOTE | 6,3 s | LIVE, contesto non operativo |
| GBP/USD | BIQUOTE | 6,9 s | LIVE, contesto non operativo |

Le età sono riportate dal job; per le commodity non sono disponibili nel riepilogo ticker provider risolto, timestamp assoluto della candela, mercato e scadenza esatta. Le due coppie Forex sono esplicitamente marcate come contesto, non operative.

WTI compare LONG nella classifica come `PAPER_WATCH`, non come ingresso. Il motore riporta:
- Recorded entries: 0;
- New feedback signals: 0;
- New additional live forecasts: 0;
- `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`.

Telegram #3727 è stato accettato dall'API in 403 ms; il corpo del messaggio non è conservato, quindi strumento, direzione e livelli non sono attribuibili.

### Journal e archivio

- `commodities_monitor_state.json`: timestamp interno `2026-09-17T03:44:02.566153+00:00`, best Benzina RBOB, LONG ma action ATTENDERE ed entry_state BLOCKED.
- `commodities_prediction_log.json`: 981 record; ultimo `created_at` `2026-09-15T15:45:04.462276+00:00`. Status: 945 PENDING, 36 NEUTRALE. Action: 21 COMPRA ORA, 292 LONG — ASPETTARE CONFERMA, 15 SHORT — ASPETTARE CONFERMA, 576 ATTENDERE, 77 NON ENTRARE. Sei record non hanno `operational_signal`. Nessun record è prova di fill.
- `journal.csv`: 11 righe del 17 ottobre, tutte con esito “nessun segnale”.
- `paper_trade_log.csv`: un WTI LONG `LEGACY_IMPORT`, OPEN, entry 96.24, stop 89.37, TP1 103.11; provider, ticker feed, timestamp quote, mercato/scadenza ed esito assenti.
- `data/paper_open.json`: P0001 WTI LONG OPEN con gli stessi livelli legacy; PnL null.
- `position.json`: vecchia posizione Heating Oil LONG, entry 4.8844, stop 4.5418, TP1 5.4473, aperta il 15 settembre. Nessuna prova di fill o riconciliazione con il monitor #171.
- `gagarin_feedback.csv`: 404, assente dal repository pubblico. Il workflow monitor dichiara che il journal privato non va committato e che la persistenza sarà riattivata solo dopo deploy e verifica dello storage privato.

Questi artefatti legacy non vengono conteggiati come trade verificati. La variabile DATABASE_URL è vuota nel job #171; ciò prova il valore vuoto in quella run, non lo stato generale di ogni secret/account.

### PR GAGARIN

- [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, 6 avanti / 6 indietro rispetto a main. Main `engine/feedback.py` non ha il matching completo provider/ticker/mercato/contratto e la documentazione del modulo dice che il doppio tocco intrabar viene risolto come STOP. Il branch PR aggiunge il caso stesso-bar SL+TP come ESITO NON VERIFICABILE e confronta ticker, market type e identità futures, ma `_market_contract_match` non confronta il provider del segnale con quello della serie successiva. Il rilievo provider è già presente nei commenti #6706619879 e #6725075554: nessun commento duplicato aggiunto.
- [PR #238](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/238) e [PR #239](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/239): entrambe DRAFT e stacked; separano app symbol, ticker/slug catalogo, feed symbol e richiedono prova esplicita di tipo contratto e scadenza. La PR #239 richiede anche evidenza esplicita di no-expiry. Il registry rimane vuoto; nessun quote adapter/feed CFD è implementato. Le CI dei rispettivi head risultano SUCCESS, ma non sono merge né accesso a Trading 212.
- [PR #221](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): DRAFT, 14 avanti / 3 indietro rispetto a main. Propone di rimuovere EUR/USD e GBP/USD dalle route del motore, lasciando le otto commodity. Le otto run CI sul relativo head SHA sono SUCCESS ma risalgono al 6 novembre; non sono una nuova validazione del 9 novembre. Main continua a mostrare 10 strumenti, incluse le due coppie Forex ausiliarie.
- [PR #234](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/234) e [PR #235](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/235): DRAFT e non integrate; journal CFD PAPER e persistenza durevole non dimostrati su main.

Workflow [GAGARIN monitor](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml): cron `*/15 * * * *`, permessi contents: read; il commento workflow dichiara che il journal privato non viene committato.

## 4. Continuità delle scansioni

Cut-off 03:27:11 UTC:

| Processo | Cron main | Ultima run schedule consultata | Gap al cut-off |
|---|---|---|---:|
| SPUTNIK collector | ogni 5 min | #292, 23:59:46 UTC | 3h27m25s |
| SPUTNIK polling | ogni 5 min | #52, 23:56:54 UTC | 3h30m17s |
| GAGARIN monitor | ogni 15 min | #171, 00:04:51 UTC | 3h22m20s |

Le ultime 100 run Actions per ciascun repository non mostrano successive run schedule. Le CI delle PR sono eventi pull_request/push e non scansioni produttive. La causa dei gap non è dimostrata; non viene attribuita a un filtro o a una causa specifica.

## 5. Esiti, statistiche e lacune

- Fill verificati: 0.
- SL prima verificato: 0.
- TP prima verificato: 0.
- ESITO NON VERIFICABILE: 29 record storici/candidati senza identità contrattuale e percorso prezzi sufficienti.
- NON_TRADE: 69 notifiche, WATCH, bias preliminari, previsioni non eseguite e messaggi informativi.

Nessun backtest è stato eseguito o inventato. Non sono stati cercati prezzi spot/futures sostitutivi per colmare ticker, provider o scadenze mancanti. Nessun livello #744 è stato classificato come già raggiunto o superato: manca una serie esatta confrontabile.

## 6. Fonti consultate

- SPUTNIK [Actions #292](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537803167), [polling #52](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537592091), workflow collector e polling su main.
- SPUTNIK [PR #150](https://github.com/andreameloni1984-sys/trump-trucker/pull/150), [PR #152](https://github.com/andreameloni1984-sys/trump-trucker/pull/152), [PR #131](https://github.com/andreameloni1984-sys/trump-trucker/pull/131), [Issue #151](https://github.com/andreameloni1984-sys/trump-trucker/issues/151), PR #147 e #144.
- GAGARIN [Actions #171](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42538235058), workflow monitor, `commodities_monitor_state.json`, `commodities_prediction_log.json`, `journal.csv`, `paper_trade_log.csv`, `data/paper_open.json`, `position.json`, `engine/feedback.py`.
- GAGARIN [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192), [PR #221](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221), [PR #238](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/238), [PR #239](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/239), PR #234 e #235.

## 7. Prossimo controllo

1. Verificare se riprendono le run schedule, distinguendole dalle CI.
2. Controllare la prima scansione SPUTNIK con un item RSS individuale datato e permalink, e verificare l'effetto della PR #150 solo dopo eventuale merge.
3. Verificare la prima quotazione commodity fresca di GAGARIN con ticker risolto, provider, timestamp assoluto, market type e scadenza.
4. Verificare se #192 aggiunge il confronto provider esplicito e se la correzione stesso-bar è effettivamente su main.
5. Verificare la scrittura e rilettura del journal privato prima di considerare ripristinata la persistenza.
6. Aggiungere al ledger solo nuovi messaggi/segnali con ID/firma univoci; nessun outcome senza candele successive dello stesso identico contratto.

**Perimetro rispettato:** audit e documentazione soltanto. Nessuna modifica a codice, strategia, filtri, score o rischio; nessun merge/deploy, ordine reale, modifica secret/Render o servizio a pagamento. PAPER ONLY.
