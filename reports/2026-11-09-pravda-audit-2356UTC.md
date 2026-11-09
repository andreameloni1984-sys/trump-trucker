# PRAVDA — Audit indipendente #22
## SPUTNIK / GAGARIN
**Rilevazione: 2026-11-09 23:56 UTC / 2026-11-10 00:56 CET**

## Perimetro e metodo

Controllo indipendente dei repository `andreameloni1984-sys/trump-trucker` e `andreameloni1984-sys/commodity-news-scanner`: elenco GitHub Actions (run recenti, distinguendo `schedule`, `push` e `pull_request`), log integrali delle run rilevanti, commit `main`, file di universo, Telegram, feedback e journal, stato e diff delle PR.

Nessun codice applicativo modificato. Nessun merge, deploy, ordine reale, modifica a secret o Render. PAPER ONLY. Nessun servizio a pagamento. Nessun accesso a Trading212 dichiarato.

## 1. Registro PRAVDA

CSV ereditato dal precedente audit e riletto con parser CSV indipendente:

- Record: **106**
- SPUTNIK: **50**
- GAGARIN: **56**
- Firme uniche: **106**
- Source ID unici: **106**
- Duplicati firma: **0**
- Duplicati source ID: **0**
- `NON_TRADE`: **77**
- `ESITO_NON_VERIFICABILE`: **29**
- Fill verificati: **0**
- SL verificati: **0**
- TP verificati: **0**

SHA del ledger: `41a1339c2047c86ad9026ab131d9a8015d0cd710`.

Nessun nuovo segnale operativo distinto è emerso: il ledger resta invariato. Non sono state aggiunte righe. Win rate, Average R e Total R restano **N/D**. Le 106 righe sono candidati, notifiche e record legacy, non 106 trade.

[Ledger cumulativo PRAVDA](https://github.com/andreameloni1984-sys/trump-trucker/blob/pravda/audit-2026-11-09-2227UTC/reports/pravda-signal-ledger-2026-11-09.csv)

## 2. SPUTNIK — GitHub Actions e stato

### Collector #295

[Run #295](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42650624196)

- Evento: `schedule`
- Avvio: 2026-11-09 16:02:05 UTC
- Completamento: 16:02:23 UTC
- Job `sputnik`: SUCCESS
- SHA di checkout riportato nei metadati Actions: `a9603cadff2ddc2f2a9603c00b014ac56a45c291`

Il log conferma:
- SEC HTTP 403, cooldown 21.600 secondi, 0 filing;
- 0 nuove operazioni documentate;
- White House RSS HTTPError;
- scansione intelligence pubblica: 6.665 ms, 1 finding;
- forwarding GAGARIN: 0 ms, senza identificativo di richiesta o conferma di ricezione.

Il run ha poi generato i messaggi GOLD #752 e #753. Telegram ha restituito `delivery confirmed` e message ID per entrambi: è prova di accettazione API, non prova di visualizzazione sul dispositivo.

### Commit di persistenza e correzione di un audit precedente

Il run #295 ha prodotto il commit [`6c3095f`](https://github.com/andreameloni1984-sys/trump-trucker/commit/6c3095f1534550b0b4e77170f1428db833253c05), messaggio `chore: persist Sputnik state`, con parent `a9603cad...`. Il diff aggiorna `sputnik_state.json` alle 16:02:16.818 UTC.

**Rettifica PRAVDA:** il diff prova che OGE era un finding runtime realmente persistito, non soltanto una riga di test. Evento:
- ID: `d6b0ef156154af76e574dd50`
- Fonte: OGE
- URL: `https://www.oge.gov/`
- Evidence: `PUBLIC_SOURCE_TEXT_PAGE_LEVEL`
- Titolo: vuoto
- Published: vuoto
- Detected: 2026-11-09 16:02:16.531 UTC
- Event type: `OTHER`
- Historical matches: nessuno
- Evidence storico: `NO_ANALOGUE`

La precedente rettifica che aveva ritirato l'attribuzione OGE è quindi superata: il commit di stato dimostra il finding. Resta però una scansione homepage/page-level, non un item RSS individuale con permalink e data di pubblicazione. Non è un catalizzatore direzionale verificato.

### Polling #55

[Run #55](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42723841180)

- Evento: `schedule`
- Avvio: 2026-11-09 23:51:48 UTC
- Completamento: 23:51:58 UTC
- SUCCESS
- Log: `Pending updates: 0`; `Polling run completed`.

Questa è una run di polling, non una nuova scansione intelligence/mercato e non una prova di invio di nuove notifiche. L'ultimo collector programmato resta #295 alle 16:02:05 UTC: gap al controllo circa **7h54m**. La lista recente delle Actions non mostra un collector schedule successivo.

## 3. SPUTNIK — segnali esaminati

### GOLD SHORT #751

Run #294, evento PUSH (non usarla come prova di ripresa del cron).

- Generazione: 2026-11-09 15:33:13.053 UTC
- API ACK: 15:33:13.055 UTC
- Strumento mostrato: GOLD
- Ticker/contratto esatto: non risolto
- Mercato: card CFD, corpo riferito a future continuo front-month
- Scadenza: assente
- Provider e timestamp quotazione: assenti
- Direzione: SHORT
- Entry: 4125.6001
- SL: 4128.3859
- TP1: 4122.8143
- TP2: 4120.0285
- ATR: 1.8572
- Score: 100
- D-L-A: NEUTRAL
- Stato: `NOT_EXECUTED`

**Classificazione: NON_TRADE.** I livelli non sono certificabili e la card stessa avverte di non utilizzarli.

### GOLD LONG #753

Run #295, evento SCHEDULE.

- Generazione: 2026-11-09 16:02:18.585 UTC
- API ACK: 16:02:18.586 UTC
- Strumento mostrato: GOLD
- Ticker/contratto esatto: non risolto
- Mercato: card CFD, corpo riferito a future continuo front-month
- Scadenza: assente
- Provider e timestamp quotazione: assenti
- Direzione: LONG
- Entry: 4129.2998
- SL: 4126.9106
- TP1: 4131.689
- TP2: 4134.0781
- ATR: 1.5928
- Score: 100
- D-L-A: LONG — ALIGNS
- Stato: `NOT_EXECUTED`

Il log del collector riporta 0 filing, 0 nuove operazioni, 1 correlazione pubblica; la card preliminare #752 dichiara `NO_DIRECTIONAL_NEWS`. L'evento OGE page-level sopra descritto non ha data di pubblicazione, permalink individuale né classificazione direzionale. Questo è un riscontro coerente con la necessità della PR #150.

**Classificazione: NON_TRADE.** Non attribuire SL/TP: mancano provider, ticker di quotazione, contratto/scadenza e candele successive della stessa serie.

### Ritardi e consegna

I round-trip API riportati per #752 e #753 sono rispettivamente 590 ms e 608 ms. I timestamp mostrano invio quasi immediato dopo la generazione, ma non misurano il ritardo tra evento pubblico originario e rilevazione. Gli ACK API non provano la visualizzazione sul dispositivo.

## 4. SPUTNIK — PR e correzioni esistenti

- [PR #150](https://github.com/andreameloni1984-sys/trump-trucker/pull/150): OPEN, non integrata. Estrae l'eligibilità item-level del digest e limita la coppia raccomandazione/CFD a nuovi item RSS con event ID, permalink e published. Il run #295 rafforza la necessità: il finding OGE page-level non soddisfa i requisiti, ma vengono generati GOLD #752/#753. La PR mantiene ancora `values()[-30:]` nella selezione della cronologia: non risolve il distinto difetto di ordinamento.
- [PR #156](https://github.com/andreameloni1984-sys/trump-trucker/pull/156): OPEN, non integrata. Corregge la selezione dei 30 record più recenti ordinando per `detected_at`; resta separata dalla #150.
- [Commento PRAVDA su #150](https://github.com/andreameloni1984-sys/trump-trucker/pull/150#issuecomment-6754784960): registra l'evento OGE del commit di stato e la rettifica dell'audit precedente.

## 5. GAGARIN — GitHub Actions e nuova PR #250

Main resta `631727912b3a2022379a4460f4b6f756eba6991f`.

### Monitor #173

[Run #173](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42659137635)

- Evento: `schedule`
- Avvio: 2026-11-09 16:52:38 UTC
- Completamento: 16:53:01 UTC
- SUCCESS
- Commit di checkout: `50b25a80d6792be913c2bcf5a117ede68dd52b59`
- Non è una scansione della successiva versione main `6317279`.

Età delle quotazioni nel log:
- Oro YAHOO: 602,6 s — STALE
- Argento YAHOO: 626,6 s — STALE
- Rame YAHOO: 604,7 s — STALE
- WTI YAHOO: 601,8 s — STALE
- Brent YAHOO: 605,0 s — STALE
- Grano YAHOO: 604,0 s — STALE
- Mais YAHOO: 606,1 s — STALE
- Soia YAHOO: 603,5 s — STALE
- EUR/USD BIQUOTE: 176,2 s — LIVE (ausiliario)
- GBP/USD BIQUOTE: 176,9 s — LIVE (ausiliario)

Risultato:
`Recorded entries: 0`; `Updated open outcomes: 0`; `New feedback signals: 0`; `New additional live forecasts: 0`; `signals=0 open=0 closed=0`.

Nessuna entrata autorizzata. Nessuna nuova scansione `schedule` GAGARIN compare nell'elenco delle run recenti fino al controllo. L'ultima scansione produttiva verificata è quindi #173, circa **7h03m** prima del controllo.

### Telegram polling #20

[Run #20](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42660005021): FAILURE, 2026-11-09 16:58:05–16:58:21 UTC. Telegram `getUpdates` restituisce HTTP 409 perché il webhook è attivo. [PR #175](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175) resta OPEN e non integrata.

### Nuova PR #250 — confronto manuale Trading 212

[PR #250](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/250) è OPEN/DRAFT, non integrata, head `16173e600f9f71d5fe2000c3adc06cfdec959791`, base main `6317279`.

Verifica diretta dei file:
- main `telegram/bot.py` SHA `f1eec468ce4ae90ba300215d18e9eea62fbe8571`: ancora presenti `compare_price` e `parse_bid_ask`, con i comandi di confronto manuale.
- branch PR `telegram/bot.py` SHA `c09f6cc963938e74f04da3a73d4cd6827481fbfb`: il bot attivo non importa più quei metodi; `/prezzo212` risponde disattivato e `/aggressivo212` rifiuta argomenti Bid/Ask prima dell'analisi.

Sei workflow `pull_request` associati all'head #250 risultano SUCCESS: Public Event Brain, SOYUZ GAGARIN PAPER, Telegram menu, SOYUZ GAGARIN Tests, Execution Layer, NEWS alert. I test aggiunti verificano assenza degli import e rifiuto degli input manuali.

La correzione evita il confronto improprio tra CFD inseriti manualmente e la serie futures usata da GAGARIN. È coerente con il perimetro richiesto, ma non è ancora su main né verificata in produzione. Nessun accesso a Trading212 è stato usato o dichiarato.

[Commento PRAVDA #6754766834](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/250#issuecomment-6754766834)

## 6. Universo GAGARIN

Il file `commodities/universe.py` su main contiene ancora 13 simboli:
`XAU/USD, XAG/USD, COPPER/USD, WTI/USD, BRENT/USD, WHEAT/USD, CORN/USD, SOYBEAN/USD, EUR/USD, DAX, SP500, NVDA, TSLA`.

[PR #248](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/248) propone il paniere esatto a otto commodity. È OPEN/DRAFT, non integrata, head `87367cafbcf37546d7736c13f228a0086703d598`, base main `6317279`, 17 commit ahead / 0 behind. I sette workflow PR risultano SUCCESS; la suite principale riporta 570 test superati. È prova CI sul branch, non prova di produzione o deploy. Il main resta a 13 strumenti fino all'eventuale integrazione autorizzata.

## 7. Journal e feedback GAGARIN

File `commodities_prediction_log.json` su main:
- 981 record;
- 945 PENDING;
- 36 NEUTRALE;
- ultimo record: 2026-09-15 15:45:04 UTC;
- azioni: NON ENTRARE 77; ATTENDERE 576; SHORT — ASPETTARE CONFERMA 15; LONG — ASPETTARE CONFERMA 292; COMPRA ORA 21.

Tutte le 21 righe COMPRA ORA sono PENDING: non sono trade eseguiti.

`paper_trade_log.csv`: un solo WTI `LEGACY_IMPORT`, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55; nessuna prova di fill o P&L. Il vecchio ticket non viene trattato come operazione verificata.

`gagarin_feedback.csv`: non trovato (GitHub contents API 404). Nel log #173 `DATABASE_URL` è vuota. Persistenza durevole del journal tra esecuzioni non dimostrata.

## 8. Outcome engine

Il file main `engine/feedback.py` SHA `41bec9bfab031c8dbf71121cd69d0e9b4c4f663f` non contiene campi espliciti provider, market type e contract expiry nel record verificato. Il matching si basa principalmente su symbol/timeframe e il controllo STOP precede il controllo target: una candela che tocca SL e TP può essere classificata STOP.

[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) propone fingerprint con provider/ticker/mercato/contratto e doppio tocco nella stessa candela come `ESITO NON VERIFICABILE`, ma resta OPEN e la sua base è un vecchio SHA main `c93906a...`, non l'attuale `6317279`. La correzione non è integrata. Non certificare performance finché la serie successiva non è verificata sul medesimo provider, ticker, mercato e contratto.

## 9. Esiti e statistiche

Segnali numerici SPUTNIK esaminati: GOLD SHORT #751 e GOLD LONG #753, entrambi `NOT_EXECUTED` → `NON_TRADE`; provider, ticker contrattuale, scadenza e OHLC successive omogenee assenti.

GAGARIN #173: zero entry e zero nuove previsioni live; #3734 è un WATCH pre-alert senza corpo conservato e senza attribuzione certa di strumento/direzione.

Nessun campione di trade eseguito con identità contrattuale completa e OHLC successive. Pertanto:
- Fill verificati: 0
- SL verificati: 0
- TP verificati: 0
- Win rate: N/D
- Average R: N/D
- Total R: N/D

## 10. Fonti consultate

- [SPUTNIK collector #295](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42650624196)
- [SPUTNIK polling #55](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42723841180)
- [Commit SPUTNIK state #6c3095f](https://github.com/andreameloni1984-sys/trump-trucker/commit/6c3095f1534550b0b4e77170f1428db833253c05)
- [SPUTNIK PR #150](https://github.com/andreameloni1984-sys/trump-trucker/pull/150)
- [SPUTNIK PR #156](https://github.com/andreameloni1984-sys/trump-trucker/pull/156)
- [GAGARIN monitor #173](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42659137635)
- [GAGARIN Telegram polling #20](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42660005021)
- [GAGARIN PR #248](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/248)
- [GAGARIN PR #250](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/250)
- [GAGARIN PR #175](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175)
- [GAGARIN PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192)

## 11. Prossimo controllo

1. Verificare la prossima run schedule del collector SPUTNIK, non confonderla con il polling.
2. Verificare che le raccomandazioni SPUTNIK siano soppresse in assenza di un nuovo item RSS datato e con permalink; tenere distinti OGE page-level e catalizzatori item-level.
3. Verificare la prima scansione produttiva GAGARIN successiva al main `6317279`.
4. Verificare se PR #248 viene integrata e se il main passa da 13 a esattamente 8 commodity.
5. Verificare la PR #250 dopo eventuale integrazione: nessun confronto manuale CFD/futures.
6. Risolvere il 409 webhook/polling e dimostrare la persistenza cross-run del journal.
7. Correggere il matching outcome per provider, ticker, mercato e scadenza; doppio tocco intrabar non ricostruibile = `ESITO NON VERIFICABILE`.

**Verdetto:** il polling SPUTNIK è tornato a eseguire una run schedulata (#55) ma ha processato zero aggiornamenti; il collector resta fermo alla #295. GAGARIN non ha una nuova scansione schedule dopo #173. La PR #250 è una correzione utile e testata per eliminare il confronto manuale Trading 212 CFD/futures, ma è ancora draft. Il paniere GAGARIN a otto commodity è ancora solo nella PR #248. Nessun risultato di trading è verificabile.

**PRAVDA — PAPER ONLY.**
