import streamlit as st

from components.layout import page_header
from services.category_data import CategoryDataError, get_hot_categories

page_header("Market Themes", "Where market interest is flowing")

try:
    categories = get_hot_categories()
    leaders = categories.get("leaders", [])
    if not leaders:
        st.info("No category data is currently available.")
    else:
        for index, item in enumerate(leaders[:10], 1):
            change = float(item.get("change_24h") or 0)
            arrow = "▲" if change > 0 else "▼" if change < 0 else "►"
            st.markdown(
                f"<div class='theme-row'><span>{index}</span>"
                f"<strong>{item.get('name', 'Theme')}</strong>"
                f"<div>{arrow} {change:+.2f}% <small>24h</small></div></div>",
                unsafe_allow_html=True,
            )
except CategoryDataError as exc:
    st.error(str(exc))
