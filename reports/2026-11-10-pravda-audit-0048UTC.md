# PRAVDA — Audit indipendente #23
## SPUTNIK / GAGARIN
**Rilevazione: 10 novembre 2026, 00:48 UTC (01:48 CET)**

## 1. Esito sintetico

Sono state verificate le ultime GitHub Actions programmate disponibili, i log completi dei job, i file correnti su `main`, i journal pubblici, i feedback engine e lo stato delle PR rilevanti.

Novità principali:

1. SPUTNIK ha completato la run schedule **#296** alle 00:11 UTC e ha generato una nuova card GOLD SHORT (#756), ma la card è `NOT_EXECUTED`, priva di ticker/contratto/provider/timestamp della quotazione e dichiara espressamente di non usare i livelli.
2. GAGARIN ha completato la nuova scansione schedule **#174** alle 00:35 UTC sul main attuale: ha analizzato ancora **13 strumenti**, non gli otto commodity della PR #248. Tutte le otto commodity risultavano stale. Nessuna entrata autorizzata.
3. GAGARIN ha registrato nel riepilogo un forecast WATCH OPEN e ha inviato il pre-alert Telegram #3756, ma il corpo del messaggio e l'identità del forecast non sono conservati; `DATABASE_URL` era vuota e non sono stati prodotti artifact.
4. Il polling Telegram GAGARIN **#21** è nuovamente fallito con API 409 per webhook attivo.
5. Le correzioni #248, #250, #153, #192 e #175 hanno CI verdi sui rispettivi head, ma nessuna di queste risulta integrata su main.

Nessun merge, deploy, ordine reale o modifica applicativa da PRAVDA.

---

## 2. Registro storico — controllo duplicati

Il ledger precedente conteneva 106 record. Sono stati aggiunti soltanto due record nuovi, identificati da source ID distinti:

- `run:42726305978/telegram_message:756` — SPUTNIK GOLD SHORT, `NOT_EXECUTED`.
- `run:42729446093/telegram_watch_pre_alert:3756` — GAGARIN WATCH non attribuibile.

Il messaggio SPUTNIK #755 è la companion analysis della card #756 e non è stato contato come secondo segnale. I messaggi #754 (digest notizia) e #757 (brief) non sono segnali operativi e non sono stati inseriti come trade.

**Verifica dopo aggiornamento:**

| Indicatore | Risultato |
|---|---:|
| Record totali | 108 |
| Firme uniche | 108 |
| Source ID unici | 108 |
| Duplicati firma | 0 |
| Duplicati source ID | 0 |
| NON_TRADE | 79 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |

SHA blob del ledger aggiornato: `7ee27891e651aa4b581d2a0b70f6f1ce219a936a`.

Le 29 righe `ESITO_NON_VERIFICABILE` sono record senza esito dimostrabile; non vanno interpretate come 29 trade eseguiti. Non esiste un campione di fill verificati: win rate, Average R e Total R restano **N/D**.

Ledger: [pravda-signal-ledger-2026-11-09.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/pravda/audit-2026-11-10-0048UTC/reports/pravda-signal-ledger-2026-11-09.csv)

---

## 3. SPUTNIK — run #296

[GitHub Actions SPUTNIK #296](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42726305978)

- Evento: `schedule`.
- Avvio: 2026-11-10 00:10:54 UTC.
- Completamento: 00:11:07 UTC.
- Job `sputnik`: SUCCESS.
- Commit di checkout: `6c3095f1534550b0b4e77170f1428db833253c05`.
- Il job ha poi persistito `sputnik_state.json` con commit `5f3ae3b8bc31275851cbf1f8c8ce964e6feb0ec6`; il diff del commit riguarda il solo file di stato.

La scansione programmata precedente #295 era partita il 9 novembre alle 16:02:05 UTC: intervallo tra #295 e #296 **8h 08m 49s**. La run Telegram Polling #55 del 9 novembre 23:51:48 UTC è SUCCESS e riporta `Pending updates: 0`; non prova una nuova scansione intelligence.

### Fonti e raccolta

- SEC: HTTP 403, cooldown 21.600 secondi, zero filing e zero record transazionali.
- White House RSS: HTTPError.
- Intelligence pubblica: 3 correlazioni.
- Nuovi eventi pubblici verificabili: 1.
- Handoff GAGARIN: disabilitato perché `GAGARIN_CLOUD_API_URL/API_KEY` non configurati; forwarding 0 ms, nessuna prova di trasmissione.

L'item RSS collegato al digest #754 è [Trumpstruth status 43537](https://www.trumpstruth.org/statuses/43537), pubblicato il **9 novembre 2026 alle 21:29:28 UTC**. Il messaggio di analisi e la card sono stati generati intorno alle **00:11:04 UTC del 10 novembre**: latenza dalla pubblicazione di circa **2h 41m 36s**.

Il testo riguarda una conversazione con il Primo Ministro del Qatar ed è mappato su DEFENSE/AI_TECH. Non è un catalizzatore commodity direzionale verificato; la stessa analisi dichiara `NO_DIRECTIONAL_NEWS`.

### Nuova card GOLD SHORT — Telegram #756

La companion analysis #755 dichiara GOLD SHORT, tecnica SHORT 5m e momentum 5m negativo `-0,053%` negli ultimi 15 minuti. La card CFD #756, invece, riporta tecnica `N/D (NOT_ASSESSED)` e D-L-A `NEUTRAL / NO_DIRECTION (INSUFFICIENT_DATA)`.

| Campo | Valore |
|---|---|
| Generazione/log card | 2026-11-10 00:11:04.0127804 UTC |
| API ACK log | 00:11:04.0141166 UTC |
| Telegram message ID | 756 |
| Strumento | GOLD |
| Direzione/Bias | SHORT |
| Stato | EARLY_SETUP; NOT_EXECUTED |
| Entry | 4145.2002 |
| SL | 4146.7429 |
| TP1 | 4143.6575 |
| TP2 | 4142.1147 |
| ATR | 1.0285 |
| Score | 100 |
| Provider | Non esposto; NARWHAL non configurato |
| Timestamp/età quotazione | Non esposti |
| Ticker esatto | Non risolto |
| Mercato/contratto | Titolo CFD, corpo riferito a future continuo front-month |
| Scadenza | UNKNOWN |

La card avverte che scadenza esatta e indipendenza upstream non sono verificate e che i livelli non devono essere utilizzati. Anche il controllo SPOT/FUTURES riporta indipendenza non verificata. Score 100 non equivale a validità operativa.

L'API Telegram ha registrato ACK per #754 (415 ms), #755 (374 ms), #756 (467 ms) e #757 (379 ms). Sono conferme API, non prove di visualizzazione sul dispositivo né di esecuzione.

**Classificazione PRAVDA #756: NON_TRADE.** Non sono disponibili candele successive dello stesso ticker e contratto: nessun esito SL/TP attribuito.

### Correzione già proposta

[SPUTNIK PR #153 — preservare la direzione tecnica 5m nella card CFD](https://github.com/andreameloni1984-sys/trump-trucker/pull/153) è OPEN/non merged, aggiornata sulla base main corrente, 2 commit avanti/0 indietro. I due workflow CI sul suo head risultano SUCCESS (186 e 67 test). Il nuovo caso #755/#756 riproduce esattamente la discrepanza.

Le PR #150 e #156 restano OPEN/non merged. Entrambe hanno due workflow CI verdi sui rispettivi head, ma il confronto con main corrente è divergente di 1 commit avanti e 1 indietro dopo la nuova persistenza dello stato.

---

## 4. GAGARIN — run #174

[GitHub Actions GAGARIN Monitor #174](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729446093)

- Evento: `schedule`.
- Avvio: 2026-11-10 00:35:20 UTC.
- Completamento: 00:35:42 UTC.
- Job: SUCCESS.
- Commit main: `631727912b3a2022379a4460f4b6f756eba6991f`.
- Nessun artifact del run.

### Universo effettivamente eseguito

Il log dichiara: `13 strumenti operativi; nessun filtro orario per categoria`. Il file main `commodities/universe.py` conferma otto commodity più EUR/USD, DAX, S&P 500, NVIDIA e Tesla.

Le otto commodity erano tutte stale:

| Commodity | Provider | Età | Stato |
|---|---|---:|---|
| Oro | YAHOO | 612,4 s | STALE |
| Argento | YAHOO | 628,1 s | STALE |
| Rame | YAHOO | 663,3 s | STALE |
| WTI | YAHOO | 602,5 s | STALE |
| Brent | YAHOO | 771,6 s | STALE |
| Grano | YAHOO | 18.938,7 s | STALE |
| Mais | YAHOO | 18.939,7 s | STALE |
| Soia | YAHOO | 18.940,8 s | STALE |

Le sole righe LIVE erano Tesla (YAHOO, 16,0 s), EUR/USD (BIQUOTE, 37,7 s) e NVIDIA (YAHOO, 2,9 s): tutte fuori dal paniere commodity richiesto. DAX e S&P 500 erano stale.

La classifica ha mostrato solo `PAPER_WATCH`; EUR/USD era SHORT ma con trigger non confermato, mismatch di direzione e confluence finale fallita. Il riepilogo operativo dichiara **NESSUNA ENTRATA AUTORIZZATA**.

### Soglie runtime osservate

Il workflow main ha passato al run: probabilità 40, qualità 30, confidence 35, RR minimo 2,5, stop massimo 2,5 ATR, buffer struttura 0,15 ATR e stop minimo 0,80 ATR. Sono valori osservati nei log/configurazione; PRAVDA non li ha modificati.

### Forecast WATCH e Telegram #3756

Il log riporta:

- Recorded entries: 0.
- Updated open outcomes: 0.
- New feedback signals: 0.
- New additional live forecasts (WATCH/other): 1.
- `signals=1 open=1 closed=0`.
- Telegram SEND CONFIRMED, message ID **3756**, round-trip 594 ms.

Il corpo del messaggio non è conservato. Non è possibile attribuire strumento, ticker, direzione, provider, timestamp della quotazione, scadenza o livelli. È stato aggiunto al ledger come `watch_pre_alert_unattributed`, non come trade. L'ACK API non prova la consegna sul dispositivo.

### Journal e persistenza

Nel run #174 `DATABASE_URL` era vuota. Non sono stati prodotti artifact. Su main:

- `commodities_prediction_log.json`: 981 record, 945 PENDING e 36 NEUTRALE; ultima registrazione 15 settembre 2026.
- Azioni nel prediction log: NON ENTRARE 77; ATTENDERE 576; SHORT—ASPETTARE CONFERMA 15; LONG—ASPETTARE CONFERMA 292; COMPRA ORA 21 (tutte PENDING).
- `paper_trade_log.csv`: una sola riga WTI LEGACY_IMPORT del 8 ottobre, senza esito.
- `position.json`: vecchia posizione Heating Oil LONG del 15 settembre.
- `paper_open.json`: assente.
- `gagarin_feedback.csv`: assente.

Non c'è prova di persistenza cross-run del forecast OPEN osservato nel riepilogo #174.

[PR #202 — persistenza del journal PostgreSQL](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202) è OPEN/DRAFT e propone di fallire esplicitamente quando il database manca o non è raggiungibile. Nessun secret è stato letto o modificato da PRAVDA.

---

## 5. PR e difetti dimostrati

| PR | Stato | Confronto con main corrente | CI sul head |
|---|---|---:|---|
| SPUTNIK #153 | OPEN, non merged | 2 avanti / 0 indietro | 2 workflow SUCCESS |
| SPUTNIK #150 | OPEN, non merged | 1 avanti / 1 indietro | 2 workflow SUCCESS |
| SPUTNIK #156 | OPEN, non merged | 1 avanti / 1 indietro | 2 workflow SUCCESS |
| GAGARIN #248 | OPEN/DRAFT, non merged | 17 avanti / 0 indietro | 7 workflow SUCCESS; suite 570 test |
| GAGARIN #250 | OPEN/DRAFT, non merged | 3 avanti / 0 indietro | 6 workflow SUCCESS |
| GAGARIN #192 | OPEN, non merged | 6 avanti / 10 indietro | 6 workflow SUCCESS |
| GAGARIN #175 | OPEN, non merged | 1 avanti / 7 indietro | 5 workflow SUCCESS |
| GAGARIN #202 | OPEN/DRAFT, non merged | proposta persistenza | non integrata |

### Universo a otto commodity — PR #248

[PR #248](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/248) è basata sul main corrente e propone esattamente XAU, XAG, COPPER, WTI, BRENT, WHEAT, CORN e SOYBEAN. Ha 7/7 workflow SUCCESS, ma resta DRAFT e non è su main. Il run #174 conferma che main continua ad analizzare 13 strumenti.

### Rimozione dei confronti manuali Trading 212 — PR #250

[PR #250](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/250) è OPEN/DRAFT, 3 avanti/0 indietro e 6/6 workflow SUCCESS. La patch rimuove dal bot attivo il confronto manuale tra prezzi CFD e la serie futures; non fornisce un feed Trading 212 e non prova accesso a un conto o a quotazioni broker.

### Outcome engine — PR #192

Su main `engine/feedback.py`:
- il fingerprint usa symbol, direction, timeframe, livelli e timestamp barra;
- i campi non includono provider, quote ticker, market type, mese o scadenza;
- il matching successivo usa symbol/timeframe;
- docstring e codice classificano STOP prima dei target quando una candela tocca entrambi.

La PR #192 propone identità provider/contratto e `ESITO NON VERIFICABILE` per il doppio tocco, ma è divergente 6 avanti/10 indietro. I test verdi sul suo head non certificano l'integrazione con il main corrente.

### Telegram polling — PR #175 e run #21

[Polling #21](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729120141) è fallita alle 00:32:48–00:33:07 UTC: token e diagnostica bot SUCCESS, `getUpdates` fallisce con API 409 perché il webhook è attivo. La PR #175 propone di saltare il polling senza cancellare il webhook; resta OPEN e divergente 1 avanti/7 indietro.

---

## 6. Commenti di audit pubblicati

Sono stati aggiunti commenti documentali, senza modifiche al codice, a:

- [SPUTNIK PR #153 — commento 6755689742](https://github.com/andreameloni1984-sys/trump-trucker/pull/153#issuecomment-6755689742)
- [GAGARIN PR #248 — commento 6755690213](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/248#issuecomment-6755690213)
- [GAGARIN PR #202 — commento 6755690739](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202#issuecomment-6755690739)
- [GAGARIN PR #175 — commento 6755691280](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175#issuecomment-6755691280)
- [GAGARIN PR #192 — commento 6755691745](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6755691745)

---

## 7. Fonti consultate

### GitHub Actions
- [SPUTNIK Collector #296](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42726305978)
- [SPUTNIK Telegram Polling #55](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42723841180)
- [SPUTNIK Collector #295](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42650624196)
- [GAGARIN Monitor #174](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729446093)
- [GAGARIN Telegram Polling #21](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729120141)
- [GAGARIN Monitor #173](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42659137635)

### File main e journal
- `commodities/universe.py`
- `.github/workflows/gagarin-monitor.yml`
- `engine/feedback.py`
- `telegram/polling_runner.py`
- `commodities_prediction_log.json`
- `paper_trade_log.csv`
- `position.json`
- `data/driver_snapshot.json`
- `sputnik_state.json` (commit di persistenza; contenuto non restituito dal fetch file)
- ledger PRAVDA aggiornato.

### Pull Request
- SPUTNIK #150, #153, #156.
- GAGARIN #175, #192, #202, #248, #250.

---

## 8. Lacune e prossimo controllo

1. SPUTNIK: ticker esatto, scadenza, provider e timestamp della quotazione per GOLD #756; candele successive dello stesso contratto.
2. SPUTNIK: ridurre e misurare la latenza tra pubblicazione item-level e analisi; la latenza osservata per il post #43537 è circa 2h41m36s.
3. SPUTNIK: verificare il prossimo schedule e l'effettiva persistenza dello stato; il commit automatico #296 ha aggiornato soltanto `sputnik_state.json`.
4. GAGARIN: verificare l'integrazione della PR #248 e che una scansione successiva riporti esattamente otto commodity.
5. GAGARIN: ottenere quote fresche per tutte le otto commodity; nel run #174 nessuna era LIVE.
6. GAGARIN: recuperare il corpo e l'identità del WATCH #3756; al momento non è attribuibile.
7. GAGARIN: dimostrare persistenza del journal tra due run; DATABASE_URL è vuota e non ci sono artifact.
8. GAGARIN: riallineare/testare l'outcome engine su provider, ticker, mercato, scadenza e doppio tocco intrabar.
9. GAGARIN: risolvere il 409 del polling senza cancellare il webhook; verificare separatamente l'effettiva consegna webhook.
10. Verificare i successivi schedule di entrambi i repository; le liste consultate espongono le ultime esecuzioni disponibili, non una prova di funzionamento di Render.

## 9. Verdetto

**108 record, 108 firme uniche, zero duplicati. Due nuovi record: una card SPUTNIK NOT_EXECUTED e un WATCH GAGARIN non attribuibile. Zero fill verificati, zero SL verificati, zero TP verificati. Nessuna statistica di performance calcolabile.**

PRAVDA non ha modificato codice applicativo, strategia, filtri, punteggi, soglie o rischio. Nessun merge, deploy, ordine reale, modifica di secret o Render. Nessun servizio a pagamento. Nessun accesso a Trading212 dichiarato. Gli ACK Telegram sono trattati esclusivamente come accettazioni API.

**PAPER ONLY.**
