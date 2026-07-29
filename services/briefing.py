from typing import Any


def _direction(value: float | None, positive: str, negative: str, neutral: str) -> str:
    if value is None:
        return neutral
    if value > 1:
        return positive
    if value < -1:
        return negative
    return neutral


def build_market_briefing(
    market: dict[str, Any],
    sentiment: dict[str, Any] | None,
    categories: dict[str, Any] | None,
    scanner: dict[str, Any] | None,
) -> dict[str, Any]:
    market_change = market.get("market_cap_change_24h")
    btc_dominance = market.get("btc_dominance")
    eth_dominance = market.get("eth_dominance")
    fear_value = sentiment.get("value") if sentiment else None

    regime_points = 0
    if market_change is not None:
        regime_points += 2 if market_change > 2 else 1 if market_change > 0 else -2 if market_change < -2 else -1
    if fear_value is not None:
        regime_points += 2 if fear_value >= 65 else 1 if fear_value >= 50 else -2 if fear_value <= 25 else -1 if fear_value < 40 else 0

    if regime_points >= 3:
        regime = "Risk-on"
    elif regime_points <= -3:
        regime = "Risk-off"
    else:
        regime = "Mixed"

    leader = None
    if categories and categories.get("leaders"):
        leader = categories["leaders"][0]

    candidates = []
    if scanner:
        candidates = [
            row for row in scanner.get("rows", [])
            if row.get("score", 0) >= 72 and row.get("risk") != "HIGH"
        ][:3]

    overview = (
        f"The market is currently in a {regime.lower()} regime. "
        f"Total crypto market capitalisation changed "
        f"{market_change:+.2f}% over 24 hours." if market_change is not None
        else f"The market is currently in a {regime.lower()} regime."
    )

    dominance = (
        f"Bitcoin dominance is {btc_dominance:.2f}% and Ethereum dominance is "
        f"{eth_dominance:.2f}%."
        if btc_dominance is not None and eth_dominance is not None
        else "Dominance data is temporarily incomplete."
    )

    sentiment_text = (
        f"Fear & Greed is {fear_value} ({sentiment.get('classification')})."
        if sentiment and fear_value is not None
        else "Sentiment data is temporarily unavailable."
    )

    narrative_text = (
        f"The strongest live category is {leader['name']} at "
        f"{leader['change_24h']:+.2f}% over 24 hours."
        if leader else "No category leader is currently available."
    )

    if candidates:
        candidate_text = "Top balanced research candidates: " + ", ".join(
            f"{row['name']} ({row['score']:.1f})" for row in candidates
        ) + "."
    else:
        candidate_text = "No scanner candidate currently clears the balanced-conviction threshold."

    risks = []
    if fear_value is not None and fear_value >= 80:
        risks.append("sentiment is extremely optimistic")
    if fear_value is not None and fear_value <= 20:
        risks.append("sentiment is extremely fearful")
    if market_change is not None and abs(market_change) >= 5:
        risks.append("market-wide volatility is elevated")
    if btc_dominance is not None and btc_dominance >= 60:
        risks.append("capital remains concentrated in Bitcoin")
    risk_text = (
        "Main caution: " + "; ".join(risks) + "."
        if risks else "No exceptional market-wide risk trigger is active, but crypto volatility remains high."
    )

    return {
        "regime": regime,
        "overview": overview,
        "dominance": dominance,
        "sentiment": sentiment_text,
        "narrative": narrative_text,
        "candidates": candidate_text,
        "risk": risk_text,
    }
