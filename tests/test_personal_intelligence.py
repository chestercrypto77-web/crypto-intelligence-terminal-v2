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

def test_attention_score_accepts_descriptive_conviction_label():
    from services.personal_intelligence import attention_score

    row = {
        "change_1h": 0,
        "change_24h": 2,
        "change_7d": 4,
        "volume_ratio": 0.05,
        "conviction": "Core",
    }
    score = attention_score(row, 1)
    assert isinstance(score, float)
    assert score > 0


def test_attention_score_prefers_numeric_conviction_score():
    from services.personal_intelligence import attention_score

    row = {
        "change_1h": 0,
        "change_24h": 0,
        "change_7d": 0,
        "volume_ratio": 0,
        "conviction": "High",
        "conviction_score": 90,
    }
    assert attention_score(row, 2) > 20

def test_attention_score_handles_none_and_bad_strings():
    from services.personal_intelligence import attention_score

    row = {
        "change_1h": None,
        "change_24h": "not-a-number",
        "change_7d": "",
        "volume_ratio": None,
        "conviction": "Core",
    }
    score = attention_score(row, 1)
    assert isinstance(score, float)
    assert score > 0


def test_build_personal_market_handles_partial_api_rows():
    from services.personal_intelligence import build_personal_market

    scanner = [{
        "symbol": "BTC",
        "name": "Bitcoin",
        "change_1h": None,
        "change_24h": None,
        "change_7d": "bad",
        "volume_ratio": None,
        "price": None,
    }]
    profile = ({
        "symbol": "BTC",
        "name": "Bitcoin",
        "priority": 1,
        "conviction": "Core",
        "conviction_score": 95,
    },)
    rows = build_personal_market(scanner, [], profile)
    assert rows[0]["available"] is True
    assert rows[0]["attention"] > 0
    assert rows[0]["momentum_state"] == "Stable"
