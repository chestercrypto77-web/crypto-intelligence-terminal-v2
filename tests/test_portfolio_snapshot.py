from services.portfolio_snapshot import (
    enrich_with_portfolio,
    portfolio_focus,
    portfolio_totals,
)


def test_live_values_use_balance_and_market_price():
    profile = (
        {
            "symbol": "BTC",
            "name": "Bitcoin",
            "balance": 0.1,
            "snapshot_value_aud": 9000,
            "priority": 1,
            "group": "Foundation",
            "conviction": "Core",
        },
    )
    market = [{"symbol": "BTC", "price": 100000, "attention": 50, "change_24h": 2}]
    rows = enrich_with_portfolio(market, profile)
    assert rows[0]["live_value_aud"] == 10000
    assert rows[0]["portfolio_weight"] == 100


def test_weighted_portfolio_change():
    rows = [
        {"live_value_aud": 10000, "snapshot_value_aud": 10000, "change_24h": 2},
        {"live_value_aud": 5000, "snapshot_value_aud": 5000, "change_24h": -1},
    ]
    totals = portfolio_totals(rows)
    assert round(totals["weighted_change_24h"], 2) == 1.0
    assert round(totals["estimated_day_change_aud"], 2) == 150.0


def test_focus_balances_attention_and_weight():
    rows = [
        {
            "symbol": "BTC",
            "attention": 30,
            "portfolio_weight": 55,
            "conviction": "Core",
            "live_value_aud": 15000,
        },
        {
            "symbol": "COTI",
            "attention": 95,
            "portfolio_weight": 1,
            "conviction": "High",
            "live_value_aud": 300,
        },
    ]
    focus = portfolio_focus(rows, 2)
    assert {row["symbol"] for row in focus} == {"BTC", "COTI"}
