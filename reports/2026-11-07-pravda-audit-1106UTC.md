# PRAVDA — Audit indipendente SPUTNIK / GAGARIN

**Controllo:** 2026-11-07 11:06:09 UTC (12:06:09 Europe/Rome)  
**Perimetro:** GitHub Actions e log completi, segnali/alert di produzione, commit di stato SPUTNIK, file journal/feedback pubblici GAGARIN, codice outcome su main e PR, ledger PRAVDA.  
**Vincoli:** PAPER ONLY. Nessuna modifica a codice, strategia, filtri, punteggi, rischio, segreti o Render. Nessun merge, deploy, rerun o ordine.

## Sintesi esecutiva

- **SPUTNIK:** ultimo monitor schedulato [#42361443562](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42361443562), su main, 09:50:55–09:51:08 UTC, SUCCESS. Al controllo era trascorsa circa 1h15m dal completamento. La scansione ha trovato due correlazioni, ma nessun evento attivo (events vuoto) e nessuna direzione operativa. Ha inviato un digest intelligence #717 e due messaggi GOLD #718/#719, tutti con ACK API; il candidato GOLD è NEUTRAL/NO_DIRECTION e NOT_EXECUTED.
- La voce RSS individuale #43499 è stata rilevata **6h38m14.443s** dopo la pubblicazione. È classificata MEDIA / OTHER, senza analogo storico: non è un catalizzatore commodity dimostrato. Una seconda voce è una pagina generale TRUTH_ARCHIVE senza timestamp individuale, ma la reazione è classificata TRADE_ESCALATION per analogia storica. È un'associazione page-level non sufficiente a dimostrare un nuovo evento.
- Il commit [1282aa3](https://github.com/andreameloni1984-sys/trump-trucker/commit/1282aa3cf75f491b71d5d68926e42fe0de2a6945) dimostra che il runtime continua a scrivere sputnik_state.json direttamente su main. La PR #144 che propone un branch separato è aperta e non integrata; il confronto attuale è 8 commit ahead / 21 behind.
- Il polling SPUTNIK [#42358078695](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42358078695) è SUCCESS; il log dice Pending updates: 0. Questo non prova consegna Telegram al dispositivo.
- **GAGARIN:** ultimo monitor schedulato [#42357485498](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42357485498), su main, 08:55:05–08:55:23 UTC, SUCCESS. Al controllo era trascorsa circa 2h11m dal completamento. In questo audit è stato recuperato il log completo (contrariamente al limite di accesso indicato nel rapporto precedente); il run non ha pubblicato artefatti Actions.
- Il monitor GAGARIN mostra tutte le otto commodity MARKET_CLOSED, con quote Yahoo vecchie di circa 11h–13h40m. WTI SHORT, Argento LONG e Mais LONG sono soltanto PAPER_WATCH, bloccati da dati stale e trigger non confermati/discordanti; non hanno entry, SL, TP o ATR. Il board Telegram #3712 è stato accettato dall'API, ma il corpo non è conservato e non si può attribuire ai tre candidati.
- Il job GAGARIN espone DATABASE_URL vuoto. Il monitor ha registrato 0 nuove entry, 0 outcome aggiornati e 0 nuovi feedback. La persistenza PostgreSQL condivisa non è dimostrata su main.
- Il ledger passa da **45 a 52 record**, con **52 firme uniche, 52 source ID unici e zero duplicati**. Sono state aggiunte sette osservazioni di questo run, tutte classificate come intelligence, WATCH o notifica non attribuibile, non come trade.
- **Campione di trade con fill e outcome verificabili: 0.** Fill verificati 0; SL/TP verificati 0; win rate e average R N/D.

## 1. GitHub Actions e cadenza

### SPUTNIK

- Monitor [#42361443562](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42361443562): evento schedule, branch main, creato 09:50:55 UTC, completato 09:51:08 UTC, SUCCESS.
- Step del job: checkout, configurazione Telegram, regression tests, esecuzione collector SPUTNIK e persistenza stato; tutti SUCCESS.
- Run precedente del collector: [#42331705890](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42331705890), creato 02:57:24 UTC. Intervallo fra gli avvii: circa 6h53m31s.
- Workflow main [trump_tracker.yml](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/.github/workflows/trump_tracker.yml): cron 2-59/5 * * * *. La run 09:50:55 non cade nel minuto nominale; GitHub non espone in questo audit l'istante originario di schedulazione, quindi il ritardo del dispatcher non è quantificabile.
- Polling separato [#42358078695](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42358078695): SUCCESS alle 09:03:26–09:03:34 UTC; log: Pending updates: 0.

### Persistenza SPUTNIK

Il commit [1282aa3](https://github.com/andreameloni1984-sys/trump-trucker/commit/1282aa3cf75f491b71d5d68926e42fe0de2a6945), creato alle 09:51:03 UTC, modifica soltanto sputnik_state.json. Il diff mostra:
- updated_at=2026-11-07T09:51:01.503631Z;
- events vuoto;
- offset Telegram persistito;
- due nuove voci in intelligence_history.

Il workflow main mantiene contents: write e termina con git push origin main: la scrittura runtime sul branch di codice è quindi confermata. La PR [#144](https://github.com/andreameloni1984-sys/trump-trucker/pull/144) è OPEN, non merged; confronto con main: 8 ahead / 21 behind. Il commento PRAVDA esistente #6705432930 contiene già questa evidenza e non è stato duplicato.

### GAGARIN

- Monitor [#42357485498](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42357485498): schedule, main, creato 08:55:05 UTC, completato 08:55:23 UTC, SUCCESS.
- Step: checkout, setup Python, dipendenze, validazione config, compile e python main.py; tutti SUCCESS.
- Run precedente monitor: [#42328183997](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42328183997), 02:13:56 UTC. Intervallo fra gli avvii: circa 6h41m09s.
- Workflow main [gagarin-monitor.yml](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/gagarin-monitor.yml): cron */15 * * * *.
- Il run più recente non ha artefatti Actions. Il log del job è stato però recuperato integralmente in questo controllo.

## 2. SPUTNIK — intelligence e messaggi effettivi

### Item RSS #43499 / Telegram #717

Record persistito:
- event ID: 55dc05ab6915f760a77f4714;
- URL: [trumpstruth.org/statuses/43499](https://www.trumpstruth.org/statuses/43499);
- titolo: “Quote post from November 7, 2026”;
- pubblicato: 03:12:47 UTC;
- rilevato: 09:51:01.443735 UTC;
- ritardo: 6h38m14.443s;
- domini: MEDIA;
- event type: OTHER;
- storico: NO_ANALOGUE.

Il digest #717 è stato accettato dall'API Telegram con round-trip 436 ms. È un item pubblico datato, ma il log non dimostra un catalizzatore economico/commodity.

### Record page-level TRUTH_ARCHIVE

Secondo record:
- event ID: ce679ecd83664e21e503141d;
- URL: [trumpstruth.org](https://www.trumpstruth.org/);
- published vuoto;
- evidenza: PUBLIC_SOURCE_TEXT_PAGE_LEVEL;
- action_reaction.event_type=TRADE_ESCALATION;
- analogo storico: china_tariff_escalation_2025_10.

Il contenuto è una pagina aggregata che mostra più post, non un singolo post identificato con data e permalink. La classificazione storica non prova una nuova escalation corrente. Lo stato persistito mantiene events vuoto; non è stato promosso un evento attivo. Il caso è stato aggiunto al commento PRAVDA esistente #6705299988 nella [PR #148](https://github.com/andreameloni1984-sys/trump-trucker/pull/148).

### GOLD #718/#719 — NO_DIRECTION

- #718: GOLD; bias preliminare NEUTRAL; priorità/score 70; tecnica 5m UNAVAILABLE; NO_DIRECTIONAL_NEWS; decisione WATCH; stato NO_DIRECTION.
- #719: scheda CFD GOLD; bias NEUTRAL; tecnica e D-L-A non valutati/NO_DIRECTION; NOT_EXECUTED.
- ACK API: #718 432 ms; #719 398 ms. ACK API non equivale a consegna al dispositivo.
- Ticker: GC=F è soltanto il mapping configurato; ticker runtime non confermato.
- Mercato: futures continuous front-month; scadenza esatta e indipendenza upstream non verificate.
- Provider/timestamp/età quotazione: non esposti; NARWHAL NOT_CONFIGURED.
- Entry, SL, TP e ATR: assenti. Il messaggio dice esplicitamente di non usare i livelli del front-month continuo.

Il punteggio 70 non è validità operativa. Non c'è direzione LONG/SHORT dimostrata, fill o trade. Le notifiche di test precedenti al collector, incluso il message_id=731 simulato, sono state escluse dalle prove di produzione.

## 3. GAGARIN — quotazioni e classificazioni del run #42357485498

Il run riporta PAPER_TRADING_ONLY=1 e 10 strumenti analizzati: 8 commodity operative e 2 Forex ausiliari. Tutte le commodity risultano MARKET_CLOSED.

| Strumento | Provider | Quote age | Direzione / classificazione | Prob. / Q / C |
|---|---|---:|---|---:|
| Brent | YAHOO | 39.618,3 s | nessuna; PAPER_WATCH | 58 / 40 / 25 |
| WTI | YAHOO | 39.618,0 s | SHORT; PAPER_WATCH | 66 / 57,5 / 37 |
| Soia | YAHOO | 49.218,9 s | nessuna; PAPER_WATCH | 30 / 0 / 0 |
| Oro | YAHOO | 39.616,5 s | nessuna; PAPER_WATCH | 30 / 0 / 0 |
| Grano | YAHOO | 49.218,5 s | nessuna; PAPER_WATCH | 38 / 15 / 5 |
| Argento | YAHOO | 39.617,6 s | LONG; PAPER_WATCH | 59 / 49,5 / 32 |
| Mais | YAHOO | 49.218,7 s | LONG; PAPER_WATCH | 63 / 52,5 / 35 |
| Rame | YAHOO | 39.617,8 s | nessuna; PAPER_WATCH | 40 / 15 / 5 |

Le età corrispondono a circa 11h per Brent/WTI/Oro/Argento/Rame e circa 13h40m per Soia/Grano/Mais. EUR/USD e GBP/USD sono ancora presenti solo come contesto FX ausiliario, provider BIQUOTE, entrambi MARKET_CLOSED e stale (~39.619 s). Nessun ticker runtime, timestamp esatto della quota, prezzo di riferimento, market type o scadenza è esposto nel log.

### Tre WATCH direzionali

1. **WTI SHORT** — generato nel log alle 08:55:20.3426128 UTC; probabilità 66, quality 57,5, confidence 37; bloccato da LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH e FINAL_CONFLUENCE_FAIL.
2. **Argento LONG** — 08:55:20.3430970 UTC; probabilità 59, quality 49,5, confidence 32; bloccato da dati stale, trigger non confermato/discordante, RR_FAIL e CONFIDENCE_FAIL.
3. **Mais LONG** — 08:55:20.3431724 UTC; probabilità 63, quality 52,5, confidence 35; bloccato da dati stale, trigger non confermato/discordante e RR1_FAIL.

Per tutti e tre: nessun entry, SL, TP1/2/3 o ATR; ticker runtime, market type e scadenza non esposti; nessun alert individuale. Le tre righe sono osservazioni WATCH del log, non tre trade né tre nuove righe feedback.

### Board Telegram #3712

Il log riporta Telegram SEND CONFIRMED | message_id=3712 | api_roundtrip=443ms. Il corpo del board non è conservato: non è possibile attribuire il messaggio a WTI, Argento o Mais. L'ACK API non prova consegna al dispositivo.

Riepilogo feedback del run:
- Recorded entries: 0;
- Updated open outcomes: 0;
- New feedback signals: 0;
- New additional live forecasts: 0;
- signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D.

## 4. Journal e legacy GAGARIN

File main letti:
- journal.csv: 11 righe del 17 ottobre, tutte con esito “nessun segnale”;
- data/paper_open.json: posizione legacy P0001 WTI LONG, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55, status OPEN, PnL null;
- paper_trade_log.csv: una riga WTI del 8 ottobre LEGACY_IMPORT, con gli stessi livelli.

P0001 in data/paper_open.json e la riga in paper_trade_log.csv sono lo stesso ticket, non due operazioni. Mancano signal_id, fill indipendente, ticker esecutivo, provider, quote timestamp, market type e scadenza. Esito: **ESITO NON VERIFICABILE**; non è conteggiato come trade con performance.

- commodities_prediction_log.json: 981 record, 945 PENDING e 36 NEUTRALE; ultimo record creato 2026-09-15 15:45:04 UTC. L'ultima riga è Benzina RBOB LONG con action “COMPRA ORA”, ma status PENDING: non prova fill o risultato.
- commodities_monitor_state.json e commodities_direction_state.json: aggiornamenti del 15–17 settembre.
- gagarin_feedback.csv: non presente nell'albero pubblico main.
- Nell'ambiente del run #42357485498, DATABASE_URL è esplicitamente vuoto; NARWHAL_API_KEY è vuoto. Il monitor completa comunque con SUCCESS, ma non dimostra persistenza PostgreSQL durevole. La PR #202 è ancora DRAFT. Il commento PRAVDA esistente #6673569819 è stato aggiornato con la nuova prova runtime; nessun secret è stato letto o modificato.

## 5. Motore outcome e PR

### GAGARIN PR #192

[PR #192](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192) è OPEN, non integrata; confronto con main: 6 ahead / 3 behind. Il branch aggiunge provider, quote symbol, market type, contract month/expiry e matching del contratto; se la stessa candela OHLC tocca SL e uno o più TP, registra ESITO NON VERIFICABILE.

**Rettifica metodologica:** la precedente osservazione PRAVDA su idx=max(hit_targets) è stata corretta nel commento #6702240640. Con target ordinati, se il target più lontano è raggiunto e lo SL non è toccato, il massimo target nel range è stato effettivamente raggiunto; non è un'ambiguità intrabar. L'ambiguità rilevante è SL e TP nella stessa candela, già gestita dalla PR. Su main, invece, resta il vecchio matching per simbolo/timeframe e lo stesso-bar SL+TP viene classificato STOP: la correzione non è ancora attiva.

### Altre PR rilevanti

- SPUTNIK [#148](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN, non-draft, 2 ahead / 9 behind; blocco ripetizioni senza nuovo item-level. I test ranking e item-intelligence del branch risultano SUCCESS; non è integrata.
- SPUTNIK [#144](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN, non merged, 8 ahead / 21 behind; propone persistenza su branch separato, ma main continua a pushare sputnik_state.json.
- SPUTNIK [#145](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): provenienza quote ancora in revisione.
- GAGARIN [#233](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/233): DRAFT, stacked su #207; distingue SPOT senza scadenza da EXPIRING_FUTURE con scadenza, ma non aggiunge feed Trading 212, quote retrieval o registry verificato. Nessun accesso Trading 212 è dimostrato.
- GAGARIN [#202](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): DRAFT; persistenza PostgreSQL dipendente dal DATABASE_URL, vuoto nel run corrente.
- GAGARIN [#175](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): OPEN, non integrata; gestisce il conflitto webhook/polling 409 senza cancellare il webhook.

### Telegram polling GAGARIN

Il run [#42317191549](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42317191549), 2026-11-07 00:16:15 UTC, fallisce con HTTP/API 409: webhook attivo, polling incompatibile. Il workflow main [telegram-polling.yml](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/.github/workflows/telegram-polling.yml) dichiara */5 7-21 * * 1-5; il run è etichettato schedule ma il timestamp è sabato 00:16 UTC, fuori dal cron. La causa della discrepanza non è dimostrata. Il workflow legacy telegram-listener.yml è disabilitato e dichiara che il webhook gestisce gli update. PR #175 non è integrata; nessuna consegna Telegram al dispositivo è stata verificata.

## 6. Ledger PRAVDA

Ledger aggiornato: [pravda-signal-ledger-2026-11-07.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-07.csv).

- Record precedenti: 45.
- Nuove osservazioni: 7 (RSS #717; pagina archive page-level; GOLD #718/#719; WTI WATCH; Argento WATCH; Mais WATCH; board #3712).
- Totale: **52 record**.
- Firme uniche: **52**.
- Source ID unici: **52**.
- Duplicati: **0**.

Le tre righe WATCH GAGARIN sono osservazioni di classificazione, non feedback signals; il run dichiara zero nuove live forecasts. I messaggi #717–#719 e #3712 hanno ACK API, non prova di consegna al dispositivo.

## 7. Esiti e statistiche

- Nuove operazioni con fill verificato: **0**.
- SL verificati: **0**.
- TP verificati: **0**.
- Outcome same-contract verificabili: **0**.
- WTI legacy P0001: OPEN nei file storici, fill e contratto non dimostrati; **ESITO NON VERIFICABILE**.
- WATCH e NO_DIRECTION: **NON_TRADE**, non successi né perdite.
- Win rate: **N/D**.
- Average R: **N/D**.

Non sono state usate candele spot per valutare futures, né contratti/scadenze differenti. Per i nuovi candidati non esistono livelli operativi o identità contrattuale sufficiente per avviare un confronto forward.

## 8. Segnalazioni PRAVDA eseguite e prossimo controllo

Commenti esistenti aggiornati, senza duplicare discussioni:
- [SPUTNIK PR #148 — #6705299988](https://github.com/andreameloni1984-sys/trump-trucker/pull/148#issuecomment-6705299988): item RSS MEDIA/OTHER tardivo e record page-level senza data.
- [GAGARIN PR #202 — #6673569819](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202#issuecomment-6673569819): DATABASE_URL vuoto nel run #42357485498.
- [GAGARIN PR #192 — #6702240640](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6702240640): rettifica della precedente critica su più TP nella stessa candela.

Prossimo controllo:
1. verificare la prossima effettiva esecuzione monitor su main e misurare la cadenza reale;
2. alla riapertura delle sessioni, verificare quote fresche con ticker, provider, timestamp, market type e scadenza;
3. controllare che PR #144, #148, #192, #202, #233 e #175 siano ancora nello stato dichiarato;
4. verificare la persistenza GAGARIN solo dopo prova runtime del backend e del secret configurato dal proprietario;
5. valutare un outcome solo dopo un fill PAPER documentato e candele successive dello stesso identico strumento/contratto.

**Nessun codice modificato. Nessuna strategia, filtro, punteggio o rischio modificato. Nessun merge, deploy, rerun, ordine reale, modifica a Render o ai segreti. Nessun servizio a pagamento. Nessun accesso Trading 212 o consegna Telegram al dispositivo dichiarati. PAPER ONLY.**
