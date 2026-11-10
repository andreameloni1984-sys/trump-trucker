# PRAVDA — Audit indipendente #25
## SPUTNIK / GAGARIN
**10 novembre 2026 — 03:05 UTC (04:05 CET)**

## Sintesi esecutiva

Verificati i run Actions più recenti, i log integrali dei job produttivi, i commit di `main`, i journal/feedback, il codice dell'outcome engine e le Pull Request correttive.

**Non risultano nuove scansioni programmate dopo SPUTNIK #296 e GAGARIN #174.** I segnali #756 (SPUTNIK) e #3756 (GAGARIN) erano già nel ledger precedente. Non sono emersi nuovi record univoci: il CSV non è stato modificato.

Novità principali:
- SPUTNIK PR #143 ha ora due workflow CI verdi sul nuovo head: 46 test item-intelligence e 186 test ranking. La correzione dei falsi match dei token brevi `ai` e `media` non è su main.
- SPUTNIK PR #153 conserva 67 test Telegram menu e 186 ranking test verdi; il difetto di propagazione della direzione tecnica resta riprodotto nell'ultimo run produttivo #296.
- GAGARIN PR #248 resta 20 commit avanti / 0 indietro rispetto a main, con 7/7 workflow verdi e 571 test superati; main continua ad analizzare 13 strumenti.
- GAGARIN PR #250 resta 3 commit avanti / 0 indietro, con 6/6 workflow verdi; la rimozione dei confronti manuali CFD Trading 212/futures non è integrata.
- Persistenza GAGARIN non dimostrata; polling Telegram #21 ancora fallito con HTTP 409.
- Nessun segnale dispone di ticker/contratto/scadenza/provider completi e OHLC successivi omogenei per certificare SL o TP.

---

## 1. Registro storico — controllo anti-duplicati

Ledger recuperato dal branch documentale precedente e analizzato con parser CSV che rispetta i campi quotati.

| Indicatore | Risultato |
|---|---:|
| Record | 108 |
| SPUTNIK | 51 |
| GAGARIN | 57 |
| Firme uniche | 108 |
| Source ID unici | 108 |
| Duplicati firma | 0 |
| Duplicati source ID | 0 |
| NON_TRADE | 79 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |

Blob SHA del CSV: `7ee27891e651aa4b581d2a0b70f6f1ce219a936a`.

I due record più recenti restano:
- SPUTNIK #756: `run:42726305978/telegram_message:756`;
- GAGARIN #3756: `run:42729446093/telegram_watch_pre_alert:3756`.

Entrambi erano già registrati nell'audit #24. Nessuna nuova riga aggiunta.

Win rate, Average R e Total R: **N/D**. Nessun campione di trade con fill verificato.

[Ledger cumulativo](reports/pravda-signal-ledger-2026-11-09.csv)

---

## 2. GitHub Actions — ultimo schedule e ritardi

Snapshot Actions consultato alle 03:05:24 UTC del 10 novembre. Le ultime 100 esecuzioni di ciascun repository non mostrano un schedule successivo ai run elencati.

| Repository/processo | Run | Avvio UTC | Fine UTC | Stato | Età dalla fine alle 03:05 UTC |
|---|---:|---|---|---|---:|
| SPUTNIK collector | [#296](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42726305978) | 00:10:54 | 00:11:07 | SUCCESS | 2h54m17s |
| SPUTNIK polling | [#55](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42723841180) | 23:51:48 (9/11) | 23:51:58 | SUCCESS | 3h13m26s |
| GAGARIN monitor | [#174](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729446093) | 00:35:20 | 00:35:42 | SUCCESS | 2h29m42s |
| GAGARIN polling | [#21](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729120141) | 00:32:48 | 00:33:07 | FAILURE | 2h32m17s |

SPUTNIK polling #55 ha concluso con `Pending updates: 0`: non dimostra che siano stati elaborati messaggi pendenti. GAGARIN polling #21 è fallito; dettagli nella sezione 8.

Main invariati:
- SPUTNIK: `5f3ae3b8bc31275851cbf1f8c8ce964e6feb0ec6`;
- GAGARIN: `631727912b3a2022379a4460f4b6f756eba6991f`.

Le Actions CI su branch PR non sono scansioni di mercato e non dimostrano deployment.

---

## 3. SPUTNIK — run produttivo #296 e segnali

[Log Actions #296](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42726305978)

Il log del job conferma:
- SEC HTTP 403; cooldown 21.600 secondi;
- filing: 0;
- estrazione transazioni: 0;
- White House RSS: HTTPError;
- scansione intelligence pubblica: 1.670 ms, 3 findings;
- GAGARIN handoff disabilitato: `GAGARIN_CLOUD_API_URL/API_KEY not configured`;
- forwarding: 0 ms;
- durata complessiva: circa 4.313 ms.

Non risulta un trasferimento produttivo dei catalizzatori a GAGARIN.

### Item pubblico e latenza

Il post [Trumpstruth #43537](https://www.trumpstruth.org/statuses/43537) risulta pubblicato il 9 novembre alle 21:29:28 UTC e rilevato intorno alle 00:11:01.522 UTC del 10 novembre. Latenza pubblicazione-rilevamento: circa **2h41m33s**.

La scansione lo classifica come contesto DEFENSE/AI_TECH, ma l'analisi dichiara `NO_DIRECTIONAL_NEWS`. Non è prova di un catalizzatore commodity direzionale.

### GOLD SHORT #756 — un solo record, non un trade

I messaggi #754–#757 sono distinti per funzione:
- #754: riepilogo notizia;
- #755: analisi preliminare GOLD SHORT;
- #756: card CFD dettagliata;
- #757: brief informativo/analogie storiche.

Il candidato va contato una sola volta, sotto la card #756; #755 è il messaggio compagno e #757 non è una nuova operazione.

| Campo | Valore |
|---|---|
| Source ID | `run:42726305978/telegram_message:756` |
| Generazione registrata | 2026-11-10 00:11:04.0127804 UTC |
| ACK registrato | 2026-11-10 00:11:04.0141166 UTC |
| Message ID | 756 |
| Strumento logico | GOLD |
| Ticker esatto | NOT_RESOLVED |
| Mercato | titolo CFD; corpo riferito a future continuo front-month |
| Scadenza | UNKNOWN |
| Provider | NOT_EXPOSED; NARWHAL NOT_CONFIGURED |
| Timestamp quotazione | NOT_EXPOSED |
| Direzione | SHORT |
| Entry | 4145.2002 |
| SL | 4146.7429 |
| TP1 | 4143.6575 |
| TP2 | 4142.1147 |
| ATR | 1.0285 |
| Score | 100/100 |
| Stato | NOT_EXECUTED |

Il compagno #755 riporta direzione tecnica SHORT 5m, momentum -0,053% su 15 minuti e `NO_DIRECTIONAL_NEWS`. La card #756 stampa invece `TECNICA: N/D (NOT_ASSESSED)` e `D-L-A: NEUTRAL / NO_DIRECTION (INSUFFICIENT_DATA)`, pur riportando nel motivo testuale una descrizione tecnica SHORT.

La card avverte che il contratto continuo non ha scadenza esatta verificata, che l'indipendenza upstream/SPOT-FUTURES non è verificata e che i livelli non vanno utilizzati. Score 100 non equivale a validità operativa.

**Esito: NON_TRADE.** Nessun fill e nessun outcome SL/TP. Ticker, contratto, scadenza, provider, timestamp/prezzo della quotazione e OHLC successivi omogenei non sono disponibili.

### Integrità temporale degli ACK

Per #756, i timestamp registrati come generazione e invio differiscono di circa **1,34 ms**, mentre la stessa riga di log dichiara API round-trip **467 ms**. I timestamp di emissione del log non sono quindi conciliabili, così come sono etichettati, con una misura affidabile del tempo generazione→invio. Il round-trip va mantenuto come misura separata; non usare la differenza di 1,34 ms per certificare la latenza end-to-end.

Gli ACK dei messaggi #754–#757 sono rispettivamente 415, 374, 467 e 379 ms. Sono conferme API con message ID, non prove di visualizzazione sul dispositivo.

Il messaggio #757 si intitola “BRIEF ORE 05:00” ma viene emesso intorno alle 00:11:04 UTC (01:11 CET). È un disallineamento tra etichetta oraria e timestamp di emissione da chiarire; il contenuto è informativo, riporta zero operazioni Form 4 e analogie storiche, non è un segnale.

### Classificazione testuale — PR #143

Su main `trump_tracker.py` usa ancora `keyword in normalized` per i domini. La ricerca per sottostringa consente falsi match: `ai` dentro “AGAIN” e `media` dentro “immediately”.

[PR SPUTNIK #143](https://github.com/andreameloni1984-sys/trump-trucker/pull/143) sostituisce per i due token brevi il controllo con confini di parola. Head `0d55fb4c8663c0d904035e0896a49c2af71449f0`, 2 commit ahead / 0 behind rispetto a main; PR OPEN, non merged.

CI sul nuovo head:
- item-intelligence: [run #42738260514](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42738260514), **46 test PASS**;
- ranking: [run #42738260306](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42738260306), **186 test PASS**.

La correzione non è su main; il comportamento produttivo aggiornato non è ancora verificato.

### Altre PR SPUTNIK

| PR | Confronto con main corrente | Stato / verifica |
|---|---|---|
| [#153](https://github.com/andreameloni1984-sys/trump-trucker/pull/153) | 2 ahead / 0 behind | OPEN, non-DRAFT; 67 Telegram menu + 186 ranking test SUCCESS. La correzione propaga direzione/timeframe/motivazione/allineamento nella card CFD; non integrata. |
| [#150](https://github.com/andreameloni1984-sys/trump-trucker/pull/150) | 1 ahead / 1 behind | OPEN; base ferma a `6c3095f`, main è `5f3ae3b`; branch divergente, va riallineato. |
| [#156](https://github.com/andreameloni1984-sys/trump-trucker/pull/156) | 1 ahead / 1 behind | OPEN; stessa base superata `6c3095f`; branch divergente. |

---

## 4. GAGARIN — run produttivo #174

[Log Actions #174](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729446093)

- avvio: 2026-11-10 00:35:20 UTC;
- completamento: 00:35:42 UTC;
- commit: `631727912b3a2022379a4460f4b6f756eba6991f`;
- modalità: PAPER ONLY.

### Universo effettivo

Il run analizza **13 strumenti**, non il paniere richiesto di otto commodity.

| Commodity | Provider | Età quotazione | Stato |
|---|---|---:|---|
| Oro | YAHOO | 612,4 s | STALE |
| Argento | YAHOO | 628,1 s | STALE |
| Rame | YAHOO | 663,3 s | STALE |
| WTI | YAHOO | 602,5 s | STALE |
| Brent | YAHOO | 771,6 s | STALE |
| Grano | YAHOO | 18.938,7 s | STALE |
| Mais | YAHOO | 18.939,7 s | STALE |
| Soia | YAHOO | 18.940,8 s | STALE |

**8/8 commodity STALE.** Le sole righe LIVE del run erano Tesla, EUR/USD e NVIDIA, fuori dal paniere commodity. DAX e S&P 500 risultavano STALE.

Il file main `commodities/universe.py` contiene 13 righe abilitate, benché l'intestazione parli di universo “10 core”. Il log produttivo e `telegram/render_runner.py` confermano 13 strumenti approvati.

### Risultato e WATCH #3756

Il run dichiara:
- Recorded entries: 0;
- Updated open outcomes: 0;
- New feedback signals: 0;
- New additional live forecasts: 1;
- `signals=1 open=1 closed=0`;
- win_rate=N/D, avg_R=N/D, total_R=0.0.

Telegram ha accettato il messaggio #3756 con round-trip 594 ms, ma il corpo non è conservato. Non sono attribuibili strumento, ticker, mercato, scadenza, provider, timestamp quotazione, direzione o livelli.

Source ID già registrato: `run:42729446093/telegram_watch_pre_alert:3756`.

**Classificazione: WATCH_PRE_ALERT non attribuibile / NOT_AUTHORIZED / NON_TRADE.** Il contatore `open=1` è un forecast aperto nel runtime, non prova di una posizione eseguita.

### Configurazione runtime

Il run espone:
- MIN_ENTRY_PROBABILITY=40;
- MIN_ENTRY_QUALITY=30;
- MIN_ENTRY_CONFIDENCE=35;
- MIN_ENTRY_RR=2.5;
- DATABASE_URL vuota;
- PAPER_TRADING_ONLY=1.

I valori 40/30/35 differiscono dal profilo Aggressive 55/45/50 discusso in precedenza. È una discrepanza osservata, non una modifica richiesta da PRAVDA. Nessuna soglia è stata cambiata.

### Cadenza

- `telegram/render_runner.py` su main imposta `interval = 5 * 60` e stampa “13 approved instruments”.
- `.github/workflows/gagarin-monitor.yml` mantiene cron `*/15 * * * *` e `MONITOR_INTERVAL_MINUTES=15`.

Il codice Render configura 5 minuti, ma non è prova di deployment o attività del servizio. GitHub Actions è configurata a 15 minuti. PRAVDA non ha consultato o modificato Render.

---

## 5. GAGARIN — universo, PR e CI

### PR #248 — otto commodity

[PR GAGARIN #248](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/248)

Head `d370ad676709f0be911db55f8314043e7dfce9fa`; confronto con main: **20 ahead / 0 behind**, merge-base uguale a main. PR OPEN/DRAFT, non integrata.

Il branch contiene allowlist fail-closed per:
1. XAU/USD;
2. XAG/USD;
3. COPPER/USD;
4. WTI/USD;
5. BRENT/USD;
6. WHEAT/USD;
7. CORN/USD;
8. SOYBEAN/USD.

CI sul head:
- 7/7 workflow SUCCESS;
- suite principale: **571 passed in 2.65s**.

È una correzione testata nel branch, non una prova che main o Render la stiano eseguendo. Main resta a 13 strumenti; l'ultima scansione produttiva #174 lo conferma.

### PR #250 — confronto manuale Trading 212

[PR GAGARIN #250](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/250)

Head `16173e600f9f71d5fe2000c3adc06cfdec959791`; 3 ahead / 0 behind. OPEN/DRAFT, non integrata. Sei workflow CI SUCCESS.

La patch rimuove dal bot attivo il confronto manuale fra prezzi CFD Trading 212 e serie futures. Non dimostra accesso al broker né uso di quotazioni Trading 212.

### Altre PR GAGARIN

| PR | Confronto con main | Stato |
|---|---|---|
| [#175](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175) polling/webhook | 1 ahead / 7 behind | OPEN, divergente |
| [#192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) outcome engine | 6 ahead / 10 behind | OPEN, divergente |
| [#202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202) journal durevole | 18 ahead / 8 behind | OPEN/DRAFT, divergente |

I vecchi check verdi associati a head non riallineati non certificano il comportamento del main corrente.

---

## 6. GAGARIN — journal e feedback

### Prediction log

`commodities_prediction_log.json` su main:
- 981 record;
- PENDING 945;
- NEUTRALE 36;
- ultimo `created_at`: 2026-09-15 15:45:04 UTC.

Azioni registrate:
- NON ENTRARE: 77;
- ATTENDERE: 576;
- SHORT — ASPETTARE CONFERMA: 15;
- LONG — ASPETTARE CONFERMA: 292;
- COMPRA ORA: 21.

Le 21 righe COMPRA ORA sono PENDING, non fill.

### Altri artefatti

- `paper_trade_log.csv`: un WTI LEGACY_IMPORT del 2026-10-08, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55; signal ID vuoto, nessuna prova di fill/esito.
- `position.json`: snapshot Heating Oil LONG del 2026-09-15, entry 4.8844, SL 4.5418, TP1 5.4473, TP2 5.6284, TP3 5.882; nessun signal ID o prova di esecuzione. Strumento fuori dal paniere attuale.
- `gagarin_feedback.csv`: HTTP 404 su main.
- `paper_open.json`: HTTP 404 su main.
- Run #174: `DATABASE_URL` vuota.
- Run #174 artifacts: nessuno.

La persistenza durevole e la continuità del journal tra run non sono dimostrate.

---

## 7. Outcome engine — main non conforme

Blob main `engine/feedback.py`: `41bec9bfab031c8dbf71121cd69d0e9b4c4f663f`.

Il campo FIELDS non conserva separatamente:
- quote provider;
- ticker effettivamente quotato;
- tipo di mercato;
- mese contrattuale;
- scadenza.

Il matching degli stati successivi avviene per symbol/timeframe, con fallback al symbol se esiste un solo stato. La docstring dichiara esplicitamente che SL e TP nella stessa candela vengono risolti come STOP; il codice controlla `stop_hit` prima di `hit_targets`.

Questo non soddisfa il protocollo PRAVDA. La stessa candela che tocca SL e TP senza sequenza intrabar ricostruibile deve risultare **ESITO NON VERIFICABILE**, non STOP.

PR #192 propone la correzione del doppio tocco e l'identità mercato/contratto, ma il branch è 6 ahead / 10 behind e il guard `_market_contract_match()` non confronta esplicitamente il provider del segnale con il provider della serie OHLC successiva. Non certificare outcome finché il matching esatto non è completo.

Regole applicate:
- SL prima dei target, su barre successive omogenee: STOP;
- target prima dello SL, su barre successive omogenee: TP;
- doppio tocco nella stessa candela senza sequenza intrabar: ESITO NON VERIFICABILE;
- provider/ticker/mercato/contratto/scadenza mancanti o diversi: ESITO NON VERIFICABILE;
- NOT_EXECUTED, WATCH, PENDING e score non sono trade.

---

## 8. Telegram GAGARIN — errore 409

[Polling run #21](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729120141)

Il job ha:
- validato il token: SUCCESS;
- eseguito la diagnostica bot: SUCCESS;
- fallito su `getUpdates` con API error 409: webhook attivo, polling non consentito;
- terminato con exit code 1.

Nessun update processato. La PR #175 contiene la gestione proposta, ma è divergente e non integrata. Nessun webhook o secret è stato modificato.

---

## 9. Fonti consultate

### SPUTNIK
- [Collector #296](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42726305978)
- [Polling #55](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42723841180)
- [PR #143](https://github.com/andreameloni1984-sys/trump-trucker/pull/143)
- [PR #153](https://github.com/andreameloni1984-sys/trump-trucker/pull/153)
- [PR #150](https://github.com/andreameloni1984-sys/trump-trucker/pull/150)
- [PR #156](https://github.com/andreameloni1984-sys/trump-trucker/pull/156)
- [Post pubblico #43537](https://www.trumpstruth.org/statuses/43537)

### GAGARIN
- [Monitor #174](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729446093)
- [Polling #21](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729120141)
- [PR #248](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/248)
- [PR #250](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/250)
- [PR #175](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175)
- [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192)
- [PR #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202)

### File main esaminati
- SPUTNIK `trump_tracker.py`;
- GAGARIN `commodities/universe.py`, `telegram/render_runner.py`, `.github/workflows/gagarin-monitor.yml`, `engine/feedback.py`, `commodities_prediction_log.json`, `paper_trade_log.csv`, `position.json`.

---

## 10. Prossimo controllo

1. Verificare il prossimo schedule SPUTNIK; separare latenza pubblicazione-rilevamento, generazione e ACK Telegram.
2. Verificare l'eventuale integrazione delle PR #143 e #153 e il comportamento della card CFD su main.
3. Verificare il prossimo schedule GAGARIN; accertare se il paniere è ancora a 13 o è stato portato a otto.
4. Verificare freschezza e timestamp di tutte le otto commodity.
5. Distinguere la configurazione Render 5m dal workflow GitHub 15m; nessuna assunzione sul deployment.
6. Verificare la persistenza del journal tra due run e recuperare il corpo del WATCH #3756, se conservato.
7. Riallineare PR #175, #192 e #202; verificare provider, ticker, mercato e scadenza nel matching OHLC.
8. Rivalutare outcome soltanto quando esistono fill paper registrati e prezzi successivi dello stesso identico strumento/contratto.

---

## 11. Verdetto PRAVDA — 03:05 UTC

| Area | SPUTNIK | GAGARIN |
|---|---|---|
| Ultimo schedule | #296 | #174 |
| Nuovo segnale dal precedente audit | Nessuno | Nessuno |
| Ultimo candidato già a ledger | GOLD SHORT #756 | WATCH #3756 non attribuibile |
| Stato | NOT_EXECUTED | WATCH / NOT_AUTHORIZED |
| Quote e contratto | incompleti | 8/8 commodity stale |
| Nuovo schedule successivo | non trovato | non trovato |
| Correzione più avanzata | PR #143/#153 | PR #248/#250 |
| Outcome certificabile | No | No |

Statistiche cumulative: **108 record, 0 duplicati, 0 fill verificati, 0 SL, 0 TP**. Win rate, Average R e Total R: **N/D**.

Nessuna modifica a codice applicativo, strategia, filtri, punteggi, soglie o rischio. Nessun merge, deploy, ordine reale, intervento su secret o Render. Nessun servizio a pagamento. Nessun accesso a Trading 212 dichiarato.

**PRAVDA — PAPER ONLY.**
