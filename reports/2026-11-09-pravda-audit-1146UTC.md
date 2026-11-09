# PRAVDA — Audit indipendente SPUTNIK / GAGARIN

**Cut-off: 9 novembre 2026, 11:46:06 UTC (12:46:06 Europe/Rome)**

## Sintesi esecutiva

Verificati direttamente tramite GitHub API:
- le ultime 100 Actions complessive e le ultime 100 run `event=schedule` di entrambi i repository;
- i log integrali dei job produttivi SPUTNIK #293 e GAGARIN #172;
- i job e i log delle CI più recenti delle PR rilevanti;
- i workflow e i cron su `main`;
- ledger PRAVDA, file journal/feedback, prediction log e stati GAGARIN;
- stato e diff delle PR #155, #153, #154, #131, #225, #241, #240, #239, #217 e #192.

**Non risultano nuove scansioni produttive dopo SPUTNIK #293 / polling #53 e GAGARIN #172.** Le nuove run SPUTNIK delle 11:43 UTC sono CI della PR #155, non scansioni di mercato.

Non è emerso alcun nuovo segnale operativo da aggiungere al ledger. Nessun fill, SL o TP è verificabile.

## 1. Ledger PRAVDA

Ledger cumulativo ereditato senza modifiche:
- File: `reports/pravda-signal-ledger-2026-11-09.csv`
- Blob SHA: `1acbe2994b6147a4d2fdd39108cf46f499fd6265`
- Record: **103**; colonne: **33**.
- SPUTNIK: **48**; GAGARIN: **55**.
- `audit_signature` uniche: **103**; duplicati: **0**.
- `source_record_id` unici: **103**; duplicati: **0**.
- Esiti registrati: **74 NON_TRADE**, **29 ESITO_NON_VERIFICABILE**.
- Fill verificati: **0**; SL verificati: **0**; TP verificati: **0**.

Nessuna nuova firma o source ID da aggiungere: gli ultimi messaggi SPUTNIK #746–#748 e i record GAGARIN della run #172 sono già presenti.

### Completezza dei campi

Nel sottoinsieme di 18 record candidati/early-setup del ledger:
- scadenza contrattuale mancante o sconosciuta: 18/18;
- provider mancante/non esposto: 12/18;
- timestamp quotazione mancante/non esposto: 17/18;
- ticker non risolto: 2/18;
- entry, SL, TP1 e ATR mancanti: 10/18 (comprende record preliminari che non espongono livelli).

Queste lacune impediscono di attribuire candele successive a un identico strumento/contratto. Le statistiche di performance restano N/D; non esiste un campione di trade con fill verificato.

## 2. SPUTNIK — ultima produzione e messaggi

### Run produttiva

[SPUTNIK #293](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770)
- Evento: `schedule`; branch `main`.
- Avvio: **2026-11-09 06:01:41 UTC**.
- Fine: **06:01:51 UTC**.
- Esito GitHub Actions: SUCCESS.

Log del job: job ID `129006852221`.

### Raccolta notizie

Il log riporta:
- SEC HTTP 403; cooldown 21.600 secondi;
- filing: 0; transazioni: 0;
- White House RSS: HTTPError sul vecchio endpoint `https://www.whitehouse.gov/feed/`;
- due item-level RSS nel digest, ma tre correlazioni pubbliche dichiarate dal collector.

Item elencati:
- Quote post #43530: pubblicato **2026-11-08 23:41:05 UTC**, rilevato nel collector alle **06:01:46 UTC**; ritardo **6h20m41s**. [Fonte](https://www.trumpstruth.org/statuses/43530)
- Post S.5653 #43532: pubblicato **2026-11-09 00:05:49 UTC**, rilevato alle **06:01:46 UTC**; ritardo **5h55m57s**. [Fonte](https://www.trumpstruth.org/statuses/43532)

Il post S.5653 è relativo a permitting/indipendenza energetica, non a un annuncio tariffario. Il collegamento a una vecchia analogia `china_tariff_escalation_2025_10` è già corretto dalla proposta PR #154, ma la PR non è integrata.

### Messaggi effettivi

| ID | Generazione UTC | Invio/API UTC | Contenuto | Stato |
|---|---|---|---|---|
| #746 | 06:01:48.1711626 | 06:01:48.1720275 | Digest informativo, due item RSS | NON_TRADE |
| #747 | 06:01:48.1720811 | 06:01:48.1731760 | GOLD LONG preliminare, tecnica 5m LONG, momentum 15m +0,077%, nessun catalizzatore direzionale | NON_TRADE |
| #748 | 06:01:48.1732205 | 06:01:48.1742253 | GOLD LONG con livelli numerici | NOT_EXECUTED |

Per i tre messaggi il log registra ACK API rispettivamente di 563 ms, 313 ms e 322 ms. È prova di accettazione API con message ID, non di visualizzazione sul dispositivo.

### GOLD #748 — livelli e identità

| Campo | Valore |
|---|---|
| Strumento logico | GOLD |
| Ticker esatto | NOT_RESOLVED |
| Direzione | LONG |
| Entry | 4133.2002 |
| SL | 4130.5859 |
| TP1 | 4135.8145 |
| TP2 | 4138.4289 |
| ATR | 1.7429 |
| Score | 100 |
| Stato | NOT_EXECUTED |
| Mercato dichiarato | titolo CFD; corpo FUTURES_CONTINUOUS_FRONT_MONTH |
| Scadenza | UNKNOWN |
| Provider / timestamp quotazione | non esposti |

Il messaggio stesso avverte: scadenza esatta e indipendenza upstream non verificate, non usare i livelli. NARWHAL non configurato; D-L-A NEUTRAL/NO_DIRECTION e TECNICA N/D nella card, nonostante il messaggio #747 riporti LONG 5m.

**Esito: ESITO NON VERIFICABILE come valutazione dei livelli; record classificato NON_TRADE, non un trade.** Non è disponibile una serie successiva con provider, ticker e scadenza identici. Non si può stabilire se i livelli siano stati raggiunti o superati.

### PR e correzioni SPUTNIK

- [PR #155 — diagnostica dei gap schedulati](https://github.com/andreameloni1984-sys/trump-trucker/pull/155): OPEN, non draft, 2 commit, base uguale a main. Aggiunge permesso read-only `actions: read` e stampa ultime 20 run schedulate/gap, fail-open. Non cambia il cron e non può far emettere a GitHub gli eventi mancanti. CI del 9 novembre: ranking **185 test SUCCESS** ([run](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42611284354)); item intelligence **46 test SUCCESS** ([run](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42611284334)). Non integrata.
- [PR #154 — classificazione tariffaria](https://github.com/andreameloni1984-sys/trump-trucker/pull/154): OPEN; ranking e intelligence CI SUCCESS; non integrata.
- [PR #153 — propagazione direzione tecnica nella card CFD](https://github.com/andreameloni1984-sys/trump-trucker/pull/153): OPEN; CI SUCCESS; non integrata.
- [PR #131 — endpoint White House RSS](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): OPEN; CI SUCCESS sul commit più recente; non integrata. Il run #293 continua a usare il vecchio endpoint.

Il file `sputnik_state.json` è presente su main (1.399.279 byte, blob SHA `ca9cf9e5bf065da6bf31fbf1fdfa2e5d30b6744d`); il lettore file non ha restituito il contenuto per le dimensioni, quindi questo audit non attribuisce nuovi eventi dal solo file.

### Daily summary / Telegram

Il run [SPUTNIK Daily Summary #11](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42480644139) è SUCCESS come job, ma il log contiene `Missing Telegram secrets; summary was not sent.` È un percorso separato dal collector #293. Nel collector #293 token/chat ID risultano presenti e gli ACK API dei messaggi #746–#748 sono espliciti; nessuna prova di consegna/visualizzazione sul dispositivo.

## 3. GAGARIN — ultima produzione

### Run produttiva

[GAGARIN Monitor #172](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716)
- Evento: `schedule`; branch `main`.
- Avvio: **2026-11-09 06:34:18 UTC**.
- Fine: **06:34:37 UTC**.
- Esito GitHub Actions: SUCCESS.
- Job ID: `129017049476`.

Il job espone `DATABASE_URL` vuota e `PAPER_TRADING_ONLY=1`. Soglie runtime stampate: Probability 40, Quality 30, Confidence 35, RR 2,5, Max Stop ATR 2,5.

### Quotazioni e candidati

| Strumento | Provider | Età | Stato |
|---|---|---:|---|
| Soia | YAHOO | 659,4 s | STALE |
| Brent | YAHOO | 603,0 s | STALE |
| WTI | YAHOO | 602,9 s | STALE |
| Argento | YAHOO | 609,5 s | STALE |
| Grano | YAHOO | 648,2 s | STALE |
| Rame | YAHOO | 613,7 s | STALE |
| Oro | YAHOO | 622,4 s | STALE |
| Mais | YAHOO | 686,3 s | STALE |
| EUR/USD | BIQUOTE | 273,0 s | LIVE, contesto |
| GBP/USD | BIQUOTE | 273,6 s | LIVE, contesto |

I timestamp assoluti delle singole quotazioni, i ticker provider esatti e le scadenze non sono esposti dal log.

Candidata Soia:
- generazione: **06:34:30.263983 UTC**;
- ticker logico: `SOYBEAN/USD`;
- direzione SHORT; Probability 63, Quality 55,5, Confidence 35;
- provider YAHOO, età 659,4 s;
- stato `PAPER_WATCH`;
- blocchi: `LIVE_DATA_NOT_FRESH`, `TRIGGER_NOT_CONFIRMED`, `TRIGGER_DIRECTION_MISMATCH`, `FINAL_CONFLUENCE_FAIL`;
- entry, SL, TP e ATR assenti; nessun invio per questa candidata.

Non è un trade e non è valutabile come esito.

Il messaggio #3728 è stato accettato dall'API alle **06:34:34.1131912 UTC**, round-trip 478 ms; il corpo non è conservato, quindi non è possibile attribuirgli strumento, direzione o livelli.

Output finale del motore:
`Recorded entries: 0`; `Updated open outcomes: 0`; `New feedback signals: 0`; `New additional live forecasts: 0`; `signals=0 open=0 closed=0`; win rate/avg R N/D.

## 4. GAGARIN — journal e feedback

Verificati su main:
- `commodities_prediction_log.json`: **981** record; ultimo `created_at` **2026-09-15 15:45:04.462276 UTC**; 945 PENDING e 36 NEUTRALE. I 21 record con action `COMPRA ORA` sono ancora PENDING; non sono fill.
- `journal.csv`: 11 righe del 17 ottobre, tutte `nessun segnale`, senza entry/SL/TP.
- `paper_trade_log.csv`: un WTI `LEGACY_IMPORT`, provider/ticker/quote timestamp vuoti, nota esplicita “Nessun esito”.
- `data/paper_open.json`: WTI P0001 OPEN, P&L null, record legacy.
- `position.json`: vecchia posizione Heating Oil LONG, aperta 15 settembre; nessuna prova di fill o serie contrattuale.
- `commodities_monitor_state.json`: timestamp 17 settembre.
- `commodities_daily_report_state.json`: ultimo report 10 settembre, evaluated 0, pending 24.
- `gagarin_feedback.csv`: HTTP 404.
- `GAGARIN_RESEARCH_LOG.md`: ultimo elemento datato 4 novembre 2026.

Questi file non costituiscono un journal operativo aggiornato. Nessuna persistenza durevole del feedback è dimostrata dal job #172.

### Universo e PR GAGARIN

- [PR #241 — disabilitare Argento](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/241): OPEN, DRAFT, 8 commit; non integrata. CI principale fallita: **2 failed, 569 passed**. I test `argento` e `silver` falliscono perché il resolver restituisce ancora l'oggetto XAG disabilitato invece di `None`. Quattro altri workflow associati sono SUCCESS. Su main Argento resta attivo e compare nella run #172.
- [PR #219 — rimuovere Forex dall'universo](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219): OPEN, non integrata; il run #172 mostra ancora EUR/USD e GBP/USD come contesto.
- [PR #225 — offset cron GAGARIN](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225): OPEN, DRAFT, 2 commit. Propone `7,22,37,52 * * * *`, mantenendo 15 minuti ma evitando il bordo dell'ora. I cinque workflow CI del 7 novembre sono SUCCESS; non integrata. Main conserva `*/15 * * * *`.
- [PR #240 — sopprimere livelli LUBJANKA stale](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/240): OPEN, DRAFT, non integrata.
- [PR #192 — identità contratto e outcome ambiguo](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, non integrata. Il diff aggiunge provider, quote symbol, market type e scadenza al record/fingerprint; `_market_contract_match` controlla quote symbol, market type e identità contratto ma **non confronta quote_provider** tra segnale e candele successive. La correzione del doppio tocco SL/TP in stessa candela come ESITO NON VERIFICABILE è presente nel branch, non su main.
- [PR #239 — evidenza identità CFD/scadenza](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/239) resta DRAFT; la protezione per scadenze passate è proposta separatamente in [PR #217](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/217), anch'essa DRAFT e non integrata nella catena #239.

Su main, `engine/feedback.py` abbina le serie per symbol/timeframe; in caso di candela che tocca SL e TP applica STOP. Non usare gli outcome di main come certificazione conforme al protocollo PRAVDA.

## 5. Continuità delle GitHub Actions

Interrogata la lista `event=schedule` (ultime 100 run restituite, ordinate per data). Ultime run produttive:
- SPUTNIK collector #293: **06:01:41 UTC**.
- SPUTNIK Telegram polling #53: **05:55:47 UTC**.
- GAGARIN monitor #172: **06:34:18 UTC**.

Al cut-off 11:46:06 UTC, gap:
- collector SPUTNIK: **5h44m25s**;
- polling SPUTNIK: **5h50m19s**;
- monitor GAGARIN: **5h11m48s**.

Cron su main:
- SPUTNIK collector: `2-59/5 * * * *`;
- SPUTNIK polling: `*/5 * * * *`;
- GAGARIN monitor: `*/15 * * * *`.

Le run SPUTNIK delle 11:43:31 UTC sono due CI della PR #155 (185 + 46 test), non run del collector. Le numerose run push/PR sul branch #241 sono test, non monitor di mercato. La causa delle schedule mancanti non è dimostrata.

## 6. Esiti e statistiche

- Segnali con entry/SL/TP ma non eseguiti o senza identità completa: **NON_TRADE / ESITO NON VERIFICABILE**, non operazioni.
- Candidata Soia: bloccata, senza livelli.
- Nessuna serie di candele successive identificata con stesso provider, ticker, mercato e scadenza.
- SL verificati: **0**.
- TP verificati: **0**.
- Fill verificati: **0**.
- Win rate, average R, total R: **N/D**.

Nessun backtest o risultato è stato inventato.

## 7. Fonti consultate

- [SPUTNIK Actions #293](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770)
- [SPUTNIK Polling #53](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570062235)
- [SPUTNIK PR #155](https://github.com/andreameloni1984-sys/trump-trucker/pull/155)
- [SPUTNIK PR #154](https://github.com/andreameloni1984-sys/trump-trucker/pull/154)
- [SPUTNIK PR #153](https://github.com/andreameloni1984-sys/trump-trucker/pull/153)
- [SPUTNIK PR #131](https://github.com/andreameloni1984-sys/trump-trucker/pull/131)
- [GAGARIN Actions #172](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716)
- [GAGARIN PR #241](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/241)
- [GAGARIN PR #225](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225)
- [GAGARIN PR #240](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/240)
- [GAGARIN PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192)
- [GAGARIN PR #239](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/239)
- [GAGARIN PR #217](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/217)

## 8. Prossimo controllo

1. Verificare se le schedule riprendono e leggere i nuovi log di collector/monitor.
2. Verificare il log di diagnostica proposto dalla PR #155 dopo eventuale integrazione.
3. Controllare l'eventuale integrazione della PR #225 e il cron effettivo su main.
4. Verificare il resolver Argento nella PR #241; fino all'integrazione, main continua a includerlo.
5. Verificare il matching esplicito del provider nella PR #192.
6. Verificare la protezione per scadenze future già scadute prima di qualsiasi registry CFD.
7. Verificare scrittura e rilettura del journal persistente.
8. Accettare esiti SL/TP solo con serie successive dello stesso identico ticker, provider, mercato e contratto, con ordine temporale determinabile.

## Verifica di perimetro

Questo audit ha aggiunto solo documentazione PRAVDA su un branch separato. Ledger ereditato senza modifiche. Nessun codice, strategia, filtro, punteggio o rischio modificato; nessun merge/deploy, ordine reale, modifica a secret o Render. Nessun servizio a pagamento. Nessun accesso a Trading 212 o consegna Telegram al dispositivo dichiarati.
