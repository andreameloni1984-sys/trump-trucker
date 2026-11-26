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


def test_keywords_match_whole_words_only():
    import trump_tracker
    assert "AI_TECH" not in trump_tracker._domains_for_public_text(
        "He said it again: beautiful Iowa air, read my mail")
    assert "AI_TECH" in trump_tracker._domains_for_public_text("New AI chips plant announced")
    assert "ENERGY" not in trump_tracker._domains_for_public_text("Farmers love this soil")
    assert "METALS" not in trump_tracker._domains_for_public_text("The Golden Dome is moving fast")
    assert "MEDIA" not in trump_tracker._domains_for_public_text("The truth is out")


def test_endorsements_and_department_of_war_are_not_market_posts():
    import sputnik_analyst as an
    assert not an.market_relevant({"title": "I endorse John for Congress, strong on tariffs",
                                   "domains": ["POLITICAL_CAMPAIGN"]})
    assert not an.market_relevant({"title": "Secretary of War Pete Hegseth is doing great", "domains": ["DEFENSE"]})
    assert an.market_relevant({"title": "Oil prices have dropped", "domains": ["ENERGY"]})


def test_brief_counts_only_market_posts():
    from datetime import datetime, timedelta, timezone
    import sputnik_analyst as an
    now = datetime(2026, 11, 26, 8, 0, tzinfo=timezone.utc)
    t = (now - timedelta(hours=2)).isoformat()
    state = {"intelligence_history": {
        "a": {"evidence": "PUBLIC_RSS_ITEM", "title": "The Failing New York Times reporter", "published": t},
        "b": {"evidence": "PUBLIC_RSS_ITEM", "title": "RT @someone great job", "published": t}}}
    assert "2 post, nessuno con impatto sui mercati" in an.brief_message(state, now)
    state["intelligence_history"]["c"] = {"evidence": "PUBLIC_RSS_ITEM", "title": "Oil prices dropped big",
                                          "published": t, "domains": ["ENERGY"]}
    text = an.brief_message(state, now)
    assert "3 post, 1 con impatto sui mercati" in text and "Failing" not in text
