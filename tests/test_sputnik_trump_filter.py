from datetime import datetime, timezone

import sputnik_analyst as sa


def item(title, text="", domains=("MEDIA",)):
    return {"title": title, "text": text, "domains": list(domains), "evidence": "PUBLIC_RSS_ITEM",
            "published": "2026-11-23T11:31:33+00:00", "source": "PUBLIC_RSS", "url": title}


def test_empty_and_non_market_posts_are_dropped():
    for title in ("Quote post from November 23, 2026", "Repost", "Video",
                  "It's incredible that Somalians have been able to take over Minnesota. They own it, “lock, stock, and barrel”. They said it again",
                  "Congratulations to the Golden Knights on a great season!"):
        assert not sa.market_relevant(item(title)), title


def test_market_posts_are_kept():
    for title in ("Isn't it interesting that Oil prices have dropped precipitously after the Midterm Elections?",
                  "The Market is down more than 6 Trillion Dollars since November 3rd. NASDAQ is down 20%.",
                  "We will impose Tariffs of 25% on all imports from Canada",
                  "The Fed must cut Interest Rates NOW!",
                  "Bitcoin is going to the moon"):
        assert sa.market_relevant(item(title)), title
    assert sa.market_relevant(item("BE COOL!", domains=("MARKET_CALL",)))


def test_deliver_sends_only_market_posts():
    now = datetime(2026, 11, 23, 11, 40, tzinfo=timezone.utc)
    state = {"analyst_started_at": "2026-01-01T00:00:00+00:00"}
    sent = []
    sa.deliver(state, [item("Quote post from November 23, 2026"),
                       item("Oil prices have dropped after the elections", domains=("ENERGY",))],
               [], [], lambda t: sent.append(t) or True, now=now)
    trump = [t for t in sent if t.startswith("🇺🇸")]
    assert len(trump) == 1 and "Oil prices" in trump[0]
