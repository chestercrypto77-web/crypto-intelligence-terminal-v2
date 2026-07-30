import html
import streamlit as st

from components.cards import section_label, status_bar
from components.layout import page_header
import config

APP_VERSION = getattr(config, "APP_VERSION", "1.1.0")
PERSONAL_ATTENTION_LIMIT = getattr(config, "PERSONAL_ATTENTION_LIMIT", 12)
EVENT_BRIEF_LIMIT = getattr(config, "EVENT_BRIEF_LIMIT", 5)

from personal_market_config import MY_MARKET
from portfolio_config import PORTFOLIO
from services.category_data import CategoryDataError, get_hot_categories
from services.conviction import build_conviction_list
from services.event_engine import daily_brief, run_event_detection
from services.event_store import recent_events
from services.formatting import compact_currency, signed_percentage, utc_time
from services.market_data import MarketDataError, get_market_snapshot, get_scanner_market
from services.personal_intelligence import build_personal_market, market_summary
from services.scanner import build_opportunity_list

page_header("My Market", "Your holdings, interests and Australian mainstream crypto context")

try:
    market = get_market_snapshot()
    scanner = build_opportunity_list(get_scanner_market())

    try:
        categories = get_hot_categories()
        leader_change = categories["leaders"][0]["change_24h"] if categories.get("leaders") else None
    except CategoryDataError:
        leader_change = None

    held_symbols = {str(item["symbol"]).upper() for item in PORTFOLIO}
    conviction_rows = build_conviction_list(scanner["rows"], leader_change, held_symbols)
    rows = build_personal_market(scanner["rows"], conviction_rows, MY_MARKET)

    detection = run_event_detection(rows)
    brief_events = recent_events(hours=24, limit=EVENT_BRIEF_LIMIT, minimum_severity="Medium")

    status_bar(APP_VERSION, utc_time(market["updated_at"]), "Personal Intelligence + Event Detection")

    section_label("Since your last checks")
    st.markdown(
        f'<div class="briefing-panel">{html.escape(daily_brief(brief_events))}</div>',
        unsafe_allow_html=True,
    )
    if detection["inserted"]:
        st.caption(
            f"{detection['inserted']} new event"
            f"{'s' if detection['inserted'] != 1 else ''} recorded during this scan."
        )
    st.page_link("pages/events.py", label="Open full Event Detection feed", icon="🔔")

    section_label("Your market today")
    st.markdown(
        f'<div class="briefing-panel">{html.escape(market_summary(rows))}</div>',
        unsafe_allow_html=True,
    )

    section_label("Needs your attention")
    priority_rows = [row for row in rows if row.get("available")][:PERSONAL_ATTENTION_LIMIT]
    for row in priority_rows:
        change = float(row.get("change_24h") or 0)
        marker = "🔥" if row["attention"] >= 85 else "⚡" if row["attention"] >= 70 else "🟢" if change >= 0 else "🔻"
        st.markdown(
            f"""
            <div class="project-card">
              <div class="project-title">{marker} {html.escape(row['name'])} ({html.escape(row['symbol'])})</div>
              <div class="terminal-card-label">{html.escape(row['group'])} · Attention {row['attention']:.0f}/100 · {html.escape(row['attention_label'])}</div>
              <div class="project-reason"><strong>{html.escape(row['momentum_state'])}</strong> — {html.escape(row['reason'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    core, mainstream = st.columns(2)
    with core:
        section_label("My holdings and active watchlist")
        personal = [row for row in rows if int(row["priority"]) <= 2]
        st.dataframe(
            [{
                "Project": row["name"],
                "Symbol": row["symbol"],
                "24h": signed_percentage(row.get("change_24h")) if row.get("available") else "—",
                "7d": signed_percentage(row.get("change_7d")) if row.get("available") else "—",
                "Volume": compact_currency(row.get("volume")) if row.get("available") else "—",
                "Attention": row.get("attention", 0),
                "State": row.get("momentum_state", "Data unavailable"),
            } for row in personal],
            use_container_width=True,
            hide_index=True,
        )

    with mainstream:
        section_label("Australian mainstream context")
        context = [row for row in rows if int(row["priority"]) == 3]
        st.dataframe(
            [{
                "Project": row["name"],
                "Symbol": row["symbol"],
                "24h": signed_percentage(row.get("change_24h")) if row.get("available") else "—",
                "7d": signed_percentage(row.get("change_7d")) if row.get("available") else "—",
                "Rank": row.get("rank", "—"),
                "State": row.get("momentum_state", "Data unavailable"),
            } for row in context],
            use_container_width=True,
            hide_index=True,
        )

    section_label("How personalisation works")
    st.info(
        "Tier 1 holdings receive the highest attention and event severity, Tier 2 watchlist projects "
        "receive active monitoring, and Tier 3 provides mainstream Australian-market context. Edit "
        "`personal_market_config.py` to add, remove or reprioritise projects."
    )
    st.caption(
        "Attention and events are monitoring signals based on market data. They are not investment advice."
    )

except MarketDataError as exc:
    st.error(str(exc))
