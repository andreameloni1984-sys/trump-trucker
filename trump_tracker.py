# TRUMP TRACKER - VERSIONE 1
# Modalità SIMULAZIONE: non esegue ordini.

CAPITALE = 100.00
RISCHIO = 1.00


def analizza(ticker, direzione, importo, ritardo,
             movimento, conferme, trend):

    punti = 0
    motivi = []

    # Importo dell'operazione
    if importo >= 1:
        punti += 2
        motivi.append("operazione significativa")

    # Altre persone hanno fatto la stessa operazione
    if conferme >= 2:
        punti += 2
        motivi.append("più conferme")
    elif conferme == 1:
        punti += 1
        motivi.append("una conferma")

    # Ritardo della disclosure
    if ritardo <= 7:
        punti += 2
        motivi.append("disclosure recente")
    elif ritardo <= 14:
        punti += 1
        motivi.append("ritardo moderato")

    # Trend
    if trend == "positivo":
        punti += 1
        motivi.append("trend positivo")

    # Evitiamo di inseguire un titolo già esploso
    if direzione == "BUY" and movimento >= 10:
        punti = min(punti, 5)
        motivi.append("prezzo già molto esteso")

    # Decisione
    if punti >= 8:
        decisione = "🟢 ENTRA"
    elif punti >= 6:
        decisione = "🟡 ASPETTA"
    else:
        decisione = "🔴 EVITA"

    print("")
    print("🚨 TRUMP TRACKER")
    print("==============================")
    print(f"Titolo:       {ticker}")
    print(f"Operazione:   {direzione}")
    print(f"Importo:      ${importo:.1f}M")
    print(f"Ritardo:      {ritardo} giorni")
    print(f"Movimento:    {movimento:+.1f}%")
    print(f"Conferme:     {conferme}")
    print(f"Trend:        {trend}")
    print("")
    print(f"SEGNale:      {punti}/10")
    print(f"DECISIONE:    {decisione}")
    print("")
    print("Motivi:")
    for motivo in motivi:
        print(" - " + motivo)
    print("==============================")

    return punti, decisione


# -------------------------------------------------
# TEST DEL SISTEMA
# -------------------------------------------------

analizza(
    ticker="NVDA",
    direzione="BUY",
    importo=2.0,
    ritardo=5,
    movimento=2.8,
    conferme=2,
    trend="positivo"
)