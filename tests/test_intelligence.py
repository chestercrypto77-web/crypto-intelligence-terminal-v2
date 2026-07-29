from services.briefing import build_market_briefing
from services.conviction import build_conviction_list, conviction_score
from services.portfolio_data import build_portfolio_snapshot
from services.scanner import build_opportunity_list


def test_portfolio_score() -> None:
    snapshot = build_portfolio_snapshot({})
    assert snapshot["score"] == 83.2


def test_scanner_sorting() -> None:
    coins = [
        {
            "name": "Alpha", "symbol": "a", "market_cap_rank": 20,
            "current_price": 1, "market_cap": 2_000_000_000,
            "total_volume": 400_000_000,
            "price_change_percentage_1h_in_currency": 2,
            "price_change_percentage_24h_in_currency": 10,
            "price_change_percentage_7d_in_currency": 20,
        },
        {
            "name": "Beta", "symbol": "b", "market_cap_rank": 30,
            "current_price": 1, "market_cap": 1_000_000_000,
            "total_volume": 20_000_000,
            "price_change_percentage_1h_in_currency": -1,
            "price_change_percentage_24h_in_currency": -5,
            "price_change_percentage_7d_in_currency": -10,
        },
    ]
    result = build_opportunity_list(coins)
    assert result["rows"][0]["name"] == "Alpha"


def test_conviction_penalises_high_risk() -> None:
    low = conviction_score(80, "LOW", 3, False)
    high = conviction_score(80, "HIGH", 3, False)
    assert low > high


def test_briefing_regime() -> None:
    market = {
        "market_cap_change_24h": 3.0,
        "btc_dominance": 55.0,
        "eth_dominance": 12.0,
    }
    sentiment = {"value": 70, "classification": "Greed"}
    result = build_market_briefing(market, sentiment, None, None)
    assert result["regime"] == "Risk-on"
