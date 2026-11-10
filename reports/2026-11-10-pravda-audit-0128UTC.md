# PRAVDA — Audit indipendente #24
## SPUTNIK / GAGARIN
**10 novembre 2026 — 01:28 UTC (02:28 CET)**

## Sintesi esecutiva

Verificati gli ultimi workflow Actions disponibili, i log integrali dei job produttivi, i commit di `main`, i file di stato e journal, le configurazioni dei monitor e le PR correttive.

**Non risultano nuove scansioni programmate dopo SPUTNIK #296 e GAGARIN #174 nel periodo esaminato.** Non sono emersi nuovi segnali da aggiungere al registro rispetto all'audit #23.

Progressi documentati:
- SPUTNIK PR #153 è ora pronta per review, aggiornata sull'ultimo `main`, con 253 test CI superati.
- GAGARIN PR #248 è stata aggiornata a 20 commit avanti / 0 indietro rispetto a `main`; sette workflow CI verdi e 571 test superati.
- La correzione GAGARIN proposta in PR #192 tratta il doppio tocco SL/TP come non verificabile, ma il matching provider resta incompleto nel patch della PR.

Problemi produttivi ancora presenti:
- GAGARIN #174 ha analizzato 13 strumenti; tutte le otto commodity selezionate erano STALE.
- GAGARIN main resta a 13 strumenti; il paniere a otto esiste soltanto nel branch PR #248.
- Il polling Telegram GAGARIN #21 fallisce ancora con HTTP 409.
- Non è dimostrata la persistenza durevole del journal GAGARIN.
- Nessun segnale esaminato dispone dell'identità contrattuale completa e di candele successive omogenee per certificare SL o TP.

---

## 1. Registro PRAVDA — controllo anti-duplicati

Ho recuperato e analizzato il CSV cumulativo dal branch documentale precedente, verificando il parsing dei campi CSV quotati e le due chiavi d'identità.

| Indicatore | Risultato |
|---|---:|
| Record | 108 |
| Firme uniche | 108 |
| Source ID unici | 108 |
| Duplicati firma | 0 |
| Duplicati source ID | 0 |
| SPUTNIK | 51 |
| GAGARIN | 57 |
| NON_TRADE | 79 |
| ESITO_NON_VERIFICABILE | 29 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |

SHA del CSV: `7ee27891e651aa4b581d2a0b70f6f1ce219a936a`.

Il registro contiene già:
- SPUTNIK #756: `run:42726305978/telegram_message:756`;
- GAGARIN #3756: `run:42729446093/telegram_watch_pre_alert:3756`.

Non ho aggiunto righe: entrambi erano già presenti nel ledger dell'audit #23 e non sono emersi nuovi segnali univoci. Non ho modificato il CSV.

Win rate, Average R e Total R: **N/D**. I record NOT_EXECUTED e WATCH non sono trade.

[Ledger PRAVDA cumulativo](https://github.com/andreameloni1984-sys/trump-trucker/blob/pravda/audit-2026-11-10-0048UTC/reports/pravda-signal-ledger-2026-11-09.csv)

---

## 2. SPUTNIK — Actions e stato produttivo

### Ultimi workflow schedule disponibili

| Workflow | Run | Avvio UTC | Fine UTC | Esito |
|---|---:|---|---|---|
| Collector SPUTNIK | [#296](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42726305978) | 00:10:54 | 00:11:07 | SUCCESS |
| Telegram Polling | [#55](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42723841180) | 23:51:48 del 9/11 | 23:51:58 | SUCCESS |

La run #55 registra `Pending updates: 0`: il polling è terminato correttamente, ma non ha processato aggiornamenti pendenti. Non dimostra la consegna di nuovi messaggi.

Alle 01:28 UTC del 10 novembre:
- collector #296 terminato da circa 1h16m53s;
- polling #55 terminato da circa 1h36m02s.

Nell'elenco recente delle Actions non compare un successivo schedule del collector.

### Run #296 — fonti

Il log produttivo conferma:
- SEC: HTTP 403, cooldown 21.600 secondi;
- filing: 0;
- White House RSS: HTTPError;
- scansione intelligence pubblica: 1.670 ms, 3 findings;
- tempo totale run: circa 4.313 ms;
- fase notifiche: circa 2.450 ms.

Il commit automatico [5f3ae3b](https://github.com/andreameloni1984-sys/trump-trucker/commit/5f3ae3b8bc31275851cbf1f8c8ce964e6feb0ec6) ha persistito lo stato su `main`, modificando il file di stato SPUTNIK.

Il diff mostra un item-level RSS:
- URL: https://www.trumpstruth.org/statuses/43537
- feed: https://www.trumpstruth.org/feed
- pubblicazione: 2026-11-09 21:29:28 UTC;
- rilevamento: 2026-11-10 00:11:01.522 UTC;
- titolo e testo presenti;
- domini classificati DEFENSE / AI_TECH;
- stato POTENTIAL_CORRELATION;
- evento GEOPOLITICAL_ESCALATION;
- evidenza storica: NO_ANALOGUE.

Latenza pubblicazione-rilevamento: circa **2h41m33s**; pubblicazione-generazione card: circa **2h41m36s**. Il ritardo è a monte della richiesta Telegram: gli ACK API delle notifiche sono nell'ordine di 374–467 ms. Il log non consente di attribuire tutto il ritardo a una sola causa, ma dimostra che la notizia era già pubblicata da oltre due ore al momento dell'analisi.

Lo stesso diff conserva un distinto snapshot homepage TRUTH_ARCHIVE senza titolo né data di pubblicazione. L'identificativo OGE resta nella mappa dello stato, ma il diff non dimostra un nuovo evento OGE in questa scansione: non va confuso con l'item RSS #43537.

### Messaggi #754–#757 e segnale GOLD

I quattro messaggi hanno funzioni differenti:
- #754: riepilogo della notizia;
- #755: analisi preliminare GOLD SHORT;
- #756: card CFD GOLD SHORT;
- #757: brief storico/analogie, non una nuova operazione.

Il candidato operativo va registrato una sola volta, sotto la card dettagliata #756. Il messaggio #755 è il suo compagno analitico.

**GOLD SHORT #756**

| Campo | Valore |
|---|---|
| Source ID | `run:42726305978/telegram_message:756` |
| Generazione | 2026-11-10 00:11:04.0127804 UTC |
| ACK API registrato | 2026-11-10 00:11:04.0141166 UTC |
| Message ID | 756 |
| Strumento logico | GOLD |
| Ticker quotato | NOT_RESOLVED |
| Mercato dichiarato | titolo CFD; riferimento a future continuo front-month |
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

Il messaggio compagno #755 riporta SHORT tecnico 5m, momentum -0,053% negli ultimi 15 minuti e NO_DIRECTIONAL_NEWS. La card #756 stampa invece `TECNICA: N/D (NOT_ASSESSED)` e D-L-A NEUTRAL / NO_DIRECTION (INSUFFICIENT_DATA). Nel motivo testuale compare comunque una descrizione della direzione tecnica SHORT: la card non conserva in modo coerente il campo strutturato/timeframe.

La card dichiara espressamente:
- future continuo front-month;
- scadenza esatta e indipendenza upstream non verificate;
- controllo SPOT/FUTURES non verificato;
- componenti SILV con indipendenza non verificata;
- livelli da non utilizzare.

Score 100 non equivale a validità operativa. NOT_EXECUTED non è un fill. Non sono disponibili ticker contrattuale, provider, timestamp/prezzo della quotazione o candele successive dello stesso contratto. **Esito: NON_TRADE; nessun SL/TP attribuito.**

ACK API:
- #754: 415 ms;
- #755: 374 ms;
- #756: 467 ms;
- #757: 379 ms.

Sono accettazioni API registrate, non prova di visualizzazione sul dispositivo.

### PR #153 — propagazione della direzione tecnica

[PR SPUTNIK #153](https://github.com/andreameloni1984-sys/trump-trucker/pull/153)

Stato attuale:
- OPEN, non-DRAFT;
- head `a536ae98c9b4ac10b7eb28de6c755c94d9c73d91`;
- base main `5f3ae3b8bc31275851cbf1f8c8ce964e6feb0ec6`;
- confronto: 2 commit ahead / 0 behind;
- ranking CI: SUCCESS, 186 test;
- Telegram menu CI: SUCCESS, 67 test;
- totale: 253 test superati.

Il diff propaga nella card CFD i campi tecnici già calcolati: direzione, timeframe, motivazione e allineamento. È una correzione di presentazione/tracciabilità; non cambia bias, livelli, rischio o autorizzazione. Non è integrata. La run #296, eseguita prima dell'aggiornamento della PR, riproduce ancora il difetto.

---

## 3. GAGARIN — run produttiva e quotazioni

### Ultimo schedule disponibile

[Monitor GAGARIN #174](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729446093)

- avvio: 2026-11-10 00:35:20 UTC;
- completamento: 00:35:42 UTC;
- esito: SUCCESS;
- commit: `631727912b3a2022379a4460f4b6f756eba6991f`.

Alle 01:28 UTC erano trascorsi circa 52m27s. Nell'elenco recente delle Actions non compare un successivo schedule GAGARIN.

### Universo e freschezza

Il log riporta 13 strumenti operativi.

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

**Otto commodity su otto STALE.**

Le sole righe LIVE nel run erano:
- Tesla — YAHOO, 16,0 s;
- EUR/USD — BIQUOTE, 37,7 s;
- NVIDIA — YAHOO, 2,9 s.

Sono strumenti fuori dal paniere commodity richiesto. DAX e S&P 500 risultavano anch'essi STALE.

Risultato operativo:
- Recorded entries: 0;
- Updated open outcomes: 0;
- New feedback signals: 0;
- New additional live forecasts (WATCH/other): 1;
- `signals=1 open=1 closed=0`;
- win_rate=N/D, avg_R=N/D, total_R=0.

Telegram #3756 è stato accettato dall'API, round-trip 594 ms. Il corpo non è conservato. Non si possono attribuire strumento, ticker, direzione, provider, timestamp della quotazione, scadenza o livelli.

Il record è già nel ledger come WATCH_PRE_ALERT non attribuibile, NOT_AUTHORIZED. Non è un ingresso né un trade.

### Frequenza: Render e GitHub Actions

Ho letto direttamente `telegram/render_runner.py` su main:
- `position_monitor_loop()` usa intervallo 5 × 60 secondi;
- ogni ciclo chiama `_run_analysis(on_demand=False)`;
- il log di startup dichiara ancora “13 approved instruments”.

Questa è la configurazione presente nel codice, non prova che il servizio Render sia stato distribuito o sia attivo.

Il workflow GitHub Actions `.github/workflows/gagarin-monitor.yml` mantiene:
- cron `*/15 * * * *`;
- `MONITOR_INTERVAL_MINUTES=15`;
- soglie runtime probabilità 40, qualità 30, confidence 35, RR 2,5.

Quindi la cadenza configurata è diversa: Render runner 5 minuti nel codice, GitHub Actions 15 minuti. Nessun accesso o intervento su Render è stato effettuato.

### PR #248 — universo esatto a otto commodity

[PR GAGARIN #248](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/248)

Nuovo head:
`d370ad676709f0be911db55f8314043e7dfce9fa`

Confronto con main:
- 20 commit ahead / 0 behind;
- merge-base uguale a main;
- PR OPEN/DRAFT, non integrata.

Il diff:
- elimina Forex, indici e azioni dalla lista canonica;
- introduce allowlist operativa fail-closed;
- fa usare `operational_commodities()` al selettore schedulato;
- modifica report, mapping provider e percorsi Telegram;
- fa dichiarare al monitor il paniere di otto commodity.

Paniere proposto: XAU/USD, XAG/USD, COPPER/USD, WTI/USD, BRENT/USD, WHEAT/USD, CORN/USD, SOYBEAN/USD.

CI sul nuovo head:
- 7/7 workflow SUCCESS;
- suite SOYUZ: **571 passed in 2.65s**.

Questi test dimostrano la correzione nel branch PR, non la sua integrazione o il deployment. Un commento automatico segnala un deployment failure del Cloudflare Worker `telegram-github-bridge`; è distinto dal servizio Render e non costituisce prova di deploy GAGARIN.

Main resta `6317279` e conserva 13 strumenti. La run #174 ne fornisce conferma produttiva.

### PR #250 — confronti manuali Trading 212

[PR GAGARIN #250](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/250)

Resta OPEN/DRAFT, 3 commit ahead / 0 behind. La patch rimuove dal bot attivo il confronto manuale tra prezzi CFD Trading 212 e serie futures, evitando di presentare mercati diversi come confrontabili. Non è integrata; non dimostra accesso a Trading 212.

---

## 4. Journal, feedback e persistenza GAGARIN

### Prediction log

File main: `commodities_prediction_log.json`.

| Indicatore | Risultato |
|---|---:|
| Record | 981 |
| PENDING | 945 |
| NEUTRALE | 36 |
| NON ENTRARE | 77 |
| ATTENDERE | 576 |
| SHORT — ASPETTARE CONFERMA | 15 |
| LONG — ASPETTARE CONFERMA | 292 |
| COMPRA ORA | 21 |
| Ultimo aggiornamento | 2026-09-15 15:45:04 UTC |

Le 21 righe COMPRA ORA sono PENDING, non trade eseguiti.

### Paper journal e database

- `paper_trade_log.csv`: un WTI LEGACY_IMPORT del 2026-10-08, senza signal ID, senza fill e senza esito.
- `paper_open.json`: non presente su main.
- `gagarin_feedback.csv`: non presente su main.
- Run #174: `DATABASE_URL` vuota.
- Artifact della run #174: nessuno.

Il messaggio WATCH #3756 e il contatore `signals=1 open=1` non sono accompagnati da un corpo conservato o da un archivio durevole verificabile. La persistenza cross-run non è dimostrata.

[PR #202 — persistenza journal](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202) resta OPEN/DRAFT e divergente rispetto a main: 18 ahead / 8 behind. La proposta richiede un database configurato dal proprietario; PRAVDA non ha letto né modificato segreti.

---

## 5. Outcome engine — verifica aggiornata

Main:
- file `engine/feedback.py`, blob `41bec9bfab031c8dbf71121cd69d0e9b4c4f663f`;
- il record non contiene campi separati per provider, quote ticker, market type, contract month o expiry;
- matching successivo principalmente per symbol/timeframe;
- docstring e codice valutano `stop_hit` prima dei target.

Una candela che tocca SL e TP può quindi essere registrata come STOP su main, in contrasto con il criterio PRAVDA.

### PR #192

[PR GAGARIN #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192)

- OPEN, non-DRAFT;
- head `295dba4b074e564a4c11aa3fca136a8e4360672c`;
- confronto con main: 6 ahead / 10 behind;
- non integrata.

Il patch della PR migliora due aspetti:
1. include provider, ticker, mercato e scadenza nel fingerprint;
2. tratta il doppio tocco SL/TP nella stessa candela come `ESITO NON VERIFICABILE`, senza R realizzato.

Resta però una lacuna dimostrata: `_market_contract_match()` confronta quote_symbol, market_type e, per futures, contract_month/contract_expiry, ma **non confronta esplicitamente quote_provider della riga segnale con il provider della serie OHLC successiva**. Il provider è nel fingerprint, ma il guard può accettare una serie proveniente da un provider diverso se ticker/mercato/contratto coincidono.

La PR deve essere riallineata e il controllo provider deve essere esplicito prima che PRAVDA possa certificare outcome. Ho aggiornato il commento di audit già esistente, senza crearne uno duplicato.

Regola di valutazione invariata:
- SL toccato prima dei target: STOP;
- target toccato prima dello SL: TP;
- SL e TP nella stessa candela senza sequenza intrabar ricostruibile: ESITO NON VERIFICABILE;
- mercato, ticker, provider o contratto/scadenza non coincidenti o non esposti: ESITO NON VERIFICABILE.

---

## 6. Telegram GAGARIN

[Polling #21](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729120141) è fallito.

Log:
`getUpdates blocked by Telegram API error_code=409: webhook is active; polling cannot run while webhook mode is enabled.`

La diagnostica del bot è riuscita; è il polling a fallire per conflitto con webhook attivo. Non è stato cancellato o modificato alcun webhook.

[PR #175](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175) resta la correzione proposta, non integrata.

---

## 7. Aggiornamenti ai reparti

Per evitare commenti duplicati ho aggiornato tre commenti PRAVDA già esistenti:

- [SPUTNIK PR #153 — aggiornamento test e riproduzione #296](https://github.com/andreameloni1984-sys/trump-trucker/pull/153#issuecomment-6755689742);
- [GAGARIN PR #248 — head d370ad, 571 test e prova produttiva #174](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/248#issuecomment-6755690213);
- [GAGARIN PR #192 — provider non confrontato nel guard](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6755691745).

Non ho creato nuovi issue né modificato codice applicativo.

---

## 8. Fonti consultate

### SPUTNIK
- [Actions collector #296](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42726305978)
- [Actions polling #55](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42723841180)
- [Commit di persistenza stato #5f3ae3](https://github.com/andreameloni1984-sys/trump-trucker/commit/5f3ae3b8bc31275851cbf1f8c8ce964e6feb0ec6)
- [Post pubblico #43537](https://www.trumpstruth.org/statuses/43537)
- [PR #153](https://github.com/andreameloni1984-sys/trump-trucker/pull/153)

### GAGARIN
- [Actions monitor #174](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729446093)
- [Actions polling #21](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42729120141)
- [PR #248](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/248)
- [PR #250](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/250)
- [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192)
- [PR #202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202)

### Artefatti
- Ledger cumulativo PRAVDA: SHA `7ee27891e651aa4b581d2a0b70f6f1ce219a936a`.
- Prediction log main: 981 record.
- Paper journal main: un solo WTI LEGACY_IMPORT.

---

## 9. Prossimo controllo

1. Verificare il prossimo schedule SPUTNIK e misurare nuovamente latenza pubblicazione-rilevamento, separandola dal round-trip Telegram.
2. Verificare se PR #153 viene integrata e se la card CFD mostra la direzione tecnica 5m in modo strutturato.
3. Verificare se PR #248 viene integrata; solo una successiva scansione su main potrà dimostrare il paniere a otto strumenti.
4. Verificare freschezza e timestamp delle otto quotazioni commodity.
5. Accertare separatamente il funzionamento del loop Render a cinque minuti, senza intervenire sul servizio.
6. Verificare la persistenza del journal tra due run e l'identità del WATCH #3756.
7. Riallineare PR #192 e verificare provider, ticker, mercato e scadenza nella selezione delle candele successive.
8. Verificare la correzione del conflitto Telegram 409 senza cancellare il webhook.

---

## 10. Verdetto

| Metrica | Risultato |
|---|---:|
| Record cumulativi | 108 |
| Duplicati | 0 |
| Nuovi record in questo audit | 0 |
| Fill verificati | 0 |
| SL verificati | 0 |
| TP verificati | 0 |
| Win rate | N/D |
| Average R | N/D |
| Total R | N/D |

**Nessuna performance può essere certificata.** GOLD #756 è NOT_EXECUTED; GAGARIN #3756 è un WATCH non attribuibile. Non esistono quote e OHLC successivi dello stesso identico strumento e contratto per attribuire SL o TP.

PRAVDA non ha modificato codice, strategia, filtri, punteggi, soglie o rischio. Nessun merge, deploy, ordine reale, modifica di secret o Render. Nessun servizio a pagamento. Nessun accesso a Trading 212 dichiarato. Gli ACK Telegram sono trattati esclusivamente come accettazioni API.

**PAPER ONLY.**
