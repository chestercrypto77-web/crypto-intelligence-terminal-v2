import streamlit as st

from components.cards import metric_card, section_label
from components.layout import page_header
from config import APP_VERSION
from portfolio_config import PORTFOLIO
from services.category_data import CategoryDataError, get_hot_categories
from services.conviction import build_conviction_list
from services.defillama import DeFiDataError, get_defi_protocols
from services.formatting import compact_currency, signed_percentage
from services.market_data import MarketDataError, get_scanner_market
from services.market_layers import research_reason, split_market_layers, tier_label
from services.momentum import (
    defi_momentum_rows,
    find_protocol_match,
    liquidity_status,
    price_momentum_row,
)
from services.scanner import build_opportunity_list

page_header(
    "Opportunity Radar",
    f"Curated emerging projects separated from the mainstream terminal · v{APP_VERSION}",
)

st.info(
    "This page identifies research candidates using market rank, liquidity, momentum, "
    "risk and conviction. It is not a recommendation to buy."
)

try:
    scanner = build_opportunity_list(get_scanner_market())

    try:
        categories = get_hot_categories()
        category_change = (
            categories["leaders"][0]["change_24h"]
            if categories.get("leaders")
            else None
        )
    except CategoryDataError:
        category_change = None

    portfolio_symbols = {str(item["symbol"]).upper() for item in PORTFOLIO}
    conviction = build_conviction_list(
        scanner["rows"],
        category_change,
        portfolio_symbols,
    )
    emerging = split_market_layers(conviction)["emerging"]

    try:
        protocols = get_defi_protocols()["protocols"]
    except DeFiDataError:
        protocols = []

    top = emerging[:15]
    cards = st.columns(4)
    with cards[0]:
        metric_card("Candidates", str(len(top)), "Highest-ranked emerging projects")
    with cards[1]:
        metric_card(
            "Emerging Leaders",
            str(sum(1 for row in top if tier_label(row) == "Emerging Leader")),
            "Highest-quality tier",
        )
    with cards[2]:
        metric_card(
            "Positive 7d",
            str(sum(1 for row in top if float(row.get("change_7d") or 0) > 0)),
            "Projects with positive weekly momentum",
        )
    with cards[3]:
        metric_card(
            "DeFi Coverage",
            str(sum(1 for row in top if find_protocol_match(row, protocols))),
            "Projects with matched TVL data",
        )

    section_label("Ranked research queue")
    table = [
        {
            "Project": row["name"],
            "Symbol": row["symbol"],
            "Tier": tier_label(row),
            "Rank": row["rank"],
            "Conviction": row["conviction"],
            "Opportunity": row["score"],
            "Risk": row["risk"],
            "Market Cap": compact_currency(row["market_cap"]),
            "24h": signed_percentage(row["change_24h"]),
            "7d": signed_percentage(row["change_7d"]),
            "Liquidity": liquidity_status(row),
            "Why it is here": research_reason(row),
        }
        for row in top
    ]
    st.dataframe(table, use_container_width=True, hide_index=True)

    if top:
        section_label("Project momentum")
        labels = [f"{row['name']} ({row['symbol']})" for row in top]
        selected_label = st.selectbox("Choose a project", labels)
        selected = top[labels.index(selected_label)]

        overview = st.columns(4)
        with overview[0]:
            metric_card("Conviction", f"{selected['conviction']}/100", tier_label(selected))
        with overview[1]:
            metric_card("Risk", selected["risk"], "Relative market risk")
        with overview[2]:
            metric_card("Liquidity", liquidity_status(selected), f"Ratio {selected['volume_ratio']:.2f}")
        with overview[3]:
            metric_card("Market Rank", f"#{selected['rank']}", compact_currency(selected["market_cap"]))

        momentum_rows = [price_momentum_row(selected)]
        protocol = find_protocol_match(selected, protocols)
        if protocol:
            momentum_rows.extend(defi_momentum_rows(protocol))
            st.caption(
                f"TVL data matched to {protocol['name']} via DeFiLlama. "
                "Price and trading data are supplied by CoinGecko."
            )
        else:
            st.caption(
                "No reliable DeFiLlama protocol match was found for this project. "
                "TVL is therefore not displayed rather than estimated."
            )

        st.dataframe(momentum_rows, use_container_width=True, hide_index=True)

        st.markdown(
            f'''
            <div class="briefing-panel">
              <strong>Why it is on the radar:</strong><br>
              {research_reason(selected)}<br><br>
              <strong>What to watch next:</strong><br>
              Confirm that weekly momentum persists, liquidity remains healthy and any
              available fundamental metrics improve alongside price.
            </div>
            ''',
            unsafe_allow_html=True,
        )

except MarketDataError as exc:
    st.error(str(exc))
