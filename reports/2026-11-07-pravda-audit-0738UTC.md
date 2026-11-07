# PRAVDA — Audit indipendente SPUTNIK / GAGARIN

**Controllo:** 2026-11-07 07:38:39 UTC (08:38:39 Europe/Rome)  
**Perimetro:** GitHub Actions e log integrali, segnali/messaggi, ledger PRAVDA, journal e prediction log pubblici, feedback engine su main e branch PR, stato PR/CI e commenti Cloudflare. **PAPER ONLY**.

## Sintesi esecutiva

- Nessuna nuova scansione di mercato su `main` dopo SPUTNIK run **#42331705890** alle 02:57:24 UTC e GAGARIN run **#42328183997** alle 02:13:56 UTC. Alle 07:38:39 UTC i gap sono **4h41m15s SPUTNIK** e **5h24m43s GAGARIN**, contro cron ogni 5 e 15 minuti.
- Le nuove Actions GAGARIN delle 07:07 UTC sono test su PR #232, non scansioni di mercato.
- SPUTNIK ha ripetuto GOLD #715/#716: bias tecnico LONG ma D-L-A NEUTRAL, nessun nuovo finding, nessun livello operativo e `NOT_EXECUTED`.
- GAGARIN ha registrato tre WATCH direzionali nel monitor di sabato: WTI SHORT, Mais LONG, Argento LONG. Tutte le otto commodity erano `MARKET_CLOSED`; nessuna entry/SL/TP/ATR e nessun fill.
- Ledger del 7 novembre: **45 record, 45 firme uniche, zero duplicati**. Nessun nuovo segnale da aggiungere; ledger invariato.
- **0 fill verificati, 0 SL/TP verificati, win rate e average R N/D.** Nessun campione di trade con outcome verificabile.
- Nuova anomalia di pipeline: Cloudflare ha riportato un **build fallito del servizio production `telegram-github-bridge` anche sulla PR draft #232**, commit `638792c8`, alle 07:14 UTC. È il secondo build production fallito osservato su una draft PR, dopo #231. PRAVDA non ha avviato né autorizzato questi build.
- PR #232 introduce una barriera prudente per i comandi Trading 212: quote manuali CFD isolate, nessun confronto con futures Yahoo/BiQuote, nessun livello senza candele CFD dello stesso contratto. È ancora draft e non attiva su main.

## 1. GitHub Actions e cron

### SPUTNIK
- Monitor: [run #42331705890](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42331705890), job #128279494938, SUCCESS, creato 02:57:24 UTC; job 02:57:26–02:57:36 UTC.
- Il job ha fatto checkout di SHA `41fb6081c649f28378d2fe0dfed8aa18cffe9dff`. La main corrente è avanzata successivamente con commit documentali PRAVDA; nessun nuovo run di produzione ha testato questi commit.
- Cron main: `2-59/5 * * * *`.
- Polling Telegram separato: [run #42329017675](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42329017675), SUCCESS, 02:23:33 UTC; log: `Pending updates: 0`. Non è una scansione di mercato né prova di consegna di messaggi al dispositivo.
- Nessun evento schedule successivo del monitor SPUTNIK nella lista interrogata.

### GAGARIN
- Monitor: [run #42328183997](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42328183997), job #128268295697, SUCCESS, creato 02:13:56 UTC; job 02:14:00–02:14:16 UTC.
- Checkout SHA/main corrente: `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`.
- Cron main: `*/15 * * * *`; la proposta di offset #225 è ancora draft e non è attiva.
- Polling: [run #42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549), FAILURE, 00:16:15 UTC, job #128232586109. Token presente e diagnostica bot OK; `getUpdates` fallisce con Telegram API 409: `webhook is active; polling cannot run while webhook mode is enabled`.
- Il run di polling è etichettato `event=schedule` alle 00:16 UTC di sabato, mentre [telegram-polling.yml](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/telegram-polling.yml) dichiara `*/5 7-21 * * 1-5`. Discrepanza dei metadati confermata; causa non dimostrata.
- Nessun evento schedule successivo del monitor GAGARIN nella lista interrogata.

## 2. SPUTNIK — messaggi #715/#716

Produzione del job #128279494938:
- Collector avviato alle 02:57:29.720 UTC.
- SEC CIK 0001849635: HTTP 403; cooldown registrato per 21.600 secondi; `filings=0`.
- White House RSS `https://www.whitehouse.gov/feed/`: HTTPError.
- Scansione intelligence: 1.226 ms, `findings=0`.
- `GAGARIN forwarding=0ms`; nessun handoff di produzione.
- Le numerose righe `OSError` per WHITE_HOUSE/TRUTH_ARCHIVE/OGE e message_id=731 appartengono ai test unitari eseguiti prima del collector, non alla produzione.

Messaggi effettivi:
- **#715**: GOLD; bias preliminare NEUTRAL; priorità/score 70; `NO_DIRECTIONAL_NEWS`; WATCH.
- **#716**: GOLD; bias CFD LONG solo tecnico; D-L-A NEUTRAL / NO_DIRECTION (NOT_ASSESSED); `TRADE PAPER: NOT_EXECUTED`. Entry/SL/TP/ATR omessi perché manca una quotazione futures fresca o ATR valido.
- Telegram API acceptance: #715 483 ms, #716 401 ms. L'ACK API non dimostra visualizzazione sul dispositivo né esecuzione.
- Il testo dichiara “front-month continuo”, ma avverte che scadenza esatta e indipendenza upstream non sono verificate. `GC=F` è mapping configurato, non ticker runtime/contratto identificato. Provider e timestamp della quotazione non esposti.

**Classificazione PRAVDA:** ripetizione del precedente candidato #713/#714, non nuovo catalizzatore e non trade. Nessun outcome finanziario valutabile.

### Stato persistente
Il file [sputnik_state.json](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/sputnik_state.json) esiste su main (blob SHA osservato `d578bee29e0eeafea3cad161263a5e012dd50634`), ma la lettura corrente non ha restituito il contenuto testuale. La precedente verifica dei 500 elementi non viene quindi ripetuta né certificata in questo controllo.

## 3. GAGARIN — run #42328183997

### Quotazioni e stato mercato
Tutte le otto commodity sono `MARKET_CLOSED`, provider YAHOO:

| Strumento | Età quota al monitor |
|---|---:|
| Brent | 15.267,6 s |
| WTI | 15.253,4 s |
| Soia | 24.853,0 s |
| Oro | 15.251,0 s |
| Grano | 24.852,7 s |
| Mais | 24.855,8 s |
| Argento | 15.252,1 s |
| Rame | 15.263,2 s |

Sabato e stato mercato spiegano l'assenza di quotazioni correnti; l'età stale da sola non dimostra un guasto del provider. Ticker runtime, market type, scadenza e timestamp individuale della quotazione non sono esposti nel riepilogo.

EUR/USD e GBP/USD appaiono solo come contesto non operativo; il workflow main imposta `GAGARIN_FOREX_ON_DEMAND=0`.

### Classifica del monitor
- Brent: nessuna direzione, 58/40/25.
- WTI: SHORT, probabilità 66, quality 57,5, confidence 37.
- Soia: nessuna direzione, 50/30/15.
- Oro: nessuna direzione, 50/30/15.
- Grano: nessuna direzione, 38/15/5.
- Mais: LONG, 63/52,5/35.
- Argento: LONG, 59/49,5/32.
- Rame: nessuna direzione, 50/30/15.

Le righe sono `PAPER_WATCH`; nessuna ha entry, SL, TP o ATR operativi. WTI/Mais/Argento hanno trigger non confermato e mismatch direzionale; Mais ha anche RR_FAIL, Argento RR1_FAIL e CONFIDENCE_FAIL.

Timestamp classificazioni:
- WTI SHORT: 02:14:13.6534379 UTC.
- Mais LONG: 02:14:13.6541730 UTC.
- Argento LONG: 02:14:13.6543040 UTC.

Le tre righe hanno `sent_at` e `telegram_message_id` vuoti: non risultano alert individuali.

Board #3711: Telegram API accepted alle 02:14:13.6555025 UTC, 472 ms. Il corpo non è conservato, quindi non viene attribuito a WTI/Mais/Argento e non prova la consegna al dispositivo.

Riepilogo del job:
- `Recorded entries: 0`
- `New feedback signals: 0`
- `New additional live forecasts: 0`
- `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D`

### Journal e feedback pubblici
- [journal.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/journal.csv): 11 righe del 17 ottobre, tutte “nessun segnale”.
- [paper_trade_log.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/paper_trade_log.csv): un WTI LONG `LEGACY_IMPORT`, entry 96.24, stop 89.37, TP1 103.11, TP2 106.55; nota “chiusura spot 6 ottobre; nessun esito”. Non espone provider, ticker di esecuzione, mercato/contratto, scadenza, ATR, signal_id o prova di fill.
- [position.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/position.json): vecchia posizione Heating Oil LONG del 15 settembre; nessuna prova indipendente di fill.
- `paper_open.json`: 404/assente.
- `gagarin_feedback.csv`: 404/assente.
- [commodities_prediction_log.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities_prediction_log.json): 981 record dal 10 al 15 settembre; 945 PENDING, 36 NEUTRALE; `operational_signal`: 960 WAIT, 15 LONG e 6 campi assenti. L'ultimo record è Benzina RBOB, `action=COMPRA ORA` ma `operational_signal=WAIT`, `status=PENDING`: non è prova di trade o fill.
- Il run mostra `DATABASE_URL` vuoto. [gagarin-monitor.yml](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml) dichiara i journal come dati privati e la persistenza sospesa finché D1 privato non sia distribuito/verificato. Il backend durevole non è dimostrato.

## 4. Motore outcome — main vs PR #192

Su main, [engine/feedback.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py):
- fingerprint basato su simbolo/direzione/timeframe/livelli/bar timestamp; non include provider, ticker effettivo, market type o scadenza;
- matching delle candele per simbolo e timeframe, senza identità completa del contratto;
- se SL e TP sono entrambi toccati nella stessa candela, il codice assegna STOP invece di `ESITO NON VERIFICABILE`;
- se più TP sono toccati nella stessa candela, usa `idx=max(hit_targets)` e attribuisce il target più alto senza prova intrabar.

[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) aggiunge quote provider/ticker/market/contract month/expiry alla firma, controlla la corrispondenza di mercato/contratto e marca SL+TP nella stessa candela come `ESITO NON VERIFICABILE`. Ma il branch mantiene `idx=max(hit_targets)` per più target toccati nella stessa candela: l'ordine intrabar resta indimostrato. Compare current main SHA `fba34bef...` vs head `295dba4b...`: **6 commit ahead / 3 behind, diverged**. PR aperta, non integrata; i test sul branch non certificano main.

## 5. PR, CI e deployment

### SPUTNIK
- [PR #148](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN, non integrata; due suite di ranking/item-intelligence SUCCESS alle 04:24 UTC; blocca raccomandazioni ripetute senza nuovo catalizzatore.
- [PR #147](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): OPEN, non integrata; test di indipendenza da GAGARIN superati.
- [PR #145](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN; provenienza quotazioni e diagnostica errori Yahoo non attive su main.

### GAGARIN
- [PR #232](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/232): DRAFT/OPEN, head `638792c8...`, base main `fba34bef...`, 4 commit ahead / 0 behind. Sei workflow di test PR alle 07:07 UTC risultano SUCCESS. Il diff isola i comandi Trading 212: /aggressivo212 e /soft212 fail closed senza feed CFD verificato; /prezzo212 accetta solo bid/ask manuali e li etichetta CFD, senza confrontarli con futures Yahoo/BiQuote e senza livelli. Non dichiara API/account access. **Non è attiva su main.**
- [PR #204](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/204): DRAFT/OPEN, separazione CFD manuale/futures; 10 ahead / 1 behind rispetto a main.
- [PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, 6 ahead / 3 behind; fix contratto/outcome incompleto come sopra.
- [PR #175](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): OPEN, non integrata; il polling main continua a fallire 409.
- [PR #223](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/223): DRAFT; M5 osservativo su sette strumenti con Argento escluso solo da quel monitor; nessun run live dimostrato e nessun entry/journal/ordine.
- [PR #225](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225): DRAFT; propone cron 7/22/37/52 ma main resta `*/15`.
- [PR #231](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/231): DRAFT; build Cloudflare production fallito sul commit `047abbc8` alle 06:50 UTC.
- PR #231 include Argento nel full universe e il monitor main lo ha classificato WATCH. La richiesta precedente di escludere Silver dalla scansione completa non risulta applicata; PR #223 lo esclude solo dalla scansione M5 separata.

### Cloudflare Git integration
- PR #231: commento Cloudflare #6703548421, `telegram-github-bridge/production`, Deployment failed, commit `047abbc8`, 06:50 UTC.
- PR #232: commento Cloudflare #6703756210, stesso servizio/target production, Deployment failed, commit `638792c8`, 07:14 UTC.
- Sono due build falliti osservati su branch draft. Non sono prova di deploy riuscito, ma dimostrano che la Git integration sta avviando build verso un target chiamato production dai branch PR.
- PRAVDA ha aggiunto il commento di audit [#6704036650](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/232#issuecomment-6704036650), chiedendo di verificare le regole branch/target. PRAVDA non ha avviato, approvato o eseguito alcun build/deploy e non ha accesso al pannello Cloudflare.

## 6. Ledger PRAVDA

CSV main: [pravda-signal-ledger-2026-11-07.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-07.csv), blob SHA `9c58b42b70c7aaf92a161b553c9eee8c1f2be52a`, 39.662 byte.

Parsing CSV completo:
- **45 record; 45 firme uniche; 0 duplicati.**
- Tipi: 21 historical prediction candidates; 1 legacy paper ticket; 6 watch pre-alert; 6 CFD early setup not executed; 1 CFD early bias not executed; 1 CFD early bias repeat not executed; 3 watch-board pre-alert unresolved; 6 watch candidates blocked.
- Outcome ledger: 29 `ESITO_NON_VERIFICABILE`, 16 `NON_TRADE`.
- Fill verificati: 0; SL/TP verificati: 0; win rate e average R: N/D.
- Campi vuoti/NOT_RECORDED/NOT_EXPOSED: sent_at 29; ticker 18; market_type 36; contract_expiry 37; provider 33; quote_timestamp_utc 44; entry 17; SL 17; TP1 17; ATR 33. Molte righe sono WATCH/NOT_EXECUTED/legacy, quindi i livelli mancanti non sono fill omessi: sono lacune di tracciabilità per record type.

**Rettifica di qualità del report precedente:** il ricalcolo diretto del CSV con parsing completo e contando anche `NOT_EXPOSED`/`NOT_RECORDED` come mancanti produce i conteggi sopra; i conteggi di completezza riportati nel precedente audit erano sottostimati. Il ledger non è stato modificato.

Nessuna nuova firma da aggiungere: #715/#716, board #3711 e i tre WATCH sono già registrati. Nessun outcome è stato ricostruito da spot/futures o da scadenze diverse.

## 7. Fonti e prossimo controllo

Fonti consultate:
- Actions/log: SPUTNIK #42331705890 e polling #42329017675; GAGARIN #42328183997 e polling #42317191549.
- File main: `trump_tracker.yml`, `gagarin-monitor.yml`, `telegram-polling.yml`, `engine/feedback.py`, `journal.csv`, `paper_trade_log.csv`, `position.json`, `commodities_prediction_log.json`, ledger PRAVDA.
- PR/CI: SPUTNIK #145/#147/#148; GAGARIN #175/#192/#204/#223/#225/#231/#232; commenti Cloudflare e PRAVDA.

Prossimo controllo:
1. verificare la prima nuova scansione schedule su main e misurare il gap reale;
2. alla riapertura dei mercati, verificare quote fresche, ticker runtime, timestamp, market type e scadenza per ogni strumento;
3. verificare l'integrazione su main delle correzioni exact-contract/outcome e webhook;
4. verificare il journal solo quando un backend durevole sia realmente configurato e il run ne dimostri l'uso;
5. controllare che i branch draft non avviino build sul target Cloudflare production;
6. verificare il perimetro Silver: full monitor main vs M5 observation-only.

**PAPER ONLY.** Nessun ordine reale, nessun merge, nessun deploy o rerun avviato da PRAVDA; nessuna modifica a codice, strategia, filtri, punteggi, rischio, segreti, Render o account broker. Nessun accesso Trading 212 dichiarato.
