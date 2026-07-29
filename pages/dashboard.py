import streamlit as st

from components.cards import metric_card, status_bar
from components.layout import page_header
from config import APP_NAME, APP_VERSION
from services.formatting import (
    compact_currency,
    percentage,
    signed_percentage,
    utc_time,
)
from services.market_data import (
    MarketDataError,
    clear_market_cache,
    get_market_snapshot,
)

page_header(APP_NAME, f"Core framework and live market data · v{APP_VERSION}")

refresh_col, _ = st.columns([1, 5])

with refresh_col:
    if st.button("Refresh data", use_container_width=True):
        clear_market_cache()
        st.rerun()

try:
    with st.spinner("Loading market data..."):
        snapshot = get_market_snapshot()

    status_bar(
        version=APP_VERSION,
        updated_at=utc_time(snapshot["updated_at"]),
        source=snapshot["source"],
    )

    columns = st.columns(4)

    with columns[0]:
        metric_card(
            "Global Market Cap",
            compact_currency(snapshot["total_market_cap"]),
            signed_percentage(snapshot["market_cap_change_24h"]),
        )

    with columns[1]:
        metric_card(
            "24h Market Volume",
            compact_currency(snapshot["total_volume"]),
            "Global trading activity",
        )

    with columns[2]:
        metric_card(
            "BTC Dominance",
            percentage(snapshot["btc_dominance"]),
            "Share of total crypto market cap",
        )

    with columns[3]:
        metric_card(
            "ETH Dominance",
            percentage(snapshot["eth_dominance"]),
            "Share of total crypto market cap",
        )

    st.subheader("Market leaders")

    coin_columns = st.columns(2)

    for column, coin_id in zip(
        coin_columns,
        ("bitcoin", "ethereum"),
    ):
        coin = snapshot["coins"].get(coin_id, {})

        with column:
            metric_card(
                coin.get("name", coin_id.title()),
                compact_currency(coin.get("price")),
                f"24h change {signed_percentage(coin.get('change_24h'))}",
            )

    st.subheader("Build status")

    status_columns = st.columns(3)

    with status_columns[0]:
        metric_card(
            "Market Data",
            "Live",
            "CoinGecko service connected",
        )

    with status_columns[1]:
        metric_card(
            "Portfolio",
            "Next",
            "Migration planned",
        )

    with status_columns[2]:
        metric_card(
            "Opportunity Scanner",
            "Queued",
            "After intelligence engine",
        )

except MarketDataError as exc:
    st.error(str(exc))
    st.info(
        "The app is working, but CoinGecko did not return data. "
        "Wait briefly and press Refresh data."
    )
