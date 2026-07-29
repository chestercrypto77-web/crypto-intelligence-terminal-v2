import streamlit as st
from components.cards import metric_card
from components.layout import page_header
from config import APP_VERSION
from services.formatting import compact_currency, ratio, signed_percentage
from services.market_data import MarketDataError, clear_market_cache, get_scanner_market
from services.scanner import build_opportunity_list

page_header("Opportunity Scanner", f"Momentum, liquidity and market-quality ranking · v{APP_VERSION}")

controls = st.columns([1, 1, 1, 2])
with controls[0]:
    minimum_score = st.slider("Minimum score", 0, 100, 55)
with controls[1]:
    risk_filter = st.selectbox("Maximum risk", ["HIGH", "MEDIUM", "LOW"])
with controls[2]:
    result_limit = st.selectbox("Results", [10, 20, 30, 50], index=1)
with controls[3]:
    st.write("")
    st.write("")
    if st.button("Refresh scanner"):
        clear_market_cache()
        st.rerun()

try:
    result = build_opportunity_list(get_scanner_market())

    summary = st.columns(3)
    with summary[0]:
        metric_card("Eligible Markets", str(result["market_count"]), "Liquidity and market-cap filters passed")
    with summary[1]:
        metric_card("Median Score", str(result["median_score"] or "Unavailable"), "Current scanner baseline")
    with summary[2]:
        metric_card("High Conviction", str(result["high_conviction"]), "Score ≥75 and not high risk")

    risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    maximum = risk_order[risk_filter]
    rows = [
        row for row in result["rows"]
        if row["score"] >= minimum_score and risk_order[row["risk"]] <= maximum
    ][:result_limit]

    table = [
        {
            "Rank": row["rank"] if row["rank"] is not None else "—",
            "Asset": row["name"],
            "Symbol": row["symbol"],
            "Opportunity": row["score"],
            "Risk": row["risk"],
            "Price": compact_currency(row["price"]),
            "1h": signed_percentage(row["change_1h"]),
            "24h": signed_percentage(row["change_24h"]),
            "7d": signed_percentage(row["change_7d"]),
            "Volume": compact_currency(row["volume"]),
            "Market Cap": compact_currency(row["market_cap"]),
            "Vol/MC": ratio(row["volume_ratio"]),
        }
        for row in rows
    ]

    st.subheader("Ranked opportunities")
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.caption(
        "The score combines short-term momentum, trading liquidity and market size, "
        "with penalties for extreme moves. It is a research ranking, not financial advice."
    )

except MarketDataError as exc:
    st.error(str(exc))
