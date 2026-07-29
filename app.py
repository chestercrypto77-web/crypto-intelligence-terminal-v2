from pathlib import Path

import streamlit as st

from components.layout import load_css
from config import APP_NAME

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css(Path(".streamlit/style.css"))

navigation = st.navigation(
    {
        "Terminal": [
            st.Page("pages/dashboard.py", title="Dashboard", icon="🏠", default=True),
            st.Page("pages/developer_status.py", title="Developer Status", icon="🛠️"),
        ]
    }
)
navigation.run()
