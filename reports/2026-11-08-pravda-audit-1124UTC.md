# PRAVDA — Audit incrementale SPUTNIK / GAGARIN

**Cut-off:** 8 novembre 2026, 11:24:53 UTC (12:24:53 Europe/Rome)  
**Perimetro:** ultime GitHub Actions di produzione su `main`, log completi dei job, journal e file di stato GAGARIN, ledger PRAVDA e PR aperte/CI. Verifica documentale indipendente. PAPER ONLY.

## 1. Esito sintetico

- **Nuovi segnali operativi verificati: 0.** Le ultime run di produzione disponibili sono SPUTNIK #288 e GAGARIN #168, entrambe SUCCESS ma senza un trade direzionale verificabile.
- Il ledger PRAVDA esistente contiene **85 record**, 85 firme uniche e 85 source ID unici: **0 duplicati**. Distribuzione: SPUTNIK 36, GAGARIN 49; 56 `NON_TRADE`, 29 `ESITO_NON_VERIFICABILE`.
- Fill verificati: **0**; SL verificati: **0**; TP verificati: **0**. Win rate, average R e total R restano **N/D**.
- I messaggi Telegram osservati hanno ACK API, non prova di consegna sul dispositivo.
- Nessun artifact allegato alle due run. I log completi dei job sono disponibili e costituiscono la prova primaria per questo controllo.
- Il ledger non è stato modificato: i messaggi #731–#733 e #3719 erano già presenti. Non è stato aggiunto alcun duplicato.

## 2. SPUTNIK — ultima run di produzione

Run: [Actions #42467543117](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42467543117)  
Workflow: `SPUTNIK`, run #288; branch `main`, SHA `1ec9e96892edab84606294b0d80965faf3c831a7`.  
Job: `sputnik`, ID `128690443372`; esito SUCCESS. Nessun artifact.

### Raccolta fonti e ritardo

- SEC: HTTP 403; cooldown di 21.600 secondi; 0 filing recuperati e 0 operazioni documentate.
- White House RSS configurato su `https://www.whitehouse.gov/feed/`: HTTPError.
- La scansione pubblica ha registrato due correlazioni; nessuna correlazione ha prodotto una mappatura commodity/direzione verificabile.
- Item Truth Archive già presente nel ledger: event ID `f3dd016d2288efc8d1a89d79`, pubblicato alle **03:53:01 UTC**, rilevato alle **09:31:37.313495 UTC**: ritardo **5h38m36s**.
- L'item è classificato MEDIA / OTHER / NO_ANALOGUE; nessun ticker, mercato, scadenza, quotazione, provider, direzione o livello. È intelligence, non segnale.

### Messaggi Telegram verificati nei log

| Message ID | Generazione/rilevazione UTC | ACK API UTC | Contenuto | Classificazione |
|---|---|---|---|---|
| 731 | 09:31:37.313495 | 09:31:38.5640305 | Digest item Truth Archive sopra | INTELLIGENCE_ONLY / NON_TRADE |
| 732 | 09:31:38.5641237 | 09:31:38.5655282 | GOLD; bias NEUTRAL; tecnica 5m unavailable; nessuna notizia direzionale | NO_DIRECTION / NON_TRADE |
| 733 | 09:31:38.5655719 | 09:31:38.5664615 | GOLD; NO_DIRECTION; NOT_EXECUTED; score 100; quotazione fresca assente; nessun livello | NON_TRADE |

I round-trip API riportati dal log sono rispettivamente 366 ms, 325 ms e 304 ms. L'ACK prova l'accettazione da parte dell'API, non la consegna al dispositivo. I timestamp delle righe di log non consentono di ricostruire con precisione il momento della richiesta HTTP.

**Difetto di etichettatura #733:** il titolo dichiara “ANALISI CFD”, ma il corpo indica `FUTURES_CONTINUOUS_FRONT_MONTH`. Ticker provider, provider, timestamp/prezzo della quotazione e scadenza esatta non sono esposti; NARWHAL è NOT_CONFIGURED. Non è quindi possibile classificarlo come CFD né identificare un contratto future preciso. Score 100 non significa validità operativa.

I messaggi #732 e #733 sono due rappresentazioni della stessa analisi GOLD, non due setup indipendenti. Nessuno dei tre messaggi ha entry, SL, TP o ATR. Nessun outcome può essere valutato su candele successive.

Il log mostra inoltre che il forwarding cloud verso GAGARIN è disabilitato perché `GAGARIN_CLOUD_API_URL/API_KEY` non sono configurati nel job. Nessun handoff operativo è dimostrato.

## 3. GAGARIN — ultima run di produzione

Run: [Actions #42467422750](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42467422750)  
Workflow: `Gagarin Paper Monitor (GitHub Actions)`, run #168; branch `main`, SHA `69bb6d07`.  
Job: `Run Gagarin directly on GitHub`, ID `128690080067`; esito SUCCESS. Nessun artifact.

### Quotazioni e classificazione

Il job riporta dieci strumenti: Soia, Brent, Argento, WTI, Grano, EUR/USD, Mais, Oro, Rame e GBP/USD. Tutti sono `MARKET_CLOSED`; le età delle quotazioni sono fra **127.811,4 e 137.416,2 secondi** (circa **35h30m–38h10m**).

- Provider riportati: YAHOO per le commodity; BIQUOTE per EUR/USD e GBP/USD.
- Il log non espone ticker provider risolto, timestamp assoluto della quotazione, prezzo di riferimento, market type né scadenza contrattuale.
- Tutti i candidati sono bloccati da `LIVE_DATA_NOT_FRESH` e/o setup/trigger/livelli mancanti. I valori della classifica sono PAPER_WATCH, non autorizzazioni operative.
- Recorded entries: 0; updated open outcomes: 0; new feedback signals: 0; new additional live forecasts: 0.
- Riepilogo: `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`.
- Telegram message **#3719**: API ACK alle **09:30:14.1243054 UTC**, round-trip 527 ms. Il log non conserva il corpo del messaggio; strumento, direzione e livelli sono NON ATTRIBUTABLE. Non è un trade.

Il workflow effettivamente esegue con `MIN_ENTRY_PROBABILITY=40`, `MIN_ENTRY_QUALITY=30`, `MIN_ENTRY_CONFIDENCE=35`, `MIN_ENTRY_RR=2.5`. Questi sono i valori stampati dal job; PRAVDA non li ha modificati.

### Journal e file di stato

- `journal.csv`: righe del 17 ottobre con esito “nessun segnale”; nessun trade recente registrato.
- `paper_trade_log.csv`: un solo record legacy WTI LONG del 8 ottobre, marcato `LEGACY_IMPORT`; provider, ticker provider, timestamp quotazione, market type e scadenza non sono valorizzati. La nota stessa dichiara assenza di esito. Non è prova di fill.
- `position.json`: Heating Oil LONG con `opened_at=2026-09-15T13:23:44Z`, entry 4.8844, SL 4.5418 e TP1 5.4473. È un artefatto vecchio e non riconciliato; la run corrente dichiara 0 posizioni aperte. Non lo conto come posizione attiva né come trade verificato.
- `commodities_monitor_state.json`: timestamp 17 settembre 2026.
- `commodities_daily_report_state.json`: ultimo report 10 settembre 2026, 0 valutazioni, 24 pending.

Il log della run mostra `DATABASE_URL` vuota in tutte le fasi. Non è dimostrato l'uso di uno store PostgreSQL condiviso per journal/feedback. I record legacy non hanno la provenienza necessaria per un confronto contrattuale e temporale.

### Universo osservato

Il monitor di main continua a includere Argento e EUR/USD/GBP/USD; non mostra Platino o Palladio. Il paniere non coincide con quello commodity richiesto in precedenza. Le modifiche di universo presenti in PR aperte non sono attive su main.

## 4. Frequenza reale delle GitHub Actions

| Workflow | Cron su main | Ultime due run osservate | Gap fra run | Situazione al cut-off |
|---|---|---|---:|---|
| SPUTNIK collector | `2-59/5 * * * *` | #287 02:41:59; #288 09:31:31 UTC | 6h49m32s | 1h53m22s dall'avvio #288 senza nuova run |
| SPUTNIK Telegram polling | `*/5 * * * *` | #48 02:20:16; #49 09:16:25 UTC | 6h56m09s | 2h08m28s senza nuova run |
| GAGARIN monitor | `*/15 * * * *` | #167 02:30:08; #168 09:29:58 UTC | 6h59m50s | 1h54m55s dall'avvio #168 senza nuova run |

Le run sono SUCCESS, ma la cadenza osservata non corrisponde ai cron dichiarati. Non è dimostrata la causa dei gap. I test PR eseguiti successivamente non sono run di produzione e non colmano questi intervalli.

## 5. PR e CI esistenti — nessuna integrazione su main

### SPUTNIK

- [PR #131 — aggiornamento endpoint White House RSS](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): OPEN, non merged. Cambia `/feed/` in `/news/feed/`. Sul suo head `793ae3b5` risultano SUCCESS sia SPUTNIK ranking tests #639 sia item intelligence tests #252. La run di produzione #288 ha ancora usato il vecchio endpoint e ha registrato HTTPError: il fix non è su main. Il confronto aggiornato con main (`75985955`, dopo il commit documentale PRAVDA) mostra il branch divergente: **1 commit ahead / 2 behind**; i test verdi non dimostrano quindi l'integrazione o la verifica sul main corrente.

### GAGARIN

- [PR #192 — identità contratto e ambiguità SL/TP](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, non merged. I sei workflow sul suo head `295dba4b` sono SUCCESS, ma il branch è divergente da main: **6 commit ahead / 4 behind**. Il diff aggiunge provider/ticker/mercato/scadenza al fingerprint, richiede ticker/mercato e identità futures coerenti per valutare le candele successive e classifica una candela che tocca SL e TP come `ESITO NON VERIFICABILE`, senza R realizzato. **Rilievo ancora aperto sul branch:** `quote_provider` è incluso nel record/fingerprint, ma `_market_contract_match` non confronta il provider del segnale con quello delle candele successive; una transizione di provider con ticker/mercato/contratto uguali potrebbe quindi passare il controllo. Il rilievo è già stato segnalato nel commento PRAVDA del 7 novembre (commento GitHub ID `6706619879`). La correzione non è attiva su main.
- [PR #200 — daily summary sullo store condiviso](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/200) e [PR #202 — journal/feedback durevole](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): entrambe OPEN. Il log corrente mostra `DATABASE_URL` vuota, quindi la persistenza condivisa non è verificata.
- [PR #225 — offset del cron monitor](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225): OPEN; main mantiene `*/15`.
- [PR #223 — scansione M5 isolata a sette strumenti](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): OPEN; non modifica il comportamento di main.
- [PR #237 — associazione catalogo CFD al simbolo esatto](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/237): OPEN draft, due workflow CI SUCCESS sul branch. È solo una correzione di validazione del catalogo; non dimostra l'esistenza di un feed o di quotazioni Trading 212 e non è in produzione.

## 6. Valutazione degli esiti e statistiche

Ledger verificato: [pravda-signal-ledger-2026-11-08.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-08.csv), 85 record / 85 firme uniche / 85 source ID unici.

| Metrica | Risultato |
|---|---:|
| SPUTNIK | 36 record |
| GAGARIN | 49 record |
| NON_TRADE | 56 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |
| Campione utile per win rate/R | 0 |

Non è possibile stabilire SL prima o TP prima per i record senza fill, senza livelli, senza timestamp della quotazione o senza identità esatta del mercato/contratto. Non viene costruito alcun backtest e non viene assegnato alcun risultato sulla base di ticker continui, spot/futures o scadenze non coincidenti.

## 7. Lacune e prossimo controllo

1. Verificare nuove run di produzione, non soltanto test su branch.
2. Per ogni eventuale setup richiedere nel log e nel journal: ID/firma, generazione, invio/API ACK, ticker provider esatto, mercato, scadenza, provider, timestamp e prezzo della quotazione, direzione, entry, SL, TP e ATR.
3. Riconciliare `position.json`, `paper_trade_log.csv` e feedback con lo stato corrente; mantenere gli artefatti legacy fuori dalle statistiche operative.
4. Verificare la persistenza condivisa solo quando il job mostra una connessione database effettivamente configurata e il journal viene letto/scritto con successo.
5. Rivalutare gli outcome esclusivamente su candele successive dello stesso identico ticker, mercato e contratto, in ordine cronologico. In caso di doppio tocco SL/TP nella stessa candela: `ESITO NON VERIFICABILE`.

**Sicurezza:** nessuna modifica a codice, strategia, filtri, punteggi o rischio; nessun merge/deploy; nessun ordine reale; nessuna modifica a secret o Render; nessun servizio a pagamento; nessun accesso Trading 212 dichiarato. Nessuna consegna Telegram al dispositivo dichiarata. PAPER ONLY.
