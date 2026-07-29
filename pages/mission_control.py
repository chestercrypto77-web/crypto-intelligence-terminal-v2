import streamlit as st

from components.cards import metric_card, section_label, status_bar
from components.layout import page_header
from config import APP_NAME, APP_VERSION
from services.briefing import build_market_briefing
from services.category_data import CategoryDataError, get_hot_categories
from services.conviction import build_conviction_list
from services.fear_greed import FearGreedError, get_fear_greed
from services.formatting import compact_currency, signed_percentage, utc_time
from services.market_data import MarketDataError, get_market_snapshot, get_scanner_market
from services.portfolio_data import build_portfolio_snapshot
from services.scanner import build_opportunity_list
from portfolio_config import PORTFOLIO

page_header(APP_NAME, "Mission Control · one-minute market overview")

try:
    market = get_market_snapshot()
    portfolio = build_portfolio_snapshot(market["coins"])
    scanner = build_opportunity_list(get_scanner_market())

    try:
        sentiment = get_fear_greed()
    except FearGreedError:
        sentiment = None

    try:
        categories = get_hot_categories()
    except CategoryDataError:
        categories = None

    briefing = build_market_briefing(market, sentiment, categories, scanner)
    leader_change = (
        categories["leaders"][0]["change_24h"]
        if categories and categories.get("leaders")
        else None
    )
    held_symbols = {str(item["symbol"]).upper() for item in PORTFOLIO}
    conviction = build_conviction_list(
        scanner["rows"],
        leader_change,
        held_symbols,
    )

    status_bar(APP_VERSION, utc_time(market["updated_at"]), "Live intelligence feeds")

    section_label("Market pulse")
    pulse = st.columns(5)
    pulse_items = (
        ("Regime", briefing["regime"], signed_percentage(market["market_cap_change_24h"])),
        ("Portfolio", f"{portfolio['score']}/100", portfolio["risk"]),
        (
            "Fear & Greed",
            str(sentiment["value"]) if sentiment else "—",
            sentiment["classification"] if sentiment else "Unavailable",
        ),
        (
            "Top Narrative",
            categories["leaders"][0]["name"] if categories and categories["leaders"] else "—",
            signed_percentage(leader_change),
        ),
        ("Market Cap", compact_currency(market["total_market_cap"]), "Global"),
    )
    for column, item in zip(pulse, pulse_items):
        with column:
            metric_card(*item)

    left, right = st.columns([1.3, 1])

    with left:
        section_label("Intelligence briefing")
        st.markdown(
            f'''
            <div class="briefing-panel">
            {briefing["overview"]}<br><br>
            {briefing["narrative"]}<br><br>
            {briefing["candidates"]}<br><br>
            <strong>Risk watch:</strong> {briefing["risk"]}
            </div>
            ''',
            unsafe_allow_html=True,
        )

    with right:
        section_label("Top conviction")
        top_rows = [
            {
                "Asset": row["name"],
                "Score": row["conviction"],
                "Level": row["conviction_label"],
                "Risk": row["risk"],
                "24h": signed_percentage(row["change_24h"]),
            }
            for row in conviction[:5]
        ]
        st.dataframe(top_rows, use_container_width=True, hide_index=True)

    section_label("Narrative leaders")
    narrative_rows = [
        {
            "Narrative": row["name"],
            "24h": signed_percentage(row["change_24h"]),
            "Market Cap": compact_currency(row["market_cap"]),
            "Volume": compact_currency(row["volume_24h"]),
        }
        for row in (categories["leaders"][:5] if categories else [])
    ]
    st.dataframe(narrative_rows, use_container_width=True, hide_index=True)

except MarketDataError as exc:
    st.error(str(exc))
