import html
import streamlit as st

from components.layout import page_header
from services.market_data import MarketDataError, get_scanner_market
from services.momentum_intelligence import build_momentum_radar
from services.scanner import build_opportunity_list
from services.volume_intelligence import build_volume_intelligence

page_header("What's Moving?", "Where momentum is strengthening or fading right now")

try:
    scanner = build_opportunity_list(get_scanner_market())
    radar = build_momentum_radar(scanner["rows"])
    volume_map = {row["symbol"]: row for row in build_volume_intelligence(scanner["rows"])}

    tabs = st.tabs(["Accelerating", "Building", "Strong", "Weakening", "All"])

    def render(rows):
        if not rows:
            st.info("No projects currently match this state.")
            return
        for row in rows[:18]:
            moves = row["moves"]
            one = moves.get("1h")
            four = moves.get("4h")
            day = moves.get("24h")
            st.markdown(
                f"<div class='move-card'>"
                f"<div class='move-head'><div><strong>{html.escape(row['symbol'])}</strong>"
                f"<span>{html.escape(row['name'])}</span></div>"
                f"<div class='state-pill state-{row['status'].lower().replace(' ', '-')}'>{html.escape(row['status'])}</div></div>"
                f"<div class='move-times'>"
                f"<div><span>1H</span><strong>{row['arrows']['1h']} {'Collecting' if one is None else f'{one:+.2f}%'}</strong></div>"
                f"<div><span>4H</span><strong>{row['arrows']['4h']} {'Collecting' if four is None else f'{four:+.2f}%'}</strong></div>"
                f"<div><span>24H</span><strong>{row['arrows']['24h']} {'Collecting' if day is None else f'{day:+.2f}%'}</strong></div>"
                f"</div>"
                f"<div class='move-foot'><span>Volume {volume_map.get(row['symbol'], {}).get('volume_activity', 'Unknown')}</span>"
                f"<span>Strength {volume_map.get(row['symbol'], {}).get('market_strength', row['confidence'])}/100</span></div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    with tabs[0]:
        render([r for r in radar if r["status"] == "Accelerating"])
    with tabs[1]:
        render([r for r in radar if r["status"] == "Building"])
    with tabs[2]:
        render([r for r in radar if r["status"] == "Strong"])
    with tabs[3]:
        render([r for r in radar if r["status"] in {"Weakening", "Rolling over", "Under pressure"}])
    with tabs[4]:
        render(radar)

    with st.expander("How these signals work"):
        st.write(
            "The arrows show direction over labelled timeframes. The state combines short-term direction, "
            "multi-hour pace, trading turnover and the amount of local history available. These are monitoring "
            "signals rather than guaranteed forecasts."
        )
except MarketDataError as exc:
    st.error(str(exc))
