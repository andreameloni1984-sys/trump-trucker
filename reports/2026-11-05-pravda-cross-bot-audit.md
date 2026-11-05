# PRAVDA — audit incrociato SPUTNIK / GAGARIN
**Snapshot iniziale:** 2026-11-05 15:58 UTC  
**Ultimo aggiornamento:** 2026-11-05 17:44 UTC  
**Scope:** artefatti GitHub pubblici, journal/feedback e GitHub Actions. Nessuna modifica a codice, strategia, filtri, score, rischio, secret o Render; nessun merge/deploy/ordine.

Ledger deduplicato: [pravda-signal-ledger-2026-11-05.csv](pravda-signal-ledger-2026-11-05.csv) — 25 record (21 candidati storici GAGARIN, 1 ticket legacy GAGARIN, 2 WATCH GAGARIN, 1 candidato CFD SPUTNIK). I 981 ID del prediction log GAGARIN sono unici. Nessun outcome verificato.

## Esito complessivo
- Esiti verificati: **0**. Campione verificabile: **0**. Win rate, average R e altre statistiche: **N/D**.
- Nessun trade può essere classificato TP o SL con le prove attuali.
- NOT_EXECUTED, PAPER_WATCH, PENDING e score non sono trade eseguiti.

## SPUTNIK — candidato CFD GOLD
Run [42010313054](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42010313054), 5 novembre 10:23:31–10:23:45 UTC.

- Telegram API confermata: messaggio analisi 697 e messaggio CFD 698.
- Strumento: GOLD. Mercato dichiarato: front-month continuo; scadenza esatta non disponibile.
- Bias catalizzatore LONG; nel messaggio preliminare la direzione tecnica è LONG, ma nel CFD TECNICA e D-L-A risultano SHORT (CONTRASTS). L'avviso MERCATO CONTRO BIAS è attivo.
- Entry 4134.2002; SL 4132.2287; TP1 4136.1717; TP2 4138.1432; ATR 1.3143; score 65/100.
- Stato EARLY_SETUP / TRADE PAPER NOT_EXECUTED. Nessun trade.
- Il log non mostra ticker runtime, provider effettivo, timestamp o età della quotazione. Il codice conserva quote_time/quote_provider/quote_symbol/quote_market_type ma il formatter CFD non li stampa. La mappatura Yahoo GOLD→GC=F esiste nel codice, ma il provider effettivamente usato in questo run non è dimostrato.
- NARWHAL NOT_CONFIGURED; scadenza esatta e indipendenza del cross-check non verificate; allineamento notizie NO_DIRECTIONAL_NEWS. SEC ha restituito HTTP 403 e il feed White House HTTPError.

**Valutazione:** ESITO NON VERIFICABILE. Mancano provenienza completa e scadenza del contratto; inoltre il trade è NOT_EXECUTED.

Lo stato [sputnik_state.json](https://github.com/andreameloni1984-sys/trump-trucker/blob/main/sputnik_state.json), aggiornato alle 10:23 UTC, contiene 500 intelligence_history (471 PUBLIC_RSS_ITEM e 29 page-level), tutti POTENTIAL_CORRELATION, e 667 intelligence_items. events e transactions sono vuoti: non è un journal di trade. L'ultimo record TRUTH_ARCHIVE è una cattura page-level senza data di pubblicazione, non un post datato.

## GAGARIN — ultimo monitor
Run [41995511121](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/41995511121), 5 novembre 08:34:23–08:34:48 UTC; precedente al merge PR #199.

- 10 strumenti: 8 commodities STALE (601–632s); EUR/USD e GBP/USD LIVE a circa 284s.
- Grano SHORT, probabilità 63, qualità 54, confidenza 35, PAPER_WATCH; bloccato da LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH e RR1/RR2/RR_FAIL.
- Nessun entry/SL/TP/ATR operativo. Telegram SEND CONFIRMED, message_id=3692, ma è un WATCH pre-alert.
- PAPER JOURNAL: 0 entries. FEEDBACK: 0 open outcomes aggiornati, 0 nuovi segnali, 0 nuove forecast; signals=0/open=0/closed=0, win_rate=N/D, avg_R=N/D.

### Journal e feedback
- Nel run DATABASE_URL è vuoto. Il backend è LOCAL_CSV_NO_DATABASE_URL.
- PR [#152](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/152), merge 2 novembre, ha rimosso la pubblicazione dei CSV operativi nel repository pubblico. È una correzione privacy corretta, ma lo storage privato non risulta distribuito/verificato: i CSV dei runner effimeri non persistono.
- [paper_trade_log.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/paper_trade_log.csv): una riga legacy WTI del 8 ottobre, LONG, entry 96.24, SL 89.37, TP1 103.11, TP2 106.55, status OPEN legacy. La nota cita chiusura spot del 6 ottobre e “Nessun esito”. Nessun provider, timestamp preciso, ATR, contratto di esecuzione o prova di fill. ESITO NON VERIFICABILE.
- [journal.csv](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/journal.csv): 11 righe del 17 ottobre, tutte “nessun segnale”.
- [commodities_prediction_log.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities_prediction_log.json): 981 righe dal 10 al 15 settembre, nessun provider. 21 etichette COMPRA ORA: 15 con operational_signal LONG e 6 con NO_OP_SIGNAL; tutte PENDING, senza outcome. Non sono prove di esecuzione.
- [commodities_daily_report_state.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities_daily_report_state.json) è fermo al 10 settembre (evaluated=0, pending=24); [commodities_monitor_state.json](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/commodities_monitor_state.json) al 17 settembre.
- [engine/feedback.py](https://github.com/andreameloni1984-sys/commodity-news-scanner/blob/main/engine/feedback.py) deduplica per symbol/direction/timeframe/livelli/candela e valuta solo candele successive; in caso di SL e TP nella stessa barra assegna SL. Ma lo schema non conserva quote timestamp, market type o scadenza e l'identità non include l'expiry: non basta sempre a certificare lo stesso contratto continuo dopo un roll.

## GitHub Actions — cadenza
Negli ultimi 24h: SPUTNIK main 4 run (cron ogni 5 min); SPUTNIK polling 4 (ogni 5 min); GAGARIN monitor 3 (ogni 15 min); GAGARIN polling 3, tutti falliti (ogni 5 min nelle ore configurate).

I run esaminati partono con created_at uguale a run_started_at; SPUTNIK main dura circa 14s, GAGARIN monitor circa 25s. Non emerge una coda runner. La causa delle invocazioni cron mancanti non è determinata: non attribuirla agli altri bot senza prova di saturazione o queue time.

Il polling GAGARIN fallisce con Telegram API error 409: webhook attivo, quindi getUpdates non può operare in modalità webhook. È un problema inbound; non annulla la conferma outbound del monitor.

## Correzioni già esistenti
- SPUTNIK [PR #125](https://github.com/andreameloni1984-sys/trump-trucker/pull/125), merge 4 novembre: aggiunge MERCATO CONTRO BIAS; il warning appare nel run 42010313054. Resta da riconciliare la divergenza tra analizzatore preliminare LONG e CFD/D-L-A SHORT.
- GAGARIN [PR #187](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/187) e [PR #188](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/188), merge 4 novembre: avvisi su disaccordo GAGARIN/LUBJANKA e contesto stale nei WATCH.
- GAGARIN [PR #199](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/199), merge 5 novembre 15:07 UTC: rimuove i blocchi orari intraday Forex. Cinque workflow post-merge sul commit 7ed290b risultano SUCCESS; nessun run gagarin-monitor successivo al merge è ancora disponibile, quindi l'effetto runtime resta da confermare.

## Difetti dimostrati da segnalare
1. SPUTNIK: il formatter CFD omette provider/ticker/timestamp/età quotazione pur avendo campi interni.
2. SPUTNIK: due messaggi dello stesso run danno direzioni tecniche opposte; warning presente ma snapshot/provenienza da riconciliare.
3. GAGARIN: feedback non persistente (DATABASE_URL vuoto; runner effimero).
4. GAGARIN: schema feedback privo di quote timestamp/market type/expiry.
5. GAGARIN: Telegram polling incompatibile con webhook attivo (409).
6. Entrambi: frequenza Actions osservata molto inferiore ai cron dichiarati; causa non accertata.

## Prossimo controllo
Verificare il primo monitor GAGARIN dopo PR #199; confrontare cron, created_at, run_started_at e queue time; ripristinare prima lo storage privato durevole; per ogni nuovo segnale conservare ticker, mercato, expiry, provider e timestamp prima di valutare candele successive dello stesso contratto. Dato mancante = ESITO NON VERIFICABILE.

**Sicurezza:** PAPER ONLY. Nessun ordine reale, accesso Trading212, modifica secret/Render, codice, merge o deploy. In questo run sono stati aggiunti solo il report e il ledger documentale.


---

## Addendum PRAVDA — controllo incrementale 2026-11-05 16:26 UTC

**Deduplicazione:** il ledger resta a 24 record (21 candidati storici GAGARIN, 1 ticket WTI legacy, 1 WATCH GAGARIN, 1 CFD SPUTNIK). Nessun nuovo segnale distinto è emerso nei run esaminati dopo lo snapshot precedente; non aggiungo righe duplicate o record di test. Tutti i 24 record restano senza esito verificabile; campione verificabile 0, win rate e R-multiples N/D.

### SPUTNIK — nessun nuovo run scanner dopo le 10:23 UTC

- Ultimo run schedulato principale ancora [42010313054](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42010313054), 2026-11-05 10:23:31–10:23:45 UTC. Nessun successivo run schedulato `trump_tracker.yml` compare nella cronologia Actions consultata fino alle 16:26 UTC, nonostante il cron `2-59/5 * * * *`.
- Il log mostra 1 sola correlazione pubblica. WHITE_HOUSE e TRUTH_ARCHIVE risultano non disponibili (OSError); SEC HTTP 403 con cooldown 21.600 secondi; 0 filing e 0 nuove operazioni documentate.
- Candidato GOLD: bias preliminare LONG, direzione tecnica nel messaggio preliminare LONG; nel CFD la tecnica e D-L-A sono SHORT/CONTRASTS. EARLY_SETUP, score 65/100, entry 4134.2002, SL 4132.2287, TP1 4136.1717, TP2 4138.1432, ATR 1.3143. Stato esplicito NOT_EXECUTED.
- Telegram API delivery confermata per messaggi 697 (analisi) e 698 (CFD), rispettivamente alle 10:23:40.295455 e 10:23:40.296948 UTC. Questo prova la risposta dell'API, non la lettura dell'utente né un trade.
- Restano assenti dal log provider effettivo, ticker runtime, timestamp/età della quotazione e scadenza del contratto. Il testo dichiara front-month continuo ma non identifica la scadenza; NARWHAL è NOT_CONFIGURED. Nessun confronto successivo con lo stesso contratto è quindi ammissibile: ESITO NON VERIFICABILE.
- Ultimo run schedulato del polling SPUTNIK consultato: [42004041198](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42004041198), 09:38:29 UTC; nessun successivo run schedulato del polling compare nella finestra consultata. Il daily summary [42038806143](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42038806143) è un riepilogo, non una nuova scansione.

### GAGARIN — PR #199 non ancora verificata a runtime

- Ultimo run schedulato del monitor ancora [41995511121](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/41995511121), 08:34:23–08:34:48 UTC, quindi precedente al merge della PR #199 alle 15:07 UTC.
- Il log di quel monitor riporta 8 commodities STALE (601–632 secondi) su YAHOO; EUR/USD e GBP/USD LIVE su BIQUOTE ma con età circa 284 secondi. Grano SHORT è soltanto PAPER_WATCH: LIVE_DATA_NOT_FRESH, trigger non confermato, mismatch di direzione e RR1/RR2/RR_FAIL. Nessun entry/SL/TP/ATR operativo, zero paper entries e zero feedback aggiornati. Telegram message_id 3692 conferma solo il WATCH pre-alert.
- Il run [42051693544](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42051693544), 15:07:08–15:07:22 UTC sul commit 7ed290b (PR #199), è un job di test/smoke, non il monitor di mercato. I 26 test indicati nel job passano; il comando `python -m soyuz_gagarin.main` termina con `PAPER_WATCH / ASSET_NOT_IN_UNIVERSE`, che non è un segnale negoziabile. Non prova l'effetto runtime della rimozione delle finestre Forex in `main.py`.
- Nessun run `gagarin-monitor.yml` successivo al merge compare nella cronologia schedulata consultata fino alle 16:26 UTC. La PR #199 resta quindi **merge verificato, comportamento del monitor post-merge non verificato**.
- L'ambiente del monitor precedente espone DATABASE_URL vuoto, `MONITOR_INTERVAL_MINUTES=15`, soglie runtime 40/30/35 e RR 2.5. Non sono state cambiate. Senza DATABASE_URL, il journal/feedback del runner non è dimostrato persistente.
- Il polling Telegram GAGARIN [42050795561](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42050795561), 15:01:51–15:02:18 UTC, fallisce con API 409: webhook attivo, quindi `getUpdates` non può funzionare in modalità polling. Il token risulta presente; nessun aggiornamento inbound è stato elaborato in quel run. Il daily summary [42046975638](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42046975638) è riuscito, ma non è una nuova scansione.

### GitHub Actions — cadenza e coda

Alla verifica delle 16:26 UTC:
- SPUTNIK scanner: cron ogni 5 minuti, ultimo scheduled run 10:23 UTC.
- SPUTNIK polling: cron ogni 5 minuti, ultimo scheduled run 09:38 UTC.
- GAGARIN monitor: cron ogni 15 minuti, ultimo scheduled run 08:34 UTC.
- GAGARIN polling: ultimo scheduled run 15:01 UTC, fallito per 409 webhook.
- I job osservati hanno `created_at` uguale a `run_started_at`; non emerge attesa in coda per quei run. Le mancate esecuzioni programmate sono reali nella cronologia consultata, ma la causa non è determinata: non attribuirle alla concorrenza con altri bot senza prova.

### Esito incrementale e prossima verifica

- Nuovi segnali negoziabili: 0.
- Nuovi trade paper registrati: 0.
- Nuovi esiti TP/SL verificabili: 0.
- Statistiche su campione verificabile: non calcolabili.
- Non è stato scaricato o usato un feed di prezzi di mercato per simulare l'esito del GOLD: ticker/expiry upstream non identificati; qualsiasi confronto spot o con un future generico sarebbe metodologicamente scorretto.
- Prossimo controllo: primo run schedulato effettivo del monitor GAGARIN dopo PR #199; primo nuovo run SPUTNIK; ripristino/diagnosi della cadenza cron senza presumere saturazione runner; per ogni nuovo candidato, conservare provider, quote timestamp, ticker/mercato/expiry e livelli prima di avviare il confronto outcome.

**Perimetro invariato:** audit documentale soltanto; nessun codice, strategia, filtro, score, rischio, secret o Render modificato; nessun merge/deploy/ordine. PAPER ONLY.


---

## Addendum PRAVDA — controllo incrementale 2026-11-05 17:44 UTC

**Deduplicazione e risultati:** ledger aggiornato da 24 a **25 record** con un solo nuovo WATCH GAGARIN (firma `PRAVDA-GAGARIN-WATCH-RUN42068931975-20261105T165250Z-WTI-SHORT`). Composizione: 21 candidati storici GAGARIN, 1 ticket legacy WTI, 2 WATCH GAGARIN, 1 candidato CFD SPUTNIK. Esiti TP/SL verificati: **0**. Campione verificabile: **0**. Win rate e R-multiples: **N/D**. I 2 WATCH sono classificati NON_TRADE; i 23 record storici/ticket/CFD restano ESITO NON VERIFICABILE. Nessun risultato di mercato è stato inferito.

### GAGARIN — primo monitor schedulato dopo PR #199

- Run [42068931975](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42068931975), 2026-11-05 16:52:29–16:52:58 UTC, SUCCESS, commit `7ed290b971e780828934d80aa3b936043769eaf6`. È il primo run effettivo `gagarin-monitor.yml` successivo al merge PR [#199](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/199) (15:07:05 UTC). Non è soltanto un test CI.
- Il codice attuale di `main.py` seleziona `enabled_commodities()`; `engine/session_filter.py` conserva tutti gli strumenti e non applica finestre intraday; `engine/forex_session.py` controlla il giorno feriale, non l'ora. La PR #199 risulta quindi presente nel codice eseguito. Il run ha analizzato tutti e 10 gli strumenti, inclusi EUR/USD e GBP/USD.
- Limite della prova runtime: il run è partito alle 16:52 UTC (17:52 Europe/Rome), ancora dentro la precedente fascia 14:00–18:00. Non dimostra da solo il comportamento fuori dalle vecchie finestre. Inoltre EUR/USD e GBP/USD sono ancora classificati `CONTESTO FX — NON OPERATIVO`; `operational_commodities()` esclude la categoria Forex. Conclusione: scansione Forex senza gate intraday nel codice, ma Forex non abilitato come sorgente autonoma di entry in questo monitor. Il banner del log continua a parlare di analisi nelle “rispettive finestre”, formulazione fuorviante rispetto al codice aggiornato.
- Dati del run: Soia, Mais, Grano, Rame, WTI, Argento, Oro e Brent sono tutti STALE su YAHOO, età 601.1–614.8 secondi. EUR/USD e GBP/USD sono etichettati LIVE su BIQUOTE, età rispettivamente 169.4 e 170.1 secondi; il log non espone il timestamp assoluto della quotazione, quindi la freschezza non è verificabile indipendentemente.
- Nuovo WATCH WTI SHORT: generato alle 16:52:46.404940 UTC; Telegram API confermata alle 16:52:50.681424 UTC, message_id=3698. Probabilità 66, qualità 54.5, confidenza 37.0. Stato PAPER_WATCH, bloccato da `LIVE_DATA_NOT_FRESH`, `TRIGGER_NOT_CONFIRMED`, `TRIGGER_DIRECTION_MISMATCH`, `RR_FAIL` e `FINAL_CONFLUENCE_FAIL`. Entry, SL, TP, ATR e prezzo di riferimento assenti. Provider YAHOO, age 601.1s; ticker provider, quote timestamp, mercato e scadenza non registrati. Firma e record aggiunti al ledger. È un pre-alert accettato dall'API, non un trade.
- PAPER JOURNAL: 0 entries; FEEDBACK: 0 aggiornamenti, 0 nuovi segnali, 0 nuove forecast; `signals=0/open=0/closed=0`. `DATABASE_URL` è vuoto nel job: nessuna prova di persistenza durevole del journal.
- L'ambiente del monitor imposta esplicitamente soglie runtime 40/30/35 e RR 2.5. Sono valori osservati nel log, non modificati da PRAVDA.

### GAGARIN — polling Telegram inbound

- Run [42050795561](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42050795561), 15:01:51–15:02:18 UTC, FAILURE. Il log riporta esattamente API error 409: webhook attivo e `getUpdates` incompatibile con webhook mode. Il token e la diagnostica bot risultano presenti; il polling non ha elaborato gli aggiornamenti. È un difetto del canale inbound e non smentisce i messaggi outbound confermati dal monitor.

### SPUTNIK — scansione e stato

- Ultimo run schedulato dello scanner principale ancora [42010313054](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42010313054), 10:23:31–10:23:45 UTC. Nella cronologia schedulata consultata fino alle 17:44 UTC non compare un successivo run `trump_tracker.yml`, benché il cron sia ogni 5 minuti. Nessun nuovo segnale scanner da aggiungere.
- Il candidato CFD GOLD del run 42010313054 resta EARLY_SETUP / NOT_EXECUTED: bias catalizzatore LONG contro tecnica/D-L-A SHORT; entry 4134.2002, SL 4132.2287, TP1 4136.1717, TP2 4138.1432, ATR 1.3143. Provider/ticker runtime/quote timestamp/expiry esatti assenti; front-month continuo non identifica una scadenza. Nessun confronto outcome sullo stesso contratto è ammissibile.
- Il polling SPUTNIK [42076754543](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42076754543) è riuscito alle 17:39:27–17:39:38 UTC: stato remoto caricato, 0 aggiornamenti pendenti. Non è una scansione di mercato.
- Il daily summary [42038806143](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42038806143) è riuscito alle 13:46:53–13:47:03 UTC; Telegram API ha confermato message_id=699. È un riepilogo dello stato, non un nuovo segnale o trade.

### GitHub Actions — frequenze e coda

- GAGARIN monitor: cron ogni 15 minuti; run schedulati recenti 01:43, 08:34 e 16:52 UTC. I gap sono incompatibili con la cadenza dichiarata.
- SPUTNIK scanner: cron ogni 5 minuti; ultimo run 10:23 UTC. SPUTNIK polling: cron ogni 5 minuti; ultimo run 17:39 UTC, ma nella finestra di 24 ore la cronologia mostra solo pochi run, non una scansione ogni 5 minuti.
- Nei run ispezionati `created_at` coincide con `run_started_at`; non emerge attesa in coda per questi esempi. Le invocazioni programmate mancanti sono dimostrate dalla cronologia, ma la causa resta non determinata. Non attribuire il fenomeno alla concorrenza tra bot senza log di queue time o altra prova.
- Il polling GAGARIN è inoltre fallito per 409; il suo run non può essere contato come ciclo inbound riuscito.

### Correzioni già esistenti e difetti da passare ai reparti

- GAGARIN PR [#199](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/199): merge verificato e primo monitor post-merge riuscito; resta da osservare un run fuori dalle vecchie finestre e chiarire la distinzione “Forex analizzato” vs “Forex operativo”.
- SPUTNIK PR [#125](https://github.com/andreameloni1984-sys/trump-trucker/pull/125): merge verificato; il candidato GOLD continua a mostrare divergenza direzionale tra bias e tecnica/D-L-A.
- Difetti confermati da questo controllo: (1) commodities GAGARIN con quote stale; (2) WATCH WTI privo di ticker/provider quote timestamp assoluto/mercato/expiry e livelli; (3) journal GAGARIN senza DATABASE_URL e senza persistenza dimostrata; (4) polling inbound GAGARIN incompatibile con webhook; (5) cadenza scanner SPUTNIK e monitor GAGARIN molto inferiore ai cron; (6) diagnostica Forex nel log non allineata al nuovo comportamento.
- Prossimo controllo: primo monitor GAGARIN fuori dalle vecchie fasce Forex; successivo run SPUTNIK scanner; verifica delle cadenze con timestamp e queue time; acquisizione dei metadati completi di ogni nuovo WATCH/CFD; verifica di storage privato persistente. Nessun outcome TP/SL finché ticker, mercato, expiry e quote timestamp non permettono un confronto sul medesimo strumento/contratto.

**Perimetro invariato:** solo report e ledger documentali aggiornati; nessuna modifica a codice, strategia, filtri, score, rischio, secrets o Render; nessun merge/deploy/ordine reale. PAPER ONLY.
