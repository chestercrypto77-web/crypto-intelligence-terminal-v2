import streamlit as st

from components.cards import metric_card
from components.layout import page_header
from config import APP_VERSION
from portfolio_config import PORTFOLIO
from services.category_data import CategoryDataError, get_hot_categories
from services.conviction import build_conviction_list
from services.formatting import compact_currency, signed_percentage
from services.market_data import MarketDataError, get_scanner_market
from services.scanner import build_opportunity_list

page_header("Conviction Engine", f"Risk-adjusted research ranking · v{APP_VERSION}")

try:
    scanner = build_opportunity_list(get_scanner_market())

    try:
        categories = get_hot_categories()
        category_change = (
            categories["leaders"][0]["change_24h"]
            if categories.get("leaders") else None
        )
    except CategoryDataError:
        category_change = None

    portfolio_symbols = {str(item["symbol"]).upper() for item in PORTFOLIO}
    rows = build_conviction_list(scanner["rows"], category_change, portfolio_symbols)

    high_count = sum(1 for row in rows if row["conviction_label"] == "HIGH")
    medium_count = sum(1 for row in rows if row["conviction_label"] == "MEDIUM")

    summary = st.columns(3)
    with summary[0]:
        metric_card("High Conviction", str(high_count), "Risk-adjusted score ≥80")
    with summary[1]:
        metric_card("Medium Conviction", str(medium_count), "Risk-adjusted score 65–79.9")
    with summary[2]:
        metric_card(
            "Narrative Tailwind",
            signed_percentage(category_change),
            "Applied as a broad category signal",
        )

    label_filter = st.multiselect(
        "Conviction levels",
        ["HIGH", "MEDIUM", "WATCH"],
        default=["HIGH", "MEDIUM"],
    )
    maximum_results = st.slider("Maximum results", 5, 40, 20, 5)

    filtered = [
        row for row in rows
        if row["conviction_label"] in label_filter
    ][:maximum_results]

    table = [
        {
            "Asset": row["name"],
            "Symbol": row["symbol"],
            "Conviction": row["conviction"],
            "Level": row["conviction_label"],
            "Opportunity": row["score"],
            "Risk": row["risk"],
            "24h": signed_percentage(row["change_24h"]),
            "7d": signed_percentage(row["change_7d"]),
            "Price": compact_currency(row["price"]),
            "Market Cap": compact_currency(row["market_cap"]),
            "Already Held": "Yes" if row["portfolio_overlap"] else "No",
        }
        for row in filtered
    ]

    st.dataframe(table, use_container_width=True, hide_index=True)
    st.caption(
        "Conviction combines scanner quality, risk, current narrative momentum "
        "and portfolio overlap. It ranks research priorities rather than issuing buy signals."
    )

except MarketDataError as exc:
    st.error(str(exc))
