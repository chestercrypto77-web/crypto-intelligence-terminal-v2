import html
import streamlit as st

from components.layout import page_header
from services.formatting import compact_currency
from services.market_data import MarketDataError, get_scanner_market
from services.scanner import build_opportunity_list
from services.volume_intelligence import build_volume_intelligence

page_header(
    "Volume Intelligence",
    "Which price moves are attracting real market participation?",
)

st.caption(
    "Relative volume compares current 24-hour turnover with the terminal's recent local baseline. "
    "The baseline becomes more reliable as the app collects snapshots."
)

try:
    scanner = build_opportunity_list(get_scanner_market())
    rows = build_volume_intelligence(scanner["rows"])

    filter_a, filter_b, filter_c = st.columns([1, 1, 1])
    with filter_a:
        activity = st.selectbox(
            "Activity",
            ["All", "Extreme", "High", "Elevated", "Normal", "Quiet", "Collecting baseline"],
        )
    with filter_b:
        interpretation = st.selectbox(
            "Price and volume",
            [
                "All",
                "Strong participation",
                "Price rising, volume unconfirmed",
                "Heavy selling",
                "Weakness on light participation",
                "Unusual activity",
                "Normal participation",
            ],
        )
    with filter_c:
        minimum_strength = st.slider("Minimum strength", 0, 100, 35, 5)

    filtered = [
        row for row in rows
        if (activity == "All" or row["volume_activity"] == activity)
        and (interpretation == "All" or row["price_volume_read"] == interpretation)
        and row["market_strength"] >= minimum_strength
    ]

    extreme = sum(1 for row in rows if row["volume_activity"] == "Extreme")
    high = sum(1 for row in rows if row["volume_activity"] in {"Extreme", "High"})
    strong = sum(1 for row in rows if row["price_volume_read"] == "Strong participation")
    selling = sum(1 for row in rows if row["price_volume_read"] == "Heavy selling")

    a, b, c, d = st.columns(4)
    a.metric("Extreme volume", extreme)
    b.metric("High activity", high)
    c.metric("Strong participation", strong)
    d.metric("Heavy selling", selling)

    st.subheader("Latest volume signals")

    if not filtered:
        st.info("No projects match the selected volume filters.")

    for row in filtered[:30]:
        rvol = row.get("rvol")
        rvol_text = "Collecting" if rvol is None else f"{rvol:.2f}×"
        one = row.get("volume_change_1h")
        four = row.get("volume_change_4h")
        twelve = row.get("volume_change_12h")
        price_change = float(row.get("change_24h") or 0)
        price_arrow = "▲" if price_change > 0.15 else "▼" if price_change < -0.15 else "►"

        def movement(value):
            if value is None:
                return "Collecting"
            arrow = "▲" if value > 1 else "▼" if value < -1 else "►"
            return f"{arrow} {value:+.1f}%"

        activity_class = row["volume_activity"].lower().replace(" ", "-")
        read_class = row["price_volume_read"].lower().replace(" ", "-").replace(",", "")

        st.markdown(
            f"<div class='volume-card'>"
            f"<div class='volume-head'>"
            f"<div><strong>{html.escape(row['symbol'])}</strong>"
            f"<span>{html.escape(row['name'])}</span></div>"
            f"<div class='activity-pill activity-{activity_class}'>{html.escape(row['volume_activity'])}</div>"
            f"</div>"
            f"<div class='volume-metrics'>"
            f"<div><span>24H VOLUME</span><strong>{compact_currency(row['volume_24h'])}</strong></div>"
            f"<div><span>RELATIVE VOLUME</span><strong>{rvol_text}</strong></div>"
            f"<div><span>1H VOLUME TREND</span><strong>{movement(one)}</strong></div>"
            f"<div><span>4H VOLUME TREND</span><strong>{movement(four)}</strong></div>"
            f"<div><span>12H VOLUME TREND</span><strong>{movement(twelve)}</strong></div>"
            f"<div><span>PRICE 24H</span><strong>{price_arrow} {price_change:+.2f}%</strong></div>"
            f"</div>"
            f"<div class='volume-foot'>"
            f"<div class='read-pill read-{read_class}'>{html.escape(row['price_volume_read'])}</div>"
            f"<div>Turnover {row['turnover_ratio'] * 100:.1f}% of market cap</div>"
            f"<div class='strength-score'>Strength {row['market_strength']}/100</div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with st.expander("How Volume Intelligence works"):
        st.write(
            "Relative volume compares the latest reported 24-hour volume with the median of recent "
            "snapshots. Price rising with high relative volume is labelled Strong participation. "
            "Price falling with high relative volume is labelled Heavy selling. Price changes without "
            "volume support receive a lower-confidence interpretation."
        )
        st.warning(
            "Volume can be distorted by exchange activity, token migrations, wash trading or one-off events. "
            "Use it as supporting evidence rather than a standalone investment instruction."
        )

except MarketDataError as exc:
    st.error(str(exc))
