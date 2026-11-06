# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-06 21:38 UTC (22:38 Europe/Rome)**

## Sintesi

- Nessun nuovo collector di mercato SPUTNIK dopo [#42270098789](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42270098789), avviato il 6 novembre alle 18:22:24 UTC.
- Nessun nuovo monitor prezzi GAGARIN dopo [#42263910777](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42263910777), avviato alle 17:41:19 UTC. Nelle 100 Actions più recenti l'unico run GAGARIN schedule successivo è il polling Telegram [#42289526533](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42289526533), non un monitor prezzi.
- Ultimo collector SPUTNIK: età al cut-off 3h16m16s; ultimo monitor GAGARIN: 3h57m21s. I cron dichiarati sono 5m e 15m.
- Nessun nuovo segnale di mercato da aggiungere: il candidato SPUTNIK #712 e il watch board GAGARIN #3709 sono già nel ledger.
- Ledger main: 35 record, 35 firme uniche, zero duplicati. Nessun fill, SL o TP verificabile; win rate e average R N/D.
- Nuova criticità metodologica confermata nel feedback GAGARIN: stessa candela con SL e TP toccati viene marcata STOP, e se più TP sono toccati nella stessa candela viene selezionato il TP più alto. Entrambe le inferenze eccedono ciò che l'OHLC consente di sapere intrabar.

## 1. Branch, Actions e continuità

### Main al momento dell'audit
- SPUTNIK `main`: `0493c6ce836f33d1c0faacad7a978a26f670a930`.
- GAGARIN `main`: `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`.

### SPUTNIK
- Workflow [SPUTNIK #42270098789](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42270098789): schedule, avvio 18:22:24 UTC, conclusione SUCCESS, checkout SHA `88d4333691bdf81a2fdabfb929756470e084aadd`.
- Precedente collector di mercato: [#42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412), avvio 11:31:39 UTC. Gap tra avvii: 6h50m45s.
- Al cut-off 21:38:40 UTC, ultimo collector vecchio di 3h16m16s.
- Cron nel workflow `.github/workflows/trump_tracker.yml`: `2-59/5 * * * *`.
- Il run #42270098789 ha job `sputnik` SUCCESS. Lo step di regression test precede il collector: il message_id #731 con round-trip 0ms compare in quel test e non è un messaggio di produzione. Il collector reale ha emesso digest #710, analisi #711 e scheda CFD #712.
- [Telegram Polling #42265633569](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42265633569), 17:52:46 UTC, è un workflow separato e non un collector di mercato.

### GAGARIN
- Workflow [Gagarin Paper Monitor #42263910777](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42263910777): schedule, avvio 17:41:19 UTC, conclusione SUCCESS, checkout SHA `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`.
- Precedente monitor: [#42203497432](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42203497432), avvio 10:32:52 UTC. Gap: 7h08m27s.
- Al cut-off, ultimo monitor vecchio di 3h57m21s.
- Cron in `.github/workflows/gagarin-monitor.yml`: `*/15 * * * *`.
- Nessun monitor prezzi successivo nelle 100 Actions più recenti. Test PR e polling non sono monitor di mercato.
- [Telegram Polling #42289526533](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42289526533), 20:34:39 UTC, FAILURE. Il job conferma diagnostica Telegram OK, poi `getUpdates` fallisce con API 409: webhook attivo, polling incompatibile. Il token/chat risultano presenti nel runner, ma questo non prova la consegna dei messaggi sul dispositivo.

La causa dei gap tra i monitor non è dimostrata. Non li attribuisco a filtri, Render o a una causa infrastrutturale specifica senza ulteriori log.

## 2. SPUTNIK — ultimo candidato GOLD SHORT, già registrato

Fonte: [run #42270098789](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42270098789).

### Identità e cronologia
- Firma ledger: `PRAVDA-SPUTNIK-CFD-RUN42270098789-20261106T182232Z-GOLD-SHORT-4069.3-4071.7536-4066.8465-4064.3929`.
- Messaggi correlati: digest #710, analisi #711, CFD #712; sono fasi dello stesso candidato.
- Generazione scheda CFD: 2026-11-06 18:22:32.111256 UTC.
- ACK API Telegram #712: 18:22:32.112773 UTC, round-trip 311 ms. È accettazione API con message_id, non prova di visualizzazione sul dispositivo e non esecuzione.
- #710 digest: ACK 377 ms; #711 analisi: ACK 300 ms.
- Il message_id #731 è output della suite di regression test eseguita prima del collector e viene escluso.

### Dati del candidato
- Strumento dichiarato: GOLD.
- Mapping configurato: `GC=F`; ticker runtime effettivamente risolto non esposto.
- Mercato: future continuo front-month.
- Contratto/scadenza esatti: UNKNOWN.
- Provider runtime, timestamp della quotazione e quote age: NOT_EXPOSED.
- Direzione preliminare: SHORT.
- Entry 4069.3; SL 4071.7536; TP1 4066.8465; TP2 4064.3929; ATR 1.6357; score 70.
- Stato: `EARLY_SETUP / NOT_EXECUTED`; il messaggio avverte che la scadenza esatta e l'indipendenza upstream non sono verificate e che i livelli non sono utilizzabili.

### Coerenza e fonti
- Il testo di analisi #711 dichiara direzione tecnica SHORT.
- La scheda CFD #712 presenta una lettura focused in contrasto: prezzo sopra EMA50, EMA50 sopra EMA200, swing crescenti e D-L-A EMA20/EMA50 LONG. La direzione dettagliata è quindi in conflitto con il bias SHORT; non tratto score 70 come validazione.
- Nessun catalizzatore direzionale verificato; `NO_DIRECTIONAL_NEWS`.
- Feed pubblico: [Trumpstruth RSS](https://www.trumpstruth.org/feed).
- Post 43495 pubblicato 12:01:50 UTC e rilevato 18:22:30.541 UTC: ritardo circa 6h20m40s. Il termine GOLD è metaforico nel testo sull'intelligenza artificiale, ma il record è etichettato METALS; il run lo classifica OTHER / NO_ANALOGUE. È un falso positivo di dominio già noto.
- Post 43496 pubblicato 18:05:27 UTC e rilevato 18:22:30.541 UTC: ritardo circa 17m03s.
- Il collector registra 4 findings/correlazioni pubbliche, zero filing e zero nuove operazioni documentate. SEC HTTP 403 con cooldown 21600s; White House RSS HTTPError; fonti WHITE_HOUSE, TRUTH_ARCHIVE e OGE con OSError.
- Handoff GAGARIN disabilitato perché GAGARIN_CLOUD_API_URL/API_KEY non sono configurati.

**Esito PRAVDA: ESITO NON VERIFICABILE.** È `NOT_EXECUTED`, non un trade. Nessuna candela successiva dello stesso ticker e della stessa scadenza è stata usata.

### Stato SPUTNIK persistito
Il run ha creato il commit [0439dca9](https://github.com/andreameloni1984-sys/trump-trucker/commit/0439dca9cfa0e349c3cb2237fd4aeb78bd110f00), discendente del checkout del run e incluso nell'attuale main. Il blob di `sputnik_state.json` è stato letto direttamente:
- aggiornato 18:22:30.578530 UTC;
- 500 record in `intelligence_history`;
- `events=0`, `transactions=0`;
- `telegram_active=true`, offset 275590742.
Non risulta un aggiornamento successivo al run #42270098789 nel materiale esaminato.

## 3. GAGARIN — ultimo monitor, watch board e quotazioni

Fonte: [run #42263910777](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42263910777).

### Quotazioni operative
Tutte le otto commodity operative risultano YAHOO STALE:
- Oro 602.3 s
- WTI 603.4 s
- Brent 609.5 s
- Grano 608.6 s
- Mais 615.7 s
- Argento 613.1 s
- Soia 601.8 s
- Rame 602.3 s

Per ciascuna il fallback dichiarato è `ALL_PROVIDER_CANDLES_STALE`. Il log non espone timestamp puntuale della candela, ticker runtime completo o scadenza del contratto.

### Contesto Forex
- EUR/USD LIVE via BIQUOTE, age 94.3 s.
- GBP/USD LIVE via BIQUOTE, age 94.8 s.
- Entrambi sono etichettati `CONTESTO FX — NON OPERATIVO`, non segnali commodity.
- Il workflow imposta `GAGARIN_FOREX_ON_DEMAND=0`, ma il runtime continua a includere due FX ausiliari nella finestra. PR #221, che rimuove rotte FX residue, è ancora draft e non integrata su main.

### Watch board #3709
- Header/run timestamp: 17:41:32.167113 UTC.
- Telegram API ACK #3709: 17:41:35.207004 UTC, 436 ms.
- Il corpo del messaggio non è presente nel log. Non attribuisco quindi con certezza il messaggio a un singolo strumento.
- La classifica mostra Argento LONG, probabilità 59.0, quality 49.5, confidence 32.0, ma è bloccato da LIVE_DATA_NOT_FRESH, trigger non confermato, mismatch direzionale, RR_FAIL e confidence fail. Questo non dimostra che il board #3709 contenesse soltanto Argento.
- Nessun entry/SL/TP/ATR operativo. È un WATCH pre-alert, non un trade.
- Il run dichiara: updated open outcomes 0; new feedback signals 0; additional live forecasts 0; `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`.

Il precedente WATCH Grano SHORT #3701 resta nel ledger: quote YAHOO stale 622.4 s, trigger non confermato, mismatch e RR insufficiente, senza livelli operativi.

## 4. Journal, feedback e posizioni legacy GAGARIN

Artefatti verificati su main:
- `journal.csv`: 11 righe, tutte del 2026-10-17 e tutte registrate come “nessun segnale”.
- `paper_trade_log.csv`: una posizione WTI LONG legacy del 2026-10-08, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55; provider/contratto/fill non documentati.
- `data/paper_open.json`: P0001 è lo stesso WTI LONG legacy, non una seconda operazione.
- `position.json`: vecchia posizione Heating Oil LONG, aperta 2026-09-15T13:23:44Z, entry 4.8844, stop 4.5418, TP1 5.4573; nessuna prova indipendente del fill o dell'esito.
- `commodities_prediction_log.json`: 981 record; ultimo creato 2026-09-15T15:45:04.462276Z. Gli ultimi record sono PENDING: l'etichetta COMPRA ORA non prova un'esecuzione.
- `gagarin_feedback.csv`: 404 su main; non è disponibile come artefatto pubblico corrente.
- Nel log monitor `DATABASE_URL` è vuoto. Il workflow ha `permissions: contents: read`; non è abilitato a committare journal privati su questo repository. Non dichiaro una persistenza DB o feedback durevole.

Le due posizioni legacy (WTI e Heating Oil) non vengono fuse né conteggiate come fill verificati.

## 5. Difetti dimostrati nel forward-outcome tracker

Ho ispezionato `engine/feedback.py` su main `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`.

### Identità contratto insufficiente
- `FIELDS` conserva symbol e timeframe, ma non market type, contract expiry, resolved quote symbol, provider o quote timestamp.
- `_signal_record()` forma l'identità da symbol/direction/timeframe/levels/entry-bar timestamp.
- `update_open_outcomes()` associa le candele tramite `(symbol, timeframe)`.
- Questo non dimostra che le candele forward appartengano allo stesso identico future e alla stessa scadenza del segnale. Senza questi campi, PRAVDA mantiene `ESITO NON VERIFICABILE`.

### Ambiguità SL/TP nella stessa candela
Il codice main controlla `stop_hit` prima di `hit_targets` e marca `STOP` quando una candela OHLC tocca sia SL sia TP. OHLC non rivela l'ordine intrabar. Secondo il protocollo PRAVDA, il caso deve rimanere ambiguo / `ESITO NON VERIFICABILE`, non diventare uno SL cronologicamente provato.

### Più target nella stessa candela
Il codice seleziona `max(hit_targets)`. Se la stessa candela copre più target, il tracker registra il target più alto e il relativo R, benché l'OHLC non identifichi il percorso intrabar o il primo target osservabile. Può sovrastimare il primo target raggiunto.

### Distinzione tra due percorsi di scorecard
La PR #91 modifica `telegram/news_monitor.py` ordinando cronologicamente le osservazioni del NEWS alert scorecard. Non aggiunge l'identità contratto/scadenza al paper forward-outcome tracker in `engine/feedback.py`; i due percorsi non vanno confusi.

Segnalazioni PRAVDA pubblicate:
- [PR #94 — identità mercato/contratto e provenienza quote](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/94#issuecomment-6696417224)
- [PR #97 — SL/TP nella stessa candela: ambiguità](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/97#issuecomment-6696418074)
- [PR #98 — più target nella stessa candela](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/98#issuecomment-6696418723)
- [PR #107 SPUTNIK — provenienza quotazione già segnalata](https://github.com/andreameloni1984-sys/trump-trucker/pull/107#issuecomment-6693183007)

## 6. PR e CI già esistenti

### SPUTNIK
- [PR #144 — persistenza stato fuori da main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN, non draft; ranking test #42297119257 SUCCESS. Non integrata.
- [PR #145 — diagnostica errori quote Yahoo futures](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN, non draft; ranking e Telegram menu tests SUCCESS. Non integrata.
- [PR #146 — alert individuali e calendario economico](https://github.com/andreameloni1984-sys/trump-trucker/pull/146): OPEN, non draft; ranking e item-intelligence tests SUCCESS. Non integrata.
- [PR #143 — falsi domini da short token](https://github.com/andreameloni1984-sys/trump-trucker/pull/143): OPEN, non draft; due suite SUCCESS. Non integrata.
- [PR #107 — provenienza quote negli alert CFD](https://github.com/andreameloni1984-sys/trump-trucker/pull/107): OPEN, non integrata; il run #422700 continua a non esporre ticker runtime/provider/timestamp/age.

### GAGARIN
- [PR #224 — calendario economico e alert eventi](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/224): OPEN, non draft; sei workflow di test SUCCESS. Non integrata.
- [PR #223 — scansione M5 isolata a sette strumenti](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): OPEN/DRAFT; cinque workflow di test SUCCESS. Non integrata.
- [PR #221 — rimozione rotte FX residue](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): OPEN/DRAFT; test integrazione ed execution SUCCESS sul branch. Non integrata; il monitor main mostra ancora due FX ausiliari.
- [PR #175 — gestione webhook attivo nel polling](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): OPEN, non draft; i test sul branch sono verdi, ma il polling main #42289526533 fallisce ancora con 409.
- [PR #91 — NEWS scorecard chronology](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/91): OPEN/DRAFT; i test sul branch sono verdi, ma il cambiamento riguarda `telegram/news_monitor.py`, non la chiave contratto del feedback engine.
- [PR #97](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/97) e [PR #98](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/98): OPEN/DRAFT, non integrate; sono le correzioni già proposte per ambiguità SL/TP e primo target.

Test verdi su branch PR non equivalgono a merge, deploy o comportamento attivo su main.

## 7. Ledger PRAVDA e statistiche

File main: [`reports/pravda-signal-ledger-2026-11-06.csv`](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-06.csv)
- Blob SHA: `0bf31f047b157129bf9329d1727f0078e9082e61`.
- Record dati: 35.
- Firme uniche: 35.
- Duplicati: 0.
- Tipi: 21 historical prediction candidate; 1 legacy paper ticket; 6 watch pre-alert; 6 CFD early setup not executed; 1 watch-board pre-alert non attribuibile.
- Outcome ledger: 28 `ESITO_NON_VERIFICABILE`; 7 `NON_TRADE`.
- Il candidato GOLD #712 e il watch board #3709 erano già presenti; nessun record aggiunto in questo controllo.
- Fill verificati: 0; TP verificati: 0; SL verificati: 0; outcome verificabili: 0.
- Win rate e average R: N/D, campione verificabile nullo.

Le 21 predizioni storiche PENDING non sono trade eseguiti. Il ticket WTI legacy OPEN non prova un fill. I WATCH e gli EARLY_SETUP NOT_EXECUTED non entrano nelle statistiche di performance.

## 8. Fonti consultate e prossimo controllo

Fonti:
- GitHub Actions run e job log: SPUTNIK #42270098789; GAGARIN #42263910777; GAGARIN Telegram Polling #42289526533.
- Branch main e commit di persistenza SPUTNIK #0439dca.
- Ledger PRAVDA e artefatti GAGARIN: `journal.csv`, `paper_trade_log.csv`, `data/paper_open.json`, `position.json`, `commodities_prediction_log.json`, `engine/feedback.py`, `telegram/news_monitor.py`, `.github/workflows/gagarin-monitor.yml`.
- PR e CI sopra elencate.
- Nessun servizio a pagamento; nessun accesso Trading212 dichiarato; Telegram è attestato soltanto tramite API ACK/message_id, non consegna al dispositivo.

Prossimo controllo:
1. Verificare un nuovo run di mercato reale per ciascun bot, distinto da polling, summary e test.
2. Richiedere ticker runtime, mercato, scadenza, provider, timestamp/age della quota per ogni candidato.
3. Conservare candele forward dello stesso identico contratto; stesso-bar SL/TP e più target nello stesso bar restano ambigui senza dati intrabar.
4. Verificare su main la correzione del polling 409, le PR quote-provenance e le PR outcome.
5. Aggiornare il ledger solo per nuove firme uniche e con identità/provenienza sufficienti.

**Perimetro:** audit/documentazione soltanto. Nessun codice bot, strategia, filtro, punteggio o rischio modificato; nessun merge, deploy, rerun o ordine reale; nessuna modifica a Render o segreti. PAPER ONLY.
