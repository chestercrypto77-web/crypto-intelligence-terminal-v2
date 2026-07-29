from typing import Any


def conviction_score(
    opportunity: float,
    risk: str,
    narrative_change: float | None,
    portfolio_overlap: bool,
) -> float:
    score = float(opportunity) * 0.72

    risk_adjustment = {"LOW": 12.0, "MEDIUM": 4.0, "HIGH": -12.0}.get(risk, 0.0)
    score += risk_adjustment

    if narrative_change is not None:
        score += max(-8.0, min(float(narrative_change), 8.0)) * 1.25

    if portfolio_overlap:
        score -= 4.0

    return round(max(0.0, min(score, 100.0)), 1)


def conviction_label(score: float) -> str:
    if score >= 80:
        return "HIGH"
    if score >= 65:
        return "MEDIUM"
    return "WATCH"


def build_conviction_list(
    scanner_rows: list[dict[str, Any]],
    category_change: float | None,
    portfolio_symbols: set[str],
) -> list[dict[str, Any]]:
    rows = []
    for item in scanner_rows:
        symbol = str(item.get("symbol", "")).upper()
        score = conviction_score(
            opportunity=float(item.get("score", 0)),
            risk=str(item.get("risk", "HIGH")),
            narrative_change=category_change,
            portfolio_overlap=symbol in portfolio_symbols,
        )
        rows.append(
            {
                **item,
                "conviction": score,
                "conviction_label": conviction_label(score),
                "portfolio_overlap": symbol in portfolio_symbols,
            }
        )
    rows.sort(key=lambda row: row["conviction"], reverse=True)
    return rows
