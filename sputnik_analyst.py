"""SPUTNIK — analista di Trump e dei miliardari.

Segue due fonti pubbliche e le incrocia:
  * Trump: post e comunicati (feed Casa Bianca + archivio Truth Social) già
    raccolti da ``trump_tracker.intelligence_snapshot``;
  * Miliardari: documenti SEC (Form 4, 13D/13G, 13F) di una lista di soggetti.

I messaggi Telegram sono ANALISI informative, non segnali operativi: nessun
ingresso, stop o target. Le operazioni dei miliardari sono pubbliche ma arrivano
in ritardo (Form 4 entro 2 giorni, 13F fino a 45 giorni dopo il trimestre).
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Callable, Iterable

import sputnik_market_call


@dataclass(frozen=True)
class Watched:
    cik: str            # 10 cifre
    label: str          # nome mostrato nei messaggi
    expected: str       # frammento atteso nel nome SEC (verifica anti-errore)
    note: str


# CIK da verificare: a ogni esecuzione il nome restituito dalla SEC deve contenere
# ``expected``, altrimenti il soggetto viene scartato (nessun avviso sbagliato).
WATCHLIST: tuple[Watched, ...] = (
    Watched("0001849635", "Trump Media (DJT)", "TRUMP MEDIA", "società di Trump"),
    Watched("0001494730", "Elon Musk", "MUSK", "Tesla, SpaceX, xAI"),
    Watched("0001067983", "Warren Buffett · Berkshire Hathaway", "BERKSHIRE", "Berkshire Hathaway"),
    Watched("0001336528", "Bill Ackman · Pershing Square", "PERSHING SQUARE", "fondo di Ackman"),
    Watched("0000921669", "Carl Icahn", "ICAHN", "investitore attivista"),
    Watched("0001536411", "Stanley Druckenmiller · Duquesne", "DUQUESNE", "family office"),
    Watched("0001035674", "John Paulson · Paulson & Co", "PAULSON", "finanziatore di Trump"),
    Watched("0001345471", "Nelson Peltz · Trian", "TRIAN", "investitore attivista"),
    Watched("0001649339", "Michael Burry · Scion", "SCION", "fondo di Burry"),
    Watched("0001656456", "David Tepper · Appaloosa", "APPALOOSA", "fondo di Tepper"),
    Watched("0001029160", "George Soros · Soros Fund", "SOROS", "fondo di Soros"),
)

SEC_FORMS = (
    "4,4/A,SC 13D,SC 13D/A,SC 13G,SC 13G/A,SCHEDULE 13D,SCHEDULE 13D/A,"
    "SCHEDULE 13G,SCHEDULE 13G/A,13F-HR,13F-HR/A,8-K"
)

MAX_FILING_AGE_DAYS = 10        # documenti più vecchi: solo archivio, niente avviso
MAX_EXTRACT_PER_RUN = 25        # protegge dai limiti della SEC
MAX_ALERTS_PER_RUN = 6
TRUMP_MAX_AGE_HOURS = 6
LINK_WINDOW_DAYS = 90           # finestra per collegare Trump ↔ miliardari

THEME_LABELS = {
    "ENERGY": "energia/petrolio", "METALS": "metalli/acciaio", "AGRICULTURE": "agricoltura",
    "DEFENSE": "difesa", "AI_TECH": "tecnologia/AI", "SPACE": "spazio", "CRYPTO": "cripto",
    "MEDIA": "media", "REAL_ESTATE": "immobiliare", "TRADE_POLICY": "dazi/commercio",
    "RATES_MACRO": "tassi/dollaro", "FINANCE": "banche/finanza", "PHARMA": "farmaceutico",
    "AUTO": "auto", "MARKET_CALL": "chiamata al mercato",
}

# Parole chiave nel nome del titolo → tema (stessi codici dei temi delle notizie).
SECURITY_THEMES: dict[str, tuple[str, ...]] = {
    "ENERGY": ("oil", "petroleum", "energy", "gas", "chevron", "exxon", "occidental", "conocophillips",
               "halliburton", "schlumberger", "pipeline", "lng", "uranium", "cameco", "vistra", "constellation energy"),
    "METALS": ("steel", "mining", "gold", "copper", "aluminum", "aluminium", "nucor", "freeport",
               "cleveland-cliffs", "alcoa", "newmont", "barrick", "metals"),
    "AGRICULTURE": ("deere", "archer-daniels", "bunge", "mosaic", "nutrien", "corteva", "fertilizer", "tyson"),
    "DEFENSE": ("lockheed", "raytheon", "rtx", "northrop", "general dynamics", "palantir", "l3harris",
                "huntington ingalls", "anduril", "defense", "aerospace", "boeing"),
    "AI_TECH": ("nvidia", "microsoft", "alphabet", "google", "amazon", "meta platforms", "oracle", "apple",
                "semiconductor", "advanced micro", "intel", "broadcom", "taiwan semiconductor", "micron",
                "salesforce", "xai", "coreweave", "super micro"),
    "SPACE": ("spacex", "rocket lab", "space", "satellite", "ast spacemobile"),
    "CRYPTO": ("coinbase", "microstrategy", "strategy inc", "bitcoin", "crypto", "marathon digital",
               "riot platforms", "galaxy digital", "ethereum"),
    "MEDIA": ("trump media", "truth social", "rumble", "fox corp", "news corp", "paramount", "warner", "disney"),
    "REAL_ESTATE": ("realty", "reit", "homes", "hotel", "property", "properties", "hilton", "marriott"),
    "FINANCE": ("bank", "bancorp", "financial", "jpmorgan", "goldman", "morgan stanley", "citigroup",
                "capital one", "american express", "visa", "mastercard", "insurance", "chubb"),
    "PHARMA": ("pharma", "pfizer", "eli lilly", "lilly", "merck", "novo nordisk", "unitedhealth", "biotech", "moderna"),
    "AUTO": ("tesla", "ford motor", "general motors", "stellantis", "toyota", "rivian"),
}

# Temi delle notizie che toccano più settori.
NEWS_THEME_LINKS = {
    "TRADE_POLICY": ("METALS", "AUTO", "AGRICULTURE", "AI_TECH"),
    "RATES_MACRO": ("FINANCE", "REAL_ESTATE"),
}


# ----------------------------------------------------------------------------- utilità

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_time(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    for parser in (lambda s: datetime.fromisoformat(s.replace("Z", "+00:00")), parsedate_to_datetime):
        try:
            parsed = parser(text)
        except (TypeError, ValueError, IndexError, OverflowError):
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    return None


def _parse_day(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value or "")[:10])
    except ValueError:
        return None


def _num(value: Any) -> float | None:
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _money(value: float) -> str:
    if value >= 1e9:
        return f"{value / 1e9:.2f} mld $"
    if value >= 1e6:
        return f"{value / 1e6:.1f} mln $"
    if value >= 1e3:
        return f"{value / 1e3:.0f} mila $"
    return f"{value:.0f} $"


def normalize_cik(value: str) -> str:
    digits = re.sub(r"\D", "", str(value))
    return digits.zfill(10) if digits else ""


def watchlist() -> list[Watched]:
    """Lista di default + eventuali CIK aggiuntivi da SPUTNIK_CIKS (senza verifica nome)."""
    items = list(WATCHLIST)
    known = {w.cik for w in items}
    for raw in os.getenv("SPUTNIK_CIKS", "").split(","):
        cik = normalize_cik(raw)
        if cik and cik not in known:
            items.append(Watched(cik, f"CIK {int(cik)}", "", "aggiunto da configurazione"))
            known.add(cik)
    return items


def by_cik() -> dict[str, Watched]:
    return {w.cik: w for w in watchlist()}


def name_matches(cik: str, sec_name: str) -> bool:
    watched = by_cik().get(normalize_cik(cik))
    if watched is None:
        return False
    return not watched.expected or watched.expected in str(sec_name or "").upper()


def label_for(cik: str, fallback: str = "") -> str:
    watched = by_cik().get(normalize_cik(cik))
    return watched.label if watched else (fallback or f"CIK {cik}")


TRUMP_MEDIA_CIK = "0001849635"


def short_security(name: str) -> str:
    """'Common Stock, $0.01 par value per share' -> 'Common Stock'."""
    text = re.split(r",?\s*\$?[\d.]+\s*par value", str(name or ""), flags=re.IGNORECASE)[0]
    return text.strip(" ,") or str(name or "")


def attribute_trade(cik: str, owner: str, issuer: str) -> tuple[str, bool] | None:
    """Chi ha fatto l'operazione.

    Restituisce (nome da mostrare, è_insider) oppure None se l'operazione va ignorata.
    Il Form 4 compare tra i documenti sia del dichiarante sia della società emittente:
    un'operazione si attribuisce al miliardario solo se il dichiarante è davvero lui/il suo fondo.
    Gli insider di altre società si ignorano, tranne quelli di Trump Media.
    """
    cik = normalize_cik(cik)
    watched = by_cik().get(cik)
    if watched is None:
        return None
    if not watched.expected or watched.expected in str(owner or "").upper():
        return watched.label, False
    if cik == TRUMP_MEDIA_CIK:
        name = " ".join(w.capitalize() for w in str(owner or "insider").split())
        return f"{name} (insider di Trump Media)", True
    return None


def themes_for_security(name: str) -> list[str]:
    text = f" {str(name or '').lower()} "
    return [theme for theme, words in SECURITY_THEMES.items() if any(w in text for w in words)]


def expand_news_themes(domains: Iterable[str]) -> set[str]:
    out = set()
    for d in domains or []:
        out.add(d)
        out.update(NEWS_THEME_LINKS.get(d, ()))
    return out


def theme_text(themes: Iterable[str]) -> str:
    labels = [THEME_LABELS.get(t, t.lower()) for t in themes]
    return ", ".join(dict.fromkeys(labels)) or "non classificato"


# ----------------------------------------------------------------------------- selezione documenti SEC

def select_filings(events: list[Any], state: dict[str, Any], now: datetime | None = None) -> tuple[list[Any], list[Any]]:
    """Divide i documenti SEC in (da avvisare, da archiviare).

    * Al primo avvio per un soggetto il suo storico viene archiviato in silenzio:
      niente valanga di messaggi vecchi. Solo gli ultimi giorni vanno nel riepilogo.
    * Dopo il primo avvio si avvisa solo per documenti nuovi e recenti.
    """
    now = now or _now()
    seen = state.setdefault("analyst_seen_filings", {})
    seeded = state.setdefault("analyst_seeded_ciks", {})
    cutoff = now.date() - timedelta(days=MAX_FILING_AGE_DAYS)
    alert, archive = [], []
    first_time = {normalize_cik(e.cik) for e in events if normalize_cik(e.cik) not in seeded}
    for event in events:
        if event.event_id in seen:
            continue
        seen[event.event_id] = now.isoformat()
        filed = _parse_day(event.filed_at)
        recent = filed is not None and filed >= cutoff
        if not recent:
            continue
        (archive if normalize_cik(event.cik) in first_time else alert).append(event)
    for cik in first_time:
        seeded[cik] = now.isoformat()
    if len(seen) > 20000:
        state["analyst_seen_filings"] = dict(sorted(seen.items(), key=lambda kv: kv[1], reverse=True)[:20000])
    alert.sort(key=lambda e: e.filed_at, reverse=True)
    archive.sort(key=lambda e: e.filed_at, reverse=True)
    return alert, archive


def to_extract(alert: list[Any], archive: list[Any]) -> list[Any]:
    return (alert + archive)[:MAX_EXTRACT_PER_RUN]


# ----------------------------------------------------------------------------- memoria delle mosse

def remember_moves(state: dict[str, Any], records: list[Any], now: datetime | None = None) -> list[dict]:
    """Salva le operazioni (Form 4) e i riepiloghi 13F nella memoria dell'analista."""
    now = now or _now()
    moves = state.setdefault("analyst_moves", {})
    added = []
    by_event: dict[str, list[Any]] = {}
    for r in records:
        if r.source_kind == "13F_POSITION":
            by_event.setdefault(r.event_id, []).append(r)
            continue
        key = "|".join((r.event_id, r.security, r.shares, r.price, r.transaction_date, r.transaction_code))
        if key in moves:
            continue
        issuer_name = getattr(r, "issuer", "") or r.company
        attribution = attribute_trade(r.cik, r.reporting_owner, issuer_name)
        if attribution is None:
            continue
        who, insider = attribution
        shares, price = _num(r.shares), _num(r.price)
        move = {
            "kind": "TRADE", "cik": normalize_cik(r.cik), "who": who, "insider": insider,
            "owner": r.reporting_owner, "action": r.action, "security": short_security(r.security),
            "issuer": (getattr(r, "issuer", "") or r.company)
                      + (f" ({r.ticker})" if getattr(r, "ticker", "") else ""),
            "shares": shares, "price": price,
            "value": shares * price if shares and price else None,
            "date": r.transaction_date or r.filing_date, "filed": r.filing_date,
            "themes": themes_for_security(f"{r.security} {getattr(r, 'issuer', '') or r.company}"),
            "url": r.source_url, "seen_at": now.isoformat(),
        }
        moves[key] = move
        added.append(move)
    for event_id, rows in by_event.items():
        key = f"13F|{event_id}"
        if key in moves:
            continue
        positions = []
        for r in rows:
            value = _num(r.price)  # in 13F "price" contiene il valore dichiarato
            positions.append({"security": r.security, "value": value or 0.0,
                              "themes": themes_for_security(r.security)})
        positions.sort(key=lambda p: -p["value"])
        themes = sorted({t for p in positions[:20] for t in p["themes"]})
        move = {
            "kind": "13F", "cik": normalize_cik(rows[0].cik), "who": label_for(rows[0].cik, rows[0].company),
            "date": rows[0].filing_date, "filed": rows[0].filing_date, "count": len(positions),
            "top": positions[:5], "themes": themes, "url": rows[0].source_url, "seen_at": now.isoformat(),
        }
        moves[key] = move
        added.append(move)
    if len(moves) > 3000:
        state["analyst_moves"] = dict(sorted(moves.items(), key=lambda kv: kv[1].get("seen_at", ""), reverse=True)[:3000])
    return added


def recent_moves(state: dict[str, Any], days: int, now: datetime | None = None) -> list[dict]:
    now = now or _now()
    cutoff = now.date() - timedelta(days=days)
    out = [m for m in state.get("analyst_moves", {}).values()
           if (_parse_day(m.get("filed") or m.get("date")) or date.min) >= cutoff
           and (m.get("kind") != "TRADE" or "insider" in m
                or attribute_trade(m.get("cik", ""), m.get("owner", ""), m.get("issuer", "")))]
    return sorted(out, key=lambda m: m.get("filed") or "", reverse=True)


def recent_trump(state: dict[str, Any], hours: float, now: datetime | None = None) -> list[dict]:
    now = now or _now()
    out = []
    for item in (state.get("intelligence_history") or {}).values():
        if item.get("evidence") != "PUBLIC_RSS_ITEM":
            continue
        t = _parse_time(item.get("published")) or _parse_time(item.get("detected_at"))
        if t and now - t <= timedelta(hours=hours):
            out.append(item)
    return sorted(out, key=lambda i: _parse_time(i.get("published")) or now, reverse=True)


# ----------------------------------------------------------------------------- messaggi

FOOTER = "ℹ️ Analisi informativa da fonti pubbliche, non è un segnale operativo né una consulenza."


def _source_name(item: dict) -> str:
    url = str(item.get("feed_url") or item.get("url") or "").lower()
    if "trumpstruth" in url or "truthsocial" in url:
        return "Truth Social (Trump)"
    if "whitehouse.gov" in url:
        return "Casa Bianca"
    return str(item.get("source") or "fonte pubblica")


def trump_message(item: dict, state: dict[str, Any], now: datetime | None = None) -> str:
    now = now or _now()
    domains = item.get("domains") or []
    themes = expand_news_themes(domains)
    lines = [
        "🇺🇸 SPUTNIK — TRUMP",
        f"📰 {str(item.get('title') or 'Nuovo comunicato').strip()[:280]}",
        f"📡 {_source_name(item)} · 🕒 {item.get('published') or 'N/D'}",
        f"🧩 Temi: {theme_text(domains)}",
    ]
    try:
        from sputnik_catalyst import directional_news_candidates
        hyps = directional_news_candidates([item], limit=3)
    except Exception:
        hyps = []
    if hyps:
        lines.append("")
        lines.append("🎯 Possibili effetti sui mercati (ipotesi da verificare):")
        for h in hyps:
            lines.append(f"• {h['instrument']}: {h['bias']} — {h['reason']}")
    linked = [m for m in recent_moves(state, LINK_WINDOW_DAYS, now) if themes & set(m.get("themes") or [])]
    if linked:
        lines.append("")
        lines.append("💰 Miliardari già esposti a questi temi (ultimi 90 giorni):")
        for m in linked[:4]:
            lines.append("• " + _move_line(m))
    lines += ["", f"🔗 {item.get('url', '')}", FOOTER]
    return "\n".join(lines)


def _move_line(m: dict) -> str:
    if m["kind"] == "13F":
        top = ", ".join(p["security"] for p in m.get("top", [])[:3])
        return f"{m['who']}: portafoglio trimestrale ({m.get('count', 0)} titoli; primi: {top}) · {m.get('filed', '')}"
    value = f" · {_money(m['value'])}" if m.get("value") else ""
    verb = "ha comprato" if m.get("action") == "ACQUISTATO" else "ha venduto"
    return f"{m['who']} {verb} {short_security(m.get('security', ''))} ({m.get('issuer', '')}){value} · {m.get('date', '')}"


def move_message(m: dict, state: dict[str, Any], now: datetime | None = None) -> str:
    now = now or _now()
    if m["kind"] == "13F":
        lines = [
            f"📊 SPUTNIK — MILIARDARI · {m['who']}",
            f"Nuovo portafoglio trimestrale (13F) depositato il {m.get('filed', '')}: {m.get('count', 0)} titoli.",
            "Prime posizioni per valore:",
        ]
        for p in m.get("top", []):
            lines.append(f"• {p['security']} — {_money(p['value'])}")
        lines.append("Nota: il 13F mostra le posizioni a fine trimestre, con fino a 45 giorni di ritardo.")
    else:
        icon, verb = ("🟢", "HA COMPRATO") if m.get("action") == "ACQUISTATO" else ("🔴", "HA VENDUTO")
        lines = [f"💰 SPUTNIK — MILIARDARI · {m['who']}", f"{icon} {verb} {short_security(m.get('security', ''))} · {m.get('issuer', '')}"]
        detail = []
        if m.get("shares"):
            detail.append(f"{m['shares']:,.0f} azioni".replace(",", "."))
        if m.get("price"):
            detail.append(f"a {m['price']:,.2f} $")
        if m.get("value"):
            detail.append(f"≈ {_money(m['value'])}")
        if detail:
            lines.append(" · ".join(detail))
        lines.append(f"📅 Operazione {m.get('date', 'N/D')} · comunicata alla SEC il {m.get('filed', 'N/D')}")
        if m.get("owner") and m["owner"].upper() not in m["who"].upper():
            lines.append(f"👤 Dichiarante: {m['owner']}")
    themes = set(m.get("themes") or [])
    lines.append(f"🧩 Settore: {theme_text(themes)}")
    linked = [i for i in recent_trump(state, 24 * 30, now) if themes & expand_news_themes(i.get("domains") or [])]
    if linked:
        lines.append("")
        lines.append("🇺🇸 Collegamento con Trump (ultimi 30 giorni, stesso settore):")
        for i in linked[:3]:
            lines.append(f"• {str(i.get('title') or '')[:140]} · {i.get('published', '')}")
    lines += ["", f"🔗 {m.get('url', '')}", FOOTER]
    return "\n".join(lines)


def disclosure_message(event: Any) -> str:
    form = str(event.form).upper()
    if "13D" in form:
        what = "ha superato il 5% di una società con intenzioni attive (13D)"
    elif "13G" in form:
        what = "ha dichiarato una quota oltre il 5% (13G, investimento passivo)"
    elif form == "8-K":
        what = "ha depositato un comunicato rilevante (8-K)"
    else:
        what = f"ha depositato un documento {event.form}"
    return "\n".join([
        f"📄 SPUTNIK — MILIARDARI · {label_for(event.cik, event.company)}",
        f"{label_for(event.cik, event.company)} {what}.",
        f"📅 Depositato il {event.filed_at}",
        f"🔗 {event.source_url}",
        FOOTER,
    ])


def brief_message(state: dict[str, Any], now: datetime | None = None) -> str:
    now = now or _now()
    trump = recent_trump(state, 24, now)
    moves = recent_moves(state, 7, now)
    lines = ["☀️ SPUTNIK — RIEPILOGO TRUMP & MILIARDARI", ""]
    lines.append(f"🇺🇸 Trump nelle ultime 24 ore: {len(trump)} comunicati con impatto sui mercati")
    counts: dict[str, int] = {}
    for item in trump:
        for d in item.get("domains") or []:
            counts[d] = counts.get(d, 0) + 1
    if counts:
        top = sorted(counts.items(), key=lambda kv: -kv[1])[:4]
        lines.append("Temi più citati: " + ", ".join(f"{THEME_LABELS.get(k, k)} ({v})" for k, v in top))
    for item in trump[:3]:
        lines.append(f"• {str(item.get('title') or '')[:140]}")
    lines += ["", f"💰 Mosse dei miliardari negli ultimi 7 giorni: {len(moves)}"]
    for m in moves[:6]:
        lines.append("• " + _move_line(m))
    trump_themes = set().union(*(expand_news_themes(i.get("domains") or []) for i in trump)) if trump else set()
    overlap = [m for m in moves if trump_themes & set(m.get("themes") or [])]
    if overlap:
        lines += ["", "🔗 Sovrapposizioni (stesso settore di cui parla Trump):"]
        for m in overlap[:4]:
            lines.append(f"• {m['who']} → {theme_text(trump_themes & set(m.get('themes') or []))}")
    if not trump and not moves:
        lines.append("Nessuna novità rilevante.")
    lines += ["", FOOTER]
    return "\n".join(lines)


# ----------------------------------------------------------------------------- consegna

def deliver(state: dict[str, Any], trump_findings: list[dict], alert_events: list[Any], new_moves: list[dict],
            send: Callable[[str], bool], now: datetime | None = None) -> int:
    """Invia gli avvisi di questo giro. Restituisce il numero di messaggi consegnati."""
    now = now or _now()
    outbox: list[str] = list(state.get("analyst_outbox") or [])
    if not state.get("analyst_started_at"):
        # Primo avvio: niente arretrati, solo un messaggio di attivazione.
        state["analyst_started_at"] = now.isoformat()
        names = ", ".join(w.label.split(" · ")[0] for w in watchlist())
        outbox.append("\n".join([
            "🛰️ SPUTNIK ANALISTA ATTIVO",
            "Seguo Trump (Truth Social e Casa Bianca) e le operazioni pubbliche SEC di: " + names + ".",
            "Ti scrivo quando Trump pubblica qualcosa che può muovere i mercati, quando un miliardario compra o vende, "
            "e ogni mattina con un riepilogo.",
            FOOTER,
        ]))
    else:
        messages: list[str] = []
        urgent: list[str] = []   # allarmi ⚡: in testa e mai tagliati dal limite di messaggi
        for item in trump_findings:
            if item.get("evidence") != "PUBLIC_RSS_ITEM":
                continue
            t = _parse_time(item.get("published"))
            if t is None or now - t > timedelta(hours=TRUMP_MAX_AGE_HOURS):
                continue
            call = sputnik_market_call.message(item)
            if call:
                urgent.append(call)
            messages.append(trump_message(item, state, now))
        trade_events = {m.get("url") for m in new_moves}
        for m in new_moves:
            if m["kind"] == "TRADE" and m.get("filed") and (_parse_day(m["filed"]) or date.min) < now.date() - timedelta(days=MAX_FILING_AGE_DAYS):
                continue
            messages.append(move_message(m, state, now))
        for event in alert_events:
            if str(event.form).startswith(("SC 13", "SCHEDULE 13", "8-K")) and event.source_url not in trade_events:
                messages.append(disclosure_message(event))
        counts = state.setdefault("analyst_counts", {})
        for text in messages:
            kind = ("Trump" if text.startswith("🇺🇸") else "operazioni miliardari" if text.startswith("💰")
                    else "portafogli 13F" if text.startswith("📊") else "quote/comunicati" if text.startswith("📄") else "altro")
            counts[kind] = counts.get(kind, 0) + 1
        if len(messages) > MAX_ALERTS_PER_RUN:
            extra = len(messages) - (MAX_ALERTS_PER_RUN - 1)
            messages = messages[:MAX_ALERTS_PER_RUN - 1] + [
                f"🛰️ SPUTNIK — altre {extra} novità in questo giro: le trovi nel riepilogo di domani mattina."]
        counts["chiamate al mercato"] = counts.get("chiamate al mercato", 0) + len(urgent)
        outbox = urgent + outbox + messages

    brief_hour = int(os.getenv("SPUTNIK_BRIEF_HOUR_ROME", "7"))
    try:
        from zoneinfo import ZoneInfo
        local = now.astimezone(ZoneInfo("Europe/Rome"))
    except Exception:
        local = now
    if local.hour >= brief_hour and state.get("analyst_brief_date") != local.date().isoformat() \
            and state.get("analyst_started_at") and _parse_time(state["analyst_started_at"]) < now - timedelta(hours=1):
        outbox.append(brief_message(state, now))
        state["analyst_brief_date"] = local.date().isoformat()

    if state.get("analyst_started_at") and report_due(state, now):
        outbox.append(report_message(state, now))

    delivered, pending = 0, []
    for text in outbox:
        if send(text):
            delivered += 1
        else:
            pending.append(text)
    state["analyst_outbox"] = pending[-20:]
    return delivered


# ----------------------------------------------------------------------------- contesto per il bot CFD

CONTEXT_FILE = os.getenv("SPUTNIK_CONTEXT_FILE", "sputnik_context.json")
CONTEXT_MONEY_DAYS = 45   # i 13F arrivano fino a 45 giorni dopo il trimestre


def export_context(state: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    """Riassunto pubblico per il bot CFD di Gagarin: notizie Trump (24h) con direzioni e mosse dei miliardari."""
    now = now or _now()
    try:
        from sputnik_catalyst import directional_news_candidates
    except Exception:
        directional_news_candidates = None
    trump = []
    for item in recent_trump(state, 24, now)[:15]:
        published = _parse_time(item.get("published")) or _parse_time(item.get("detected_at"))
        normalized = {**item, "published": published.isoformat() if published else ""}
        hyps = []
        if directional_news_candidates:
            try:
                hyps = directional_news_candidates([normalized], limit=6)
            except Exception:
                hyps = []
        trump.append({
            "title": str(item.get("title") or "")[:200],
            "published": normalized["published"],
            "url": item.get("url", ""),
            "source": _source_name(item),
            "domains": list(item.get("domains") or []),
            "bias": [{"instrument": h["instrument"], "bias": h["bias"], "reason": h["reason"]} for h in hyps],
        })
    money = []
    for m in recent_moves(state, CONTEXT_MONEY_DAYS, now)[:40]:
        row = {"kind": m["kind"], "who": m["who"], "filed": m.get("filed", ""), "themes": m.get("themes", [])}
        if m["kind"] == "TRADE":
            row.update({"action": m.get("action"), "security": short_security(m.get("security", "")),
                        "issuer": m.get("issuer", ""), "value": m.get("value")})
        else:
            row["top"] = [p["security"] for p in m.get("top", [])[:5]]
        money.append(row)
    return {"version": 1, "trump": trump, "money": money}


def write_context(state: dict[str, Any], path: str = CONTEXT_FILE, now: datetime | None = None) -> bool:
    """Scrive il file solo se il contenuto è cambiato (evita commit inutili ogni 15 minuti)."""
    import json
    from pathlib import Path
    now = now or _now()
    data = export_context(state, now)
    target = Path(path)
    try:
        current = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        current = {}
    comparable = dict(current)
    comparable.pop("updated_at", None)
    if comparable == data:
        return False
    data["updated_at"] = now.isoformat()
    target.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return True


# ----------------------------------------------------------------------------- pagellino (verifica dal vivo)

PRICE_SYMBOLS = {"GOLD": "GC=F", "WTI": "CL=F", "BRENT": "BZ=F", "NASDAQ100": "NQ=F", "USD": "DX-Y.NYB"}
INSTRUMENT_NAMES = {"GOLD": "Oro", "WTI": "Petrolio WTI", "BRENT": "Brent", "NASDAQ100": "Nasdaq 100", "USD": "Dollaro"}
CHECK_AFTER = timedelta(hours=24)
REPORT_WEEKDAY, REPORT_HOUR = 5, 9   # sabato alle 9 (Roma)


def _default_price(symbol: str) -> float | None:
    try:
        from sputnik_demo.data import fetch
        return fetch(symbol, range_="5d", interval="1h").last_price
    except Exception:  # noqa: BLE001
        return None


def track_predictions(state: dict[str, Any], now: datetime | None = None,
                      price: Callable[[str], float | None] = _default_price) -> int:
    """Registra le ipotesi nate dalle notizie di Trump e le verifica dopo 24 ore.

    Il prezzo di partenza è quello del momento in cui Sputnik vede la notizia: misura
    cosa sarebbe successo seguendo l'avviso, non il movimento già avvenuto prima.
    """
    now = now or _now()
    preds = state.setdefault("analyst_predictions", {})
    cache: dict[str, float | None] = {}

    def px(instrument: str) -> float | None:
        symbol = PRICE_SYMBOLS.get(instrument)
        if not symbol:
            return None
        if symbol not in cache:
            cache[symbol] = price(symbol)
        return cache[symbol]

    for item in export_context(state, now)["trump"]:
        for b in item.get("bias") or []:
            inst = str(b.get("instrument", "")).upper()
            key = f"{item.get('url')}|{inst}"
            if key in preds or inst not in PRICE_SYMBOLS:
                continue
            entry = px(inst)
            if entry:
                preds[key] = {"instrument": inst, "bias": b.get("bias", ""), "title": item.get("title", "")[:140],
                              "first_seen": now.isoformat(), "entry": entry}
    checked = 0
    for p in preds.values():
        if "move" in p or now - datetime.fromisoformat(p["first_seen"]) < CHECK_AFTER:
            continue
        last = px(p["instrument"])
        if not last:
            continue
        move = last / p["entry"] - 1
        sign = 1 if "LONG" in str(p["bias"]).upper() else -1
        p.update({"exit": last, "move": round(move, 5), "correct": move * sign > 0, "checked_at": now.isoformat()})
        checked += 1
    if len(preds) > 1000:
        state["analyst_predictions"] = dict(sorted(preds.items(), key=lambda kv: kv[1]["first_seen"])[-1000:])
    return checked


def _demo_section() -> list[str]:
    import json
    from pathlib import Path
    path = Path(os.getenv("SPUTNIK_DEMO_STATE_FILE", "sputnik_demo_state.json"))
    try:
        demo = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ["🤖 Trader demo: nessuna operazione ancora registrata"]
    closed = demo.get("closed") or []
    total = sum(c.get("pnl_eur", 0) for c in closed)
    wins = sum(1 for c in closed if c.get("pnl_eur", 0) > 0)
    lines = [f"🤖 Trader demo: {len(closed)} operazioni chiuse · vincenti {wins} · risultato {total:+.2f} € "
             f"· posizioni aperte {len(demo.get('positions') or {})}"]
    if demo.get("halted"):
        lines.append("   ⚠️ nuovi acquisti sospesi (conto sotto l'85%)")
    return lines


def report_message(state: dict[str, Any], now: datetime | None = None) -> str:
    now = now or _now()
    preds = [p for p in (state.get("analyst_predictions") or {}).values() if "move" in p]
    week = [p for p in preds if now - datetime.fromisoformat(p["checked_at"]) <= timedelta(days=7)]

    def line(rows: list[dict]) -> str:
        if not rows:
            return "nessuna ipotesi verificata"
        ok = sum(1 for p in rows if p["correct"])
        avg = sum((1 if "LONG" in str(p["bias"]).upper() else -1) * p["move"] for p in rows) / len(rows)
        return f"{ok}/{len(rows)} giuste ({ok / len(rows):.0%}) · movimento medio nella direzione indicata {avg:+.2%}"

    counts = state.get("analyst_counts") or {}
    lines = ["📊 PAGELLINO SPUTNIK — risultati dal vivo", "",
             "🇺🇸 Ipotesi dalle notizie di Trump, verificate dopo 24 ore:",
             f"• Ultimi 7 giorni: {line(week)}",
             f"• Da quando è attivo: {line(preds)}"]
    by_inst: dict[str, list[dict]] = {}
    for p in preds:
        by_inst.setdefault(p["instrument"], []).append(p)
    for inst, rows in sorted(by_inst.items()):
        lines.append(f"   {INSTRUMENT_NAMES.get(inst, inst)}: {line(rows)}")
    lines += ["", "📨 Avvisi inviati finora: " + (", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "nessuno"), ""]
    lines += _demo_section()
    lines += ["", "Una moneta lanciata indovinerebbe ~50%: servono almeno 30 ipotesi verificate per un giudizio.",
              FOOTER]
    return "\n".join(lines)


def report_due(state: dict[str, Any], now: datetime) -> bool:
    from zoneinfo import ZoneInfo
    local = now.astimezone(ZoneInfo("Europe/Rome"))
    week_id = f"{local.isocalendar().year}-W{local.isocalendar().week:02d}"
    if local.weekday() == REPORT_WEEKDAY and local.hour >= REPORT_HOUR and state.get("analyst_report_week") != week_id:
        state["analyst_report_week"] = week_id
        return True
    return False
