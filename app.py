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
        "Terminal": [
            st.Page("pages/dashboard.py", title="Dashboard", icon="🏠", default=True),
            st.Page("pages/whats_hot.py", title="What's Hot", icon="🔥"),
            st.Page("pages/opportunity_scanner.py", title="Opportunity Scanner", icon="🚀"),
            st.Page("pages/portfolio.py", title="Portfolio", icon="💼"),
            st.Page("pages/developer_status.py", title="Developer Status", icon="🛠️"),
        ]
    }
)
navigation.run()
