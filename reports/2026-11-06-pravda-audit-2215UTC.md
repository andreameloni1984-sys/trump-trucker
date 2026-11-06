# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-06 22:15 UTC (23:15 Europe/Rome)**

## Sintesi

- Nessun nuovo monitor di mercato dopo SPUTNIK [#42270098789](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42270098789) e GAGARIN [#42263910777](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42263910777).
- Ultimo collector SPUTNIK: 18:22:24 UTC; età al cut-off 3h53m04s. Cron dichiarato `2-59/5 * * * *`.
- Ultimo monitor GAGARIN: 17:41:19 UTC; età al cut-off 4h34m09s. Cron dichiarato `*/15 * * * *`.
- Nessun nuovo candidato di mercato rispetto al ledger: 35 righe dati, 35 firme uniche, zero duplicati.
- Nessun fill, SL o TP verificabile; statistiche di performance N/D.
- Correzione di audit: `sputnik_state.json` risulta vuoto (0 byte) sul commit del run SPUTNIK, su main e sul branch della PR #144. La precedente affermazione che quel file contenesse 500 record non è supportata dal contenuto verificato.
- GAGARIN PR #192 contiene una proposta concreta per identità contratto e ambiguità same-bar, ma è OPEN, non integrata e basata su un main molto precedente. Resta inoltre un problema di selezione del TP più alto quando più target ricadono nella stessa candela.

## 1. GitHub Actions e continuità

### SPUTNIK
- Ultimo collector schedule: [#42270098789](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42270098789), run #280, main SHA `88d4333691bdf81a2fdabfb929756470e084aadd`, avvio 18:22:24 UTC, conclusione 18:22:35 UTC, SUCCESS.
- Job: regression tests Telegram SUCCESS; esecuzione SPUTNIK SUCCESS; step “Persist SPUTNIK state” SUCCESS.
- Il precedente collector [#42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412) era partito alle 11:31:39 UTC: gap tra collector 6h50m45s.
- Le esecuzioni successive più recenti sono polling/summary o test PR, non nuovi collector di mercato.
- Il workflow dichiara cron `2-59/5 * * * *`.

### GAGARIN
- Ultimo monitor schedule: [#42263910777](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42263910777), run #160, main SHA `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`, avvio 17:41:19 UTC, job 17:41:22–17:41:36 UTC, SUCCESS.
- Il precedente monitor noto [#42203497432](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42203497432) era partito alle 10:32:52 UTC: gap tra monitor 7h08m27s.
- Dopo #42263910777 non compare un nuovo monitor prezzi nelle pagine recenti esaminate. Sono presenti summary, FETCH DRIVERS, polling e test PR, che non sono monitor prezzi.
- Cron dichiarato nel workflow: `*/15 * * * *`.
- Il polling [#42289526533](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42289526533) fallisce: validazione token superata, step “Run polling runner” fallito. Il conflitto webhook/getUpdates 409 resta quindi osservato su main.

I gap sono dimostrati dalle esecuzioni disponibili; la loro causa tecnica non è determinata.

## 2. Segnali e candidati esaminati

### SPUTNIK — GOLD SHORT, messaggi #711/#712
Un solo candidato, già presente nel ledger:
- Firma: `PRAVDA-SPUTNIK-CFD-RUN42270098789-20261106T182232Z-GOLD-SHORT-4069.3-4071.7536-4066.8465-4064.3929`.
- Run fonte: [#42270098789](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42270098789).
- Generazione CFD: 2026-11-06 18:22:32.111256 UTC.
- ACK API Telegram: 18:22:32.112773 UTC, message_id #712, round-trip 311 ms. È accettazione API, non prova di visualizzazione sul dispositivo o di esecuzione.
- Strumento: GOLD; mapping configurato `GC=F`; chiave/ticker runtime non esposti.
- Mercato: future continuo front-month; scadenza esatta UNKNOWN.
- Provider e timestamp/età quota: NOT_EXPOSED.
- Bias preliminare SHORT; entry 4069.30; SL 4071.7536; TP1 4066.8465; TP2 4064.3929; ATR 1.6357; score 70.
- La scheda analisi #711 indica SHORT preliminare/tecnico; la scheda CFD #712 indica tecnica LONG e D-L-A LONG (CONTRASTS). Il digest riporta NO_DIRECTIONAL_NEWS.
- NARWHAL non configurato; indipendenza upstream SILV non dimostrata; livelli marcati non operativi senza contratto/provenienza verificabili.

**Classificazione:** `EARLY_SETUP / NOT_EXECUTED`; non è un trade. **Esito: ESITO NON VERIFICABILE.** Non esistono candele forward attribuibili allo stesso contratto identificato.

Il log del run segnala inoltre:
- post pubblico 43495 pubblicato alle 12:01:50 UTC e rilevato alle 18:22:30.542 UTC: ritardo circa 6h20m40s; GOLD è usato metaforicamente nel contesto AI, ma il contenuto è stato etichettato METALS;
- post 43496 pubblicato alle 18:05:27 UTC e rilevato alle 18:22:30.542 UTC: ritardo circa 17m04s;
- SEC HTTP 403 e White House RSS HTTPError; zero filing e zero nuove operazioni.

### GAGARIN — WATCH board #3709
- Firma: `PRAVDA-GAGARIN-WATCH-RUN42263910777-20261106T174135Z-BOARD-MSG3709`.
- Run fonte: [#42263910777](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42263910777).
- Timestamp log/header: 17:41:32.167113 UTC; ACK API: 17:41:35.207004 UTC, message_id #3709, round-trip 436 ms.
- Il corpo del messaggio non è conservato nel log: strumento, ticker, direzione e livelli non sono attribuibili con certezza.
- Le otto righe commodity disponibili nel run erano YAHOO STALE, età 601.8–615.7 secondi.
- La classifica mostrava Argento LONG (probabilità 59, quality 49.5, confidence 32), ma questo non prova che il messaggio #3709 fosse riferito all'Argento. Il board può aggregare più candidati.
- Nessuna entry, SL, TP o ATR operativo; nessuna prova di fill.

**Classificazione:** WATCH pre-alert, NON_TRADE. Non entra nelle statistiche di performance.

### Candidati precedenti ancora nel ledger
- SPUTNIK GOLD LONG #707/#708 e GOLD SHORT #705: già registrati, nessun nuovo record.
- GAGARIN Grano SHORT WATCH #3701: già registrato; Yahoo stale 622.4s, trigger non confermato, mismatch, RR fail.
- Le altre predizioni storiche GAGARIN sono PENDING e non costituiscono trade eseguiti.

## 3. Journal, posizioni e feedback GAGARIN

File main verificati:
- `journal.csv`: 11 righe, tutte del 2026-10-17 con “nessun segnale”; nessun entry/SL/TP valorizzato.
- `paper_trade_log.csv`: un ticket WTI LONG legacy del 2026-10-08, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55. Provider, ticker di mercato, contratto/scadenza e fill non dimostrati.
- `data/paper_open.json`: posizione PAPER P0001 WTI LONG con gli stessi livelli; non è un secondo trade indipendente.
- `position.json`: Heating Oil LONG, HO/USD, entry 4.8844, SL 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882; opened_at 2026-09-15T13:23:44Z. Nessuna prova indipendente di fill, provider o contratto.
- `commodities_prediction_log.json`: 981 record; ultimo 2026-09-15T15:45:04.462276Z. Gli ultimi record sono PENDING; l'etichetta “COMPRA ORA” e score 100 non dimostrano esecuzione.
- `gagarin_feedback.csv`: 404 sul repository pubblico. Il workflow dichiara che i journal sono dati operativi privati e non vanno committati nel repository pubblico; la persistenza è subordinata a storage privato verificato. Non ho accesso al database privato né prova della sua disponibilità nel run corrente. Quindi il contenuto del feedback privato è **non ispezionabile**, non “zero”.

## 4. Verifica del motore outcome GAGARIN

Main attuale `engine/feedback.py` (blob SHA `41bec9bfab031c8dbf71121cd69d0e9b4c4f663f`):
- I campi persistiti non includono quote_symbol, market_type, contract_month o contract_expiry.
- La firma del forecast usa symbol, direction, timeframe, livelli e timestamp barra, ma non provider/ticker/mercato/scadenza.
- Il matching delle candele usa `(symbol, timeframe)` e, in assenza, un fallback per symbol quando esiste un solo state.
- Se SL e TP sono entrambi toccati nella stessa candela OHLC, main assegna STOP, benché l'ordine intrabar non sia noto.
- Se più TP sono toccati nella stessa candela, il codice seleziona `max(hit_targets)`, cioè il target più alto, senza prova di percorso/fill a quel livello.

### Correzione già proposta: GAGARIN PR #192
[PR #192 — Combine Gagarin exact-contract and ambiguous-outcome audit fixes](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) è OPEN, non merged, non draft. Head `295dba4b074e564a4c11aa3fca136a8e4360672c`; base main `c93906a2a4b28d60fd58c600b51cd3c05929f89d`, mentre main corrente è `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`: la PR non è basata sul main corrente.
- La branch aggiunge quote provider/timestamp/age, quote symbol, market type, contract month/expiry e ATR allo schema.
- La branch confronta quote symbol, market type e identità futures; futures continui senza contratto o con rollover diventano ESITO NON VERIFICABILE.
- La branch cambia same-bar SL+TP in ESITO NON VERIFICABILE senza R.
- Sei suite CI associate al commit PR #192 risultano SUCCESS (run #41981315423, #41981315298, #41981315378, #41981315376, #41981315318, #41981315414).
- Limite residuo dimostrato nel codice della branch: se più target sono raggiunti nella stessa candela senza SL, `max(hit_targets)` assegna il TP più alto. Il test aggiunto copre same-bar SL/TP, ma non il caso di più target nella stessa barra.

La PR #192 è un progresso reale e va registrata, ma non è attiva su main e il test suite verde non risolve il residuo TP multi-livello.

## 5. Stato PR e CI rilevante

### SPUTNIK
- [PR #145 — quote provenance/Yahoo diagnostics](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN; ranking tests e Telegram menu tests SUCCESS sul branch, run #42301132800 e #42301132667.
- [PR #146 — alert individuali/calendario](https://github.com/andreameloni1984-sys/trump-trucker/pull/146): OPEN; ranking e item intelligence tests SUCCESS, run #42281838872 e #42281838736.
- [PR #144 — persistenza stato off-main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN; ranking test SUCCESS su branch. Il file `sputnik_state.json` sul branch PR è però vuoto.
- [PR #131 — endpoint White House RSS](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): OPEN; non integrata, mentre il run collector più recente riporta ancora White House RSS HTTPError.
- [PR #107 — quote provenance CFD](https://github.com/andreameloni1984-sys/trump-trucker/pull/107): OPEN, non integrata.

### GAGARIN
- [PR #224 — calendario economico e alert](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/224): OPEN, non draft; sei suite SUCCESS sul branch.
- [PR #223 — scan M5 isolato a sette strumenti](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): OPEN/DRAFT; non attiva su main.
- [PR #221 — rimozione rotte FX residue](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): OPEN/DRAFT; non attiva su main.
- [PR #217/#207 — identità contratti Trading 212 CFD](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/217): OPEN/DRAFT e stacked; non attiva su main.
- [PR #218 — validazione timestamp BiQuote](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/218): OPEN/DRAFT e stacked; non attiva su main.
- [PR #175 — webhook/polling](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): OPEN; i test sul suo branch risultano verdi, ma il polling main #42289526533 fallisce ancora con 409.
- [PR #202 — journal/feedback persistente](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): OPEN/DRAFT; non dimostra storage privato attivo.

I test verdi di branch non equivalgono a merge, deploy o comportamento su main.

## 6. Ledger e statistiche

File: `reports/pravda-signal-ledger-2026-11-06.csv`
- Blob SHA: `0bf31f047b157129bf9329d1727f0078e9082e61`.
- Record dati: 35; firme uniche: 35; duplicati: 0.
- Tipi: 21 historical prediction candidate; 1 legacy paper ticket; 6 watch pre-alert; 6 CFD early setup NOT_EXECUTED; 1 watch-board pre-alert non attribuibile.
- Outcome ledger: 28 ESITO_NON_VERIFICABILE; 7 NON_TRADE.
- Nuovi record da aggiungere: 0. Il GOLD SHORT #712 e il WATCH board #3709 sono già presenti.
- Fill verificati: 0; TP verificati: 0; SL verificati: 0; outcome verificabili: 0.
- Win rate e average R: N/D (campione verificabile nullo).

## 7. Fonti consultate e prossimo controllo

Fonti:
- GitHub Actions: SPUTNIK #42270098789; GAGARIN #42263910777; GAGARIN polling #42289526533; job e step dei run.
- Branch main, metadati PR e CI per PR SPUTNIK #144/#145/#146/#131/#107 e GAGARIN #192/#224/#223/#221/#218/#217/#207/#175/#202.
- SPUTNIK `sputnik_state.json` su main, run commit e branch PR #144; workflow `.github/workflows/trump_tracker.yml`.
- GAGARIN `journal.csv`, `paper_trade_log.csv`, `data/paper_open.json`, `position.json`, `commodities_prediction_log.json`, `engine/feedback.py`, `.github/workflows/gagarin-monitor.yml`.
- Ledger PRAVDA e precedenti report già salvati.
- Nessun servizio a pagamento; nessun accesso Trading212 dichiarato; ACK Telegram API non equivale a consegna al dispositivo.

Prossimo controllo:
1. Verificare nuovi monitor di mercato effettivi, distinti da polling, summary, fetch e test.
2. Verificare la persistenza SPUTNIK su un artefatto non vuoto e leggibile; non considerare sufficiente il solo step “Persist state: SUCCESS”.
3. Verificare su main la provenienza quote SPUTNIK e la risoluzione RSS.
4. Verificare la PR #192 dopo rebase su main e chiedere copertura del caso multi-TP nella stessa candela.
5. Verificare disponibilità del feedback privato GAGARIN senza esporre segreti o dati privati.
6. Valutare outcome soltanto con candele successive dello stesso ticker, mercato e contratto/scadenza; se identità o sequenza intrabar non sono provate, lasciare ESITO NON VERIFICABILE.

**Perimetro:** audit/documentazione soltanto. Nessun codice bot, strategia, filtro, punteggio o rischio modificato; nessun merge, deploy, rerun o ordine reale; nessuna modifica a Render o segreti. PAPER ONLY.
