import streamlit as st

from components.cards import metric_card, status_bar
from components.layout import page_header
from config import APP_VERSION
from services.formatting import compact_currency, signed_percentage, utc_time
from services.market_data import MarketDataError, get_market_snapshot
from services.portfolio_data import build_portfolio_snapshot

page_header("Portfolio Intelligence", f"Weighted portfolio view · v{APP_VERSION}")

try:
    with st.spinner("Loading portfolio market data..."):
        market = get_market_snapshot()
        portfolio = build_portfolio_snapshot(market["coins"])

    status_bar(APP_VERSION, utc_time(market["updated_at"]), market["source"])

    summary = st.columns(5)
    with summary[0]:
        metric_card("Portfolio Score", f"{portfolio['score']}/100", "Weighted intelligence score")
    with summary[1]:
        metric_card("Portfolio Risk", portfolio["risk"], f"{portfolio['high_risk_weight']:.0f}% high-risk weight")
    with summary[2]:
        metric_card("24h Momentum", signed_percentage(portfolio["change_24h"]), "Weighted available holdings")
    with summary[3]:
        metric_card("Strongest", portfolio["strongest"], "Highest intelligence score")
    with summary[4]:
        metric_card("Weakest", portfolio["weakest"], "Lowest intelligence score")

    table_rows = []
    for row in portfolio["rows"]:
        table_rows.append(
            {
                "Asset": row["name"],
                "Symbol": row["symbol"],
                "Weight": f"{row['weight']:.0f}%",
                "Score": row["score"],
                "Risk": row["risk"],
                "Price": compact_currency(row["price"]),
                "24h": signed_percentage(row["change_24h"]),
                "Market Cap": compact_currency(row["market_cap"]),
                "Rank": row["rank"] if row["rank"] is not None else "—",
                "Narrative": row["narrative"],
                "Data": row["data_status"],
            }
        )

    st.subheader("Holdings")
    st.dataframe(
        table_rows,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Scores and portfolio weights are research inputs, not financial advice. "
        "Market prices update from CoinGecko."
    )

except MarketDataError as exc:
    st.error(str(exc))
