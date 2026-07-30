import html
import streamlit as st

from components.cards import metric_card, section_label, status_bar
from components.layout import page_header
import config

APP_VERSION = getattr(config, "APP_VERSION", "0.9.1")
PULSE_FEED_LIMIT = getattr(config, "PULSE_FEED_LIMIT", 12)
PULSE_HISTORY_DAYS = getattr(config, "PULSE_HISTORY_DAYS", 7)
PULSE_MOVER_LIMIT = getattr(config, "PULSE_MOVER_LIMIT", 8)
PULSE_NARRATIVE_LIMIT = getattr(config, "PULSE_NARRATIVE_LIMIT", 8)
from portfolio_config import PORTFOLIO
from services.category_data import CategoryDataError, get_hot_categories
from services.conviction import build_conviction_list
from services.fear_greed import FearGreedError, get_fear_greed
from services.formatting import signed_percentage, utc_time
from services.history_store import asset_history, market_history
from services.intelligence_engine import capital_rotation
from services.market_data import MarketDataError, get_market_snapshot, get_scanner_market
from services.market_layers import split_market_layers
from services.portfolio_data import build_portfolio_snapshot
from services.pulse_engine import (
    daily_brief,
    intelligence_movers,
    live_feed,
    market_pulse_score,
    narrative_heat,
    portfolio_monitor,
    pulse_direction,
    pulse_label,
)
from services.scanner import build_opportunity_list

page_header("Market Pulse", "What changed, why it matters and what deserves attention now")

try:
    market = get_market_snapshot()
    scanner = build_opportunity_list(get_scanner_market())
    portfolio = build_portfolio_snapshot(market["coins"])

    try:
        sentiment = get_fear_greed()
    except FearGreedError:
        sentiment = None

    try:
        categories = get_hot_categories()
        category_rows = categories.get("leaders", []) + categories.get("laggards", [])
        leader_change = categories["leaders"][0]["change_24h"] if categories.get("leaders") else None
    except CategoryDataError:
        categories = None
        category_rows = []
        leader_change = None

    held_symbols = {str(item["symbol"]).upper() for item in PORTFOLIO}
    conviction_rows = build_conviction_list(scanner["rows"], leader_change, held_symbols)
    layers = split_market_layers(conviction_rows)
    rotations = capital_rotation(category_rows)

    histories = {
        str(row.get("symbol", "")).upper(): asset_history(
            str(row.get("symbol", "")), PULSE_HISTORY_DAYS
        )
        for row in conviction_rows
    }
    movers = intelligence_movers(conviction_rows, histories, PULSE_MOVER_LIMIT)
    portfolio_rows = portfolio_monitor(list(PORTFOLIO), conviction_rows)
    market_hist = market_history(PULSE_HISTORY_DAYS)

    pulse = market_pulse_score(market, sentiment, rotations, portfolio)
    state = pulse_label(pulse)
    direction = pulse_direction(pulse, market_hist)
    research_queue = layers["emerging"][:5]

    status_bar(APP_VERSION, utc_time(market["updated_at"]), "Live pulse and historical intelligence")

    top_left, top_right = st.columns([0.72, 1.28])
    with top_left:
        st.markdown(
            f'''
            <div class="pulse-meter">
              <div class="terminal-card-label">Market Pulse</div>
              <div class="pulse-number">{pulse}</div>
              <div class="pulse-label">{html.escape(state)}</div>
              <div class="pulse-direction">{html.escape(direction)}</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
    with top_right:
        section_label("Daily intelligence brief")
        st.markdown(
            f'<div class="pulse-panel">{html.escape(daily_brief(pulse, state, rotations, movers, research_queue))}</div>',
            unsafe_allow_html=True,
        )

    section_label("Live intelligence feed")
    feed = live_feed(
        market, sentiment, rotations, movers, portfolio_rows, PULSE_FEED_LIMIT
    )
    for item in feed:
        marker = "▲" if item["level"] == "positive" else "▼" if item["level"] == "negative" else "●"
        st.markdown(
            f'''
            <div class="feed-item">
              <div class="feed-time">{html.escape(item["time"])}</div>
              <div class="feed-title">{marker} {html.escape(item["title"])}</div>
              <div class="feed-detail">{html.escape(item["detail"])}</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    left, right = st.columns([1.05, 0.95])
    with left:
        section_label("Biggest intelligence movers")
        mover_table = [
            {
                "Project": f"{row['name']} ({row['symbol']})",
                "Conviction": row["current"],
                "Change": "—" if row["delta"] is None else f"{row['delta']:+.1f}",
                "Signal": row["signal"],
                "Risk": row["risk"],
            }
            for row in movers
        ]
        st.dataframe(mover_table, use_container_width=True, hide_index=True)

    with right:
        section_label("Narrative heatmap")
        heat = narrative_heat(rotations, PULSE_NARRATIVE_LIMIT)
        if heat:
            for row in heat:
                st.markdown(
                    f'''
                    <div class="heat-row">
                      <div>{html.escape(str(row["name"]))}</div>
                      <div class="heat-track">
                        <div class="heat-fill" style="width:{row["heat"]}%"></div>
                      </div>
                      <div><strong>{html.escape(row["state"])}</strong></div>
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )
        else:
            st.info("Narrative data is temporarily unavailable.")

    section_label("Portfolio monitor")
    portfolio_table = [
        {
            "Holding": row["name"],
            "Symbol": row["symbol"],
            "Weight": row["weight"],
            "Conviction": row["conviction"] if row["conviction"] is not None else "—",
            "Status": row["status"],
            "Risk": row["risk"],
        }
        for row in portfolio_rows
    ]
    st.dataframe(portfolio_table, use_container_width=True, hide_index=True)

    section_label("Today's research focus")
    research_table = [
        {
            "Project": row["name"],
            "Symbol": row["symbol"],
            "Conviction": row["conviction"],
            "24h": signed_percentage(row["change_24h"]),
            "7d": signed_percentage(row["change_7d"]),
            "Risk": row["risk"],
        }
        for row in research_queue
    ]
    st.dataframe(research_table, use_container_width=True, hide_index=True)

    st.caption(
        "Market Pulse combines live market movement, sentiment, relative narrative activity, "
        "portfolio health and stored conviction history. A missing historical baseline is shown "
        "as 'New baseline' rather than estimated."
    )

except MarketDataError as exc:
    st.error(str(exc))
