from pathlib import Path

import streamlit as st

from config import APP_NAME
from components.layout import load_css

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css(Path(".streamlit/style.css"))

pages = {
    "Terminal": [
        st.Page("pages/dashboard.py", title="Dashboard", icon="🏠", default=True),
        st.Page(
            "pages/developer_status.py",
            title="Developer Status",
            icon="🛠️",
        ),
    ]
}

navigation = st.navigation(pages)
navigation.run()
