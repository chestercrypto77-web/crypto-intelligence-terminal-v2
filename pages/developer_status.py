import sys
from pathlib import Path

import requests
import streamlit as st

from components.layout import page_header
from config import (
    APP_VERSION,
    COINGECKO_BASE_URL,
    DEFILLAMA_BASE_URL,
    FEAR_GREED_URL,
    HISTORY_DATABASE_PATH,
    REQUEST_TIMEOUT_SECONDS,
)
from services.history_store import snapshot_count

page_header("Developer Status", f"System checks · v{APP_VERSION}")

required = {
    "Pages folder": Path("pages").is_dir(),
    "Components folder": Path("components").is_dir(),
    "Services folder": Path("services").is_dir(),
    "Configuration": Path("config.py").is_file(),
    "Mission Control page": Path("pages/mission_control.py").is_file(),
    "Opportunity Radar page": Path("pages/opportunity_radar.py").is_file(),
    "Market layer service": Path("services/market_layers.py").is_file(),
    "Momentum service": Path("services/momentum.py").is_file(),
    "History page": Path("pages/history.py").is_file(),
    "Watchlist page": Path("pages/watchlist.py").is_file(),
    "History service": Path("services/history_store.py").is_file(),
    "Snapshot engine": Path("services/snapshot_engine.py").is_file(),
    "Embedded theme": Path("components/theme.py").is_file(),
}

for label, passed in required.items():
    if passed:
        st.success(f"✅ {label} found")
    else:
        st.error(f"❌ {label} missing")

counts = snapshot_count()
st.info(
    f"History database: {HISTORY_DATABASE_PATH} · "
    f"{counts['market']} market snapshots · {counts['assets']} asset records"
)

columns = st.columns(3)
tests = (
    ("CoinGecko", f"{COINGECKO_BASE_URL}/ping", None),
    ("Fear & Greed", FEAR_GREED_URL, {"limit": 1}),
    ("DeFiLlama", f"{DEFILLAMA_BASE_URL}/protocols", None),
)

for column, (label, url, params) in zip(columns, tests):
    with column:
        if st.button(f"Test {label}"):
            try:
                response = requests.get(
                    url,
                    params=params,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
                response.raise_for_status()
                st.success(f"✅ {label} connection successful")
            except requests.RequestException as exc:
                st.error(f"❌ {label} failed: {exc}")

st.caption(f"Python {sys.version.split()[0]}")
st.caption(f"Streamlit {st.__version__}")
