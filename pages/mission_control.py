import streamlit as st

from components.cards import metric_card, section_label, status_bar
from components.layout import page_header
from config import APP_NAME, APP_VERSION
from portfolio_config import PORTFOLIO
from services.briefing import build_market_briefing
from services.category_data import CategoryDataError, get_hot_categories
from services.conviction import build_conviction_list
from services.fear_greed import FearGreedError, get_fear_greed
from services.formatting import compact_currency, signed_percentage, utc_time
from services.market_data import MarketDataError, get_market_snapshot, get_scanner_market
from services.market_layers import research_reason, split_market_layers, tier_label
from services.portfolio_data import build_portfolio_snapshot
from services.scanner import build_opportunity_list

page_header(APP_NAME, "Two focused views · mainstream market intelligence or emerging opportunities")

mode = st.radio(
    "Terminal mode",
    options=["🏛️ Market Intelligence", "🚀 Opportunity Radar"],
    horizontal=True,
    label_visibility="collapsed",
)

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
    conviction = build_conviction_list(scanner["rows"], leader_change, held_symbols)
    layers = split_market_layers(conviction)

    status_bar(APP_VERSION, utc_time(market["updated_at"]), "Live intelligence feeds")

    if mode == "🏛️ Market Intelligence":
        st.markdown(
            '<div class="mode-panel"><strong>Market Intelligence</strong><br>'
            'A calm, mainstream view focused on established projects, familiar narratives '
            'and the information an average investor needs first.</div>',
            unsafe_allow_html=True,
        )

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

        left, right = st.columns([1.25, 1])
        with left:
            section_label("One-minute briefing")
            st.markdown(
                f'''
                <div class="briefing-panel">
                {briefing["overview"]}<br><br>
                {briefing["narrative"]}<br><br>
                <strong>Risk watch:</strong> {briefing["risk"]}
                </div>
                ''',
                unsafe_allow_html=True,
            )

        with right:
            section_label("Established leaders")
            core_rows = [
                {
                    "Asset": row["name"],
                    "Rank": row["rank"],
                    "Conviction": row["conviction"],
                    "Risk": row["risk"],
                    "24h": signed_percentage(row["change_24h"]),
                    "7d": signed_percentage(row["change_7d"]),
                }
                for row in layers["core"][:8]
            ]
            st.dataframe(core_rows, use_container_width=True, hide_index=True)

        section_label("Familiar narrative leaders")
        narrative_rows = [
            {
                "Narrative": row["name"],
                "24h": signed_percentage(row["change_24h"]),
                "Market Cap": compact_currency(row["market_cap"]),
                "Volume": compact_currency(row["volume_24h"]),
            }
            for row in (categories["leaders"][:6] if categories else [])
        ]
        st.dataframe(narrative_rows, use_container_width=True, hide_index=True)

    else:
        st.markdown(
            '<div class="mode-panel"><strong>Opportunity Radar</strong><br>'
            'A separate research view for less-established projects showing unusual '
            'momentum, liquidity and conviction. These are research candidates—not buy signals.'
            '</div>',
            unsafe_allow_html=True,
        )

        emerging = layers["emerging"][:10]
        summary = st.columns(4)
        with summary[0]:
            metric_card("Research Queue", str(len(emerging)), "Curated emerging projects")
        with summary[1]:
            high = sum(1 for row in emerging if row["conviction"] >= 80)
            metric_card("High Conviction", str(high), "Score of 80 or higher")
        with summary[2]:
            lower_risk = sum(1 for row in emerging if row["risk"] == "LOW")
            metric_card("Lower Risk", str(lower_risk), "Relative scanner classification")
        with summary[3]:
            median = (
                sum(row["conviction"] for row in emerging) / len(emerging)
                if emerging else 0
            )
            metric_card("Median Quality", f"{median:.1f}", "Queue conviction average")

        section_label("Today's research queue")
        for row in emerging[:6]:
            st.markdown(
                f'''
                <div class="project-card">
                  <div class="project-title">
                    {row["name"]} ({row["symbol"]}) · {tier_label(row)}
                  </div>
                  <div class="project-reason">
                    <strong>Conviction:</strong> {row["conviction"]}/100
                    &nbsp;·&nbsp; <strong>Risk:</strong> {row["risk"]}
                    &nbsp;·&nbsp; <strong>24h:</strong> {signed_percentage(row["change_24h"])}
                    &nbsp;·&nbsp; <strong>7d:</strong> {signed_percentage(row["change_7d"])}
                    <br><strong>Why it is here:</strong> {research_reason(row)}
                  </div>
                </div>
                ''',
                unsafe_allow_html=True,
            )

        st.caption(
            "Open Opportunity Radar from the sidebar for the complete ranked table "
            "and project momentum view."
        )

except MarketDataError as exc:
    st.error(str(exc))
