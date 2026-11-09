# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-09 02:38:33 UTC (03:38:33 Europe/Rome)**

## Sintesi

Audit svolto sui due repository, sugli ultimi job log produttivi disponibili, sui workflow main, sugli artefatti journal/feedback, sul ledger PRAVDA e sulle PR correnti.

**Non è emerso un nuovo segnale operativo da aggiungere al ledger.** Le ultime notifiche attribuibili restano SPUTNIK #743/#744/#745 e GAGARIN #3727. Sono già registrate. Non sono state aggiunte righe né alterato il CSV.

Nuove evidenze rispetto al controllo precedente:
- SPUTNIK PR #152 corregge l'etichetta fuorviante del brief giornaliero; è OPEN, non draft, 3 commit avanti e 0 indietro, con 231 test CI superati.
- GAGARIN PR #239 richiede prove esplicite per tipo di contratto e scadenza, anche per SPOT/no-expiry; è ancora DRAFT e non aggiunge un feed o quotazioni.
- La revisione indipendente del feedback engine conferma che su main il matching è soltanto per symbol/timeframe (con fallback su symbol univoco), senza provider, ticker quote, mercato o scadenza. La PR #192 migliora il matching e il doppio tocco, ma non confronta ancora esplicitamente il provider.

## 1. Ledger e integrità

Ledger cumulativo ereditato dal branch precedente:
[pravda-signal-ledger-2026-11-09.csv](pravda-signal-ledger-2026-11-09.csv)

SHA blob: a5211b7e5515860443f3860b374e294cd7465bca.

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

I record più recenti sono già presenti:
- SPUTNIK #743: bias preliminare GOLD SHORT.
- SPUTNIK #744: GOLD EARLY_SETUP, NOT_EXECUTED.
- SPUTNIK #745: brief giornaliero informativo.
- GAGARIN #3727: WATCH pre-alert senza corpo conservato né attribuzione strumento.

Non si aggiunge una nuova riga per PR, CI o messaggi già registrati. Win rate, average R e total R restano N/D: campione di fill verificati pari a zero.

Campi assenti/non valorizzati nel CSV (conteggio su 98 righe; alcuni campi non sono applicabili ai messaggi informativi):
- quote timestamp: 70;
- ATR: 85;
- ticker: 44;
- market type: 50;
- scadenza: 52;
- provider: 28;
- entry/SL/TP1: 69 ciascuno.

## 2. SPUTNIK — ultima produzione ispezionata

Run [#292](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537803167), job ID 128905894291, SUCCESS. Il log va da 2026-11-08 23:59:49 UTC a 23:59:56 UTC; il riepilogo run indica avvio 23:59:46 e completamento 23:59:58 UTC.

### Distinzione test/runtime

Le righe OSError per WHITE_HOUSE, TRUTH_ARCHIVE e OGE e le righe di conferma GAGARIN compaiono nello step dei test automatici prima di python trump_tracker.py. Non sono errori o conferme del runtime produttivo.

Nel runtime:
- SEC: HTTP 403, cooldown 21.600 secondi.
- White House RSS: HTTPError sull'endpoint https://www.whitehouse.gov/feed/.
- Public intelligence scan: 1 finding.
- Il messaggio GOLD dichiara NO_DIRECTIONAL_NEWS.
- NARWHAL reference è abilitato, ma la chiave è vuota/non configurata; nessun prezzo utilizzabile.
- GAGARIN handoff: URL e API key vuote; non risulta un inoltro esterno.

### Messaggi effettivi

| ID | Generazione UTC | Invio/API UTC | Contenuto | Valutazione |
|---|---|---|---|---|
| #743 | 23:59:54.842537 | 23:59:54.843863 | GOLD SHORT preliminare; momentum 5m -0,061%; NO_DIRECTIONAL_NEWS | NON_TRADE |
| #744 | 23:59:54.843913 | 23:59:54.844979 | GOLD EARLY_SETUP SHORT | NOT_EXECUTED, NON_TRADE |
| #745 | 23:59:54.845051 | 23:59:54.845432 | Brief informativo | NON_TRADE |

L'API ha accettato #743/#744/#745 rispettivamente in 401/396/364 ms. È prova di risposta positiva API, non della visualizzazione sul dispositivo.

**#744 — livelli riportati, ma non valutabili come trade**
- Entry 4069.1001
- SL 4071.9929
- TP1 4066.2073
- TP2 4063.3145
- ATR 1.9285
- Direzione tecnica SHORT; D-L-A NEUTRAL / NO_DIRECTION / NOT_ASSESSED.
- Stato esplicito: NOT_EXECUTED.

Il titolo parla di CFD, mentre il corpo identifica un future continuo front-month. Ticker esatto, provider, timestamp della quotazione, mercato e scadenza effettiva non sono esposti; l'indipendenza della serie upstream non è verificata. Il messaggio avverte di non usare i livelli. Non esiste quindi una serie dello stesso contratto su cui valutare SL prima o TP prima. Score 100 non equivale a validità operativa.

**#745 — etichetta oraria fuorviante**
Il brief è stato inviato alle 23:59:54 UTC (00:59:54 Europe/Rome), ma il titolo diceva “BRIEF ORE 05:00”. Il brief è first-scan-driven dopo la PR #149, non un invio alle 05:00. La nuova [PR #152](https://github.com/andreameloni1984-sys/trump-trucker/pull/152) corregge soltanto titolo/docstring e aggiunge una regressione. È OPEN, non draft, 3 commit avanti/0 indietro rispetto a main. CI head: ranking #650 SUCCESS (185 test), item intelligence #260 SUCCESS (46 test), totale 231. Non è integrata.

### Altre PR SPUTNIK

- [#150 — non ripetere raccomandazioni senza nuovo item RSS](https://github.com/andreameloni1984-sys/trump-trucker/pull/150): OPEN; 2 avanti/2 indietro rispetto a main corrente; CI #648/#258 SUCCESS (185+46). Non integrata.
- [#131 — nuovo endpoint White House RSS](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): OPEN; 1 avanti/1 indietro; CI #649/#259 SUCCESS (184+45). Non integrata; il runtime #292 usa ancora /feed/ e registra HTTPError.
- [#147 — rimozione handoff GAGARIN](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN; 1 avanti/9 indietro.
- [#145 — diagnostica quotazioni](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN; 1 avanti/11 indietro.
- [#144 — persistenza separata](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN; 1 avanti/42 indietro.
- [#149](https://github.com/andreameloni1984-sys/trump-trucker/pull/149): MERGED; rimosso il gate orario fisso del brief.

Il workflow .github/workflows/trump_tracker.yml su main conserva cron 2-59/5 * * * *, permissions: contents: write e uno step che committa/pusha sputnik_state.json su main. Il commit più recente visibile è 15f34dfe1e9866755bc2604e58ce8b582e34b5ac (“chore: persist Sputnik state”, 23:59:54 UTC). La PR #144 non è integrata.

## 3. GAGARIN — ultima produzione ispezionata

Run [#171](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42538235058), job ID 128907219566, SUCCESS. Log: 2026-11-09 00:04:54–00:05:07 UTC; run indicata dalle Actions intorno a 00:04:51–00:05:10 UTC.

Il job stampa DATABASE_URL vuota in tutti gli step. Il workflow dichiara che il journal è dato operativo privato, non va committato nel repository pubblico e che la persistenza sarà riattivata solo dopo deploy e verifica dello storage privato.

### Quotazioni e blocchi

Il monitor dichiara 10 strumenti: 8 commodity operative e 2 Forex ausiliari di contesto.

| Strumento | Provider | Età quote | Stato |
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

Per le commodity il log non espone timestamp assoluto della candela, ticker risolto, mercato e scadenza. Le due coppie Forex sono marcate “CONTESTO FX — NON OPERATIVO”.

WTI appare LONG nella classifica (probabilità 63, qualità 52,5, confidenza 35), ma resta PAPER_WATCH: il log riporta dati non freschi, trigger non confermato, mismatch direzionale e RR_FAIL. Non è un ingresso.

Risultati:
- Recorded entries: 0.
- New feedback signals: 0.
- New additional live forecasts: 0.
- signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0.
- Telegram #3727: API SEND CONFIRMED, 403 ms; il corpo non è conservato, quindi nessuna attribuzione a strumento/ticker/direzione/livelli. Non è un trade.

### Journal e archivio storico

File letti su main:
- journal.csv: 11 righe del 17 ottobre, tutte “nessun segnale”.
- paper_trade_log.csv: WTI LONG del 8 ottobre marcato LEGACY_IMPORT, senza esito.
- position.json: vecchia posizione Heating Oil LONG del 15 settembre.
- data/paper_open.json: WTI P0001 OPEN legacy.
- gagarin_feedback.csv: 404, assente.

Questi artefatti non provano fill e non sono stati contati come trade. Le posizioni legacy non sono riconciliate con il monitor corrente.

commodities_prediction_log.json contiene 981 record; ultimo created_at 2026-09-15 15:45:04 UTC. Stati: 945 PENDING, 36 NEUTRALE. Azioni: 21 COMPRA ORA, tutte PENDING. operational_signal: 960 WAIT, 15 LONG, 6 mancanti. Nessuno di questi record è prova di esecuzione.

## 4. Outcome engine — difetto dimostrato

Su main, engine/feedback.py:
- associa le serie per (symbol, timeframe), con fallback al solo symbol quando esiste una sola serie;
- non verifica provider, quote ticker, market type, contract month o expiry;
- se la stessa candela OHLC tocca SL e TP, controlla prima stop_hit e registra STOP.

Con OHLC della stessa candela non si conosce l'ordine intrabar: secondo il protocollo PRAVDA l'esito deve essere ESITO NON VERIFICABILE, non STOP.

La [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) aggiunge quote symbol, market type, mese/scadenza futures e gestisce il doppio tocco come ESITO NON VERIFICABILE. È OPEN, 6 avanti/6 indietro; le sei CI associate risultano SUCCESS. Ma la funzione _market_contract_match() sul branch non confronta esplicitamente il provider del segnale con quello delle candele successive. Correzione non integrata e ancora incompleta su questo punto.

## 5. PR GAGARIN e workflow

- [#239 — prove esplicite per tipo contratto e scadenza](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/239): OPEN/DRAFT, impilata su #238; CI #1960 e #3833 SUCCESS. Richiede evidenza esplicita anche per SPOT/no-expiry. Non autentica un feed; registry ancora vuoto.
- [#238](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/238) e [#237](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/237): OPEN/DRAFT, catena di separazione app symbol, catalogue ticker/slug e broker/feed symbol.
- [#234](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/234) e [#235](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/235): OPEN/DRAFT, journal CFD PAPER isolato e persistenza durevole non integrati.
- [#221](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): OPEN/DRAFT, 14 avanti/3 indietro; consolidamento universo a otto commodity e rimozione route FX non integrati.
- [#223](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): OPEN/DRAFT, 10 avanti/3 indietro; M5 osservativo a sette strumenti, senza entry/SL/TP, journal o alert. L'esclusione Argento riguarda soltanto questa scansione M5 proposta, non il monitor completo.
- [#225](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225): OPEN/DRAFT, 2 avanti/3 indietro; propone offset cron.
- [#222](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222): MERGED; rimosso il veto intraday session_ok, restano gli altri controlli indipendenti.

Il workflow main .github/workflows/gagarin-monitor.yml conserva cron */15 * * * *. La PR #225 non è integrata. Il workflow non committa i journal pubblici e la persistenza resta disattivata/non dimostrata.

## 6. Continuità e limiti della verifica

Ultimi log produttivi che ho potuto ispezionare:
- SPUTNIK #292: completamento 2026-11-08 23:59:58 UTC; al cut-off erano trascorsi circa 2h38m35s.
- GAGARIN #171: completamento circa 2026-11-09 00:05:10 UTC; al cut-off erano trascorsi circa 2h33m23s.

I cron configurati restano rispettivamente ogni 5 minuti (offset al minuto 2) e ogni 15 minuti. Il connettore GitHub utilizzato in questo controllo non espone un elenco paginato completo delle run Actions; quindi questi sono gli ultimi log recuperati, non una prova assoluta che non esistano run successive. Non attribuisco una causa al gap senza il run listing completo.

Gli endpoint artefatti delle due run non restituiscono workflow artifacts.

## 7. Esiti e statistiche

- Nuovi record eleggibili: 0.
- Nuovi fill verificati: 0.
- Nuovi SL/TP verificati: 0.
- Campione di performance verificabile: 0.

Nessun prezzo spot generico, future continuo o contratto con scadenza diversa è stato usato per stimare l'esito di #744 o dei record storici. Tutte le valutazioni non supportate da una serie esatta restano non verificabili.

## 8. Fonti consultate

- [SPUTNIK Actions #292](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42537803167), job log completo e lista artefatti.
- [GAGARIN Actions #171](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42538235058), job log completo e lista artefatti.
- Workflow main: .github/workflows/trump_tracker.yml, .github/workflows/gagarin-monitor.yml.
- Ledger PRAVDA CSV e rapporto precedente.
- commodities_prediction_log.json, journal.csv, paper_trade_log.csv, position.json, data/paper_open.json, ricerca di gagarin_feedback.csv.
- engine/feedback.py su main e sul branch PR #192.
- Metadati, confronti commit e CI delle PR #152, #150, #131, #147, #145, #144, #192, #239, #238, #237, #234, #235, #221, #223, #225 e #222.

## 9. Prossimo controllo

1. Ottenere/consultare il run listing Actions completo per distinguere con certezza l'ultimo schedule run da CI e misurare il ritardo reale.
2. Verificare eventuali nuovi messaggi SPUTNIK senza contarli due volte e distinguere sempre test da runtime.
3. Verificare se #152 e #131 vengono integrate e se il nuovo endpoint White House funziona nel runtime.
4. Verificare le prime quotazioni commodity fresche con provider, timestamp assoluto, ticker, mercato e scadenza.
5. Seguire #192 e verificare il confronto provider prima di considerare affidabile l'outcome engine.
6. Verificare persistenza journal soltanto con prova di scrittura e successiva lettura.
7. Aggiungere record solo per nuovi eventi identificabili; outcome soltanto da prezzi successivi dello stesso identico strumento/contratto.

**Sicurezza:** nessuna modifica a codice applicativo, strategia, filtri, punteggi o rischio; nessun merge/deploy, ordine reale, modifica a secret o Render. Nessun servizio a pagamento. ACK Telegram significa soltanto risposta positiva API, non consegna al dispositivo. Nessun accesso a Trading 212/feed CFD dichiarato. PAPER ONLY.
