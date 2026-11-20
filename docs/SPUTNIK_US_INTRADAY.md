# Sputnik INVEST

L’anteprima `python sputnik_us_intraday.py` legge fonti pubbliche e stampa eventuali segnali. La suite offline si esegue con `python -m unittest discover -s tests -v`.

## Dalla notizia al segnale

La raccolta parallela conserva permalink, orario originale con fuso, tempo di acquisizione e latenza. Ogni feed ha un timeout indipendente. Un errore lascia proseguire gli altri feed, con un nuovo tentativo alla scansione successiva. Il mirror di Truth Social serve a scoprire i post. Per attribuire un bias al post, Sputnik cerca di confermare autore, testo, permalink e data anche sul servizio originale. Reuters è facoltativo tramite `SPUTNIK_REUTERS_FEED_URL` e richiede un feed autorizzato e operativo.

Le regole riconoscono fatti direzionali su guidance e risultati, commesse, acquisizioni a premio, FDA, sanzioni SEC, export, dazi e Fed. Per management, licenziamenti e annunci industriali o tecnologici il sistema classifica la notizia e scarta i casi senza una tesi esplicita supportata da una regola. I segnali da fonti giornalistiche secondarie richiedono un annuncio primario indipendente. Le ipotesi macro cercano un ETF ordinario su Nasdaq-100 o S&P 500 direttamente nel catalogo Demo. Gli emittenti societari sono risolti dall’emittente del feed o dall’anagrafica SEC, con controllo del ticker dichiarato nel titolo quando presente.

Sputnik incrocia il ticker con i record USD univoci di azioni ed ETF USA esposti da `/api/v0/equity/metadata/instruments` su `demo.trading212.com`. La presenza nel catalogo attesta la copertura dell’anagrafica per quell’account. L’API metadata fornisce un accesso in sola lettura e non garantisce un’esecuzione. Le quotazioni vengono richieste solo per i ticker derivati da un catalizzatore e per misurare previsioni ancora aperte.

**PREPARARE** richiede fatto verificabile, tesi motivata e riscontro nel catalogo. Una quotazione mancante o scaduta viene mostrata come N/D. **ENTRARE** richiede una reazione tecnica LONG con barre regolari recenti, EMA20/50, momentum 1/5/15 minuti, breakout o inversione, volume e limiti di estensione basati sull’ATR. L’RSI è diagnostico. Stop e due target derivano dal rischio del setup. Un bias SHORT resta una tesi simulata in PREPARARE. INVEST non supporta vendite allo scoperto.

Il ledger PRAVDA nello stato raccoglie previsioni, prezzi a 5/15/30/60 minuti, escursioni, attraversamenti simulati, dati mancanti e conteggi per categoria. PREPARARE ed ENTRARE hanno istanti distinti e vengono misurati separatamente. Una barra che attraversa livelli incompatibili è registrata come indeterminata. Le statistiche non cambiano le regole.

## Come abilitarlo

- Dopo revisione e merge autorizzato, usare i secret `SPUTNIK_INVEST_DEMO_API_KEY` e `SPUTNIK_INVEST_DEMO_API_SECRET` con accesso all’anagrafica INVEST Demo. Configurare `SEC_USER_AGENT` per l’identificazione richiesta dalla SEC.
- La variabile GitHub Actions `SPUTNIK_US_INTRADAY_ENABLED=true` seleziona il job INVEST su `main` al posto del collector precedente. Per abilitare la consegna usare anche `SPUTNIK_US_TELEGRAM_ENABLED=true` con `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`.
- Il job riserva i segnali nello stato prima di consegnarli e scarta ENTRARE se la barra scade. Un guasto dopo il salvataggio della riserva può perdere un messaggio. Lo stato viene salvato in `sputnik_us_state.json`.

La cadenza condivisa resta nominalmente di 15 minuti. Una scansione ogni 5 minuti comporterebbe 288 avvii al giorno rispetto ai 96 correnti. GitHub Actions non garantisce puntualità, soprattutto sotto carico, e un timer a 5 minuti non garantisce una rilevazione entro 5 minuti. Un sistema a eventi richiederebbe notifiche affidabili dei singoli editori oppure un processo sempre attivo per il polling. Conviene misurare prima ritardo di avvio del job, acquisizione, scansione e disponibilità di Yahoo Finance sulla configurazione effettiva.
