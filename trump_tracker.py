# TRUMP TRACKER - VERSIONE 2
# Modalità SIMULAZIONE / ALERT: non esegue ordini Trading 212.

import os
import json
import urllib.parse
import urllib.request

CAPITALE = 100.00
RISCHIO = 1.00

def analizza(ticker, direzione, importo, ritardo, movimento, conferme, trend):
    punti = 0
    motivi = []
    if importo >= 1:
        punti += 2
        motivi.append('operazione significativa')
    if conferme >= 2:
        punti += 2
        motivi.append('più conferme')
    elif conferme == 1:
        punti += 1
        motivi.append('una conferma')
    if ritardo <= 7:
        punti += 2
        motivi.append('disclosure recente')
    elif ritardo <= 14:
        punti += 1
        motivi.append('ritardo moderato')
    if trend == 'positivo':
        punti += 1
        motivi.append('trend positivo')
    if direzione == 'BUY' and movimento >= 10:
        punti = min(punti, 5)
        motivi.append('prezzo già molto esteso')
    if punti >= 8:
        decisione = '🟢 ENTRA'
    elif punti >= 6:
        decisione = '🟡 ASPETTA'
    else:
        decisione = '🔴 EVITA'
    return punti, decisione, motivi

def crea_messaggio(ticker, direzione, importo, ritardo, movimento, conferme, trend):
    punti, decisione, motivi = analizza(ticker, direzione, importo, ritardo, movimento, conferme, trend)
    return (
        '🚨 TRUMP TRACKER\n'
        '━━━━━━━━━━━━━━━━━━\n'
        f'📌 {ticker} — {decisione}\n'
        f'📊 Segnale: {punti}/10\n'
        f'🔄 Operazione: {direzione}\n'
        f'💰 Importo: USD {importo:.1f}M\n'
        f'⏱️ Ritardo disclosure: {ritardo} giorni\n'
        f'📈 Movimento: {movimento:+.1f}%\n'
        f'👥 Conferme: {conferme}\n'
        f'📉 Trend: {trend}\n'
        '━━━━━━━━━━━━━━━━━━\n'
        'Motivi: ' + (', '.join(motivi) if motivi else 'nessuno') + '\n'
        '⚠️ Segnale informativo/simulazione: nessun ordine automatico.'
    )

def invia_telegram(messaggio):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        print('Telegram non configurato: TELEGRAM_BOT_TOKEN/CHAT_ID mancanti.')
        return False
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = urllib.parse.urlencode({'chat_id': chat_id, 'text': messaggio}).encode('utf-8')
    request = urllib.request.Request(url, data=data, method='POST')
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode('utf-8'))
        if payload.get('ok'):
            print('✅ Telegram: messaggio inviato.')
            return True
        print('❌ Telegram: API ha risposto con errore:', payload)
    except Exception as exc:
        print('❌ Telegram:', exc)
    return False

def main():
    # TEST DI COLLEGAMENTO. Nella V3 sostituiremo questo evento con le disclosure reali.
    messaggio = crea_messaggio('NVDA', 'BUY', 2.0, 5, 2.8, 2, 'positivo')
    print(messaggio)
    invia_telegram(messaggio)

if __name__ == '__main__':
    main()