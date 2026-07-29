import streamlit as st

from components.cards import metric_card, section_label
from components.layout import page_header
from config import APP_VERSION, WATCHLIST_DEFAULT_IDS
from portfolio_config import PORTFOLIO
from services.category_data import CategoryDataError, get_hot_categories
from services.conviction import build_conviction_list
from services.formatting import compact_currency, signed_percentage
from services.history_store import asset_history
from services.market_data import MarketDataError, get_scanner_market
from services.scanner import build_opportunity_list
from services.trends import history_summary

page_header("Watchlist", f"Focused projects and score movement · v{APP_VERSION}")

try:
    scanner = build_opportunity_list(get_scanner_market())

    try:
        categories = get_hot_categories()
        category_change = (
            categories["leaders"][0]["change_24h"]
            if categories.get("leaders")
            else None
        )
    except CategoryDataError:
        category_change = None

    portfolio_symbols = {str(item["symbol"]).upper() for item in PORTFOLIO}
    conviction_rows = build_conviction_list(
        scanner["rows"],
        category_change,
        portfolio_symbols,
    )

    available = {
        str(row.get("symbol", "")).upper(): row
        for row in conviction_rows
    }
    default_symbols = [
        str(item["symbol"]).upper()
        for item in PORTFOLIO
        if str(item["symbol"]).upper() in available
    ]
    all_symbols = sorted(available)

    selected_symbols = st.multiselect(
        "Projects",
        options=all_symbols,
        default=default_symbols,
        help="Select the projects you want to keep visible.",
    )

    selected_rows = [available[symbol] for symbol in selected_symbols]

    summary = st.columns(3)
    with summary[0]:
        metric_card("Projects", str(len(selected_rows)), "Current watchlist")
    with summary[1]:
        improving = sum(
            1 for row in selected_rows
            if history_summary(asset_history(row["symbol"], 30), "conviction_score")["change"] not in (None, 0)
            and history_summary(asset_history(row["symbol"], 30), "conviction_score")["change"] > 0
        )
        metric_card("Improving", str(improving), "Positive stored conviction change")
    with summary[2]:
        high_risk = sum(1 for row in selected_rows if row["risk"] == "HIGH")
        metric_card("High Risk", str(high_risk), "Current scanner classification")

    section_label("Watchlist table")
    table = []
    for row in selected_rows:
        stored = asset_history(row["symbol"], 30)
        trend = history_summary(stored, "conviction_score")
        table.append(
            {
                "Asset": row["name"],
                "Symbol": row["symbol"],
                "Conviction": row["conviction"],
                "Level": row["conviction_label"],
                "30d Change": (
                    f"{trend['change']:+.1f}"
                    if trend["change"] is not None and len(stored) > 1
                    else "Build history"
                ),
                "Trend": trend["trend"],
                "Risk": row["risk"],
                "Price": compact_currency(row["price"]),
                "24h": signed_percentage(row["change_24h"]),
                "7d": signed_percentage(row["change_7d"]),
                "Held": "Yes" if row["portfolio_overlap"] else "No",
            }
        )

    st.dataframe(table, use_container_width=True, hide_index=True)
    st.caption(
        "Watchlist selections are session-based in this release. "
        "Historical trends appear after snapshots have been captured."
    )

except MarketDataError as exc:
    st.error(str(exc))
