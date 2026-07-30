import streamlit as st
from components.theme import apply_theme
from config import APP_NAME

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()

navigation = st.navigation(
    {
        "Daily Desk": [
            st.Page("pages/morning_brief.py", title="Today", icon="☀️", default=True),
            st.Page("pages/portfolio_desk.py", title="My Portfolio", icon="💼"),
            st.Page("pages/whats_moving.py", title="What's Moving?", icon="📈"),
            st.Page("pages/volume_intelligence.py", title="Volume Intelligence", icon="🔊"),
            st.Page("pages/market_themes.py", title="Market Themes", icon="🌍"),
            st.Page("pages/attention_desk.py", title="Needs Attention", icon="🚨"),
        ],
        "Research": [
            st.Page("pages/opportunity_scanner.py", title="Market Scanner", icon="🔎"),
            st.Page("pages/conviction.py", title="Conviction Research", icon="⭐"),
            st.Page("pages/defi_intelligence.py", title="DeFi Research", icon="🌐"),
            st.Page("pages/history.py", title="History", icon="🕘"),
        ],
        "Technical Tools": [
            st.Page("pages/my_market.py", title="Personal Intelligence", icon="🧠"),
            st.Page("pages/momentum_radar.py", title="Legacy Momentum", icon="📊"),
            st.Page("pages/events.py", title="Legacy Events", icon="🔔"),
            st.Page("pages/market_pulse.py", title="Legacy Market Pulse", icon="⚡"),
            st.Page("pages/market_briefing.py", title="Legacy Briefing", icon="📰"),
            st.Page("pages/mission_control.py", title="Mission Control", icon="🎯"),
            st.Page("pages/developer_status.py", title="Developer Status", icon="🛠️"),
        ],
    }
)
navigation.run()
