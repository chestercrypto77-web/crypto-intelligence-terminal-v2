from math import log10
from statistics import median
from typing import Any

from config import (
    SCANNER_MAX_ABS_24H_CHANGE,
    SCANNER_MIN_MARKET_CAP,
    SCANNER_MIN_VOLUME,
)


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def opportunity_score(coin: dict[str, Any]) -> float:
    market_cap = float(coin.get("market_cap") or 0)
    volume = float(coin.get("total_volume") or 0)
    change_1h = float(coin.get("price_change_percentage_1h_in_currency") or 0)
    change_24h = float(coin.get("price_change_percentage_24h_in_currency") or 0)
    change_7d = float(coin.get("price_change_percentage_7d_in_currency") or 0)
    volume_ratio = volume / market_cap if market_cap else 0

    momentum = (
        clamp(change_1h, -5, 5) / 5 * 8
        + clamp(change_24h, -20, 20) / 20 * 18
        + clamp(change_7d, -50, 50) / 50 * 16
    )
    liquidity = clamp(volume_ratio / 0.20, 0, 1) * 24
    size_quality = clamp((log10(max(market_cap, 1)) - 7.5) / 3.5, 0, 1) * 20
    base = 32 + momentum + liquidity + size_quality

    penalty = 0
    if abs(change_24h) > 40:
        penalty += 10
    if volume_ratio > 1.5:
        penalty += 8
    if market_cap < 100_000_000:
        penalty += 5

    return round(clamp(base - penalty, 0, 100), 1)


def risk_label(coin: dict[str, Any]) -> str:
    market_cap = float(coin.get("market_cap") or 0)
    volume = float(coin.get("total_volume") or 0)
    change_24h = abs(float(coin.get("price_change_percentage_24h_in_currency") or 0))
    volume_ratio = volume / market_cap if market_cap else 0

    points = 0
    if market_cap < 250_000_000:
        points += 2
    elif market_cap < 1_000_000_000:
        points += 1
    if change_24h > 25:
        points += 2
    elif change_24h > 12:
        points += 1
    if volume_ratio > 1:
        points += 1

    return "HIGH" if points >= 4 else "MEDIUM" if points >= 2 else "LOW"


def build_opportunity_list(coins: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = []
    for coin in coins:
        market_cap = float(coin.get("market_cap") or 0)
        volume = float(coin.get("total_volume") or 0)
        change_24h = float(coin.get("price_change_percentage_24h_in_currency") or 0)
        if market_cap < SCANNER_MIN_MARKET_CAP or volume < SCANNER_MIN_VOLUME:
            continue
        if abs(change_24h) > SCANNER_MAX_ABS_24H_CHANGE:
            continue

        row = {
            "name": coin.get("name", "Unknown"),
            "symbol": str(coin.get("symbol", "")).upper(),
            "rank": coin.get("market_cap_rank"),
            "price": coin.get("current_price"),
            "market_cap": market_cap,
            "volume": volume,
            "volume_ratio": volume / market_cap if market_cap else 0,
            "change_1h": coin.get("price_change_percentage_1h_in_currency"),
            "change_24h": change_24h,
            "change_7d": coin.get("price_change_percentage_7d_in_currency"),
            "score": opportunity_score(coin),
            "risk": risk_label(coin),
        }
        eligible.append(row)

    eligible.sort(key=lambda row: row["score"], reverse=True)
    scores = [row["score"] for row in eligible]
    return {
        "rows": eligible,
        "median_score": round(median(scores), 1) if scores else None,
        "high_conviction": sum(1 for row in eligible if row["score"] >= 75 and row["risk"] != "HIGH"),
        "market_count": len(eligible),
    }
