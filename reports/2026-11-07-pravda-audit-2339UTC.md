# PRAVDA — Audit SPUTNIK / GAGARIN
**Cut-off:** 7 novembre 2026, 23:39 UTC (8 novembre, 00:39 CET)  
**Ambito:** verifica indipendente; PAPER ONLY. Nessuna modifica a codice, strategia, filtri, punteggi o rischio.

## Esito sintetico
- Nessun fill verificato; nessun esito SL/TP verificabile su un contratto esatto.
- SPUTNIK: ultimo monitor di mercato con log direttamente ispezionato [#42409488950](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42409488950), concluso SUCCESS alle 20:07:24 UTC. Il successivo polling [#42423194296](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42423194296), concluso alle 23:00:21 UTC, ha trovato `Pending updates: 0`: non è una scansione.
- Alle 23:37:26 UTC è stato creato il commit di persistenza [42f6859](https://github.com/andreameloni1984-sys/trump-trucker/commit/42f685921fa356f2669e85b6764b290535b95f8e), con nuove osservazioni intelligence nello stato. Non ho un run ID/log Actions associabile a quel commit in questa verifica; non lo conto come monitor di mercato né come prova di invio Telegram.
- GAGARIN: ultimo monitor direttamente ispezionato [#42423479990](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42423479990), concluso SUCCESS alle 23:03:58 UTC; tutte le dieci voci del runtime erano MARKET_CLOSED e con quotazioni stale.

## 1. Ledger PRAVDA
Ledger CSV riletto, nuove firme controllate contro `source_record_id` e contenuto riletto dopo il salvataggio.

- Record: **74**
- Per bot: **{"GAGARIN":46,"SPUTNIK":28}**
- Firme uniche: **74/74**
- Source record ID unici: **74/74**
- Duplicati: **0**
- Outcome: **{"ESITO_NON_VERIFICABILE":29,"NON_TRADE":45}**
- Fill verificati: **0**
- SL/TP verificati: **0**
- Win rate / average R: **N/D** — nessun campione con fill e contratto verificati.

Le 8 nuove righe sono osservazioni intelligence NON_TRADE, non segnali di mercato. ID stabili: `commit:42f685921fa356f2669e85b6764b290535b95f8e/intelligence:<event_id>`.

## 2. SPUTNIK
### Ultimo monitor con log disponibile
Run [#42409488950](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42409488950), job `sputnik` SUCCESS:
- SEC HTTP 403, cooldown 21.600 secondi, zero filing.
- White House RSS: HTTPError.
- Telegram #723 digest notizie: API ACK, 388 ms; non è un segnale.
- #724 GOLD NEUTRAL/WATCH, tecnica 5m UNAVAILABLE, nessuna quotazione o livello attribuibile; API ACK 378 ms.
- #725 GOLD NO_DIRECTION / NOT_EXECUTED; front-month continuo senza scadenza esatta, NARWHAL non configurato, nessun entry/SL/TP/ATR; API ACK 368 ms.
Gli ACK dimostrano accettazione API con message_id, non visualizzazione sul dispositivo. Nessuno dei tre messaggi è un trade.

Polling separato [#42423194296](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42423194296): job SUCCESS, `Pending updates: 0`. Il polling non prova una scansione o un invio in uscita.

### Nuovo commit di stato, non segnale
Commit [42f6859](https://github.com/andreameloni1984-sys/trump-trucker/commit/42f685921fa356f2669e85b6764b290535b95f8e), `sputnik_state.json`, `updated_at=2026-11-07T23:37:25Z`: sette item RSS individuali e una pagina TRUTH_ARCHIVE page-level.
- `400702d6cc01b700c4442a7f` — Sat, 07 Nov 2026 18:40:20 +0000 → rilevato 2026-11-07T23:37:24.997632+00:00; GEOPOLITICAL_ESCALATION/NO_ANALOGUE; PUBLIC_RSS_ITEM; nessun mapping commodity. https://truthsocial.com/@realDonaldTrump/117576618491350292
- `3e4190e62a81433d271dc5e8` — Sat, 07 Nov 2026 18:45:15 +0000 → rilevato 2026-11-07T23:37:24.997505+00:00; OTHER/NO_ANALOGUE; PUBLIC_RSS_ITEM; nessun mapping commodity. https://truthsocial.com/@realDonaldTrump/117576637813209602
- `6974af1e615bae7fe540141c` — Sat, 07 Nov 2026 19:50:37 +0000 → rilevato 2026-11-07T23:37:24.997361+00:00; OTHER/NO_ANALOGUE; PUBLIC_RSS_ITEM; nessun mapping commodity. https://truthsocial.com/@realDonaldTrump/117576894858031741
- `6cd8fe75d47cbf3a2f4087f8` — Sat, 07 Nov 2026 19:55:09 +0000 → rilevato 2026-11-07T23:37:24.997253+00:00; OTHER/NO_ANALOGUE; PUBLIC_RSS_ITEM; nessun mapping commodity. https://truthsocial.com/@realDonaldTrump/117576912671985823
- `c11f21fda47e951be02989fa` — Sat, 07 Nov 2026 20:08:16 +0000 → rilevato 2026-11-07T23:37:24.997093+00:00; OTHER/NO_ANALOGUE; PUBLIC_RSS_ITEM; nessun mapping commodity. https://truthsocial.com/@realDonaldTrump/117576964275275822
- `7594c8fc168b8676e48f8537` — Sat, 07 Nov 2026 21:47:48 +0000 → rilevato 2026-11-07T23:37:24.996968+00:00; OTHER/NO_ANALOGUE; PUBLIC_RSS_ITEM; nessun mapping commodity. https://truthsocial.com/@realDonaldTrump/117577355679832817
- `91dc6fd3521f8bab53099fb2` — Sat, 07 Nov 2026 21:48:09 +0000 → rilevato 2026-11-07T23:37:24.996836+00:00; OTHER/NO_ANALOGUE; PUBLIC_RSS_ITEM; nessun mapping commodity. https://truthsocial.com/@realDonaldTrump/117577357040264617
- `7cc65876877d52fca4dd552e` — data pubblicazione non disponibile → rilevato 2026-11-07T23:37:24.357893+00:00; OTHER/NO_ANALOGUE; PUBLIC_SOURCE_TEXT_PAGE_LEVEL; nessun mapping commodity. https://www.trumpstruth.org/

I sette item individuali sono stati rilevati circa 1h49m–4h57m dopo la pubblicazione. Le classificazioni sono `NO_ANALOGUE`; anche l'item classificato `GEOPOLITICAL_ESCALATION` non ha historical match. Nessuno produce mapping commodity, bias, quotazione o livelli. La pagina archivio non ha titolo né timestamp individuale. Nessun messaggio Telegram è attribuito a queste otto osservazioni.

### Cadenza
Cron dichiarato nel workflow: `2-59/5 * * * *`. Tra il monitor di mercato alle 20:07:24 UTC e il cut-off 23:39 UTC trascorrono circa **3h31m**. Il commit di stato delle 23:37 non basta a certificare un monitor di mercato o a spiegare il gap. La causa non è dimostrata.

## 3. GAGARIN
Run [#42423479990](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42423479990), job `Run Gagarin directly on GitHub` SUCCESS:
- Runtime: Soia, Grano, Brent, WTI, EUR/USD, Oro, Argento, Mais, Rame, GBP/USD.
- Tutti `MARKET_CLOSED`.
- Età quote: cereali/soia circa 100.132 secondi (~27h49m); metalli/petrolio/FX circa 90.532–90.534 secondi (~25h09m).
- Unico candidato con direzione: Argento LONG, probabilità 59, qualità 49,5, confidence 32, `PAPER_WATCH`. Mancano ticker provider risolto, timestamp quote, mercato/scadenza, reference price e livelli. Non è un trade.
- `signals=0 open=0 closed=0`; nuovi feedback 0.
- Telegram #3717 API ACK 474 ms, ma il body non è conservato: strumento/direzione non attribuibili.

Journal e persistenza su main:
- `journal.csv`: 11 righe datate 17 ottobre, tutte “nessun segnale”.
- `paper_trade_log.csv`: un legacy WTI P0001, senza prova di fill.
- `data/paper_open.json`: stesso P0001, non una seconda posizione.
- `position.json`: vecchia posizione HO/USD aperta il 15 settembre, senza prova di fill o contratto esatto.
- `gagarin_feedback.csv`: 404.
- `DATABASE_URL` vuoto nel log del run. Persistenza cross-run non dimostrata.

Cron dichiarato: `*/15 * * * *`. Ultimo run ispezionato alle 23:03:58 UTC; al cut-off sono trascorsi circa 35 minuti. Non ho accesso a un endpoint di enumerazione completa di tutte le Actions recenti: non dichiaro che non siano esistiti run successivi.

## 4. PR/correzioni esistenti
Stati PR verificati su GitHub:
- SPUTNIK #144 persistenza stato off-main: OPEN, non integrata; il commit 42f685 dimostra che lo stato è ancora scritto su main.
- SPUTNIK #148 stop ripetizione raccomandazioni: OPEN.
- SPUTNIK #147 isolamento da GAGARIN, #146 alert individuali/calendario e #145 provenance quote: OPEN.
- GAGARIN #175 webhook/polling, #192 identità contratto/outcome, #219 rimozione FX: OPEN, non integrate.
- GAGARIN #222 rimozione veto intraday, #223 scansione M5 senza Argento, #202 journal PostgreSQL e #235 journal CFD isolato: OPEN/DRAFT, non integrate.

Il runtime GAGARIN continua a includere Argento e le due coppie FX; le PR aperte non sono correzioni attive su main.

## 5. Lacune e prossimo controllo
1. SPUTNIK: acquisire il run Actions/log associato al commit di stato delle 23:37; distinguere collector, polling e persistenza; conservare body Telegram e timestamp di invio.
2. GAGARIN: alla riapertura mercati acquisire ticker risolto, provider, timestamp quote, mercato e scadenza esatti per ogni candidato.
3. Non attribuire il board #3717 ad Argento senza il body.
4. Non calcolare outcome legacy WTI/HO senza fill e candele successive dello stesso identico contratto.
5. Continuare a classificare i messaggi WATCH/NO_DIRECTION e le notizie senza mapping come NON_TRADE.

## Fonti consultate
- GitHub Actions e log job #42409488950, #42423194296 e #42423479990.
- Commit SPUTNIK [42f6859](https://github.com/andreameloni1984-sys/trump-trucker/commit/42f685921fa356f2669e85b6764b290535b95f8e) e diff di `sputnik_state.json`.
- Ledger PRAVDA, `journal.csv`, `paper_trade_log.csv`, `data/paper_open.json`, `position.json`; `gagarin_feedback.csv` 404.
- Workflow `.github/workflows/trump_tracker.yml` e `.github/workflows/gagarin-monitor.yml`.
- Metadata PR dei due repository.

**Nessuna modifica al codice o ai workflow. Nessun merge/deploy, ordine reale, segreto o Render modificato. Nessun servizio a pagamento. PAPER ONLY.**
