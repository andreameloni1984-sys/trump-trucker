# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**9 novembre 2026 — 06:42 UTC (07:42 CET)**

## Esito sintetico

Nuovo controllo eseguito direttamente sulle GitHub Actions, sui log completi, sulle PR e sugli artefatti presenti su `main`.

- SPUTNIK: nuova run produttiva **#293**, tre messaggi Telegram API-ACK (#746–#748); un digest informativo, un bias preliminare GOLD LONG e una card CFD `NOT_EXECUTED`.
- GAGARIN: nuova run produttiva **#172**, una candidata Soia SHORT bloccata e un WATCH pre-alert #3728 non attribuibile.
- Nessun nuovo trade eseguito.
- Nessuna candela successiva identificabile per un contratto esatto; nessun esito SL/TP verificabile.
- Cinque nuovi record aggiunti al ledger cumulativo, senza duplicati.

## 1. Ledger cumulativo

| Indicatore | Prima | Dopo |
|---|---:|---:|
| Record | 98 | 103 |
| SPUTNIK | 45 | 48 |
| GAGARIN | 53 | 55 |
| Firme uniche | 98 | 103 |
| Source ID unici | 98 | 103 |
| Duplicati | 0 | 0 |
| NON_TRADE | 69 | 74 |
| ESITO_NON_VERIFICABILE | 29 | 29 |
| Fill verificati | 0 | 0 |
| SL verificati | 0 | 0 |
| TP verificati | 0 | 0 |

Le cinque aggiunte sono:
- SPUTNIK #746 — digest informativo, non segnale.
- SPUTNIK #747 — GOLD LONG EARLY_BIAS, non confermato.
- SPUTNIK #748 — GOLD EARLY_SETUP, `NOT_EXECUTED`.
- GAGARIN — candidata Soia SHORT `PAPER_WATCH`, bloccata.
- GAGARIN #3728 — WATCH pre-alert senza corpo conservato.

**Statistiche operative:** campione di fill verificabili = 0. Win rate, average R e total R = N/D. Nessun backtest o rendimento dedotto.

## 2. SPUTNIK — run #293

[GitHub Actions #293](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770) — avvio 06:01:41 UTC, completamento 06:01:51 UTC, SUCCESS. Il job ha eseguito i test di regressione di consegna/intelligence (30 test, OK) prima del collector.

### Fonti e raccolta
- SEC: HTTP 403, cooldown 21.600 secondi; 0 filing, 0 transazioni.
- White House RSS: il runtime continua a interrogare `https://www.whitehouse.gov/feed/`, che restituisce HTTPError.
- Il collector riporta 3 nuove correlazioni pubbliche; il digest espone 2 eventi RSS individuali verificabili.
- Gli OSError WHITE_HOUSE/TRUTH_ARCHIVE/OGE stampati prima del collector appartengono ai test automatici, non alla raccolta produttiva.

### Messaggi
**#746 — digest informativo.** Due elementi mostrati:
- Quote post, pubblicato 2026-11-08 23:41:05 UTC: https://www.trumpstruth.org/statuses/43530 (MEDIA).
- Post su S.5653 / energia, pubblicato 2026-11-09 00:05:49 UTC: https://www.trumpstruth.org/statuses/43532 (ENERGY, AI_TECH).

Il digest non è un segnale e non stabilisce una direzione.

**#747 — GOLD LONG preliminare.**
- Direzione tecnica: LONG (5m).
- Momentum 5m negli ultimi 15 minuti: +0,077%.
- Allineamento notizie: `NO_DIRECTIONAL_NEWS`.
- Stato: `EARLY_BIAS`; nessuna entry, SL, TP o ATR.

**#748 — card CFD GOLD LONG, NOT_EXECUTED.**

| Campo | Valore |
|---|---:|
| Entry | 4133.2002 |
| SL | 4130.5859 |
| TP1 | 4135.8145 |
| TP2 | 4138.4289 |
| ATR | 1.7429 |
| Score visualizzato | 100/100 |

Limiti decisivi:
- Titolo CFD, corpo `FUTURES_CONTINUOUS_FRONT_MONTH`; scadenza esatta non verificata.
- Ticker esatto, provider e timestamp/età della quotazione non esposti.
- NARWHAL `NOT_CONFIGURED`, quindi nessun prezzo di riferimento utilizzabile.
- Indipendenza del controllo SPOT/FUTURES dichiarata non verificata.
- La card mostra `TECNICA: N/D` e D-L-A `NEUTRAL / NO_DIRECTION`, mentre il messaggio #747 dello stesso gruppo riporta LONG 5m.
- Il testo dice espressamente di non usare i livelli per entry/SL/TP.

Questi livelli sono conservati per audit, ma non sono un trade e non è possibile verificare se siano stati già superati: manca la serie del contratto esatto. Score e rischio massimo visualizzato non sono prova di validità o esposizione.

### Telegram e stato
Le API hanno confermato gli ID #746, #747 e #748 (round-trip 563, 313 e 322 ms). Il polling #53 ha trovato 0 update pendenti. Non è prova di visualizzazione sul dispositivo.

La run ha persistito `sputnik_state.json` su `main`, creando il commit `8bdf7ab16ec3bfd23d5f3160a4e87dffbfd35396`. La persistenza fuori da main proposta nella PR #144 non è integrata.

### PR SPUTNIK
- [PR #153 — preservare direzione tecnica 5m nella card CFD](https://github.com/andreameloni1984-sys/trump-trucker/pull/153): OPEN, 2 commit avanti / 0 indietro; ranking e Telegram menu CI SUCCESS. Il difetto è riprodotto in produzione da #747/#748. Commento PRAVDA aggiunto: [#6734079335](https://github.com/andreameloni1984-sys/trump-trucker/pull/153#issuecomment-6734079335).
- [PR #150 — evitare raccomandazioni ripetute senza nuovo RSS](https://github.com/andreameloni1984-sys/trump-trucker/pull/150): OPEN, 1 avanti / 1 indietro; non integrata.
- [PR #131 — endpoint White House RSS](https://github.com/andreameloni1984-sys/trump-trucker/pull/131): OPEN, 3 avanti / 1 indietro; non integrata. La run #293 conferma che main usa ancora il vecchio `/feed/` e riceve HTTPError.

## 3. GAGARIN — run #172

[GitHub Actions #172](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716) — avvio 06:34:18 UTC, completamento 06:34:37 UTC, SUCCESS. Nessun artifact prodotto.

### Quotazioni e candidati
Universo runtime: 10 strumenti, 8 commodity operative e 2 FX ausiliari.
- Commodity YAHOO: Soia 659,4s; Brent 603,0s; WTI 602,9s; Argento 609,5s; Grano 648,2s; Rame 613,7s; Oro 622,4s; Mais 686,3s. Tutte classificate STALE.
- EUR/USD e GBP/USD BIQUOTE: LIVE, età circa 273s, ma contesto FX non operativo.

Candidata principale:
- Soia / simbolo logico `SOYBEAN/USD`: SHORT, Prob 63,0, Quality 55,5, Confidence 35,0.
- Stato `PAPER_WATCH`; blocchi: `LIVE_DATA_NOT_FRESH`, `TRIGGER_NOT_CONFIRMED`, `TRIGGER_DIRECTION_MISMATCH`, `FINAL_CONFLUENCE_FAIL`.
- Nessuna entry, SL, TP o ATR. Non è un segnale autorizzato.

Telegram #3728 è stato accettato dall'API in 478 ms, ma il corpo non è conservato; strumento e livelli non attribuibili.

### Journal e feedback
- `DATABASE_URL` vuota nell'ambiente della run; `PAPER_TRADING_ONLY=1`.
- `commodities_prediction_log.json`: 981 record; ultimo `created_at` 2026-09-15 15:45:04 UTC. 945 PENDING, 36 NEUTRALE. Azioni: 21 COMPRA ORA (tutte PENDING), 292 LONG attendere conferma, 15 SHORT attendere conferma, 576 ATTENDERE, 77 NON ENTRARE. Sei record non hanno il campo `operational_signal`; nessuno di questi conteggi dimostra un fill.
- `commodities_monitor_state.json`: timestamp 2026-09-17 03:44:02 UTC.
- `journal.csv`: 11 righe del 17 ottobre, tutte “nessun segnale”.
- `paper_trade_log.csv`: vecchio WTI LEGACY_IMPORT dell'8 ottobre, con nota “nessun esito”; mercato/contratto di esecuzione e provider non identificati.
- `position.json`: vecchia posizione Heating Oil aperta il 15 settembre; nessuna prova di fill verificato o outcome.
- `gagarin_feedback.csv`: HTTP 404.

Il job ha registrato 0 nuove entrate, 0 outcome aggiornati, 0 nuovi feedback e 0 nuovi forecast; riepilogo `signals=0 open=0 closed=0`.

### Configurazione osservata
La run espone `MIN_ENTRY_PROBABILITY=40`, `MIN_ENTRY_QUALITY=30`, `MIN_ENTRY_CONFIDENCE=35`, `MIN_ENTRY_RR=2.5`. I valori 40/30/35 differiscono dalle soglie 62/55/60 annotate nelle precedenti specifiche GAGARIN. È una divergenza da verificare con il reparto proprietario; PRAVDA non ha modificato alcun parametro.

### Universo e PR GAGARIN
Il main continua a includere Argento nel monitor e non contiene Platino/Palladio. [PR #241 — disabilitare Argento nell'universo attivo](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/241) è OPEN, 8 commit avanti / 0 indietro. Quattro workflow CI sono SUCCESS; `SOYUZ GAGARIN Tests` è FAILURE: 2 test falliti, 569 passati. I test falliti dimostrano che `_resolve_commodity('argento')` e `_resolve_commodity('silver')` restituiscono ancora l'oggetto Argento con `enabled=False`, invece di non risolverlo. Commento PRAVDA aggiunto: [#6734056996](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/241#issuecomment-6734056996).

La PR #241, anche una volta completata, porta il codice mostrato a 7 commodity attive + 2 FX ausiliari; Platino e Palladio restano assenti rispetto al paniere precedentemente definito. La modifica non è su main.

[PR #240 — sopprimere livelli LUBJANKA stale](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/240): OPEN, 5 avanti / 0 indietro; tutte le 5 GitHub Actions associate sono SUCCESS. Il diff riduce l'età massima della candela M5 a 600s e nasconde entry/SL/TP quando quotazione o barra sono stale. Un controllo esterno Cloudflare ha riportato build failure; non è una GitHub Action e non è stato eseguito alcun deploy.

[PR #192 — matching contratto e outcome ambiguo](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, il commit auditato risulta 6 avanti / 6 indietro rispetto a main. Su main `engine/feedback.py` abbina per symbol/timeframe e classifica STOP prima di TP nella stessa candela. Il branch PR introduce il matching di ticker/mercato/scadenza e l'esito ambiguo per doppio tocco, ma il controllo esplicito di uguaglianza del provider manca ancora; il rilievo PRAVDA precedente è già nei commenti, nessun duplicato aperto.

## 4. Frequenza delle GitHub Actions

Cron verificati nei workflow:
- SPUTNIK collector: `2-59/5 * * * *`.
- SPUTNIK polling: `*/5 * * * *`.
- GAGARIN monitor: `*/15 * * * *`.

Gap effettivi tra run programmate:
- SPUTNIK #292 → #293: 6h 01m 55s. Al cut-off, #293 era terminata da 41m 07s.
- Polling #52 → #53: 5h 58m 53s. Al cut-off, #53 era terminata da 47m 01s.
- GAGARIN #171 → #172: 6h 29m 27s. Al cut-off, #172 era terminata da 8m 30s.

Le ultime run sono SUCCESS, ma la cadenza dichiarata non è stata rispettata nei gap osservati. La causa non è dimostrata.

## 5. Difetti, lacune e prossimo controllo

1. Identificare ticker provider, provider e timestamp della quotazione GOLD; distinguere CFD, future continuo e contratto con scadenza.
2. Verificare il recepimento della PR #153 e la coerenza tra brief tecnico e card CFD.
3. Verificare endpoint White House e anti-ripetizione dopo riallineamento delle PR #131/#150.
4. Risolvere la route alias Argento nei test PR #241 prima di considerare completata l'esclusione.
5. Verificare la persistenza del feedback con scrittura e successiva lettura; ora non è dimostrata.
6. Correggere il matching outcome per provider/ticker/mercato/scadenza e il doppio tocco SL/TP prima di usare statistiche.
7. Monitorare i prossimi run programmati e registrare soltanto nuovi ID/firme.

## 6. Fonti consultate

- SPUTNIK run #293 e job log: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570608770
- SPUTNIK polling #53: https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42570062235
- GAGARIN run #172 e job log: https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42573849716
- PR SPUTNIK #153, #150, #131.
- PR GAGARIN #241, #240, #192.
- Main: `sputnik_cfd.py`, `commodities/universe.py`, `soyuz_gagarin/config.py`, `engine/feedback.py`, monitor state, prediction log, journal CSV, paper trade log, position JSON e workflow YAML.
- Risposta GitHub per `gagarin_feedback.csv`: 404.

## Perimetro

PRAVDA ha aggiunto soltanto documentazione e record al ledger su un branch separato. Nessuna modifica al codice applicativo, strategia, filtri, punteggi o rischio; nessun merge/deploy, ordine reale, intervento su secret o Render, servizio a pagamento o accesso broker dichiarato. Gli ACK Telegram sono soltanto conferme API. **PAPER ONLY.**
