from typing import Any
import streamlit as st

from config import FEAR_GREED_URL, MARKET_CACHE_SECONDS
from services.http_client import DataServiceError, get_json

FearGreedError = DataServiceError


@st.cache_data(ttl=MARKET_CACHE_SECONDS, show_spinner=False)
def get_fear_greed() -> dict[str, Any]:
    try:
        item = get_json(FEAR_GREED_URL, {"limit": 1, "format": "json"})["data"][0]
        return {"value": int(item["value"]), "classification": str(item["value_classification"])}
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise FearGreedError("Fear & Greed returned incomplete data.") from exc


def clear_fear_greed_cache() -> None:
    get_fear_greed.clear()
