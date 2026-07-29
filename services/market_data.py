from datetime import datetime, timezone
from typing import Any
import streamlit as st

from config import (
    COINGECKO_BASE_URL,
    DISPLAY_CURRENCY,
    MARKET_CACHE_SECONDS,
    SCANNER_MARKET_COUNT,
    TRACKED_COINS,
)
from services.http_client import DataServiceError, get_json

MarketDataError = DataServiceError


@st.cache_data(ttl=MARKET_CACHE_SECONDS, show_spinner=False)
def get_market_snapshot() -> dict[str, Any]:
    global_payload = get_json(f"{COINGECKO_BASE_URL}/global")
    coin_payload = get_json(
        f"{COINGECKO_BASE_URL}/coins/markets",
        {
            "vs_currency": DISPLAY_CURRENCY,
            "ids": ",".join(TRACKED_COINS),
            "order": "market_cap_desc",
            "sparkline": "false",
            "price_change_percentage": "24h",
        },
    )
    global_data = global_payload.get("data", {})
    market_caps = global_data.get("total_market_cap", {})
    volumes = global_data.get("total_volume", {})
    dominance = global_data.get("market_cap_percentage", {})
    if DISPLAY_CURRENCY not in market_caps or DISPLAY_CURRENCY not in volumes:
        raise MarketDataError("CoinGecko returned incomplete global market data.")

    coins = {
        item["id"]: {
            "name": item.get("name", item["id"].title()),
            "symbol": item.get("symbol", "").upper(),
            "price": item.get("current_price"),
            "change_24h": item.get("price_change_percentage_24h"),
            "market_cap": item.get("market_cap"),
            "volume": item.get("total_volume"),
            "rank": item.get("market_cap_rank"),
        }
        for item in coin_payload if item.get("id")
    }
    return {
        "total_market_cap": market_caps[DISPLAY_CURRENCY],
        "total_volume": volumes[DISPLAY_CURRENCY],
        "market_cap_change_24h": global_data.get("market_cap_change_percentage_24h_usd"),
        "btc_dominance": dominance.get("btc"),
        "eth_dominance": dominance.get("eth"),
        "coins": coins,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source": "CoinGecko",
    }


@st.cache_data(ttl=MARKET_CACHE_SECONDS, show_spinner=False)
def get_scanner_market() -> list[dict[str, Any]]:
    payload = get_json(
        f"{COINGECKO_BASE_URL}/coins/markets",
        {
            "vs_currency": DISPLAY_CURRENCY,
            "order": "market_cap_desc",
            "per_page": SCANNER_MARKET_COUNT,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "1h,24h,7d",
        },
    )
    if not isinstance(payload, list):
        raise MarketDataError("CoinGecko returned invalid scanner market data.")
    return payload


def clear_market_cache() -> None:
    get_market_snapshot.clear()
    get_scanner_market.clear()
