# PRAVDA — Audit indipendente SPUTNIK / GAGARIN

**Cut-off: 8 novembre 2026, 23:46:41 UTC (9 novembre 2026, 00:46:41 Europe/Rome).**

## Sintesi

Verificati i branch `main`, le ultime GitHub Actions schedule, i job log, i journal/feedback pubblici, il ledger PRAVDA e le PR aperte.

**Non risultano nuove run produttive dopo SPUTNIK #291 (20:35:50 UTC) e GAGARIN #170 (20:41:00 UTC).** Le esecuzioni successive visibili sono CI di PR, non scansioni di mercato. I messaggi #741, #742 e #3726 sono già nel ledger: nessuna nuova riga e nessun duplicato.

Novità rilevanti:
1. SPUTNIK PR #131 è stata aggiornata a 23:37 UTC; il nuovo endpoint White House ha superato i test, ma non è ancora su main.
2. SPUTNIK PR #150 ha superato 231 test; il recommender continua però a produrre la coppia GOLD #741/#742 su main senza nuovi item RSS.
3. GAGARIN PR #238 introduce una separazione più corretta degli identificativi Trading 212, ma resta draft e senza registry/feed/quotazioni. Un'integrazione Cloudflare ha riportato un build fallito sul branch PR; non è prova di deploy riuscito.

## 1. Repository e riferimenti di versione

- SPUTNIK `main`: `0374d771810648626cd113bce14b2c8eb7c2f52d`.
- GAGARIN `main`: `e7f5d2f890e8df52fcdc230bf4f0c16fd3266e56`.

Il ledger verificato è `reports/pravda-signal-ledger-2026-11-08.csv` nel repository SPUTNIK.

## 2. Ledger: integrità e copertura

- Record: **94**.
- SPUTNIK: **42**.
- GAGARIN: **52**.
- Firme uniche: **94**.
- Source ID unici: **94**.
- Duplicati firma/source ID: **0**.
- Outcome `NON_TRADE`: **65**.
- Outcome `ESITO_NON_VERIFICABILE`: **29**.
- Fill verificati: **0**.
- SL verificati: **0**.
- TP verificati: **0**.

I 29 record `ESITO_NON_VERIFICABILE` sono candidati/previsioni senza percorso di prezzo omogeneo e verificabile; **non sono 29 trade**. I record `PENDING` dell'archivio previsioni non sono esecuzioni.

Copertura grezza dei campi sul ledger completo (94 record; i campi non applicabili a notizie/digest/board sono inclusi nei mancanti):
- timestamp generazione presente: 88;
- timestamp invio presente: 62;
- ticker presente: 71;
- market type presente: 43;
- scadenza presente: 26;
- provider presente: 57;
- timestamp quotazione presente: 21;
- entry/SL/TP1 presenti: 28;
- ATR presente: 12.

Per bot, su record complessivi:
- SPUTNIK (42): sent_at 41, ticker 39, market type 35, expiry 19, provider 27, quote timestamp 19, entry/SL/TP1 6, ATR 6.
- GAGARIN (52): sent_at 21, ticker 32, market type 8, expiry 7, provider 30, quote timestamp 2, entry/SL/TP1 22, ATR 6.

Questi conteggi misurano la completezza del registro, non la percentuale di segnali operativi validi. Win rate, average R e total R restano **N/D** perché il campione di fill verificati è zero.

Ultimi record già presenti e riconciliati:
- SPUTNIK #741 e #742, run `42520937991`;
- GAGARIN #3726, run `42521363444`.

Nessuna modifica al CSV in questo audit.

## 3. SPUTNIK — ultima run produttiva #291

[GitHub Actions #42520937991](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42520937991) — evento `schedule`, SUCCESS; avvio 20:35:50 UTC; job ID `128854031090`.

### Raccolta e analisi
Nel vero runtime:
- SEC CIK 0001849635: HTTP 403; cooldown 21.600 secondi; filing=0.
- White House RSS `https://www.whitehouse.gov/feed/`: HTTPError.
- filing=0, transazioni=0, nuove correlazioni pubbliche=0.
- Il collector ha comunque prodotto due messaggi GOLD.

Le righe OSError per WHITE_HOUSE/TRUTH_ARCHIVE/OGE e la falsa conferma GAGARIN appaiono nello step dei test automatici prima dell'avvio del runtime; non sono attribuite alla produzione.

### Messaggi
- #741: WATCH / NEUTRAL / NO_DIRECTION; tecnica 5m non disponibile; API ACK alle 20:35:58.6659378 UTC, round-trip 497 ms.
- #742: NOT_EXECUTED / NO_DIRECTION; API ACK alle 20:35:58.6670675 UTC, round-trip 444 ms.

Sono la stessa analisi GOLD, non due opportunità indipendenti. Per #742 il titolo usa “CFD”, ma il corpo dichiara `FUTURES_CONTINUOUS_FRONT_MONTH` senza scadenza esatta. Non risultano ticker runtime risolto, provider, timestamp/età quota, prezzo di riferimento, entry, SL, TP o ATR. Score/priorità 100 non è validità operativa; `NOT_EXECUTED` non è un trade. Gli ACK API non provano la visualizzazione sul dispositivo.

### PR SPUTNIK
- [PR #150 — no-repeat recommendations](https://github.com/andreameloni1984-sys/trump-trucker/pull/150): OPEN, non draft, mergeable; 2 commit avanti / 1 indietro rispetto a main al cut-off. CI sul head `3b61e784f7ae41f765278f2f2cf8b56301b375c4`: item intelligence #258 SUCCESS (46 test), ranking #648 SUCCESS (185 test), totale 231. La modifica fa partire la coppia recommendation/CFD soltanto se la scansione corrente ha un nuovo item RSS item-level con metadata validi. Non è su main.
- [PR #131 — White House RSS endpoint](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): OPEN, non draft, 1 commit avanti / 0 indietro. Head `258e40b4fbd243e57e39f46f51695024cf6f9b90`. CI #259 item intelligence SUCCESS (45 test) e #649 ranking SUCCESS (184 test), totale 229. Cambia il default da `/feed/` a `/news/feed/`. Il controllo esterno ha ricevuto MIME RSS, ma il recupero dal runner deve ancora essere confermato da una successiva run produttiva. La run #291 ha ancora usato il vecchio endpoint perché la PR non è integrata.
- [PR #147 — rimozione handoff GAGARIN](https://github.com/andreameloni1984-sys/trump-trucker/pull/147) e [PR #145 — provenienza quote](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): ancora aperte e non in produzione.
- PR #149 resta MERGED.

Polling [#51](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42520176845) è SUCCESS alle 20:27:04 UTC; non ci sono run polling successive visibili al cut-off.

## 4. GAGARIN — ultima run produttiva #170

[GitHub Actions #42521363444](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42521363444) — evento `schedule`, SUCCESS; avvio 20:41:00 UTC; job ID `128855369410`.

### Quotazioni e blocchi
Il runtime ha analizzato 10 voci: 8 commodity e 2 Forex di contesto. Tutte risultano `MARKET_CLOSED`.
- YAHOO commodity: età 168.073,8–177.677,7 secondi (circa 46,7–49,4 ore).
- BIQUOTE EUR/USD e GBP/USD: circa 168.374 secondi (46,8 ore).
- Il log non espone timestamp assoluti delle quote, ticker provider risolti, market type/contratto o scadenza.

Le righe sono bloccate da mercato chiuso/dati stale e da setup/trigger/livelli mancanti. Riepilogo letterale:
- Recorded entries: 0
- Updated open outcomes: 0
- New feedback signals: 0
- New additional live forecasts: 0
- `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`

Telegram #3726: API SEND CONFIRMED alle 20:41:14.9990102 UTC, 337 ms; il corpo non è conservato, quindi non è attribuibile a strumento/direzione. Il record è già presente nel ledger come `NON_TRADE`.

### Journal e feedback su main
- `journal.csv`: 11 righe del 17 ottobre, tutte “nessun segnale”.
- `paper_trade_log.csv`: un WTI LONG dell'8 ottobre, `LEGACY_IMPORT`, entry 96.24, stop 89.37, TP1 103.11; senza provider, quote timestamp, mercato/scadenza di esecuzione o prova di fill.
- `position.json`: vecchia Heating Oil LONG del 15 settembre, entry 4.8844, stop 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882; identità contrattuale e quote mancanti.
- `data/paper_open.json`: WTI P0001 `OPEN` legacy, non riconciliato con il monitor corrente.
- `commodities_monitor_state.json`: timestamp 17 settembre, non aggiornato dalla run #170.
- `commodities_prediction_log.json`: 981 previsioni legacy; 945 PENDING, 36 NEUTRALE. Le 21 etichettate COMPRA ORA (19 RBOB, 2 Heating Oil) sono tutte PENDING, non fill.
- `gagarin_feedback.csv`: assente su main (404).

Nel job #170 il valore risolto di `DATABASE_URL` è vuoto. La persistenza condivisa del feedback non è quindi dimostrata in questa run. Nessun secret è stato letto o modificato.

### Outcome engine
Su main `engine/feedback.py`:
- lo schema feedback non conserva provider, quote ticker risolto, market type e scadenza;
- il matching successivo usa symbol/timeframe e fallback sul solo symbol quando esiste un unico stato;
- controlla SL prima dei target: un OHLC che tocca SL e TP nella stessa candela viene registrato STOP anche se la sequenza intrabar non è conoscibile.

[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) è OPEN, non integrata, 6 commit avanti / 6 indietro. Le sei GitHub Actions associate al suo head risultano SUCCESS. Il branch aggiunge identità ticker/mercato/contratto e `ESITO NON VERIFICABILE` per il doppio tocco SL/TP, ma `_market_contract_match()` non confronta esplicitamente `quote_provider` del segnale con il provider dello stato successivo. Il rilievo è già registrato nel commento PRAVDA [#6706619879](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6706619879); nessun commento duplicato.

### Nuova PR GAGARIN #238
[PR #238](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/238) è DRAFT, basata su #237, 26 commit avanti / 4 indietro rispetto a main. Separa `app_symbol`, `catalogue_ticker`, `catalogue_slug` e `broker_symbol`, correggendo l'assunzione errata che lo slug URL coincida con il simbolo feed/broker. La PR dichiara esplicitamente che il registry resta vuoto e che non aggiunge feed, prezzi o autenticazione di quote.
- GitHub Actions #1959 SOYUZ GAGARIN Tests e #3829 Execution Layer Tests: SUCCESS sul head `5508832a05bb7d5a95394c69dedd740972a765f0`.
- Il bot Cloudflare Workers ha però commentato [build fallito](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/238#issuecomment-6728797024) per il servizio `telegram-github-bridge`, commit `5508832`, alle 23:40:34 UTC, etichettato “production”. È un'integrazione esterna, non una GitHub Action; non prova un deploy riuscito. Non sono stati aperti i log Cloudflare.
- PR #237/#236/#233 e #234/#235 restano draft/stacked; la persistenza CFD durevole non è su main e non prova l'esistenza di un feed Trading 212. Nessun accesso a conto o quotazioni Trading 212 è stato effettuato o dichiarato.

Altre correzioni:
- [PR #222](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222) MERGED alle 20:24:56 UTC: rimosso il veto intraday `session_ok`; il monitor #170 resta comunque bloccato da MARKET_CLOSED e dati stale.
- [PR #221](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221) è draft per rimuovere le route FX residue.
- [PR #223](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223) è draft: M5 osservazionale a sette strumenti, Argento escluso, senza alert, journal, Governor o livelli.
- [PR #225](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225) è draft: propone cron offset `7,22,37,52`; main conserva `*/15 * * * *`.

## 5. Continuità GitHub Actions

| Processo | Cron su main | Ultime due run schedule consultate | Gap tra run | Gap al cut-off |
|---|---|---|---:|---:|
| SPUTNIK collector | `2-59/5 * * * *` | #289 16:15:37 → #291 20:35:50 UTC | 4h20m13s | 3h10m51s |
| SPUTNIK polling | ogni 5 min | #50 16:05:42 → #51 20:27:04 UTC | 4h21m22s | 3h19m37s |
| GAGARIN monitor | `*/15 * * * *` | #169 16:16:25 → #170 20:41:00 UTC | 4h24m35s | 3h05m41s |

Non risultano ulteriori run schedule entro il cut-off. Le run #259/#649 SPUTNIK e #1959/#3829 GAGARIN sono CI di PR, non scansioni produttive. La causa dei gap non è dimostrata. Il monitor #170 mostrava mercato chiuso; senza una run successiva non si può attestare lo stato delle quotazioni alla riapertura.

## 6. Esiti e statistiche

Nessun record dispone contemporaneamente di fill dimostrato, identità esatta provider/ticker/mercato/contratto/scadenza e candele successive omogenee. Non è possibile stabilire SL prima o TP prima.

- Fill verificati: **0**
- SL verificati: **0**
- TP verificati: **0**
- Win rate / average R / total R: **N/D**
- Nessun backtest prodotto o dichiarato.

## 7. Fonti consultate

- SPUTNIK run #291: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42520937991
- SPUTNIK polling #51: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42520176845
- GAGARIN run #170: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42521363444
- SPUTNIK PR #150, #131, #147, #145.
- GAGARIN PR #192, #238, #237, #236, #233, #235, #234, #221, #223, #225, #222.
- Ledger PRAVDA, `engine/feedback.py`, `journal.csv`, `paper_trade_log.csv`, `position.json`, `data/paper_open.json`, `commodities_monitor_state.json`, `commodities_prediction_log.json`.
- GitHub Actions job logs e PR comments/CI.

## 8. Prossimo controllo

1. Verificare la prima nuova run schedule SPUTNIK e GAGARIN dopo il cut-off.
2. Verificare se SPUTNIK #131 e #150 vengono integrate; poi controllare il recupero reale del nuovo RSS e la soppressione delle raccomandazioni senza nuovi item.
3. Verificare che GAGARIN torni a registrare quote fresche con timestamp assoluto e ticker/provider/mercato/scadenza.
4. Verificare lo stato delle PR #192, #221, #223, #225 e della catena #233–#238.
5. Riconciliare journal/feedback solo con prove di scrittura/lettura persistente.
6. Aggiungere nuovi record solo se il source ID/firma non esiste già; valutare outcome esclusivamente su prezzi successivi dello stesso identico contratto.

**Limiti e sicurezza:** nessun codice, strategia, filtro, punteggio o rischio modificato. Nessun merge o deploy effettuato da PRAVDA; nessun ordine reale; nessun secret o Render consultato/modificato; nessun servizio a pagamento; nessun accesso a Trading 212 o feed CFD dichiarato. PAPER ONLY.
