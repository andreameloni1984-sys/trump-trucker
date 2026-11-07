# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-07 01:31 UTC (02:31 Europe/Rome)**

## Sintesi

- Nessun nuovo monitor di mercato SPUTNIK dopo [run #42311247999](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42311247999), avviato il 2026-11-06 alle 23:20:35 UTC.
- Nessun nuovo monitor prezzi GAGARIN dopo [run #42304574886](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42304574886), avviato il 2026-11-06 alle 22:25:16 UTC.
- Le Actions più recenti non di mercato sono test PR SPUTNIK alle 00:32 UTC e polling Telegram GAGARIN alle 00:16 UTC; non sono state conteggiate come monitor.
- Nessun nuovo segnale di mercato da aggiungere al ledger: 40 record, 40 firme uniche, zero duplicati.
- Nessun fill, TP o SL verificabile. Il campione di operazioni con outcome verificabile resta zero.
- PR GAGARIN #192 è ora OPEN e non draft; aggiunge controlli di identità contratto e ambiguità SL/TP nella stessa candela, ma non è integrata e resta un difetto sulla selezione del target più alto nella stessa candela.
- PR SPUTNIK #147 ha due suite verdi ma resta OPEN e non integrata.
- Nessun codice modificato da PRAVDA; nessun merge, deploy, rerun, ordine reale o modifica a segreti/Render.

## 1. GitHub Actions e continuità

### SPUTNIK
Workflow `.github/workflows/trump_tracker.yml`: cron `2-59/5 * * * *`.
Ultimo collector disponibile:
- [#42311247999](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42311247999)
- evento `schedule`, main, commit eseguito `efe601a7af853660da1eca4d4a512533a9a72550`;
- avvio 2026-11-06 23:20:35 UTC; job completato con SUCCESS;
- nessun collector successivo nelle 100 Actions più recenti al cut-off.
- Gap dal monitor al cut-off: circa 2h10m25s.

I test PR #147 delle 00:32 UTC non sono monitor di mercato.

### GAGARIN
Workflow `.github/workflows/gagarin-monitor.yml`: cron `*/15 * * * *`.
Ultimo monitor:
- [#42304574886](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42304574886)
- evento `schedule`, main, commit `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`;
- avvio 2026-11-06 22:25:16 UTC; job SUCCESS;
- nessun monitor prezzi successivo nelle 100 Actions più recenti.
- Gap dal monitor al cut-off: circa 3h05m44s.

Il polling [#42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549) alle 00:16:15 UTC del 7 novembre è un workflow ausiliario, non un monitor prezzi. Il job fallisce con Telegram API 409: webhook attivo, polling non consentito. Il file workflow su main dichiara cron `*/5 7-21 * * 1-5`, che non coincide con sabato 00:16 UTC. La discrepanza è osservata; la causa (ritardo schedule, trigger o altra condizione) non è determinata.

## 2. SPUTNIK — candidato GOLD #713/#714

Un solo candidato collegato, non due segnali:
- run: #42311247999;
- analisi #713 generata alle 23:20:43.370895 UTC;
- scheda CFD #714 accettata dall'API Telegram alle 23:20:43.3721907 UTC; round-trip dichiarato 383 ms;
- API ACK non dimostra consegna al dispositivo né esecuzione.

Contenuto:
- strumento: GOLD;
- mapping configurato: GC=F; ticker effettivo runtime non esposto;
- mercato dichiarato: future continuo front-month;
- scadenza esatta: UNKNOWN;
- provider runtime, timestamp quotazione e quote age: NOT_EXPOSED;
- NARWHAL: NOT_CONFIGURED (chiave non presente nell'ambiente del run);
- messaggio #713: bias preliminare NEUTRAL, tecnica UNAVAILABLE, NO_DIRECTIONAL_NEWS;
- messaggio #714: bias LONG, tecnica LONG/TECHNICAL_ONLY, D-L-A NEUTRAL/NO_DIRECTION;
- score/priorità 70; nessun entry, SL, TP o ATR emesso;
- stato EARLY_BIAS / NOT_EXECUTED.

La discrepanza fra analisi #713 e scheda #714 è esplicita. Il messaggio #714 avverte che il future continuo non ha scadenza esatta e che i livelli non sono utilizzabili. Nessun trade e nessun outcome di mercato da valutare.

Il log di produzione riporta SEC HTTP 403, White House RSS HTTPError, zero filing, zero nuove operazioni e una correlazione pubblica. Il record TRUTH_ARCHIVE associato nello stato è una pagina archivio di livello homepage: titolo e data di pubblicazione vuoti, dominio POLITICAL_CAMPAIGN, testo che incorpora più post. `findings=1` non dimostra un singolo catalizzatore di mercato individuale con timestamp verificabile.

### Stato persistente SPUTNIK

Il commit [f503a7b](https://github.com/andreameloni1984-sys/trump-trucker/commit/f503a7b507868dcfb5bf4f76ca81aadbf906372e) ha aggiornato `sputnik_state.json` alle 23:20:41.952 UTC.
Il blob SHA corrente è `7970e96759412b85a1c6d1f12d404166281884a0`, dimensione 1.395.898 byte. Lettura tramite blob (il wrapper fetch_file restituisce contenuto vuoto su questo file grande):
- 500 elementi in `intelligence_history`;
- `events` vuoto;
- offset Telegram presente;
- `telegram_active=true`.

Rettifica metodologica: il precedente risultato vuoto di fetch_file era un limite/artefatto di lettura, non prova che il file Git fosse vuoto. Il blob conferma i 500 elementi. Non significa però 500 catalizzatori individuali verificati: la cronologia include snapshot e pagine archivio.

## 3. GAGARIN — quotazioni e classificazione del monitor #42304574886

Tutte le otto commodity operative sono stale secondo il log. Provider selezionato: Yahoo. Timestamp esatto della quotazione, ticker risolto, mercato e scadenza non sono esposti.

| Strumento | Provider | Quote age | Classificazione |
|---|---|---:|---|
| Brent | Yahoo | 1547,5 s | nessun setup valido |
| WTI | Yahoo | 1533,2 s | SHORT WATCH bloccato |
| Soia | Yahoo | 11133,1 s | nessuna direzione |
| Oro | Yahoo | 1530,7 s | nessuna direzione |
| Grano | Yahoo | 11132,7 s | nessuna direzione |
| Mais | Yahoo | 11135,9 s | LONG WATCH bloccato |
| Argento | Yahoo | 1531,7 s | LONG WATCH bloccato |
| Rame | Yahoo | 1542,9 s | nessuna direzione |

Candidati visibili:
- WTI SHORT: probability 66, quality 57,5, confidence 37; stale, trigger non confermato e mismatch direzionale.
- Mais LONG: 63 / 52,5 / 35; stale, trigger non confermato, mismatch e RR_FAIL.
- Argento LONG: 59 / 49,5 / 32; stale, trigger non confermato, mismatch, RR1_FAIL e confidence fail.

Nessuno ha entry, SL, TP o ATR operativo completo. Sono WATCH, non trade.

### Rettifica FX
Il log mostra EUR/USD e GBP/USD come contesto ausiliario non operativo:
- GBP/USD: Yahoo LIVE, age 5,5 s; BiQuote STALE, age 1833 s.
- EUR/USD: Yahoo LIVE, age 4,8 s; BiQuote STALE, age 1833 s.

Quindi il precedente rapporto che descriveva BiQuote come provider LIVE per questi due contesti era errato: nel run esaminato la quotazione LIVE proviene da Yahoo. Il workflow imposta `GAGARIN_FOREX_ON_DEMAND=0`, ma il log dichiara che EUR/USD e GBP/USD restano strumenti ausiliari analizzati nelle rispettive finestre; sono esplicitamente non operativi.

### Telegram e feedback
- Watch board message_id 3710 generato alle 22:25:29.422938 UTC e accettato dall'API alle 22:25:33.877068 UTC (358 ms).
- Il corpo del messaggio non è conservato; non è possibile associare in modo certo il board a uno specifico candidato.
- `Recorded entries: 0`; `Updated open outcomes: 0`; `New feedback signals: 0`; `New additional live forecasts: 0`; `signals=0 open=0 closed=0`.
- `DATABASE_URL` è vuoto nel run; il workflow dichiara che i journal paper privati non vengono committati e che la persistenza attende storage privato D1 verificato.
- Il polling #42317191549 fallisce esplicitamente con errore 409 webhook attivo. PR #175 è ancora OPEN/non merged.

## 4. Journal e artefatti GAGARIN

- `journal.csv`: 11 righe, tutte 2026-10-17 e con esito “nessun segnale”.
- `paper_trade_log.csv`: un WTI LONG legacy del 2026-10-08, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55; provider, contratto, scadenza e fill non documentati.
- `data/paper_open.json`: stessa posizione WTI P0001, `paper_only=true`; non è un secondo trade.
- `position.json`: Heating Oil LONG aperto nel record 2026-09-15; nessuna prova indipendente di fill.
- `commodities_prediction_log.json`: 981 record; ultimo `created_at` 2026-09-15T15:45:04.462276Z; record PENDING non equivalgono a trade.
- `gagarin_feedback.csv`: non presente su main; feedback privato non accessibile in questo audit.

Non è stato attribuito alcun outcome a WTI P0001 o Heating Oil: mancano prova di esecuzione, identità del contratto e sequenza di candele successive verificabile.

## 5. Motore outcome e PR #192

Su main, `engine/feedback.py`:
- abbina gli stati per simbolo e timeframe;
- non verifica provider/ticker di quotazione, mercato e scadenza del contratto;
- se SL e TP sono nella stessa candela, assegna STOP;
- se più TP sono toccati nella stessa candela, usa `idx = max(hit_targets)`, senza prova dell'ordine intrabar.

PR [#192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) è ora OPEN, non draft, non merged; head `295dba4b074e564a4c11aa3fca136a8e4360672c`. Aggiunge:
- quote provider/timestamp/age/ticker, market type, contract month/expiry, ATR e signal status;
- identità segnale estesa;
- verifica di ticker, mercato e contratto prima dell'abbinamento;
- `ESITO NON VERIFICABILE` se manca l'identità futures o se SL e TP cadono nella stessa candela.

Sei suite CI sul commit head risultano SUCCESS, eseguite il 2026-11-05 alle 06:34:25 UTC: Execution Layer, NEWS alert, Public Event Brain, trade-plan, PAPER e GAGARIN tests. Questi test sono sul branch PR, non su main.

Il base SHA della PR è `c93906a2a4b28d60fd58c600b51cd3c05929f89d`, mentre main corrente è `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`; il confronto GitHub mostra main avanti di 3 commit. PR #192 non è quindi aggiornata all'attuale main e non dimostra che la correzione sia in produzione.

Difetto residuo nel branch PR: `idx = max(hit_targets)` sceglie ancora il TP più alto quando più target sono toccati nella stessa candela. A risoluzione OHLC l'ordine intrabar è ignoto; il target specifico non è verificabile. Il commento PRAVDA già esistente [#6699958308](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6699958308) documenta questo punto; non è stato duplicato.

## 6. PR e correzioni esistenti

### SPUTNIK
- PR [#147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147), “Keep SPUTNIK independent: remove GAGARIN handoff”: OPEN, non draft, non merged. Due suite sul head `668a17aaeaead4cab403653e1288c22c58343f54` SUCCESS alle 00:32:21 UTC ([ranking](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42318832066), [item intelligence](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42318832108)). Non attiva su main.
- PR #145 quote provenance, #144 state off-main, #143 token/domain labels e altre correzioni restano aperte; nessuna è stata dichiarata integrata in questo audit.

### GAGARIN
- PR #192 exact contract/outcome: OPEN, non draft, test branch verdi, base dietro main.
- PR #175 webhook/polling: OPEN, non merged; il run main continua a fallire 409.
- PR #94/#97/#98 outcome coverage/ambiguity/target ordering: ancora aperte/draft secondo l'elenco PR corrente.

## 7. Ledger e statistiche

File `reports/pravda-signal-ledger-2026-11-06.csv`, blob SHA `ed76e1f4af5ed2ac586244527c99460a051345b2`.
CSV analizzato con parsing corretto dei campi quotati:
- record dati: 40;
- firme `audit_signature` uniche: 40;
- duplicati: 0;
- tipi: 21 historical_prediction_candidate; 1 legacy_paper_ticket; 6 watch_pre_alert; 6 cfd_early_setup_not_executed; 2 watch_board_pre_alert_unresolved; 1 cfd_early_bias_not_executed; 3 watch_candidate_blocked;
- outcome label: 29 ESITO_NON_VERIFICABILE e 11 NON_TRADE.

Queste etichette non sono statistiche di trade: includono candidati non eseguiti e record legacy. Fill verificati 0; TP verificati 0; SL verificati 0; operazioni con outcome verificabile 0. Win rate e average R: N/D.

Nuovi record da aggiungere: 0. Il candidato SPUTNIK #713/#714 e i WATCH GAGARIN del run #42304574886 sono già rappresentati nel ledger. Il board #3710 è registrato come non attribuibile, senza duplicare i singoli candidati.

## 8. Fonti consultate e lacune

Fonti:
- GitHub Actions e job logs: SPUTNIK #42311247999; GAGARIN #42304574886; GAGARIN Telegram Polling #42317191549; SPUTNIK PR tests #42318832066/#42318832108.
- Repository main e workflow `trump_tracker.yml`, `gagarin-monitor.yml`, `telegram-polling.yml`.
- SPUTNIK `sputnik_state.json` tramite Git blob; PR #147 e relativo CI.
- GAGARIN `journal.csv`, `paper_trade_log.csv`, `data/paper_open.json`, `position.json`, `commodities_prediction_log.json`, `engine/feedback.py`, PR #192 e CI.
- Ledger PRAVDA, 40 record.

Lacune:
1. Nessun nuovo monitor mercato dopo gli orari indicati.
2. GAGARIN non espone timestamp quote, ticker risolto e scadenza dei futures nel log del monitor.
3. SPUTNIK non espone provider/timestamp/age della quotazione runtime e usa un continuo front-month senza scadenza esatta.
4. Nessuna candela successiva dello stesso identico contratto disponibile per i candidati recenti.
5. Journal/feedback GAGARIN privati non accessibili; DATABASE_URL vuoto nel run.
6. API ACK Telegram non prova consegna al dispositivo.
7. Nessuna prova di accesso Trading212.

## 9. Prossimo controllo

1. Verificare un nuovo collector SPUTNIK e un nuovo monitor GAGARIN, confrontando run, commit effettivo e cadenza.
2. Per ogni quotazione GAGARIN acquisire timestamp, ticker effettivo, provider, mercato e scadenza; finché stale, mantenere il candidato non operativo.
3. Verificare che PR #192 sia aggiornata sul main corrente e che il caso multi-TP nella stessa candela non venga promosso al target più alto senza prova intrabar.
4. Verificare la risoluzione del 409 Telegram e la discrepanza fra schedule event 00:16 UTC e cron dichiarato.
5. Aggiungere record solo per nuove firme; valutare outcome esclusivamente con candele successive dello stesso ticker/mercato/contratto.

**Perimetro:** audit e documentazione soltanto. Nessuna modifica a codice, strategia, filtri, punteggi o rischio; nessun merge, deploy, rerun, ordine reale, modifica di segreti o Render. PAPER ONLY.
