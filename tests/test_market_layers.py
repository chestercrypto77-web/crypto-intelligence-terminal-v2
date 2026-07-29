from services.market_layers import (
    is_core_asset,
    is_emerging_asset,
    research_reason,
    split_market_layers,
    tier_label,
)
from services.momentum import arrow, momentum_status


def test_market_layer_split() -> None:
    rows = [
        {
            "name": "Core",
            "symbol": "BTC",
            "rank": 1,
            "market_cap": 1_000_000_000_000,
            "volume": 20_000_000_000,
            "conviction": 90,
            "risk": "LOW",
        },
        {
            "name": "Emerging",
            "symbol": "NEW",
            "rank": 70,
            "market_cap": 500_000_000,
            "volume": 20_000_000,
            "conviction": 78,
            "risk": "MEDIUM",
        },
    ]
    result = split_market_layers(rows)
    assert len(result["core"]) == 1
    assert len(result["emerging"]) == 1
    assert is_core_asset(rows[0])
    assert is_emerging_asset(rows[1])


def test_labels_and_reasons() -> None:
    row = {
        "conviction": 84,
        "risk": "LOW",
        "change_7d": 15,
        "change_24h": 4,
        "volume_ratio": 0.22,
    }
    assert tier_label(row) == "Emerging Leader"
    assert "conviction" in research_reason(row).lower()


def test_momentum_helpers() -> None:
    assert arrow(4.2) == "↑ 4.2%"
    assert arrow(-3.1) == "↓ 3.1%"
    assert momentum_status(2, 8, 20).startswith("🟢")
