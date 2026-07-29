import streamlit as st

from components.cards import metric_card
from components.layout import page_header
from config import APP_VERSION
from services.briefing import build_market_briefing
from services.category_data import CategoryDataError, get_hot_categories
from services.fear_greed import FearGreedError, get_fear_greed
from services.market_data import MarketDataError, get_market_snapshot, get_scanner_market
from services.scanner import build_opportunity_list

page_header("Market Briefing", f"Rule-based intelligence summary · v{APP_VERSION}")

try:
    market = get_market_snapshot()

    try:
        sentiment = get_fear_greed()
    except FearGreedError:
        sentiment = None

    try:
        categories = get_hot_categories()
    except CategoryDataError:
        categories = None

    scanner = build_opportunity_list(get_scanner_market())
    briefing = build_market_briefing(market, sentiment, categories, scanner)

    top = st.columns(3)
    with top[0]:
        metric_card("Market Regime", briefing["regime"], "Composite market and sentiment reading")
    with top[1]:
        metric_card("Scanner Candidates", str(scanner["high_conviction"]), "Score ≥75 and not high risk")
    with top[2]:
        metric_card(
            "Leading Narrative",
            categories["leaders"][0]["name"] if categories and categories["leaders"] else "Unavailable",
            "Highest 24-hour category momentum",
        )

    st.subheader("Intelligence summary")
    st.markdown(
        f'''
        <div class="briefing-panel">
        <strong>Market:</strong> {briefing["overview"]}<br><br>
        <strong>Dominance:</strong> {briefing["dominance"]}<br><br>
        <strong>Sentiment:</strong> {briefing["sentiment"]}<br><br>
        <strong>Narratives:</strong> {briefing["narrative"]}<br><br>
        <strong>Research candidates:</strong> {briefing["candidates"]}<br><br>
        <strong>Risk watch:</strong> {briefing["risk"]}
        </div>
        ''',
        unsafe_allow_html=True,
    )

    st.caption(
        "This briefing is generated from transparent rules using live market, "
        "sentiment, category and scanner data. It is not financial advice."
    )

except MarketDataError as exc:
    st.error(str(exc))
