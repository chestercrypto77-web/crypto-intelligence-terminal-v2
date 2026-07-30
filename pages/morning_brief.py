import html

import streamlit as st

import config
from components.layout import page_header
from portfolio_profile import PORTFOLIO_PROFILE, PROFILE_STATUS
from services.category_data import CategoryDataError, get_hot_categories
from services.conviction import build_conviction_list
from services.event_engine import run_event_detection
from services.event_store import recent_events
from services.formatting import signed_percentage, utc_time
from services.market_data import MarketDataError, get_market_snapshot, get_scanner_market
from services.morning_brief import market_mood, overnight_story, portfolio_health, risks
from services.personal_intelligence import build_personal_market
from services.portfolio_snapshot import enrich_with_portfolio, portfolio_focus, portfolio_totals
from services.scanner import build_opportunity_list

APP_VERSION = getattr(config, "APP_VERSION", "2.1.2")

page_header("Good morning, Mark", "Your calm five-minute crypto briefing")

try:
    market = get_market_snapshot()
    scanner = build_opportunity_list(get_scanner_market())

    try:
        categories = get_hot_categories()
        leader_change = (
            categories["leaders"][0]["change_24h"]
            if categories.get("leaders")
            else None
        )
    except CategoryDataError:
        leader_change = None

    held_symbols = {asset["symbol"] for asset in PORTFOLIO_PROFILE}
    conviction = build_conviction_list(
        scanner["rows"],
        leader_change,
        held_symbols,
    )
    intelligence_rows = build_personal_market(
        scanner["rows"],
        conviction,
        PORTFOLIO_PROFILE,
    )
    run_event_detection(intelligence_rows)

    rows = enrich_with_portfolio(intelligence_rows, PORTFOLIO_PROFILE)
    totals = portfolio_totals(rows)
    focus_rows = portfolio_focus(rows, 4)
    health, health_label = portfolio_health(rows)
    mood, mood_note = market_mood(market, rows)
    event_rows = recent_events(hours=24, limit=10, minimum_severity="High")
    risk_rows = risks(rows, 3)

    st.caption(
        f"Updated {utc_time(market['updated_at'])} · AUD pricing · {PROFILE_STATUS} · Release {APP_VERSION}"
    )

    value = totals["value_aud"]
    day_change = totals["estimated_day_change_aud"]
    day_percent = totals["weighted_change_24h"]

    a, b, c, d = st.columns(4)
    a.metric(
        "Estimated portfolio",
        f"${value:,.0f} AUD",
        f"${day_change:+,.0f} today",
    )
    b.metric("Portfolio move", f"{day_percent:+.2f}%", "Weighted 24-hour estimate")
    c.metric("Portfolio health", f"{health}/100", health_label)
    d.metric("Market mood", mood, f"{float(market.get('market_cap_change_24h') or 0):+.1f}%")

    if not event_rows and not risk_rows:
        st.markdown(
            """
            <div class="calm-banner">
              <div class="calm-icon">✓</div>
              <div>
                <div class="calm-title">Nothing urgent needs your attention</div>
                <div class="calm-copy">Your portfolio can be left alone today unless you want to explore the deeper research.</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="morning-story">
          <div class="morning-kicker">THE OVERNIGHT STORY</div>
          <div class="morning-headline">{html.escape(mood)} conditions</div>
          <div class="morning-copy">{html.escape(overnight_story(market, rows))}</div>
          <div class="morning-note">{html.escape(mood_note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("What matters to your portfolio today")
    columns = st.columns(4)
    for column, row in zip(columns, focus_rows):
        with column:
            change = float(row.get("change_24h") or 0)
            weight = float(row.get("portfolio_weight") or 0)
            value_aud = float(row.get("live_value_aud") or 0)
            attention = float(row.get("attention") or 0)
            marker = "🔥" if attention >= 85 else "⚡" if attention >= 70 else "●"
            st.markdown(
                f"""
                <div class="morning-asset">
                  <div class="morning-asset-top">
                    <span class="morning-asset-symbol">{marker} {html.escape(row["symbol"])}</span>
                    <span class="portfolio-weight">{weight:.1f}%</span>
                  </div>
                  <div class="morning-asset-change">{change:+.1f}%</div>
                  <div class="morning-asset-value">${value_aud:,.0f} AUD</div>
                  <div class="morning-asset-label">{html.escape(row.get("group", "Holding"))} · Attention {attention:.0f}</div>
                  <div class="morning-asset-reason">{html.escape(row.get("reason", ""))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    left, right = st.columns([1.15, 0.85])
    with left:
        st.subheader("Your holdings")
        for row in sorted(rows, key=lambda item: float(item.get("live_value_aud") or 0), reverse=True)[:7]:
            st.markdown(
                f"""
                <div class="holding-row">
                  <div>
                    <strong>{html.escape(row["name"])}</strong>
                    <span class="holding-symbol">{html.escape(row["symbol"])}</span>
                  </div>
                  <div class="holding-right">
                    <strong>${float(row.get("live_value_aud") or 0):,.0f}</strong>
                    <span class="holding-change">{float(row.get("change_24h") or 0):+.1f}%</span>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.subheader("Today’s attention")
        if event_rows:
            for event in event_rows[:3]:
                st.markdown(
                    f"""
                    <div class="attention-line">
                      <div class="attention-dot"></div>
                      <div>
                        <strong>{html.escape(event["symbol"])} · {html.escape(event["title"])}</strong>
                        <div>{html.escape(event["detail"])}</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No high-priority events were detected in the past 24 hours.")

        if risk_rows:
            st.markdown("**Risks to watch**")
            for row in risk_rows:
                st.markdown(
                    f'<div class="risk-line">⚠️ <strong>{html.escape(row["symbol"])}</strong> — '
                    f'{html.escape(row.get("reason", ""))}</div>',
                    unsafe_allow_html=True,
                )

    st.divider()

    with st.expander("View the complete portfolio"):
        st.dataframe(
            [
                {
                    "Project": row["name"],
                    "Balance": row["balance"],
                    "Est. value (AUD)": round(float(row["live_value_aud"]), 2),
                    "Weight": f'{float(row["portfolio_weight"]):.1f}%',
                    "24h": signed_percentage(row.get("change_24h")) if row.get("available") else "—",
                    "Group": row["group"],
                    "State": row.get("momentum_state", "Data unavailable"),
                }
                for row in sorted(
                    rows,
                    key=lambda item: float(item.get("live_value_aud") or 0),
                    reverse=True,
                )
            ],
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("View market details"):
        m1, m2, m3 = st.columns(3)
        m1.metric("BTC dominance", f"{float(market.get('btc_dominance') or 0):.1f}%")
        m2.metric("ETH dominance", f"{float(market.get('eth_dominance') or 0):.1f}%")
        m3.metric("High-priority events", len(event_rows))

    with st.expander("About these portfolio figures"):
        st.write(
            f"Balances are taken from the recent screenshot you supplied. "
            f"{int(totals['live_price_count'])} holdings currently use live AUD prices and "
            f"{int(totals['snapshot_fallback_count'])} use their recent screenshot value as a fallback. "
            "This is a portfolio-awareness tool, not tax or financial accounting software."
        )

except MarketDataError as exc:
    st.error(str(exc))
