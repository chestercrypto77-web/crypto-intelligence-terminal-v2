from pathlib import Path
import tempfile

from services.trends import history_summary, trend_label


def test_trend_labels() -> None:
    assert trend_label([50, 64]) == "Strong Uptrend"
    assert trend_label([50, 56]) == "Improving"
    assert trend_label([50, 51]) == "Neutral"
    assert trend_label([50, 44]) == "Weakening"
    assert trend_label([50, 35]) == "Strong Downtrend"


def test_history_summary() -> None:
    rows = [
        {"score": 60},
        {"score": 65},
        {"score": 70},
    ]
    result = history_summary(rows, "score")
    assert result["current"] == 70
    assert result["change"] == 10
    assert result["average"] == 65
    assert result["trend"] == "Improving"
