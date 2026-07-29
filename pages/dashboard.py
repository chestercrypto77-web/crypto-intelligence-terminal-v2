import streamlit as st

from components.layout import page_header
from components.cards import metric_card

page_header(
    "Crypto Intelligence Terminal V2",
    "Clean foundation release · v0.1.0",
)

cols = st.columns(4)
with cols[0]:
    metric_card("Market Health", "Coming next", "Core data migration")
with cols[1]:
    metric_card("Portfolio", "Coming next", "Portfolio engine migration")
with cols[2]:
    metric_card("Opportunities", "Coming next", "Scanner migration")
with cols[3]:
    metric_card("Alerts", "Coming next", "Alert engine migration")

st.subheader("Foundation status")
st.success("Navigation, layout, theme and reusable components are working.")
st.info("Version 1 remains untouched while Version 2 is built here in controlled releases.")
