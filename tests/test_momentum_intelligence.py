from services.momentum_intelligence import _arrow, _confidence, _status


def test_direction_arrows():
    assert _arrow(1) == "▲"
    assert _arrow(-1) == "▼"
    assert _arrow(0.02) == "►"
    assert _arrow(None) == "•"


def test_accelerating_requires_volume_confirmation():
    values = {"1h": 2.0, "4h": 5.0, "12h": 7.0, "24h": 10.0}
    assert _status(values, True) == "Accelerating"
    assert _status(values, False) == "Building"


def test_rolling_over_detection():
    values = {"1h": -2.0, "4h": -5.0, "12h": -8.0, "24h": -10.0}
    assert _status(values, True) == "Rolling over"


def test_confidence_is_bounded():
    values = {"15m": 1, "1h": 2, "4h": 3, "12h": 4, "24h": 5}
    confidence = _confidence(values, 30, True)
    assert 0 <= confidence <= 100
