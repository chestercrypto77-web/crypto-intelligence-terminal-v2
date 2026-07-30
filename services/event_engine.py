from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import config
from services.event_store import save_events, save_observations

PRICE_EVENT_THRESHOLD_24H = float(getattr(config, "EVENT_PRICE_THRESHOLD_24H", 8.0))
PRICE_EVENT_THRESHOLD_1H = float(getattr(config, "EVENT_PRICE_THRESHOLD_1H", 2.5))
ATTENTION_HIGH_THRESHOLD = float(getattr(config, "EVENT_ATTENTION_HIGH", 70.0))
ATTENTION_CRITICAL_THRESHOLD = float(getattr(config, "EVENT_ATTENTION_CRITICAL", 88.0))
ATTENTION_CHANGE_THRESHOLD = float(getattr(config, "EVENT_ATTENTION_CHANGE", 10.0))
CONVICTION_CHANGE_THRESHOLD = float(getattr(config, "EVENT_CONVICTION_CHANGE", 6.0))
VOLUME_RATIO_THRESHOLD = float(getattr(config, "EVENT_VOLUME_RATIO_THRESHOLD", 0.18))
RISK_SEVERITY = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
SEVERITY_RANK = {"Informational": 1, "Medium": 2, "High": 3, "Critical": 4}


def _number(row: dict[str, Any] | None, key: str) -> float:
    if not row:
        return 0.0
    try:
        return float(row.get(key) or 0)
    except (TypeError, ValueError):
        return 0.0


def _severity_for_priority(base: str, priority: int) -> str:
    if priority != 1:
        return base
    return {"Informational": "Medium", "Medium": "High", "High": "Critical", "Critical": "Critical"}[base]


def _event(*, bucket: str, row: dict[str, Any], event_type: str, severity: str,
           title: str, detail: str, metric_name: str | None = None,
           current_value: float | None = None, previous_value: float | None = None,
           change_value: float | None = None) -> dict[str, Any]:
    symbol = str(row.get("symbol", "")).upper()
    priority = int(row.get("priority") or 3)
    severity = _severity_for_priority(severity, priority)
    direction = "up" if (change_value or 0) > 0 else "down" if (change_value or 0) < 0 else "state"
    rounded = round(float(current_value or 0), 2)
    return {
        "detected_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "event_key": f"{bucket}|{symbol}|{event_type}|{direction}|{rounded}",
        "symbol": symbol,
        "name": row.get("name", symbol),
        "event_type": event_type,
        "severity": severity,
        "title": title,
        "detail": detail,
        "metric_name": metric_name,
        "current_value": current_value,
        "previous_value": previous_value,
        "change_value": change_value,
        "priority": priority,
    }


def detect_events(rows: list[dict[str, Any]], previous_by_symbol: dict[str, dict[str, Any] | None],
                  bucket: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []

    for row in rows:
        if not row.get("available"):
            continue
        symbol = str(row.get("symbol", "")).upper()
        previous = previous_by_symbol.get(symbol)
        change_1h = _number(row, "change_1h")
        change_24h = _number(row, "change_24h")
        change_7d = _number(row, "change_7d")
        attention = _number(row, "attention")
        conviction = _number(row, "conviction") or _number(row, "score")
        volume_ratio = _number(row, "volume_ratio")
        risk = str(row.get("risk") or "LOW").upper()
        state = str(row.get("momentum_state") or "Stable")

        if abs(change_24h) >= PRICE_EVENT_THRESHOLD_24H:
            rising = change_24h > 0
            severity = "High" if abs(change_24h) >= 15 else "Medium"
            events.append(_event(
                bucket=bucket, row=row, event_type="price_momentum", severity=severity,
                title=f"{symbol} {'momentum surge' if rising else 'sharp weakness'}",
                detail=(f"{row['name']} is {change_24h:+.1f}% over 24 hours and {change_1h:+.1f}% "
                        f"over the latest hour. Momentum is {state.lower()}."),
                metric_name="change_24h", current_value=change_24h, change_value=change_24h,
            ))

        if abs(change_1h) >= PRICE_EVENT_THRESHOLD_1H:
            events.append(_event(
                bucket=bucket, row=row, event_type="short_term_acceleration", severity="Medium",
                title=f"{symbol} short-term acceleration",
                detail=f"The latest one-hour move is {change_1h:+.1f}%, with the 24-hour move at {change_24h:+.1f}%.",
                metric_name="change_1h", current_value=change_1h, change_value=change_1h,
            ))

        if attention >= ATTENTION_CRITICAL_THRESHOLD:
            events.append(_event(
                bucket=bucket, row=row, event_type="critical_attention", severity="High",
                title=f"{symbol} entered immediate-attention territory",
                detail=f"Attention is {attention:.0f}/100. {row.get('reason', '')}",
                metric_name="attention", current_value=attention,
            ))
        elif attention >= ATTENTION_HIGH_THRESHOLD:
            events.append(_event(
                bucket=bucket, row=row, event_type="high_attention", severity="Medium",
                title=f"{symbol} requires high attention",
                detail=f"Attention is {attention:.0f}/100. {row.get('reason', '')}",
                metric_name="attention", current_value=attention,
            ))

        if volume_ratio >= VOLUME_RATIO_THRESHOLD:
            events.append(_event(
                bucket=bucket, row=row, event_type="volume_intensity",
                severity="Medium" if volume_ratio < 0.35 else "High",
                title=f"{symbol} elevated trading intensity",
                detail=(f"Twenty-four-hour volume is {volume_ratio * 100:.1f}% of market capitalisation, "
                        "indicating elevated turnover."),
                metric_name="volume_ratio", current_value=volume_ratio,
            ))

        if state in {"Accelerating", "Deteriorating"}:
            events.append(_event(
                bucket=bucket, row=row, event_type="momentum_state",
                severity="High" if state == "Deteriorating" else "Medium",
                title=f"{symbol} momentum is {state.lower()}",
                detail=f"One-hour: {change_1h:+.1f}%, 24-hour: {change_24h:+.1f}%, seven-day: {change_7d:+.1f}%.",
                metric_name="momentum_state", current_value=change_24h,
            ))

        if previous:
            previous_attention = _number(previous, "attention")
            attention_delta = attention - previous_attention
            if abs(attention_delta) >= ATTENTION_CHANGE_THRESHOLD:
                events.append(_event(
                    bucket=bucket, row=row, event_type="attention_change",
                    severity="High" if abs(attention_delta) >= 18 else "Medium",
                    title=f"{symbol} attention {'jumped' if attention_delta > 0 else 'fell'}",
                    detail=f"Attention changed from {previous_attention:.0f} to {attention:.0f} ({attention_delta:+.0f} points).",
                    metric_name="attention", current_value=attention,
                    previous_value=previous_attention, change_value=attention_delta,
                ))

            previous_conviction = _number(previous, "conviction")
            conviction_delta = conviction - previous_conviction
            if previous_conviction and abs(conviction_delta) >= CONVICTION_CHANGE_THRESHOLD:
                events.append(_event(
                    bucket=bucket, row=row, event_type="conviction_change",
                    severity="High" if abs(conviction_delta) >= 10 else "Medium",
                    title=f"{symbol} conviction {'improved' if conviction_delta > 0 else 'weakened'}",
                    detail=f"Conviction moved from {previous_conviction:.0f} to {conviction:.0f} ({conviction_delta:+.0f} points).",
                    metric_name="conviction", current_value=conviction,
                    previous_value=previous_conviction, change_value=conviction_delta,
                ))

            previous_risk = str(previous.get("risk") or "LOW").upper()
            if RISK_SEVERITY.get(risk, 1) > RISK_SEVERITY.get(previous_risk, 1):
                events.append(_event(
                    bucket=bucket, row=row, event_type="risk_change", severity="High",
                    title=f"{symbol} risk increased",
                    detail=f"Risk classification changed from {previous_risk} to {risk}.",
                    metric_name="risk",
                ))

            previous_state = str(previous.get("momentum_state") or "Stable")
            if previous_state != state and state in {"Accelerating", "Deteriorating", "Strong", "Weakening"}:
                events.append(_event(
                    bucket=bucket, row=row, event_type="momentum_transition",
                    severity="High" if state == "Deteriorating" else "Medium",
                    title=f"{symbol} changed to {state.lower()}",
                    detail=f"Momentum state changed from {previous_state} to {state}.",
                    metric_name="momentum_state",
                ))

    deduplicated: dict[tuple[str, str], dict[str, Any]] = {}
    for event in events:
        key = (event["symbol"], event["event_type"])
        existing = deduplicated.get(key)
        if not existing or SEVERITY_RANK[event["severity"]] > SEVERITY_RANK[existing["severity"]]:
            deduplicated[key] = event

    result = list(deduplicated.values())
    result.sort(key=lambda event: (-SEVERITY_RANK[event["severity"]], int(event.get("priority") or 3), event["symbol"]))
    return result


def run_event_detection(rows: list[dict[str, Any]]) -> dict[str, Any]:
    bucket, previous = save_observations(rows)
    events = detect_events(rows, previous, bucket)
    inserted = save_events(events)
    return {"bucket": bucket, "events": events, "inserted": inserted,
            "observations": sum(1 for row in rows if row.get("available"))}


def daily_brief(events: list[dict[str, Any]]) -> str:
    if not events:
        return "No significant personal-market events have been detected in the selected period."
    critical = sum(1 for event in events if event["severity"] == "Critical")
    high = sum(1 for event in events if event["severity"] == "High")
    projects: list[str] = []
    for event in events:
        if event["symbol"] not in projects:
            projects.append(event["symbol"])
    text = f"{len(events)} important event{'s' if len(events) != 1 else ''} detected. "
    if critical:
        text += f"{critical} critical. "
    if high:
        text += f"{high} high severity. "
    text += f"Leading event: {events[0]['title']}. Active projects: {', '.join(projects[:6])}."
    return text
