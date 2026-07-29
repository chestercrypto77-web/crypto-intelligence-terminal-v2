import sys
from pathlib import Path

import streamlit as st

from components.layout import page_header

page_header("Developer Status", "Foundation checks · v0.1.0")

checks = {
    "Streamlit loaded": True,
    "Pages folder found": Path("pages").is_dir(),
    "Components folder found": Path("components").is_dir(),
    "Services folder found": Path("services").is_dir(),
}

for label, passed in checks.items():
    if passed:
        st.success(f"✅ {label}")
    else:
        st.error(f"❌ {label}")

st.caption(f"Python {sys.version.split()[0]}")
st.caption(f"Streamlit {st.__version__}")
