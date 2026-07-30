from services.volume_intelligence import (
    _activity_label,
    _price_volume_read,
    _strength_score,
)


def test_activity_labels():
    assert _activity_label(None) == "Collecting baseline"
    assert _activity_label(3.0) == "Extreme"
    assert _activity_label(1.8) == "High"
    assert _activity_label(1.2) == "Elevated"
    assert _activity_label(0.5) == "Quiet"


def test_price_volume_interpretation():
    assert _price_volume_read(5, 2.0) == "Strong participation"
    assert _price_volume_read(5, 1.0) == "Price rising, volume unconfirmed"
    assert _price_volume_read(-5, 2.0) == "Heavy selling"
    assert _price_volume_read(-5, 1.0) == "Weakness on light participation"


def test_strength_score_is_bounded():
    score = _strength_score(80, 2.0, 30, 50, 8)
    assert 0 <= score <= 100
