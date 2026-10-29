# Migrazione SPUTNIK da Render a GitHub

Documento di stato per spostare la parte interattiva di SPUTNIK fuori da Render.

## Cosa gira già su GitHub Actions

- **`.github/workflows/trump_tracker.yml`**  
  Esegue `python trump_tracker.py` ogni 5 minuti (`cron: "2-59/5 * * * *"`).  
  Raccoglie dati SEC, aggiorna lo stato, invia notifiche Telegram quando necessario.  
  Il job continua anche se il listener Render non è raggiungibile.

## Cosa dipende ancora da Render

- `telegram_listener.py`  
  Listener persistente pensato per un servizio web su Render.  
  Gestisce i comandi interattivi Telegram (menu, classifica, segnali CFD, ecc.).  
  URL di riferimento: `https://sputnik-telegram-listener.onrender.com`

- Il workflow attuale prova a fare bootstrap del listener su Render, ma non si blocca se fallisce.

## Strategia di migrazione

1. **Raccolta dati e notifiche push** (già fatto)  
   Continuare a usare `trump_tracker.yml` come motore principale.

2. **Comandi Telegram interattivi**  
   Usare un runner di polling one-shot (`telegram/polling_runner.py`) lanciato da Actions.  
   Processa gli update pendenti e termina.

3. **Deprecare il listener Render**  
   Tenere `telegram_listener.py` come riferimento finché il polling non copre i casi d'uso principali.

## Prossimi passi

- [ ] Testare il polling runner.
- [ ] Verificare che i comandi principali (cosa comprare, segnale, aiuto) funzionino in modalità polling.
- [ ] Spegnere il servizio Render quando stabile.
- [ ] Rimuovere i riferimenti a `sputnik-telegram-listener.onrender.com` dal workflow.

Ultimo aggiornamento: 2026-10-29
