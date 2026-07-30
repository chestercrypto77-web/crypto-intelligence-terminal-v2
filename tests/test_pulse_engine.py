from services.pulse_engine import (
    intelligence_movers,
    market_pulse_score,
    narrative_heat,
    pulse_label,
)


def test_market_pulse_score():
    market = {"market_cap_change_24h": 2.0}
    sentiment = {"value": 70}
    rotations = [{"rotation_score": 80}, {"rotation_score": 70}]
    portfolio = {"score": 85}
    score = market_pulse_score(market, sentiment, rotations, portfolio)
    assert 0 <= score <= 100
    assert pulse_label(score) in {
        "Excellent", "Healthy", "Constructive",
        "Balanced", "Cautious", "Weak",
    }


def test_intelligence_movers():
    current = [
        {"name": "Alpha", "symbol": "A", "conviction": 82, "risk": "LOW"},
        {"name": "Beta", "symbol": "B", "conviction": 60, "risk": "MEDIUM"},
    ]
    history = {
        "A": [{"conviction_score": 70}],
        "B": [{"conviction_score": 65}],
    }
    movers = intelligence_movers(current, history)
    assert movers[0]["symbol"] == "A"
    assert movers[0]["delta"] == 12


def test_narrative_heat():
    rows = narrative_heat([
        {"name": "DeFi", "rotation_score": 85},
        {"name": "Gaming", "rotation_score": 30},
    ])
    assert rows[0]["state"] == "Hot"
    assert rows[1]["state"] == "Weak"
