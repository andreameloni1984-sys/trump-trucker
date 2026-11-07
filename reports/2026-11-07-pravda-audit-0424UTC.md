# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Data controllo:** 2026-11-07 04:24 UTC (05:24 Europe/Rome)  
**Perimetro:** repository pubblici, GitHub Actions, log dei job, ledger e artefatti pubblici. PAPER ONLY.

## Sintesi esecutiva

- Nessuna nuova scansione di mercato risulta dopo SPUTNIK run #42331705890 (02:57:24 UTC) e GAGARIN run #42328183997 (02:13:56 UTC), fino al controllo delle 04:24 UTC.
- SPUTNIK ha inviato due messaggi API-accepted sullo stesso candidato GOLD (#715 analisi e #716 scheda CFD): nessun catalizzatore nuovo nel run, nessun prezzo futures fresco, nessun livello operativo. Il secondo messaggio è LONG tecnico/CFD, ma D-L-A è NEUTRAL e lo stato è NOT_EXECUTED.
- GAGARIN ha classificato WTI SHORT, Mais LONG e Argento LONG come PAPER_WATCH; tutti gli otto mercati commodity erano MARKET_CLOSED e le quotazioni Yahoo avevano 4h14m–6h54m di anzianità. Nessuna entrata e nessun outcome aggiornato.
- PR #148 (SPUTNIK) e PR #225 (GAGARIN) hanno test superati, ma sono ancora aperte; #225 è draft. Nessuna delle due modifiche è attiva su main.
- Il ledger giornaliero resta a 45 record, 45 firme uniche e zero duplicati. Tutti i candidati/notification ID dei due run esaminati erano già presenti: nessuna riga nuova necessaria.

## 1. Repository e revisioni esaminate

| Repository | HEAD main al controllo | Ultimo monitor mercato osservato |
|---|---|---|
| SPUTNIK — `andreameloni1984-sys/trump-trucker` | `5fecc13fcac2784f9e3e98bb20fa69497d6a20b4` | #42331705890, 2026-11-07 02:57:24 UTC |
| GAGARIN — `andreameloni1984-sys/commodity-news-scanner` | `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c` | #42328183997, 2026-11-07 02:13:56 UTC |

Fonti:
- [SPUTNIK workflow main](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/trump_tracker.yml)
- [GAGARIN workflow main](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml)
- [SPUTNIK run #42331705890](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42331705890)
- [GAGARIN run #42328183997](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42328183997)

## 2. GitHub Actions: continuità

### SPUTNIK
Il workflow main dichiara cron `2-59/5 * * * *` (cadenza ogni 5 minuti, offset al minuto 2). L'ultimo run di mercato osservato è #42331705890 alle 02:57:24 UTC. Alle 04:24 UTC non risultano run schedule successivi: gap osservato circa **1h26m42s**, incompatibile con la cadenza dichiarata. Il run Telegram polling #42329017675 alle 02:23:33 UTC è un workflow separato e non è una scansione di mercato.

Non è dimostrata la causa del gap: non viene attribuito automaticamente a un filtro orario.

### GAGARIN
Il workflow main dichiara ancora `*/15 * * * *`. L'ultimo monitor è #42328183997 alle 02:13:56 UTC; nessun monitor schedule successivo risulta fino alle 04:24 UTC: gap circa **2h10m10s**. Il run Telegram polling #42317191549 alle 00:16:15 UTC è fallito; non risultano successivi run polling main nel periodo controllato.

La PR #225 propone `7,22,37,52 * * * *`, mantenendo l'intervallo di 15 minuti e spostando gli avvii lontano dal confine dell'ora. Il test di esecuzione #42337488636 è SUCCESS, ma la PR è ancora draft e main conserva `*/15`: nessuna prova runtime della correzione.

## 3. SPUTNIK — evidenza del run #42331705890

Job log: [run #42331705890](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42331705890), job `sputnik` #128279494938.

### Risultato della scansione produttiva
Dopo l'avvio del run alle 02:57:29.812865 UTC, il log produttivo riporta:
- SEC CIK 0001849635: HTTP 403, cooldown di 21.600 secondi;
- SEC filings: 0;
- White House RSS: HTTPError;
- public intelligence scan: 1.226 ms, findings=0;
- nuove operazioni documentate: 0;
- nuove correlazioni da fonti pubbliche: 0;
- GAGARIN forwarding: 0 ms; URL/API key di handoff vuoti nel runtime;
- notizia: `NO_DIRECTIONAL_NEWS`.

Le righe `OSError`, il messaggio di conferma GAGARIN e il message_id=731 che compaiono **prima** di `SPUTNIK: run started` appartengono alla suite di regressione/mocking del job e non sono stati conteggiati come eventi produttivi.

### Messaggi reali del run
- **#715**, generato alle 02:57:32.776935 UTC e API-accepted alle 02:57:32.7768518Z (483 ms): GOLD, bias preliminare NEUTRAL, priorità 70/100, tecnica UNAVAILABLE (5m), NO_DIRECTIONAL_NEWS, decisione WATCH. Nessun entry/SL/TP.
- **#716**, generato alle 02:57:32.7769354 UTC e API-accepted alle 02:57:32.7788127Z (401 ms): GOLD, bias LONG, tecnica LONG (TECHNICAL_ONLY), D-L-A NEUTRAL/NO_DIRECTION, EARLY_BIAS, score 70, **TRADE PAPER: NOT_EXECUTED**. Entry, SL, TP e ATR omessi perché non erano disponibili quotazione futures fresca e ATR valido. NARWHAL NOT_CONFIGURED. Il log dichiara front-month continuo, ma scadenza esatta e indipendenza upstream non verificate.

L'ACK API conferma l'accettazione da Telegram, non la visualizzazione sul dispositivo e non un'esecuzione. I messaggi #715/#716 costituiscono un'unica coppia informativa sul candidato GOLD, non due trade. È una ripetizione della precedente ipotesi GOLD, senza nuovo finding pubblico nel run.

### Stato persistente
Il blob `sputnik_state.json` verificato tramite Git blob è di 1.395.898 byte e contiene:
- 500 elementi in `intelligence_history`;
- 0 eventi attivi;
- aggiornamento `2026-11-07T02:57:31.194056Z`;
- Telegram update offset 275590742;
- fonti nella cronologia: PUBLIC_RSS 465, TRUTH_ARCHIVE 27, WHITE_HOUSE 5, OGE 3.

I 500 elementi includono snapshot/pagine archivio: non sono 500 catalizzatori individuali verificati. La persistenza è dimostrata; non è dimostrata la freschezza dei catalizzatori nel run corrente.

### Correzioni in revisione
- [PR #148 — stop a raccomandazioni ripetute senza nuovo catalizzatore](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN, non draft, 2 commit, 2 suite (ranking e item intelligence) SUCCESS; base aggiornata a main, non integrata. Il gate richiede un nuovo item RSS individuale, datato e con permalink prima di generare la coppia raccomandazione/CFD. È coerente con il difetto osservato nel run #42331705890.
- [PR #147 — rimozione handoff GAGARIN](https://github.com/andreameloni1984-sys/trump-trucker/pull/147): ancora OPEN. Il workflow main continua a dichiarare le variabili GAGARIN_CLOUD_API_URL/API_KEY; nel run sono vuote e il forwarding è 0 ms. L'indipendenza completa non è ancora integrata.

Commento PRAVDA registrato su [PR #148](https://github.com/andreameloni1984-sys/trump-trucker/pull/148), comment ID 6702230305.

## 4. GAGARIN — evidenza del run #42328183997

Job log: [run #42328183997](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42328183997), job #128268295697.

### Mercati e quotazioni
Il run è iniziato alle 02:14:09.817324 UTC. Tutte le otto commodity operative sono `MARKET_CLOSED`, provider YAHOO:
- Brent 15.267,6 s;
- WTI 15.253,4 s;
- Oro 15.251,0 s;
- Argento 15.252,1 s;
- Rame 15.263,2 s;
- Grano 24.852,7 s;
- Mais 24.855,8 s;
- Soia 24.853,0 s.

EUR/USD e GBP/USD sono ausiliari/non operativi, provider BIQUOTE, entrambi MARKET_CLOSED con età circa 15.553 s. La chiusura del sabato è coerente con il mercato chiuso: l'età delle quotazioni non viene classificata automaticamente come guasto provider.

### Classificazioni direzionali WATCH
| Strumento | Direzione | Probabilità | Quality | Confidence | Blocchi principali |
|---|---:|---:|---:|---:|---|
| WTI | SHORT | 66 | 57,5 | 37 | dati non freschi, trigger non confermato, mismatch direzione, confluence |
| Mais | LONG | 63 | 52,5 | 35 | dati non freschi, trigger non confermato/mismatch, RR_FAIL |
| Argento | LONG | 59 | 49,5 | 32 | dati non freschi, trigger non confermato/mismatch, RR1_FAIL, confidence |

Tutti sono PAPER_WATCH, non segnali operativi: ticker runtime, mercato/scadenza, timestamp quotazione, entry, SL, TP e ATR non sono esposti nel log di classificazione. Non c'è autorizzazione d'ingresso.

Il pre-alert Telegram #3711 è stato API-accepted alle 02:14:13.6555025Z (472 ms), ma il corpo non è conservato. Il ledger lo registra già come `watch_board_pre_alert_unresolved`, non attribuibile a WTI/Mais/Argento. Le tre classificazioni individuali sono righe distinte; non risultano invii individuali (sent_at vuoto).

### Journal e feedback
Il run dichiara:
- PAPER_TRADING_ONLY=1;
- DATABASE_URL vuoto;
- Recorded entries=0;
- Updated open outcomes=0;
- New feedback signals=0;
- New additional live forecasts=0;
- signals=0, open=0, closed=0, win_rate=N/D, avg_R=N/D.

Artefatti main:
- [journal.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/journal.csv): 11 righe del 17 ottobre, tutte `nessun segnale`;
- [commodities_prediction_log.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities_prediction_log.json): 981 record; ultimo creato il 15 settembre 2026 alle 15:45:04 UTC (Benzina RBOB, PENDING);
- [paper_trade_log.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/paper_trade_log.csv): una riga WTI LONG legacy importata, 8 ottobre, entry 96,24 / SL 89,37 / TP1 103,11 / TP2 106,55, status OPEN, PnL nullo, data_status LEGACY_IMPORT e nessuna identità contratto/provider/quotazione;
- [data/paper_open.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/data/paper_open.json): P0001, la stessa posizione WTI legacy, non un secondo trade;
- [position.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/position.json): vecchia posizione Heating Oil LONG del 15 settembre, senza prova indipendente di fill;
- `gagarin_feedback.csv`: non presente nel repository pubblico;
- [commodities_monitor_state.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities_monitor_state.json): timestamp 17 settembre 2026, non rappresenta lo stato del run corrente.

La documentazione del workflow dichiara che i journal PAPER sono dati operativi privati e non vengono committati nel repository pubblico; la persistenza privata D1/Postgres non è dimostrata. Il log conferma DATABASE_URL vuoto. Non si inferisce un outcome dalle posizioni legacy.

### Motore outcome e PR
Main [engine/feedback.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py), blob SHA `41bec9bfab031c8dbf71121cd69d0e9b4c4f663f`, ancora:
- abbina per simbolo/timeframe senza identità completa ticker/mercato/scadenza;
- assegna STOP se SL e TP sono nella stessa candela;
- se più TP sono toccati nella stessa candela, seleziona `max(hit_targets)`, cioè il target più alto, senza prova intrabar.

[PR #192 — exact contract/outcome audit](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) è OPEN, 6 commit, branch 6 ahead e 3 behind rispetto a main. Il branch introduce provider/ticker/mercato/scadenza e rende non verificabile la candela che tocca sia SL sia TP. **Rimane** `idx = max(hit_targets)` quando più target sono raggiunti nella stessa candela: il TP più alto non è dimostrato. Commento di follow-up PRAVDA aggiunto, ID 6702240640.

[PR #225 — offset cron monitor](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225) è OPEN/DRAFT, 2 commit, test #42337488636 SUCCESS, non integrata. Commento PRAVDA aggiunto, ID 6702230572.

[PR #175 — gestione webhook attivo](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175) è OPEN. I test del branch sono SUCCESS, ma l'ultimo polling main osservato #42317191549 (00:16:15 UTC) è FAILURE per Telegram 409 webhook attivo. Non c'è un successivo run main che provi la correzione runtime.

## 5. Ledger e outcome

Ledger consultato: [pravda-signal-ledger-2026-11-07.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-07.csv).

Verifica CSV:
- righe dati: **45**;
- firme uniche: **45**;
- duplicati: **0**;
- `ESITO_NON_VERIFICABILE`: **29**;
- `NON_TRADE`: **16**.

Le 45 righe comprendono candidati storici, watch, notifiche e record legacy: non sono 45 trade. I messaggi SPUTNIK #715/#716, il board GAGARIN #3711 e le tre classificazioni WATCH sono già registrati. Nessun nuovo segnale/record distinto è emerso dai run di mercato osservati, quindi il ledger non è stato modificato.

- Fill verificati: **0**.
- TP verificati: **0**.
- SL verificati: **0**.
- Campione di trade con outcome verificabile: **0**.
- Win rate e average R: **N/D**.

Non sono disponibili candele successive abbinate allo stesso ticker, mercato e contratto per i candidati recenti; inoltre mancano livelli operativi o prova di fill. Nessun backtest è stato prodotto.

## 6. Prossimo controllo

1. Verificare le prossime esecuzioni schedule effettive, non solo i cron dichiarati, e misurare i gap.
2. Alla riapertura, verificare provider, timestamp e freschezza delle otto commodity; non trattare MARKET_CLOSED come segnale.
3. Verificare PR #148 e #225 su main prima di attribuire loro effetti runtime.
4. Verificare PR #192 dopo rebase e dopo correzione del caso multi-TP nella stessa candela.
5. Verificare il webhook/polling GAGARIN dopo eventuale integrazione PR #175.
6. Per ogni futuro candidato operativo, conservare ticker esatto, mercato, scadenza, provider/timestamp, entry, SL, TP, ATR, generazione e invio; valutare soltanto candele successive dello stesso contratto.

## 7. Vincoli rispettati

Nessuna modifica al codice, alla strategia, ai filtri, ai punteggi o al rischio. Nessun merge, deploy, rerun, ordine reale, modifica a Render o ai segreti. Nessun servizio a pagamento. Nessun accesso Trading212 dichiarato. Telegram è riportato solo come API acceptance nei log, non come consegna certa al dispositivo.

**PAPER ONLY.**
