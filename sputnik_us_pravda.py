"""Persist and score paper forecasts against completed one-minute bars."""
from collections import Counter, defaultdict
from datetime import datetime

HORIZONS = (5, 15, 30, 60)


def record_observations(forecast, bars, now):
    start = datetime.fromisoformat(forecast["signalled"]).timestamp()
    # Only candles entirely after the signal may contribute high/low or fills.
    observed = [bar for bar in bars if start <= bar[0] and bar[0] + 60 <= start + 3600]
    by_close = {bar[0] + 60: bar[3] for bar in observed}
    prices = forecast.setdefault("prices", {})
    for minutes in HORIZONS:
        horizon = start + minutes * 60
        if now.timestamp() >= horizon:
            close = int(horizon // 60) * 60
            prices[str(minutes)] = by_close.get(close, prices.get(str(minutes)))
    price = forecast.get("price")
    for _, high, low, _, _ in observed:
        if price is None:
            break
        favorable, adverse = ((high - price, price - low) if forecast["direction"] == "LONG"
                              else (price - low, high - price))
        forecast["mfe"] = max(forecast.get("mfe", 0), favorable)
        forecast["mae"] = max(forecast.get("mae", 0), adverse)

    levels = forecast.get("levels")
    if levels:
        for stamp, high, low, _, _ in observed:
            if stamp <= forecast.get("last_simulated_bar", -1):
                continue
            forecast["last_simulated_bar"] = stamp
            if not forecast.get("filled"):
                if low <= levels["entry"] <= high:
                    forecast.update(filled=True, outcome="entry")
                    if low <= levels["stop"] or high >= levels["tp1"]:
                        forecast["outcome"] = "sequenza intrabar indeterminata"
                continue
            if forecast["outcome"] not in {"entry", "tp1"}:
                break
            next_target = levels["tp2"] if forecast["outcome"] == "tp1" else levels["tp1"]
            if low <= levels["stop"] and high >= next_target:
                forecast["outcome"] = "sequenza intrabar indeterminata"
                break
            if low <= levels["stop"]:
                forecast["outcome"] = "stop dopo tp1" if forecast["outcome"] == "tp1" else "stop"
                break
            if high >= levels["tp2"]:
                forecast["outcome"] = "tp2"
                break
            if high >= levels["tp1"]:
                forecast["outcome"] = "tp1"
    if now.timestamp() >= start + 3600:
        forecast["complete"] = True
        if levels and not forecast.get("filled"):
            forecast["outcome"] = "entry non raggiunta"
        if any(prices.get(str(minutes)) is None for minutes in HORIZONS):
            forecast["error"] = "barre mancanti agli orizzonti richiesti"
        elif price is None:
            forecast["error"] = "prezzo iniziale indisponibile"
        elif forecast.get("outcome") == "stop":
            forecast["error"] = "stop raggiunto nella simulazione"
        elif forecast.get("outcome") == "sequenza intrabar indeterminata":
            forecast["error"] = "ordine degli attraversamenti sconosciuto"
        elif (prices["60"] - price) * (1 if forecast["direction"] == "LONG" else -1) < 0:
            forecast["error"] = "variazione a 60 minuti contraria alla tesi"


def summarize(forecasts):
    results = defaultdict(Counter)
    for forecast in forecasts:
        if forecast.get("complete"):
            results[forecast["category"]][forecast.get("error") or forecast.get("outcome", "osservato")] += 1
    return dict(results)
