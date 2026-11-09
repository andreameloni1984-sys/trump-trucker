# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-09 12:41:05 UTC (13:41:05 CET)**

## Perimetro e metodo

Verifica in sola lettura tramite GitHub REST: elenco delle ultime 100 Actions per repository, metadati e job delle ultime run schedulate, PR e relativi check, file su `main`, ledger PRAVDA precedente e artefatti pubblici. Nessun log ZIP/artifact è disponibile per le due run produttive esaminate; i job espongono gli step ma non il contenuto completo del log. Non vengono quindi ripetuti come nuovi fatti gli errori provider riportati in audit precedenti se non verificabili dai dati correnti.

## 1. Registro cumulativo

Ledger ereditato senza modifiche:
- File: `reports/pravda-signal-ledger-2026-11-09.csv`
- Blob SHA: `1acbe2994b6147a4d2fdd39108cf46f499fd6265`
- Record dati: **103**
- SPUTNIK: **48**; GAGARIN: **55**
- `audit_signature` uniche: **103**
- `source_record_id` unici: **103**
- Duplicati firma/source ID: **0**
- Outcome registrati: **74 NON_TRADE**, **29 ESITO_NON_VERIFICABILE**

I 29 record ESITO_NON_VERIFICABILE non sono 29 perdite e non costituiscono un campione di fill. Nessun fill verificato, nessun SL/TP verificato; win rate, average R e total R restano N/D. Non è stato aggiunto alcun record perché non è emerso un nuovo segnale produttivo successivo a quelli già registrati.

## 2. SPUTNIK — run, stato e segnali

### Ultime esecuzioni schedulate su main

- Collector #293: run `42570608770`, avvio 2026-11-09 06:01:41 UTC, completamento 06:01:51 UTC, SUCCESS.
- Polling #53: run `42570062235`, avvio 05:55:47 UTC, completamento 05:55:56 UTC, SUCCESS.
- Precedenti collector #292: 2026-11-08 23:59:46 UTC; polling #52: 23:56:54 UTC.
- Gap fra collector #292 e #293: **6h 01m 55s**; fra polling #52 e #53: **5h 58m 53s**.
- Al cut-off 12:41:05 UTC: circa **6h 39m** dall'ultimo collector e **6h 45m** dall'ultimo polling.
- Cron su main: collector `2-59/5 * * * *`; polling `*/5 * * * *`.

Le ultime 100 run API non mostrano una run schedulata successiva a #293/#53. Le run #42611284354 e #42611284334 sono CI della PR #155, non scansioni produttive.

### Stato persistito

`sputnik_state.json` su main:
- `updated_at=2026-11-09T06:01:46.594274+00:00`
- `events={}`
- `intelligence_history`: 500 elementi.

Ultimi item RSS:
- Post #43530, pubblicato 2026-11-08 23:41:05 UTC, rilevato 2026-11-09 06:01:46.562982 UTC: ritardo **6h 20m 41.6s**.
- Post #43532 / S.5653, pubblicato 2026-11-09 00:05:49 UTC, rilevato 06:01:46.562743 UTC: ritardo **5h 55m 57.6s**.
- È presente anche una correlazione TRUTH_ARCHIVE page-level senza titolo/permalink/data di pubblicazione individuale: non è un terzo post identificabile.

Difetto dimostrato nello stato persistito: il post S.5653 riguarda permitting e indipendenza energetica, ma l'item RSS #43532 è classificato `TRADE_ESCALATION` e associato all'analogia `china_tariff_escalation_2025_10`. Anche lo snapshot page-level TRUTH_ARCHIVE riceve la stessa analogia. La correzione proposta è PR #154, ancora OPEN/non merged.

### Messaggi già registrati nel ledger

| ID Telegram | Generazione UTC | Invio/API UTC | Contenuto | Campi e stato |
|---|---|---|---|---|
| #746 | 06:01:48.1711626 | 06:01:48.1720275 | Digest 2 item RSS | Informativo, nessuna direzione/nessun trade |
| #747 | 06:01:48.1720811 | 06:01:48.1731760 | GOLD LONG preliminare | LONG 5m, momentum +0,077%/15m; nessun livello; `NOT_CONFIRMED`; score 100 non è validità operativa |
| #748 | 06:01:48.1732205 | 06:01:48.1742253 | GOLD EARLY_SETUP | Entry 4133.2002; SL 4130.5859; TP1 4135.8145; TP2 4138.4289; ATR 1.7429; `NOT_EXECUTED` |

Per #748 il ledger registra titolo CFD ma corpo `FUTURES_CONTINUOUS_FRONT_MONTH`, ticker non risolto, expiry UNKNOWN, provider e quote timestamp non esposti, prezzo di riferimento assente, NARWHAL non configurato e D-L-A NEUTRAL. La direzione tecnica è LONG nel messaggio #747 ma NOT_ASSESSED nella card #748. Non è un trade: nessun esito SL/TP viene calcolato e non si può stabilire se i livelli fossero già superati. Gli ACK API riportati nel ledger non provano la visualizzazione sul dispositivo.

### PR SPUTNIK

- #155 cadence diagnostics: OPEN, non merged, base SHA uguale a main corrente `8bdf7ab16ec3bfd23d5f3160a4e87dffbfd35396`; due CI SUCCESS. Aggiunge solo diagnostica read-only delle ultime run schedulate; non ripristina gli eventi schedule mancanti.
- #154 classificazione China/tariff: OPEN, due CI SUCCESS; non integrata, quindi il difetto S.5653 è ancora presente nello stato su main.
- #153 propagazione direzione tecnica nella card CFD: OPEN, due CI SUCCESS; non integrata.
- #150 anti-ripetizione, #152 brief giornaliero, #147 separazione SPUTNIK/GAGARIN: OPEN, non integrate.
- #145 quote provenance e #144 persistenza stato: OPEN; i rispettivi base SHA non coincidono con il main corrente, quindi richiedono riallineamento/revalidazione.

Il workflow su main non contiene ancora `actions: read` e non contiene il nuovo step diagnostico proposto dalla #155.

## 3. GAGARIN — run e candidata

### Ultima esecuzione schedulata

- Monitor #172: run `42573849716`, avvio 2026-11-09 06:34:18 UTC, completamento 06:34:37 UTC, SUCCESS.
- Monitor precedente #171: 2026-11-09 00:04:51 UTC.
- Gap #171→#172: **6h 29m 27s**.
- Al cut-off 12:41:05 UTC: circa **6h 06m 47s** dall'ultima run.
- Cron su main: `*/15 * * * *`.

Le ultime 100 Actions non mostrano una successiva run schedulata del monitor. Le numerose run push/PR dei branch #241 e #240 sono CI, non monitor di mercato. Il run #172 non ha artifact associati; il connettore espone gli step ma non il log completo. Perciò in questo controllo non è possibile riconfermare le età di tutte le commodity dal log originale.

### Candidata registrata

Run #172, candidato `SOYBEAN/USD:SHORT`:
- generazione: 2026-11-09 06:34:30.263983 UTC;
- direzione SHORT; probability 63, quality 55.5, confidence 35;
- provider YAHOO, quote age 659.4 secondi;
- quote timestamp assoluto, Yahoo ticker risolto, market type e expiry non esposti;
- entry, SL, TP e ATR assenti;
- `PAPER_WATCH`, `NOT_AUTHORIZED`, bloccato da LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH e FINAL_CONFLUENCE_FAIL.

È una candidata bloccata, non un trade e non un segnale autorizzato.

Telegram #3728 è registrato come WATCH_PRE_ALERT, API timestamp 06:34:34.1131912 UTC. Il corpo non è conservato: strumento, direzione, provider e livelli non sono attribuibili. L'ACK API non prova consegna sul dispositivo.

### Journal e feedback pubblici

- `commodities_prediction_log.json`: **981** record, 981 ID unici, zero ID duplicati; ultimo `created_at` 2026-09-15 15:45:04.462276 UTC.
- `operational_signal`: 960 WAIT, 15 LONG, 6 campi assenti.
- `action=COMPRA ORA`: 21 record, tutti status PENDING; i sei record più recenti con schema incompleto non hanno `operational_signal`. Non sono prova di fill.
- `commodities_monitor_state.json`: ultimo timestamp 2026-09-17 03:44:02 UTC.
- `commodities_direction_state.json`: timestamp degli aggiornamenti del 17 settembre.
- `journal.csv`: 11 righe del 17 ottobre, tutte “nessun segnale”.
- `paper_trade_log.csv`: una riga WTI LEGACY_IMPORT dell'8 ottobre, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55; provider/ticker contratto/timestamp quota e signal_id assenti, P&L vuoto.
- `data/paper_open.json`: P0001 WTI LONG OPEN, PAPER ONLY, stessi livelli; record legacy senza prova di fill né outcome.
- `position.json`: vecchia posizione Heating Oil LONG aperta il 15 settembre, senza prova di esecuzione o outcome.
- `gagarin_feedback.csv`: assente dal ramo pubblico; la directory `data/` non contiene un feedback journal.
- `driver_snapshot.json` letto l'8 novembre: EIA crude stocks e natgas storage `no_data`; valori USDA wheat/corn/soy null; inventari/curva/supply shock e altre variabili restano UNKNOWN.

Il workflow `gagarin-monitor.yml` dichiara che la persistenza dei journal privati sarà riattivata solo dopo deploy e verifica dello storage privato. Non è stata dimostrata una scrittura e rilettura persistente; non si inferisce lo stato dei secret.

## 4. Universo operativo GAGARIN — conflitto di perimetro

Su main `commodities/universe.py` contiene 10 simboli logici:
XAU/USD, XAG/USD, COPPER/USD, WTI/USD, BRENT/USD, WHEAT/USD, CORN/USD, SOYBEAN/USD, EUR/USD, GBP/USD. Il runner main usa ancora `enabled_commodities()`; quindi il ramo attivo conserva Argento e le due coppie Forex. Platino e Palladio non compaiono nell'universo main.

Le PR propongono due perimetri incompatibili:
- #241: Argento disabilitato, 7 commodity operative + EUR/USD e GBP/USD come contesto; base SHA uguale al main corrente, ma DRAFT e un workflow CI (`SOYUZ GAGARIN Tests`) fallisce; gli altri quattro workflow associati sono SUCCESS.
- #221: 8 commodity inclusa Argento, Forex rimosso e runner limitato a `operational_commodities()`; DRAFT, sei CI SUCCESS, ma base SHA `fba34bef...` è precedente al main corrente `e7f5d2f...`, quindi branch da riallineare e revalidare.

La richiesta precedente di escludere Argento e la proposta #221 che lo mantiene non sono coerenti. PRAVDA non decide né modifica il perimetro; segnala la discrepanza. Nessuna delle due PR è integrata.

## 5. Outcome engine e PR

- Main `engine/feedback.py` non conserva provider/ticker/market/expiry nel record di feedback e classifica ancora come STOP una candela OHLC che tocca contemporaneamente SL e TP.
- PR #192 aggiunge provider/ticker/market/contract month/expiry al fingerprint, controlli di quote symbol e market type, matching del contratto futures e `ESITO NON VERIFICABILE` per il doppio tocco.
- Difetto residuo dimostrato nel branch #192: `_market_contract_match()` confronta quote symbol, market type, contract month/expiry, ma non confronta il provider della serie successiva con `quote_provider` del segnale. Il provider è nel fingerprint, non nel matching delle candele.
- PR #192 è OPEN, non merged, base SHA `c93906a...` diverso dal main corrente `e7f5d2f...`; i sei CI SUCCESS sono riferiti al branch/head testato, non dimostrano la compatibilità con il main attuale.
- PR #239 richiede prova esplicita del tipo CFD e dell'eventuale assenza di expiry; è DRAFT e stacked su #238, non su main. Registry CFD dichiarato vuoto nella descrizione PR.
- PR #202 journal PostgreSQL è DRAFT, non integrata; la descrizione propone PostgreSQL, mentre il commento nel workflow main parla di storage privato D1. Backend da chiarire prima di considerare verificata la persistenza.
- PR #225 offset cron GAGARIN è DRAFT, non integrata; cinque CI SUCCESS sul branch, ma base SHA non è il main corrente. Main resta `*/15`.

## 6. Esiti e statistiche

- Nuovi segnali produttivi dopo SPUTNIK #293 e GAGARIN #172: **0**.
- Segnali #747/#748: NON_TRADE; #748 NOT_EXECUTED.
- Soia: candidata bloccata, non autorizzata.
- #3728: pre-alert non attribuibile.
- Candele successive dello stesso identico provider, ticker, mercato e contratto: non disponibili.
- Fill verificati: **0**; SL verificati: **0**; TP verificati: **0**.
- Win rate / average R / total R: **N/D**.

Nessun backtest, fill o risultato è stato inventato.

## 7. Fonti dirette

- SPUTNIK run #293: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770
- SPUTNIK polling #53: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570062235
- SPUTNIK state: https://github.com/andreameloni1984-sys/trump-trucker/blob/main/sputnik_state.json
- SPUTNIK workflow: https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/trump_tracker.yml
- SPUTNIK PR #155: https://github.com/andreameloni1984-sys/trump-trucker/pull/155
- SPUTNIK PR #154: https://github.com/andreameloni1984-sys/trump-trucker/pull/154
- SPUTNIK PR #153: https://github.com/andreameloni1984-sys/trump-trucker/pull/153
- GAGARIN run #172: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716
- GAGARIN workflow: https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml
- GAGARIN prediction log: https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities_prediction_log.json
- GAGARIN universe: https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities/universe.py
- GAGARIN paper journal: https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/paper_trade_log.csv
- GAGARIN paper open: https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/data/paper_open.json
- GAGARIN PR #241: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/241
- GAGARIN PR #221: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221
- GAGARIN PR #225: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225
- GAGARIN PR #192: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192
- GAGARIN PR #202: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202
- GAGARIN PR #239: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/239

## 8. Prossimo controllo

1. Verificare nuove run schedulate e misurare il gap con i timestamp GitHub.
2. Dopo eventuale merge #155, verificare la diagnostica cadence su una vera run main.
3. Controllare che la correzione #154 elimini l'analogia tariffaria sul caso S.5653.
4. Verificare la direzione tecnica nella card CFD dopo #153.
5. Risolvere il conflitto di perimetro #241/#221 senza modifiche PRAVDA.
6. Ottenere quote timestampate e identità contrattuale completa per le commodity; non inferire futures expiry da ticker continuo.
7. Riallineare e rieseguire i test di #192 su main corrente, includendo il confronto del provider delle candele.
8. Dimostrare scrittura e rilettura del journal su un backend privato documentato.
9. Attribuire #3728 solo se il corpo del messaggio viene conservato.
10. Valutare SL/TP soltanto su candele successive dello stesso identico strumento, provider, mercato e contratto; stesso-candle dual touch = ESITO NON VERIFICABILE.

## Sicurezza e perimetro

Solo audit e documentazione PRAVDA su branch separato. Ledger ereditato senza modifiche. Nessun codice applicativo, strategia, filtro, punteggio o rischio modificato; nessun merge/deploy, ordine reale, secret o Render modificati. Nessun servizio a pagamento. Nessun accesso a Trading 212 né consegna Telegram al dispositivo dichiarati.
