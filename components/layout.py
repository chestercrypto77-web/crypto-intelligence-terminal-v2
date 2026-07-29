from pathlib import Path

import streamlit as st


def load_css(path: Path) -> None:
    if not path.exists():
        return

    css = path.read_text(encoding="utf-8")

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)
    st.divider()
