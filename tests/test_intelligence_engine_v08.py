from services.intelligence_engine import (
    build_evidence,
    capital_rotation,
    health_breakdown,
    overall_health,
    project_summary,
)
from services.timeline import timeline_direction


def sample_project():
    return {
        "name": "Example",
        "symbol": "EX",
        "conviction": 84,
        "score": 80,
        "risk": "LOW",
        "change_1h": 1.0,
        "change_24h": 5.0,
        "change_7d": 14.0,
        "volume_ratio": 0.20,
    }


def test_health_and_evidence():
    row = sample_project()
    scores = health_breakdown(row)
    assert 0 <= overall_health(scores) <= 100
    evidence, confidence = build_evidence(row)
    assert len(evidence) >= 4
    assert 45 <= confidence <= 95
    assert "momentum" in project_summary(row).lower()


def test_rotation_sorting():
    rows = [
        {"name": "A", "change_24h": 8, "market_cap": 1000, "volume_24h": 200},
        {"name": "B", "change_24h": -4, "market_cap": 1000, "volume_24h": 30},
    ]
    result = capital_rotation(rows)
    assert result[0]["name"] == "A"


def test_timeline_direction():
    history = [
        {"conviction_score": 70},
        {"conviction_score": 82},
    ]
    assert "building" in timeline_direction(history).lower()
