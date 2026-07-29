from __future__ import annotations

from typing import Any

from config import (
    CORE_ASSET_SYMBOLS,
    CORE_MAX_MARKET_RANK,
    EMERGING_MAX_MARKET_CAP,
    EMERGING_MAX_MARKET_RANK,
    EMERGING_MIN_MARKET_CAP,
    EMERGING_MIN_MARKET_RANK,
    EMERGING_MIN_VOLUME,
)


def is_core_asset(row: dict[str, Any]) -> bool:
    symbol = str(row.get("symbol", "")).upper()
    rank = int(row.get("rank") or 9999)
    return symbol in CORE_ASSET_SYMBOLS or rank <= CORE_MAX_MARKET_RANK


def is_emerging_asset(row: dict[str, Any]) -> bool:
    rank = int(row.get("rank") or 9999)
    market_cap = float(row.get("market_cap") or 0)
    volume = float(row.get("volume") or 0)
    return (
        EMERGING_MIN_MARKET_RANK <= rank <= EMERGING_MAX_MARKET_RANK
        and EMERGING_MIN_MARKET_CAP <= market_cap <= EMERGING_MAX_MARKET_CAP
        and volume >= EMERGING_MIN_VOLUME
    )


def split_market_layers(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    core = [row for row in rows if is_core_asset(row)]
    emerging = [row for row in rows if is_emerging_asset(row)]
    core.sort(key=lambda row: (row.get("rank") or 9999, -float(row.get("conviction") or 0)))
    emerging.sort(key=lambda row: float(row.get("conviction") or 0), reverse=True)
    return {"core": core, "emerging": emerging}


def research_reason(row: dict[str, Any]) -> str:
    reasons: list[str] = []
    change_7d = float(row.get("change_7d") or 0)
    change_24h = float(row.get("change_24h") or 0)
    volume_ratio = float(row.get("volume_ratio") or 0)
    score = float(row.get("conviction") or row.get("score") or 0)
    risk = str(row.get("risk", "HIGH"))

    if score >= 80:
        reasons.append("high conviction")
    elif score >= 68:
        reasons.append("improving conviction")

    if change_7d >= 12:
        reasons.append("strong 7-day momentum")
    elif change_7d >= 4:
        reasons.append("positive weekly momentum")

    if volume_ratio >= 0.20:
        reasons.append("heavy trading activity")
    elif volume_ratio >= 0.08:
        reasons.append("healthy liquidity")

    if change_24h < -5 and change_7d > 5:
        reasons.append("constructive pullback")

    if risk == "LOW":
        reasons.append("lower relative risk")
    elif risk == "MEDIUM":
        reasons.append("manageable risk profile")

    if not reasons:
        reasons.append("balanced momentum and liquidity signals")

    sentence = ", ".join(reasons[:3])
    return sentence[:1].upper() + sentence[1:] + "."


def tier_label(row: dict[str, Any]) -> str:
    conviction = float(row.get("conviction") or 0)
    risk = str(row.get("risk", "HIGH"))
    if conviction >= 82 and risk != "HIGH":
        return "Emerging Leader"
    if conviction >= 70 and risk != "HIGH":
        return "Research Queue"
    return "Early Watch"
