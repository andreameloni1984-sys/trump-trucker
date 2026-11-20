"""Offline PRAVDA analytics for the INVEST journals (standard library only)."""

import argparse
from collections import Counter, defaultdict
from contextlib import closing
import csv
from datetime import date, datetime, time, timedelta, timezone
import hashlib
import json
from math import isfinite, sqrt
from pathlib import Path
import sqlite3
from statistics import mean, NormalDist
from tempfile import NamedTemporaryFile
from urllib.parse import urlsplit

UTC = timezone.utc
MINUTE = timedelta(minutes=1)
HORIZONS = (5, 15, 30, 60)
LEVELS = ("entry", "stop", "tp1", "tp2", "tp3")
BOTS = ("Gagarin", "Sputnik")
MISSING = "DATA_UNAVAILABLE"
MIN_SAMPLE = 30


def stamp(value):
    try:
        result = datetime.fromisoformat(value)
        return result.astimezone(UTC) if result.tzinfo else None
    except (ValueError, TypeError):
        return None


def price(value):
    return value if type(value) in (int, float) and isfinite(value) and value > 0 else None


def source_url(value):
    try:
        parsed = urlsplit(value or "")
        return value if parsed.scheme in {"https", "http"} and parsed.hostname else None
    except ValueError:
        return None


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def read_gagarin(path):
    # A local SQLite backup keeps WAL pages and avoids locks on the worker database.
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        rows = db.execute("""SELECT id,event,latest,first_signal,entry_signal,observations,outcome
                             FROM candidates WHERE latest IS NOT NULL""")
        for key, *payloads in rows:
            event, latest, first, entry, observations, outcome = [
                json.loads(raw) if raw else {} for raw in payloads
            ]
            seen = set()
            for signal in (first, entry, latest if latest.get("state") == "SCARTARE" else {}):
                state = signal.get("state")
                if not state or state in seen:
                    continue
                seen.add(state)
                yield ("Gagarin", [key, state], event, signal,
                       observations if signal == first else {}, outcome if signal == entry else {})


def read_sputnik(path):
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    events = data.get("invest_events", {})
    for signal in data["pravda"]:
        event = events.get(signal["url"], {})
        yield ("Sputnik", [signal["url"], signal["ticker"], signal["direction"], signal["stage"]],
               event, signal, signal.get("prices", {}), {})


def normalize(bot, identity, event, signal, observations, outcome):
    gagarin = bot == "Gagarin"
    direction = event.get("direction") if gagarin else signal.get("direction")
    started = stamp(signal.get("signaled_at") if gagarin else signal.get("signalled"))
    if not started or direction not in {"LONG", "SHORT"}:
        return None
    side = 1 if direction == "LONG" else -1
    published = stamp((event if gagarin else signal).get("published"))
    quote_at = stamp(signal.get("quote_at") if gagarin else signal.get("price_timestamp"))
    reference = price(signal.get("price"))
    baseline_ok = reference is not None and quote_at is not None and quote_at <= started
    chronology_ok = published is not None and published <= started
    observations_out = {}
    for minutes in HORIZONS:
        target = started + minutes * MINUTE
        value = observations.get(str(minutes))
        if gagarin:
            observed_at = stamp(value.get("at")) if value else None
            observed_price = price(value.get("price")) if value else None
            time_ok = observed_at is not None and target <= observed_at <= target + MINUTE
        else:
            observed_at = target.replace(second=0, microsecond=0)
            observed_price = price(value)
            time_ok = observed_at - MINUTE >= started
        valid = baseline_ok and chronology_ok and time_ok and observed_price is not None
        change = 100 * (observed_price - reference) / reference if valid else None
        observations_out[str(minutes)] = dict(
            status="AVAILABLE" if valid else MISSING,
            observed_at=observed_at.isoformat() if observed_price is not None and observed_at else None,
            observed_price=observed_price,
            change_pct=change, theoretical_pct=side * change if valid else None,
            correct=side * change > 0 if valid else None,
        )

    raw_levels = signal.get("levels") or {}
    if isinstance(raw_levels, list):
        raw_levels = dict(zip(LEVELS, raw_levels))
    levels = {name: price(raw_levels.get(name)) for name in LEVELS}
    entry, stop = levels["entry"], levels["stop"]
    exit_at = stamp(outcome.get("at"))
    exit_price = price(outcome.get("exit"))
    reason = outcome.get("reason")
    simulation = None
    if (gagarin and chronology_ok and side == 1 and signal.get("state") == "ENTRARE"
            and entry and stop and stop < entry and exit_price and exit_at
            and started < exit_at <= started + 61 * MINUTE and reason in {"STOP", "TP1", "TIME"}):
        simulation = dict(exit_at=exit_at.isoformat(), reason=reason, exit_price=exit_price,
                          gross_pct=100 * (exit_price - entry) / entry,
                          gross_r=(exit_price - entry) / (entry - stop),
                          policy="GAGARIN_OHLC_STOP_FIRST")
    paper_outcome = signal.get("outcome") if not gagarin else reason
    hits = dict.fromkeys(("stop", "tp1", "tp2", "tp3"))
    if simulation:
        hits.update(stop=reason == "STOP", tp1=reason == "TP1")
    # Sputnik stores a cumulative OHLC outcome and no per-level timestamp.
    # Completed rows become eligible only after the full observation window.
    finalized = not gagarin and signal.get("complete") is True
    if finalized and chronology_ok and levels["entry"] and side == 1:
        if paper_outcome in {"stop", "stop dopo tp1"}:
            hits["stop"] = True
        if paper_outcome in {"tp1", "tp2", "stop dopo tp1"}:
            hits["tp1"] = True
        if paper_outcome == "tp2":
            hits["tp2"] = True
    excursions = {}
    for field in ("mfe", "mae"):
        raw = signal.get(field)
        excursions[field + "_observed_pct"] = (
            raw * 100 / reference if finalized and baseline_ok and chronology_ok
            and type(raw) in (int, float) and isfinite(raw) and raw >= 0 else None
        )
    news = event if gagarin else signal
    url = source_url(news.get("url"))
    score = signal.get("heuristic_score") if gagarin else signal.get("score")
    score = score if type(score) in (int, float) and isfinite(score) else None
    confidence = signal.get("confidence")
    state = signal.get("state") if gagarin else signal.get("stage")
    return dict(
        id=digest([bot, identity]), bot=bot, ticker=event.get("symbol") if gagarin else signal.get("ticker"),
        instrument=signal.get("name") or event.get("symbol") or signal.get("ticker"),
        signaled_at=started.isoformat(), direction=direction, state=state,
        title=news.get("title"), source=event.get("source") or signal.get("source"),
        source_url=url, published_at=published.isoformat() if published else None,
        technical=signal.get("technical"),
        category=news.get("category"), strategy=raw_levels.get("setup") or signal.get("phase"),
        confidence=confidence, initial_score=score, reference_price=reference,
        reference_at=quote_at.isoformat() if quote_at else None,
        data_quality=dict(reference="AVAILABLE" if baseline_ok else MISSING,
                          news="AVAILABLE" if url and chronology_ok else MISSING,
                          net_execution=MISSING,
                          excursion="OBSERVED_BARS_ONLY" if excursions["mfe_observed_pct"] is not None else MISSING),
        levels=levels, observations=observations_out, level_hits=hits, simulation=simulation,
        outcome=paper_outcome, source_error=signal.get("error"),
        finalized_at=(started + 60 * MINUTE).isoformat() if finalized else None,
        net_pct=None, profitable=None, **excursions,
    )


def ingest(db, sources):
    db.execute("""CREATE TABLE IF NOT EXISTS signals
                  (id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, at TEXT NOT NULL, payload TEXT NOT NULL)""")
    changed = 0
    for source in sources:
        for raw in source:
            bot, identity, *_ = raw
            key, fingerprint = digest([bot, identity]), digest(raw)
            previous = db.execute("SELECT fingerprint,payload FROM signals WHERE id=?", (key,)).fetchone()
            if previous and previous[0] == fingerprint:
                continue
            row = normalize(*raw)
            if row is None:
                continue
            if previous and row["source"] is None:
                row["source"] = json.loads(previous[1])["source"]
            db.execute("""INSERT INTO signals VALUES (?,?,?,?)
                          ON CONFLICT(id) DO UPDATE SET fingerprint=excluded.fingerprint,
                          at=excluded.at, payload=excluded.payload""",
                       (key, fingerprint, row["signaled_at"], json.dumps(row, ensure_ascii=False)))
            changed += 1
    return changed


def as_of(row, cutoff):
    """Mask labels that could not yet have been observed at the cutoff."""
    row = dict(row)
    started = stamp(row["signaled_at"])
    observations = {}
    for minutes, item in row["observations"].items():
        at = stamp(item["observed_at"])
        if started + int(minutes) * MINUTE > cutoff or (at and at > cutoff):
            item = dict.fromkeys(item)
            item["status"] = MISSING
        observations[minutes] = item
    row["observations"] = observations
    simulation = row["simulation"]
    if simulation and stamp(simulation["exit_at"]) > cutoff:
        row["simulation"] = row["outcome"] = None
        row["level_hits"] = dict.fromkeys(row["level_hits"])
    finalized = stamp(row["finalized_at"])
    if row["bot"] == "Sputnik" and (not finalized or finalized > cutoff):
        row.update(finalized_at=None, outcome=None, source_error=None,
                   mfe_observed_pct=None, mae_observed_pct=None,
                   level_hits=dict.fromkeys(row["level_hits"]),
                   data_quality={**row["data_quality"], "excursion": MISSING})
    return row


def average(values):
    valid = [value for value in values if value is not None]
    return dict(n=len(valid), mean=mean(valid) if valid else None)


def wilson(wins, n, z=1.959963984540054):
    if not n:
        return None
    p = wins / n
    center = p + z * z / (2 * n)
    half = z * sqrt((p * (1 - p) + z * z / (4 * n)) / n)
    denominator = 1 + z * z / n
    return [max(0, (center - half) / denominator), min(1, (center + half) / denominator)]


def summarize(rows):
    horizons = {}
    for minutes in HORIZONS:
        samples = [row["observations"][str(minutes)] for row in rows]
        valid = [item for item in samples if item["correct"] is not None]
        wins = sum(item["correct"] for item in valid)
        horizons[str(minutes)] = dict(
            n=len(valid), correct=wins, accuracy=wins / len(valid) if valid else None,
            ci95=wilson(wins, len(valid)), flat=sum(item["change_pct"] == 0 for item in valid),
            theoretical_pct=average(item["theoretical_pct"] for item in valid),
        )
    simulations = [row["simulation"] for row in rows if row["simulation"]]
    hits = {}
    for level in ("stop", "tp1", "tp2", "tp3"):
        known = [row["level_hits"][level] for row in rows if row["level_hits"][level] is not None]
        hits[level] = dict(known_hits=sum(known), known_non_hits=len(known) - sum(known),
                           unknown=len(rows) - len(known),
                           frequency=None)
        # Only the Gagarin exit model supplies positive and negative labels
        # under a common observation policy. Sputnik contributes confirmed hits.
        model_labels = [r["level_hits"][level] for r in rows
                        if r["simulation"] and r["level_hits"][level] is not None]
        hits[level].update(model_n=len(model_labels),
                           frequency=mean(model_labels) if model_labels else None)
    return dict(signals=len(rows), horizons=horizons, modeled_gross_pct=average(s["gross_pct"] for s in simulations),
                modeled_gross_r=average(s["gross_r"] for s in simulations),
                net_profitability=average(row["profitable"] for row in rows), level_hits=hits,
                mfe_observed_pct=average(r["mfe_observed_pct"] for r in rows),
                mae_observed_pct=average(r["mae_observed_pct"] for r in rows))


def attributes(row):
    at = stamp(row["signaled_at"])
    score = row["initial_score"]
    # Raw heuristics use different scales and must not be pooled.
    score_bucket = None
    if score is not None:
        step = 10 if row["bot"] == "Sputnik" else 1
        lower = int(score // step) * step
        score_bucket = f"{row['bot']} [{lower},{lower + step})"
    relative_volume = (row.get("technical") or {}).get("relative_volume")
    volume_group = None if relative_volume is None else (">=1.5x" if relative_volume >= 1.5 else "<1.5x")
    return dict(relative_volume=volume_group, bot=row["bot"], ticker=row["ticker"], category=row["category"],
                hour_utc=f"{at.hour:02d}:00", weekday_utc=str(at.isoweekday()),
                direction=row["direction"], state=row["state"], strategy=row["strategy"],
                confidence=row["confidence"], score=score_bucket)


def group(rows):
    groups = defaultdict(lambda: defaultdict(list))
    for row in rows:
        for dimension, label in attributes(row).items():
            groups[dimension][str(label) if label is not None else MISSING].append(row)
    return groups


def recommendations(rows, cutoff):
    split = cutoff - timedelta(days=30)
    start = split - timedelta(days=90)
    # Exclude signals whose longest label could straddle the split.
    discovery = [as_of(r, split) for r in rows
                 if start <= stamp(r["signaled_at"]) <= split - 61 * MINUTE]
    later = [r for r in rows if split <= stamp(r["signaled_at"]) <= cutoff - 61 * MINUTE]
    # Use a single comparable stage per event whenever present.
    discovery = [r for r in discovery if r["state"] == "PREPARARE"]
    later = [r for r in later if r["state"] == "PREPARARE"]
    proposals = []
    for bot in BOTS:
        discovery_bot = [r for r in discovery if r["bot"] == bot]
        later_bot = [r for r in later if r["bot"] == bot]
        training_groups = group(discovery_bot)
        testing_groups = group(later_bot)
        for dimension in ("category", "ticker", "direction", "confidence", "score"):
            for label, selection in training_groups.get(dimension, {}).items():
                if label == MISSING:
                    continue
                rest = [r for r in discovery_bot if str(attributes(r)[dimension]) != label]
                selected = summarize(selection)["horizons"]["60"]
                baseline = summarize(rest)["horizons"]["60"]
                if min(selected["n"], baseline["n"]) < MIN_SAMPLE:
                    continue
                testing = testing_groups.get(dimension, {}).get(label, [])
                testing_rest = [r for r in later_bot if str(attributes(r)[dimension]) != label]
                proposals.append((bot, dimension, label, selected, baseline,
                                  summarize(testing)["horizons"]["60"],
                                  summarize(testing_rest)["horizons"]["60"]))
        # Compare horizons on the same signals to avoid varying coverage.
        for minute in (5, 15, 30):
            key = str(minute)
            train_pairs = [r for r in discovery_bot if all(r["observations"][h]["correct"] is not None
                                                       for h in (key, "60"))]
            test_pairs = [r for r in later_bot if all(r["observations"][h]["correct"] is not None
                                                   for h in (key, "60"))]
            if len(train_pairs) >= MIN_SAMPLE:
                a, b = summarize(train_pairs)["horizons"], summarize(test_pairs)["horizons"]
                proposals.append((bot, "horizon_vs_60m", key, a[key], a["60"], b[key], b["60"]))
    # Conservative simultaneous intervals over the proposed contrasts and both cohorts.
    z = NormalDist().inv_cdf(1 - .05 / (8 * max(1, len(proposals))))
    validated = []
    for bot, dimension, label, train, train_ref, test, test_ref in proposals:
        if min(test["n"], test_ref["n"]) < MIN_SAMPLE:
            continue
        a, b, c, d = [wilson(x["correct"], x["n"], z) for x in (train, train_ref, test, test_ref)]
        relation = "higher" if a[0] > b[1] and c[0] > d[1] else (
            "lower" if a[1] < b[0] and c[1] < d[0] else None
        )
        if relation:
            validated.append(dict(bot=bot, dimension=dimension, value=label, relation=relation,
                                  discovery=train, discovery_reference=train_ref,
                                  validation=test, validation_reference=test_ref))
    return dict(discovery_start=start.isoformat(), validation_start=split.isoformat(),
                minimum_n_per_group=MIN_SAMPLE, tested=len(proposals), validated=validated)


def report(rows, day, cutoff):
    daily = [r for r in rows if stamp(r["signaled_at"]).date() == day]
    groups = group(daily)
    breakdown = {dimension: {label: summarize(rows) for label, rows in sorted(buckets.items())}
                 for dimension, buckets in groups.items()}
    bots = {bot: summarize(groups["bot"].get(bot, [])) for bot in BOTS}
    comparison = {}
    for horizon in map(str, HORIZONS):
        a, b = (bots[bot]["horizons"][horizon] for bot in BOTS)
        comparison[horizon] = dict(
            gagarin_n=a["n"], sputnik_n=b["n"],
            difference_pp=100 * (a["accuracy"] - b["accuracy"])
            if min(a["n"], b["n"]) else None,
        )
    total = summarize(daily)
    categories = {label: item["horizons"]["60"] for label, item in breakdown.get("category", {}).items()
                  if label != MISSING and item["horizons"]["60"]["n"] >= MIN_SAMPLE}
    ranked = sorted(categories, key=lambda label: categories[label]["accuracy"])
    errors = Counter(r["source_error"] for r in daily if r["source_error"])
    errors["Dati a 60 minuti indisponibili"] = len(daily) - total["horizons"]["60"]["n"]
    errors["Direzione errata o invariata a 60 minuti"] = (
        total["horizons"]["60"]["n"] - total["horizons"]["60"]["correct"]
    )
    return daily, dict(date=day.isoformat(), as_of=cutoff.isoformat(), mode="PAPER ONLY", total=total,
                       bots=bots, breakdown=breakdown, comparison=comparison,
                       best_category=(ranked[-1] if len(ranked) >= 2 else None),
                       worst_category=(ranked[0] if len(ranked) >= 2 else None),
                       errors=dict(errors.most_common(5)),
                       recommendations=recommendations(rows, cutoff))


def render(result):
    def accuracy(metric):
        n, rate = metric["n"], metric["accuracy"]
        if not n:
            return "DATA_UNAVAILABLE (n=0, campione insufficiente)"
        suffix = ", campione insufficiente" if n < MIN_SAMPLE else ""
        return f"{rate:.1%} (n={n}{suffix})"

    text = ["# PRAVDA — ANALISI RISULTATI", "", f"{result['date']} UTC · PAPER ONLY", "",
            f"- Segnali analizzati: {result['total']['signals']}"]
    for bot, summary in result["bots"].items():
        text.append(f"- {bot}: {summary['signals']} segnali, direzione a 60 min "
                    f"{accuracy(summary['horizons']['60'])}")
    for title, field in (("Migliore", "best_category"), ("Peggiore", "worst_category")):
        label = result[field]
        metric = result["breakdown"].get("category", {}).get(label, {}).get("horizons", {}).get("60")
        value = f"{label}, {accuracy(metric)}" if metric else "campione insufficiente per la classifica"
        text.append(f"- {title} categoria di catalizzatore: {value}")
    for horizon, summary in result["total"]["horizons"].items():
        text.append(f"- {horizon} min: {accuracy(summary)}")
    errors = [f"{label} ({count})" for label, count in result["errors"].items() if count]
    text.append("- Principali errori: " + (", ".join(errors) if errors else "nessun errore documentato"))
    net = result["total"]["net_profitability"]
    text.append(f"- Redditività netta: DATA_UNAVAILABLE (n={net['n']})")
    validated = result["recommendations"]["validated"]
    if not validated:
        text.append("- Miglioramenti suggeriti: nessuna proposta confermata sul campione successivo.")
    for item in validated:
        relation = "superiore" if item["relation"] == "higher" else "inferiore"
        text.append(f"- Miglioramento da valutare · {item['bot']}, {item['dimension']} "
                    f"{item['value']}: accuratezza {relation} nel campione successivo, "
                    f"{accuracy(item['validation'])} contro {accuracy(item['validation_reference'])}.")
    return "\n".join(text) + "\n"


def export(directory, rows, result):
    directory.mkdir(parents=True, exist_ok=True)
    fields = ["id", "bot", "ticker", "instrument", "signaled_at", "direction", "state",
              "category", "strategy", "confidence", "initial_score", "title", "source", "source_url",
              "published_at", "technical", "reference_price", "reference_at", "levels", "observations", "data_quality",
              "level_hits", "simulation", "outcome", "source_error", "finalized_at", "net_pct", "profitable",
              "mfe_observed_pct", "mae_observed_pct"]
    horizon_fields = [f"{field}_{minutes}m" for minutes in HORIZONS for field in
                      ("status", "observed_at", "observed_price", "change_pct", "theoretical_pct", "correct")]
    for filename in ("report.md", "report.json", "signals.csv"):
        with NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=directory, delete=False) as file:
            temp = Path(file.name)
            try:
                if filename == "report.md":
                    file.write(render(result))
                elif filename == "report.json":
                    json.dump({"report": result, "signals": rows}, file, indent=2, ensure_ascii=False)
                else:
                    writer = csv.DictWriter(file, fieldnames=fields + horizon_fields)
                    writer.writeheader()
                    for row in rows:
                        flat = {key: csv_value(value) for key, value in row.items()}
                        flat.update({f"{field}_{minutes}m": value
                                     for minutes, observation in row["observations"].items()
                                     for field, value in observation.items()})
                        writer.writerow(flat)
                file.flush()
                temp.replace(directory / filename)
            finally:
                temp.unlink(missing_ok=True)


def csv_value(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gagarin", type=Path, help="Snapshot SQLite del journal INVEST v3")
    parser.add_argument("--sputnik", type=Path, help="Snapshot JSON dello stato INVEST v2")
    parser.add_argument("--ledger", type=Path, required=True, help="Database SQLite analytics persistente")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--day", type=date.fromisoformat, help="Giorno UTC, ieri per impostazione predefinita")
    args = parser.parse_args()
    now = datetime.now(UTC)
    day = args.day or now.date() - timedelta(days=1)
    if day >= now.date():
        parser.error("--day deve essere un giorno UTC concluso")
    cutoff = datetime.combine(day + timedelta(days=1), time.min, UTC)
    inputs = [path.resolve() for path in (args.gagarin, args.sputnik) if path]
    targets = [args.ledger.resolve(), *(args.out / name for name in ("report.md", "report.json", "signals.csv"))]
    if any(path.resolve() in inputs for path in targets) or len(set(p.resolve() for p in targets)) != len(targets):
        parser.error("I percorsi di input, database analytics e report devono essere distinti")
    if not inputs and not args.ledger.is_file():
        parser.error("Fornire almeno uno snapshot per inizializzare il database")
    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    sources = []
    if args.gagarin:
        sources.append(read_gagarin(args.gagarin))
    if args.sputnik:
        sources.append(read_sputnik(args.sputnik))
    with sqlite3.connect(args.ledger) as db:
        db.execute("BEGIN IMMEDIATE")
        changed = ingest(db, sources)
        rows = [as_of(json.loads(raw), cutoff) for (raw,) in db.execute(
            "SELECT payload FROM signals WHERE at >= ? AND at < ? ORDER BY at,id",
            ((cutoff - timedelta(days=120)).isoformat(), cutoff.isoformat()),
        )]
    daily, result = report(rows, day, cutoff)
    export(args.out, daily, result)
    print(f"PRAVDA: {changed} record nuovi o aggiornati. Report in {args.out}")


if __name__ == "__main__":
    main()
