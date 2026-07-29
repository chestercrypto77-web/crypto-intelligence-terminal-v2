import streamlit as st

from components.cards import metric_card, status_bar
from components.layout import page_header
from config import APP_VERSION
from services.defillama import DeFiDataError, clear_defi_cache, get_defi_protocols
from services.formatting import compact_currency, signed_percentage, utc_time

page_header("DeFi Intelligence", f"Protocol TVL and sector leadership · v{APP_VERSION}")

if st.button("Refresh DeFi data"):
    clear_defi_cache()
    st.rerun()

try:
    data = get_defi_protocols()
    status_bar(APP_VERSION, utc_time(data["updated_at"]), data["source"])

    top_protocol = data["protocols"][0] if data["protocols"] else None
    top_category = data["categories"][0] if data["categories"] else None

    summary = st.columns(4)
    with summary[0]:
        metric_card("Tracked TVL", compact_currency(data["total_tvl"]), "Top eligible protocols")
    with summary[1]:
        metric_card("Protocols", str(len(data["protocols"])), "Ranked by current TVL")
    with summary[2]:
        metric_card(
            "TVL Leader",
            top_protocol["name"] if top_protocol else "Unavailable",
            compact_currency(top_protocol["tvl"]) if top_protocol else "",
        )
    with summary[3]:
        metric_card(
            "Largest Sector",
            top_category["category"] if top_category else "Unavailable",
            compact_currency(top_category["tvl"]) if top_category else "",
        )

    st.subheader("Protocol leaders")
    protocol_rows = [
        {
            "Rank": index,
            "Protocol": row["name"],
            "Symbol": row["symbol"] or "—",
            "Category": row["category"],
            "TVL": compact_currency(row["tvl"]),
            "1d": signed_percentage(row["change_1d"]),
            "7d": signed_percentage(row["change_7d"]),
            "1m": signed_percentage(row["change_1m"]),
            "Chains": ", ".join(row["chains"][:4]) if row["chains"] else "—",
        }
        for index, row in enumerate(data["protocols"][:30], 1)
    ]
    st.dataframe(protocol_rows, use_container_width=True, hide_index=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Top DeFi sectors")
        st.dataframe(
            [
                {"Sector": row["category"], "TVL": compact_currency(row["tvl"])}
                for row in data["categories"][:15]
            ],
            use_container_width=True,
            hide_index=True,
        )
    with right:
        st.subheader("Most represented chains")
        st.dataframe(
            [
                {"Chain": row["chain"], "Top protocols represented": row["protocols"]}
                for row in data["chains"][:15]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "TVL is one research input and does not by itself measure protocol safety, "
        "revenue quality or token value."
    )

except DeFiDataError as exc:
    st.error(str(exc))
