from datetime import datetime, timezone
from typing import Any
import streamlit as st

from config import COINGECKO_BASE_URL, HOT_CATEGORY_COUNT, MARKET_CACHE_SECONDS
from services.http_client import DataServiceError, get_json

CategoryDataError = DataServiceError


@st.cache_data(ttl=MARKET_CACHE_SECONDS, show_spinner=False)
def get_hot_categories() -> dict[str, Any]:
    payload = get_json(f"{COINGECKO_BASE_URL}/coins/categories")
    if not isinstance(payload, list):
        raise CategoryDataError("CoinGecko returned invalid category data.")

    rows = []
    excluded = ("stablecoin", "wrapped", "bridged", "tokenized stock")
    for item in payload:
        name = str(item.get("name", ""))
        change = item.get("market_cap_change_24h")
        market_cap = item.get("market_cap")
        volume = item.get("volume_24h")
        if change is None or market_cap is None or volume is None:
            continue
        if any(term in name.lower() for term in excluded):
            continue
        rows.append(
            {
                "id": item.get("id"),
                "name": name,
                "change_24h": float(change),
                "market_cap": float(market_cap),
                "volume_24h": float(volume),
                "top_3_coins": item.get("top_3_coins", []),
            }
        )

    rows.sort(key=lambda row: row["change_24h"], reverse=True)
    return {
        "leaders": rows[:HOT_CATEGORY_COUNT],
        "laggards": list(reversed(rows[-5:])),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source": "CoinGecko Categories",
    }


def clear_category_cache() -> None:
    get_hot_categories.clear()
