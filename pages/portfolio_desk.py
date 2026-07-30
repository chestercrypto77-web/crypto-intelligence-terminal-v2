import html
import streamlit as st

from components.layout import page_header
from portfolio_profile import PORTFOLIO_PROFILE, PROFILE_STATUS
from services.conviction import build_conviction_list
from services.market_data import MarketDataError, get_scanner_market
from services.personal_intelligence import build_personal_market
from services.portfolio_snapshot import enrich_with_portfolio, portfolio_totals
from services.scanner import build_opportunity_list

page_header("My Portfolio", "How your money is positioned and what is changing")

try:
    scanner = build_opportunity_list(get_scanner_market())
    symbols = {item["symbol"] for item in PORTFOLIO_PROFILE}
    conviction = build_conviction_list(scanner["rows"], None, symbols)
    intelligence = build_personal_market(scanner["rows"], conviction, PORTFOLIO_PROFILE)
    rows = enrich_with_portfolio(intelligence, PORTFOLIO_PROFILE)
    totals = portfolio_totals(rows)

    live_count = int(totals["live_price_count"])
    fallback_count = int(totals["snapshot_fallback_count"])

    a, b, c = st.columns(3)
    a.metric("Estimated value", f"${totals['value_aud']:,.0f} AUD",
             f"${totals['estimated_day_change_aud']:+,.0f} today")
    b.metric("Weighted 24h move", f"{totals['weighted_change_24h']:+.2f}%")
    c.metric("Pricing health", f"{live_count}/{len(rows)} live",
             "All live" if fallback_count == 0 else f"{fallback_count} fallback")

    if fallback_count:
        fallback_symbols = [row["symbol"] for row in rows if row["valuation_source"] != "Live AUD estimate"]
        st.warning("Live prices are unavailable for: " + ", ".join(fallback_symbols))

    st.subheader("Your positions")
    for row in sorted(rows, key=lambda item: float(item.get("live_value_aud") or 0), reverse=True):
        move = float(row.get("change_24h") or 0)
        arrow = "▲" if move > 0.15 else "▼" if move < -0.15 else "►"
        source = "LIVE" if row["valuation_source"] == "Live AUD estimate" else "SNAPSHOT"
        st.markdown(
            f"<div class='desk-row'>"
            f"<div><div class='desk-symbol'>{html.escape(row['symbol'])}</div>"
            f"<div class='desk-name'>{html.escape(row['name'])} · {html.escape(row['group'])}</div></div>"
            f"<div class='desk-value'>${float(row['live_value_aud']):,.0f}<span>AUD</span></div>"
            f"<div class='desk-move'>{arrow} {move:+.2f}%<span>24h</span></div>"
            f"<div class='source-pill source-{source.lower()}'>{source}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with st.expander("Balances and complete position data"):
        st.caption(PROFILE_STATUS)
        st.dataframe(
            [{
                "Asset": row["name"],
                "Symbol": row["symbol"],
                "Balance": row["balance"],
                "AUD value": round(float(row["live_value_aud"]), 2),
                "Weight": f"{float(row['portfolio_weight']):.1f}%",
                "1h": row.get("change_1h"),
                "24h": row.get("change_24h"),
                "7d": row.get("change_7d"),
                "Price source": row["valuation_source"],
            } for row in rows],
            use_container_width=True,
            hide_index=True,
        )
except MarketDataError as exc:
    st.error(str(exc))
