# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
## Controllo #17 — 9 novembre 2026, 19:23 CET (18:23 UTC)

## Esito sintetico

Audit eseguito sui due repository, sui log integrali dei run identificati, sui file correnti di `main`, sui journal pubblici e sulle PR esistenti.

Novità e conferme:
- Nessun nuovo segnale operativo è emerso dai run produttivi con log recuperati dopo SPUTNIK #295 e GAGARIN #173. Non è stata aggiunta alcuna riga al ledger.
- SPUTNIK #295 ha inviato la card GOLD LONG #753, ma la card dichiara front-month continuo, scadenza e indipendenza upstream non verificate e avverte di non usare i livelli.
- Il forwarding SPUTNIK→GAGARIN risulta disabilitato nel run #295: `GAGARIN_CLOUD_API_URL/API_KEY` non configurati.
- GAGARIN #173 ha completato il monitor, ma tutte le otto commodity erano STALE; zero entry, zero nuovi feedback, zero outcome aggiornati.
- GAGARIN polling #20 è fallito nuovamente con API 409 per webhook attivo.
- Il journal GAGARIN non è durevole: `DATABASE_URL` vuota, CSV feedback assente dal main e il research log conferma che i CSV pubblici non vengono più committati mentre il backend privato non è ancora verificato.
- L'outcome engine su main resta inadatto a certificare gli esiti: identità incompleta, matching per symbol/timeframe e doppio tocco SL/TP classificato STOP.
- PR #222 è già stata integrata da altri: rimuove `session_ok` dal veto operativo obbligatorio. PRAVDA non ha eseguito né approvato questa modifica; la registra come modifica esistente del gate.

Nessun fill verificato. Nessun esito SL/TP certificabile.

## 1. Registro storico PRAVDA

Ledger letto dal branch precedente `pravda/audit-2026-11-09-1752UTC`.

- Record: 106
- SPUTNIK: 50
- GAGARIN: 56
- Firme uniche: 106
- Source ID unici: 106
- Duplicati firma: 0
- Duplicati source ID: 0
- NON_TRADE: 77
- ESITO_NON_VERIFICABILE: 29
- Fill verificati: 0
- SL verificati: 0
- TP verificati: 0

SHA ledger invariato: `41a1339c2047c86ad9026ab131d9a8015d0cd710`.

Nessun nuovo record aggiunto. Le card #751 e #753 restano due opportunità distinte SPUTNIK; i messaggi preliminari #750/#752 sono compagni delle rispettive card e non sono contati due volte. Il WATCH GAGARIN #3734 resta non attribuibile e non operativo.

Win rate, average R e total R: N/D. Non esiste un campione di fill con outcome verificato.

Ledger: https://github.com/andreameloni1984-sys/trump-trucker/blob/pravda/audit-2026-11-09-1752UTC/reports/pravda-signal-ledger-2026-11-09.csv

## 2. SPUTNIK — ultimo run con log recuperato

Run: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42650624196

- Run #295, evento `schedule`.
- Avvio: 2026-11-09 16:02:05 UTC.
- Fine: 16:02:23 UTC.
- Job: SUCCESS.
- Il job ha eseguito il commit di persistenza dello stato; commit successivo: https://github.com/andreameloni1984-sys/trump-trucker/commit/6c3095f1534550b0b4e77170f1428db833253c05

La precedente scansione collector schedule verificata era #293 alle 06:01:41 UTC. Il run #294 alle 15:33:04 UTC era `event=push`, non schedule. Gap tra #293 e #295: 10h00m24s. Al cut-off 18:23:42 UTC, #295 era trascorso da 2h21m37s.

Il workflow main dichiara cron `2-59/5 * * * *`. La causa dei gap non è dimostrata.

**Limite di enumerazione:** in questo controllo ho potuto recuperare i log dei run identificati #295, #173 e #20 e consultare i commit recenti, ma non ho ottenuto un elenco REST completo e aggiornato di tutte le Actions. Quindi #295 è l'ultimo collector con log verificato in questo audit, non una dichiarazione assoluta che non esistano run successivi.

### Raccolta fonti e collegamento tra bot

Nel log #295:
- SEC: HTTP 403; cooldown 21.600 secondi.
- Filing: 0.
- White House RSS `https://www.whitehouse.gov/feed/`: HTTPError.
- GAGARIN forwarding: 0 ms.
- Test e runtime dichiarano GAGARIN handoff disabilitato perché `GAGARIN_CLOUD_API_URL` e `GAGARIN_CLOUD_API_KEY` non sono configurati.
- `NARWHAL_REFERENCE_ENABLED=1`, ma `NARWHAL_API_KEY` è vuota; la card riporta NARWHAL NOT_CONFIGURED.

La catena SPUTNIK→GAGARIN non è quindi dimostrata come attiva.

### GOLD LONG — messaggi #752/#753

I due messaggi appartengono a una sola opportunità; ledger conservato una sola volta sotto la card #753.

Analisi preliminare #752:
- generata circa 16:02:18.582 UTC;
- GOLD, bias LONG;
- tecnica LONG 5m;
- momentum 15m +0,031%;
- NO_DIRECTIONAL_NEWS;
- stato EARLY_BIAS;
- API ACK #752 circa 16:02:18.584 UTC, 590 ms.

Card #753:
- ID/firma: `run:42650624196/telegram_message:753`;
- generazione: 16:02:18.5845249 UTC;
- invio/ACK API: 16:02:18.5856255 UTC;
- Telegram message ID: 753;
- strumento logico: GOLD;
- ticker esatto: NOT_RESOLVED;
- mercato dichiarato: titolo CFD, corpo FUTURES_CONTINUOUS_FRONT_MONTH;
- scadenza: UNKNOWN;
- provider: NOT_EXPOSED; NARWHAL_NOT_CONFIGURED;
- timestamp/età quotazione: NOT_EXPOSED;
- reference price: NOT_RECORDED;
- direzione: LONG;
- tecnica/D-L-A: LONG / ALIGNS;
- entry: 4129.2998;
- SL: 4126.9106;
- TP1: 4131.689;
- TP2: 4134.0781;
- TP3: assente;
- ATR: 1.5928;
- score: 100;
- stato: EARLY_SETUP / NOT_EXECUTED.

La card avverte che il front-month continuo non ha scadenza esatta né indipendenza upstream verificate e dice di non usare i livelli. Score 100 non prova validità operativa; NOT_EXECUTED non è un trade. Non esiste una serie successiva identificata dello stesso ticker/contratto/provider: nessun SL o TP può essere attribuito. Outcome contabile: NON_TRADE; outcome di prezzo non verificabile.

L'API ha accettato i messaggi #752 e #753; questo non prova visualizzazione sul dispositivo né esecuzione.

### GOLD SHORT precedente — messaggi #750/#751

Card #751 già registrata una sola volta:
- generazione: 15:33:13.053057 UTC;
- invio/ACK API: 15:33:13.0545671 UTC;
- ID: `run:42645788987/telegram_message:751`;
- GOLD SHORT;
- entry 4125.6001;
- SL 4128.3859;
- TP1 4122.8143;
- TP2 4120.0285;
- ATR 1.8572;
- score 100;
- NOT_EXECUTED.

La card dichiara CFD nel titolo e future continuo front-month nel corpo; ticker, scadenza, provider, timestamp e reference price non sono esposti; NARWHAL non configurato; D-L-A NEUTRAL e tecnica N/D nonostante #750 riportasse SHORT 5m. NON_TRADE, nessun esito verificabile.

### PR SPUTNIK pertinenti

- PR #155 cadence diagnostics: OPEN, non integrata; check associati al suo head SUCCESS. Il run #295 documenta un intervallo schedule anomalo, ma non dimostra la causa.
- PR #153 direzione tecnica nella card CFD: OPEN, non integrata. La card #753 conserva LONG correttamente, mentre il caso #751 aveva perso la direzione; un solo caso positivo non certifica la correzione generale.
- PR #154 classificazione tariffaria: OPEN, non integrata.
- PR #131 endpoint White House: OPEN, non integrata.

Nessun merge o modifica PRAVDA.

## 3. GAGARIN — monitor #173

Run: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42659137635

- Evento: schedule.
- Avvio: 16:52:38 UTC.
- Fine: 16:53:01 UTC.
- Risultato: SUCCESS.
- SHA eseguito: `50b25a80d6792be913c2bcf5a117ede68dd52b59`.
- Main è stato successivamente aggiornato dal driver snapshot commit `5f523c6f5db62eed4bb3468874285155ed8cd455` alle 16:55:43 UTC.

Il monitor precedente verificato #172 era partito alle 06:34:18 UTC; gap start-to-start #172→#173: 10h18m20s. Il workflow main continua a dichiarare cron `*/15 * * * *` e `MONITOR_INTERVAL_MINUTES=15`.

Al cut-off 18:23:42 UTC, #173 era trascorso da 1h31m04s. Non dichiaro l'assenza assoluta di run successivi perché non ho ottenuto un elenco completo aggiornato delle Actions.

### Quotazioni del run #173

Otto commodity operative, tutte YAHOO STALE:

- Rame: 604,7 s.
- Grano: 604,0 s.
- WTI: 601,8 s.
- Mais: 606,1 s.
- Soia: 603,5 s.
- Oro: 602,6 s.
- Brent: 605,0 s.
- Argento: 626,6 s.

EUR/USD 176,2 s e GBP/USD 176,9 s risultano LIVE via BIQUOTE, ma il log li classifica come contesto Forex/non operativo.

Il log espone provider ed età, non timestamp assoluto, ticker contrattuale esatto e scadenza di ogni serie commodity. Il mapping applicativo è futures continuous; non va confuso con spot o con un future a scadenza specifica.

Tutte le commodity risultano PAPER_WATCH, con blocchi di freshness, setup/trigger non confermati e livelli mancanti. Nessuna entry, SL, TP o ATR operativo completo.

Risultato:
- Recorded entries: 0.
- Updated open outcomes: 0.
- New feedback signals: 0.
- New additional live forecasts: 0.
- signals=0, open=0, closed=0.
- win_rate=N/D, avg_R=N/D, total_R=0.0.

### Telegram #3734

- ID: `run:42659137635/telegram_watch_pre_alert:3734`.
- API ACK: circa 16:52:57.4478258 UTC.
- Message ID: 3734.
- Round-trip: 556 ms.
- Generazione: non esposta.
- Corpo: non conservato.
- Strumento/direzione/livelli: non attribuibili.

Resta WATCH pre-alert non operativo, già registrato come NON_TRADE. ACK API non prova visualizzazione sul dispositivo.

## 4. Telegram polling GAGARIN — errore 409

Run #20: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42660005021

- Avvio job: 16:58:18 UTC.
- Token validation: SUCCESS.
- Telegram diagnostic: SUCCESS.
- `getUpdates`: API 409.
- Errore: webhook attivo; polling incompatibile con webhook mode.
- Job: FAILURE.

Il workflow polling main è schedulato ogni 5 minuti nei giorni feriali, 07–21 UTC. La PR #175 propone di riconoscere il 409, saltare il polling senza cancellare il webhook e senza confermare update non processati.

PR #175 è OPEN; il branch è 1 commit avanti e 5 indietro rispetto al main corrente. I check verdi associati sono sul vecchio head e non provano una validazione contro il main attuale.

Commento PRAVDA aggiornato: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175#issuecomment-6748037506

## 5. Journal, prediction log e persistenza

### Prediction log storico

File main: `commodities_prediction_log.json`.

Verifica diretta:
- record: 981;
- ID unici: 981;
- duplicati ID: 0;
- primo timestamp: 2026-09-10 19:04:57 UTC;
- ultimo timestamp: 2026-09-15 15:45:04 UTC;
- status PENDING: 945;
- status NEUTRALE: 36;
- action COMPRA ORA: 21, tutte PENDING;
- action WAIT/ATTENDERE e direzioni in attesa: non sono fill.

Questi sono record previsionali storici, non operazioni eseguite e non un campione di outcome verificati.

### Altri artefatti main

- `paper_trade_log.csv`: una sola riga WTI del 2026-10-08, `LEGACY_IMPORT`, senza quote provider/ticker/timestamp/market/expiry; la nota dice esplicitamente “Nessun esito”.
- `data/paper_open.json`: WTI P0001 LONG OPEN legacy, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55, P&L null; nessuna prova di fill o identità contrattuale.
- `position.json`: Heating Oil LONG aperta 2026-09-15 13:23:44 UTC, entry 4.8844, SL 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882; provider, ticker contrattuale, scadenza e fill non dimostrati.
- `gagarin_feedback.csv`: 404, assente dal main.
- Nel run #173 `DATABASE_URL` è vuota.

Il `GAGARIN_RESEARCH_LOG.md` registra il 2 novembre la decisione di non pubblicare più i CSV PAPER nei workflow pubblici: i runner GitHub sono effimeri e il backend privato D1 non era ancora distribuito/verificato. La PR #202 propone PostgreSQL, ma la configurazione/runtime non prova una persistenza cross-run.

PR #202 è DRAFT; confronto con main: 18 commit avanti, 6 indietro. I test verdi associati al vecchio head non provano il funzionamento sul main corrente. Il workflow parla di D1 mentre la PR propone PostgreSQL: backend da allineare.

Commento PRAVDA aggiornato: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202#issuecomment-6748038594

## 6. Outcome engine — difetti dimostrati su main

Main corrente GAGARIN: `5f523c6f5db62eed4bb3468874285155ed8cd455`.

In `engine/feedback.py`:
- FIELDS non hanno campi separati per quote_provider, quote_symbol, market_type, contract_month, contract_expiry; è presente solo `data_source`.
- Il fingerprint usa symbol, direction, timeframe, livelli e bar timestamp; non include l'identità completa provider/mercato/contratto.
- `update_open_outcomes` abbina gli stati per `(symbol, timeframe)`, con fallback sul symbol se esiste un solo candidato.
- Il codice controlla `stop_hit` prima di `hit_targets`; la docstring dichiara esplicitamente che il doppio tocco nella stessa candela viene risolto come STOP.

Questo non soddisfa la regola PRAVDA. Se una candela tocca SL e TP e l'ordine intrabar non è ricostruibile, l'esito deve essere ESITO NON VERIFICABILE.

PR #192 propone fingerprint provider/ticker/mercato/contratto e gestione non verificabile del doppio tocco. Ma il branch è 6 commit avanti e 8 indietro rispetto al main attuale; i check verdi risalgono al vecchio head. Nel patch esaminato il provider entra nel fingerprint, ma `_market_contract_match` confronta quote symbol, market type e contratto senza un confronto esplicito row-provider/state-provider. La PR non è ancora certificabile come matching completo del provider.

Commento PRAVDA aggiornato: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6748038018

## 7. Universo, gate e PR

### Argento

Su main `commodities/universe.py` Argento è ancora `enabled=True`; compare anche nel run #173 con YAHOO STALE. La PR #241 è chiusa senza merge, quindi l'esclusione proposta non è attiva. Questa è una mancata applicazione della precedente richiesta di escludere Argento, non una modifica PRAVDA.

PR #241: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/241

### Gate sessione

PR #222 è stata MERGED il 2026-11-08 20:24:56 UTC. Il commit `e7f5d2f...` rimuove `session_ok` dai veto operativi obbligatori del Governor e del bridge. La PR dichiara che market-open, quote freshness, data quality, contract, liquidity, volatility, regime, trigger, risk e RR restano controlli separati.

È una modifica già effettuata da altri sul main; PRAVDA non l'ha eseguita né approvata. Va registrata come modifica al gate operativo, non nascosta come semplice test.

### PR #243 — rimozione monitor Invest legacy

PR #243 è DRAFT, non integrata. I sette workflow GitHub associati al suo head risultano SUCCESS, ma il commento Cloudflare segnala build del Worker fallita. La PR dichiara esplicitamente che rimuove soltanto il vecchio monitor Trading 212 Invest e i relativi comandi; non implementa un feed CFD né dimostra accesso a quotazioni CFD. Nessun deploy è verificato.

### PR #242 — scadenze passate

PR #242 è DRAFT, basata su una catena separata; il confronto col main è 30 commit avanti e 6 indietro. I due test associati risultano SUCCESS, ma il commento Cloudflare riporta build fallita. La modifica riguarda validazione identità/scadenza, non un provider di quotazioni o un feed CFD.

### Soglie runtime

Il workflow main espone:
- MIN_ENTRY_PROBABILITY=40;
- MIN_ENTRY_QUALITY=30;
- MIN_ENTRY_CONFIDENCE=35;
- MIN_ENTRY_RR=2.5;
- MAX_ENTRY_STOP_ATR=2.5;
- MONITOR_INTERVAL_MINUTES=15.

I valori 40/30/35 non coincidono con le precedenti specifiche annotate 62/55/60. PRAVDA non ha cambiato alcuna soglia.

## 8. Driver snapshot macro

Snapshot main aggiornato 2026-11-09 16:55:43 UTC.

- Scorte petrolio USA EIA: no_data.
- Storage gas naturale EIA: no_data.
- Bilanci mondiali WASDE per grano/mais/soia: null.
- Dollar index FRED: data 2026-10-30.
- Real rate 10Y FRED: data 2026-11-05.

Le variabili senza dato sono correttamente lasciate UNKNOWN; non sono state inventate osservazioni. Il quadro macro resta parziale e con alcune date non recenti.

## 9. Segnalazioni ai reparti

Commenti di audit pubblicati, senza modifiche al codice:
- PR #175 — nuovo 409 e branch stale: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175#issuecomment-6748037506
- PR #192 — outcome engine main e branch stale: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6748038018
- PR #202 — DATABASE_URL vuota, feedback assente, persistenza non dimostrata: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202#issuecomment-6748038594

## 10. Verdetto PRAVDA — 19:23 CET

| Indicatore | Risultato |
|---|---:|
| Record PRAVDA | 106 |
| Firme/source ID unici | 106 |
| Duplicati | 0 |
| Nuovi record | 0 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |
| Win rate | N/D |
| Average R | N/D |
| Total R | N/D |

- SPUTNIK #753: GOLD LONG, livelli presenti ma NOT_EXECUTED e contratto/provenienza incompleti; NON_TRADE.
- SPUTNIK #751: GOLD SHORT, NOT_EXECUTED e contratto/provenienza incompleti; NON_TRADE.
- GAGARIN #3734: WATCH pre-alert senza corpo, strumento non attribuibile; NON_TRADE.
- GAGARIN #173: otto commodity stale, nessuna entry autorizzata.
- Nessun esito SL/TP può essere verificato con candele successive dello stesso identico contratto.

## 11. Prossimo controllo

1. Ottenere un elenco completo aggiornato delle GitHub Actions e distinguere schedule, push e workflow_dispatch.
2. Verificare la prossima scansione SPUTNIK e la cadenza reale.
3. Verificare la prossima scansione GAGARIN e la freschezza di ciascuna commodity.
4. Verificare il forwarding SPUTNIK→GAGARIN solo con prova runtime della configurazione e dell'ACK applicativo.
5. Risolvere il 409 polling/webhook senza cancellare il webhook.
6. Dimostrare il backend persistente del journal, senza leggere o modificare secret.
7. Riallineare PR #175, #192 e #202 al main corrente.
8. Rendere il matching outcome esatto su provider, quote ticker, mercato e scadenza.
9. Per ogni candela con doppio tocco SL/TP senza sequenza intrabar: ESITO NON VERIFICABILE.
10. Non attribuire risultati alle card CFD front-month senza contratto e serie successiva identici.

## Limiti e sicurezza

Nessun codice applicativo, strategia, filtro, punteggio, soglia o rischio modificato da PRAVDA. Nessun merge, deploy, ordine reale, secret letto/modificato o intervento Render. Nessun servizio a pagamento. Nessun accesso a Trading212 dichiarato. Gli ACK Telegram sono riportati soltanto come accettazione API, non come consegna sul dispositivo.

PAPER ONLY.
