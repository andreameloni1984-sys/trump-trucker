# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
## Controllo #16 — 9 novembre 2026, 18:52 CET (17:52 UTC)

## Esito sintetico

Verificati i run produttivi più recenti, i log integrali dei job, i workflow YAML su `main`, i journal/feedback pubblici, il codice dell'outcome engine e le PR pertinenti.

Novità di questo controllo:
- SPUTNIK: l'ultima scansione collector resta la #295 delle 16:02:05 UTC; nessun run schedule successivo compare nella cronologia consultata. Il polling #54 è l'ultimo schedule, alle 15:43:25 UTC.
- GAGARIN: il monitor #173 è una nuova scansione produttiva schedule, ma le otto commodity sono tutte STALE. La scansione non ha registrato entry, feedback o nuove previsioni.
- GAGARIN Telegram polling #20 è fallito nuovamente con API 409: webhook attivo incompatibile con getUpdates.
- L'outcome engine su main continua a non vincolare il matching a provider, mercato e scadenza; nella stessa candela classifica STOP prima di TP.
- Il ledger PRAVDA non richiede nuove righe: i messaggi #753 e #3734 erano già stati registrati nel controllo #15.

Nessun nuovo trade verificabile. Nessun esito SL/TP attribuibile.

## 1. Registro PRAVDA

Ledger letto dal branch precedente `pravda/audit-2026-11-09-1658UTC`.

- Record: 106
- Firme uniche: 106
- Source ID unici: 106
- SPUTNIK: 50
- GAGARIN: 56
- Duplicati: 0
- NON_TRADE: 77
- ESITO_NON_VERIFICABILE: 29
- Fill verificati: 0
- SL verificati: 0
- TP verificati: 0

SHA ledger invariato: `41a1339c2047c86ad9026ab131d9a8015d0cd710`.

Non è stata aggiunta alcuna riga. Il WATCH #3734 è già registrato come pre-alert non attribuibile; la card GOLD #753 è già registrata una sola volta insieme all'analisi compagna #752.

Win rate, average R e total R restano N/D: non esiste un campione di fill e outcome verificati.

Ledger: https://github.com/andreameloni1984-sys/trump-trucker/blob/pravda/audit-2026-11-09-1658UTC/reports/pravda-signal-ledger-2026-11-09.csv

## 2. SPUTNIK — produzione e cadenza

Repository main head al controllo: `6c3095f1534550b0b4e77170f1428db833253c05`.

Workflow principale `.github/workflows/trump_tracker.yml`: cron `2-59/5 * * * *`.
Telegram polling: cron `*/5 * * * *`.
Daily summary: cron `0 6 * * *`.

Ultimi run schedule verificati:
- Collector #295: 2026-11-09 16:02:05 UTC, SUCCESS, concluso 16:02:23 UTC.
- Telegram polling #54: 15:43:25 UTC, SUCCESS, `Pending updates: 0`.
- Daily summary #12: 14:48:35 UTC, SUCCESS; Telegram API ha accettato il messaggio #749, ma il corpo non è conservato e non viene contato come segnale.
- Collector #294 alle 15:33:04 UTC era `event=push`, non schedule.

Al cut-off 17:52:42 UTC:
- ultimo collector schedule #295: 1h50m37s;
- ultimo polling schedule #54: 2h09m17s;
- daily summary #12: 3h04m07s.

La ripresa del collector è quindi isolata, non una prova di cadenza regolare ogni 5 minuti. La causa dei gap non è dimostrata.

### Raccolta fonti nel run #295

Log del job `sputnik`:
- SEC: HTTP 403; cooldown 21.600 secondi.
- Filing: 0.
- White House RSS `https://www.whitehouse.gov/feed/`: HTTPError.
- Intelligence pubblica: un finding.
- Il commit di stato successivo registra un elemento OGE page-level con evento OTHER, nessun analogo storico e nessuna direzione di mercato.

Il commit `6c3095f` è una prova di persistenza GitHub dello stato per questa run: il diff aggiorna `updated_at` a `2026-11-09T16:02:16.818516Z`, aggiorna il fingerprint OGE e mantiene offset Telegram. Non equivale a prova di consegna sul dispositivo o a un segnale operativo.

### GOLD — messaggi #752 e #753

Run: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42650624196

I messaggi sono una sola opportunità e vengono contati una volta, usando la card #753.

Analisi #752:
- generata nel log alle 16:02:18.582 UTC circa;
- GOLD, bias LONG;
- tecnica LONG 5m;
- momentum 15m +0,031%;
- NO_DIRECTIONAL_NEWS;
- stato EARLY_BIAS;
- API Telegram ACK #752 alle 16:02:18.584 UTC circa, round-trip 590 ms.

Card #753:
- generata alle 16:02:18.5846201 UTC;
- API Telegram ACK alle 16:02:18.5856255 UTC, round-trip 608 ms;
- strumento logico GOLD;
- ticker contrattuale: NOT_RESOLVED;
- direzione LONG;
- tecnica LONG / D-L-A LONG ALIGNS;
- entry 4129.2998;
- SL 4126.9106;
- TP1 4131.689;
- TP2 4134.0781;
- TP3 assente;
- ATR 1.5928;
- score 100;
- stato EARLY_SETUP / NOT_EXECUTED.

Identità/provenienza mancanti:
- titolo CFD, corpo dichiarato future continuo front-month;
- scadenza esatta sconosciuta;
- provider non esposto;
- timestamp ed età della quotazione non esposti;
- prezzo di riferimento non registrato;
- NARWHAL NOT_CONFIGURED;
- indipendenza del controllo SPOT/FUTURES non verificata.

La card dice espressamente di non usare i livelli. Score 100 non costituisce validità operativa. NOT_EXECUTED non è un trade. Senza ticker/contratto/provider e candele successive della stessa serie, l'esito è ESITO NON VERIFICABILE; non si attribuisce né SL né TP.

PR #153 resta OPEN/non integrata: il difetto di propagazione della direzione tecnica era stato riprodotto sulle card #748 e #751. La card #753 non ripete quella specifica contraddizione, ma questo singolo caso non certifica la correzione generale.

### PR SPUTNIK pertinenti

- PR #155 cadence diagnostics: OPEN, non integrata. Commento PRAVDA aggiornato con il gap corrente.
- PR #153 technical direction in CFD card: OPEN, non integrata.
- PR #154 tariff analogue on generic China mentions: OPEN, non integrata.
- PR #131 White House RSS endpoint: OPEN, non integrata.

Commento cadence PRAVDA #155: https://github.com/andreameloni1984-sys/trump-trucker/pull/155#issuecomment-6747446646

## 3. GAGARIN — monitor #173

Repository main head al controllo: `5f523c6f5db62eed4bb3468874285155ed8cd455` (driver snapshot del 9 novembre). Il monitor #173 ha eseguito sul precedente main SHA `50b25a80d6792be913c2bcf5a117ede68dd52b59`.

Run: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42659137635

- Evento: schedule.
- Avvio: 16:52:38 UTC.
- Fine: 16:53:01 UTC.
- Risultato: SUCCESS.
- Run precedente monitor #172: avvio 06:34:18 UTC.
- Gap start-to-start: 10h18m20s.
- Cron su main: `*/15 * * * *`.

Al cut-off 17:52:42 UTC il run #173 era trascorso da 1h00m04s. Nessuna scansione monitor schedule successiva compare nella cronologia consultata.

### Quotazioni #173

Tutte le otto commodity operative hanno provider YAHOO e stato STALE:
- Rame 604,7 s;
- Grano 604,0 s;
- WTI 601,8 s;
- Mais 606,1 s;
- Soia 603,5 s;
- Oro 602,6 s;
- Brent 605,0 s;
- Argento 626,6 s.

EUR/USD 176,2 s e GBP/USD 176,9 s risultano LIVE via BIQUOTE, ma il log li classifica come Forex ausiliari/non operativi.

Il timestamp assoluto della singola quotazione e il contratto/scadenza delle serie commodity non sono esposti nel riepilogo. Questi valori sono riferiti al run delle 16:52 UTC, non sono prezzi aggiornati al cut-off dell'audit.

### Risultato del motore

- Recorded entries: 0.
- Updated open outcomes: 0.
- New feedback signals: 0.
- New additional live forecasts: 0.
- signals=0, open=0, closed=0.
- win_rate=N/D, avg_R=N/D, total_R=0.0.

Tutte le commodity sono PAPER_WATCH senza setup autorizzato e senza entry/SL/TP/ATR completi.

### Telegram #3734

- API SEND CONFIRMED alle 16:52:57.4478258 UTC circa.
- Message ID 3734.
- Round-trip 556 ms.
- Il corpo non è conservato nel log.

È già registrato nel ledger come WATCH pre-alert non attribuibile. Non si può assegnare strumento, ticker, direzione, provider, livelli o outcome. ACK API non prova visualizzazione sul dispositivo.

## 4. Telegram polling GAGARIN — errore 409 riprodotto

Run #20: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42660005021

- Avvio 16:58:05 UTC.
- Token validation: OK.
- Telegram diagnostic: OK.
- getUpdates: HTTP/API 409.
- Errore: webhook attivo; polling non consentito mentre webhook mode è attivo.
- Conclusione: FAILURE alle 16:58:19 UTC.

Il conflitto webhook/getUpdates è quindi riprodotto su main. PR #175 contiene già la gestione specifica `WebhookActiveError` per saltare il polling senza cancellare il webhook e senza ack degli update, ma resta OPEN/non integrata e la base della PR è precedente all'attuale main.

Commento PRAVDA già presente sulla PR #175: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175#issuecomment-6746165769

## 5. Universo GAGARIN e journal/feedback

Il file `commodities/universe.py` su main abilita 10 strumenti logici:
- Oro XAU/USD;
- Argento XAG/USD;
- Rame COPPER/USD;
- WTI;
- Brent;
- Grano;
- Mais;
- Soia;
- EUR/USD;
- GBP/USD.

Il run #173 conferma 8 commodity operative più 2 Forex ausiliari. Argento è ancora incluso nel monitor; Platino e Palladio non sono presenti nell'universo corrente. Le PR di modifica del perimetro non sono integrate: nessuna modifica è stata effettuata da PRAVDA.

### Prediction log storico

`commodities_prediction_log.json`:
- 981 record;
- 981 ID unici;
- 945 PENDING;
- 36 NEUTRALE;
- operational_signal: WAIT 960, LONG 15, campo assente 6;
- ultimo created_at: 2026-09-15T15:45:04.462276Z;
- 25 simboli storici.

Le 15 righe LONG e le etichette storiche COMPRA ORA restano PENDING: non sono prova di fill né trade eseguiti. Il log storico include strumenti fuori dall'universo attuale e non va usato come performance del paniere corrente.

### Journal e storage

- `journal.csv`: 11 vecchie righe di osservazione senza segnali.
- `data/paper_open.json`: WTI P0001 LONG, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55, OPEN legacy, P&L null; nessuna prova di fill.
- `paper_trade_log.csv`: WTI LEGACY_IMPORT, non è un secondo trade verificato.
- `gagarin_feedback.csv`: 404, file non presente su main.
- Nel job #173 `DATABASE_URL` è vuota.

La persistenza durevole del journal/feedback non è dimostrata. Il runner GitHub usa storage locale/ephemeral in assenza di DATABASE_URL; non è stata verificata alcuna banca dati esterna.

## 6. Outcome engine — difetto dimostrato su main

Su main, `engine/feedback.py`:
- i campi feedback non conservano provider, ticker quotato, market type, contract month o expiry;
- il fingerprint usa symbol, direzione, timeframe, livelli e timestamp candela;
- l'abbinamento successivo usa symbol + timeframe, con fallback symbol-only se c'è un solo stato;
- se una candela tocca SL e TP, il ramo STOP viene valutato prima dei target e registra STOP.

Questo non rispetta la regola PRAVDA. Se l'ordine intrabar non è ricostruibile, l'esito corretto è ESITO NON VERIFICABILE.

PR #192 propone campi provider/ticker/mercato/scadenza, matching di ticker/mercato/contratto e gestione del doppio tocco come ESITO NON VERIFICABILE. Ma:
- PR #192 è OPEN/non integrata;
- il branch è basato su una revisione main precedente;
- nel suo `_market_contract_match()` il provider è registrato nel fingerprint ma non viene confrontato esplicitamente tra il provider del segnale e quello dello stato successivo.

Quindi la correzione è parziale e non attiva in produzione.

PR #192: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192

## 7. PR e CI rilevanti

- GAGARIN PR #243: OPEN/DRAFT, head `08ec51fc`. I sette workflow GitHub sul commit finale risultano SUCCESS; il commento Cloudflare segnala un deployment build FAILED. Non è integrata né distribuita. La PR rimuove il legacy Invest-account polling/commands e i riferimenti alle credenziali Invest nel workflow manuale; dichiara esplicitamente che non implementa il canale dati CFD separato. Nessun accesso a Trading212 o feed CFD è dimostrato.
- GAGARIN PR #175: OPEN, non integrata; risolve il conflitto webhook/polling.
- GAGARIN PR #225: OPEN/DRAFT; propone cron offset `7,22,37,52`, ma non ha validazione runtime post-merge e main resta `*/15`.
- GAGARIN PR #240: OPEN/DRAFT; la patch modifica limiti temporali di freschezza (20→10 minuti e M5 1200→600 secondi). Tali modifiche sono soglie/filtri e non sono autorizzate dalle istruzioni correnti; PRAVDA non le ha approvate né integrate.
- GAGARIN PR #192: OPEN/non integrata; matching provider incompleto come sopra.

PR #243: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/243
PR #175: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175
PR #225: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225
PR #240: https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/240

## 8. Segnalazioni PRAVDA inviate

- SPUTNIK PR #155: commento cadence con #295, #294 push e polling #54; ID commento 6747446646.
- GAGARIN PR #225: commento cadence con #173, gap 10h18m20s, tutte le commodity stale e zero entry/feedback; ID commento 6747447502.

I commenti sono audit-only. Nessun codice, workflow, filtro o soglia modificati.

## 9. Statistiche e classificazione esiti

Campione verificabile di operazioni eseguite: n=0.
- Fill verificati: 0.
- SL verificati: 0.
- TP verificati: 0.
- Win rate: N/D.
- Average R: N/D.
- Total R: N/D.

Nessuna candela successiva dello stesso identico strumento, provider, mercato e contratto è disponibile per attribuire un outcome ai candidati GOLD #751/#753. La candidata Soia e gli altri setup del run #173 sono stati bloccati prima dell'ingresso. I pre-alert #3728/#3734 non sono segnali attribuibili a uno strumento.

## 10. Prossimo controllo

1. Verificare una nuova scansione collector SPUTNIK schedule, distinguendola da push/test/daily summary.
2. Verificare la continuità del monitor GAGARIN e la freschezza delle otto commodity.
3. Verificare il recepimento della gestione webhook 409 senza cancellare il webhook né ack non elaborati.
4. Verificare l'identità ticker/mercato/scadenza/provider per ogni futura card GOLD.
5. Completare il matching provider nel feedback engine e mantenere ESITO NON VERIFICABILE per doppio tocco intrabar.
6. Dimostrare la persistenza durevole del journal; in assenza di DATABASE_URL classificare lo storage come locale/ephemeral.
7. Chiarire l'universo effettivamente autorizzato; nessuna PR di modifica perimetro è stata integrata.

## 11. Limiti e sicurezza

- Nessun accesso a Trading212 dichiarato.
- Nessuna consegna Telegram al dispositivo dichiarata: sono disponibili soltanto gli ACK API riportati.
- Nessun servizio a pagamento.
- Nessun secret letto o modificato.
- Nessun intervento su Render o webhook.
- Nessun ordine reale.
- Nessun merge o deploy.
- Nessuna modifica a codice, strategia, filtri, soglie, score, direzione o rischio.

**PRAVDA — PAPER ONLY.**
