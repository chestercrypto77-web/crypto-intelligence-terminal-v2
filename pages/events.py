import html
from datetime import datetime

import streamlit as st

from components.cards import metric_card, section_label, status_bar
from components.layout import page_header
import config
from services.event_engine import daily_brief
from services.event_store import available_event_symbols, event_counts, recent_events

APP_VERSION = getattr(config, "APP_VERSION", "1.1.0")
DEFAULT_HOURS = int(getattr(config, "EVENT_DEFAULT_HISTORY_HOURS", 72))

page_header(
    "Event Detection",
    "Automatically detected changes across your holdings, watchlist and personal market",
)

filter_a, filter_b, filter_c = st.columns([1, 1, 1])
with filter_a:
    choices = [24, 48, 72, 168, 720]
    hours = st.selectbox(
        "Time window",
        choices,
        index=choices.index(DEFAULT_HOURS) if DEFAULT_HOURS in choices else 2,
        format_func=lambda value: "30 days" if value == 720 else "7 days" if value == 168 else f"{value} hours",
    )
with filter_b:
    selected_symbol = st.selectbox("Project", ["All"] + available_event_symbols())
with filter_c:
    severity = st.selectbox(
        "Minimum severity",
        ["Informational", "Medium", "High", "Critical"],
        index=1,
    )

events = recent_events(
    hours=hours,
    limit=200,
    symbol=selected_symbol,
    minimum_severity=severity,
)
counts = event_counts(hours=24)

status_bar(APP_VERSION, datetime.now().astimezone().strftime("%d %b %Y %H:%M"), "Event Detection Engine")

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("Events · 24h", str(counts["total"]), "All detected events")
with m2:
    metric_card("Critical", str(counts["Critical"]), "Immediate review")
with m3:
    metric_card("High", str(counts["High"]), "Important changes")
with m4:
    metric_card("Projects active", str(len({event["symbol"] for event in events})), f"Within {hours} hours")

st.markdown(
    f'<div class="briefing-panel">{html.escape(daily_brief(events))}</div>',
    unsafe_allow_html=True,
)

section_label("Intelligence feed")
if not events:
    st.info(
        "No events match the selected filters yet. Open My Market to run the latest "
        "personal-market scan, then return here."
    )

severity_icon = {
    "Critical": "🚨",
    "High": "🔥",
    "Medium": "⚡",
    "Informational": "ℹ️",
}

for event in events:
    detected = str(event["detected_at"]).replace("T", " ").replace("+00:00", " UTC")
    priority_label = {
        1: "Core holding",
        2: "Active watchlist",
        3: "Mainstream context",
    }.get(int(event["priority"]), "Monitored")
    severity_value = str(event["severity"])
    st.markdown(
        f"""
        <div class="feed-item severity-{html.escape(severity_value.lower())}">
          <div class="feed-time">{html.escape(detected)} · {html.escape(severity_value)} · {html.escape(priority_label)}</div>
          <div class="feed-title">{severity_icon.get(severity_value, '•')} {html.escape(str(event['title']))}</div>
          <div class="feed-detail">{html.escape(str(event['detail']))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

section_label("Detection rules")
st.caption(
    "The engine monitors one-hour and 24-hour movement, trading intensity, attention score, "
    "conviction changes, momentum-state transitions and risk changes. Tier 1 core holdings "
    "receive higher severity so projects such as COTI are surfaced prominently."
)
