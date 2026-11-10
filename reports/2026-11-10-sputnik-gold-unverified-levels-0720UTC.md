# PRAVDA — Anomalia SPUTNIK GOLD: livelli pubblicati senza validazione completa

**Osservazione:** 10 novembre 2026, 07:20 UTC  
**Bot:** SPUTNIK  
**Strumento dichiarato:** GOLD  
**Classificazione PRAVDA:** `NON_TRADE` · `ANOMALY_LEVELS_WITH_UNVERIFIED_MARKET_DATA`  
**Stato dichiarato dal bot:** `EARLY_SETUP` · `TRADE PAPER: NOT_EXECUTED`

## Evidenza ricevuta

Messaggio SPUTNIK — ANALISI CFD, timestamp dichiarato 2026-11-10 07:20 UTC:

- BIAS: SHORT
- SETUP: EARLY_SETUP
- TECNICA: `N/D (NOT_ASSESSED)`
- D-L-A: SHORT (`ALIGNS`)
- TRADE PAPER: `NOT_EXECUTED`
- SCORE: 100/100
- ENTRY: 4126.7002
- SL: 4129.4967
- TP1: 4123.9037 (1R)
- TP2: 4121.1072 (2R)
- ATR: 1.8643
- NARWHAL REF: `NOT_CONFIGURED`
- Contratto: front-month continuo; scadenza esatta e indipendenza upstream non verificate
- Spot/futures: `SPOT_VS_FUTURES_BASIS_CHECK_INDEPENDENCE_UNVERIFIED`
- Componenti dichiarate da SILV; indipendenza non verificata
- Motivazione: direzione tecnica SHORT, ma nessun catalizzatore USA direzionale verificato; D-L-A basato su proxy OHLCV (EMA20/EMA50 SHORT, VWAP SHORT)
- Rischio dichiarato: 1,0% max
- Nota esplicita: analisi informativa; trade paper non eseguito da questo modulo

Il precedente messaggio di intelligence associato riportava inoltre `NO_DIRECTIONAL_NEWS` per GOLD. La notizia politica su Thomas Massie/Pete Hegseth non dimostra da sola un catalizzatore direzionale sull'oro.

## Anomalia

Il modulo pubblica ENTRY, SL, TP1 e TP2 nonostante:
1. `TECNICA=N/D (NOT_ASSESSED)`;
2. assenza di un catalizzatore USA direzionale verificato;
3. riferimento NARWHAL non configurato;
4. contratto continuo senza scadenza esatta verificata;
5. indipendenza della fonte spot/futures non verificata.

Il punteggio 100/100 non è accompagnato da evidenza che giustifichi una validità operativa. La dicitura `EARLY_SETUP` non risolve queste carenze.

## Controllo aritmetico, non validazione di mercato

- Distanza ENTRY–SL: 2.7965
- Distanza ENTRY–TP1: 2.7965 (1R)
- Distanza ENTRY–TP2: 5.5930 (2R)
- Distanza ENTRY–SL / ATR: circa 1.50 ATR

I livelli sono coerenti aritmeticamente con una struttura 1R/2R e uno stop di circa 1,5 ATR. Questo controllo non verifica che ENTRY sia un prezzo negoziabile, che ATR appartenga allo stesso contratto o che i livelli siano utilizzabili.

## Trattamento nel ledger

- Classificare come `NON_TRADE`: il bot dichiara `NOT_EXECUTED`.
- Non registrare fill, stop raggiunto, target raggiunto o rendimento.
- Non calcolare win rate, average R o total R da questo messaggio.
- Non aggiungere una riga al ledger cumulativo: il testo ricevuto non contiene un Telegram message ID né un source record ID stabile; non è possibile costruire una firma univoca senza inventare identificativi.
- Conservare i valori e le avvertenze esattamente come riportati.

## Correzione attesa da sottoporre a verifica

1. Se `TECNICA=NOT_ASSESSED`, sopprimere ENTRY/SL/TP e classificare il risultato come sola ipotesi direzionale.
2. Consentire livelli solo dopo verifica della quotazione, timestamp/età, provider, ticker risolto, mercato e scadenza.
3. Se l'indipendenza spot/futures è `UNVERIFIED`, impedire che la quota venga presentata come prezzo operativo validato.
4. Separare score del catalizzatore, score tecnico e validazione dei livelli; non mostrare 100/100 senza componenti e motivazione verificabili.
5. Mantenere distinti `EARLY_SETUP`, `NOT_EXECUTED` e un trade PAPER effettivamente registrato.

## Esito

**Anomalia documentata; nessuna operazione registrata.** Questo documento registra l'evidenza fornita dall'utente, non una verifica indipendente del feed o dei prezzi di mercato. Nessuna modifica al codice, nessun merge e nessun deploy eseguiti.
