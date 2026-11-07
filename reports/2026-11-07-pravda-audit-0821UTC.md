# PRAVDA — Audit indipendente SPUTNIK / GAGARIN

**Controllo:** 2026-11-07 08:21:43 UTC (09:21:43 Europe/Rome)  
**Perimetro:** GitHub Actions programmate, log completi degli ultimi monitor, journal e artefatti pubblici su `main`, ledger PRAVDA, motore feedback, PR/CI e commenti di deployment Cloudflare.  
**Vincoli:** PAPER ONLY. Nessuna modifica a codice dei bot, strategia, filtri, punteggi, rischio, segreti o Render. Nessun merge, deploy, rerun o ordine.

## Sintesi esecutiva

- Nessuna nuova scansione di mercato su `main` dopo SPUTNIK run **#42331705890** (02:57:24 UTC) e GAGARIN run **#42328183997** (02:13:56 UTC).
- Alle 08:21:43 UTC i gap sono **5h24m19s SPUTNIK** e **6h07m47s GAGARIN**. Le liste GitHub Actions filtrate per `event=schedule` non mostrano un monitor di mercato successivo.
- SPUTNIK ha prodotto i messaggi #715/#716: GOLD, bias tecnico CFD LONG ma D-L-A NEUTRAL, `NO_DIRECTIONAL_NEWS`, nessun entry/SL/TP/ATR. Sono la ripetizione della tesi #713/#714, non un nuovo catalizzatore.
- GAGARIN ha classificato WTI SHORT, Mais LONG e Argento LONG come `PAPER_WATCH`; tutte le otto commodity erano `MARKET_CLOSED`, con quote Yahoo stale. Nessun livello operativo completo e nessun ingresso.
- Il journal pubblico GAGARIN contiene 11 righe senza segnali; il paper trade log contiene un WTI legacy senza prova di fill. `DATABASE_URL` è vuoto nel run.
- Nuova PR GAGARIN **#233** formalizza l'identità CFD SPOT senza scadenza (`contract_type=SPOT`, `expiry=None`) separandola dai futures con scadenza. I due job CI della PR sono SUCCESS, ma la PR è draft e basata sulla PR #207, non su main; non aggiunge feed o prezzi Trading 212.
- Cloudflare ha registrato un terzo build fallito verso il target denominato `telegram-github-bridge/production`, questa volta sul commit della PR draft #233. Non è un deploy riuscito. PRAVDA ha segnalato il fatto nel commento #6704451931.
- Ledger: **45 righe, 45 firme uniche, zero duplicati**. Nessun nuovo segnale da inserire. **0 fill verificati, 0 SL/TP verificati; win rate e average R N/D.**

## 1. GitHub Actions e continuità

### SPUTNIK
- Monitor: [run #42331705890](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42331705890), job #128279494938, SUCCESS, creato 02:57:24 UTC, branch `main`.
- Ultimo monitor precedente: [run #42311247999](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42311247999), 23:20:35 UTC. Intervallo tra i due monitor: 3h36m49s.
- Cron su main: `2-59/5 * * * *`. Nessuna successiva esecuzione schedule del monitor nella lista interrogata.
- Polling separato: [run #42329017675](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42329017675), SUCCESS alle 02:23:33 UTC, `Pending updates: 0`. Non è un monitor di mercato né prova di consegna al dispositivo.

### GAGARIN
- Monitor: [run #42328183997](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42328183997), job #128268295697, SUCCESS, creato 02:13:56 UTC, branch `main`.
- Ultimo monitor precedente: [run #42304574886](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42304574886), 22:25:16 UTC. Intervallo: 3h48m40s.
- Cron su main: `*/15 * * * *`. Nessuna successiva esecuzione schedule del monitor nella lista interrogata.
- Polling: [run #42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549), FAILURE alle 00:16:15 UTC. Token e diagnostica bot OK; `getUpdates` termina con Telegram API 409: webhook attivo, polling incompatibile.
- Il workflow monitor su main dichiara `DATABASE_URL: ${{ secrets.DATABASE_URL }}`, ma il log del run stampa il valore vuoto. Il workflow documenta che i journal sono dati operativi privati e che la persistenza verrà riattivata solo dopo un database privato verificato.

## 2. SPUTNIK — messaggi #715/#716

Log del job #128279494938:
- Collector avviato alle 02:57:29.720 UTC.
- SEC CIK 0001849635: HTTP 403, cooldown 21.600 secondi, `filings=0`.
- White House RSS: HTTPError.
- Scansione intelligence: 1.226 ms, `findings=0`.
- Nessuna correlazione pubblica nuova; `NO_DIRECTIONAL_NEWS`.
- `GAGARIN forwarding=0ms`; nessun handoff di produzione.

Messaggi effettivi:
- **#715:** GOLD, bias preliminare NEUTRAL, priorità/score 70, decisione WATCH.
- **#716:** GOLD, bias tecnico CFD LONG, D-L-A NEUTRAL / NO_DIRECTION; `TRADE PAPER: NOT_EXECUTED`. Entry, SL, TP e ATR non emessi per assenza di quotazione futures fresca/ATR valido.
- Telegram API acceptance: #715 483 ms, #716 401 ms. L'ACK API non prova la visualizzazione sul dispositivo.
- `GC=F` è un mapping configurato, non ticker runtime o contratto verificato. Scadenza, provider effettivo e timestamp della quotazione non sono esposti.

Le righe di test che precedono il collector (inclusi OSError simulati e message_id=731) appartengono alle regression tests, non alla produzione. Non sono conteggiate come segnali.

**Classificazione PRAVDA:** ripetizione del candidato #713/#714, nessun nuovo catalizzatore, nessun trade e nessun outcome finanziario valutabile.

### Stato SPUTNIK
Il blob `sputnik_state.json` non è stato restituito in forma testuale dal fetch corrente. Non si rinnova in questo controllo la precedente verifica dei 500 elementi. Non dichiaro il file vuoto né considero la persistenza nuovamente certificata.

## 3. GAGARIN — quotazioni e candidati

Log del job #128268295697. Tutte le otto commodity sono `MARKET_CLOSED`, provider YAHOO:

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

La chiusura del sabato è coerente con il calendario; la stale age da sola non dimostra un guasto del provider. Ticker runtime, market type, scadenza e timestamp individuale della quotazione non sono esposti nel riepilogo.

EUR/USD e GBP/USD risultano anch'essi `MARKET_CLOSED` via BIQUOTE e non sono segnali commodity operativi.

### Classifica
- WTI SHORT: probabilità 66, quality 57,5, confidence 37; blocchi: dati non freschi, trigger non confermato, mismatch direzionale e confluence.
- Mais LONG: 63 / 52,5 / 35; blocchi: dati non freschi, trigger non confermato, mismatch direzionale, RR_FAIL.
- Argento LONG: 59 / 49,5 / 32; blocchi: dati non freschi, trigger non confermato, mismatch direzionale, RR1_FAIL e CONFIDENCE_FAIL.
- Gli altri cinque strumenti non hanno direzione valida.

Timestamp delle tre classificazioni: WTI 02:14:13.6534379 UTC; Mais 02:14:13.6541730 UTC; Argento 02:14:13.6543040 UTC.

Le tre righe non hanno `sent_at` né `telegram_message_id`: non risultano alert individuali. Il board #3711 è stato accettato dall'API alle 02:14:13.6555025 UTC (472 ms), ma il corpo non è conservato e non può essere attribuito con certezza ai tre strumenti.

Riepilogo del run:
- `Recorded entries: 0`
- `New feedback signals: 0`
- `New additional live forecasts: 0`
- `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D total_R=0.0`

## 4. Journal, posizioni legacy e motore feedback

File pubblici verificati su main:
- [journal.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/journal.csv): 11 righe del 17 ottobre, tutte senza segnale.
- [paper_trade_log.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/paper_trade_log.csv): un WTI LONG legacy, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55. Il record stesso annota una chiusura spot del 6 ottobre e “Nessun esito”; provider, ticker esecutivo, contratto/scadenza e fill non sono dimostrati.
- `commodities_monitor_state.json`: timestamp 2026-09-17 03:44:02 UTC, Benzina RBOB, azione ATTENDERE, entry BLOCKED.
- `commodities_direction_state.json`: direzioni aggiornate al 17 settembre (alcuni strumenti al 15 settembre), non uno stato operativo corrente.
- `gagarin_feedback.csv` non è presente su main.
- `DATABASE_URL` vuoto nel log.

Su main, [engine/feedback.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py) usa fingerprint basato su simbolo/direzione/timeframe/livelli/barra; il matching forward usa simbolo e timeframe, senza identità completa provider/ticker/mercato/scadenza. Se SL e TP cadono nella stessa candela, main assegna STOP; se più TP sono toccati nella stessa candela senza SL, usa `idx=max(hit_targets)` e assegna il target più alto. Quest'ultimo risultato non è dimostrabile dalla sola OHLC.

**PR #192** (aperta, non integrata) aggiunge identità provider/ticker/market/contratto e classifica SL+TP nella stessa candela come `ESITO NON VERIFICABILE`; tuttavia il diff lascia invariata la selezione `idx=max(hit_targets)` per più TP raggiunti nella stessa candela. Quindi resta una sovrastima potenziale del target in quella casistica.

## 5. Nuova PR #233 — identità SPOT senza scadenza

[PR #233](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/233) è OPEN/DRAFT, head `b79159452e5f4e6bf088e68506f50b41e10c07ce`, base `feat/gagarin-t212-cfd-identity-guard-20261106` (PR #207), non main.

La modifica introduce:
- `contract_type=SPOT` con `expiry=None`;
- `contract_type=EXPIRING_FUTURE` con data ISO obbligatoria;
- matching del contract type fra strumento e quote series;
- contract type incluso nella fingerprint.

I job [#42354553254](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42354553254) e [#42354553252](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42354553252) sono SUCCESS. La PR dichiara esplicitamente che il registry resta vuoto in attesa di verifica esatta e che non aggiunge feed, quote, calcolo livelli, journal, ordini o integrazione Trading 212. I test verdi non provano accesso al broker né disponibilità di prezzi CFD.

PR #232 resta OPEN/DRAFT su main; PR #175 resta OPEN e il polling main continua a fallire 409. PR #192 è OPEN, non integrata.

## 6. Cloudflare Git integration — terzo build fallito su draft

Il commento automatico Cloudflare sulla PR #233 riporta:
- servizio: `telegram-github-bridge`;
- target denominato `production`;
- commit: `b7915945`;
- aggiornamento: 2026-11-07 08:18 UTC;
- build ID: `bd5e6781-3cb9-476e-9b60-d6d387d8d410`;
- stato: **Deployment failed**.

È il terzo build fallito osservato su PR draft #231, #232 e #233. È prova di tentativi di build sul target denominato production, non di deploy riusciti o di modifica effettiva del servizio. PRAVDA non ha accesso al pannello Cloudflare e non ha avviato o modificato deployment.

PRAVDA ha lasciato il commento di audit [#6704451931](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/233#issuecomment-6704451931), chiedendo di verificare le regole Git integration e impedire build del target production da branch draft non destinati al rilascio.

## 7. Ledger PRAVDA — controllo CSV indipendente

Riletto il file [pravda-signal-ledger-2026-11-07.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-07.csv) con parser CSV che gestisce correttamente virgolette e delimitatori.

| Indicatore | Valore |
|---|---:|
| Righe dati | 45 |
| Firme uniche | 45 |
| Duplicati | 0 |
| Record SPUTNIK | 8 |
| Record GAGARIN | 37 |
| `ESITO_NON_VERIFICABILE` | 29 |
| `NON_TRADE` | 16 |
| Fill verificati | 0 |
| SL/TP verificati | 0 |
| Win rate / average R | N/D |

Tipi record: 21 historical prediction candidate; 1 legacy paper ticket; 6 watch pre-alert; 6 CFD early setup not executed; 3 watch-board unresolved; 1 CFD early bias not executed; 6 watch candidate blocked; 1 CFD early bias repeat not executed.

Campi mancanti o non registrati (conteggio su 45 righe, considerando `NOT_RECORDED`, `NOT_EXPOSED`, `FIELD_ABSENT` come mancanti):
- timestamp invio: 28;
- ticker: 17;
- market type: 36;
- scadenza: 37;
- provider: 24;
- timestamp quotazione: 43;
- entry: 17;
- SL: 17;
- TP1: 17;
- ATR: 33;
- source URL: 0.

Molti record sono WATCH, NOT_EXECUTED o storici e non devono essere interpretati come trade con livelli mancanti. Nessun nuovo segnale è stato aggiunto; ledger lasciato invariato.

## 8. Fonti e prossime verifiche

Fonti consultate:
- run e log SPUTNIK #42331705890;
- run e log GAGARIN #42328183997;
- polling GAGARIN #42317191549;
- journal, paper trade log, monitor state, direction state e feedback engine su main;
- PR #175, #192, #207, #232, #233 e relativi status/commenti;
- ledger PRAVDA del 7 novembre.

Prossimo controllo:
1. verificare nuove esecuzioni schedule di entrambi i monitor e distinguere i test PR dalle scansioni;
2. alla riapertura dei mercati, verificare freshness, ticker runtime, market type, scadenza e timestamp quote;
3. verificare se PR #192 e #175 vengono integrate e poi controllare il comportamento effettivo su main;
4. verificare il matching dei contratti CFD SPOT/FUTURE soltanto dopo l'integrazione delle PR pertinenti, senza presumere feed Trading 212;
5. ottenere un journal durevole e un fill PAPER identificabile prima di calcolare statistiche;
6. verificare la configurazione Cloudflare Git integration prima di ulteriori modifiche ai branch draft.

**Verdetto:** nessun trade con fill e outcome verificabile. Non sono stati effettuati backtest. Nessuna modifica a codice, strategia, filtri, score, rischio, segreti, Render o configurazione Cloudflare. Nessun merge, deploy, rerun o ordine reale. PAPER ONLY.
