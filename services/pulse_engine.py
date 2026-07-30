from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean
from typing import Any


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def market_pulse_score(
    market: dict[str, Any],
    sentiment: dict[str, Any] | None,
    rotations: list[dict[str, Any]],
    portfolio: dict[str, Any] | None,
) -> int:
    market_change = float(market.get("market_cap_change_24h") or 0)
    market_component = clamp(50 + market_change * 8)

    sentiment_component = float(sentiment.get("value", 50)) if sentiment else 50.0
    rotation_component = (
        mean(float(row.get("rotation_score") or 50) for row in rotations[:5])
        if rotations else 50.0
    )
    portfolio_component = float(portfolio.get("score", 50)) if portfolio else 50.0

    return round(
        market_component * 0.30
        + sentiment_component * 0.20
        + rotation_component * 0.30
        + portfolio_component * 0.20
    )


def pulse_label(score: int) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 72:
        return "Healthy"
    if score >= 58:
        return "Constructive"
    if score >= 45:
        return "Balanced"
    if score >= 32:
        return "Cautious"
    return "Weak"


def pulse_direction(current_score: int, history: list[dict[str, Any]]) -> str:
    historical = [
        float(row["portfolio_score"])
        for row in history[-5:]
        if row.get("portfolio_score") is not None
    ]
    if not historical:
        return "Building history"
    baseline = mean(historical)
    delta = current_score - baseline
    if delta >= 6:
        return "↑ Improving"
    if delta <= -6:
        return "↓ Weakening"
    if delta >= 2:
        return "↗ Firming"
    if delta <= -2:
        return "↘ Cooling"
    return "→ Stable"


def intelligence_movers(
    current_rows: list[dict[str, Any]],
    history_by_symbol: dict[str, list[dict[str, Any]]],
    limit: int = 8,
) -> list[dict[str, Any]]:
    movers: list[dict[str, Any]] = []
    for row in current_rows:
        symbol = str(row.get("symbol", "")).upper()
        history = history_by_symbol.get(symbol, [])
        prior = next(
            (item for item in reversed(history) if item.get("conviction_score") is not None),
            None,
        )
        current = float(row.get("conviction") or 0)
        previous = float(prior["conviction_score"]) if prior else None
        delta = current - previous if previous is not None else None

        if delta is None:
            signal = "New baseline"
        elif delta >= 5:
            signal = "Strongly improving"
        elif delta >= 2:
            signal = "Improving"
        elif delta <= -5:
            signal = "Strongly weakening"
        elif delta <= -2:
            signal = "Weakening"
        else:
            signal = "Stable"

        movers.append({
            "name": row.get("name", symbol),
            "symbol": symbol,
            "current": round(current, 1),
            "previous": round(previous, 1) if previous is not None else None,
            "delta": round(delta, 1) if delta is not None else None,
            "signal": signal,
            "risk": row.get("risk", "—"),
        })

    movers.sort(
        key=lambda item: abs(item["delta"]) if item["delta"] is not None else -1,
        reverse=True,
    )
    return movers[:limit]


def narrative_heat(rotations: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
    rows = []
    for row in rotations[:limit]:
        score = float(row.get("rotation_score") or 50)
        if score >= 82:
            state = "Hot"
        elif score >= 68:
            state = "Strong"
        elif score >= 58:
            state = "Rising"
        elif score >= 45:
            state = "Neutral"
        elif score >= 35:
            state = "Cooling"
        else:
            state = "Weak"
        rows.append({**row, "heat": round(score), "state": state})
    return rows


def portfolio_monitor(
    portfolio_rows: list[dict[str, Any]],
    conviction_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    conviction_map = {
        str(row.get("symbol", "")).upper(): row for row in conviction_rows
    }
    results = []
    for holding in portfolio_rows:
        symbol = str(holding.get("symbol", "")).upper()
        row = conviction_map.get(symbol, {})
        change = float(row.get("change_7d") or 0)
        conviction = float(row.get("conviction") or 0)
        if change >= 10 and conviction >= 75:
            status = "Accelerating"
        elif change >= 2:
            status = "Improving"
        elif change <= -10:
            status = "Weakening"
        elif change <= -2:
            status = "Cooling"
        else:
            status = "Stable"
        results.append({
            "symbol": symbol,
            "name": row.get("name", symbol),
            "weight": holding.get("weight", holding.get("allocation", "—")),
            "conviction": round(conviction, 1) if conviction else None,
            "status": status,
            "risk": row.get("risk", "—"),
        })
    return results


def live_feed(
    market: dict[str, Any],
    sentiment: dict[str, Any] | None,
    rotations: list[dict[str, Any]],
    movers: list[dict[str, Any]],
    portfolio_rows: list[dict[str, Any]],
    limit: int = 12,
) -> list[dict[str, str]]:
    now = datetime.now(timezone.utc).strftime("%H:%M UTC")
    items: list[dict[str, str]] = []

    market_change = float(market.get("market_cap_change_24h") or 0)
    items.append({
        "time": now,
        "title": "Global market",
        "detail": f"Market capitalisation is {market_change:+.2f}% over 24 hours.",
        "level": "positive" if market_change > 0 else "negative" if market_change < 0 else "neutral",
    })

    if sentiment:
        items.append({
            "time": now,
            "title": "Market sentiment",
            "detail": f"Fear & Greed is {sentiment.get('value', '—')} — {sentiment.get('classification', 'Unknown')}.",
            "level": "neutral",
        })

    for row in rotations[:3]:
        items.append({
            "time": now,
            "title": f"{row.get('name', 'Narrative')} rotation",
            "detail": f"{row.get('rotation_signal', 'Neutral')} with a score of {row.get('rotation_score', 50):.0f}.",
            "level": "positive" if float(row.get("rotation_score") or 50) >= 58 else "negative",
        })

    for mover in movers[:4]:
        delta = mover.get("delta")
        change_text = "new baseline" if delta is None else f"{delta:+.1f} conviction points"
        items.append({
            "time": now,
            "title": f"{mover['name']} intelligence",
            "detail": f"{mover['signal']} — {change_text}.",
            "level": "positive" if delta is not None and delta > 0 else "negative" if delta is not None and delta < 0 else "neutral",
        })

    for holding in portfolio_rows[:2]:
        items.append({
            "time": now,
            "title": f"Portfolio · {holding['symbol']}",
            "detail": f"{holding['status']} with conviction {holding.get('conviction') or '—'}.",
            "level": "neutral",
        })

    return items[:limit]


def daily_brief(
    pulse_score: int,
    pulse_state: str,
    rotations: list[dict[str, Any]],
    movers: list[dict[str, Any]],
    research_queue: list[dict[str, Any]],
) -> str:
    leaders = ", ".join(row.get("name", "Unknown") for row in rotations[:3]) or "no clear narrative"
    improving = [row["name"] for row in movers if row.get("delta") is not None and row["delta"] > 0]
    improving_text = ", ".join(improving[:3]) if improving else "no major conviction improvement"
    focus = ", ".join(row.get("name", "Unknown") for row in research_queue[:3]) or "none yet"

    return (
        f"Market Pulse is {pulse_score}/100 and currently classified as {pulse_state.lower()}. "
        f"The strongest relative narrative activity is in {leaders}. "
        f"Intelligence momentum is improving most in {improving_text}. "
        f"Today's research focus is {focus}. "
        "These are evidence-based monitoring signals, not investment recommendations."
    )
