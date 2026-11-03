import sputnik_public_feed_monitor as monitor


def test_operational_asset_filter_keeps_only_selected_metals_and_crops():
    assert monitor.domains_for("Gold and copper prices rise") == ["METALS"]
    assert monitor.domains_for("Wheat and soybean export outlook") == ["AGRICULTURE"]
    assert "AGRICULTURE" not in monitor.domains_for("Coffee and cocoa prices jump")
    assert "METALS" not in monitor.domains_for("Uranium and aluminum markets move")


def test_macro_catalyst_domains_are_preserved():
    assert "TRADE_POLICY" in monitor.domains_for("New tariffs announced")
    assert "RATES_MACRO" in monitor.domains_for("Federal Reserve interest rates")
