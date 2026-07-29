from typing import Any
from portfolio_config import PORTFOLIO


def build_portfolio_snapshot(coins: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows = []
    weighted_score = 0.0
    weighted_change = 0.0
    available_change_weight = 0.0

    for holding in PORTFOLIO:
        market = coins.get(holding["id"], {})
        weight = float(holding["weight"])
        change = market.get("change_24h")
        weighted_score += float(holding["score"]) * weight / 100.0
        if change is not None:
            weighted_change += float(change) * weight / 100.0
            available_change_weight += weight
        rows.append({
            **holding,
            "price": market.get("price"),
            "change_24h": change,
            "market_cap": market.get("market_cap"),
            "rank": market.get("rank"),
            "data_status": "Live" if market else "Unavailable",
        })

    strongest = max(rows, key=lambda row: row["score"])
    weakest = min(rows, key=lambda row: row["score"])
    high_risk_weight = sum(float(row["weight"]) for row in rows if str(row["risk"]).upper() == "HIGH")
    normalised_change = weighted_change * 100.0 / available_change_weight if available_change_weight else None

    return {
        "rows": rows,
        "score": round(weighted_score, 1),
        "change_24h": normalised_change,
        "risk": "HIGH" if high_risk_weight >= 20 else "MEDIUM",
        "strongest": strongest["name"],
        "weakest": weakest["name"],
        "high_risk_weight": high_risk_weight,
    }
