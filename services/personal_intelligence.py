from __future__ import annotations

from typing import Any


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def attention_score(row: dict[str, Any], priority: int) -> float:
    change_1h = float(row.get("change_1h") or 0)
    change_24h = float(row.get("change_24h") or 0)
    change_7d = float(row.get("change_7d") or 0)
    volume_ratio = float(row.get("volume_ratio") or 0)
    conviction = float(row.get("conviction") or row.get("score") or 0)

    momentum = (
        min(abs(change_1h), 8) * 2.2
        + min(abs(change_24h), 35) * 1.25
        + min(abs(change_7d), 70) * 0.35
    )
    liquidity_signal = min(volume_ratio / 0.25, 1.0) * 18
    conviction_signal = conviction * 0.22
    personal_weight = {1: 20, 2: 10, 3: 3}.get(int(priority), 0)

    return round(clamp(momentum + liquidity_signal + conviction_signal + personal_weight), 1)


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


def momentum_state(change_1h: float, change_24h: float, change_7d: float) -> str:
    if change_24h >= 12 and change_1h > 0:
        return "Accelerating"
    if change_24h >= 5:
        return "Strong"
    if change_24h >= 2:
        return "Improving"
    if change_24h <= -12:
        return "Deteriorating"
    if change_24h <= -5:
        return "Weakening"
    if change_7d >= 8:
        return "Building"
    return "Stable"


def reason_text(row: dict[str, Any]) -> str:
    change_1h = float(row.get("change_1h") or 0)
    change_24h = float(row.get("change_24h") or 0)
    change_7d = float(row.get("change_7d") or 0)
    volume_ratio = float(row.get("volume_ratio") or 0)
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

    return "; ".join(reasons).capitalize() + "." if reasons else "No unusual market signal is currently detected."


def build_personal_market(
    scanner_rows: list[dict[str, Any]],
    conviction_rows: list[dict[str, Any]],
    configured_assets: tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    scanner_map = {str(row.get("symbol", "")).upper(): row for row in scanner_rows}
    conviction_map = {str(row.get("symbol", "")).upper(): row for row in conviction_rows}
    results: list[dict[str, Any]] = []

    for asset in configured_assets:
        symbol = str(asset["symbol"]).upper()
        source = conviction_map.get(symbol) or scanner_map.get(symbol)
        if not source:
            results.append({**asset, "available": False, "attention": 0, "attention_label": "Data unavailable"})
            continue

        row = {**source, **asset, "available": True}
        row["attention"] = attention_score(row, int(asset["priority"]))
        row["attention_label"] = attention_label(row["attention"])
        row["momentum_state"] = momentum_state(
            float(row.get("change_1h") or 0),
            float(row.get("change_24h") or 0),
            float(row.get("change_7d") or 0),
        )
        row["reason"] = reason_text(row)
        results.append(row)

    results.sort(key=lambda item: (not item.get("available", False), -float(item.get("attention") or 0), int(item["priority"])))
    return results


def market_summary(rows: list[dict[str, Any]]) -> str:
    available = [row for row in rows if row.get("available")]
    urgent = [row for row in available if float(row.get("attention") or 0) >= 70]
    gainers = sorted(available, key=lambda row: float(row.get("change_24h") or 0), reverse=True)
    losers = sorted(available, key=lambda row: float(row.get("change_24h") or 0))

    if not available:
        return "Personal market data is temporarily unavailable."

    lead = gainers[0]
    text = (
        f"{lead['name']} is showing the strongest 24-hour momentum in your market "
        f"at {float(lead.get('change_24h') or 0):+.1f}%. "
    )
    if urgent:
        text += f"{len(urgent)} project{'s' if len(urgent) != 1 else ''} currently require high attention. "
    if losers and float(losers[0].get("change_24h") or 0) <= -5:
        text += f"{losers[0]['name']} is the weakest monitored project at {float(losers[0].get('change_24h') or 0):+.1f}%. "
    text += "Attention scores prioritise your holdings and interests while still retaining broader Australian-market context."
    return text
