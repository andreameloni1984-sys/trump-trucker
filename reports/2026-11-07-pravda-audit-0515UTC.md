# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Controllo:** 2026-11-07 05:15:41 UTC (06:15:41 Europe/Rome)  
**Perimetro:** GitHub Actions su main, log dei job, ledger PRAVDA, journal e artefatti pubblici, PR e CI. **PAPER ONLY**.

## Sintesi esecutiva

- Nessun nuovo monitor di mercato su `main` dopo SPUTNIK run **#42331705890** (02:57:24 UTC) e GAGARIN run **#42328183997** (02:13:56 UTC). Query Actions filtrate per `event=schedule` e create dopo i rispettivi run: **0 risultati** in entrambi i repository fino alle 05:15:41 UTC.
- Il gap dall'ultimo monitor al controllo è **2h18m17s SPUTNIK** e **3h01m45s GAGARIN**, contro cron dichiarati ogni 5 e 15 minuti.
- SPUTNIK ha ripetuto la stessa ipotesi GOLD dei messaggi #713/#714 con #715/#716, pur avendo `findings=0`, `NO_DIRECTIONAL_NEWS`, nessuna nuova correlazione pubblica e nessun livello operativo.
- GAGARIN ha registrato tre classificazioni direzionali WATCH (WTI SHORT, Mais LONG, Argento LONG) in un run di sabato con tutti gli otto mercati commodity `MARKET_CLOSED`. Nessuna aveva entry/SL/TP/ATR; il board #3711 è stato accettato dall'API ma il corpo non è conservato.
- Il ledger del 7 novembre è invariato: **45 record, 45 firme uniche, zero duplicati**. Nessun nuovo segnale/record da aggiungere.
- Non esiste un campione di trade con fill verificato: **0 fill, 0 SL/TP verificati, win rate e average R N/D**.

## 1. Revisioni e Actions su main

HEAD osservati:
- SPUTNIK: `b86862bb8421127d74bfeaf4ccde8ed4441adcca` (ultimo commit documentale PRAVDA, 04:28:14 UTC).
- GAGARIN: `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c` (ultimo commit main 6 novembre, 14:39:45 UTC).

Run monitor:
- [SPUTNIK #42331705890](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42331705890), job #128279494938, SUCCESS, 02:57:24 UTC.
- [GAGARIN #42328183997](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42328183997), job #128268295697, SUCCESS, 02:13:56 UTC.
- [GAGARIN Telegram polling #42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549), job #128232586109, FAILURE, 00:16:15 UTC.
- [SPUTNIK Telegram polling #42329017675](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42329017675), SUCCESS, 02:23:33 UTC; workflow separato, non contato come scansione mercato.

Cron main verificati:
- SPUTNIK `.github/workflows/trump_tracker.yml`: `2-59/5 * * * *`.
- GAGARIN `.github/workflows/gagarin-monitor.yml`: `*/15 * * * *`.
- GAGARIN polling `.github/workflows/telegram-polling.yml`: `*/5 7-21 * * 1-5`.

La run GAGARIN polling #42317191549 è marcata da GitHub come `event=schedule` alle 00:16 UTC di sabato, fuori dal cron dichiarato. L'anomalia è verificata nei metadati; la causa non è dimostrata e non viene attribuita a una causa specifica.

## 2. SPUTNIK — GOLD #715/#716

Log produttivo del job #128279494938:
- run avviato alle 02:57:29.812865 UTC;
- SEC CIK 0001849635: HTTP 403;
- White House RSS: HTTPError;
- scan intelligence: 1.226 ms, `findings=0`;
- nuove operazioni documentate: 0;
- nuove correlazioni pubbliche: 0;
- notizia: `NO_DIRECTIONAL_NEWS`;
- NARWHAL non configurato; handoff GAGARIN URL/API key vuoti nel runtime.

Messaggi:
- **#715**: GOLD, bias preliminare NEUTRAL, score/priorità 70, tecnica UNAVAILABLE, `NO_DIRECTIONAL_NEWS`, WATCH; nessun livello.
- **#716**: GOLD, bias LONG solo tecnico, D-L-A NEUTRAL/NO_DIRECTION, EARLY_BIAS, `TRADE PAPER: NOT_EXECUTED`; entry/SL/TP/ATR omessi per assenza di quotazione futures fresca e ATR valido.

Le API Telegram hanno confermato l'accettazione dei messaggi #715 e #716 con round-trip dichiarati di 483 ms e 401 ms. L'ACK API non prova la visualizzazione sul dispositivo né un'esecuzione. Il ledger rappresenta la coppia come un solo candidato, evitando di contarla due volte; conserva un unico timestamp `sent_at` per la scheda #716, mentre i due ACK sono distinti nel log.

Identità strumento incompleta:
- `GC=F` è mapping configurato, non ticker runtime risolto;
- front-month continuo dichiarato, ma mese/scadenza esatta non disponibile;
- provider e timestamp della quotazione non esposti;
- nessun entry/SL/TP/ATR.

È una ripetizione della tesi GOLD #713/#714 senza nuovo catalizzatore nel run. [PR #148](https://github.com/andreameloni1984-sys/trump-trucker/pull/148) propone il gate su nuovo item pubblico individuale e datato; resta OPEN, non integrata. Il suo head `f46de84560ee6f4a3ea5c7b4e641d9fa69cd7682` ha due check (tests e item-intelligence) SUCCESS alle 04:24 UTC.

Persistenza: la precedente verifica aveva letto 500 elementi in `sputnik_state.json` alle 02:57 UTC. In questo controllo il file, di grandi dimensioni, non è stato nuovamente leggibile tramite il connettore GitHub (contenuto non restituito / fetch raw rifiutato per dimensione); quindi il dato 500 è riportato come **ultima verifica precedente**, non come nuova lettura di questo audit.

## 3. GAGARIN — run #42328183997

Il job #128268295697 è partito alle 02:14:09.817324 UTC. Tutte le otto commodity sono `MARKET_CLOSED`, provider YAHOO:

| Strumento | Età quotazione (s) | Età approssimativa |
|---|---:|---:|
| Brent | 15.267,6 | 4h14m |
| WTI | 15.253,4 | 4h14m |
| Oro | 15.251,0 | 4h14m |
| Argento | 15.252,1 | 4h14m |
| Rame | 15.263,2 | 4h14m |
| Grano | 24.852,7 | 6h54m |
| Mais | 24.855,8 | 6h54m |
| Soia | 24.853,0 | 6h54m |

La chiusura del sabato è coerente con il mercato chiuso: l'età è stale, ma non prova da sola un guasto provider.

Classificazioni direzionali visibili nel log:
- WTI SHORT: probabilità 66, quality 57,5, confidence 37.
- Mais LONG: probabilità 63, quality 52,5, confidence 35.
- Argento LONG: probabilità 59, quality 49,5, confidence 32.

Sono tutte `PAPER_WATCH`; nessun ticker runtime, market type, scadenza o timestamp quotazione individuale esposto; nessun entry/SL/TP/ATR; nessuna autorizzazione di ingresso. Nessun invio individuale: `sent_at` vuoto nel ledger per le tre classificazioni.

Il board Telegram #3711 è stato API-accepted alle 02:14:13.6555025 UTC (472 ms). Il corpo non è conservato; non è attribuibile con certezza ai tre strumenti. L'ACK non prova la visualizzazione sul dispositivo.

## 4. Journal, feedback e predizioni legacy GAGARIN

File main verificati:
- [journal.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/journal.csv): 11 righe del 17 ottobre, tutte con `nessun segnale`, nessun fill.
- [paper_trade_log.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/paper_trade_log.csv): una riga WTI LONG `LEGACY_IMPORT`, con livelli 96,24 / 89,37 / 103,11; nota legacy senza esito. Non prova un fill.
- [position.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/position.json): vecchia posizione Heating Oil LONG aperta il 15 settembre 2026; nessuna prova indipendente di fill.
- `gagarin_feedback.csv`: 404, assente dal main pubblico.
- `paper_open.json`: 404, assente dal main pubblico; non viene assunto che la posizione WTI sia duplicata in questo file.
- [commodities_prediction_log.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities_prediction_log.json): 981 record, dal 10 al 15 settembre; ultimo record 15 settembre 15:45:04 UTC. Stati: 945 PENDING, 36 NEUTRALE. Azioni: 960 WAIT, 15 LONG. Le righe LONG/COMPRA ORA restano predizioni legacy senza prova di fill, provider/contratto/scadenza e candele dello stesso contratto; non sono trade verificati.

Il log del monitor mostra `DATABASE_URL` vuoto, `Recorded entries=0`, `Updated open outcomes=0`, `New feedback signals=0`. Il workflow main dichiara che i journal sono dati privati e che la persistenza sarà riattivata solo dopo deploy e verifica dello storage D1 privato.

## 5. Motore outcome e PR #192

Il file main [engine/feedback.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py) è ancora la versione precedente:
- abbina per simbolo/timeframe, senza identità esplicita del contratto;
- tratta SL e TP nella stessa candela come STOP;
- quando più target sono nella stessa candela seleziona `max(hit_targets)`.

[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) è OPEN, non draft, non merged. Head `295dba4b074e564a4c11aa3fca136a8e4360672c`; base SHA `c93906a2a4b28d60fd58c600b51cd3c05929f89d`, mentre main è `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`. Compare: **6 commit ahead, 3 behind, diverged**.

La PR aggiunge provider/ticker/mercato/mese/scadenza alla firma, richiede il matching del mercato e del contratto futures, e rende `ESITO NON VERIFICABILE` lo stesso-bar SL+TP. Ma sul suo head rimane a righe 431–434 `idx = max(hit_targets)`: se TP1/TP2/TP3 sono toccati nella stessa OHLC candle, attribuisce il target più alto senza sequenza intrabar dimostrata. Il difetto è già stato segnalato nel commento PRAVDA [#6702240640](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6702240640); nessun commento duplicato aggiunto.

CI visibile sul branch #192: sei suite funzionali SUCCESS del 5 novembre; il check Cloudflare Workers `telegram-github-bridge` è FAILURE. Non è una verifica aggiornata contro il main corrente, dato il branch divergente.

## 6. Altre PR e CI rilevanti

- [SPUTNIK #145](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN; quote provenance e diagnostica Yahoo proposte, non su main. Due check sul head risultano SUCCESS il 6 novembre.
- [SPUTNIK #148](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN; due check SUCCESS il 7 novembre 04:24 UTC; il run produttivo #42331705890 dimostra il caso ripetizione senza nuovo item.
- [GAGARIN #175](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): OPEN; head `7bb944f...`; sette check funzionali SUCCESS, Workers Build `telegram-github-bridge` FAILURE. Main continua a fallire con Telegram API 409: `getUpdates` incompatibile con webhook attivo. La PR propone di saltare il polling senza cancellare webhook e senza acknowledge; non è integrata.
- [GAGARIN #225](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/225): OPEN, draft; sette check funzionali SUCCESS alle 04:13 UTC, Workers Build FAILURE. Main conserva `*/15`; nessuna prova runtime del cron offset proposto.
- [GAGARIN #221](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/221): OPEN, draft; rimozione delle rotte FX residue non integrata. I log correnti mostrano EUR/USD e GBP/USD solo come contesto ausiliario MARKET_CLOSED, non come ingressi commodity.

## 7. Ledger PRAVDA e statistiche

File: [pravda-signal-ledger-2026-11-07.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-07.csv)  
Blob SHA: `9c58b42b70c7aaf92a161b553c9eee8c1f2be52a`.

Verifica CSV completa:
- record: **45**;
- firme uniche: **45**;
- duplicati: **0**;
- SPUTNIK: 8 record;
- GAGARIN: 37 record;
- outcome `ESITO_NON_VERIFICABILE`: 29;
- `NON_TRADE`: 16.

Campi mancanti nel ledger (record complessivi; include legacy e WATCH, non solo segnali operativi): timestamp generazione 1; timestamp invio 28; ticker 18; market type 36; expiry 37; provider 33; timestamp quotazione 44; entry/SL/TP1 17 ciascuno; ATR 33. Tutti i 45 record hanno un link fonte/log.

Nessun nuovo record è stato aggiunto: #715/#716, #3711 e le tre classificazioni WTI/Mais/Argento erano già presenti. Nessun fill, SL o TP verificato. Campione operativo verificabile = 0; win rate e average R = N/D.

## 8. Fonti consultate

- GitHub Actions run e log: SPUTNIK #42331705890, SPUTNIK polling #42329017675, GAGARIN #42328183997, GAGARIN polling #42317191549.
- Workflow main: `trump_tracker.yml`, `gagarin-monitor.yml`, `telegram-polling.yml`.
- Ledger PRAVDA del 7 novembre.
- GAGARIN: `engine/feedback.py`, `journal.csv`, `paper_trade_log.csv`, `position.json`, `commodities_prediction_log.json`.
- PR e check: SPUTNIK #145/#148; GAGARIN #175/#192/#221/#225.

## 9. Prossimo controllo

1. Verificare che compaiano nuovi run schedule su main e misurare gli intervalli reali.
2. Alla riapertura dei mercati, verificare quotazioni fresche, ticker risolto, provider, timestamp e contratto/scadenza per ogni strumento.
3. Verificare su main, non solo sulle PR, le correzioni #192, #175, #148 e l'offset #225.
4. Non valutare outcome finché non esistono fill/entry bar e candele successive dello stesso identico strumento e contratto.
5. Mantenere il ledger a 45 record finché non compare un nuovo record con firma realmente distinta.

**Nessuna modifica al codice, strategia, filtri, punteggi o rischio. Nessun merge, deploy, rerun, ordine reale, modifica a Render o segreti. Nessun servizio a pagamento. Nessun accesso Trading212 o consegna Telegram al dispositivo dichiarati. PAPER ONLY.**
