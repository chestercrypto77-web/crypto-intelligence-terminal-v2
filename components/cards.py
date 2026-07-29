import html

import streamlit as st


def metric_card(label: str, value: str, note: str = "") -> None:
    safe_label = html.escape(label)
    safe_value = html.escape(value)
    safe_note = html.escape(note)
    st.markdown(
        f"""
        <div class="terminal-card">
            <div class="terminal-card-label">{safe_label}</div>
            <div class="terminal-card-value">{safe_value}</div>
            <div class="terminal-card-note">{safe_note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
