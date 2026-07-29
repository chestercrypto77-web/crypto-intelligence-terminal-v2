from datetime import datetime, timezone
from typing import Any

import streamlit as st

from config import DEFILLAMA_BASE_URL, DEFI_PROTOCOL_COUNT, MARKET_CACHE_SECONDS
from services.http_client import DataServiceError, get_json

DeFiDataError = DataServiceError


@st.cache_data(ttl=MARKET_CACHE_SECONDS, show_spinner=False)
def get_defi_protocols() -> dict[str, Any]:
    payload = get_json(f"{DEFILLAMA_BASE_URL}/protocols")
    if not isinstance(payload, list):
        raise DeFiDataError("DeFiLlama returned invalid protocol data.")

    rows = []
    for item in payload:
        tvl = item.get("tvl")
        if tvl is None or float(tvl or 0) <= 0:
            continue
        rows.append(
            {
                "name": item.get("name", "Unknown"),
                "symbol": str(item.get("symbol") or "").upper(),
                "category": item.get("category") or "Other",
                "chains": item.get("chains") or [],
                "tvl": float(tvl),
                "change_1d": item.get("change_1d"),
                "change_7d": item.get("change_7d"),
                "change_1m": item.get("change_1m"),
                "mcap": item.get("mcap"),
            }
        )

    rows.sort(key=lambda row: row["tvl"], reverse=True)
    leaders = rows[:DEFI_PROTOCOL_COUNT]

    category_totals: dict[str, float] = {}
    chain_counts: dict[str, int] = {}
    for row in leaders:
        category_totals[row["category"]] = category_totals.get(row["category"], 0.0) + row["tvl"]
        for chain in row["chains"]:
            chain_counts[str(chain)] = chain_counts.get(str(chain), 0) + 1

    categories = sorted(
        ({"category": name, "tvl": tvl} for name, tvl in category_totals.items()),
        key=lambda row: row["tvl"],
        reverse=True,
    )
    chains = sorted(
        ({"chain": name, "protocols": count} for name, count in chain_counts.items()),
        key=lambda row: row["protocols"],
        reverse=True,
    )

    return {
        "protocols": leaders,
        "categories": categories,
        "chains": chains,
        "total_tvl": sum(row["tvl"] for row in leaders),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source": "DeFiLlama",
    }


def clear_defi_cache() -> None:
    get_defi_protocols.clear()
