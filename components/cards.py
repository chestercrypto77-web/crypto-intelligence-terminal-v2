import html
import streamlit as st


def metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f'''
        <div class="terminal-card">
          <div class="terminal-card-label">{html.escape(str(label))}</div>
          <div class="terminal-card-value">{html.escape(str(value))}</div>
          <div class="terminal-card-note">{html.escape(str(note))}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def status_bar(version: str, updated_at: str, source: str) -> None:
    st.markdown(
        f'''
        <div class="terminal-status">
          <strong>v{html.escape(str(version))}</strong>
          &nbsp;·&nbsp; Updated {html.escape(str(updated_at))}
          &nbsp;·&nbsp; {html.escape(str(source))}
        </div>
        ''',
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    st.markdown(
        f'<div class="section-label">{html.escape(str(text))}</div>',
        unsafe_allow_html=True,
    )
