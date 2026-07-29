import streamlit as st

st.set_page_config(
    page_title="Crypto Intelligence Terminal V2",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = {
    "Terminal": [
        st.Page("pages/dashboard.py", title="Dashboard", icon="🏠", default=True),
        st.Page("pages/developer_status.py", title="Developer Status", icon="🛠️"),
    ]
}

navigation = st.navigation(pages)
navigation.run()
