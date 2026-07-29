import streamlit as st

from components.theme import apply_theme
from config import APP_NAME

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

navigation = st.navigation(
    {
        "Intelligence": [
            st.Page("pages/mission_control.py", title="Mission Control", icon="🎯", default=True),
            st.Page("pages/market_briefing.py", title="Market Briefing", icon="🧠"),
            st.Page("pages/whats_hot.py", title="What's Hot", icon="🔥"),
            st.Page("pages/history.py", title="History", icon="📈"),
        ],
        "Research": [
            st.Page("pages/opportunity_scanner.py", title="Opportunity Scanner", icon="🚀"),
            st.Page("pages/conviction.py", title="Conviction Engine", icon="⭐"),
            st.Page("pages/defi_intelligence.py", title="DeFi Intelligence", icon="🌐"),
        ],
        "Portfolio": [
            st.Page("pages/portfolio.py", title="Portfolio", icon="💼"),
            st.Page("pages/watchlist.py", title="Watchlist", icon="👁️"),
        ],
        "System": [
            st.Page("pages/developer_status.py", title="Developer Status", icon="🛠️"),
        ],
    }
)
navigation.run()
