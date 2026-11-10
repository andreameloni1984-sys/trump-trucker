# PRAVDA — AUDIT INDIPENDENTE #27
## SPUTNIK / GAGARIN
**Cut-off: 10 novembre 2026, 06:13 CET (05:13 UTC)**

## 1. Esito sintetico

Nessuna nuova scansione di mercato schedulata è comparsa dopo SPUTNIK #296 e GAGARIN #174. Non sono emersi nuovi segnali operativi da aggiungere al registro. La verifica ha però corretto un'identità Telegram attribuita in modo errato nell'audit precedente e ha documentato ulteriori slot schedulati mancanti.

- Nessun fill verificato.
- Nessun trade PAPER eseguito dimostrato.
- Nessun esito SL prima / TP prima verificabile.
- Nessuna serie successiva dello stesso identico contratto disponibile per i segnali con identità contrattuale incompleta.
- Nessun merge, deploy o modifica al codice applicativo.

Main esaminati:
- SPUTNIK: `5f3ae3b8bc31275851cbf1f8c8ce964e6feb0ec6`.
- GAGARIN: `631727912b3a2022379a4460f4b6f756eba6991f`.

## 2. Registro PRAVDA — correzione senza nuovi record

Il ledger è stato riletto con parser CSV che rispetta i campi quotati. Prima e dopo la correzione:

| Indicatore | Risultato |
|---|---:|
| Record | 108 |
| SPUTNIK | 51 |
| GAGARIN | 57 |
| Firme uniche | 108 |
| Source record ID unici | 108 |
| Duplicati | 0 |
| NON_TRADE | 79 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |

Il solo cambiamento al ledger è una rettifica di provenienza del record GOLD SHORT della run SPUTNIK #296. Non è stato aggiunto un secondo record.

### Rettifica dell'identità Telegram

La lettura integrale del job log [SPUTNIK #296](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42726305978) stabilisce la sequenza:

| Message ID | Contenuto effettivamente stampato nel log | Classificazione |
|---|---|---|
| #754 | SPUTNIK — ANALISI DI MERCATO, GOLD SHORT preliminare, tecnica SHORT 5m, momentum -0,053%, NO_DIRECTIONAL_NEWS | Pre-alert, non ingresso |
| #755 | SPUTNIK — ANALISI CFD, GOLD SHORT, livelli numerici, NOT_EXECUTED | Record del segnale da conservare |
| #756 | BRIEF ORE 05:00, reazioni storiche incluse OIL DOWN (8 analoghi) | Brief informativo, non trade |
| #757 | ACK API successivo; nessun corpo associabile conservato nel log | Non attribuibile |

Il precedente ledger attribuiva erroneamente la card CFD al messaggio #756. È stato corretto a **#755**:
- `source_record_id=run:42726305978/telegram_message:755`;
- `telegram_message_id=755`;
- ACK API #755: 00:11:04.0127044 UTC, round-trip 374 ms;
- il corpo mostra soltanto 00:11 UTC (precisione al minuto); il timestamp esatto di generazione non è esposto separatamente.

Il messaggio #756 è il brief storico OIL DOWN, non la card CFD. Il messaggio #757 resta privo di corpo attribuibile. Gli ACK dimostrano accettazione API, non visualizzazione sul dispositivo.

### GOLD SHORT — parametri conservati

| Campo | Valore |
|---|---|
| Strumento logico | GOLD |
| Ticker quotato | NOT_RESOLVED |
| Mercato dichiarato | CFD; riferimento a future continuo front-month |
| Scadenza | UNKNOWN |
| Provider | NOT_EXPOSED; NARWHAL_NOT_CONFIGURED |
| Timestamp / età quotazione | NOT_EXPOSED |
| Direzione preliminare | SHORT |
| Tecnica nella card | NOT_ASSESSED |
| D-L-A | NEUTRAL / NO_DIRECTION |
| Entry | 4145.2002 |
| SL | 4146.7429 |
| TP1 | 4143.6575 |
| TP2 | 4142.1147 |
| ATR | 1.0285 |
| Score | 100 |
| Stato | EARLY_SETUP / NOT_EXECUTED |
| Outcome | NON_TRADE |

La card avverte esplicitamente: scadenza esatta e indipendenza upstream non verificate; non usare i livelli. Lo score non rende il segnale operativo. Senza ticker, scadenza e quotazione non è possibile selezionare candele successive dello stesso contratto: nessun esito SL/TP viene attribuito.

Il record GAGARIN [#3756](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729446093) rimane un WATCH pre-alert non attribuibile: l'API ha accettato il messaggio, ma il corpo non è conservato. Il run dichiara 0 entrate registrate, 0 feedback nuovi e 1 forecast WATCH aperto. Non è un trade.

## 3. SPUTNIK — Actions, fonti e difetti dimostrati

### Ultime esecuzioni schedulate disponibili

| Processo | Ultima run | Risultato | Configurazione main |
|---|---|---|---|
| Collector | [#296](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42726305978), 00:10:54–00:11:07 UTC | SUCCESS | `2-59/5 * * * *` |
| Telegram polling | [#55](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42723841180), 23:51:48–23:51:58 UTC | SUCCESS, pending updates 0 | `*/5 * * * *` |

La cronologia filtrata per `event=schedule` non mostra run successive. Al cut-off 05:13 UTC:
- collector: 61 slot teorici non presenti, da 00:12 a 05:12 UTC;
- polling: 64 slot teorici non presenti, da 23:55 a 05:10 UTC.

Sono slot calcolati dai cron e dal cut-off, non una diagnosi della causa. Non è dimostrato che Actions sia disabilitato; la causa dei trigger mancanti resta sconosciuta.

### Raccolta e classificazione

Nel run #296, il collector produttivo riporta SEC HTTP 403 e White House RSS HTTPError. Le numerose righe `source ... unavailable: OSError` compaiono nel passo precedente di regression test, che usa sorgenti simulate: non vanno attribuite alla raccolta live.

Il brief #756 riporta:
- US_EQUITIES DOWN (8 analoghi);
- NASDAQ DOWN (8 analoghi);
- USD DOWN (8 analoghi);
- TREASURY_YIELDS DOWN (8 analoghi);
- OIL DOWN (8 analoghi);
- analogo `china_tariff_escalation_2025_10`.

Il post individuale #43537 riguarda Qatar/Iran e nel messaggio #754 è accompagnato da `NO_DIRECTIONAL_NEWS`; il log non dimostra un nuovo evento tariffario individuale che giustifichi OIL DOWN. Su main, `sputnik_action_reaction.py` classifica ancora una menzione generica di China/Xi come `TRADE_ESCALATION`. La [PR #154](https://github.com/andreameloni1984-sys/trump-trucker/pull/154) propone di richiedere wording tariffario esplicito, ma non è integrata (1 commit avanti, 0 indietro; 234 test CI superati).

### PR SPUTNIK sotto verifica

| PR | Stato rispetto a main | CI / rilievo |
|---|---|---|
| [#156 — ordinamento cronologia](https://github.com/andreameloni1984-sys/trump-trucker/pull/156) | OPEN; 3 avanti, 1 indietro | 187 ranking + 66 menu + 47 intelligence = 300 test PASS; non integrata |
| [#155 — diagnostica cadenza](https://github.com/andreameloni1984-sys/trump-trucker/pull/155) | OPEN; 1 avanti, 0 indietro | 186 ranking + 46 intelligence = 232 test PASS; aggiunge osservabilità, non ripara i trigger |
| [#154 — analogia Cina/tariffe](https://github.com/andreameloni1984-sys/trump-trucker/pull/154) | OPEN; 1 avanti, 0 indietro | 234 test PASS; non integrata |
| [#153 — direzione tecnica nella card](https://github.com/andreameloni1984-sys/trump-trucker/pull/153) | OPEN; 2 avanti, 0 indietro | 253 test PASS; non integrata |
| [#144 — stato su branch dedicato](https://github.com/andreameloni1984-sys/trump-trucker/pull/144) | OPEN; 1 avanti, 0 indietro | 194 test ranking PASS; primo ciclo remoto non verificato |
| [#128 — separare test dai log live](https://github.com/andreameloni1984-sys/trump-trucker/pull/128) | OPEN; 4 avanti, 151 indietro | Branch troppo divergente per essere considerato pronto |

La #156 corregge l'uso di `values()[-30:]` su una cronologia newest-first, che selezionava record vecchi. La #153 risolve la perdita della direzione tecnica tra analisi preliminare e card CFD. Nessuna delle due è su main.

Il workflow live esegue ancora regression test prima del collector; le righe mock confondono il log produttivo. La #128 è 151 commit indietro e non è una correzione pronta da integrare.

## 4. GAGARIN — scansione, universe e quotazioni

Ultima scansione schedulata: [Monitor #174](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729446093), 00:35:20–00:35:42 UTC, SUCCESS su main `6317279`.

Il workflow main dichiara cron `*/15 * * * *`. Nessuna successiva run schedule è presente nella cronologia consultata: 18 slot teorici non presenti da 00:45 a 05:00 UTC.

### Universo effettivo

Il log e `commodities/universe.py` su main confermano 13 strumenti operativi: otto commodity più EUR/USD, DAX, S&P 500, NVIDIA e Tesla. Il runner Render nel codice stampa ancora “13 approved instruments”; la presenza del loop a 5 minuti nel codice non dimostra un deployment Render attivo.

| Commodity | Provider | Età nel run #174 | Stato |
|---|---|---:|---|
| Oro | YAHOO | 612,4 s | STALE |
| Argento | YAHOO | 628,1 s | STALE |
| Rame | YAHOO | 663,3 s | STALE |
| WTI | YAHOO | 602,5 s | STALE |
| Brent | YAHOO | 771,6 s | STALE |
| Grano | YAHOO | 18.938,7 s | STALE |
| Mais | YAHOO | 18.939,7 s | STALE |
| Soia | YAHOO | 18.940,8 s | STALE |

Otto commodity su otto stale. Le sole righe LIVE erano Tesla, EUR/USD e NVIDIA, fuori dal paniere commodity. Tutte le otto commodity risultano bloccate da `LIVE_DATA_NOT_FRESH` e mancano setup/trigger/livelli. Il run riporta 0 entrate, 0 outcome aggiornati, 0 feedback nuovi e un WATCH non attribuibile (#3756).

### Correzione universo disponibile

[PR #248 — paniere esatto a otto commodity](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/248):
- head `c8f55e0f0fabe53a2eec32613d4d7b7a9f078920`;
- 22 commit avanti, 0 indietro rispetto a main;
- 7/7 workflow CI SUCCESS;
- il log più recente della suite principale [#42756695026](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42756695026) riporta **572 passed in 2.72s**.

La PR è ancora OPEN/DRAFT e non integrata. Main resta a 13 strumenti.

[PR #250 — disabilitare confronti manuali CFD Trading 212/futures](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/250):
- 3 avanti, 0 indietro;
- 6/6 workflow CI SUCCESS;
- suite principale 574 test PASS e NEWS alert 73 test PASS;
- OPEN/DRAFT, non integrata.

Non è stato consultato Trading 212 né dichiarato accesso a quotazioni broker.

## 5. GAGARIN — journal, feedback e outcome

### Journal

- `commodities_prediction_log.json`: 981 record; ultimo record 2026-09-15 15:45:04 UTC; 945 PENDING, 36 NEUTRALE; 21 “COMPRA ORA”, tutte PENDING.
- `paper_trade_log.csv`: un solo WTI `LEGACY_IMPORT` (entry 96.24, SL 89.37, TP1 103.11, TP2 106.55), senza signal ID, quote provenance o esito; non è un fill verificato.
- `gagarin_feedback.csv`: assente su main.
- `paper_open.json`: assente su main.
- Nel run #174 `DATABASE_URL` è vuota e non ci sono artifact. Il workflow commenta che i journal PAPER sono dati privati e che la persistenza sarà riattivata dopo il deployment di storage privato D1. La persistenza durevole non è dimostrata; non è stato letto o modificato alcun secret.

### Outcome engine

Su main, `engine/feedback.py` abbina soprattutto symbol/timeframe e classifica STOP prima dei target. Se una candela OHLC tocca SL e TP nella stessa barra, il codice attuale può assegnare STOP anche se l'ordine intrabar è ignoto.

[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) propone:
- fingerprint con provider, quote ticker, mercato e scadenza;
- matching di ticker/mercato e contratto futures;
- `ESITO NON VERIFICABILE` per doppio tocco nella stessa candela.

La PR è OPEN, 6 commit avanti e 10 indietro rispetto a main. Il patch include il provider nel fingerprint, ma `_market_contract_match()` non confronta esplicitamente il provider della serie successiva: la continuità della provenienza va chiarita prima di considerare la correzione completa.

Altre PR rilevanti:
- [#202 — journal PostgreSQL](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): OPEN/DRAFT, 18 avanti e 8 indietro; non integrata.
- [#175 — conflitto webhook/polling 409](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): OPEN, 1 avanti e 7 indietro. La run [#21](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729120141) fallisce con `getUpdates 409: webhook is active`.
- [#240 — nascondere livelli LUBJANKA stale](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/240): OPEN/DRAFT, 5 avanti e 4 indietro; CI non certificata in questo controllo.
- [#198 — ripristino ranking baseline](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/198): OPEN/DRAFT, 2 avanti e 10 indietro. Main conserva il bonus/malus di accelerazione momentum fino a +8/-4 punti; nessuna modifica effettuata da PRAVDA.

Il workflow Telegram polling GAGARIN su main dichiara cron `*/5 7-21 * * 1-5`, mentre la run #21 marcata `schedule` è delle 00:32:48 UTC, fuori da quella finestra. Al cut-off 05:13 UTC la finestra 07–21 UTC non è ancora iniziata. La discrepanza fra timestamp del run e cron attuale richiede riconciliazione; non viene ipotizzata una causa.

## 6. Statistiche e classificazione

Le sole statistiche ammesse dal campione sono quelle documentali del ledger:
- 108 record, 108 firme uniche, 108 source ID unici, 0 duplicati;
- 79 record NON_TRADE;
- 29 record ESITO_NON_VERIFICABILE;
- 0 fill verificati, 0 SL verificati, 0 TP verificati.

Win rate, Average R e Total R: **N/D**. Non esiste un campione di trade eseguiti con ticker, mercato, scadenza e prezzi successivi dello stesso contratto sufficiente a calcolarli.

## 7. Fonti consultate

**SPUTNIK**
- [Run #296](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42726305978), job log completo e artifacts (nessuno).
- [Polling #55](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42723841180).
- `.github/workflows/trump_tracker.yml`, `.github/workflows/telegram-polling.yml`.
- `sputnik_action_reaction.py`, `sputnik_state.json` tramite commit di persistenza.
- PR #128, #144, #153, #154, #155, #156 e relative CI.

**GAGARIN**
- [Monitor #174](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729446093), job log completo e artifacts (nessuno).
- [Polling #21](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729120141).
- `.github/workflows/gagarin-monitor.yml`, `.github/workflows/telegram-polling.yml`.
- `commodities/universe.py`, `telegram/render_runner.py`, `engine/feedback.py`, `engine/prediction_ranker.py`.
- `commodities_prediction_log.json`, `paper_trade_log.csv`; verifica 404 di `gagarin_feedback.csv` e `paper_open.json`.
- PR #175, #192, #198, #202, #240, #248, #250 e relative CI.

## 8. Lacune e prossimo controllo

1. Verificare se ripartono i cron SPUTNIK e GAGARIN e documentare il gap senza attribuire cause non provate.
2. Verificare l'integrazione effettiva della PR #248 prima di dichiarare attivo il paniere a otto.
3. Verificare quotazioni fresche per tutte le otto commodity e identità esatta di ticker, mercato e scadenza.
4. Verificare la card SPUTNIK dopo l'eventuale integrazione della #153 e la classificazione dopo la #154.
5. Conservare per ogni messaggio il corpo, il message ID e l'ACK associato; distinguere ACK API da consegna sul dispositivo.
6. Dimostrare persistenza del journal tra esecuzioni senza pubblicare dati privati.
7. Completare e riallineare l'outcome engine; doppio tocco intrabar resta ESITO NON VERIFICABILE.
8. Verificare il conflitto Telegram 409 e la discrepanza tra cron e timestamp della run #21.

**Confini rispettati:** nessuna modifica a codice applicativo, strategia, filtri, punteggi, soglie o rischio; nessun merge/deploy, ordine reale, accesso Trading 212, modifica a secret o Render, né servizio a pagamento. PAPER ONLY.
