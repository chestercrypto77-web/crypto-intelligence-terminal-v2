import streamlit as st


def page_header(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)
    st.divider()
