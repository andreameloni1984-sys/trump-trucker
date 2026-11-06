# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-06 16:22 UTC (17:22 Europe/Rome)**

## Sintesi

- Nessun nuovo collector SPUTNIK dopo [#42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412), schedulato, avviato alle 11:31:39 UTC e concluso alle 11:31:53 UTC.
- Nessun nuovo monitor prezzi GAGARIN dopo [#42203497432](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42203497432), schedulato, avviato alle 10:32:52 UTC e concluso alle 10:33:10 UTC.
- Gap al cut-off: SPUTNIK 4h50m; GAGARIN 5h49m. Le cadenze dichiarate nei workflow restano rispettivamente 5m e 15m. Non attribuisco una causa del gap non dimostrata.
- Ledger: 32 record, 32 firme uniche, zero duplicati. Nessun nuovo candidato da aggiungere.
- Nessun fill, TP o SL verificabile. Campione verificabile di outcome: zero; win rate e average R N/D.
- Nessuna modifica ai bot o alla strategia. Nessun merge, deploy, rerun o ordine reale.

## 1. GitHub Actions e continuità dei monitor

### SPUTNIK
- Ultimo collector schedule: [#42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412), branch main, SHA eseguito `fbcb0de2bfe921383eee7edff10c5d9cf3d306d2`.
- Il workflow [trump_tracker.yml](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/trump_tracker.yml) dichiara cron `2-59/5 * * * *`.
- Nelle 100 Actions più recenti non compare un collector successivo. [Daily Summary #42226158074](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42226158074) è un riepilogo, non una scansione di mercato; [Telegram Polling #42206505491](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42206505491) è polling.
- Il collector ha completato con SUCCESS, ma ha trovato 0 filing, 0 nuove operazioni documentate, 0 nuove correlazioni e `findings=0`. SEC ha restituito HTTP 403 con cooldown; il feed White House RSS ha restituito HTTPError. Nessun nuovo catalizzatore direzionale verificato.

### GAGARIN
- Ultimo monitor schedule noto: [#42203497432](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42203497432), branch main, SHA eseguito `7ed290b971e780828934d80aa3b936043769eaf6`.
- Il workflow [gagarin-monitor.yml](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml) dichiara cron `*/15 * * * *`.
- Nessun monitor prezzi successivo compare nelle 100 Actions più recenti. [Daily Summary #42232309653](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42232309653) e [FETCH DRIVERS #42235888213](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42235888213) sono workflow ausiliari, non monitor prezzi.
- [Telegram Polling #42236174265](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42236174265) è fallito con API 409: webhook attivo, polling non consentito. Non è un fallimento del motore prezzi, ma impedisce quel percorso di polling.

## 2. SPUTNIK — candidato GOLD LONG già registrato

Il run #42210907412 contiene un solo candidato collegato, già presente nel ledger come firma `PRAVDA-SPUTNIK-CFD-RUN42210907412-20261106T113148Z-GOLD-LONG-4075.8999-4074.2713-4077.5285-4079.1570`.

| Campo | Valore verificato |
|---|---|
| Run / fonte | [#42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412) |
| Analisi / CFD | messaggi #707 / #708 |
| Generazione analisi | 11:31:48.566388 UTC |
| ACK API analisi | 11:31:48.567503 UTC |
| Generazione CFD | 11:31:48.567717 UTC |
| ACK API CFD | 11:31:48.569094 UTC |
| Strumento | GOLD |
| Ticker | GC=F è il mapping configurato; ticker runtime effettivo non confermato |
| Mercato / scadenza | future continuo front-month; scadenza esatta UNKNOWN |
| Provider / timestamp quota | non esposti nel log |
| Direzione | LONG preliminare |
| Entry / SL | 4075.8999 / 4074.2713 |
| TP1 / TP2 | 4077.5285 / 4079.1570 |
| ATR | 1.0857 |
| Score / stato | 70; EARLY_SETUP / NOT_EXECUTED |

### Coerenza e outcome
- Messaggio #707: tecnica LONG a 5m, momentum +0,064% negli ultimi 15m, nessuna notizia direzionale.
- Messaggio #708: tecnica NOT_ASSESSED, D-L-A NEUTRAL/NO_DIRECTION, swing con massimi/minimi decrescenti ed EMA non univoche.
- I messaggi sono due fasi dello stesso candidato, non due segnali. Score 70 non convalida l'operatività.
- Il messaggio dichiara esplicitamente front-month continuo, scadenza non verificata e livelli non utilizzabili per entry/SL/TP.
- Mancano provider runtime, timestamp/anzianità della quota, ticker risolto e scadenza. Non è possibile associare candele successive allo stesso contratto.

**Esito: ESITO NON VERIFICABILE.** `NOT_EXECUTED`; non è un trade e non entra nelle statistiche.

### Telegram: distinzione test / produzione
- I soli messaggi di mercato #707 e #708 hanno risposta API con message_id e round-trip rispettivamente 549ms e 437ms: prova di accettazione API, non di consegna al dispositivo.
- Il log contiene anche message_id=731 con round-trip 0ms prima dell'avvio del collector. Non è un messaggio di produzione: [test_sputnik_item_intelligence.py](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/tests/test_sputnik_item_intelligence.py) usa `@patch("trump_tracker.urllib.request.urlopen")` e una risposta simulata con message_id 731. Anche le risposte negative a 0ms sono test, non tentativi reali di consegna.
- Il riepilogo SPUTNIK #42226158074 ha un ACK Telegram registrato con message_id=709; è un riepilogo, non un segnale.

## 3. SPUTNIK — stato persistito e ritardo delle fonti

Verifica diretta dell'endpoint GitHub Contents API per `sputnik_state.json` su main:
- `updated_at=2026-11-06T11:31:46.900527Z`;
- `events` vuoto;
- `intelligence_history`: 500 record;
- `telegram_active=true`;
- offset Telegram 275590742.

La persistenza è confermata dal commit [6b91525](https://github.com/andreameloni1984-sys/trump-trucker/commit/6b91525e9ded6611696290e641ff74c4863f05de), creato dal workflow dopo il collector. **Correzione dell'audit precedente:** il precedente `fetch_file` aveva restituito contenuto vuoto per questo JSON; il controllo diretto della Contents API dimostra che il file non è vuoto e che lo stato è stato persistito. La segnalazione precedente di file vuoto era quindi errata.

L'ultimo item RSS con data di pubblicazione esplicita nella cronologia è il post sul calo del mercato azionario, pubblicato il 5 novembre alle 23:18:52 UTC e rilevato il 6 novembre alle 03:39:51.999 UTC: circa 261 minuti dopo. È classificato `OTHER`, dominio `AI_TECH`, `POTENTIAL_CORRELATION`, non catalizzatore direzionale. Il contenuto di pagina TRUTH_ARCHIVE associato è page-level, senza timestamp item-level: non è una seconda notizia indipendente.

Il run delle 11:31 non ha aggiunto nuovi eventi; GAGARIN handoff risulta disabilitato perché URL/API key cloud non configurati. NARWHAL non configurato; indipendenza upstream SILV non dimostrata.

## 4. GAGARIN — prezzi, setup, feedback

Nel monitor #42203497432 il runtime dichiara 8 commodity operative più 2 Forex ausiliari. Prezzi:
- Grano: YAHOO STALE, 622,4s.
- Brent: YAHOO STALE, 604,3s.
- WTI: YAHOO STALE, 601,2s.
- Oro: YAHOO STALE, 614,5s.
- Argento: YAHOO STALE, 606,0s.
- Rame: YAHOO STALE, 607,1s.
- Mais: YAHOO STALE, 622,4s.
- Soia: YAHOO STALE, 664,5s.
- EUR/USD e GBP/USD: BIQUOTE LIVE, circa 187s; sono strumenti ausiliari, non segnali commodity.

Per tutte le otto commodity il log riporta `ALL_PROVIDER_CANDLES_STALE`. Il grano è SHORT `PAPER_WATCH`, bloccato da dato non fresco, trigger non confermato, mismatch direzionale, RR_FAIL e confluence failure. Brent, WTI, Oro, Argento, Rame, Mais e Soia non hanno setup operativo completo; mancano entry/SL/TP/ATR/RR o la conferma richiesta. Nessun livello è idoneo a outcome scoring.

Il run riporta:
- `New feedback signals: 0`;
- `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`.

Artefatti su main:
- `journal.csv`: 11 righe, tutte del 17 ottobre e con esito “nessun segnale”.
- `paper_trade_log.csv`: un WTI LONG legacy del 8 ottobre, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55. Importato come `LEGACY_IMPORT`; provider, ticker/contratto esatto, timestamp quota, mercato e prova fill assenti. La nota parla di chiusura spot del 6 ottobre: non è prova di esito e non va confrontata con un future.
- `commodities_prediction_log.json`: 981 record; ultimo creato il 15 settembre 2026 alle 15:45:04.462 UTC, Benzina RBOB LONG, stato PENDING. L'etichetta `COMPRA ORA` non prova esecuzione.
- `gagarin_feedback.csv`: non presente su main (404). Il riepilogo del monitor non registra nuovi feedback.

**Esiti GAGARIN:** nessun outcome verificabile. La posizione WTI legacy e le predizioni PENDING restano `ESITO NON VERIFICABILE`, non trade confermati.

## 5. PR e correzioni già esistenti

### SPUTNIK
- [PR #144 — Persist SPUTNIK state outside main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN, non merged. Head `8646794e...`; test ranking [#42247768085](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42247768085) verde; tentativo precedente [#42247726537](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42247726537) fallito sul commit precedente. Il confronto con main corrente mostra 4 commit ahead e 1 behind: branch divergente, non integrato.
- [PR #143 — Fix SPUTNIK short-token false domain labels](https://github.com/andreameloni1984-sys/trump-trucker/pull/143): OPEN, non merged; ranking e item-intelligence tests [#42243656376](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42243656376) e [#42243656439](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42243656439) verdi.

### GAGARIN
- [PR #221 — Remove residual FX routes](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): OPEN, DRAFT, head `74999010...`, ora direttamente basata su main `fba34bef...`, 12 commit ahead e zero behind. Correzione non ancora attiva su main. Integration tests [#42245355490](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42245355490), execution tests [#42245355476](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42245355476), e push checks [#42245347685](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42245347685) / [#42245347619](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42245347619) verdi sul relativo head.
- [PR #220 — Explicit commodity quote aliases](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/220): OPEN, DRAFT, non integrata.
- [PR #175 — Active Telegram webhook in scheduled polling](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): OPEN, non integrata. Il run #42236174265 continua a dimostrare 409 webhook/polling su main.

Il fatto che i test PR #221 siano verdi non dimostra che il monitor prezzi sia ripartito: il run operativo più recente resta #42203497432 e le commodity erano tutte stale.

## 6. Ledger, statistiche e decisione

File: `reports/pravda-signal-ledger-2026-11-06.csv`
- 32 record, 32 firme uniche, zero duplicati.
- GOLD LONG #707/#708 già presente una sola volta.
- Nessun nuovo segnale operativo da aggiungere.
- Fill verificati: 0; SL verificati: 0; TP verificati: 0; outcome verificabili: 0.
- Win rate e average R: N/D.

Non sono state scaricate o attribuite candele di strumenti/contratti diversi per forzare un risultato. Non è stato effettuato alcun backtest.

## 7. Fonti e prossimo controllo

Fonti: GitHub Actions e log completi dei job #42210907412, #42203497432, #42236174265, #42226158074 e #42232309653; GitHub Contents API per `sputnik_state.json`; ledger PRAVDA; journal, paper trade log, prediction log e workflow YAML su main; metadati e CI delle PR #143, #144, #175, #220 e #221.

Prossimo controllo:
1. verificare un nuovo collector SPUTNIK e un nuovo monitor GAGARIN su main;
2. per ogni alert, acquisire ticker runtime, mercato, scadenza, provider, timestamp/age quota e timestamp di ACK;
3. associare candele successive soltanto allo stesso ticker/contratto/scadenza e risolvere SL/TP in ordine temporale;
4. verificare che la rimozione FX e la correzione webhook/polling siano effettivamente su main prima di dichiararle attive;
5. mantenere il ledger senza duplicati e non classificare WATCH, PENDING o NOT_EXECUTED come trade.

**Perimetro:** audit e documentazione soltanto. Nessuna modifica a codice bot, strategia, filtri, punteggi o rischio; nessun merge/deploy/rerun, nessun ordine reale, nessuna modifica a segreti o Render. Nessun servizio a pagamento. PAPER ONLY.
