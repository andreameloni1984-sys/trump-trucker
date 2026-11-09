# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**9 novembre 2026 — 07:37 UTC (08:37 Europe/Rome)**

## Esito sintetico

Verificati direttamente tramite GitHub API:
- ultime 100 GitHub Actions per ciascun repository;
- job e log completi delle ultime run produttive disponibili;
- workflow YAML e cron effettivi;
- PR rilevanti e relativi check CI;
- ledger PRAVDA cumulativo;
- journal, prediction log, position state e codice outcome GAGARIN.

Nessuna nuova run schedulata dopo le ultime produzioni osservate:
- SPUTNIK collector #293: 2026-11-09 06:01:41 UTC, SUCCESS;
- SPUTNIK polling #53: 2026-11-09 05:55:47 UTC, SUCCESS;
- GAGARIN monitor #172: 2026-11-09 06:34:18 UTC, SUCCESS.

Al cut-off 07:37:24 UTC i gap erano rispettivamente 1h35m43s, 1h41m37s e 1h03m06s. I cron presenti nei workflow sono SPUTNIK 2-59/5 * * * *, polling */5 * * * *, GAGARIN */15 * * * *. Le CI delle PR non sono run produttive. La causa dei gap non è dimostrata.

## 1. Ledger e deduplicazione

Ledger cumulativo consultato sul branch pravda/audit-2026-11-09-0642UTC:
- record: **103**;
- firme uniche: **103**;
- source ID unici: **103**;
- duplicati: **0**.

Le ultime registrazioni già presenti coprono SPUTNIK #746–#748 e GAGARIN candidato SOYBEAN/USD SHORT e messaggio #3728. Nessuna nuova produzione schedulata è comparsa dopo le run già registrate; **non sono state aggiunte righe**. Il CSV è stato ereditato senza modifiche.

Ledger: https://github.com/andreameloni1984-sys/trump-trucker/blob/pravda/audit-2026-11-09-0642UTC/reports/pravda-signal-ledger-2026-11-09.csv

## 2. SPUTNIK — run produttiva #293

Run: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770

Avvio 06:01:41 UTC; job completato con SUCCESS. Il log del collector mostra:
- SEC HTTP 403, cooldown 21.600 secondi;
- filing 0, transazioni 0;
- White House RSS sul vecchio endpoint https://www.whitehouse.gov/feed/: HTTPError;
- digest con due eventi individuali: post #43530 (pubblicato 2026-11-08 23:41:05 UTC) e post #43532 relativo a S.5653 (pubblicato 2026-11-09 00:05:49 UTC);
- il runtime dichiara tre correlazioni pubbliche, mentre il digest conserva due eventi individuali: la terza correlazione non è attribuibile dal messaggio.

Le righe OSError di WHITE_HOUSE/TRUTH_ARCHIVE/OGE che precedono il collector sono prodotte dal passo di test automatici, non dal runtime produttivo. Non sono conteggiate come errori del collector.

### Messaggi già registrati

| ID | Generazione UTC | Invio/API UTC | Contenuto | Classificazione PRAVDA |
|---|---|---|---|---|
| #746 | 06:01:48.1711626 | 06:01:48.1720275 | Digest informativo, due eventi | NON_TRADE |
| #747 | 06:01:48.1720811 | 06:01:48.1731760 | GOLD LONG 5m preliminare, momentum +0,077%/15m, nessun catalizzatore direzionale, nessun livello | NON_TRADE |
| #748 | 06:01:48.1732205 | 06:01:48.1742253 | GOLD LONG EARLY_SETUP | NOT_EXECUTED / NON_TRADE |

#748 riporta entry 4133.2002, SL 4130.5859, TP1 4135.8145, TP2 4138.4289, ATR 1.7429. Il log dice però esplicitamente:
- titolo CFD, corpo FUTURES_CONTINUOUS_FRONT_MONTH;
- scadenza esatta e indipendenza upstream non verificate;
- NARWHAL REF NOT_CONFIGURED e nessun prezzo utilizzabile;
- provider e timestamp della quotazione non esposti;
- D-L-A NEUTRAL/NO_DIRECTION e tecnica N/D, nonostante il messaggio #747 indichi LONG 5m;
- istruzione esplicita a non usare i livelli per entry/SL/TP.

Gli ACK API Telegram sono 563 ms (#746), 313 ms (#747) e 322 ms (#748). Sono conferme API, non prova di visualizzazione sul dispositivo. Nessun fill e nessun esito valutabile: non esiste una serie successiva identificata per lo stesso ticker/contratto.

### PR SPUTNIK

- PR #154, aperta e non merged: https://github.com/andreameloni1984-sys/trump-trucker/pull/154. Corregge il falso mapping TRADE_ESCALATION causato da menzioni generiche di “China/Xi”: richiede parole esplicite tariff/tariffs/trade war prima di applicare l'analogia tariffaria. La PR documenta che il post S.5653 è stato classificato su main come TRADE_ESCALATION e ha ereditato l'analogia tariffaria 2025, nonostante il contenuto fosse una proposta di permitting/energia. Check ranking #42577454924 e item-intelligence #42577454907: entrambi SUCCESS. Non integrata, quindi il difetto resta in produzione.
- PR #153, aperta e non merged: https://github.com/andreameloni1984-sys/trump-trucker/pull/153. Propaga la direzione tecnica 5m nella card CFD. Check ranking #42573153508 e Telegram menu #42573153515: SUCCESS. È pertinente alla discrepanza #747/#748.
- PR #150, aperta: https://github.com/andreameloni1984-sys/trump-trucker/pull/150. Impedisce di riemettere la coppia raccomandazione/CFD senza un nuovo RSS item-level valido; CI dichiarata nel PR: 231 test SUCCESS. Non integrata.
- PR #131, aperta: https://github.com/andreameloni1984-sys/trump-trucker/pull/131. Sostituisce il vecchio endpoint White House RSS con /news/feed/; 229 test SUCCESS, ma la run produttiva #293 usa ancora il vecchio endpoint e riceve HTTPError. Non integrata.

Nel job #293 NARWHAL_API_KEY è vuota. Nessun segreto è stato modificato.

## 3. GAGARIN — run produttiva #172

Run: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716

Avvio 06:34:18 UTC, fine 06:34:37 UTC, SUCCESS. Il log mostra DATABASE_URL vuota e PAPER_TRADING_ONLY=1. Soglie caricate dal workflow: probability 40, quality 30, confidence 35, RR 2.5. Sono valori osservati, non modificati da PRAVDA.

### Quotazioni

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
| EUR/USD | BIQUOTE | 273,0 s | LIVE, contesto FX non operativo |
| GBP/USD | BIQUOTE | 273,6 s | LIVE, contesto FX non operativo |

I timestamp assoluti delle quotazioni e i ticker Yahoo risolti non sono esposti nel log.

Candidata Soia:
- ticker logico SOYBEAN/USD, provider YAHOO, età 659,4 s;
- SHORT, probability 63, quality 55,5, confidence 35;
- PAPER_WATCH / NOT_AUTHORIZED;
- blocchi: LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, FINAL_CONFLUENCE_FAIL;
- nessuna entry, SL, TP o ATR; market type e scadenza non esposti.

Il messaggio #3728 è stato accettato dall'API in 478 ms, ma il corpo non è conservato: nessuna attribuzione di strumento o direzione. API ACK non equivale a prova di consegna sul dispositivo.

Riepilogo run: recorded entries 0; updated open outcomes 0; new feedback signals 0; signals=0 open=0 closed=0. Nessun trade.

## 4. Journal e feedback GAGARIN

File letti direttamente da main:
- journal.csv: 11 righe datate 2026-10-17, tutte “nessun segnale”;
- paper_trade_log.csv: una sola riga WTI del 2026-10-08, LEGACY_IMPORT / PAPER_ENTRY / OPEN, entry 96.24, stop 89.37, TP1 103.11, TP2 106.55; nessun esito e nessun provider/mercato/scadenza della quotazione;
- position.json: vecchia posizione Heating Oil LONG HO/USD, aperta 2026-09-15, entry 4.8844, stop 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882, ancora senza chiusura documentata;
- commodities_monitor_state.json: timestamp 2026-09-17;
- commodities_prediction_log.json: 981 record dal 10 al 15 settembre; ultimo 2026-09-15 15:45:04 UTC. Azioni: 77 NON ENTRARE, 576 ATTENDERE, 15 SHORT—ASPETTARE CONFERMA, 292 LONG—ASPETTARE CONFERMA, 21 COMPRA ORA. Stato: 945 PENDING, 36 NEUTRALE.

I record LEGACY_IMPORT/OPEN e le previsioni PENDING non sono fill. Il tree di main non contiene un gagarin_feedback.csv; la run #172 mostra DATABASE_URL vuota. Non è dimostrata persistenza durevole o lettura/scrittura condivisa del feedback.

## 5. Universo Argento e PR GAGARIN

La run #172 continua a includere Argento (XAG/USD) nel monitor: la PR #241 non è integrata.

Rettifica di audit: la richiesta più recente dell'utente (6 novembre) è di escludere Argento dalla scansione perché troppo volatile. La PR #241 è quindi coerente con l'ultima istruzione sul perimetro. Il precedente commento PRAVDA che affermava il contrario è stato corretto sullo stesso commento GitHub:
https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/241#issuecomment-6734073910

La PR #241 resta aperta/non merged. I check sono quattro SUCCESS e un FAILURE: run #42574224863, 2 failed / 569 passed. I test test_removed_commodities_are_not_resolved[argento] e [silver] falliscono perché _resolve_commodity() restituisce ancora l'oggetto XAG con enabled=False invece di None. Il difetto dimostrato è nel resolver alias; il perimetro di esclusione è quello richiesto.

PR #240, aperta/non merged: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/240. Sopprime i livelli LUBJANKA quando quote o M5 sono stale oltre 600s; cinque workflow CI SUCCESS. Non è ancora in main.

PR #238/#239, entrambe DRAFT e non integrate: separano app symbol, catalogue ticker/slug e broker symbol e richiedono prove esplicite per tipo contratto/scadenza. Il registry resta vuoto; non viene fornito un feed CFD o un quote adapter. Nessun accesso Trading212 è dimostrato.

## 6. Outcome engine — difetto confermato

Su main, engine/feedback.py:
- il fingerprint contiene symbol, direction, timeframe, entry, stop, TP e bar timestamp, ma non provider, quote symbol, market type, contract month o expiry;
- il matching delle serie successive usa symbol/timeframe;
- se la stessa candela OHLC tocca SL e TP, il codice classifica STOP prima di TP.

PR #192 è aperta/non merged: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192
Sul suo branch il fingerprint include provider, quote symbol, market type, contract month ed expiry; il matching verifica quote symbol, market type e identità futures. Il doppio tocco è correttamente ESITO NON VERIFICABILE. Resta però assente il confronto esplicito del provider della serie successiva con il provider registrato nel segnale: _market_contract_match() confronta ticker, market type e scadenza, ma non quote_provider. La PR è quindi una correzione parziale rispetto al protocollo PRAVDA.

## 7. Statistiche e valutazione esiti

Campione storico ledger: 103 record, 103 firme uniche, 103 source ID unici, zero duplicati.
- Fill verificati: 0.
- SL verificati: 0.
- TP verificati: 0.
- Esiti di trade verificabili: 0.

#748 è NOT_EXECUTED, non un trade. La candidata Soia è NOT_AUTHORIZED e non ha livelli. Le vecchie posizioni WTI/Heating Oil non hanno fill verificati. Non esistono quindi win rate, average R o total R calcolabili: N/D.

Non è stato possibile verificare SL prima di TP o TP prima di SL per nessun campione. Mancano prezzi/candele successivi con identico ticker, provider, mercato e contratto/scadenza.

## 8. Fonti consultate

- SPUTNIK run #293 e log: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770
- SPUTNIK polling #53: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570062235
- GAGARIN run #172 e log: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716
- SPUTNIK PR #154: https://github.com/andreameloni1984-sys/trump-trucker/pull/154
- SPUTNIK PR #153: https://github.com/andreameloni1984-sys/trump-trucker/pull/153
- SPUTNIK PR #150: https://github.com/andreameloni1984-sys/trump-trucker/pull/150
- SPUTNIK PR #131: https://github.com/andreameloni1984-sys/trump-trucker/pull/131
- GAGARIN PR #241: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/241
- GAGARIN PR #240: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/240
- GAGARIN PR #192: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192
- GAGARIN PR #238/#239: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/238 e https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/239

## 9. Prossimo controllo

1. Recuperare nuove run schedulate e verificare la ripresa della cadenza.
2. Verificare la classificazione del post S.5653 dopo eventuale integrazione PR #154.
3. Verificare il nuovo endpoint White House solo dopo integrazione PR #131.
4. Verificare la direzione tecnica nella card CFD dopo eventuale integrazione PR #153.
5. Verificare la correzione alias Argento nella PR #241; non considerare esclusione attiva finché main continua a mostrarlo.
6. Verificare nuove quotazioni commodity con timestamp, provider, ticker, mercato e scadenza.
7. Verificare persistenza del feedback con scrittura e successiva lettura.
8. Richiedere provider matching esplicito nella PR #192.
9. Valutare gli esiti soltanto su candele successive dello stesso identico strumento/contratto.

**Sicurezza:** nessun codice applicativo modificato; nessuna strategia, soglia, filtro, punteggio o rischio cambiato; nessun merge/deploy, ordine reale, secret, Render o servizio a pagamento toccato. PAPER ONLY.
