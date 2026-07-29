from typing import Any

import requests
import streamlit as st

from config import FEAR_GREED_URL, MARKET_CACHE_SECONDS, REQUEST_TIMEOUT_SECONDS


class FearGreedError(RuntimeError):
    pass


@st.cache_data(ttl=MARKET_CACHE_SECONDS, show_spinner=False)
def get_fear_greed() -> dict[str, Any]:
    try:
        response = requests.get(
            FEAR_GREED_URL,
            params={"limit": 1, "format": "json"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        item = payload["data"][0]
        return {
            "value": int(item["value"]),
            "classification": item["value_classification"],
        }
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as exc:
        raise FearGreedError("Fear & Greed data is temporarily unavailable.") from exc


def clear_fear_greed_cache() -> None:
    get_fear_greed.clear()
