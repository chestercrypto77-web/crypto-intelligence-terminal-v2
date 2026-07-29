from __future__ import annotations

import html
from typing import Any

import streamlit as st


def health_bars(scores: dict[str, float]) -> None:
    rows = []
    for label, raw_value in scores.items():
        value = max(0.0, min(100.0, float(raw_value)))
        rows.append(
            f'''
            <div class="health-row">
              <div>{html.escape(label)}</div>
              <div class="health-track">
                <div class="health-fill" style="width:{value:.0f}%"></div>
              </div>
              <div><strong>{value:.0f}</strong></div>
            </div>
            '''
        )
    st.markdown("".join(rows), unsafe_allow_html=True)


def evidence_panel(evidence: list[dict[str, Any]], confidence: int) -> None:
    items = []
    for item in evidence:
        symbol = "✓" if item.get("direction") == "positive" else "!" if item.get("direction") == "caution" else "↓"
        items.append(
            f'<div class="evidence-item"><strong>{symbol}</strong> '
            f'{html.escape(str(item.get("text", "")))}</div>'
        )
    body = "".join(items) or '<div class="evidence-item">No sufficient evidence is available yet.</div>'
    st.markdown(
        f'''
        <div class="evidence-panel">
          <strong>Why this conclusion?</strong>
          {body}
          <div style="margin-top:12px"><strong>Evidence confidence: {confidence}%</strong></div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def flow_badge(signal: str) -> str:
    mapping = {
        "Strong inflow signal": "▲▲▲",
        "Positive rotation": "▲▲",
        "Early improvement": "▲",
        "Neutral": "→",
        "Cooling": "▼",
        "Weakening": "▼▼",
    }
    return mapping.get(signal, "→")
