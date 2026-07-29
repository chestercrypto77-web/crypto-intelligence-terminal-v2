import html

import streamlit as st


def metric_card(label: str, value: str, note: str = "") -> None:
    safe_label = html.escape(str(label))
    safe_value = html.escape(str(value))
    safe_note = html.escape(str(note))

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


def status_bar(version: str, updated_at: str, source: str) -> None:
    safe_version = html.escape(str(version))
    safe_updated_at = html.escape(str(updated_at))
    safe_source = html.escape(str(source))

    st.markdown(
        f"""
        <div class="terminal-status">
            <strong>Version {safe_version}</strong>
            &nbsp;·&nbsp; Updated {safe_updated_at}
            &nbsp;·&nbsp; Source: {safe_source}
        </div>
        """,
        unsafe_allow_html=True,
    )
