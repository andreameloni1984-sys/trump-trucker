# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-06 20:43 UTC (21:43 Europe/Rome)**

## Sintesi

- Ultimo collector SPUTNIK: [run #42270098789](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42270098789), avviato 18:22:24 UTC, SUCCESS. Nessun collector di mercato successivo nelle 100 Actions esaminate.
- Ultimo monitor prezzi GAGARIN: [run #42263910777](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42263910777), avviato 17:41:19 UTC, SUCCESS. Nessun monitor prezzi successivo nelle 100 Actions esaminate.
- L'ultima Action GAGARIN è invece [Telegram Polling #42289526533](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42289526533), 20:34:39 UTC, FAILURE per Telegram API 409. Non è un monitor di mercato.
- Nessun nuovo segnale di mercato da aggiungere al ledger rispetto al precedente audit.
- Ledger: 35 record, 35 firme uniche, zero duplicati.
- Nessun fill, SL o TP verificabile; win rate e average R N/D.
- Nessuna candela successiva dello stesso identico contratto è stata utilizzata: manca la chiave contratto/scadenza e la provenienza completa delle quotazioni.

## 1. Branch e workflow verificati

### Main
- SPUTNIK `main`: `50820b63527f31f8e37ac59cd398f00bc0ee2c25`.
- GAGARIN `main`: `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`.

### Frequenze configurate e continuità effettiva
- SPUTNIK `.github/workflows/trump_tracker.yml`: cron `2-59/5 * * * *` (ogni 5 minuti).
  - Ultimo collector #42270098789: 18:22:24 UTC.
  - Precedente collector #42210907412: 11:31:39 UTC.
  - Gap tra i due avvii: circa 6h50m45s.
  - Età dell'ultimo collector al cut-off: circa 2h21m03s.
  - Telegram polling è separato; #42265633569 è polling, non collector.
- GAGARIN `.github/workflows/gagarin-monitor.yml`: cron `*/15 * * * *` (ogni 15 minuti).
  - Ultimo monitor #42263910777: 17:41:19 UTC.
  - Precedente monitor #42203497432: 10:32:52 UTC.
  - Gap tra i due avvii: circa 7h08m27s.
  - Età dell'ultimo monitor al cut-off: circa 3h02m08s.
  - Nessun monitor prezzi successivo nella lista delle 100 Actions più recenti. Polling, test PR e riepiloghi non sono stati conteggiati come monitor.
- La causa dei gap non è dimostrata; non la attribuisco a filtri orari o a una specifica infrastruttura senza log che lo provino.

## 2. SPUTNIK — candidato GOLD SHORT già presente nel ledger

Run di origine: [#42270098789](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42270098789).

### Identità e cronologia
- Firma PRAVDA: `PRAVDA-SPUTNIK-CFD-RUN42270098789-20261106T182232Z-GOLD-SHORT-4069.3-4071.7536-4066.8465-4064.3929`.
- Messaggi collegati: digest #710, analisi #711, scheda CFD #712. Sono fasi dello stesso candidato, non tre trade.
- Generazione CFD #712: 2026-11-06 18:22:32.111256 UTC.
- ACK API #712: 18:22:32.112773 UTC; round-trip 311 ms. Il log registra anche ACK #710 (377 ms) e #711 (300 ms). Sono risposte API/ID messaggio, non prova di esecuzione né prova autonoma di visualizzazione sul dispositivo.
- Il messaggio #731 compare durante lo step di regression tests prima dell'avvio del collector: è output del test, escluso dal conteggio dei segnali.

### Dati del candidato
- Strumento: GOLD.
- Mapping configurato: `GC=F`; ticker risolto runtime non esposto.
- Mercato: future continuo front-month.
- Scadenza/contratto esatto: UNKNOWN.
- Provider runtime, timestamp quotazione e quote age: NOT_EXPOSED.
- Direzione preliminare: SHORT.
- Analisi #711: tecnica SHORT (5m), momentum 15m -0,020%, nessuna notizia direzionale.
- Scheda CFD #712: tecnica LONG (CONTRASTS), D-L-A LONG (CONTRASTS); quindi discordante dal bias SHORT e anche dall'analisi tecnica del messaggio #711.
- Entry 4069.3; SL 4071.7536; TP1 4066.8465; TP2 4064.3929; ATR 1.6357; score 70.
- Stato: `EARLY_SETUP / NOT_EXECUTED`. La scheda dichiara che il front-month continuo non ha scadenza esatta verificata e che i livelli non devono essere usati per entry/SL/TP.

**Classificazione PRAVDA: NOT_EXECUTED, non trade. ESITO NON VERIFICABILE.** Nessuna candela forward dello stesso ticker/contratto è stata selezionata.

### Fonti e ritardi intelligence
- Feed pubblico: `https://www.trumpstruth.org/feed`.
- Post 43495: pubblicato 12:01:50 UTC, rilevato 18:22:30.541 UTC, ritardo circa 6h20m40s. Il testo usa GOLD in senso metaforico parlando di Super Intelligence/AI, ma è stato classificato METALS; il record indica evento OTHER e NO_ANALOGUE. Falso positivo di dominio già segnalato in PR #143.
- Post 43496: pubblicato 18:05:27 UTC, rilevato 18:22:30.541 UTC, ritardo circa 17m03s; classificato POLITICAL_CAMPAIGN, non fornisce un catalizzatore commodity direzionale.
- Il collector registra 4 findings di scansione e 2 nuovi eventi pubblici; zero filing e zero nuove operazioni documentate.
- SEC: HTTP 403, cooldown 21600 secondi. White House RSS: HTTPError. OGE, WHITE_HOUSE e TRUTH_ARCHIVE riportano anche OSError nelle chiamate del run.
- Handoff GAGARIN disabilitato perché GAGARIN_CLOUD_API_URL/API_KEY non configurati; il log menziona una conferma per un evento, ma nessun ordine è richiesto o inviato.

### Stato persistito
Il file `sputnik_state.json` su main è popolato:
- aggiornato 18:22:30.578530 UTC;
- 500 elementi nella `intelligence_history`;
- `events` vuoto;
- `telegram_active=true`;
- offset Telegram 275590742.
Il commit di persistenza del run è [0439dca9](https://github.com/andreameloni1984-sys/trump-trucker/commit/0439dca9cfa0e349c3cb2237fd4aeb78bd110f00). Lo stato non risulta aggiornato dopo le 18:22 nel materiale consultato.

## 3. GAGARIN — ultimo monitor e watch board

Run di origine: [#42263910777](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42263910777), main `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`.

### Quotazioni nel monitor
Tutte le otto commodity operative risultano YAHOO STALE:
- Oro 602.3 s.
- WTI 603.4 s.
- Brent 609.5 s.
- Grano 608.6 s.
- Mais 615.7 s.
- Argento 613.1 s.
- Soia 601.8 s.
- Rame 602.3 s.

Non sono esposti nel log ticker runtime completo, scadenza del contratto e timestamp puntuale della candela. La ragione fallback riportata è `ALL_PROVIDER_CANDLES_STALE`.

### Watch board
- Argento: LONG, probabilità 59.0, quality 49.5, confidence 32.0, stato PAPER_WATCH.
- Gli altri strumenti commodity sono WATCH senza livelli operativi completi; il log riporta blocchi quali LIVE_DATA_NOT_FRESH, trigger non confermato, setup/direzione non validi e livelli mancanti.
- EUR/USD e GBP/USD sono LIVE via BIQUOTE (94.3 s e 94.8 s) ma esplicitamente `CONTESTO FX — NON OPERATIVO`; non sono trade commodity né segnali operativi.
- Il workflow imposta `GAGARIN_FOREX_ON_DEMAND=0`, mentre il runtime dichiara che EUR/USD e GBP/USD restano ausiliari e li mostra nel contesto. Evidenza segnalata sulla PR #221, senza attribuire loro ingressi.

### Telegram e journal
- Telegram API ha accettato il watch board #3709 alle 17:41:35.207 UTC (436 ms). Il corpo del messaggio non è presente nel log: non attribuisco #3709 con certezza all'Argento o a un altro strumento.
- New feedback signals: 0; new additional live forecasts: 0.
- `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`.
- `journal.csv`: 11 righe del 17 ottobre, tutte con nessun segnale.
- `paper_trade_log.csv`: una posizione WTI legacy del 2026-10-08 (entry 96.24, SL 89.37, TP1 103.11, TP2 106.55), senza provider, contratto/scadenza e prova di fill.
- `data/paper_open.json`: P0001 è la stessa posizione WTI, PAPER ONLY/OPEN; non è un secondo trade e non prova un fill.
- `position.json`: vecchia posizione Heating Oil LONG (HO/USD), aperta il 15 settembre; non c'è prova indipendente di esecuzione.
- `commodities_prediction_log.json`: 981 record, ultimo 2026-09-15T15:45:04.462276Z; record PENDING/WAIT non sono esecuzioni.
- `gagarin_feedback.csv` e `monitor_state.json` non sono presenti su main. Il workflow documenta che la persistenza dei paper journal pubblici è disabilitata in attesa di storage privato D1 verificato.

## 4. Difetto dimostrato nella verifica outcome GAGARIN

File main: `engine/feedback.py`.
- Lo schema del feedback conserva `symbol`, `timeframe`, `data_source`, entry/SL/TP e timestamp della barra.
- Non conserva market type, contract ID/scadenza, provider quote e timestamp/age della quotazione.
- `update_open_outcomes()` abbina gli stati tramite `(symbol, timeframe)` e usa un fallback symbol-only se esiste un solo stato per simbolo.
- La cronologia è correttamente limitata alle candele strettamente successive all'entry bar; se SL e TP sono toccati nella stessa candela, la regola conservativa assegna SL prima.
- Tuttavia, senza identità del contratto, questa correttezza temporale non dimostra che le candele appartengano alla stessa scadenza futures/CFD. Per PRAVDA tali outcome restano non verificabili.

PR #91 (`Resolve Gagarin alert outcomes chronologically`) è ancora OPEN/DRAFT e non integrata su main. Il commento di audit precedente è presente.

## 5. Telegram polling GAGARIN — errore 409 confermato

Run [#42289526533](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42289526533), avviato 20:34:39 UTC:
- token validation: OK;
- Telegram diagnostic: OK;
- `getUpdates`: FAILURE, API error 409 — webhook attivo; polling non consentito in modalità webhook.
- Job #128138981056 fallito allo step `Run polling runner`.
- PR #175 è OPEN e non integrata su main.

Nuova evidenza inviata al reparto tramite commento [PR #175, commento #6695099293](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175#issuecomment-6695099293).

Evidenza sulla presenza residua delle rotte FX/context inviata tramite [PR #221, commento #6695099866](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221#issuecomment-6695099866).

## 6. PR e correzioni esistenti

### SPUTNIK
- [PR #145 — diagnostica errori quote Yahoo futures](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN; test ranking/Telegram menu sul commit PR superati.
- [PR #146 — alert individuali e calendario economico](https://github.com/andreameloni1984-sys/trump-trucker/pull/146): OPEN, non draft; ranking e item-intelligence test superati.
- [PR #143 — falsi domain label da token brevi](https://github.com/andreameloni1984-sys/trump-trucker/pull/143): OPEN; test precedentemente superati, non integrata.
- [PR #144 — persistenza stato](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN; test ranking superato sul commit aggiornato, non integrata.
- [PR #107 — provenienza quote CFD](https://github.com/andreameloni1984-sys/trump-trucker/pull/107): OPEN; la lacuna resta visibile nel run #42270098789.

### GAGARIN
- [PR #224 — calendario economico/event alert](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/224): OPEN, non draft; suite test PR sul commit `388d1867...` superate. Il commento Cloudflare segnala deployment failed: i test verdi non equivalgono a deploy riuscito.
- [PR #223 — scansione M5 a sette strumenti, Argento escluso](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): OPEN/DRAFT; test superati sul commit PR, ma commento Cloudflare segnala deployment failed. Non attiva su main: il monitor main include ancora Argento.
- [PR #221 — rimozione rotte FX residue](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): OPEN/DRAFT, non attiva.
- [PR #222 — rimozione veto sessione](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/222): OPEN/DRAFT, non attiva.
- [PR #219 — rimozione EUR/USD e GBP/USD dall'universo](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219): OPEN, non integrata.
- [PR #175 — conflitto webhook/polling](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): OPEN; errore 409 riprodotto su main.
- [PR #91 — outcome cronologici](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/91): OPEN/DRAFT; chiave contratto/scadenza assente su main.

Nessuna delle PR citate è stata approvata, unita o distribuita da PRAVDA.

## 7. Ledger e statistiche

Ledger: `reports/pravda-signal-ledger-2026-11-06.csv`.
- Blob SHA: `0bf31f047b157129bf9329d1727f0078e9082e61`.
- Record dati: 35.
- Firme uniche: 35.
- Duplicati: 0.
- Ultimo candidato operativo registrato: GOLD SHORT #712, già presente.
- Ultimo record WATCH: board #3709, strumento non attribuibile dal body mancante.
- Nuove firme da aggiungere in questo audit: 0.

Statistiche outcome:
- Fill verificati: 0.
- SL-first verificati: 0.
- TP-first verificati: 0.
- Esiti verificabili su identico contratto: 0.
- Win rate: N/D.
- Average R: N/D.

Le posizioni legacy WTI/Heating Oil e i record PENDING non sono conteggiati come trade eseguiti.

## 8. Fonti consultate e limiti

- GitHub Actions: ultime 100 esecuzioni per repository; job e log completi dei run #42270098789, #42263910777 e #42289526533; test CI delle PR citate.
- GitHub main: workflow SPUTNIK/GAGARIN, `sputnik_state.json`, ledger PRAVDA, GAGARIN journal/paper/prediction artifacts e `engine/feedback.py`.
- Item pubblici SPUTNIK 43495 e 43496 tramite feed archiviato nei log/stato.
- Commenti e metadati delle PR citate.
- Nessun servizio a pagamento usato. Nessun accesso Trading212 dichiarato. L'ACK Telegram non viene presentato come prova di consegna sul dispositivo.

Limiti:
- Nessun provider esterno di prezzi/candele è stato interrogato in questo audit: le identità ticker/contratto/scadenza e i timestamp quote mancano, quindi non sarebbe corretto cercare un proxy spot o un future diverso.
- I journal/feedback privati non sono accessibili su main; i file pubblici mancanti sono indicati sopra.
- Nessun outcome è stato inventato o ricostruito con dati non omogenei.

## 9. Prossimo controllo

1. Verificare un nuovo run di mercato SPUTNIK e GAGARIN; distinguere sempre collector/monitor da polling, summary e PR CI.
2. Controllare che i prezzi delle otto commodity siano freschi e che il ticker runtime, mercato, scadenza e provider siano espliciti.
3. Verificare se PR #145/#146 e PR #221/#223/#224 diventano effettivamente parte di main; non confondere CI con deploy.
4. Verificare la risoluzione del 409 solo dopo un polling scheduled completato senza errore.
5. Mantenere gli outcome GAGARIN non verificabili finché il matching non conserva e confronta l'identità esatta del contratto.
6. Aggiungere record al ledger solo per nuove firme; tenere digest/analisi/CFD collegati come un solo candidato e non promuovere WATCH/PENDING/NOT_EXECUTED a trade.

**Perimetro rispettato:** audit e documentazione soltanto. Nessuna modifica a codice bot, strategia, filtri, punteggi o rischio; nessun merge, deploy o rerun; nessun ordine reale; nessuna modifica a segreti, Render o servizi esterni. PAPER ONLY.
