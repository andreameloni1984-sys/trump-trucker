# PRAVDA — Audit indipendente SPUTNIK / GAGARIN
**Cut-off: 2026-11-06 15:29 UTC (16:29 Europe/Rome)**

## Sintesi esecutiva

- Nessun nuovo collector di mercato SPUTNIK dopo il run schedulato #42210907412 delle 11:31:39 UTC.
- Nessun nuovo monitor prezzi GAGARIN dopo il run schedulato #42203497432 delle 10:32:52 UTC.
- Le esecuzioni di Daily Summary, Telegram Polling, Fetch Drivers e CI non sono state conteggiate come monitor di mercato.
- Nuovo difetto runtime GAGARIN: il polling Telegram #42236174265 fallisce con API error 409 perché un webhook è attivo.
- Nuova PR GAGARIN #219 per rimuovere EUR/USD e GBP/USD: test d'integrazione fallito, 21 test falliti e 549 passati. La PR è OPEN, non merged.
- Nessun nuovo segnale individuale completo; ledger invariato a 32 record, 32 firme uniche, zero duplicati.
- Nessun fill, TP o SL verificabile. Win rate e average R: N/D.

## 1. Cronologia Actions distinta per funzione

### SPUTNIK

Ultimo collector schedulato:
- [Run #42210907412](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42210907412)
- Workflow: `.github/workflows/trump_tracker.yml`
- Avvio: 2026-11-06 11:31:39 UTC; conclusione 11:31:53 UTC; SUCCESS.
- Commit eseguito: `fbcb0de2bfe921383eee7edff10c5d9cf3d306d2`.
- Cut-off: 15:29 UTC; tempo dall'ultimo collector: circa 3h57m21s.
- Cron su main: `2-59/5 * * * *`.
- Concurrency: `group: sputnik-main`, `queue: max`, `cancel-in-progress: false`.
- Il workflow esegue due gruppi di regression test prima del collector e continua a persistere `sputnik_state.json` con `git push origin main`.

Altri run schedulati più recenti non sono collector:
- [Daily Summary #42226158074](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42226158074), 13:31:21 UTC, SUCCESS: riepilogo.
- [Telegram Polling #42206505491](https://github.com/andreameloni1984-sys/trump-trucker/actions/runs/42206505491), 10:56:51 UTC, SUCCESS: polling, non intelligence.

Nella prima pagina delle 100 Actions più recenti non compare un collector `trump_tracker.yml` successivo a #42210907412. La causa del gap non è determinata; non attribuisco il ritardo a una causa ipotetica. Il branch main attuale è `ff7430f608fedf2a0f4c64eedf0d876b092d6dfa`, diverso dal commit del collector: nessun collector successivo ha testato il codice attuale.

### GAGARIN

Ultimo monitor schedulato:
- [Run #42203497432](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42203497432)
- Workflow: `.github/workflows/gagarin-monitor.yml`
- Avvio: 2026-11-06 10:32:52 UTC; conclusione 10:33:10 UTC; SUCCESS.
- Commit eseguito: `7ed290b971e780828934d80aa3b936043769eaf6`.
- Cut-off: 15:29 UTC; tempo dall'ultimo monitor: circa 4h56m08s.
- Cron su main: `*/15 * * * *`.
- Il branch main attuale è `fba34bef94ac8968f7d31e3ee70ade8efe3fd51c`, quindi il monitor non ha ancora eseguito l'attuale head.

Altri run schedulati più recenti non sono monitor prezzi:
- [Daily Summary #42232309653](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42232309653), 14:15:30 UTC, SUCCESS: riepilogo.
- [FETCH DRIVERS #42235888213](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42235888213), 14:39:35 UTC, SUCCESS: snapshot driver.
- [Telegram Polling #42236174265](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42236174265), 14:41:31 UTC, FAILURE: polling, non monitor prezzi.

Nella prima pagina delle 100 Actions più recenti non compare un monitor `gagarin-monitor.yml` successivo a #42203497432.

## 2. Difetto Telegram GAGARIN — webhook contro polling

Run [#42236174265](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42236174265), job `127954240667`:
- installazione dipendenze: completata;
- validazione token: completata, token presente;
- diagnostica Telegram: OK, bot identificato;
- `getUpdates`: fallito con HTTP/API 409;
- messaggio: `webhook is active; polling cannot run while webhook mode is enabled`.

È un conflitto dimostrato tra modalità webhook e polling. Non prova un guasto del motore prezzi, ma il canale comandi Telegram basato su polling non ha completato il run.

La correzione proposta esiste già nella [PR #175 — Handle active Telegram webhook in scheduled polling](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175), ma la PR è ancora OPEN e non integrata. PRAVDA ha aggiunto il riscontro runtime nel thread: [commento #6688546557](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/175#issuecomment-6688546557).

## 3. GAGARIN — dati mercato dell'ultimo monitor

Nel run #42203497432, tutte le otto commodity erano stale su Yahoo:
- Grano 622,4 s
- Brent 604,3 s
- WTI 601,2 s
- Oro 614,5 s
- Argento 606,0 s
- Rame 607,1 s
- Mais 622,4 s
- Soia 664,5 s

EUR/USD e GBP/USD erano LIVE su BiQuote (187,0 e 187,5 s), ma erano riportati come contesto Forex non operativo. Il run ha analizzato dieci strumenti complessivi.

Candidati:
- Grano SHORT: probabilità 63, qualità 52,5, confidenza 35, PAPER_WATCH; bloccato da LIVE_DATA_NOT_FRESH, TRIGGER_NOT_CONFIRMED, TRIGGER_DIRECTION_MISMATCH, RR_FAIL e FINAL_CONFLUENCE_FAIL.
- Brent, WTI, Oro, Argento, Rame, Mais e Soia: PAPER_WATCH senza livelli operativi completi; blocchi includono dati stale, setup/trigger non validi e livelli mancanti.
- GBP/USD e EUR/USD: CONTEXTO FX — NON OPERATIVO.

Output monitor: zero nuove entrate PAPER, zero outcome aggiornati, zero nuovi feedback, zero nuove previsioni live aggiuntive; `signals=0 open=0 closed=0 win_rate=N/D avg_R=N/D`.

Il messaggio riepilogativo #3701 ha avuto API acknowledgement in 509 ms. Non è un trade e l'ACK non prova consegna al dispositivo.

## 4. Nuova PR GAGARIN #219 — suite fallita

[PR #219 — Remove EUR/USD and GBP/USD from Gagarin universe](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219):
- Stato: OPEN, non merged; head `8c3192fc33701f0a6484a3f4dbc872f061cf6648`.
- Run CI [#42239182472](https://github.com/andreameloni1984-sys/commodity-news-scanner/actions/runs/42239182472), 15:01:35 UTC: FAILURE.
- Risultato: **21 failed, 549 passed**.

Tra i fallimenti osservati:
- test che ancora si aspettano EUR/USD e GBP/USD nella scansione e nelle route di mercato a dieci simboli; questi test sono in conflitto con l'obiettivo dichiarato della PR di ridurre l'universo alle otto commodity;
- test di alert aggressivi che ricevono stringa vuota e non mostrano `POSSIBILE OPPORTUNITÀ`;
- test LUBJANKA Telegram che non trovano il contenuto atteso;
- test su session windows, deduplicazione e delivery state.

PRAVDA non presume che tutti i 21 fallimenti siano causati dalla rimozione del Forex: il branch deve riconciliare l'intera suite prima di essere considerato verde. La nota è stata aggiunta alla PR: [commento #6688547345](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/219#issuecomment-6688547345).

Un commento automatico Cloudflare segnala inoltre un deployment del servizio `telegram-github-bridge` fallito sul commit della PR alle 15:07 UTC. È un'integrazione esterna separata, non un deployment dei bot eseguito da PRAVDA.

PR correlate ancora aperte:
- [#220 — quote aliases negli alert](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/220), draft, basata sul head della #219.
- [#218 — rifiuto quote BiQuote stale](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/218), draft.
- [#217 — identità contratti CFD scaduti](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/217), draft.
- [#198 — ripristino ranking baseline](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/198), draft.
- [#181 — provenienza quote](https://github.com/andreameloni1984-sys/commodity-news-scanner/pull/181), aperta.

## 5. Journal, feedback e prediction log

Artefatti GAGARIN su main:
- `journal.csv`: 11 righe dati, tutte del 17 ottobre e con `nessun segnale`.
- `paper_trade_log.csv`: un WTI LONG legacy del 8 ottobre; nessun provider, timestamp quote, mercato/contratto di esecuzione o prova fill.
- `data/paper_open.json`: P0001 WTI corrisponde alla stessa posizione logica del record legacy; non duplicare.
- `position.json`: Heating Oil LONG legacy già noto; provenienza incompleta.
- `commodities_prediction_log.json`: 981 record; ultimo `created_at` 2026-09-15T15:45:04.462276Z. Gli ultimi record mostrano `PENDING`; anche un'etichetta `COMPRA ORA` non dimostra esecuzione.
- `gagarin_feedback.csv`: non presente su main (404).
- `DATABASE_URL`: vuoto nel run monitor; persistenza DB non dimostrata.

Il workflow GAGARIN su main dichiara PAPER ONLY e specifica che i journal sono dati operativi privati; la persistenza è subordinata a uno storage privato verificato. Non ho tentato di leggere o modificare secrets/storage.

## 6. SPUTNIK — segnale più recente già registrato

Nessun nuovo segnale dopo il run #42210907412. Il candidato GOLD LONG dei messaggi #707/#708 rimane un solo record:
- generazione CFD: 11:31:48.567717 UTC; ACK API: 11:31:48.569094 UTC;
- GOLD, mapping GC=F configurato ma ticker runtime non confermato;
- future continuo front-month; scadenza UNKNOWN;
- provider e timestamp/età quotazione non esposti;
- LONG preliminare; entry 4075.8999; SL 4074.2713; TP1 4077.5285; TP2 4079.1570; ATR 1.0857; score 70;
- CFD: tecnica NOT_ASSESSED, D-L-A NEUTRAL/NO_DIRECTION; livelli dichiarati non utilizzabili sul continuo senza scadenza verificata;
- stato EARLY_SETUP / NOT_EXECUTED.

Esito: ESITO NON VERIFICABILE. Nessun fill e nessuna candela successiva dello stesso contratto/scadenza. I messaggi #707 e #708 sono una sola ipotesi, non due trade.

## 7. Ledger e statistiche

Il ledger corrente su main:
- Blob SHA: `cfcd19a244cb38e0bb6549de5f191ce68277575a`.
- 32 record dati, 32 firme uniche, zero duplicati.
- Nessun nuovo segnale completo da aggiungere in questo controllo.
- Nessun TP/SL/outcome verificabile.
- Campione valido per win rate e average R: zero; entrambe N/D.

Il ledger non è stato modificato.

## 8. Prossimo controllo

1. Verificare il prossimo collector SPUTNIK e il prossimo monitor GAGARIN separandoli da summary, polling, fetch-driver e CI.
2. Controllare perché il polling GAGARIN continua a ricevere 409 nonostante la PR #175 esistente.
3. Verificare la correzione della PR #219: test FX aggiornati e suite alert/LUBJANKA verde prima di qualsiasi integrazione.
4. Verificare che il monitor GAGARIN venga eseguito sul commit main attuale e che le quote commodity siano fresche.
5. Richiedere ticker runtime, mercato, scadenza, provider e timestamp quote per ogni nuovo candidato.
6. Attribuire TP/SL solo su candele successive dello stesso identico contratto e rispettando l'ordine temporale.

**Perimetro:** nessun codice bot o workflow modificato; nessuna strategia, filtro, score o rischio modificato; nessun merge, deploy o rerun; nessun ordine reale; nessuna modifica a secrets o Render; nessun servizio a pagamento. PRAVDA ha soltanto pubblicato due commenti di audit su PR esistenti e creato questo documento. PAPER ONLY.
