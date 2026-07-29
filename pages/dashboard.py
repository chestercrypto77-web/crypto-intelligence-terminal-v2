import streamlit as st

from components.cards import metric_card, status_bar
from components.layout import page_header
from config import APP_NAME, APP_VERSION
from services.fear_greed import FearGreedError, clear_fear_greed_cache, get_fear_greed
from services.formatting import compact_currency, percentage, signed_percentage, utc_time
from services.market_data import MarketDataError, clear_market_cache, get_market_snapshot

page_header(APP_NAME, f"Live market intelligence · v{APP_VERSION}")

refresh_col, _ = st.columns([1, 5])
with refresh_col:
    if st.button("Refresh data", use_container_width=True):
        clear_market_cache()
        clear_fear_greed_cache()
        st.rerun()

try:
    with st.spinner("Loading market data..."):
        snapshot = get_market_snapshot()

    status_bar(APP_VERSION, utc_time(snapshot["updated_at"]), snapshot["source"])

    fear_greed = None
    try:
        fear_greed = get_fear_greed()
    except FearGreedError:
        pass

    columns = st.columns(5)
    cards = (
        ("Global Market Cap", compact_currency(snapshot["total_market_cap"]),
         signed_percentage(snapshot["market_cap_change_24h"])),
        ("24h Market Volume", compact_currency(snapshot["total_volume"]),
         "Global trading activity"),
        ("BTC Dominance", percentage(snapshot["btc_dominance"]),
         "Share of total market cap"),
        ("ETH Dominance", percentage(snapshot["eth_dominance"]),
         "Share of total market cap"),
        (
            "Fear & Greed",
            str(fear_greed["value"]) if fear_greed else "Unavailable",
            fear_greed["classification"] if fear_greed else "External feed unavailable",
        ),
    )

    for column, card in zip(columns, cards):
        with column:
            metric_card(*card)

    st.subheader("Market leaders")
    leaders = st.columns(2)
    for column, coin_id in zip(leaders, ("bitcoin", "ethereum")):
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
        metric_card("Market Data", "Live", "CoinGecko connected")
    with status_columns[1]:
        metric_card("Portfolio Intelligence", "Live", "Open Portfolio in sidebar")
    with status_columns[2]:
        metric_card("Opportunity Scanner", "Next", "Planned for Release 0.4")

except MarketDataError as exc:
    st.error(str(exc))
    st.info("Wait briefly, then press Refresh data.")
