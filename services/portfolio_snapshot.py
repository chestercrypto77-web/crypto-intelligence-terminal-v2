from __future__ import annotations

from typing import Any


def enrich_with_portfolio(
    market_rows: list[dict[str, Any]],
    portfolio_profile: tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    """Combine current AUD market prices with the saved portfolio balances."""
    by_symbol = {
        str(row.get("symbol", "")).upper(): row
        for row in market_rows
    }
    enriched: list[dict[str, Any]] = []

    for asset in portfolio_profile:
        symbol = str(asset["symbol"]).upper()
        market_row = dict(by_symbol.get(symbol, {}))
        combined = {**asset, **market_row}

        # Portfolio facts always come from the user's saved profile.
        combined["symbol"] = symbol
        combined["name"] = asset["name"]
        combined["balance"] = float(asset.get("balance") or 0)
        combined["snapshot_value_aud"] = float(asset.get("snapshot_value_aud") or 0)
        combined["priority"] = int(asset.get("priority") or 3)
        combined["group"] = asset.get("group", "Holding")
        combined["conviction"] = asset.get("conviction", "Medium")
        combined["narrative"] = asset.get("narrative", "")

        price_aud = market_row.get("price")
        if price_aud is not None and float(price_aud) > 0:
            combined["price_aud"] = float(price_aud)
            combined["live_value_aud"] = float(price_aud) * combined["balance"]
            combined["valuation_source"] = "Live AUD estimate"
        else:
            combined["price_aud"] = None
            combined["live_value_aud"] = combined["snapshot_value_aud"]
            combined["valuation_source"] = "Recent screenshot"

        enriched.append(combined)

    total = sum(float(row.get("live_value_aud") or 0) for row in enriched)
    for row in enriched:
        value = float(row.get("live_value_aud") or 0)
        row["portfolio_weight"] = (value / total * 100) if total else 0.0

    return enriched


def portfolio_totals(rows: list[dict[str, Any]]) -> dict[str, float]:
    value = sum(float(row.get("live_value_aud") or 0) for row in rows)
    snapshot = sum(float(row.get("snapshot_value_aud") or 0) for row in rows)

    weighted_change = 0.0
    if value:
        weighted_change = sum(
            float(row.get("live_value_aud") or 0)
            * float(row.get("change_24h") or 0)
            for row in rows
        ) / value

    estimated_day_change = value * weighted_change / 100
    live_count = sum(1 for row in rows if row.get("valuation_source") == "Live AUD estimate")
    snapshot_count = len(rows) - live_count

    return {
        "value_aud": value,
        "snapshot_value_aud": snapshot,
        "weighted_change_24h": weighted_change,
        "estimated_day_change_aud": estimated_day_change,
        "live_price_count": live_count,
        "snapshot_fallback_count": snapshot_count,
    }


def portfolio_focus(rows: list[dict[str, Any]], limit: int = 4) -> list[dict[str, Any]]:
    ranked = sorted(
        rows,
        key=lambda row: (
            -(
                float(row.get("attention") or 0) * 0.55
                + min(float(row.get("portfolio_weight") or 0), 35) * 1.1
                + (12 if row.get("conviction") == "High" else 0)
            ),
            -float(row.get("live_value_aud") or 0),
        ),
    )
    return ranked[:limit]
