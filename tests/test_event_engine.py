from services.event_engine import detect_events


def sample_row(**overrides):
    row = {
        "available": True,
        "name": "COTI",
        "symbol": "COTI",
        "priority": 1,
        "price": 0.1,
        "change_1h": 3.0,
        "change_24h": 15.0,
        "change_7d": 20.0,
        "volume": 50_000_000,
        "volume_ratio": 0.25,
        "attention": 92.0,
        "conviction": 78.0,
        "risk": "MEDIUM",
        "momentum_state": "Accelerating",
        "reason": "Strong momentum.",
    }
    row.update(overrides)
    return row


def test_first_scan_produces_absolute_events():
    events = detect_events([sample_row()], {"COTI": None}, "2026-07-30T00:00:00+00:00")
    types = {event["event_type"] for event in events}
    assert "price_momentum" in types
    assert "critical_attention" in types
    assert "volume_intensity" in types


def test_tier_one_event_severity_is_upgraded():
    events = detect_events(
        [sample_row(change_1h=0, change_24h=9, attention=60, volume_ratio=0.05, momentum_state="Strong")],
        {"COTI": None},
        "2026-07-30T00:00:00+00:00",
    )
    price_event = next(event for event in events if event["event_type"] == "price_momentum")
    assert price_event["severity"] == "High"


def test_transition_events_compare_previous_observation():
    previous = {"attention": 60, "conviction": 65, "risk": "LOW", "momentum_state": "Stable"}
    events = detect_events(
        [sample_row(attention=82, conviction=75, risk="MEDIUM", momentum_state="Strong")],
        {"COTI": previous},
        "2026-07-30T00:15:00+00:00",
    )
    types = {event["event_type"] for event in events}
    assert "attention_change" in types
    assert "conviction_change" in types
    assert "risk_change" in types
    assert "momentum_transition" in types
