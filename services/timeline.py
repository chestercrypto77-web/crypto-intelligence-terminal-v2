from __future__ import annotations

from typing import Any


def conviction_timeline(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "Date": row.get("captured_at"),
            "Conviction": row.get("conviction_score"),
            "Opportunity": row.get("opportunity_score"),
            "Price": row.get("price"),
        }
        for row in history
        if row.get("captured_at")
    ]


def timeline_direction(history: list[dict[str, Any]]) -> str:
    scores = [
        float(row["conviction_score"])
        for row in history
        if row.get("conviction_score") is not None
    ]
    if len(scores) < 2:
        return "Building history"
    change = scores[-1] - scores[0]
    if change >= 8:
        return "🟢 Conviction building"
    if change <= -8:
        return "🔴 Conviction weakening"
    if change >= 2:
        return "🟢 Gradually improving"
    if change <= -2:
        return "🟠 Gradually cooling"
    return "🟡 Stable"
