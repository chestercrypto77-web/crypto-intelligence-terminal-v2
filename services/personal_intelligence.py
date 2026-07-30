from __future__ import annotations

from math import isfinite
from typing import Any


def safe_float(value: Any, default: float = 0.0) -> float:
    """Convert API/profile values safely, including None, labels and malformed strings."""
    if value is None or isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        number = float(value)
        return number if isfinite(number) else default
    try:
        text = str(value).strip().replace(",", "")
        if not text:
            return default
        number = float(text)
        return number if isfinite(number) else default
    except (TypeError, ValueError, OverflowError):
        return default


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def numeric_conviction(row: dict[str, Any]) -> float:
    """Return conviction as a 0–100 numeric score."""
    explicit = row.get("conviction_score")
    if explicit is not None:
        return clamp(safe_float(explicit))

    score = row.get("score")
    if score is not None:
        return clamp(safe_float(score))

    value = row.get("conviction")
    labels = {
        "core": 95.0,
        "very high": 90.0,
        "high": 82.0,
        "medium": 65.0,
        "moderate": 60.0,
        "low": 40.0,
    }
    label = str(value or "").strip().lower()
    if label in labels:
        return labels[label]
    return clamp(safe_float(value))


def attention_score(row: dict[str, Any], priority: int) -> float:
    change_1h = safe_float(row.get("change_1h"))
    change_24h = safe_float(row.get("change_24h"))
    change_7d = safe_float(row.get("change_7d"))
    volume_ratio = safe_float(row.get("volume_ratio"))
    conviction = numeric_conviction(row)
    priority_value = int(safe_float(priority, 3))

    momentum = (
        min(abs(change_1h), 8) * 2.2
        + min(abs(change_24h), 35) * 1.25
        + min(abs(change_7d), 70) * 0.35
    )
    liquidity_signal = min(max(volume_ratio, 0) / 0.25, 1.0) * 18
    conviction_signal = conviction * 0.22
    personal_weight = {1: 20, 2: 10, 3: 3}.get(priority_value, 0)

    return round(
        clamp(momentum + liquidity_signal + conviction_signal + personal_weight),
        1,
    )


def attention_label(score: float) -> str:
    if score >= 85:
        return "Immediate attention"
    if score >= 70:
        return "High attention"
    if score >= 55:
        return "Worth reviewing"
    if score >= 40:
        return "Monitor"
    return "Quiet"


def momentum_state(change_1h: Any, change_24h: Any, change_7d: Any) -> str:
    one_hour = safe_float(change_1h)
    daily = safe_float(change_24h)
    weekly = safe_float(change_7d)

    if daily >= 12 and one_hour > 0:
        return "Accelerating"
    if daily >= 5:
        return "Strong"
    if daily >= 2:
        return "Improving"
    if daily <= -12:
        return "Deteriorating"
    if daily <= -5:
        return "Weakening"
    if weekly >= 8:
        return "Building"
    return "Stable"


def reason_text(row: dict[str, Any]) -> str:
    change_1h = safe_float(row.get("change_1h"))
    change_24h = safe_float(row.get("change_24h"))
    change_7d = safe_float(row.get("change_7d"))
    volume_ratio = safe_float(row.get("volume_ratio"))
    reasons: list[str] = []

    if change_24h >= 10:
        reasons.append(f"strong 24-hour momentum of {change_24h:+.1f}%")
    elif change_24h <= -10:
        reasons.append(f"sharp 24-hour weakness of {change_24h:+.1f}%")
    elif abs(change_24h) >= 4:
        reasons.append(f"meaningful 24-hour movement of {change_24h:+.1f}%")

    if change_1h >= 2:
        reasons.append(f"momentum is still building over the latest hour ({change_1h:+.1f}%)")
    elif change_1h <= -2:
        reasons.append(f"the latest hour has cooled ({change_1h:+.1f}%)")

    if volume_ratio >= 0.20:
        reasons.append("turnover is high relative to market capitalisation")
    elif volume_ratio >= 0.08:
        reasons.append("liquidity activity is elevated")

    if change_7d >= 15:
        reasons.append(f"the seven-day trend remains strong ({change_7d:+.1f}%)")
    elif change_7d <= -15:
        reasons.append(f"the seven-day trend remains weak ({change_7d:+.1f}%)")

    return (
        "; ".join(reasons).capitalize() + "."
        if reasons
        else "No unusual market signal is currently detected."
    )


def build_personal_market(
    scanner_rows: list[dict[str, Any]],
    conviction_rows: list[dict[str, Any]],
    configured_assets: tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    scanner_map = {
        str(row.get("symbol", "")).upper(): row
        for row in scanner_rows
        if row
    }
    conviction_map = {
        str(row.get("symbol", "")).upper(): row
        for row in conviction_rows
        if row
    }
    results: list[dict[str, Any]] = []

    for asset in configured_assets:
        symbol = str(asset.get("symbol", "")).upper()
        source = conviction_map.get(symbol) or scanner_map.get(symbol)

        if not source:
            results.append(
                {
                    **asset,
                    "symbol": symbol,
                    "available": False,
                    "attention": 0.0,
                    "attention_label": "Data unavailable",
                    "momentum_state": "Data unavailable",
                    "reason": "Live market data is temporarily unavailable.",
                }
            )
            continue

        # Market data comes first; portfolio identity and priority remain authoritative.
        row = {**source, **asset, "symbol": symbol, "available": True}
        priority = int(safe_float(asset.get("priority"), 3))
        row["conviction_score"] = numeric_conviction(row)
        row["attention"] = attention_score(row, priority)
        row["attention_label"] = attention_label(row["attention"])
        row["momentum_state"] = momentum_state(
            row.get("change_1h"),
            row.get("change_24h"),
            row.get("change_7d"),
        )
        row["reason"] = reason_text(row)
        results.append(row)

    results.sort(
        key=lambda item: (
            not item.get("available", False),
            -safe_float(item.get("attention")),
            int(safe_float(item.get("priority"), 3)),
        )
    )
    return results


def market_summary(rows: list[dict[str, Any]]) -> str:
    available = [row for row in rows if row.get("available")]
    if not available:
        return "Personal market data is temporarily unavailable."

    urgent = [row for row in available if safe_float(row.get("attention")) >= 70]
    gainers = sorted(
        available,
        key=lambda row: safe_float(row.get("change_24h")),
        reverse=True,
    )
    losers = sorted(
        available,
        key=lambda row: safe_float(row.get("change_24h")),
    )

    lead = gainers[0]
    text = (
        f"{lead['name']} is showing the strongest 24-hour momentum in your market "
        f"at {safe_float(lead.get('change_24h')):+.1f}%. "
    )
    if urgent:
        text += (
            f"{len(urgent)} project{'s' if len(urgent) != 1 else ''} "
            "currently require high attention. "
        )
    if losers and safe_float(losers[0].get("change_24h")) <= -5:
        text += (
            f"{losers[0]['name']} is the weakest monitored project at "
            f"{safe_float(losers[0].get('change_24h')):+.1f}%. "
        )
    text += (
        "Attention scores prioritise your holdings and interests while retaining "
        "broader Australian-market context."
    )
    return text
