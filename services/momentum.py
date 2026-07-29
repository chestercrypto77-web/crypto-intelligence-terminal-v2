from __future__ import annotations

from typing import Any


def _value(row: dict[str, Any], key: str) -> float:
    return float(row.get(key) or 0)


def arrow(value: float | None) -> str:
    if value is None:
        return "—"
    if value > 0.15:
        return f"↑ {value:.1f}%"
    if value < -0.15:
        return f"↓ {abs(value):.1f}%"
    return "→ 0.0%"


def momentum_status(short: float | None, medium: float | None, long: float | None) -> str:
    values = [value for value in (short, medium, long) if value is not None]
    if not values:
        return "Unavailable"

    positive = sum(value > 0.5 for value in values)
    negative = sum(value < -0.5 for value in values)

    if len(values) >= 3 and positive == 3 and values[0] > values[1] / 7:
        return "🟢 Accelerating"
    if positive >= 2:
        return "🟢 Strong"
    if negative >= 2:
        return "🔴 Weakening"
    if positive == 1 and negative == 0:
        return "🟢 Growing"
    if negative == 1 and positive == 0:
        return "🟠 Cooling"
    return "🟡 Stable"


def price_momentum_row(row: dict[str, Any]) -> dict[str, str]:
    one_hour = row.get("change_1h")
    one_day = row.get("change_24h")
    seven_day = row.get("change_7d")
    return {
        "Metric": "Price",
        "1h": arrow(one_hour),
        "24h": arrow(one_day),
        "7d": arrow(seven_day),
        "Trend": momentum_status(one_hour, one_day, seven_day),
    }


def liquidity_status(row: dict[str, Any]) -> str:
    ratio = _value(row, "volume_ratio")
    if ratio >= 0.30:
        return "🟢 Exceptional"
    if ratio >= 0.15:
        return "🟢 Strong"
    if ratio >= 0.06:
        return "🟡 Healthy"
    return "🟠 Thin"


def defi_momentum_rows(protocol: dict[str, Any]) -> list[dict[str, str]]:
    one_day = protocol.get("change_1d")
    seven_day = protocol.get("change_7d")
    month = protocol.get("change_1m")
    return [
        {
            "Metric": "TVL",
            "24h": arrow(one_day),
            "7d": arrow(seven_day),
            "30d": arrow(month),
            "Trend": momentum_status(one_day, seven_day, month),
        }
    ]


def find_protocol_match(
    project: dict[str, Any],
    protocols: list[dict[str, Any]],
) -> dict[str, Any] | None:
    symbol = str(project.get("symbol", "")).upper()
    name = str(project.get("name", "")).lower()
    for protocol in protocols:
        if symbol and symbol == str(protocol.get("symbol", "")).upper():
            return protocol
        if name and name == str(protocol.get("name", "")).lower():
            return protocol
    return None
