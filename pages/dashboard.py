import streamlit as st
from components.cards import metric_card, status_bar
from components.layout import page_header
from config import APP_NAME, APP_VERSION
from services.fear_greed import FearGreedError, clear_fear_greed_cache, get_fear_greed
from services.formatting import compact_currency, percentage, signed_percentage, utc_time
from services.market_data import MarketDataError, clear_market_cache, get_market_snapshot

page_header(APP_NAME, f"Live market intelligence · v{APP_VERSION}")

if st.button("Refresh all data"):
    clear_market_cache()
    clear_fear_greed_cache()
    st.rerun()

try:
    snapshot = get_market_snapshot()
    status_bar(APP_VERSION, utc_time(snapshot["updated_at"]), snapshot["source"])
    try:
        sentiment = get_fear_greed()
    except FearGreedError:
        sentiment = None

    cards = st.columns(5)
    values = (
        ("Global Market Cap", compact_currency(snapshot["total_market_cap"]), signed_percentage(snapshot["market_cap_change_24h"])),
        ("24h Volume", compact_currency(snapshot["total_volume"]), "Global trading activity"),
        ("BTC Dominance", percentage(snapshot["btc_dominance"]), "Share of market cap"),
        ("ETH Dominance", percentage(snapshot["eth_dominance"]), "Share of market cap"),
        ("Fear & Greed", str(sentiment["value"]) if sentiment else "Unavailable", sentiment["classification"] if sentiment else "Feed unavailable"),
    )
    for col, item in zip(cards, values):
        with col:
            metric_card(*item)

    st.subheader("Market leaders")
    leaders = st.columns(2)
    for col, coin_id in zip(leaders, ("bitcoin", "ethereum")):
        coin = snapshot["coins"].get(coin_id, {})
        with col:
            metric_card(
                coin.get("name", coin_id.title()),
                compact_currency(coin.get("price")),
                f"24h {signed_percentage(coin.get('change_24h'))}",
            )

    st.subheader("Terminal modules")
    modules = st.columns(4)
    module_data = (
        ("Portfolio", "Live", "Weighted holdings intelligence"),
        ("What's Hot", "Live", "Narrative category momentum"),
        ("Opportunity Scanner", "Live", "Top-100 market scoring"),
        ("AI Briefing", "Next", "Planned for Release 0.5"),
    )
    for col, item in zip(modules, module_data):
        with col:
            metric_card(*item)

except MarketDataError as exc:
    st.error(str(exc))
    st.info("Wait briefly and press Refresh all data.")
