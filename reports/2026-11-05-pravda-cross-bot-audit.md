# PRAVDA — audit incrociato SPUTNIK / GAGARIN
**Snapshot:** 2026-11-05 15:58 UTC  
**Scope:** artefatti GitHub pubblici, journal/feedback e GitHub Actions. Nessuna modifica a codice, strategia, filtri, score, rischio, secret o Render; nessun merge/deploy/ordine.

Ledger deduplicato: [pravda-signal-ledger-2026-11-05.csv](pravda-signal-ledger-2026-11-05.csv) — 24 record (21 candidati storici GAGARIN, 1 ticket legacy GAGARIN, 1 WATCH GAGARIN, 1 candidato CFD SPUTNIK). I 981 ID del prediction log GAGARIN sono unici. Nessun outcome verificato.

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
