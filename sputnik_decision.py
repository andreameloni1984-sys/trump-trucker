"""Data-only scenario catalog consumed by the strict SPUTNIK decision engine.

Decision matching and Telegram formatting live in sputnik_decision_engine.py.
"""
from __future__ import annotations

SCENARIOS = [
    {
        "id": "tariff_escalation",
        "trigger": ("tariff", "tariffs", "trade war", "import duties", "dazi"),
        "event": "Escalatione commerciale / nuovi dazi",
        "candidate": "ORO (XAU/USD)",
        "bias": "LONG condizionale",
        "if_then": "Se viene annunciato un aumento concreto dei dazi e oro rompe una resistenza intraday con USD non in forte rialzo, valutare LONG sull'oro.",
        "confirmation": "Annuncio ufficiale + rottura confermata su prezzo/volume; controllare DXY e rendimenti reali.",
        "invalidation": "Nessuna rottura, USD e rendimenti in rialzo, oppure annuncio ritirato/rinviato.",
        "source_quality": "Catalizzatore politico da verificare su fonte primaria; prezzo non incluso.",
    },
    {
        "id": "trade_deescalation",
        "trigger": ("trade deal", "trade agreement", "tariff pause", "pause tariffs", "dazi sospesi", "accordo commerciale"),
        "event": "De-escalation commerciale / accordo o pausa dei dazi",
        "candidate": "NASDAQ-100 (indice/CFD)",
        "bias": "LONG condizionale",
        "if_then": "Se una pausa/accordo commerciale è confermata ufficialmente e Nasdaq supera il massimo della sessione con futures in rialzo, valutare LONG sul Nasdaq-100.",
        "confirmation": "Conferma ufficiale + breakout del massimo intraday; verificare ampiezza del mercato e futures.",
        "invalidation": "Accordo non confermato, breakout fallito o nuova escalation.",
        "source_quality": "Catalizzatore politico da verificare su fonte primaria; prezzo non incluso.",
    },
    {
        "id": "oil_supply_disruption",
        "trigger": ("hormuz", "oil supply", "oil exports", "crude", "brent", "wti", "iran", "tanker", "petroleum"),
        "event": "Rischio di interruzione dell'offerta energetica",
        "candidate": "BRENT (petrolio)",
        "bias": "LONG condizionale",
        "if_then": "Se la notizia documenta un rischio concreto per i flussi fisici di petrolio e Brent rompe il massimo intraday, valutare LONG sul Brent.",
        "confirmation": "Fonte ufficiale/agenzia affidabile + breakout del prezzo; verificare scorte, spread Brent-WTI e conferme indipendenti.",
        "invalidation": "Flussi normali, notizia smentita, prezzo che rientra sotto il livello di breakout.",
        "source_quality": "Tema energia rilevato; serve verificare che la notizia riguardi davvero l'offerta fisica.",
    },
    {
        "id": "geopolitical_deescalation",
        "trigger": ("iran peace deal", "iran agreement", "ceasefire", "sanctions lifted", "diplomatic agreement", "accordo diplomatico"),
        "event": "De-escalation geopolitica / riduzione del rischio energetico",
        "candidate": "BRENT e WTI (petrolio); ORO come scenario secondario",
        "bias": "SHORT condizionale sul petrolio; ORO da rivalutare",
        "if_then": "Se un accordo verificato riduce concretamente il rischio sui flussi energetici o rimuove sanzioni, valutare SHORT su Brent/WTI solo dopo conferma del prezzo; l'oro può perdere domanda di bene rifugio ma richiede conferma separata.",
        "confirmation": "Annuncio primario verificato, dettagli su sanzioni/produzione/rotte e reazione coerente di Brent/WTI; verificare USD e rendimenti prima di valutare l'oro.",
        "invalidation": "Accordo non firmato, smentito, privo di effetti sui flussi fisici o prezzo del petrolio che rompe al rialzo.",
        "source_quality": "Catalizzatore politico indiretto: non equivale automaticamente a variazione dell'offerta; richiede verifica dei dettagli e del prezzo.",
    },
    {
        "id": "defense_escalation",
        "trigger": ("missile", "military strike", "defense spending", "defence spending", "military operation", "defense contract"),
        "event": "Escalation militare o spesa/commessa difesa",
        "candidate": "SETTORE DIFESA (ETF/azioni liquide)",
        "bias": "LONG condizionale",
        "if_then": "Se viene confermata una nuova commessa o un'escalation con impatto concreto sulla spesa e il settore rompe la resistenza, valutare LONG su uno strumento liquido del settore difesa.",
        "confirmation": "Comunicazione ufficiale/contratto verificato + conferma di prezzo e volumi.",
        "invalidation": "Nessun impatto su spesa/commesse o breakout fallito.",
        "source_quality": "Tema geopolitico rilevato; non equivale a un ordine di acquisto.",
    },
]
