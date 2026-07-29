from __future__ import annotations

from statistics import mean
from typing import Any

from config import INTELLIGENCE_EVIDENCE_LIMIT


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def normalise_change(value: float | None, scale: float = 20.0) -> float:
    if value is None:
        return 50.0
    return clamp(50.0 + (float(value) / scale) * 50.0)


def liquidity_score(row: dict[str, Any]) -> float:
    ratio = float(row.get("volume_ratio") or 0)
    if ratio >= 0.30:
        return 95.0
    if ratio >= 0.15:
        return 85.0
    if ratio >= 0.08:
        return 72.0
    if ratio >= 0.04:
        return 58.0
    return 38.0


def risk_score(row: dict[str, Any]) -> float:
    return {"LOW": 90.0, "MEDIUM": 68.0, "HIGH": 35.0}.get(
        str(row.get("risk", "HIGH")).upper(),
        45.0,
    )


def health_breakdown(
    row: dict[str, Any],
    protocol: dict[str, Any] | None = None,
) -> dict[str, float]:
    momentum = mean(
        [
            normalise_change(row.get("change_1h"), 8.0),
            normalise_change(row.get("change_24h"), 18.0),
            normalise_change(row.get("change_7d"), 35.0),
        ]
    )
    liquidity = liquidity_score(row)
    fundamentals = float(row.get("conviction") or row.get("score") or 50)
    stability = risk_score(row)
    adoption = 50.0

    if protocol:
        tvl_changes = [
            protocol.get("change_1d"),
            protocol.get("change_7d"),
            protocol.get("change_1m"),
        ]
        available = [normalise_change(value, 25.0) for value in tvl_changes if value is not None]
        if available:
            adoption = mean(available)
            fundamentals = mean([fundamentals, adoption])

    return {
        "Fundamentals": round(clamp(fundamentals), 1),
        "Momentum": round(clamp(momentum), 1),
        "Liquidity": round(clamp(liquidity), 1),
        "Adoption / TVL": round(clamp(adoption), 1),
        "Risk Quality": round(clamp(stability), 1),
    }


def overall_health(scores: dict[str, float]) -> int:
    weights = {
        "Fundamentals": 0.28,
        "Momentum": 0.22,
        "Liquidity": 0.20,
        "Adoption / TVL": 0.15,
        "Risk Quality": 0.15,
    }
    return round(sum(scores[key] * weight for key, weight in weights.items()))


def build_evidence(
    row: dict[str, Any],
    protocol: dict[str, Any] | None = None,
) -> tuple[list[dict[str, str]], int]:
    evidence: list[dict[str, str]] = []

    conviction = float(row.get("conviction") or row.get("score") or 0)
    if conviction >= 80:
        evidence.append({"direction": "positive", "text": f"Conviction is high at {conviction:.0f}/100."})
    elif conviction >= 68:
        evidence.append({"direction": "positive", "text": f"Conviction is constructive at {conviction:.0f}/100."})
    else:
        evidence.append({"direction": "caution", "text": f"Conviction remains moderate at {conviction:.0f}/100."})

    for label, key in (("24-hour price", "change_24h"), ("7-day price", "change_7d")):
        value = row.get(key)
        if value is None:
            continue
        direction = "positive" if value > 1 else "negative" if value < -1 else "caution"
        evidence.append({"direction": direction, "text": f"{label} change is {float(value):+.1f}%."})

    ratio = float(row.get("volume_ratio") or 0)
    if ratio >= 0.15:
        evidence.append({"direction": "positive", "text": "Trading volume is strong relative to market capitalisation."})
    elif ratio < 0.05:
        evidence.append({"direction": "caution", "text": "Liquidity is comparatively thin and deserves monitoring."})
    else:
        evidence.append({"direction": "positive", "text": "Trading liquidity is within a healthy range."})

    if protocol:
        for label, key in (("24-hour TVL", "change_1d"), ("7-day TVL", "change_7d"), ("30-day TVL", "change_1m")):
            value = protocol.get(key)
            if value is None:
                continue
            direction = "positive" if value > 1 else "negative" if value < -1 else "caution"
            evidence.append({"direction": direction, "text": f"{label} change is {float(value):+.1f}%."})

    evidence = evidence[:INTELLIGENCE_EVIDENCE_LIMIT]
    data_points = len(evidence)
    agreement = sum(item["direction"] == "positive" for item in evidence)
    confidence = round(clamp(45 + data_points * 7 + agreement * 3, 45, 95))
    return evidence, confidence


def project_summary(
    row: dict[str, Any],
    protocol: dict[str, Any] | None = None,
) -> str:
    parts: list[str] = []
    change_7d = float(row.get("change_7d") or 0)
    ratio = float(row.get("volume_ratio") or 0)
    risk = str(row.get("risk", "HIGH")).lower()

    if change_7d >= 10:
        parts.append("Weekly momentum is accelerating")
    elif change_7d >= 2:
        parts.append("Weekly momentum remains constructive")
    elif change_7d <= -10:
        parts.append("Weekly momentum has weakened materially")
    else:
        parts.append("Weekly price momentum is broadly stable")

    if ratio >= 0.15:
        parts.append("trading participation is strong")
    elif ratio >= 0.06:
        parts.append("liquidity remains healthy")
    else:
        parts.append("liquidity is comparatively thin")

    if protocol and protocol.get("change_1m") is not None:
        monthly_tvl = float(protocol["change_1m"])
        if monthly_tvl >= 5:
            parts.append("and 30-day TVL is expanding")
        elif monthly_tvl <= -5:
            parts.append("while 30-day TVL is contracting")
        else:
            parts.append("with 30-day TVL holding steady")

    return (
        f"{parts[0]}, {parts[1]} {parts[2] if len(parts) > 2 else ''}. "
        f"The current scanner classifies relative risk as {risk}. "
        "Treat this as a research signal and confirm the underlying fundamentals before acting."
    ).replace("  ", " ")


def rotation_signal(category: dict[str, Any]) -> dict[str, Any]:
    change = float(category.get("change_24h") or 0)
    market_cap = float(category.get("market_cap") or 0)
    volume = float(category.get("volume_24h") or 0)
    turnover = volume / market_cap if market_cap else 0.0

    score = clamp(50 + change * 3 + min(turnover, 0.35) * 80)
    if score >= 82:
        label = "Strong inflow signal"
    elif score >= 68:
        label = "Positive rotation"
    elif score >= 58:
        label = "Early improvement"
    elif score >= 45:
        label = "Neutral"
    elif score >= 35:
        label = "Cooling"
    else:
        label = "Weakening"

    return {
        **category,
        "rotation_score": round(score, 1),
        "rotation_signal": label,
        "turnover": turnover,
    }


def capital_rotation(categories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [rotation_signal(category) for category in categories]
    rows.sort(key=lambda row: row["rotation_score"], reverse=True)
    return rows


def market_intelligence_summary(
    market: dict[str, Any],
    sentiment: dict[str, Any] | None,
    rotations: list[dict[str, Any]],
) -> str:
    change = float(market.get("market_cap_change_24h") or 0)
    if change >= 2:
        regime = "Market risk appetite is improving"
    elif change <= -2:
        regime = "Market risk appetite is weakening"
    else:
        regime = "Market conditions are broadly balanced"

    sentiment_text = ""
    if sentiment:
        sentiment_text = (
            f" Sentiment is {str(sentiment.get('classification', 'neutral')).lower()} "
            f"at {sentiment.get('value', '—')}."
        )

    leaders = ", ".join(row["name"] for row in rotations[:3]) if rotations else "no clear category"
    return (
        f"{regime}.{sentiment_text} The strongest current category rotation signals are "
        f"{leaders}. Rotation scores combine category price movement and turnover; "
        "they indicate relative activity rather than verified on-chain capital flows."
    )
