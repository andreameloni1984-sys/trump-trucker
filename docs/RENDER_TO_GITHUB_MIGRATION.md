# Migrazione SPUTNIK da Render a GitHub — COMPLETATA (indipendenza)

Sputnik è ora **indipendente da Render**. La raccolta dati e le notifiche girano su GitHub Actions. I comandi Telegram interattivi usano polling.

## Percorsi attivi (solo GitHub)

- **Raccolta dati Sputnik**: `.github/workflows/trump_tracker.yml` (ogni 5 min) → `python trump_tracker.py`
- **Polling Telegram Sputnik**: `.github/workflows/telegram-polling.yml` + `telegram/polling_runner.py`

## Cosa non è più usato

- Servizio Render `sputnik-telegram-listener.onrender.com`
- Bootstrap del listener Render nel workflow (rimosso)
- `telegram_listener.py` come servizio persistente — mantenuto solo come riferimento per la logica dei comandi

## Limitazioni note

- I comandi Telegram interattivi hanno latenza (fino a 5 minuti).
- Non esiste più un listener sempre acceso.

## Prossimi passi (opzionali)

- Spegnere il servizio su Render se ancora attivo.
- Verificare che i comandi principali funzionino con il polling runner.

Ultimo aggiornamento: 2026-10-29
