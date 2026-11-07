# PRAVDA — Audit indipendente SPUTNIK / GAGARIN

**Controllo:** 2026-11-07 11:53:42 UTC (12:53:42 Europe/Rome)  
**Perimetro:** ultime GitHub Actions, log integrali dei job, notifiche/risultati, journal e feedback pubblici, codice feedback su `main`, PR e ledger PRAVDA.  
**Vincoli:** PAPER ONLY. Nessuna modifica a codice, strategia, filtri, punteggi, direzione, rischio, segreti o Render. Nessun merge, deploy, rerun o ordine reale.

## Sintesi esecutiva

- **SPUTNIK:** ultimo monitor schedulato [#42361443562](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42361443562), 09:50:55–09:51:08 UTC, SUCCESS. Al controllo erano trascorse **2h02m34s** dal completamento. Ha inviato digest intelligence #717 e due messaggi GOLD #718/#719; il contenuto GOLD è **NEUTRAL / NO_DIRECTION**, 5m tecnico unavailable, NARWHAL non configurato, nessun livello e **NOT_EXECUTED**.
- **GAGARIN:** ultimo monitor schedulato [#42357485498](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42357485498), 08:55:05–08:55:23 UTC, SUCCESS. Al controllo erano trascorse **2h58m19s**. Nessuna nuova scansione schedulata successiva nelle ultime esecuzioni controllate.
- I test PR non sono stati contati come monitor di mercato. Nessuno dei due job ha prodotto artifact scaricabili.
- Il ledger PRAVDA resta a **52 record, 52 firme uniche, 52 source ID unici, zero duplicati**. Tutti i messaggi/candidati dei due monitor sopra erano già registrati: **nessuna nuova riga** da aggiungere.
- **Fill verificati: 0. SL verificati: 0. TP verificati: 0. Outcome finanziari verificabili: 0.** Win rate e Average R: N/D.

## 1. GitHub Actions e cadenza

### SPUTNIK
- Monitor: [run #42361443562](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42361443562), evento `schedule`, branch `main`, SHA di checkout `8c1e070290bf677293d549b05ed9b5bc91ce23b6`.
- Polling Telegram separato: [run #42358078695](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42358078695), 09:03:26–09:03:34 UTC, SUCCESS; log: `Pending updates: 0`. Questo prova che il runner ha completato il polling senza aggiornamenti pendenti, non la consegna di un messaggio a un dispositivo.
- Il workflow dichiara cron `2-59/5 * * * *`; il polling `*/5 * * * *`. La cadenza effettiva osservata non è regolare.
- Il job del monitor esegue 30 test unitari prima del collector: tutti superati in 0,033 s. Il log di test contiene un invio simulato `message_id=731` con round-trip 0 ms: **non è un messaggio Telegram di produzione**.
- Durante la stessa run il workflow ha committato `sputnik_state.json` direttamente su `main`: commit [1282aa3](https://github.com/andreameloni1984-sys/trump-trucker/commit/1282aa3cf75f491b71d5d68926e42fe0de2a6945), con `git push origin main`. La PR #144, che sposta lo stato sul branch dedicato, è ancora aperta e non integrata.
- HEAD di `main` al controllo: [6682f93](https://github.com/andreameloni1984-sys/trump-trucker/commit/6682f93b6563a3fa2d25539da9535b153b093d60), commit documentale dell'audit precedente.

### GAGARIN
- Monitor: [run #42357485498](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42357485498), evento `schedule`, branch `main`, SHA `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`.
- Cron configurato: `*/15 * * * *`; il divario effettivo dall'ultimo monitor è molto superiore a 15 minuti.
- Nessun artifact scaricabile dal run.
- Non è stato osservato un nuovo run di monitor schedulato dopo #42357485498 nella prima pagina delle ultime 30 esecuzioni consultate. I run PR sono stati esclusi dal conteggio.

## 2. SPUTNIK — segnali e intelligence

### Collector e fonti
Il log del run #42361443562 riporta:
- SEC CIK 0001849635: HTTP 403; cooldown 21.600 secondi; filing 0.
- White House RSS: HTTPError.
- `findings=2`, ma il digest distingue **un solo item pubblico individuale verificabile**; l'altra correlazione è page-level.
- Nessuna nuova operazione documentata.
- Handoff GAGARIN disabilitato: `GAGARIN_CLOUD_API_URL/API_KEY not configured`.
- NARWHAL abilitato come riferimento ma `NARWHAL_API_KEY` vuota; nel messaggio è indicato `NOT_CONFIGURED`.

### Item RSS individuale
- ID: `55dc05ab6915f760a77f4714`.
- URL: https://www.trumpstruth.org/statuses/43499
- Pubblicazione: 03:12:47 UTC.
- Rilevamento/digest: circa 09:51:03 UTC.
- Ritardo di rilevamento: circa **6h38m16s**.
- Classificazione: MEDIA / OTHER; nessuna analogia storica.
- Telegram #717: API ACK, round-trip dichiarato 436 ms.
- È intelligence pubblica, **non un catalizzatore commodity direzionale dimostrato**.

### Correlazione TRUTH_ARCHIVE page-level
- ID: `ce679ecd83664e21e503141d`.
- Fonte: pagina generale TRUTH_ARCHIVE, non un singolo post.
- Timestamp individuale di pubblicazione: assente.
- Classificazione/analogia: TRADE_ESCALATION / `china_tariff_escalation_2025_10`.
- Non va conteggiata come nuovo evento tariffario individualmente verificato.

### GOLD #718/#719
- Run: #42361443562; generazione intorno a 09:51:03 UTC.
- #718 analisi GOLD; #719 scheda CFD; API ACK rispettivamente 432 ms e 398 ms.
- Bias preliminare: **NEUTRAL**.
- Tecnica 5m: **UNAVAILABLE**; D-L-A: NEUTRAL / NO_DIRECTION.
- Score: 70/100, che non certifica validità operativa.
- Decisione: WATCH / NO_DIRECTION; trade PAPER NOT_EXECUTED.
- Entry, SL, TP, ATR: assenti.
- `GC=F` è un mapping configurato, non il ticker runtime verificato; il log dichiara front-month continuo, scadenza esatta e indipendenza upstream non verificate. NARWHAL non configurato.
- Nessun esito finanziario da valutare.

### PR SPUTNIK
- [PR #144 — Persist state outside main](https://github.com/andreameloni1984-sys/trump-trucker/pull/144): OPEN, non draft, 8 commit ahead e **23 behind** rispetto a main. La run #42361443562 dimostra che main continua a ricevere il commit di stato.
- [PR #148 — Stop repeating recommendations](https://github.com/andreameloni1984-sys/trump-trucker/pull/148): OPEN, non draft, 2 ahead e **11 behind** rispetto a main. Il diff di `item_level_public_catalysts()` richiede `PUBLIC_RSS_ITEM`, event_id, URL e published, ma non esclude `event_type=OTHER`. Il run corrente fornisce un caso concreto: l'item RSS era MEDIA/OTHER e ha comunque innescato i messaggi GOLD neutrali #718/#719.
- Commento PRAVDA aggiunto alla #148: [issue comment #6706624290](https://github.com/andreameloni1984-sys/trump-trucker/pull/148#issuecomment-6706624290). Richiesto test per item completo ma non-catalitico `OTHER`; nessuna modifica strategica richiesta.
- [PR #145 — quote provenance](https://github.com/andreameloni1984-sys/trump-trucker/pull/145): OPEN; non integrata.

## 3. GAGARIN — monitor, strumenti e candidati

Il log #42357485498 dichiara: `SESSION FILTER: 8 commodities operative; EUR/USD e GBP/USD restano ausiliari`.

### Quotazioni
Tutte le otto commodity erano `MARKET_CLOSED`; fallback esplicito `MARKET_CLOSED`. Provider Yahoo. Età esposta dal log:
- Brent 39.618,3 s (circa 11h00m18s).
- WTI 39.618,0 s.
- Soia 49.218,9 s (circa 13h40m19s).
- Oro 39.616,5 s.
- Grano 49.218,5 s.
- Argento 39.617,6 s.
- Mais 49.218,7 s.
- Rame 39.617,8 s.

EUR/USD e GBP/USD sono contesto FX non operativo, provider BiQuote, anch'essi `MARKET_CLOSED`, età circa 39.619 s.

Il log non espone timestamp puntuale della quotazione, ticker runtime, market type o scadenza. Le età non sostituiscono il timestamp. Non è quindi possibile costruire un confronto successivo sullo stesso contratto.

### Classifica
- WTI SHORT: Prob 66, Quality 57,5, Confidence 37; bloccato da LIVE_DATA_NOT_FRESH, trigger non confermato e mismatch direzionale.
- Argento LONG: Prob 59, Quality 49,5, Confidence 32; bloccato da dati stale, trigger non confermato/mismatch, RR e confidence.
- Mais LONG: Prob 63, Quality 52,5, Confidence 35; bloccato da dati stale, trigger non confermato/mismatch e RR1.
- Gli altri cinque strumenti commodity non avevano direzione operativa; EUR/USD e GBP/USD sono esplicitamente contesto FX non operativo.
- Tutti i candidati sono `PAPER_WATCH`; nessuno ha entry, SL, TP o ATR operativi completi.

Timestamp di generazione delle tre classificazioni:
- WTI: 08:55:20.3426128 UTC.
- Argento: 08:55:20.3430970 UTC.
- Mais: 08:55:20.3431724 UTC.

Il board Telegram #3712 è stato accettato dall'API in 443 ms. Il corpo del messaggio non è conservato; non è possibile attribuire con certezza il board ai tre candidati né assegnare loro un timestamp di invio individuale.

Riepilogo del run:
`Recorded entries: 0`; `Updated open outcomes: 0`; `New feedback signals: 0`; `New additional live forecasts: 0`; `signals=0 open=0 closed=0`.

## 4. Journal e feedback GAGARIN

File pubblici letti direttamente:
- `journal.csv`: 11 righe, tutte con esito “nessun segnale”.
- `data/paper_open.json`: contiene P0001, WTI LONG, stato OPEN, entry 96,24, SL 89,37, TP1 103,11, TP2 106,55, PnL null.
- `paper_trade_log.csv`: la stessa posizione P0001 come import legacy del 2026-10-08 16:23 UTC; campi quote_provider, quote_symbol, quote_timestamp, quote_market_type ed execution_* vuoti. Nota: “Chiusura spot 6 ottobre 2026. Nessun esito.”
- P0001 in `paper_open.json` e `paper_trade_log.csv` è **un solo ticket legacy**, non due trade.
- `commodities_prediction_log.json`: 981 record; ultimo creato il 2026-09-15 15:45:04 UTC, action “COMPRA ORA”, status PENDING. Action/score non provano fill o esecuzione.
- `gagarin_feedback.csv`: assente dal repository pubblico.

Nel log del monitor `DATABASE_URL` è vuoto nelle fasi di esecuzione. Su main, `engine.feedback.storage_backend()` sceglie il backend locale CSV quando la variabile è vuota. Il run è comunque terminato SUCCESS con zero entry/feedback. Questo non dimostra persistenza durevole tra runner.

### PR GAGARIN
- [PR #192 — exact-contract e same-candle ambiguity](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192): OPEN, non draft, mergeable, 6 ahead / 3 behind rispetto a main. Le sei suite sul branch risultano SUCCESS, ma non equivalgono a codice integrato su main. Main attuale costruisce ancora l'identità soprattutto da symbol/direction/timeframe/livelli/bar_ts e, se la stessa candela tocca SL e TP, assegna STOP prima di considerare il target. La PR aggiunge provider/ticker/market/contract e classifica SL+TP nella stessa candela come `ESITO NON VERIFICABILE`.
- Rettifica mantenuta: la selezione del TP più lontano quando è raggiunto e SL non è toccato non è, da sola, un difetto; l'ambiguità critica è SL e TP nella stessa candela.
- **Nuovo rilievo:** la docstring di `_market_contract_match` dichiara matching provider/ticker/market, ma la funzione confronta ticker, market type e identità futures; non confronta `row.quote_provider` con il provider della serie corrente. Il provider è nella firma/record ma non nel guard di matching. Commento PRAVDA aggiunto: [#6706619879](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6706619879). Richiesta verifica esplicita o chiarimento della policy; nessuna modifica al codice.
- [PR #202 — PostgreSQL journal/feedback](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/202): DRAFT, 18 ahead / 1 behind. Propone persistenza durevole e fallimento del monitor se DATABASE_URL manca o il DB non è raggiungibile. Non è integrata; il valore del secret non è stato letto né modificato.
- [PR #233 — identità CFD SPOT senza expiry](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/233): DRAFT, 21 ahead / 1 behind dalla PR #207. Distingue SPOT da EXPIRING_FUTURE; il registro resta vuoto. Non aggiunge feed/quote Trading 212, livelli, Governor, journal o ordini.
- [PR #175 — webhook Telegram](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175): OPEN, non draft, non integrata. La correzione gestisce il 409 evitando deleteWebhook/ack impropri; non prova consegna al dispositivo. L'errore 409 già osservato resta evidenza storica; in questo controllo non è stato dimostrato un nuovo errore runtime GAGARIN.

## 5. Ledger PRAVDA e outcome

Ledger: [pravda-signal-ledger-2026-11-07.csv](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/reports/pravda-signal-ledger-2026-11-07.csv).

Verifica parser CSV:
- 52 record.
- 52 firme `audit_signature` uniche.
- 52 `source_record_id` unici.
- 0 duplicati.
- Distribuzione: SPUTNIK 11; GAGARIN 41.

I run #42361443562 e #42357485498 sono già rappresentati nel ledger; nessuna nuova riga è stata aggiunta.

Lacune strutturali nel ledger misto (include intelligence, WATCH, predizioni storiche e legacy; i campi N/A non equivalgono a trade incompleti):
- sent_at_utc mancante/non registrato: 32 record;
- ticker non esposto: 22;
- market_type non registrato: 40;
- contract_expiry non registrata: 50;
- provider non registrato: 35;
- quote_timestamp non registrato: 49;
- entry, SL e TP1 non valorizzati: 24 ciascuno;
- ATR non valorizzato: 40.

Esiti:
- fill dimostrati: 0;
- SL verificati: 0;
- TP verificati: 0;
- outcome finanziari verificabili: 0;
- win rate: N/D;
- average R: N/D.

P0001 WTI resta `OPEN_LEGACY` con fill/contratto non provati e outcome non verificabile. Non è incluso come trade verificato.

## 6. Commenti PRAVDA e prossimi controlli

Commenti nuovi, senza modificare codice:
- SPUTNIK PR #148: [#6706624290](https://github.com/andreameloni1984-sys/trump-trucker/pull/148#issuecomment-6706624290), item RSS `OTHER` ancora idoneo al gate proposto.
- GAGARIN PR #192: [#6706619879](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/192#issuecomment-6706619879), provider registrato ma non confrontato nel guard.

Prossimo controllo:
1. Verificare nuove esecuzioni `schedule` su main, distinguendole dai test PR.
2. Alla riapertura, acquisire timestamp, ticker, provider, market type e scadenza della stessa serie prima di qualsiasi outcome.
3. Verificare se #144 sposta davvero la persistenza SPUTNIK fuori da main e se #148 esclude item non-catalitici.
4. Verificare #192 su una base aggiornata e il confronto del provider.
5. Verificare #202 solo dopo prova runtime di backend PostgreSQL durevole.
6. Non valutare P0001 né alcun WATCH senza fill e identità del contratto.

**Conclusione:** monitor SPUTNIK e GAGARIN non regolari; nessun nuovo trade; zero outcome finanziari certificabili. Nessun merge/deploy/rerun/ordine reale; nessun accesso Trading 212 dichiarato; nessuna modifica a segreti o Render. PAPER ONLY.
