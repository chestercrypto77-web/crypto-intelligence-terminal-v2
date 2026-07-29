import sys
from pathlib import Path
import requests
import streamlit as st

from components.layout import page_header
from config import APP_VERSION, COINGECKO_BASE_URL, FEAR_GREED_URL, REQUEST_TIMEOUT_SECONDS

page_header("Developer Status", f"System checks · v{APP_VERSION}")

required = {
    "Pages folder": Path("pages").is_dir(),
    "Components folder": Path("components").is_dir(),
    "Services folder": Path("services").is_dir(),
    "Configuration": Path("config.py").is_file(),
    "Portfolio configuration": Path("portfolio_config.py").is_file(),
    "What's Hot page": Path("pages/whats_hot.py").is_file(),
    "Opportunity Scanner page": Path("pages/opportunity_scanner.py").is_file(),
    "Embedded theme": Path("components/theme.py").is_file(),
}

for label, passed in required.items():
    if passed:
        st.success(f"✅ {label} found")
    else:
        st.error(f"❌ {label} missing")

left, right = st.columns(2)
with left:
    if st.button("Test CoinGecko"):
        try:
            response = requests.get(f"{COINGECKO_BASE_URL}/ping", timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            st.success("✅ CoinGecko connection successful")
        except requests.RequestException as exc:
            st.error(f"❌ CoinGecko failed: {exc}")
with right:
    if st.button("Test Fear & Greed"):
        try:
            response = requests.get(FEAR_GREED_URL, params={"limit": 1}, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            st.success("✅ Fear & Greed connection successful")
        except requests.RequestException as exc:
            st.error(f"❌ Fear & Greed failed: {exc}")

st.caption(f"Python {sys.version.split()[0]}")
st.caption(f"Streamlit {st.__version__}")
