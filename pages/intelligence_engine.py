import pandas as pd
import streamlit as st

from components.cards import metric_card, section_label
from components.intelligence import evidence_panel, flow_badge, health_bars
from components.layout import page_header
from config import (
    APP_VERSION,
    INTELLIGENCE_RESEARCH_QUEUE_SIZE,
    INTELLIGENCE_TIMELINE_DAYS,
)
from portfolio_config import PORTFOLIO
from services.category_data import CategoryDataError, get_hot_categories
from services.conviction import build_conviction_list
from services.defillama import DeFiDataError, get_defi_protocols
from services.fear_greed import FearGreedError, get_fear_greed
from services.formatting import compact_currency, signed_percentage
from services.history_store import asset_history
from services.intelligence_engine import (
    build_evidence,
    capital_rotation,
    health_breakdown,
    market_intelligence_summary,
    overall_health,
    project_summary,
)
from services.market_data import MarketDataError, get_market_snapshot, get_scanner_market
from services.market_layers import research_reason, split_market_layers, tier_label
from services.momentum import find_protocol_match
from services.scanner import build_opportunity_list
from services.timeline import conviction_timeline, timeline_direction

page_header(
    "Intelligence Engine",
    f"Evidence-backed conclusions, health scores, rotation signals and timelines · v{APP_VERSION}",
)

try:
    market = get_market_snapshot()
    scanner = build_opportunity_list(get_scanner_market())
    held_symbols = {str(item["symbol"]).upper() for item in PORTFOLIO}

    try:
        category_data = get_hot_categories()
        categories = category_data.get("leaders", []) + category_data.get("laggards", [])
        category_change = category_data["leaders"][0]["change_24h"] if category_data.get("leaders") else None
    except CategoryDataError:
        category_data = None
        categories = []
        category_change = None

    try:
        sentiment = get_fear_greed()
    except FearGreedError:
        sentiment = None

    conviction = build_conviction_list(scanner["rows"], category_change, held_symbols)
    layers = split_market_layers(conviction)
    rotations = capital_rotation(categories)

    section_label("Today's intelligence")
    st.markdown(
        f'<div class="briefing-panel">{market_intelligence_summary(market, sentiment, rotations)}</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Capital rotation is an activity signal derived from category movement and turnover. "
        "It is not presented as measured on-chain fund flow."
    )

    section_label("Capital rotation")
    rotation_table = [
        {
            "Narrative": row["name"],
            "Signal": f"{flow_badge(row['rotation_signal'])} {row['rotation_signal']}",
            "Rotation Score": row["rotation_score"],
            "24h": signed_percentage(row["change_24h"]),
            "Turnover": f"{row['turnover']:.1%}",
            "Market Cap": compact_currency(row["market_cap"]),
        }
        for row in rotations[:8]
    ]
    st.dataframe(rotation_table, use_container_width=True, hide_index=True)

    section_label("Research queue")
    queue = layers["emerging"][:INTELLIGENCE_RESEARCH_QUEUE_SIZE]
    queue_table = [
        {
            "Project": f"{row['name']} ({row['symbol']})",
            "Tier": tier_label(row),
            "Conviction": row["conviction"],
            "Risk": row["risk"],
            "24h": signed_percentage(row["change_24h"]),
            "7d": signed_percentage(row["change_7d"]),
            "Why": research_reason(row),
        }
        for row in queue
    ]
    st.dataframe(queue_table, use_container_width=True, hide_index=True)

    project_pool = layers["core"][:12] + layers["emerging"][:15]
    if project_pool:
        section_label("Project intelligence")
        labels = [f"{row['name']} ({row['symbol']})" for row in project_pool]
        selected_label = st.selectbox("Choose a project", labels)
        selected = project_pool[labels.index(selected_label)]

        try:
            protocols = get_defi_protocols()["protocols"]
        except DeFiDataError:
            protocols = []
        protocol = find_protocol_match(selected, protocols)

        scores = health_breakdown(selected, protocol)
        health = overall_health(scores)
        evidence, confidence = build_evidence(selected, protocol)

        summary_cards = st.columns(4)
        with summary_cards[0]:
            metric_card("Overall Health", f"{health}/100", "Evidence-weighted")
        with summary_cards[1]:
            metric_card("Conviction", f"{selected['conviction']}/100", tier_label(selected))
        with summary_cards[2]:
            metric_card("Risk", selected["risk"], "Relative scanner classification")
        with summary_cards[3]:
            metric_card("Confidence", f"{confidence}%", f"{len(evidence)} evidence points")

        left, right = st.columns([1.05, 1])
        with left:
            section_label("Investment health")
            health_bars(scores)
        with right:
            section_label("Intelligence summary")
            st.markdown(
                f'<div class="briefing-panel">{project_summary(selected, protocol)}</div>',
                unsafe_allow_html=True,
            )

        section_label("Evidence")
        evidence_panel(evidence, confidence)

        section_label("Opportunity timeline")
        history = asset_history(selected["symbol"], INTELLIGENCE_TIMELINE_DAYS)
        timeline = conviction_timeline(history)
        if len(timeline) >= 2:
            frame = pd.DataFrame(timeline)
            frame["Date"] = pd.to_datetime(frame["Date"])
            st.line_chart(frame.set_index("Date")[["Conviction", "Opportunity"]])
            st.caption(timeline_direction(history))
        else:
            st.info(
                "More historical snapshots are required. Save snapshots over several days "
                "and this section will show whether conviction is building or weakening."
            )

        with st.expander("Data coverage and limitations"):
            st.write(
                "Price, market capitalisation and volume come from CoinGecko. "
                "TVL is included only when a reliable DeFiLlama protocol match exists. "
                "Wallet, developer, fee and stablecoin-flow metrics are not estimated."
            )

except MarketDataError as exc:
    st.error(str(exc))
