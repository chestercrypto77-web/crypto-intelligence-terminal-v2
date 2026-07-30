import html

import streamlit as st

import config
from components.layout import page_header
from services.market_data import MarketDataError, get_scanner_market
from services.momentum_intelligence import build_momentum_radar
from services.scanner import build_opportunity_list

APP_VERSION = getattr(config, "APP_VERSION", "2.2.0")

page_header(
    "Momentum Radar",
    "Near-real-time movement, acceleration and volume confirmation",
)

st.caption(
    "The radar refreshes from live market data and builds its own 15-minute history. "
    "The 15m, 4h and 12h readings become more reliable as snapshots accumulate."
)

try:
    scanner = build_opportunity_list(get_scanner_market())
    radar = build_momentum_radar(scanner["rows"])

    controls = st.columns([1.1, 1, 1])
    with controls[0]:
        group = st.selectbox(
            "Momentum state",
            ["All", "Accelerating", "Building", "Strong", "Stable", "Weakening", "Rolling over"],
        )
    with controls[1]:
        minimum_confidence = st.slider("Minimum confidence", 0, 100, 35, 5)
    with controls[2]:
        limit = st.selectbox("Projects shown", [10, 20, 40, 75], index=1)

    filtered = [
        row for row in radar
        if (group == "All" or row["status"] == group)
        and row["confidence"] >= minimum_confidence
    ][:limit]

    accelerating = sum(1 for row in radar if row["status"] == "Accelerating")
    building = sum(1 for row in radar if row["status"] == "Building")
    weakening = sum(1 for row in radar if row["status"] in {"Weakening", "Rolling over"})
    high_confidence = sum(1 for row in radar if row["confidence"] >= 70)

    a, b, c, d = st.columns(4)
    a.metric("Accelerating", accelerating)
    b.metric("Building", building)
    c.metric("Weakening", weakening)
    d.metric("High confidence", high_confidence)

    st.subheader("Latest movement")

    if not filtered:
        st.info("No projects match the selected momentum filters.")

    for row in filtered:
        moves = row["moves"]
        status_class = row["status"].lower().replace(" ", "-")
        cells = []
        for key in ("15m", "1h", "4h", "12h", "24h"):
            value = moves.get(key)
            display = "Collecting" if value is None else f"{value:+.2f}%"
            cells.append(
                f"<div class='momentum-cell'>"
                f"<div class='momentum-time'>{key}</div>"
                f"<div class='momentum-value'>{row['arrows'][key]} {display}</div>"
                f"</div>"
            )

        acceleration = row.get("acceleration")
        acceleration_text = (
            "Collecting history"
            if acceleration is None
            else f"{'▲' if acceleration > 0.15 else '▼' if acceleration < -0.15 else '►'} "
                 f"{acceleration:+.2f}% versus 4h pace"
        )
        volume_text = "Confirmed" if row["volume_confirmed"] else "Not confirmed"

        st.markdown(
            f"<div class='momentum-row'>"
            f"<div class='momentum-project'>"
            f"<div class='momentum-symbol'>{html.escape(row['symbol'])}</div>"
            f"<div class='momentum-name'>{html.escape(row['name'])}</div>"
            f"</div>"
            f"<div class='momentum-grid'>{''.join(cells)}</div>"
            f"<div class='momentum-summary'>"
            f"<div class='momentum-status status-{status_class}'>{html.escape(row['status'])}</div>"
            f"<div class='momentum-meta'>Acceleration: {html.escape(acceleration_text)}</div>"
            f"<div class='momentum-meta'>Volume: {volume_text}</div>"
            f"<div class='momentum-confidence'>Confidence {row['confidence']}%</div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with st.expander("How to interpret Momentum Radar"):
        st.write(
            "Arrows show direction over each labelled time frame. Accelerating means the latest "
            "movement is stronger than the recent multi-hour pace and is supported by trading activity. "
            "Building means positive momentum is developing but has not yet reached the stronger threshold. "
            "Rolling over means short-term direction has weakened relative to the recent trend."
        )
        st.warning(
            "These are probabilistic monitoring signals, not predictions or automatic buy and sell recommendations. "
            "Fast price movement can reverse without warning."
        )

except MarketDataError as exc:
    st.error(str(exc))
