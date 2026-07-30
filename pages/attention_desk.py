import html
import streamlit as st

from components.layout import page_header
from services.event_store import recent_events

page_header("Needs Attention", "Only the changes worth reviewing")

events = recent_events(hours=48, limit=50, minimum_severity="Medium")

if not events:
    st.success("Nothing important currently needs your attention.")
else:
    priority = [e for e in events if e["severity"] in {"Critical", "High"}]
    st.metric("Important changes", len(priority), f"{len(events)} total signals in 48h")
    for event in events[:15]:
        st.markdown(
            f"<div class='attention-card'>"
            f"<div class='attention-top'><strong>{html.escape(event['symbol'])}</strong>"
            f"<span>{html.escape(event['severity'])}</span></div>"
            f"<div class='attention-title'>{html.escape(event['title'])}</div>"
            f"<div class='attention-copy'>{html.escape(event['detail'])}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

with st.expander("Full technical event feed"):
    st.page_link("pages/events.py", label="Open legacy Event Detection")
