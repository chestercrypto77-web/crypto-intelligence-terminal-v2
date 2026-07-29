import pandas as pd
import streamlit as st

from components.cards import metric_card, section_label
from components.intelligence import evidence_panel, health_bars
from components.layout import page_header
from config import APP_VERSION, INTELLIGENCE_TIMELINE_DAYS
from portfolio_config import PORTFOLIO
from services.category_data import CategoryDataError, get_hot_categories
from services.conviction import build_conviction_list
from services.defillama import DeFiDataError, get_defi_protocols
from services.formatting import compact_currency, signed_percentage
from services.history_store import asset_history
from services.intelligence_engine import (
    build_evidence,
    health_breakdown,
    overall_health,
    project_summary,
)
from services.market_data import MarketDataError, get_scanner_market
from services.market_layers import research_reason, split_market_layers, tier_label
from services.momentum import (
    defi_momentum_rows,
    find_protocol_match,
    liquidity_status,
    price_momentum_row,
)
from services.scanner import build_opportunity_list
from services.timeline import conviction_timeline, timeline_direction

page_header(
    "Opportunity Radar",
    f"Curated emerging projects with evidence-backed intelligence · v{APP_VERSION}",
)

st.info(
    "This page identifies research candidates using market rank, liquidity, momentum, "
    "risk and conviction. It is not a recommendation to buy."
)

try:
    scanner = build_opportunity_list(get_scanner_market())

    try:
        categories = get_hot_categories()
        category_change = categories["leaders"][0]["change_24h"] if categories.get("leaders") else None
    except CategoryDataError:
        category_change = None

    portfolio_symbols = {str(item["symbol"]).upper() for item in PORTFOLIO}
    conviction = build_conviction_list(scanner["rows"], category_change, portfolio_symbols)
    emerging = split_market_layers(conviction)["emerging"]

    try:
        protocols = get_defi_protocols()["protocols"]
    except DeFiDataError:
        protocols = []

    top = emerging[:15]
    cards = st.columns(4)
    with cards[0]:
        metric_card("Candidates", str(len(top)), "Highest-ranked emerging projects")
    with cards[1]:
        metric_card("Emerging Leaders", str(sum(tier_label(row) == "Emerging Leader" for row in top)), "Highest-quality tier")
    with cards[2]:
        metric_card("Positive 7d", str(sum(float(row.get("change_7d") or 0) > 0 for row in top)), "Positive weekly momentum")
    with cards[3]:
        metric_card("DeFi Coverage", str(sum(bool(find_protocol_match(row, protocols)) for row in top)), "Matched TVL data")

    section_label("Ranked research queue")
    table = [
        {
            "Project": row["name"],
            "Symbol": row["symbol"],
            "Tier": tier_label(row),
            "Rank": row["rank"],
            "Conviction": row["conviction"],
            "Risk": row["risk"],
            "Market Cap": compact_currency(row["market_cap"]),
            "24h": signed_percentage(row["change_24h"]),
            "7d": signed_percentage(row["change_7d"]),
            "Liquidity": liquidity_status(row),
            "Why it is here": research_reason(row),
        }
        for row in top
    ]
    st.dataframe(table, use_container_width=True, hide_index=True)

    if top:
        section_label("Project intelligence")
        labels = [f"{row['name']} ({row['symbol']})" for row in top]
        selected_label = st.selectbox("Choose a project", labels)
        selected = top[labels.index(selected_label)]
        protocol = find_protocol_match(selected, protocols)

        scores = health_breakdown(selected, protocol)
        health = overall_health(scores)
        evidence, confidence = build_evidence(selected, protocol)

        overview = st.columns(4)
        with overview[0]:
            metric_card("Health", f"{health}/100", "Evidence-weighted")
        with overview[1]:
            metric_card("Conviction", f"{selected['conviction']}/100", tier_label(selected))
        with overview[2]:
            metric_card("Risk", selected["risk"], "Relative market risk")
        with overview[3]:
            metric_card("Confidence", f"{confidence}%", f"{len(evidence)} evidence points")

        momentum_rows = [price_momentum_row(selected)]
        if protocol:
            momentum_rows.extend(defi_momentum_rows(protocol))
            st.caption(f"TVL matched to {protocol['name']} through DeFiLlama.")
        else:
            st.caption("No reliable DeFiLlama protocol match was found; TVL is not estimated.")
        st.dataframe(momentum_rows, use_container_width=True, hide_index=True)

        left, right = st.columns([1, 1])
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
            st.info("More saved snapshots are required before a conviction timeline can be calculated.")

except MarketDataError as exc:
    st.error(str(exc))
