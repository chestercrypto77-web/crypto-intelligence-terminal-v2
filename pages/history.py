from datetime import datetime

import streamlit as st

from components.cards import metric_card, section_label
from components.layout import page_header
from config import APP_VERSION, HISTORY_DEFAULT_DAYS
from services.formatting import signed_percentage
from services.history_store import (
    asset_history,
    available_assets,
    database_bytes,
    market_history,
    restore_database,
    snapshot_count,
)
from services.snapshot_engine import capture_intelligence_snapshot
from services.trends import history_summary

page_header("Historical Intelligence", f"Score movement and trend context · v{APP_VERSION}")

action_columns = st.columns([1, 1, 1, 2])
with action_columns[0]:
    if st.button("Capture snapshot", use_container_width=True):
        with st.spinner("Capturing current intelligence..."):
            result = capture_intelligence_snapshot()
        st.success(
            f"Snapshot saved at {result['captured_at']} "
            f"with {result['assets_saved']} assets."
        )
        st.rerun()

with action_columns[1]:
    counts = snapshot_count()
    st.download_button(
        "Download history",
        data=database_bytes(),
        file_name="intelligence_history.db",
        mime="application/octet-stream",
        use_container_width=True,
    )

with action_columns[2]:
    uploaded = st.file_uploader(
        "Restore history",
        type=["db"],
        label_visibility="collapsed",
    )
    if uploaded is not None and st.button("Confirm restore", use_container_width=True):
        restore_database(uploaded.getvalue())
        st.success("History database restored.")
        st.rerun()

st.caption(
    "Streamlit Cloud storage can reset during redeployments or restarts. "
    "Download the database regularly and restore it after an update."
)

counts = snapshot_count()
summary_cards = st.columns(3)
with summary_cards[0]:
    metric_card("Market Snapshots", str(counts["market"]), "Saved observation points")
with summary_cards[1]:
    metric_card("Asset Records", str(counts["assets"]), "Saved project observations")
with summary_cards[2]:
    metric_card("Storage", "Local SQLite", "Backup before redeploying")

days = st.select_slider(
    "History window",
    options=[7, 14, 30, 60, 90, 180],
    value=HISTORY_DEFAULT_DAYS,
)

market_rows = market_history(days)
if market_rows:
    section_label("Market history")
    market_score = history_summary(market_rows, "portfolio_score")
    market_change = history_summary(market_rows, "market_change_24h")

    market_cards = st.columns(4)
    with market_cards[0]:
        metric_card("Portfolio Trend", market_score["trend"], f"{market_score['current']:.1f}/100")
    with market_cards[1]:
        metric_card("Score Change", f"{market_score['change']:+.1f}", f"{days}-day window")
    with market_cards[2]:
        metric_card("Average Score", f"{market_score['average']:.1f}", "Historical mean")
    with market_cards[3]:
        metric_card("Market Momentum", market_change["trend"], signed_percentage(market_change["current"]))

    chart_rows = [
        {
            "Captured": datetime.fromisoformat(row["captured_at"]),
            "Portfolio Score": row["portfolio_score"],
            "Fear & Greed": row["fear_greed"],
            "Market Change": row["market_change_24h"],
        }
        for row in market_rows
    ]
    st.line_chart(
        chart_rows,
        x="Captured",
        y=["Portfolio Score", "Fear & Greed"],
        use_container_width=True,
    )
else:
    st.info("Capture at least one snapshot to begin building history.")

assets = available_assets()
if assets:
    section_label("Asset history")
    labels = [f"{item['name']} ({item['symbol']})" for item in assets]
    selected_label = st.selectbox("Asset", labels)
    selected = assets[labels.index(selected_label)]
    rows = asset_history(selected["symbol"], days)

    opportunity = history_summary(rows, "opportunity_score")
    conviction = history_summary(rows, "conviction_score")

    asset_cards = st.columns(4)
    with asset_cards[0]:
        metric_card("Conviction Trend", conviction["trend"], f"{conviction['current']:.1f}")
    with asset_cards[1]:
        metric_card("Conviction Change", f"{conviction['change']:+.1f}", f"{days}-day window")
    with asset_cards[2]:
        metric_card("Opportunity Trend", opportunity["trend"], f"{opportunity['current']:.1f}")
    with asset_cards[3]:
        metric_card("Score Range", f"{conviction['low']:.1f}–{conviction['high']:.1f}", "Conviction")

    chart_rows = [
        {
            "Captured": datetime.fromisoformat(row["captured_at"]),
            "Opportunity": row["opportunity_score"],
            "Conviction": row["conviction_score"],
        }
        for row in rows
    ]
    st.line_chart(
        chart_rows,
        x="Captured",
        y=["Opportunity", "Conviction"],
        use_container_width=True,
    )
