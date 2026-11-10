# PRAVDA — Audit indipendente #26
## SPUTNIK / GAGARIN
**10 novembre 2026 — 03:42 UTC (04:42 CET)**

## 1. Esito sintetico

Nuovo controllo indipendente dei log integrali, dei commit su `main`, dei file di stato/journal e delle PR già aperte. Non sono state effettuate modifiche al codice applicativo.

Riscontri principali:

1. SPUTNIK #296 ha prodotto GOLD SHORT #756 come `EARLY_SETUP / NOT_EXECUTED`, ma la card non conserva la direzione tecnica SHORT del messaggio #755 e non identifica il contratto o la quotazione.
2. Lo stesso run ha prodotto il brief informativo #757 con `OIL: DOWN (8 analoghi)` e l'analogo tariffario `china_tariff_escalation_2025_10`, pur senza un nuovo evento tariffario individuale dimostrato. La PR #154 affronta il difetto ed è già documentata con CI verde.
3. Il workflow SPUTNIK su `main` esegue ancora i test mock prima della raccolta live e poi persiste `sputnik_state.json` con `git push origin main`. Le PR #128 e #144 propongono le correzioni, entrambe non integrate.
4. GAGARIN #174 ha analizzato 13 strumenti: tutte le otto commodity selezionate erano STALE; le sole quotazioni LIVE appartenevano a Tesla, EUR/USD e NVIDIA. È stato registrato un WATCH non attribuibile, non un ingresso.
5. GAGARIN `main` conserva ancora 13 strumenti, il journal non ha persistenza durevole dimostrata e l'outcome engine continua a classificare STOP prima di verificare un possibile TP nella stessa candela.
6. Il ranker su GAGARIN `main` contiene ancora un bonus/malus di accelerazione momentum (+8 / -4 punti); la PR #198 propone di ripristinare il baseline precedente.

**Nessun fill, nessun esito SL/TP verificato, nessuna statistica di performance certificabile.**

---

## 2. Registro storico PRAVDA

Riletto il CSV cumulativo con parser CSV che gestisce correttamente i campi quotati.

| Indicatore | Risultato |
|---|---:|
| Record | 108 |
| SPUTNIK | 51 |
| GAGARIN | 57 |
| Firme uniche | 108 |
| Source ID unici | 108 |
| Duplicati | 0 |
| NON_TRADE | 79 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |

Blob SHA del ledger GitHub: `7ee27891e651aa4b581d2a0b70f6f1ce219a936a`.

Non aggiungo righe: #756 e #3756 sono già presenti. #757 è un brief storico/informativo senza livelli e non viene contato come segnale di mercato.

- [Ledger cumulativo PRAVDA — 108 record](https://github.com/andreameloni1984-sys/trump-trucker/blob/pravda/audit-2026-11-10-0305UTC/reports/pravda-signal-ledger-2026-11-09.csv)

Distribuzione per esito: 79 record NON_TRADE e 29 ESITO_NON_VERIFICABILE. Non risultano campioni con fill e percorso OHLC esatto da cui calcolare win rate, Average R o Total R: tutte e tre le metriche restano **N/D**.

---

## 3. SPUTNIK — run #296 e messaggi

### 3.1 Workflow e raccolta

- [GitHub Actions run #296](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42726305978)
- Avvio: 2026-11-10 00:10:54 UTC.
- Completamento: 00:11:07 UTC.
- Job `sputnik`: SUCCESS.
- Commit di checkout: `a9603cad`.
- Commit di persistenza generato dal run: [5f3ae3b](https://github.com/andreameloni1984-sys/trump-trucker/commit/5f3ae3b8bc31275851cbf1f8c8ce964e6feb0ec6), creato alle 00:11:04 UTC.

Log live:
- SEC: HTTP 403; cooldown 21.600 secondi; 0 filing.
- White House RSS: HTTPError su `https://www.whitehouse.gov/feed/`.
- Raccolta intelligence pubblica: 1.670 ms, 3 findings.
- 0 nuove operazioni documentate.
- Handoff GAGARIN disabilitato; `GAGARIN forwarding=0ms`.

Le righe `OSError` e alcuni messaggi Telegram mock presenti prima della raccolta appartengono alla step di unit test, non alle fonti live. La raccolta live inizia dopo la step di test.

### 3.2 Nuova conferma: test mock dentro il collector produttivo

Il workflow su `main` contiene ancora `Run SPUTNIK Telegram delivery regression tests` prima di `python trump_tracker.py`. Il run #296 ha eseguito 30 test e ha stampato nel log live:
- `source WHITE_HOUSE/TRUTH_ARCHIVE/OGE unavailable: OSError` dai mock;
- risposte Telegram simulate, incluso `message_id=731`.

Solo dopo compaiono gli errori live SEC 403 e White House RSS HTTPError. La sovrapposizione può indurre a leggere output di test come errori delle fonti o invii produttivi.

PR esistente:
- [SPUTNIK #128 — Keep regression-test output out of live collector logs](https://github.com/andreameloni1984-sys/trump-trucker/pull/128), OPEN/non integrata.
- Nuova conferma indipendente registrata nel commento [#6758368455](https://github.com/andreameloni1984-sys/trump-trucker/pull/128#issuecomment-6758368455).

### 3.3 GOLD SHORT #755/#756

I due messaggi sono un'unica ipotesi collegata; il ledger conserva una sola riga dettagliata per la card CFD #756.

**Messaggio preliminare #755**
- Generazione: circa 00:11:04.011 UTC.
- GOLD, bias SHORT preliminare.
- Tecnica SHORT (5m).
- Momentum 5m negativo negli ultimi 15 minuti: -0,053%.
- Allineamento notizie: `NO_DIRECTIONAL_NEWS`.
- Stato: `EARLY_BIAS`.

**Card CFD #756**
- Generazione: 00:11:04.0127804 UTC.
- API ACK: 00:11:04.0141166 UTC; round-trip 467 ms.
- GOLD SHORT.
- Entry 4145.2002.
- SL 4146.7429.
- TP1 4143.6575.
- TP2 4142.1147.
- ATR 1.0285.
- Score 100.
- Stato `EARLY_SETUP / NOT_EXECUTED`.

Incongruenza verificata: la card riporta `TECNICA: N/D (NOT_ASSESSED)` e `D-L-A: NEUTRAL / NO_DIRECTION`, mentre il messaggio #755 mostra SHORT 5m. La direzione tecnica non viene conservata nel messaggio CFD.

Provenienza mancante:
- ticker contrattuale risolto: assente;
- mercato: card intitolata CFD, ma riferimento dichiarato a future continuo front-month;
- scadenza esatta: UNKNOWN;
- provider, timestamp e age della quotazione: non esposti;
- prezzo di riferimento: assente;
- NARWHAL: NOT_CONFIGURED;
- indipendenza upstream/spot-futures: non verificata.

La card avverte di non usare i livelli. Il punteggio 100 non rende il setup eseguibile. **NON_TRADE**; non è possibile valutare SL prima o TP prima senza identità contrattuale e candele successive della stessa serie.

La fonte individuale #43537 risulta pubblicata alle 21:29:28 UTC del 9 novembre; l'analisi/card viene generata intorno alle 00:11:04 UTC del 10 novembre: circa **2 h 41 min 36 s** di distanza tra pubblicazione e generazione. L'ACK API non prova la visualizzazione sul dispositivo.

### 3.4 Brief #757 — analogia tariffaria non dimostrata

Il messaggio #757, generato alle 00:11:04.014 UTC e accettato dall'API in 379 ms, riporta:
- `TREASURY_YIELDS: DOWN (8 analoghi)`;
- `OIL: DOWN (8 analoghi)`;
- analogo `china_tariff_escalation_2025_10`.

Il log non dimostra una nuova notizia tariffaria individuale che giustifichi l'attribuzione. La PR #154 documenta che una menzione generica della Cina nel post S.5653 e uno snapshot homepage aggregato con il testo S.5653 + Iran vengono classificati `TRADE_ESCALATION`, ereditando l'analogo tariffario. Il post individuale #43537 sul Qatar/Iran è invece registrato come `GEOPOLITICAL_ESCALATION / NO_ANALOGUE`.

Questo brief è **informazione storica con causalità non verificata**, non un segnale OIL SHORT e non un trade. Non viene aggiunto al ledger operativo.

Correzione già disponibile:
- [SPUTNIK #154 — avoid tariff analogue on generic China mentions](https://github.com/andreameloni1984-sys/trump-trucker/pull/154).
- Head `93f7162c80af109690340c59bed40090f369af59), confronto con main: 1 commit avanti / 0 indietro.
- CI: ranking #667 SUCCESS (187 test); item intelligence #270 SUCCESS (47 test); 234 esecuzioni di test complessive; zero artifact.
- PR OPEN, non integrata.
- Commento indipendente PRAVDA: [#6758361012](https://github.com/andreameloni1984-sys/trump-trucker/pull/154#issuecomment-6758361012).

### 3.5 Stato SPUTNIK scritto su main

Il workflow su main contiene:
- `permissions: contents: write`;
- step `Persist SPUTNIK state`;
- `git push origin main`.

Il run #296 ha effettivamente creato e inviato il commit `5f3ae3b` su main. Il branch dedicato `sputnik-state` non è stato trovato (lookup ref 404).

Correzione disponibile:
- [SPUTNIK #144 — Persist SPUTNIK state outside main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144).
- Head `e4a7459a6c1c0f259d86112266f2f66e3fab5c17), confronto con main: 1 avanti / 0 indietro.
- Ranking CI #670 SUCCESS: 194 test; Telegram menu CI #301 SUCCESS.
- La CI verifica codice e struttura dei workflow, non il primo push/restore live sul branch dedicato.
- PR OPEN, non integrata. Il problema su main resta dimostrato dal run #296.

Altre PR SPUTNIK ancora aperte e pertinenti:
- [#153](https://github.com/andreameloni1984-sys/trump-trucker/pull/153): propagazione della direzione tecnica nella card CFD; 186 test ranking + 67 Telegram/menu, entrambi SUCCESS; 253 esecuzioni complessive.
- [#150](https://github.com/andreameloni1984-sys/trump-trucker/pull/150): non ripetere raccomandazioni da snapshot senza nuovo RSS item idoneo.
- [#156](https://github.com/andreameloni1984-sys/trump-trucker/pull/156): selezionare i 30 record intelligence più recenti.
- [#155](https://github.com/andreameloni1984-sys/trump-trucker/pull/155): diagnostica dei gap di schedule; non dimostra né risolve la causa delle invocazioni mancanti.

---

## 4. GAGARIN — run #174

### 4.1 Workflow e configurazione

- [GitHub Actions run #174](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729446093)
- Avvio: 00:35:20 UTC.
- Completamento: 00:35:42 UTC.
- Commit: `631727912b3a2022379a4460f4b6f756eba6991f`.
- Job: SUCCESS.
- Modalità: PAPER ONLY.

Il workflow GitHub Actions `.github/workflows/gagarin-monitor.yml` è programmato ogni 15 minuti (`*/15 * * * *`) e imposta `MONITOR_INTERVAL_MINUTES=15`. Il codice `telegram/render_runner.py` dichiara invece un loop a 5 minuti, ma stampa ancora `13 approved instruments`. La presenza del loop nel codice non prova che un deployment Render corrispondente sia attivo; nessun controllo o intervento Render è stato effettuato.

### 4.2 Universo produttivo: 13, non 8

Su main, `commodities/universe.py` contiene 13 strumenti abilitati:
- 8 commodity: Oro, Argento, Rame, WTI, Brent, Grano, Mais, Soia;
- EUR/USD;
- DAX;
- S&P 500;
- NVIDIA;
- Tesla.

Il runner dichiara esplicitamente 13 strumenti approvati. Il run #174 mostra tutte e 13 le righe. Non è conforme al paniere di otto commodity richiesto.

### 4.3 Quotazioni

| Strumento | Provider | Age nel log | Stato |
|---|---|---:|---|
| Oro | YAHOO | 612,4 s | STALE |
| Argento | YAHOO | 628,1 s | STALE |
| Rame | YAHOO | 663,3 s | STALE |
| WTI | YAHOO | 602,5 s | STALE |
| Brent | YAHOO | 771,6 s | STALE |
| Grano | YAHOO | 18.938,7 s | STALE |
| Mais | YAHOO | 18.939,7 s | STALE |
| Soia | YAHOO | 18.940,8 s | STALE |

Tutte le otto commodity sono STALE. Le sole righe LIVE sono Tesla (YAHOO, 16,0 s), EUR/USD (BIQUOTE, 37,7 s) e NVIDIA (YAHOO, 2,9 s), tutte fuori dal paniere richiesto.

Il log fornisce provider e age, ma non un timestamp assoluto della quotazione per ciascuna riga. Non posso quindi ricostruire una sequenza OHLC successiva esatta. Nessuna quotazione commodity fresca nel run.

### 4.4 Esito del run e WATCH #3756

Il log riporta:
- Recorded entries: 0;
- Updated open outcomes: 0;
- New feedback signals: 0;
- New additional live forecasts (WATCH/other): 1;
- `signals=1 open=1 closed=0`;
- win rate / avg_R / total_R: N/D.

Telegram ha confermato l'accettazione API del messaggio #3756 alle 00:35:38.6208015 UTC, round-trip 594 ms. Il corpo del messaggio non è conservato. Strumento, ticker, mercato, scadenza, provider, timestamp quotazione, direzione e livelli non sono attribuibili.

Record già presente nel ledger come `watch_pre_alert_unattributed`; **non è un trade**.

### 4.5 Journal e persistenza

Nel run #174 `DATABASE_URL` è vuota. Nessun artifact è stato prodotto. Il prediction log su main ha 981 record:
- 945 PENDING;
- 36 NEUTRALE;
- 21 voci `COMPRA ORA`, tutte PENDING;
- ultimo `created_at` nel file: 2026-09-15 15:45:04 UTC.

PENDING e COMPRA ORA non equivalgono a fill. La persistenza durevole tra runner GitHub distinti non è dimostrata. Il run mostra un forecast OPEN, ma non un archivio durevole consultabile da questa esecuzione.

Correzione disponibile:
- [GAGARIN #202 — Persist Gagarin paper journal and daily feedback in PostgreSQL](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202), OPEN.
- Propone deduplica con signal_id e fallimento esplicito quando il database manca/non è raggiungibile. La configurazione del secret `DATABASE_URL` resta responsabilità del proprietario del repository; PRAVDA non lo legge né modifica.

### 4.6 Outcome engine

Il file main `engine/feedback.py` (SHA `41bec9bfab031c8dbf71121cd69d0e9b4c4f663f`) conserva `data_source`, ma non campi separati per provider, ticker quotato, mercato, mese contratto e scadenza. Il fingerprint usa symbol, direzione, timeframe, livelli e timestamp candela. `update_open_outcomes()` abbina principalmente per symbol/timeframe, con fallback symbol se esiste un solo candidato.

La docstring e il codice controllano `stop_hit` prima dei target: una candela che tocca SL e TP può essere registrata STOP senza conoscere la sequenza intrabar. Regola PRAVDA: **doppio tocco SL/TP nella stessa candela senza ordine intrabar ricostruibile = ESITO NON VERIFICABILE**.

- [PR #192 — exact-contract and ambiguous-outcome audit fixes](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) resta OPEN e non integrata. Il suo patch affronta il doppio tocco e aggiunge provider al fingerprint, ma il commento di audit precedente ha rilevato che il guard `_market_contract_match()` non confronta esplicitamente provider del segnale e provider della serie successiva. Serve verifica di quel punto prima di considerare la correzione completa.

### 4.7 Punteggio e soglie: discrepanze da non modificare in audit

Il ranker main `engine/prediction_ranker.py` (SHA `7ebee56d2b439596c69531b3dc7c6664c9d4905b`) contiene un `momentum_acceleration_score` che aggiunge fino a 8 o sottrae fino a 4 punti. La PR [#198](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/198) dichiara che questa modifica è stata introdotta senza richiesta esplicita e propone il ripristino del baseline. PR OPEN; nessuna modifica PRAVDA.

La run #174 usa:
- MIN_ENTRY_PROBABILITY 40;
- MIN_ENTRY_QUALITY 30;
- MIN_ENTRY_CONFIDENCE 35;
- MIN_ENTRY_RR 2.5.

Sono valori di runtime osservati, non modificati in questa verifica. La loro coerenza con i profili precedentemente approvati va verificata dal reparto responsabile; PRAVDA non li cambia.

### 4.8 Correzioni GAGARIN esistenti

- [#248 — restore exact eight-commodity universe](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/248): head `d370ad676709f0be911db55f8314043e7dfce9fa`, 20 commit avanti / 0 indietro rispetto a main; allowlist fail-closed di otto commodity; 7/7 workflow SUCCESS; suite principale 571 test PASS. OPEN/DRAFT, non integrata. È la proposta più aggiornata verificata per il paniere.
- [#240 — suppress stale LUBJANKA trigger levels](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/240): propone di nascondere entry/SL/TP quando quote o candela M5 superano 600 secondi; OPEN. Nel body della PR i check CI sono ancora da verificare.
- [#175 — active Telegram webhook vs polling](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): il polling run #21 fallisce con API 409 perché webhook attivo. PR OPEN; non cancella il webhook.
- [#250 — disable manual Trading 212 quote comparisons](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/250): proposta per evitare confronto tra CFD manuale e serie futures; OPEN, non integrata.
- Le PR #212 e #221 trattano anch'esse l'universo a otto strumenti e si sovrappongono in parte a #248; evitare di considerare una proposta aperta come attiva su main.

---

## 5. Valutazione degli esiti

| Elemento | Stato | Motivo |
|---|---|---|
| SPUTNIK GOLD SHORT #756 | NON_TRADE | NOT_EXECUTED; ticker/contratto/provider/quote timestamp assenti |
| SPUTNIK brief #757 | Informativo, non segnale | Reazione storica OIL DOWN senza catalizzatore tariffario individuale verificato |
| GAGARIN WATCH #3756 | NON_TRADE | Corpo non conservato; strumento e contratto non attribuibili |
| Legacy PENDING nel prediction log | NON_TRADE / non valutabile | PENDING non prova fill; identità serie e timestamp quotazioni incompleti |

Non sono state valutate candele successive come se fossero dello stesso strumento/contratto quando tale identità manca. Nessun caso SL prima, TP prima o doppio tocco è certificabile in questo campione.

**Statistiche su campioni verificabili: campione operativo = 0; win rate N/D; Average R N/D; Total R N/D.**

---

## 6. Actions e limiti di copertura

Log integrali consultati:
- SPUTNIK #296: job `sputnik` SUCCESS; artifacts 0.
- GAGARIN #174: job monitor SUCCESS; artifacts 0.
- GAGARIN Telegram polling #21: failure per 409 webhook/polling.
- PR CI: SPUTNIK #154 (#667/#270) SUCCESS; SPUTNIK #144 (#670/#301) SUCCESS; GAGARIN #248 7/7 SUCCESS.

Il connettore GitHub disponibile consente di recuperare run/job noti e CI associate a commit PR, ma non espone un elenco paginato completo di tutte le workflow runs programmate per repository. Perciò #296 e #174 sono gli ultimi log completi esaminati in questo controllo, **non una prova che non esistano esecuzioni successive**. Non viene dichiarata assenza di run senza enumerazione completa.

Fonti principali:
- repository [SPUTNIK](https://github.com/andreameloni1984-sys/trump-trucker);
- repository [GAGARIN](https://github.com/andreameloni1984-sys/commodity-news-scanner);
- log Actions #296, #174 e #21;
- commit SPUTNIK `5f3ae3b`;
- file main: `trump_tracker.yml`, `sputnik_catalyst.py`, `commodities/universe.py`, `telegram/render_runner.py`, `gagarin-monitor.yml`, `engine/feedback.py`, `engine/prediction_ranker.py`, `commodities_prediction_log.json`;
- PR #128, #144, #150, #153, #154, #156, #175, #192, #198, #202, #240, #248 e #250.

Nessun servizio a pagamento usato. Nessun accesso a Trading 212 dichiarato. Nessun accesso a Render o prova di consegna Telegram sul dispositivo.

---

## 7. Prossimo controllo

1. Verificare la prima scansione SPUTNIK dopo un'eventuale correzione della classificazione tariffaria e della propagazione tecnica.
2. Verificare che il workflow SPUTNIK non esegua unit test mock nel collector live e che la persistenza non scriva più su main dopo eventuale integrazione #144.
3. Verificare l'integrazione effettiva della PR #248 e confermare nel log che GAGARIN scansioni solo otto commodity.
4. Richiedere quotazioni fresche con timestamp assoluto, ticker, mercato e scadenza per ciascuna commodity.
5. Verificare la persistenza journal su due run distinti; il run con DATABASE_URL vuota non basta.
6. Riallineare e verificare l'outcome engine: provider, ticker, mercato, contratto/scadenza e doppio tocco intrabar.
7. Verificare PR #240 per evitare di mostrare livelli su dati stale.
8. Verificare polling/webhook senza cancellare o modificare il webhook.
9. Acquisire l'elenco completo delle workflow runs programmate prima di dichiarare gap o assenza di esecuzioni.

---

## 8. Confini operativi

Audit e documentazione soltanto. Nessuna modifica al codice applicativo, strategia, filtri, punteggi, soglie, rischio, sizing o direzioni. Nessun merge, deploy, ordine reale, modifica a segreti o Render. Nessun accesso a Trading 212 dichiarato. PAPER ONLY.
