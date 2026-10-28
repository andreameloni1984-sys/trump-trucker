from sputnik_anticipation import adjacent_sentence_plan, anticipation_message


def test_adjacent_oil_action_and_topic_create_anticipation_only():
    text = (
        "Authorities disrupted the route overnight. "
        "Tanker traffic near Hormuz was affected."
    )
    plan = adjacent_sentence_plan(text)
    assert plan is not None
    assert plan["id"] == "oil_supply_disruption"
    assert plan["evidence_mode"] == "ADJACENT_SENTENCES"
    assert plan["status"] == "ANTICIPATION_ONLY_NEEDS_PRICE_VOLUME_CONFIRMATION"

    message = anticipation_message(plan, "Official public source", quotes={})
    assert "SPUTNIK — OPPORTUNITÀ ANTICIPATA" in message
    assert "PAPER TRADING" in message
    assert "ANTICIPAZIONE, NON SEGNALE CONFERMATO" in message
    assert "quotazione aggiornata e ATR necessari" in message
    assert "Entry" not in message


def test_ambiguous_adjacent_trade_policy_match_abstains():
    text = (
        "The administration announced a new measure. "
        "Tariffs on imports take effect next month."
    )
    assert adjacent_sentence_plan(text) is None


def test_negated_adjacent_action_does_not_create_anticipation():
    text = (
        "Authorities did not disrupt the route overnight. "
        "Tanker traffic near Hormuz was affected."
    )
    assert adjacent_sentence_plan(text) is None


def test_existing_strict_match_is_left_to_primary_decision_engine():
    text = "The Houthis attacked shipping near Hormuz."
    assert adjacent_sentence_plan(text) is None
