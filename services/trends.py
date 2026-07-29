from statistics import mean
from typing import Any


def trend_label(values: list[float | None]) -> str:
    clean = [float(value) for value in values if value is not None]
    if len(clean) < 2:
        return "Insufficient history"

    change = clean[-1] - clean[0]
    if change >= 12:
        return "Strong Uptrend"
    if change >= 4:
        return "Improving"
    if change <= -12:
        return "Strong Downtrend"
    if change <= -4:
        return "Weakening"
    return "Neutral"


def history_summary(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    values = [float(row[field]) for row in rows if row.get(field) is not None]
    if not values:
        return {
            "current": None,
            "change": None,
            "average": None,
            "high": None,
            "low": None,
            "trend": "Insufficient history",
        }

    return {
        "current": values[-1],
        "change": values[-1] - values[0] if len(values) > 1 else 0.0,
        "average": mean(values),
        "high": max(values),
        "low": min(values),
        "trend": trend_label(values),
    }
