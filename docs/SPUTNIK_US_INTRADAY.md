# Sputnik USA intraday

`python sputnik_us_intraday.py` esegue un'anteprima con fonti pubbliche, stampa gli eventuali setup e lascia intatti lo stato e Telegram. La scansione passa dalle notizie datate ai ticker, poi verifica i prezzi soltanto per i ticker associati a un catalizzatore. `python -m unittest discover -s tests -v` esegue la suite offline.

## Copertura

- Casa Bianca (azioni presidenziali e comunicati), Trump (archivio Trump’s Truth con permalink originale di Truth Social), Federal Reserve, Congresso e leggi federali via GovInfo, FDA, SEC, MarketWatch e comunicati di Microsoft, NVIDIA ed Eli Lilly.
- Reuters ha risposto con errori di accesso durante la verifica. MarketWatch copre il canale giornalistico tramite RSS pubblico. I feed delle singole società coprono una parte del mercato. Il feed Atom di Apple espone la data di aggiornamento e le pagine controllate espongono solo il giorno di pubblicazione, quindi il feed è escluso.
- Le regole riconoscono decisioni Fed, alcune azioni tariffarie esplicite, variazioni di guidance di società mappate e approvazioni FDA per farmaci Lilly identificati. Le altre notizie verificabili restano nello storico. QQQ, SPY, AAPL, MSFT, NVDA e LLY definiscono l'universo iniziale. Il mercato di quotazione, la valuta e il tipo di strumento sono controllati presso il provider.
- Yahoo Finance fornisce barre a un minuto. La conferma richiede la sessione regolare USA, una barra post-notizia chiusa da al massimo 90 secondi, storico continuo, trend e momentum concordi, breakout di supporto/resistenza e volume almeno 1,5 volte la media. Il range reale medio filtra movimenti estesi e determina il margine dello stop. TP1 e TP2 proiettano rispettivamente 1,5 e 2,5 volte il rischio, prima dell'arrotondamento. Il setup scade 45 minuti dopo la pubblicazione. La scansione delle notizie continua anche fuori sessione.
- Lo stato registra i bias senza livelli in assenza di una conferma. Telegram riceve solo setup confermati con livelli paper. La deduplicazione usa URL canonici e un blocco conservativo di otto ore per tipo di catalizzatore e ticker, che può accorpare due notizie distinte della stessa categoria.

## Esecuzione pianificata

Il workflow esistente ha una cadenza nominale di 15 minuti. Il job USA richiede la variabile repository `SPUTNIK_US_INTRADAY_ENABLED=true` e il ramo `main`. Quando il job USA è abilitato, prende il posto del collector precedente. Usa `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` e facoltativamente `SEC_USER_AGENT`. Non legge lo stato del collector precedente. I moduli di ricerca e i comandi storici restano disponibili nel repository.

Il job serializza le esecuzioni e salva `sputnik_us_state.json` prima della consegna. I livelli devono risultare ancora recenti al momento dell'invio. Un conflitto di push impedisce l'invio. In caso di risposta Telegram ambigua o di interruzione dopo la prenotazione, il setup può andare perso. Il job evita un secondo invio della stessa opportunità. GitHub Actions può avviare il job in ritardo e Yahoo Finance può limitare o ritardare i dati. In entrambi i casi la finestra di conferma può scadere.

Il replay della decisione Fed del 18 settembre 2024 usa barre sintetiche per verificare long, livelli, scadenza, deduplicazione e Telegram simulato. Questo replay verifica il software e non misura il rendimento della strategia.
