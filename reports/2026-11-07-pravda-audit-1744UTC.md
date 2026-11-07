# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Data controllo:** 7 novembre 2026, 17:44 UTC (18:44 Europe/Rome)  
**Modalità:** PAPER ONLY — audit in sola lettura; nessun ordine, merge, deploy o rerun.

## 1. Sintesi e perimetro

Sono state interrogate le prime 30 GitHub Actions recenti per ciascun repository, recuperati i job e i log completi degli ultimi monitor di mercato individuati, verificati i file del journal, i driver, il ledger PRAVDA e lo stato/diff delle PR pertinenti.

**Ultimi monitor di mercato individuati:**

| Bot | Run | Inizio UTC | Fine UTC | Età al controllo | Esito |
|---|---:|---:|---:|---:|---|
| SPUTNIK | [#42388887315](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42388887315) | 15:57:48 | 15:58:04 | 1h46m54s | SUCCESS |
| GAGARIN | [#42386803148](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42386803148) | 15:31:37 | 15:31:58 | 2h13m05s | SUCCESS |

Nelle prime 30 run recenti non risultano monitor di mercato programmati successivi a questi due. Sono presenti workflow distinti di polling, riepilogo, aggiornamento driver e test PR: non sono conteggiati come scansioni. L'enumerazione è limitata alla prima pagina di 30 run per repository; non si afferma di aver esaminato tutte le 1.513/14.213 run storiche.

Entrambi i monitor esaminati non hanno artifact Actions associati.

## 2. SPUTNIK — run #42388887315

### Raccolta e fonti
- 30 test di regressione eseguiti prima del collector nella run produttiva; i test sono separati dai finding reali.
- SEC: HTTP 403, cooldown 21.600 secondi, 0 filing.
- White House RSS: HTTPError.
- Intelligence pubblica: 1 finding.
- Nessuna operazione documentata.
- Handoff GAGARIN disabilitato perché GAGARIN_CLOUD_API_URL/API_KEY non configurati.
- NARWHAL_API_KEY vuoto/non configurato.

Il finding persistito nel commit [efaa67a](https://github.com/andreameloni1984-sys/trump-trucker/commit/efaa67a227abf8cebfb5eff2b64ad60bece10506) è:
- ID: `df6c3173377e2a283c05395c`;
- fonte: TRUTH_ARCHIVE;
- URL: homepage generale dell'archivio;
- titolo e timestamp individuale di pubblicazione: assenti;
- evidenza: `PUBLIC_SOURCE_TEXT_PAGE_LEVEL`;
- classificazione: `TRADE_ESCALATION` per analogia storica.

È un record page-level, non un singolo post datato e non prova un nuovo catalizzatore commodity.

### GOLD — messaggi #721 e #722
- strumento logico: GOLD;
- mapping configurato: GC=F;
- mercato dichiarato: futures continuous front-month;
- ticker runtime, provider effettivo, prezzo/timestamp della quotazione e scadenza esatta: non esposti/non verificati;
- bias: NEUTRAL;
- tecnica 5m: UNAVAILABLE;
- allineamento notizie: NO_DIRECTIONAL_NEWS;
- score: 70/100;
- decisione: WATCH / NO_DIRECTION;
- stato: NOT_EXECUTED;
- entry, SL, TP e ATR: assenti.

Il log avverte espressamente di non usare il continuous front-month per livelli operativi perché scadenza esatta e indipendenza upstream non sono verificate. Telegram API ha confermato #721 (738 ms) e #722 (485 ms). Il message_id 731 appartiene ai test e non è contato come invio produttivo. L'ACK API non prova la visualizzazione sul dispositivo.

### Persistenza e correzioni SPUTNIK
Il workflow su main continua a contenere `permissions: contents: write` e `git push origin main`. Il log della run #42388887315 conferma il push su main dopo il collector. La separazione non è ancora attiva.

**Progresso concreto — PR #144:** la PR [Persist SPUTNIK state outside main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144) è stata aggiornata sul main corrente:
- OPEN, non draft, non merged, mergeable;
- head `18ae5cd465edc063990d2984c8ff5ac7c024301e`;
- confronto con main `47d39ac892d949d6327b6ed929827bb869631912`: 1 commit avanti, 0 indietro;
- ranking CI [#42395679151](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42395679151): 193 test, SUCCESS;
- Telegram/menu CI [#42395679172](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42395679172): 66 test, SUCCESS.

Il diff della PR sposta il ripristino/salvataggio dello stato sul branch `sputnik-state`, con fallback temporaneo a main per la lettura, e rimuove il push del collector su main. Tuttavia una lettura diretta di `branches/sputnik-state` restituisce 404. Poiché la PR non è stata integrata, non esiste ancora una prova runtime del ciclo remoto branch-write/read. Nessun merge è stato eseguito da PRAVDA.

**PR #148:** [Stop repeating SPUTNIK recommendations](https://github.com/andreameloni1984-sys/trump-trucker/pull/148) è OPEN e non merged. Il confronto mostra 2 commit avanti e 21 indietro rispetto a main. Il diff propone di invocare il recommender soltanto con nuovi item pubblici individuali e datati; il codice su main continua invece a usare le ultime 30 voci di intelligence history insieme ai finding correnti. Il rischio di ripetere raccomandazioni da storia non è quindi risolto su main. Il run corrente ha emesso due messaggi GOLD neutrali, ma non è possibile dimostrare che il finding page-level sia stato l'unica causa.

## 3. GAGARIN — run #42386803148

### Configurazione runtime osservata
- PAPER_TRADING_ONLY=1.
- MONITOR_INTERVAL_MINUTES=15.
- soglie loggate nel run: probabilità 40, quality 30, confidence 35, RR 2.5.
- DATABASE_URL vuoto.
- NARWHAL_API_KEY vuoto.

Le soglie sono riportate come configurazione osservata, non come giudizio o modifica della strategia.

### Quotazioni
Tutte le otto commodity risultavano `MARKET_CLOSED`, provider Yahoo:
- Soia, Grano e Mais: età circa 73.013 secondi (20h17m);
- Brent, WTI, Oro, Argento e Rame: circa 63.412 secondi (17h37m).
- EUR/USD e GBP/USD erano contesto FX non operativo, provider BiQuote, anch'essi stale.

Ticker risolto, timestamp puntuale della quotazione, prezzo, market type e scadenza non sono stati esposti nel log. Le età sono quindi l'unica misura di freschezza disponibile; non consentono matching di contratto o valutazione di outcome.

### Classifica
| Strumento | Direzione | Prob. | Quality | Confidence | Stato |
|---|---|---:|---:|---:|---|
| Soia | — | 50 | 30 | 15 | PAPER_WATCH |
| Grano | — | 38 | 15 | 5 | PAPER_WATCH |
| Brent | — | 38 | 15 | 5 | PAPER_WATCH |
| WTI | — | 38 | 15 | 5 | PAPER_WATCH |
| Oro | — | 40 | 15 | 5 | PAPER_WATCH |
| Argento | LONG | 59 | 49,5 | 32 | PAPER_WATCH |
| Mais | — | 48 | 30 | 15 | PAPER_WATCH |
| Rame | — | 38 | 15 | 5 | PAPER_WATCH |

Argento è l'unico candidato direzionale. È bloccato da LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, CONFIDENCE_FAIL e FINAL_CONFLUENCE_FAIL. Non ha entry, SL, TP o ATR. Nessun ingresso è autorizzato.

Telegram API ha confermato il board #3715 in 489 ms, ma il corpo del messaggio non è conservato: l'esatta attribuzione del board a uno strumento non è dimostrabile. Il monitor riporta:
- Recorded entries: 0;
- Updated open outcomes: 0;
- New feedback signals: 0;
- New additional live forecasts: 0;
- signals=0 open=0 closed=0.

### Journal e legacy
Lettura diretta degli artefatti main:
- `journal.csv`: 11 righe, tutte annotazioni di nessun segnale;
- `data/paper_open.json`: WTI P0001 LONG, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55, status OPEN;
- `paper_trade_log.csv`: la stessa posizione WTI P0001, import legacy, nota “Chiusura spot 6 ottobre 2026. Nessun esito.”;
- `position.json`: Heating Oil LONG, entry 4,8844, SL 4,5418, TP1 5,4473, TP2 5,6284, TP3 5,882, opened_at 2026-09-15T13:23:44.547184Z;
- `gagarin_feedback.csv`: 404, file non presente nel repository consultato;
- `commodities_prediction_log.json`: 981 record; ultimi record del 15 settembre 2026, status PENDING.

WTI P0001 compare in due artefatti ma è una sola posizione legacy, non due trade. Per WTI e Heating Oil mancano prova di fill, provider, timestamp della quotazione, ticker esecutivo completo, market type e scadenza. Esito di entrambe: ESITO NON VERIFICABILE. Non sono state confrontate candele di strumenti/contratti non identificati.

Il run non ha artifact Actions associati. DATABASE_URL è vuoto, quindi non è dimostrato un archivio durevole condiviso tra monitor e riepilogo.

### Driver economici
Il driver snapshot [data/driver_snapshot.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/data/driver_snapshot.json), letto alle 13:37:41 UTC:
- EIA crude stocks: no_data;
- EIA gas storage: no_data;
- USDA wheat/corn/soybeans: valori assenti;
- FRED Dollar Index: 121,6656 al 30 ottobre;
- FRED real rate 10Y: 2,60 al 5 novembre.
Le variabili prive di dato restano UNKNOWN. Nessun catalizzatore aggiuntivo è dimostrato.

## 4. Correzioni GAGARIN e difetti residui

- [PR #192 — exact contract/outcome](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, non merged; 6 commit avanti e 4 indietro rispetto a main. Il diff aggiunge ticker, mercato, mese/scadenza e provider alla firma del segnale, e tratta SL+TP nella stessa candela come ESITO NON VERIFICABILE. Tuttavia `_market_contract_match` confronta quote symbol, market type e identità futures, ma non confronta `quote_provider` del segnale con il provider della serie successiva. La provenienza del provider è inclusa nella firma, ma non nel matching outcome: il requisito di identità completa non è ancora soddisfatto neppure nel diff esaminato.
- [PR #202 — durable journal](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): OPEN, DRAFT; 18 commit avanti e 2 indietro. La proposta PostgreSQL/DATABASE_URL non è attiva; il workflow main mostra DATABASE_URL vuoto. Rimane inoltre da chiarire la discrepanza tra la documentazione che menziona storage privato D1 e la proposta PostgreSQL.
- [PR #233 — CFD SPOT identity](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/233): OPEN, DRAFT, 2 commit avanti rispetto alla sua base `feat/gagarin-t212-cfd-identity-guard-20261106`; non è una PR basata direttamente su main e non abilita un feed Trading 212.
- [PR #30 — commodity universe](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/30): la precedente esclusione dell'Argento non risulta attiva su main; l'universo e il log del run lo includono ancora.

Il workflow Daily Summary GAGARIN [#42374841686](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42374841686) è SUCCESS, ma il file main `.github/workflows/daily-summary.yml` stampa “Summary sent” dopo la risposta HTTP senza interpretare `ok=true` e `result.message_id`. SUCCESS non prova l'accettazione Telegram.

## 5. Ledger PRAVDA e statistiche

Il ledger main [pravda-signal-ledger-2026-11-07.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-07.csv) è stato riletto e analizzato con parser CSV che rispetta i campi quotati.

| Indicatore | Risultato |
|---|---:|
| Record | 58 |
| Firme uniche | 58 |
| Source ID unici | 58 |
| Firme duplicate | 0 |
| Source ID duplicati | 0 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |
| Outcome finanziari verificabili | 0 |
| Win rate | N/D |
| Average R | N/D |

Le osservazioni dei run #42388887315 e #42386803148 (page-level intelligence, GOLD NO_DIRECTION, Argento WATCH e board #3715) erano già presenti nel ledger. Nessuna nuova riga è stata aggiunta per evitare duplicati. Il ledger resta invariato, blob SHA `f13f1a087561f08b32b0abc94f17c209175ad513`.

Non è disponibile un campione di trade eseguiti. NOT_EXECUTED, WATCH, score e predizioni PENDING non sono stati conteggiati come operazioni. Nessuna valutazione SL/TP è possibile senza fill e candele successive dello stesso provider, strumento e contratto.

## 6. Lacune e prossimo controllo

1. Dopo eventuale integrazione autorizzata della PR #144, verificare il primo ciclo reale di creazione/scrittura/lettura del branch `sputnik-state`; fino ad allora main continua a persistere lo stato.
2. Verificare su main il gate item-level della PR #148 prima di considerare risolte le raccomandazioni ripetute.
3. Alla riapertura dei mercati, verificare quotazioni fresche, ticker risolto, provider, timestamp, market type e scadenza per ogni strumento.
4. Verificare il journal GAGARIN tra due esecuzioni consecutive e chiarire il backend D1/PostgreSQL.
5. Verificare che il Daily Summary interpreti l'ACK Telegram e conservi message_id.
6. Correggere nel motore outcome la verifica del provider della serie successiva; mantenere ESITO NON VERIFICABILE quando identità o sequenza intrabar non sono dimostrabili.
7. Solo dopo un fill PAPER documentato, valutare le candele successive dello stesso identico strumento e contratto: SL prima, TP prima, oppure ESITO NON VERIFICABILE.

## 7. Fonti consultate

- Actions SPUTNIK: [monitor #42388887315](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42388887315), [polling #42387284361](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42387284361).
- Actions GAGARIN: [monitor #42386803148](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42386803148), [daily summary #42374841686](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42374841686), [fetch drivers #42377815727](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42377815727).
- CI PR #144: [ranking #42395679151](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42395679151), [Telegram/menu #42395679172](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42395679172).
- PR: [SPUTNIK #144](https://github.com/andreameloni1984-sys/trump-trucker/pull/144), [SPUTNIK #148](https://github.com/andreameloni1984-sys/trump-trucker/pull/148), [GAGARIN #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192), [GAGARIN #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202), [GAGARIN #233](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/233).
- File GAGARIN: `journal.csv`, `data/paper_open.json`, `paper_trade_log.csv`, `position.json`, `commodities_prediction_log.json`, `data/driver_snapshot.json`, `engine/feedback.py`, `.github/workflows/daily-summary.yml`.
- File SPUTNIK: `.github/workflows/trump_tracker.yml`, `trump_tracker.py`, `sputnik_state.json`.

**Conclusione:** PR #144 ha compiuto un progresso verificabile sul branch di lavoro (193+66 test superati e branch aggiornato), ma non è integrata e il branch runtime `sputnik-state` non esiste ancora. SPUTNIK main continua a scrivere lo stato su main. GAGARIN ha eseguito una scansione, ma tutte le commodity erano stale/market closed, zero ingressi e nessun feedback nuovo. Ledger: 58 record, zero duplicati. Campione finanziario verificabile: zero.

Nessun codice dei bot modificato. Nessuna strategia, filtro, punteggio o rischio modificato. Nessun merge, deploy, rerun, ordine reale, modifica a Render o ai segreti. Nessun servizio a pagamento. Nessun accesso a Trading212 dichiarato. PAPER ONLY.
