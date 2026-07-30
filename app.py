import streamlit as st
from config import APP_NAME,APP_VERSION
from services.market_data import get_market_rows
from intelligence.engine import build_portfolio
from ui.theme import apply_theme
from ui.components import page_header
st.set_page_config(page_title=APP_NAME,page_icon="◈",layout="wide",initial_sidebar_state="expanded");apply_theme();rows,source,updated=get_market_rows();portfolio=build_portfolio(rows)
st.sidebar.markdown("## ◈ Intelligence Desk");st.sidebar.caption(f"Version {APP_VERSION}");st.sidebar.markdown("---");st.sidebar.markdown("**Daily Desk**");st.sidebar.page_link("app.py",label="Today",icon="☀️");st.sidebar.page_link("pages/1_Portfolio.py",label="Portfolio",icon="💼");st.sidebar.page_link("pages/2_Markets.py",label="Markets",icon="🌍");st.sidebar.page_link("pages/3_Watch.py",label="Watch",icon="⚡");st.sidebar.markdown("**Research**");st.sidebar.page_link("pages/4_Research.py",label="Research",icon="🧠");st.sidebar.markdown("---");st.sidebar.caption(f"{source} · refreshes every 5 minutes")
page_header("Good morning, Mark","Your portfolio briefing in under five minutes.");exec(open("pages/_today_content.py",encoding="utf-8").read())
