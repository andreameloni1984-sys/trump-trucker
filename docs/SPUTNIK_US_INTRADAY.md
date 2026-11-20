# Sputnik USA intraday

`python sputnik_us_intraday.py` esegue un’anteprima con fonti pubbliche e stampa gli eventuali setup. `python -m unittest discover -s tests -v` esegue la suite offline.

## Fonti e selezione

- Casa Bianca, Trump’s Truth (con permalink del post originale su Truth Social), Federal Reserve e FOMC, GovInfo per Congresso e leggi federali, FDA, SEC e MarketWatch.
- Comunicati societari di Microsoft, NVIDIA ed Eli Lilly e comunicati diffusi su GlobeNewswire e PR Newswire. Apple rimane nell’universo iniziale tramite fonti terze. Il suo feed ufficiale espone l’ultimo aggiornamento senza un orario di pubblicazione distinto.
- Reuters è facoltativo. `SPUTNIK_REUTERS_FEED_URL` accetta un feed RSS/Atom pubblico su un dominio Reuters. Durante la verifica il feed Reuters non è risultato raggiungibile.
- Si conservano solo notizie con titolo, permalink e data di pubblicazione completa di fuso orario. Le regole assegnano bias a decisioni Fed, alcuni provvedimenti tariffari espliciti, variazioni di guidance e approvazioni FDA per farmaci Lilly identificati. Altre notizie, comprese quelle ambigue, restano consultabili nello stato.
- SPY, QQQ, AAPL, MSFT, NVDA e LLY sono l’universo iniziale. Per una guidance con direzione esplicita il bot può ricavare un nuovo ticker da una sigla con borsa nel titolo o dall’anagrafica SEC se il nome dell’emittente corrisponde in modo univoco. Yahoo Finance verifica valuta, simbolo, borsa e tipo di strumento. Serve un catalizzatore prima di interrogare le quotazioni.
- I bias includono motivazione e incertezza qualitativa. La deduplicazione usa permalink, titoli normalizzati per le copie da stampa e agenzie e, per le decisioni Fed, l’entità della variazione riportata entro due ore. Le riscritture con titolo e dati diversi possono restare distinte.

## Conferma e consegna

Yahoo Finance fornisce barre a un minuto. Sputnik ricava barre a cinque minuti allineate alla sessione quando ci sono dati completi. Richiede sessione regolare, una barra successiva alla notizia e chiusa da non più di 90 secondi, continuità delle quotazioni, momentum e trend concordi, breakout o inversione e volume pari ad almeno 1,5 volte la media. Supporto, resistenza e ATR determinano i livelli. TP1 e TP2 proiettano 1,5 e 2,5 volte il rischio prima dell’arrotondamento. La conferma scade 45 minuti dopo la pubblicazione. La raccolta continua a mercato chiuso e conserva anche i bias privi di conferma.

Il workflow GitHub Actions ha una cadenza nominale di 15 minuti. Con `SPUTNIK_US_INTRADAY_ENABLED=true` il job USA sostituisce il collector precedente su `main`. Il job salva lo stato separato `sputnik_us_state.json`. Con `SPUTNIK_US_TELEGRAM_ENABLED=true` e i secret `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`, il job prenota i segnali prima del push dello stato e invia su Telegram soltanto i setup confermati, ancora recenti e marcati PAPER ONLY. Con l’invio disabilitato il job conserva le analisi e i livelli simulati senza prenotare i messaggi. `SEC_USER_AGENT` e `SPUTNIK_REUTERS_FEED_URL` sono facoltativi.

Una risposta Telegram ambigua o un’interruzione dopo il salvataggio della prenotazione può far perdere un messaggio. Un conflitto di push impedisce l’invio. Ritardi di GitHub Actions o del feed prezzi possono far scadere un setup.

Il replay offline della decisione Fed del 18 settembre 2024 usa barre sintetiche e Telegram simulato. Verifica il flusso del software, inclusi livelli, scadenza e deduplicazione.
