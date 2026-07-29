import streamlit as st
from components.cards import metric_card, status_bar
from components.layout import page_header
from config import APP_VERSION
from services.category_data import CategoryDataError, clear_category_cache, get_hot_categories
from services.formatting import compact_currency, signed_percentage, utc_time

page_header("What's Hot Now", f"Live narrative and category momentum · v{APP_VERSION}")

if st.button("Refresh categories"):
    clear_category_cache()
    st.rerun()

try:
    data = get_hot_categories()
    status_bar(APP_VERSION, utc_time(data["updated_at"]), data["source"])

    if data["leaders"]:
        top = data["leaders"][0]
        overview = st.columns(3)
        with overview[0]:
            metric_card("Leading Narrative", top["name"], signed_percentage(top["change_24h"]))
        with overview[1]:
            metric_card("Narratives Tracked", str(len(data["leaders"])), "Top eligible categories")
        with overview[2]:
            metric_card("Leader Volume", compact_currency(top["volume_24h"]), "24-hour category volume")

    st.subheader("Narrative leaders")
    table = [
        {
            "Rank": index,
            "Narrative": row["name"],
            "24h Change": signed_percentage(row["change_24h"]),
            "Market Cap": compact_currency(row["market_cap"]),
            "24h Volume": compact_currency(row["volume_24h"]),
            "Volume / Market Cap": f"{row['volume_24h'] / row['market_cap']:.3f}" if row["market_cap"] else "Unavailable",
        }
        for index, row in enumerate(data["leaders"], 1)
    ]
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.subheader("Weakest categories")
    laggards = [
        {
            "Narrative": row["name"],
            "24h Change": signed_percentage(row["change_24h"]),
            "Market Cap": compact_currency(row["market_cap"]),
        }
        for row in data["laggards"]
    ]
    st.dataframe(laggards, use_container_width=True, hide_index=True)

    st.caption("Category momentum can reverse quickly. Use it as a research signal, not a buy instruction.")

except CategoryDataError as exc:
    st.error(str(exc))
