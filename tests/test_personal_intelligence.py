from services.personal_intelligence import (
    attention_label,
    attention_score,
    build_personal_market,
    momentum_state,
)


def test_attention_prioritises_core_holding():
    row = {
        "change_1h": 2,
        "change_24h": 12,
        "change_7d": 20,
        "volume_ratio": 0.15,
        "conviction": 70,
    }
    assert attention_score(row, 1) > attention_score(row, 3)


def test_momentum_state():
    assert momentum_state(2, 14, 20) == "Accelerating"
    assert momentum_state(0, -14, -20) == "Deteriorating"


def test_personal_market_build():
    scanner = [{
        "name": "COTI", "symbol": "COTI", "change_1h": 3, "change_24h": 18,
        "change_7d": 25, "volume_ratio": 0.22, "score": 75, "risk": "MEDIUM",
    }]
    configured = ({"id": "coti", "name": "COTI", "symbol": "COTI", "priority": 1, "group": "Core", "narrative": "Privacy"},)
    rows = build_personal_market(scanner, scanner, configured)
    assert rows[0]["available"] is True
    assert rows[0]["attention"] >= 70
    assert attention_label(rows[0]["attention"]) in {"Immediate attention", "High attention"}
