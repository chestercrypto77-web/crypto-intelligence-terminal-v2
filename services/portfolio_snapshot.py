from __future__ import annotations

from typing import Any


def enrich_with_portfolio(
    market_rows: list[dict[str, Any]],
    portfolio_profile: tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    by_symbol = {
        str(row.get("symbol", "")).upper(): row
        for row in market_rows
    }
    enriched: list[dict[str, Any]] = []

    for asset in portfolio_profile:
        symbol = str(asset["symbol"]).upper()
        row = dict(by_symbol.get(symbol, {}))
        combined = {**asset, **row}
        combined["symbol"] = symbol
        combined["balance"] = float(asset.get("balance") or 0)
        combined["snapshot_value_aud"] = float(asset.get("snapshot_value_aud") or 0)

        price = row.get("price")
        if price is not None:
            combined["live_value_aud"] = float(price) * combined["balance"]
            combined["valuation_source"] = "Live estimate"
        else:
            combined["live_value_aud"] = combined["snapshot_value_aud"]
            combined["valuation_source"] = "Snapshot"

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
    return {
        "value_aud": value,
        "snapshot_value_aud": snapshot,
        "weighted_change_24h": weighted_change,
        "estimated_day_change_aud": estimated_day_change,
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
