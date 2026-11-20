# PRAVDA Analytics

Report giornaliero offline per Gagarin INVEST v3 e Sputnik INVEST v2. Il comando usa Python 3.10+ e la libreria standard. Legge snapshot locali e scrive su un database dedicato. Nessun ordine, accesso di rete o invio Telegram.

## Origini e attivazione

- Gagarin usa la tabella `candidates` del journal di `invest_v3/journal.py` (commodity-news-scanner #259). Il worker integra i prezzi a 5, 15, 30 e 60 minuti, ancorati al primo segnale. Il percorso è quello passato al worker con `--journal`. Creare uno snapshot coerente via SQLite backup API o comando `.backup`, che include le pagine del WAL. Eseguire il backup fuori dal processo dei segnali. Copiare il solo file database durante le scritture può produrre uno snapshot incompleto.
- Sputnik usa `pravda` e, quando presente, `invest_events` da `sputnik_us_state.json` (trump-trucker #164). Esportare l'ultima versione effettivamente persistita dallo step **Persist Sputnik USA events and notification reservations** del workflow del bot. Il workflow legacy e il suo `sputnik_state.json` hanno un formato diverso. Sputnik registra close ai quattro orizzonti, escursioni sulle barre osservate e uno stato di simulazione.
- Usare gli snapshot delle modalità paper. Tenere snapshot, database e report su un volume persistente con accesso limitato. In GitHub Actions un runner effimero richiede un volume persistente esterno già configurato. Una cache o un artifact a scadenza non sostituisce il registro.
- Eseguire dalla radice del repository su un host con accesso alle copie locali. Per un report automatico programmare il comando con cron o con il proprio scheduler, dopo l'aggiornamento degli snapshot. Per esempio, alle 02:15 UTC ogni giorno su un host in UTC. Programmare una sola esecuzione per directory di output.

```sh
python -m pravda_analytics \
  --gagarin /srv/pravda/snapshots/gagarin.sqlite \
  --sputnik /srv/pravda/snapshots/sputnik_us_state.json \
  --ledger /srv/pravda/analytics/ledger.sqlite \
  --out /srv/pravda/analytics/latest
```

`--day YYYY-MM-DD` sceglie un giorno UTC concluso. Il default è ieri. Una fonte può essere omessa se temporaneamente assente. Per rigenerare un report è possibile usare il solo database analytics già inizializzato. Una fonte fornita con formato incompatibile fa fallire l'importazione e lascia intatta la transazione. Fornire gli snapshot più recenti: un replay con uno snapshot precedente può sovrascrivere un record aggiornato. Ogni import legge i registri disponibili e normalizza solo record nuovi o modificati. L'ID resta stabile per bot, evento e stato. Il database conserva le righe quando scompaiono dallo snapshot. Per disattivare basta rimuovere la schedulazione del comando.

## Interpretazione

- `report.md` contiene la sintesi, `report.json` la sintesi, i breakdown e le righe di giornata, `signals.csv` una riga per segnale con le misure per orizzonte. Le metriche riportano il relativo denominatore. I prezzi mancanti non sono imputati. Uno spostamento nullo è una direzione non confermata e viene contato anche separatamente.
- Il report è una fotografia alla fine del giorno UTC. Le osservazioni successive a mezzanotte sono oscurate anche quando presenti nello snapshot. Analytics controlla i timestamp del riferimento, della notizia e delle osservazioni; per Sputnik l'orario del close è derivato dalla regola del journal. Gli snapshot storici non includono l'ora di acquisizione di ogni barra, quindi un replay non dimostra che un dato arrivato in ritardo fosse già disponibile in produzione.
- Gagarin conserva il primo segnale, il primo ENTRARE e l'ultimo SCARTARE disponibile. Un ENTRARE successivo non eredita i prezzi a termine del PREPARARE. Il registro Sputnik conserva PREPARARE e ENTRARE; gli scarti senza timestamp di segnale e gli stadi che i bot non hanno persistito non sono ricostruibili.
- Il rendimento teorico è il movimento del prezzo corretto per il verso LONG/SHORT. Il rendimento e il multiplo R lordi Gagarin derivano dal suo modello OHLC con precedenza allo stop nelle barre ambigue. Le frequenze con denominatore verificabile si riferiscono alle uscite modellate. Sputnik contribuisce con raggiungimenti registrati, ma il suo esito aggregato non basta per attribuire prezzi o tempi di esecuzione. Il rendimento netto e i trade profittevoli rimangono `DATA_UNAVAILABLE` finché non sono disponibili riempimenti e costi verificabili, inclusi spread, commissioni e slippage.
- MFE e MAE Sputnik riguardano le barre osservate e possono sottostimare il percorso in presenza di lacune. Gagarin non persiste gli estremi. TP2 e TP3 sono indisponibili dove il journal si ferma a TP1. Gli score euristici sono raggruppati per scala del singolo bot. La confidenza esplicita viene usata solo quando presente. Per il contesto di mercato, il volume relativo è disponibile solo quando persistito da Gagarin.
- Il confronto tra bot è descrittivo e riporta rendimenti teorici, accuratezza, intervalli Wilson al 95% e differenza in punti percentuali con denominatori. Universi, stadi, prezzi di riferimento e copertura possono differire. La classifica giornaliera richiede almeno due categorie con 30 misure valide ciascuna.
- Le raccomandazioni confrontano il primo stadio PREPARARE per bot, con 90 giorni di sviluppo e 30 successivi di verifica. Un margine di 61 minuti separa gli esiti dai limiti temporali. Le categorie, gli strumenti, le direzioni e i livelli di confidenza o punteggio vengono valutati a 60 minuti. Gli orizzonti sono confrontati sugli stessi segnali. Servono almeno 30 osservazioni valide in ciascun gruppo, in entrambi i periodi, e intervalli simultanei separati nello stesso verso. Segnali correlati possono ridurre il campione effettivo. Le indicazioni sono ipotesi statistiche per la revisione e non cambiano strategie o filtri.

## Verifica

```sh
python -m unittest discover -s tests -p test_pravda_analytics.py -v
```

## Esempio sintetico

**PRAVDA — ANALISI RISULTATI** · 2026-11-18 UTC · PAPER ONLY

- Segnali analizzati: 1
- Gagarin: 0 segnali, direzione a 60 min DATA_UNAVAILABLE (n=0)
- Sputnik: 1 segnale, direzione a 60 min 0% (n=1, campione insufficiente)
- Migliore e peggiore categoria: campione insufficiente
- 5 min: 100% (n=1) · 15 min: 0% (n=1, prezzo invariato) · 30 min: DATA_UNAVAILABLE (n=0) · 60 min: 0% (n=1)
- Errore osservato: direzione a 60 min contraria al segnale SHORT (1)
- Redditività netta: DATA_UNAVAILABLE (n=0)
- Miglioramenti suggeriti: nessuna proposta confermata sul campione successivo
