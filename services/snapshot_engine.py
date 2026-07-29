from typing import Any

from portfolio_config import PORTFOLIO
from services.briefing import build_market_briefing
from services.category_data import get_hot_categories
from services.conviction import build_conviction_list
from services.fear_greed import get_fear_greed
from services.history_store import save_snapshot
from services.market_data import get_market_snapshot, get_scanner_market
from services.portfolio_data import build_portfolio_snapshot
from services.scanner import build_opportunity_list


def capture_intelligence_snapshot() -> dict[str, Any]:
    market = get_market_snapshot()
    sentiment = get_fear_greed()
    categories = get_hot_categories()
    scanner = build_opportunity_list(get_scanner_market())
    portfolio = build_portfolio_snapshot(market["coins"])

    leader_change = (
        categories["leaders"][0]["change_24h"]
        if categories.get("leaders")
        else None
    )
    portfolio_symbols = {str(item["symbol"]).upper() for item in PORTFOLIO}
    conviction_rows = build_conviction_list(
        scanner["rows"],
        leader_change,
        portfolio_symbols,
    )

    briefing = build_market_briefing(
        market,
        sentiment,
        categories,
        scanner,
    )

    captured_at = save_snapshot(
        market=market,
        briefing=briefing,
        sentiment=sentiment,
        categories=categories,
        portfolio=portfolio,
        conviction_rows=conviction_rows,
    )

    return {
        "captured_at": captured_at,
        "assets_saved": len(conviction_rows),
        "regime": briefing["regime"],
        "portfolio_score": portfolio["score"],
    }
