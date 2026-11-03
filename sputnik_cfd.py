"""SPUTNIK CFD signal helpers.

Keep a supported LONG/SHORT catalyst visible as BIAS when setup confirmation
or fresh execution data is missing. D-L-A grades setup timing; it does not veto
the directional hypothesis. This module never executes a paper or live order.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import math
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_RISK_PCT = 1.0
DEFAULT_CAPITAL = 300.0
ATR_MULTIPLIER = 1.5          # SL distance = 1.5 * ATR
QUOTE_MAX_AGE_MIN = 30


def _number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def _quote_age_seconds(quote: dict[str, Any]) -> float | None:
    stamp = quote.get("timestamp") or quote.get("updated_at") or quote.get("as_of")
    if not stamp:
        return None
    try:
        dt = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds()
    except (TypeError, ValueError):
        return None


def _quote_is_fresh(quote: dict[str, Any], max_age_minutes: int = QUOTE_MAX_AGE_MIN) -> bool:
    age = _quote_age_seconds(quote)
    return age is not None and -60 <= age <= max_age_minutes * 60


def _find_quote(instrument: str, quotes: dict[str, Any]) -> dict[str, Any] | None:
    """Map common commodity names to possible quote keys."""
    instrument = (instrument or "").upper()
    # Decision scenarios use display labels such as "ORO (XAU/USD)" and
    # "BRENT (petrolio)". Resolve the instrument family before quote lookup.
    base_name = instrument.split("(", 1)[0].strip()
    if base_name in {"ORO", "GOLD"}:
        base_name = "GOLD"
    elif base_name.startswith("BRENT"):
        base_name = "BRENT"
    elif base_name.startswith("WTI") or base_name == "PETROLIO WTI":
        base_name = "WTI"
    elif base_name.startswith("NASDAQ"):
        base_name = "NASDAQ100"
    mapping = {
        "WTI": ["WTI", "USOIL", "CL", "USOIL.cash"],
        "BRENT": ["BRENT", "UKOIL", "BRN", "UKOIL.cash"],
        "GOLD": ["GOLD", "XAUUSD", "XAU/USD", "XAUUSD.cash"],
        "SILVER": ["SILVER", "XAGUSD", "XAG/USD"],
        "COPPER": ["COPPER", "HG", "XCUUSD"],
        "NATURAL_GAS": ["NATGAS", "NG", "NATURALGAS"],
        "NASDAQ100": ["NASDAQ100", "NAS100", "USTEC", "QQQ"],
    }
    keys = mapping.get(base_name, [base_name])
    for key in keys:
        q = quotes.get(key) or quotes.get(key.lower()) or quotes.get(key.upper())
        if isinstance(q, dict):
            return q
    return None



YAHOO_FUTURES = {
    "GOLD": "GC=F", "ORO": "GC=F", "SILVER": "SI=F", "ARGENTO": "SI=F",
    "COPPER": "HG=F", "RAME": "HG=F", "WTI": "CL=F", "PETROLIO WTI": "CL=F",
    "BRENT": "BZ=F", "NATURAL_GAS": "NG=F", "GAS NATURALE": "NG=F",
    "WHEAT": "ZW=F", "GRANO": "ZW=F", "CORN": "ZC=F", "MAIS": "ZC=F",
    "SOYBEAN": "ZS=F", "SOIA": "ZS=F",
}

# Yahoo continuous futures are execution-basis quotes. Yahoo does not expose
# the exact delivery month through this chart symbol, so it is never treated
# as an exact-expiry match with a spot reference.
YAHOO_FUTURES_METADATA = {
    "GC=F": {"currency": "USD", "unit": "troy_oz", "market_type": "FUTURES_CONTINUOUS",
             "contract_description": "COMEX gold continuous futures; exact expiry not exposed"},
    "SI=F": {"currency": "USD", "unit": "troy_oz", "market_type": "FUTURES_CONTINUOUS",
             "contract_description": "COMEX silver continuous futures; exact expiry not exposed"},
    "HG=F": {"currency": "USD", "unit": "pound", "market_type": "FUTURES_CONTINUOUS",
             "contract_description": "COMEX copper continuous futures; exact expiry not exposed"},
    "CL=F": {"currency": "USD", "unit": "barrel", "market_type": "FUTURES_CONTINUOUS",
             "contract_description": "NYMEX WTI continuous futures; exact expiry not exposed"},
    "BZ=F": {"currency": "USD", "unit": "barrel", "market_type": "FUTURES_CONTINUOUS",
             "contract_description": "ICE Brent continuous futures; exact expiry not exposed"},
    "NG=F": {"currency": "USD", "unit": "MMBtu", "market_type": "FUTURES_CONTINUOUS",
             "contract_description": "NYMEX natural gas continuous futures; exact expiry not exposed"},
    "ZW=F": {"currency": "USD", "unit": "bushel", "market_type": "FUTURES_CONTINUOUS",
             "contract_description": "CBOT wheat continuous futures; exact expiry not exposed"},
    "ZC=F": {"currency": "USD", "unit": "bushel", "market_type": "FUTURES_CONTINUOUS",
             "contract_description": "CBOT corn continuous futures; exact expiry not exposed"},
    "ZS=F": {"currency": "USD", "unit": "bushel", "market_type": "FUTURES_CONTINUOUS",
             "contract_description": "CBOT soybean continuous futures; exact expiry not exposed"},
}


def fetch_yahoo_quote(instrument: str, timeout: int = 8) -> dict[str, Any] | None:
    """Fetch latest Yahoo 1-minute futures candle and calculate ATR(14)."""
    label = str(instrument or "").upper().split("(", 1)[0].strip()
    symbol = YAHOO_FUTURES.get(label)
    if not symbol:
        for name, ticker in YAHOO_FUTURES.items():
            if label.startswith(name):
                symbol = ticker
                break
    if not symbol:
        return None
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + urllib.parse.quote(symbol, safe="=")
    url += "?range=1d&interval=1m&includePrePost=true"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 SputnikMarketData/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        result = payload["chart"]["result"][0]
        timestamps = result.get("timestamp") or []
        quote_data = result["indicators"]["quote"][0]
        opens = quote_data.get("open") or []
        highs = quote_data.get("high") or []
        lows = quote_data.get("low") or []
        closes = quote_data.get("close") or []
        volumes = quote_data.get("volume") or []
        # Preserve the legacy H/L/C ATR fallback. OHLCV candles are built
        # only when Yahoo actually supplies every required field.
        raw_hlc = [
            (float(h), float(l), float(cl), int(ts))
            for h, l, cl, ts in zip(highs, lows, closes, timestamps)
            if h is not None and l is not None and cl is not None
            and math.isfinite(float(h)) and math.isfinite(float(l)) and math.isfinite(float(cl))
        ]
        if len(raw_hlc) < 15:
            return None
        candles = [
            {"open": float(o), "high": float(h), "low": float(l),
             "close": float(cl), "volume": float(v), "timestamp": int(ts)}
            for o, h, l, cl, v, ts in zip(opens, highs, lows, closes, volumes, timestamps)
            if o is not None and h is not None and l is not None and cl is not None and v is not None
            and math.isfinite(float(o)) and math.isfinite(float(h))
            and math.isfinite(float(l)) and math.isfinite(float(cl)) and math.isfinite(float(v))
            and float(v) > 0
        ]
        true_ranges = []
        previous_close = None
        for high, low, close, _ in raw_hlc:
            tr = high - low if previous_close is None else max(
                high - low, abs(high - previous_close), abs(low - previous_close)
            )
            true_ranges.append(tr)
            previous_close = close
        atr = sum(true_ranges[-14:]) / 14
        high, low, close, stamp = raw_hlc[-1]
        timestamp = datetime.fromtimestamp(stamp, timezone.utc).isoformat()
        metadata = YAHOO_FUTURES_METADATA.get(symbol, {})
        return {
            "price": close, "atr": atr,
            "timestamp": timestamp,
            "provider": "Yahoo Finance chart (1m futures)", "symbol": symbol,
            "currency": metadata.get("currency"),
            "unit": metadata.get("unit"),
            "market_type": metadata.get("market_type", "FUTURES_CONTINUOUS"),
            "contract_description": metadata.get("contract_description"),
            "bid": None, "ask": None,
            "age_seconds": _quote_age_seconds({"timestamp": timestamp}),
            "candle_high": high, "candle_low": low,
            "candles": candles,
        }
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        return None



SILV_SPOT_KEYS = {
    "GOLD": "gold", "ORO": "gold",
    "SILVER": "silver", "ARGENTO": "silver",
    "COPPER": "copper", "RAME": "copper",
}


def fetch_silv_reference(instrument: str, timeout: int = 6) -> dict[str, Any] | None:
    """Free keyless spot reference; never substitutes a futures execution quote."""
    label = str(instrument or "").upper().split("(", 1)[0].strip()
    key = SILV_SPOT_KEYS.get(label)
    if not key:
        return None
    request = urllib.request.Request(
        "https://data.silv.app/commodities.json",
        headers={"User-Agent": "Mozilla/5.0 SputnikMultiSource/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        item = (payload.get("commodities") or {}).get(key) or {}
        price = _number(item.get("price"))
        stamp = item.get("last_updated") or item.get("timestamp")
        if price is None or not stamp:
            return None
        reference = {
            "price": price,
            "bid": _number(item.get("bid")),
            "ask": _number(item.get("ask")),
            "timestamp": stamp,
            "observed_at": item.get("timestamp") or (payload.get("metadata") or {}).get("updated"),
            "provider": "SILV DATA spot reference",
            "symbol": item.get("symbol") or key.upper(),
            "currency": str(item.get("currency") or "").upper() or None,
            "unit": item.get("unit"),
            "market_type": "SPOT",
            "age_seconds": _quote_age_seconds({"timestamp": stamp}),
            "source_components": sorted({
                str(source.get("source") or "").strip().lower()
                for source in (item.get("source_prices") or [])
                if isinstance(source, dict) and str(source.get("source") or "").strip()
            }),
        }
        return reference if _quote_is_fresh(reference, 30) else None
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _canonical_unit(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "troy_oz": "troy_oz",
        "troy_ounce": "troy_oz",
        "troy_ounces": "troy_oz",
        "troy_ounce(s)": "troy_oz",
        "lb": "pound",
        "lbs": "pound",
        "pounds": "pound",
        "pound": "pound",
        "bbl": "barrel",
        "bbls": "barrel",
        "barrels": "barrel",
        "barrel": "barrel",
        "bushels": "bushel",
        "bushel": "bushel",
        "mmbtu": "mmbtu",
    }
    return aliases.get(normalized, normalized or None)


def attach_silv_crosscheck(quote: dict[str, Any], instrument: str) -> dict[str, Any]:
    """Attach a separately labelled spot/futures basis; never blend price bases."""
    reference = fetch_silv_reference(instrument)
    quote["crosscheck_provider"] = "SILV DATA"
    quote["crosscheck_price"] = None
    quote["crosscheck_bid"] = None
    quote["crosscheck_ask"] = None
    quote["crosscheck_timestamp"] = None
    quote["crosscheck_age_seconds"] = None
    quote["crosscheck_currency"] = None
    quote["crosscheck_unit"] = None
    quote["crosscheck_market_type"] = None
    quote["crosscheck_source_components"] = []
    quote["crosscheck_independent"] = None
    quote["crosscheck_independence_status"] = "NOT_ASSESSED"
    quote["spot_futures_basis_price"] = None
    quote["spot_futures_basis_pct"] = None
    quote["crosscheck_status"] = "UNAVAILABLE_OR_STALE"

    if not reference:
        return quote

    ref_price = _number(reference.get("price"))
    quote["crosscheck_price"] = ref_price
    quote["crosscheck_bid"] = _number(reference.get("bid"))
    quote["crosscheck_ask"] = _number(reference.get("ask"))
    quote["crosscheck_timestamp"] = reference.get("timestamp")
    quote["crosscheck_age_seconds"] = reference.get("age_seconds")
    quote["crosscheck_currency"] = reference.get("currency")
    quote["crosscheck_unit"] = reference.get("unit")
    quote["crosscheck_market_type"] = reference.get("market_type")
    source_components = list(reference.get("source_components") or [])
    quote["crosscheck_source_components"] = source_components

    execution_price = _number(quote.get("price"))
    execution_currency = str(quote.get("currency") or "").upper()
    reference_currency = str(reference.get("currency") or "").upper()
    execution_unit = _canonical_unit(quote.get("unit"))
    reference_unit = _canonical_unit(reference.get("unit"))
    execution_market = str(quote.get("market_type") or "").upper()
    reference_market = str(reference.get("market_type") or "").upper()

    execution_provider = str(quote.get("provider") or "").lower()
    execution_source = (
        "yahoo" if "yahoo" in execution_provider
        else "biquote" if "biquote" in execution_provider
        else "twelvedata" if "twelve data" in execution_provider or "twelvedata" in execution_provider
        else None
    )
    if not source_components:
        quote["crosscheck_status"] = "UNVERIFIED_SOURCE_COMPOSITION"
    elif execution_source is None:
        quote["crosscheck_status"] = "UNVERIFIED_EXECUTION_SOURCE"
    elif execution_source in source_components:
        quote["crosscheck_status"] = "SOURCE_OVERLAP"
        quote["crosscheck_independent"] = False
        quote["crosscheck_independence_status"] = "KNOWN_SOURCE_OVERLAP"
    elif execution_price is None or ref_price is None:
        quote["crosscheck_status"] = "UNCOMPARABLE_PRICE"
    elif not execution_currency or not reference_currency or not execution_unit or not reference_unit:
        quote["crosscheck_status"] = "UNCOMPARABLE_METADATA_MISSING"
    elif execution_currency != reference_currency:
        quote["crosscheck_status"] = "UNCOMPARABLE_CURRENCY"
    elif execution_unit != reference_unit:
        quote["crosscheck_status"] = "UNCOMPARABLE_UNIT"
    elif execution_market not in {"FUTURES", "FUTURES_CONTINUOUS"} or reference_market != "SPOT":
        quote["crosscheck_status"] = "UNCOMPARABLE_MARKET_TYPE"
    else:
        # Signed basis is spot minus futures. SILV reports component names,
        # but their independence is not independently audited. Keep the
        # descriptive basis while refusing to label this source independent.
        basis = ref_price - execution_price
        quote["spot_futures_basis_price"] = round(basis, 6)
        quote["spot_futures_basis_pct"] = round(basis / execution_price * 100, 4)
        quote["spot_futures_basis_definition"] = "spot_minus_futures"
        quote["crosscheck_independent"] = None
        quote["crosscheck_independence_status"] = "PROVIDER_REPORTED_NOT_AUDITED"
        quote["crosscheck_status"] = "SPOT_VS_FUTURES_BASIS_CHECK_INDEPENDENCE_UNVERIFIED"

    return quote



# Optional Narwhal free-plan futures reference. Read-only; never execution.
NARWHAL_FUTURES_URL = "https://api.narwhalapi.com/v1/futures/{root}/price"
NARWHAL_REFERENCE_ROTATION_SECONDS = 1800
NARWHAL_REFERENCE_MAX_AGE_SECONDS = 900
NARWHAL_FUTURES_ROOTS = {
    "GOLD": "GC", "ORO": "GC", "SILVER": "SI", "ARGENTO": "SI",
    "COPPER": "HG", "RAME": "HG", "WTI": "CL", "PETROLIO WTI": "CL",
    "WHEAT": "ZW", "GRANO": "ZW", "CORN": "ZC", "MAIS": "ZC",
    "SOYBEAN": "ZS", "SOIA": "ZS",
}
_NARWHAL_SLOT_CACHE: dict[int, dict[str, Any]] = {}


def fetch_narwhal_reference(instrument: str, timeout: int = 6) -> dict[str, Any]:
    """Fetch one delayed free-tier quote as reference-only metadata."""
    label = str(instrument or "").upper().split("(", 1)[0].strip()
    root = NARWHAL_FUTURES_ROOTS.get(label)
    base = {
        "provider": "NARWHAL", "symbol": root, "price": None,
        "source_timestamp": None, "currency": None, "unit": None,
        "bid": None, "ask": None, "age_seconds": None,
        "market_type": "FUTURES_FRONT_MONTH_CONTINUOUS",
        "contract_month": None, "deviation_pct": None,
        "source_independence_status": "UNVERIFIED_UPSTREAM_ROUTING_NOT_DISCLOSED",
        "status": "NOT_COVERED" if not root else "DISABLED",
        "use_restriction": "REFERENCE_ONLY_NOT_FOR_TRADE_EXECUTION",
    }
    if not root:
        return base
    if os.getenv("NARWHAL_REFERENCE_ENABLED", "0").strip() != "1":
        return base
    api_key = os.getenv("NARWHAL_API_KEY", "").strip()
    if not api_key:
        base["status"] = "NOT_CONFIGURED"
        return base

    slot = int(time.time() // NARWHAL_REFERENCE_ROTATION_SECONDS)
    rotation = tuple(dict.fromkeys(NARWHAL_FUTURES_ROOTS.values()))
    scheduled_root = rotation[slot % len(rotation)]
    if root != scheduled_root:
        base["status"] = "NOT_SCHEDULED_THIS_SLOT"
        base["scheduled_symbol"] = scheduled_root
        return base
    cached = _NARWHAL_SLOT_CACHE.get(slot)
    if cached is not None:
        return dict(cached)

    _NARWHAL_SLOT_CACHE[slot] = {**base, "status": "REQUEST_PENDING"}
    request = urllib.request.Request(
        NARWHAL_FUTURES_URL.format(root=root),
        headers={
            "User-Agent": "SPUTNIK-MultiSource/1.0",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        status = "RATE_LIMITED" if exc.code == 429 else f"HTTP_ERROR_{exc.code}"
        result = {**base, "status": status}
        _NARWHAL_SLOT_CACHE[slot] = result
        return dict(result)
    except (OSError, TimeoutError, ValueError, TypeError):
        result = {**base, "status": "REQUEST_OR_JSON_ERROR"}
        _NARWHAL_SLOT_CACHE[slot] = result
        return dict(result)

    if not isinstance(payload, dict) or str(payload.get("id") or "").upper() != root:
        result = {**base, "status": "INVALID_RESPONSE_OR_SYMBOL_MISMATCH"}
        _NARWHAL_SLOT_CACHE[slot] = result
        return dict(result)

    price = _number(payload.get("price"))
    timestamp = payload.get("timestamp")
    age = _quote_age_seconds({"timestamp": timestamp}) if timestamp else None
    currency = str(payload.get("currency") or "").upper()
    unit = str(payload.get("unit") or "").strip()
    if price is None:
        status = "INVALID_PRICE"
    elif age is None or age < -60:
        status = "INVALID_TIMESTAMP"
    elif currency != "USD" or not unit:
        status = "INVALID_PRICE_METADATA"
    else:
        session = str(payload.get("market_session") or "unknown").lower()
        if payload.get("stale") is True or (session == "open" and age > NARWHAL_REFERENCE_MAX_AGE_SECONDS):
            status = "STALE"
        elif session == "closed":
            status = "MARKET_CLOSED"
        elif payload.get("delayed") is True:
            status = "DELAYED_15M"
        else:
            status = "DELAY_STATUS_UNVERIFIED"

    usable_statuses = {"DELAYED_15M", "MARKET_CLOSED", "STALE", "DELAY_STATUS_UNVERIFIED"}
    observed_at = datetime.now(timezone.utc).isoformat()
    result = {
        **base,
        "price": price if status in usable_statuses else None,
        "source_timestamp": timestamp,
        "observed_at": observed_at,
        "currency": currency or None,
        "unit": unit or None,
        "age_seconds": round(max(0.0, age), 1) if age is not None else None,
        "delayed": payload.get("delayed") if isinstance(payload.get("delayed"), bool) else None,
        "stale": payload.get("stale") if isinstance(payload.get("stale"), bool) else None,
        "market_session": str(payload.get("market_session") or "unknown").lower(),
        "price_scale": payload.get("price_scale"),
        "unit_key": payload.get("unit_key"),
        "status": status,
    }
    _NARWHAL_SLOT_CACHE[slot] = result
    for old_slot in sorted(_NARWHAL_SLOT_CACHE)[:-4]:
        _NARWHAL_SLOT_CACHE.pop(old_slot, None)
    return dict(result)



def build_cfd_signal(
    recommendation: dict[str, Any] | None,
    quotes: dict[str, Any] | None = None,
    risk_pct: float = DEFAULT_RISK_PCT,
) -> dict[str, Any]:
    """Build a standardized CFD signal dict from a SPUTNIK recommendation.

    Returns a dict with keys: instrument, direction, entry, stop, tp1, tp2,
    atr, score, status, reason, confirmation, risk_pct, timestamp.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    base = {
        "instrument": "N/D",
        "direction": "NEUTRAL",
        "entry": None,
        "stop": None,
        "tp1": None,
        "tp2": None,
        "atr": None,
        "score": 0,
        "status": "NO_DIRECTION",
        "reason": "Nessuna raccomandazione direzionale disponibile.",
        "confirmation": "D-L-A valuta qualità e timing del setup; non annulla un bias LONG/SHORT.",
        "bias_status": "NO_DIRECTION",
        "setup_status": "NO_DIRECTION",
        "setup_direction": "NEUTRAL / NO_DIRECTION",
        "setup_alignment": "NOT_ASSESSED",
        "paper_trade_status": "NOT_EXECUTED",
        "execution_readiness": "NO_DIRECTIONAL_EDGE",
        "risk_pct": risk_pct,
        "timestamp": now,
        "paper_only": True,
    }
    if not recommendation:
        return base

    instrument = str(recommendation.get("instrument") or "N/D").upper()
    bias = str(recommendation.get("bias") or "NEUTRAL").upper()
    score = float(recommendation.get("score") or 0)
    reason = str(recommendation.get("reason") or "")
    confirmation = str(recommendation.get("confirmation") or "Verifica prezzo e volume live.")

    direction = "LONG" if "LONG" in bias else "SHORT" if "SHORT" in bias else "NEUTRAL"
    directional = direction in {"LONG", "SHORT"}
    base.update({
        "instrument": instrument,
        "direction": direction,
        "score": score,
        "reason": reason,
        "confirmation": confirmation,
        "status": "EARLY_BIAS" if directional else "NO_DIRECTION",
        "bias_status": "DIRECTIONAL_BIAS" if directional else "NO_DIRECTION",
        "setup_status": "EARLY_BIAS" if directional else "NO_DIRECTION",
        "paper_trade_status": "NOT_EXECUTED",
        "execution_readiness": "EARLY_BIAS" if directional else "NO_DIRECTIONAL_EDGE",
    })

    quotes = quotes or {}
    quote = _find_quote(instrument, quotes)
    if not quote or not _quote_is_fresh(quote):
        # Pull a fresh public 1m futures candle and calculate ATR automatically.
        quote = fetch_yahoo_quote(instrument)
    # Delayed Narwhal quote is reference-only and never creates execution levels.
    base["narwhal_reference"] = fetch_narwhal_reference(instrument)
    if quote and _quote_is_fresh(quote):
        quote = attach_silv_crosscheck(quote, instrument)
    # Analyze only the commodity selected by the news engine, when OHLCV is supplied.
    if quote and isinstance(quote.get("candles"), list):
        try:
            from sputnik_focused_trader import analyze_focused_market
            focused = analyze_focused_market(instrument, quote["candles"])
            base["focused_analysis"] = focused
            if focused.get("status") == "DIRECTIONAL":
                technical_direction = str(focused.get("direction") or "NEUTRAL").upper()
                base["technical_direction"] = technical_direction
                if base["direction"] not in {"LONG", "SHORT"}:
                    base["direction"] = technical_direction
                    base["bias_source"] = "TECHNICAL_ONLY"
                    base["technical_alignment"] = "TECHNICAL_ONLY"
                else:
                    base["technical_alignment"] = "ALIGNS" if technical_direction == base["direction"] else "CONTRASTS"
                base["reason"] += " | Analisi tecnica focused " + base["technical_alignment"] + ": " + str(focused.get("reason") or "")
            elif focused.get("status") == "WAIT_CONFIRMATION":
                # Keep the directional news thesis; missing trigger confirmation
                # lowers readiness but does not erase the market hypothesis.
                base["reason"] += " | Bias news non ancora confermato dal trigger tecnico: " + str(focused.get("reason") or "")
                base["execution_readiness"] = "EARLY_BIAS"
        except Exception as exc:
            base["reason"] += " | Analisi tecnica focused non disponibile: " + type(exc).__name__
    # Professional-style execution gate: Direction -> Location -> Aggression.
    # This is an OHLCV proxy, not true bid/ask footprint or DOM order flow.
    if quote and _quote_is_fresh(quote) and isinstance(quote.get("candles"), list) and len(quote["candles"]) >= 60:
        try:
            from sputnik_competition_setup import evaluate_competition_setup
            setup = evaluate_competition_setup(instrument, quote["candles"])
            base["competition_setup"] = setup
            setup_status = str(setup.get("status") or "NO_DIRECTION").upper()
            setup_direction = str(setup.get("direction") or "NEUTRAL").upper()
            if setup_status == "SETUP_CONFIRMED":
                base["setup_direction"] = setup_direction
                if base["direction"] not in {"LONG", "SHORT"}:
                    base["direction"] = setup_direction
                    base["bias_source"] = "DLA_ONLY"
                    base["setup_alignment"] = "TECHNICAL_ONLY"
                    base["execution_readiness"] = "CONFIRMED"
                elif setup_direction == base["direction"]:
                    base["setup_alignment"] = "ALIGNS"
                    base["execution_readiness"] = "CONFIRMED"
                else:
                    # A confirmed technical setup in the opposite direction
                    # grades the catalyst as CONTRASTS; it never flips the bias.
                    base["setup_alignment"] = "CONTRASTS"
                    base["execution_readiness"] = "EARLY_BIAS"
                base["reason"] += " | D-L-A " + str(base.get("setup_alignment")) + ": " + "; ".join(setup.get("confirmations") or [])
            elif setup_status == "EARLY_SETUP" and setup_direction in {"LONG", "SHORT"}:
                # Preserve the D-L context direction before the trigger. It is
                # a setup grade, not an execution authorization or news veto.
                base["setup_direction"] = setup_direction
                if base["direction"] in {"LONG", "SHORT"}:
                    base["setup_alignment"] = "ALIGNS" if setup_direction == base["direction"] else "CONTRASTS"
                else:
                    base["direction"] = setup_direction
                    base["bias_source"] = "DLA_EARLY"
                    base["setup_alignment"] = "TECHNICAL_ONLY"
                base["execution_readiness"] = "EARLY_BIAS"
                details = setup.get("confirmations") or setup.get("missing_conditions") or ["trigger/aggressione non confermati"]
                base["reason"] += " | D-L-A EARLY_SETUP (OHLCV proxy): " + "; ".join(details)
            else:
                # Neutral or insufficient D-L-A data never emits WAIT and
                # never removes a separately supported catalyst direction.
                base["setup_direction"] = "NEUTRAL / NO_DIRECTION"
                base["setup_alignment"] = setup_status
                base["execution_readiness"] = (
                    "EARLY_BIAS" if base["direction"] in {"LONG", "SHORT"}
                    else "NO_DIRECTIONAL_EDGE"
                )
                details = setup.get("reasons") or setup.get("missing_conditions") or ["nessun contesto D-L-A allineato"]
                base["reason"] += " | D-L-A " + setup_status + " (bias news mantenuto): " + "; ".join(details)
        except Exception as exc:
            base["execution_readiness"] = "EARLY_BIAS"
            base["setup_status"] = "UNVERIFIED"
            base["setup_alignment"] = "UNVERIFIED"
            base["reason"] += " | D-L-A non verificabile; bias direzionale mantenuto: " + type(exc).__name__
    base["bias_status"] = "DIRECTIONAL_BIAS" if base["direction"] in {"LONG", "SHORT"} else "NO_DIRECTION"
    if not quote or not _quote_is_fresh(quote):
        directional = base["direction"] in {"LONG", "SHORT"}
        base["status"] = "EARLY_BIAS" if directional else "NO_DIRECTION"
        base["setup_status"] = "EARLY_BIAS" if directional else "NO_DIRECTION"
        base["execution_readiness"] = "EARLY_BIAS" if directional else "NO_DIRECTIONAL_EDGE"
        base["paper_trade_status"] = "NOT_EXECUTED"
        base["reason"] += " | Quotazione futures fresca assente: il bias resta visibile, entry/SL/TP omessi."
        return base

    entry = _number(quote.get("price") or quote.get("bid") or quote.get("last"))
    atr = _number(quote.get("atr") or quote.get("ATR") or quote.get("atr_14"))
    if entry is None or atr is None:
        directional = base["direction"] in {"LONG", "SHORT"}
        base["status"] = "EARLY_BIAS" if directional else "NO_DIRECTION"
        base["setup_status"] = "EARLY_BIAS" if directional else "NO_DIRECTION"
        base["execution_readiness"] = "EARLY_BIAS" if directional else "NO_DIRECTIONAL_EDGE"
        base["paper_trade_status"] = "NOT_EXECUTED"
        base["reason"] += " | Prezzo futures o ATR non valido/mancante: bias mantenuto, entry/SL/TP omessi."
        return base

    distance = ATR_MULTIPLIER * atr
    if base["direction"] == "LONG":
        stop = entry - distance
        tp1 = entry + distance          # 1R
        tp2 = entry + 2 * distance      # 2R
    elif base["direction"] == "SHORT":
        stop = entry + distance
        tp1 = entry - distance
        tp2 = entry - 2 * distance
    else:
        base["status"] = "NO_DIRECTION"
        base["bias_status"] = "NO_DIRECTION"
        base["setup_status"] = "NO_DIRECTION"
        base["execution_readiness"] = "NO_DIRECTIONAL_EDGE"
        base["paper_trade_status"] = "NOT_EXECUTED"
        return base

    setup_state = "CONFIRMED" if base.get("execution_readiness") == "CONFIRMED" else "EARLY_SETUP"
    base.update({
        "entry": round(entry, 4),
        "stop": round(stop, 4),
        "tp1": round(tp1, 4),
        "tp2": round(tp2, 4),
        "atr": round(atr, 4),
        "status": setup_state,
        "bias_status": "DIRECTIONAL_BIAS",
        "setup_status": setup_state,
        "paper_trade_status": "NOT_EXECUTED",
        "execution_readiness": setup_state,
        "quote_time": quote.get("timestamp") or quote.get("updated_at"),
        "quote_provider": quote.get("provider") or "state/provider",
        "quote_symbol": quote.get("symbol") or instrument,
        "quote_currency": quote.get("currency"),
        "quote_unit": quote.get("unit"),
        "quote_market_type": quote.get("market_type"),
        "quote_contract_description": quote.get("contract_description"),
        "quote_bid": _number(quote.get("bid")),
        "quote_ask": _number(quote.get("ask")),
        "quote_age_seconds": _quote_age_seconds(quote),
        "quote_status": "FRESH",
        "crosscheck_provider": quote.get("crosscheck_provider"),
        "crosscheck_status": quote.get("crosscheck_status"),
        "crosscheck_price": quote.get("crosscheck_price"),
        "crosscheck_bid": quote.get("crosscheck_bid"),
        "crosscheck_ask": quote.get("crosscheck_ask"),
        "crosscheck_timestamp": quote.get("crosscheck_timestamp"),
        "crosscheck_age_seconds": quote.get("crosscheck_age_seconds"),
        "crosscheck_currency": quote.get("crosscheck_currency"),
        "crosscheck_unit": quote.get("crosscheck_unit"),
        "crosscheck_market_type": quote.get("crosscheck_market_type"),
        "crosscheck_source_components": quote.get("crosscheck_source_components"),
        "crosscheck_independent": quote.get("crosscheck_independent"),
        "crosscheck_independence_status": quote.get("crosscheck_independence_status"),
        "spot_futures_basis_price": quote.get("spot_futures_basis_price"),
        "spot_futures_basis_pct": quote.get("spot_futures_basis_pct"),
        "spot_futures_basis_definition": quote.get("spot_futures_basis_definition"),
        "narwhal_reference": base.get("narwhal_reference"),
    })
    return base


def format_cfd_signal(signal: dict[str, Any]) -> str:
    """Telegram-ready BIAS / SETUP / PAPER status message; never implies an order."""
    if not signal or signal.get("status") == "NO_SIGNAL":
        return (
            "🛰️ SPUTNIK — ANALISI CFD\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🟡 BIAS: NEUTRAL / NO_DIRECTION\n"
            "🎯 SETUP: NO_DIRECTION\n"
            "🧪 TRADE PAPER: NOT_EXECUTED\n"
            "⚠️ Nessun ordine inviato."
        )

    direction = signal.get("direction", "NEUTRAL")
    icon = "🟢" if direction == "LONG" else "🔴" if direction == "SHORT" else "🟡"
    status = signal.get("status", "NO_DIRECTION")
    setup_status = signal.get("setup_status", status)
    paper_status = signal.get("paper_trade_status", "NOT_EXECUTED")

    lines = [
        f"{icon} SPUTNIK — ANALISI CFD",
        "━━━━━━━━━━━━━━━━━━",
        "🧪 PAPER ONLY • NESSUN ORDINE AUTOMATICO",
        f"🕒 {signal.get('timestamp', '')}",
        "",
        f"📈 STRUMENTO: {signal.get('instrument')}",
        f"🧭 BIAS: {direction}",
        f"🎯 SETUP: {setup_status}",
        f"🧭 TECNICA: {signal.get('technical_direction', 'N/D')} ({signal.get('technical_alignment', 'NOT_ASSESSED')})",
        f"🧪 D-L-A: {signal.get('setup_direction', 'N/D')} ({signal.get('setup_alignment', 'NOT_ASSESSED')})",
        f"🧪 TRADE PAPER: {paper_status}",
        f"📊 SCORE: {signal.get('score', 0):.0f}/100",
        f"📌 STATO: {status}",
    ]

    # Show the exact execution quote behind these levels. The builder already
    # records this metadata; omitting it made a fresh-looking setup impossible
    # to audit against its source timestamp and market basis.
    quote_metadata_keys = (
        "quote_provider", "quote_symbol", "quote_time", "quote_market_type",
        "quote_age_seconds",
    )
    if any(signal.get(key) is not None for key in quote_metadata_keys):
        quote_age = signal.get("quote_age_seconds")
        try:
            quote_age_value = float(quote_age)
            quote_age_text = f"{quote_age_value:.0f}s" if math.isfinite(quote_age_value) else "N/D"
        except (TypeError, ValueError, OverflowError):
            quote_age_text = "N/D"
        quote_bid = signal.get("quote_bid")
        quote_ask = signal.get("quote_ask")
        lines.extend([
            "",
            f"📡 QUOTAZIONE: {signal.get('quote_provider') or 'N/D'} | {signal.get('quote_symbol') or 'N/D'} | {signal.get('quote_status') or 'N/D'}",
            f"🧾 MERCATO: {signal.get('quote_market_type') or 'N/D'} | {signal.get('quote_currency') or 'N/D'}/{signal.get('quote_unit') or 'N/D'}",
            f"🕒 QUOTE UTC: {signal.get('quote_time') or 'N/D'} | età {quote_age_text}",
            f"↔️ BID/ASK: {quote_bid if quote_bid is not None else 'N/D'}/{quote_ask if quote_ask is not None else 'N/D'}",
        ])
        contract_description = signal.get("quote_contract_description")
        if contract_description:
            lines.append(f"📅 CONTRATTO: {str(contract_description)[:180]}")
    else:
        lines.extend(["", "📡 QUOTAZIONE: N/D — fonte e timestamp non disponibili."])

    if signal.get("entry") is not None:
        lines.extend([
            "",
            f"💰 ENTRY: {signal['entry']}",
            f"🛑 SL:    {signal['stop']}",
            f"🎯 TP1:   {signal['tp1']} (1R)",
            f"🎯 TP2:   {signal['tp2']} (2R)",
            f"📏 ATR:   {signal.get('atr')}",
        ])
    elif direction in {"LONG", "SHORT"}:
        lines.append("\n⏳ BIAS mantenuto; livelli omessi (entry/SL/TP): quotazione futures fresca o ATR valido non disponibile.")
    else:
        lines.append("\n🟡 NO_DIRECTION: nessuna tesi LONG/SHORT sostenibile.")

    narwhal = signal.get("narwhal_reference") or {}
    if narwhal:
        n_status = narwhal.get("status", "UNKNOWN")
        n_price = narwhal.get("price")
        n_age = narwhal.get("age_seconds")
        if n_price is not None:
            lines.append("🌊 NARWHAL REF: " + str(narwhal.get("symbol") or "") + " " + str(n_price) + " " + str(narwhal.get("currency") or "") + "/" + str(narwhal.get("unit") or "") + " | " + str(n_status) + " | età " + str(n_age) + "s | bid/ask n.d.")
            lines.append("🕒 Fonte Narwhal: " + str(narwhal.get("source_timestamp") or "N/D") + " | ricevuto: " + str(narwhal.get("observed_at") or "N/D"))
        else:
            lines.append("🌊 NARWHAL REF: " + str(n_status) + " (solo riferimento; nessun prezzo utilizzabile)")
        lines.append("⚠️ Front-month continuo; scadenza esatta e indipendenza upstream non verificate. Non usare per entry/SL/TP.")

    if signal.get("crosscheck_status"):
        lines.extend(["", f"🔎 CONTROLLO SPOT/FUTURES: {signal['crosscheck_status']}"])
        if signal.get("crosscheck_independence_status") == "PROVIDER_REPORTED_NOT_AUDITED":
            lines.append("⚠️ Componenti dichiarate da SILV; indipendenza non verificata.")
        elif signal.get("crosscheck_independence_status") == "KNOWN_SOURCE_OVERLAP":
            lines.append("⚠️ Sovrapposizione nota con la fonte di esecuzione.")

    lines.extend([
        "",
        f"📌 MOTIVO: {signal.get('reason', '')[:280]}",
        f"ℹ️ D-L-A: {signal.get('confirmation', '')}",
        f"⚠️ RISK: {signal.get('risk_pct', 1.0):.1f}% max",
        "",
        "⚠️ Analisi informativa. TRADE PAPER non eseguito da questo modulo.",
    ])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Legacy helpers kept for backward compatibility
# ---------------------------------------------------------------------------

def _quote_for(row: dict[str, Any], quotes: dict[str, Any]) -> dict[str, Any] | None:
    keys = (
        str(row.get("ticker") or "").strip().upper(),
        str(row.get("security") or "").strip().upper(),
    )
    for key in keys:
        quote = quotes.get(key) or quotes.get(key.lower())
        if isinstance(quote, dict):
            return quote
    return None


def build_conditional_trade_plan(
    plan: dict[str, Any],
    quotes: dict[str, Any] | None,
    risk_pct: float = DEFAULT_RISK_PCT,
) -> dict[str, Any]:
    """Legacy wrapper — prefer build_cfd_signal for new code."""
    rec = {
        "instrument": plan.get("candidate"),
        "bias": plan.get("bias"),
        "score": plan.get("score", 0),
        "reason": plan.get("reason", ""),
    }
    return build_cfd_signal(rec, quotes, risk_pct)


def cfd_cart_display_state(item: dict[str, Any] | None) -> dict[str, str]:
    """Render cart state without conflating a directional bias with an executed trade.

    The legacy SEC/CFD cart never authorizes an order: a supported side remains
    LONG/SHORT BIAS, setup timing is EARLY_BIAS or EARLY_SETUP, and PAPER stays
    NOT_EXECUTED. Missing or unsupported direction is explicitly NO_DIRECTION.
    """
    item = item if isinstance(item, dict) else {}
    direction = str(item.get("direction") or "NEUTRAL").strip().upper()
    if direction not in {"LONG", "SHORT"}:
        return {
            "direction": "NEUTRAL",
            "bias": "NO_DIRECTION",
            "setup": "NO_DIRECTION",
            "paper_trade": "NOT_EXECUTED",
        }
    setup = str(item.get("setup_status") or item.get("status") or "EARLY_BIAS").strip().upper()
    if setup not in {"EARLY_BIAS", "EARLY_SETUP", "CONFIRMED"}:
        setup = "EARLY_BIAS"
    return {
        "direction": direction,
        "bias": "DIRECTIONAL_BIAS",
        "setup": setup,
        "paper_trade": "NOT_EXECUTED",
    }


def build_cfd_cart(
    ranked_rows: list[dict[str, Any]],
    quotes: dict[str, Any] | None,
    capital: float = DEFAULT_CAPITAL,
    risk_pct: float = DEFAULT_RISK_PCT,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Legacy cart builder with explicit BIAS/SETUP states; never executes a trade."""
    capital_value = _number(capital)
    if capital_value is None:
        raise ValueError("capital must be positive")
    if not 0 < risk_pct <= 5:
        raise ValueError("risk_pct must be between 0 and 5")
    if limit <= 0:
        return []
    cart = []
    for row in ranked_rows[:limit]:
        signal = str(row.get("signal") or "")
        directional = signal == "COMPRA"
        item = {
            "security": row.get("security") or "N/D",
            "company": row.get("company") or "N/D",
            "score": row.get("score", 0),
            "evidence_signal": signal,
            "direction": "LONG" if directional else "NEUTRAL",
            "bias_status": "DIRECTIONAL_BIAS" if directional else "NO_DIRECTION",
            "setup_status": "EARLY_BIAS" if directional else "NO_DIRECTION",
            "paper_trade_status": "NOT_EXECUTED",
            "status": "EARLY_BIAS" if directional else "NO_DIRECTION",
            "entry": None,
            "stop": None,
            "target": None,
            "risk_eur": round(capital_value * risk_pct / 100, 2),
            "units": None,
            "reason": "",
        }
        if not directional:
            item["reason"] = "NO_DIRECTION: evidenza sotto soglia BUY; nessun lato sostenibile."
            cart.append(item)
            continue
        quote = _quote_for(row, quotes or {})
        if not quote or not _quote_is_fresh(quote):
            item["reason"] = "Bias LONG mantenuto; quotazione fresca non disponibile, livelli omessi."
            cart.append(item)
            continue
        entry = _number(quote.get("price"))
        stop = _number(quote.get("stop"))
        target = _number(quote.get("target"))
        if entry is None or stop is None or target is None or not (stop < entry < target):
            item["reason"] = "Bias LONG mantenuto; livelli non validi o incompleti, nessun sizing calcolato."
            cart.append(item)
            continue
        risk_per_unit = entry - stop
        units = (capital_value * risk_pct / 100) / risk_per_unit
        item.update({
            "status": "EARLY_SETUP",
            "setup_status": "EARLY_SETUP",
            "entry": entry,
            "stop": stop,
            "target": target,
            "units": round(units, 6),
            "rr": round((target - entry) / risk_per_unit, 2),
            "reason": "Bias LONG con livelli disponibili; nessuna operazione PAPER è stata registrata o eseguita.",
        })
        cart.append(item)
    return cart
