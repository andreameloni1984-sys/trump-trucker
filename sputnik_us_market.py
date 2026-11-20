"""Intraday execution checks for the supported US shares and equity ETFs."""
from datetime import datetime, timedelta, timezone
from math import isfinite
from statistics import mean

from sputnik_equity_confirmation import fetch_intraday_series
from sputnik_us_news import ISSUERS

UNIVERSE = {*ISSUERS, "QQQ", "SPY"}
MAX_CATALYST_AGE = timedelta(minutes=45)
MAX_QUOTE_AGE = timedelta(seconds=90)


def evaluate(ticker, direction, published, now, fetch_series=fetch_intraday_series):
    if ticker not in UNIVERSE or direction not in {"LONG", "SHORT"}:
        return "strumento non idoneo", None
    if not timedelta(0) <= now - published <= MAX_CATALYST_AGE:
        return "catalizzatore fuori finestra intraday", None

    try:
        series = fetch_series(ticker)
        meta = series["meta"]
        if (meta["symbol"] != ticker or meta["currency"] != "USD"
                or meta["exchangeName"] not in {"NMS", "NGM", "NCM", "NYQ", "PCX", "ASE", "BTS"}
                or meta["instrumentType"] != ("ETF" if ticker in {"QQQ", "SPY"} else "EQUITY")):
            return "strumento non verificato dal provider", None
        period = meta["currentTradingPeriod"]["regular"]
        if not period["start"] <= now.timestamp() < period["end"]:
            return "sessione regolare chiusa", None
        quotes = series["indicators"]["quote"][0]
        bars = []
        for index, stamp in enumerate(series["timestamp"]):
            if type(stamp) is not int or stamp < period["start"] or stamp + 60 > now.timestamp():
                continue
            values = [quotes[key][index] for key in ("high", "low", "close", "volume")]
            if (any(type(value) not in (int, float) or not isfinite(value) or value <= 0
                    for value in values) or not values[1] <= values[2] <= values[0]):
                continue
            bars.append((stamp, *values))
    except (OSError, KeyError, ValueError, TypeError, IndexError, OverflowError, AttributeError):
        return "dati prezzo/volume indisponibili", None

    tail = bars[-21:]
    if len(tail) < 21 or any(b[0] - a[0] != 60 for a, b in zip(tail, tail[1:])):
        return "storico intraday insufficiente o discontinuo", None
    stamp, high, low, entry, volume = tail[-1]
    closed = datetime.fromtimestamp(stamp + 60, tz=timezone.utc)
    if not timedelta(0) <= now - closed <= MAX_QUOTE_AGE or stamp < published.timestamp():
        return "quotazione obsoleta o precedente alla notizia", None

    previous = tail[:-1]
    resistance = max(bar[1] for bar in previous)
    support = min(bar[2] for bar in previous)
    atr = mean(max(b[1] - b[2], abs(b[1] - a[3]), abs(b[2] - a[3]))
               for a, b in zip(previous, previous[1:]))
    sign = 1 if direction == "LONG" else -1
    trend = entry - mean(bar[3] for bar in previous)
    momentum = entry - previous[-5][3]
    if min(trend * sign, momentum * sign, (entry - previous[-1][3]) * sign) <= 0:
        return "tecnica contraria al bias", None
    level = resistance if sign > 0 else support
    breakout = (entry - level) * sign
    if breakout <= 0 or volume < 1.5 * mean(bar[4] for bar in previous):
        return "breakout o volume non confermato", None
    if atr <= 0 or breakout > 2 * atr or high - low > 4 * atr:
        return "volatilità eccessiva o prezzo già esteso", None

    # Avoid chasing a reaction that already moved several normal bar ranges.
    before = [bar for bar in bars if bar[0] + 60 <= published.timestamp()]
    if before and (entry - before[-1][3]) * sign > 6 * atr:
        return "reazione alla notizia già estesa", None

    entry = round(entry, 2)
    stop = round(level - sign * atr, 2)
    risk = (entry - stop) * sign
    tp1 = round(entry + sign * 1.5 * risk, 2)
    tp2 = round(entry + sign * 2.5 * risk, 2)
    if risk <= 0 or min(entry, stop, tp1, tp2) <= 0 or tp1 in {entry, tp2}:
        return "livelli incompatibili con il tick", None
    return "CONFERMATO", {"entry": entry, "stop": stop, "tp1": tp1, "tp2": tp2,
                         "rr1": (tp1 - entry) * sign / risk,
                         "rr2": (tp2 - entry) * sign / risk,
                         "quote_timestamp": closed.isoformat()}
