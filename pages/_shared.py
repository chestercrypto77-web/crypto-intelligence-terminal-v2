import streamlit as st
from services.market_data import get_market_rows
from intelligence.engine import build_portfolio
from ui.theme import apply_theme
def setup(title):
 st.set_page_config(page_title=title,page_icon="◈",layout="wide");apply_theme();rows,source,updated=get_market_rows();return build_portfolio(rows),source,updated
