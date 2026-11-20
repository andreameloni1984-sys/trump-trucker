"""Intraday execution checks for the supported US shares and equity ETFs."""
from datetime import datetime, timedelta, timezone
from math import isfinite
import re
from statistics import mean

from sputnik_equity_confirmation import fetch_intraday_series
MAX_CATALYST_AGE = timedelta(minutes=45)
MAX_QUOTE_AGE = timedelta(seconds=90)


def read_bars(ticker, now, expected_type, fetch_series=fetch_intraday_series, *, history=False):
    try:
        series = fetch_series(ticker)
        meta = series["meta"]
        if (meta["symbol"] != ticker or meta["currency"] != "USD"
                or meta["exchangeName"] not in {"NMS", "NGM", "NCM", "NYQ", "PCX", "ASE", "BTS", "BZX"}
                or meta["instrumentType"] != expected_type):
            return "strumento non verificato dal provider", []
        period = meta["currentTradingPeriod"]["regular"]
        regular_open = period["start"] <= now.timestamp() < period["end"]
        if not history and not regular_open:
            return "sessione regolare chiusa", []
        quotes = series["indicators"]["quote"][0]
        bars = []
        for index, stamp in enumerate(series["timestamp"]):
            if type(stamp) is not int or not period["start"] <= stamp < period["end"] or stamp + 60 > now.timestamp():
                continue
            values = [quotes[key][index] for key in ("high", "low", "close", "volume")]
            if (any(type(value) not in (int, float) or not isfinite(value) or value <= 0
                    for value in values) or not values[1] <= values[2] <= values[0]):
                continue
            bars.append((stamp, *values))
    except (OSError, KeyError, ValueError, TypeError, IndexError, OverflowError, AttributeError):
        return "dati prezzo/volume indisponibili", []

    bars.sort()
    return (None if regular_open else "sessione regolare chiusa"), bars

def ema(values, period):
    average = mean(values[:period])
    for value in values[period:]:
        average += 2 * (value - average) / (period + 1)
    return average


def evaluate_bars(bars, direction, published, now, *, invest=False, session_start=0):
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
    indicators = {}
    if invest:
        history = bars[-50:]
        if len(history) < 50 or any(b[0] - a[0] != 60 for a, b in zip(history, history[1:])):
            return "storico insufficiente per EMA50", None
        closes = [bar[3] for bar in history]
        ema20, ema50 = ema(closes, 20), ema(closes, 50)
        changes = [b - a for a, b in zip(closes[-15:-1], closes[-14:])]
        gains = sum(max(0, change) for change in changes)
        losses = sum(max(0, -change) for change in changes)
        momentum15 = entry - closes[-16]
        trend = ema20 - ema50
        indicators = {"ema20": ema20, "ema50": ema50,
                      "rsi": 100 * gains / (gains + losses) if gains + losses else 50,
                      "momentum_1m": entry - closes[-2], "momentum_5m": entry - closes[-6],
                      "momentum_15m": momentum15, "atr": atr,
                      "support": support, "resistance": resistance, "volume": volume}
        if momentum15 * sign <= 0:
            return "momentum 15m contrario al bias", None
    momentum = entry - previous[-5][3]
    if min(trend * sign, momentum * sign, (entry - previous[-1][3]) * sign) <= 0:
        return "tecnica contraria al bias", None
    if not invest:
        # Build complete, session-aligned five-minute bars from the same live series.
        # Check the completed post-news bar when one exists. Earlier in the reaction
        # the one-minute breakout and five-minute momentum provide the confirmation.
        last_five_start = stamp + 60 - (stamp + 60 - session_start) % 300 - 300
        if last_five_start >= published.timestamp():
            by_minute = {bar[0]: bar for bar in bars}
            five_minutes = [by_minute.get(t) for t in range(last_five_start - 60, last_five_start + 300, 60)]
            if all(five_minutes) and (five_minutes[-1][3] - five_minutes[0][3]) * sign <= 0:
                return "barra a cinque minuti contraria al bias", None
    level = resistance if sign > 0 else support
    breakout = (entry - level) * sign
    setup = "breakout"
    if breakout <= 0:
        prior = previous[:-1]
        pivot = min(bar[2] for bar in prior) if sign > 0 else max(bar[1] for bar in prior)
        sweep = previous[-1][2 if sign > 0 else 1]
        if (previous[-1][0] < published.timestamp() or (sweep - pivot) * sign >= 0
                or (entry - pivot) * sign <= 0):
            return "breakout o inversione non confermati", None
        level, breakout, setup = sweep, (entry - sweep) * sign, "inversione"
    if volume < 1.5 * mean(bar[4] for bar in previous):
        return "volume non confermato", None
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
                         "setup": setup, "quote_timestamp": closed.isoformat(), **indicators}


def evaluate(ticker, direction, published, now, fetch_series=fetch_intraday_series, *, instrument_type=None):
    if not re.fullmatch(r"[A-Z][A-Z0-9.-]{0,9}", ticker) or direction not in {"LONG", "SHORT"}:
        return "strumento non idoneo", None
    if not timedelta(0) <= now - published <= MAX_CATALYST_AGE:
        return "catalizzatore fuori finestra intraday", None

    expected = instrument_type or ("ETF" if ticker in {"QQQ", "SPY"} else "EQUITY")
    session_start = 0

    def fetch(symbol):
        nonlocal session_start
        series = fetch_series(symbol)
        session_start = series["meta"]["currentTradingPeriod"]["regular"]["start"]
        return series

    error, bars = read_bars(ticker, now, expected, fetch)
    if error:
        return error, None
    return evaluate_bars(bars, direction, published, now, invest=instrument_type is not None,
                         session_start=session_start)
