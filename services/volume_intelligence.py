from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import math
import sqlite3
from statistics import median
from typing import Any

import config

DATABASE_PATH = getattr(config, "HISTORY_DATABASE_PATH", "data/intelligence_history.db")
HISTORY_HOURS = int(getattr(config, "VOLUME_HISTORY_HOURS", 168))
BASELINE_MIN_POINTS = int(getattr(config, "VOLUME_BASELINE_MIN_POINTS", 8))
HIGH_RVOL = float(getattr(config, "VOLUME_HIGH_RVOL", 1.50))
EXTREME_RVOL = float(getattr(config, "VOLUME_EXTREME_RVOL", 2.50))

SCHEMA = """
CREATE TABLE IF NOT EXISTS volume_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at TEXT NOT NULL,
    bucket TEXT NOT NULL,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    price REAL,
    volume_24h REAL,
    market_cap REAL,
    change_1h REAL,
    change_24h REAL,
    UNIQUE(bucket, symbol)
);

CREATE INDEX IF NOT EXISTS idx_volume_symbol_time
ON volume_snapshots(symbol, captured_at DESC);
"""


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
        return number if math.isfinite(number) else default
    except (TypeError, ValueError):
        return default


def _connect() -> sqlite3.Connection:
    path = Path(DATABASE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection


def _bucket(moment: datetime, minutes: int = 15) -> str:
    minute = (moment.minute // minutes) * minutes
    return moment.replace(minute=minute, second=0, microsecond=0).isoformat()


def record_volume_snapshots(rows: list[dict[str, Any]]) -> int:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    bucket = _bucket(now)
    inserted = 0
    with _connect() as connection:
        for row in rows:
            symbol = str(row.get("symbol", "")).upper()
            if not symbol:
                continue
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO volume_snapshots (
                    captured_at, bucket, symbol, name, price, volume_24h,
                    market_cap, change_1h, change_24h
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    now.isoformat(),
                    bucket,
                    symbol,
                    row.get("name", symbol),
                    row.get("price"),
                    row.get("volume"),
                    row.get("market_cap"),
                    row.get("change_1h"),
                    row.get("change_24h"),
                ),
            )
            inserted += int(cursor.rowcount > 0)
    return inserted


def _history(symbol: str, hours: int = HISTORY_HOURS) -> list[dict[str, Any]]:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT * FROM volume_snapshots
            WHERE UPPER(symbol) = UPPER(?) AND captured_at >= ?
            ORDER BY captured_at ASC
            """,
            (symbol, cutoff),
        ).fetchall()
    return [dict(row) for row in rows]


def _baseline(history: list[dict[str, Any]]) -> float | None:
    values = [
        safe_float(row.get("volume_24h"))
        for row in history[:-1]
        if safe_float(row.get("volume_24h")) > 0
    ]
    if len(values) < BASELINE_MIN_POINTS:
        return None
    # Median is deliberately used to reduce distortion from one-off spikes.
    return median(values)


def _period_change(history: list[dict[str, Any]], hours: float) -> float | None:
    if len(history) < 2:
        return None
    latest = history[-1]
    latest_volume = safe_float(latest.get("volume_24h"))
    if latest_volume <= 0:
        return None

    latest_time = datetime.fromisoformat(latest["captured_at"])
    target = latest_time - timedelta(hours=hours)
    prior = min(
        history,
        key=lambda row: abs(
            (datetime.fromisoformat(row["captured_at"]) - target).total_seconds()
        ),
    )
    tolerance = max(20 * 60, hours * 3600 * 0.50)
    if abs((datetime.fromisoformat(prior["captured_at"]) - target).total_seconds()) > tolerance:
        return None

    previous_volume = safe_float(prior.get("volume_24h"))
    if previous_volume <= 0:
        return None
    return (latest_volume / previous_volume - 1) * 100


def _price_volume_read(price_change: float, rvol: float | None) -> str:
    high_volume = rvol is not None and rvol >= HIGH_RVOL
    if price_change >= 2 and high_volume:
        return "Strong participation"
    if price_change >= 2 and not high_volume:
        return "Price rising, volume unconfirmed"
    if price_change <= -2 and high_volume:
        return "Heavy selling"
    if price_change <= -2 and not high_volume:
        return "Weakness on light participation"
    if high_volume:
        return "Unusual activity"
    return "Normal participation"


def _activity_label(rvol: float | None) -> str:
    if rvol is None:
        return "Collecting baseline"
    if rvol >= EXTREME_RVOL:
        return "Extreme"
    if rvol >= HIGH_RVOL:
        return "High"
    if rvol >= 1.10:
        return "Elevated"
    if rvol <= 0.65:
        return "Quiet"
    return "Normal"


def _strength_score(
    momentum_score: float,
    rvol: float | None,
    volume_change_1h: float | None,
    volume_change_4h: float | None,
    price_change_24h: float,
) -> int:
    score = momentum_score * 0.45

    if rvol is not None:
        score += min(rvol / 3.0, 1.0) * 30
    else:
        score += 8

    if volume_change_1h is not None:
        score += max(-10, min(15, volume_change_1h / 8))
    if volume_change_4h is not None:
        score += max(-8, min(10, volume_change_4h / 15))

    if price_change_24h > 0:
        score += min(price_change_24h, 10) * 0.7
    else:
        score += max(price_change_24h, -10) * 0.5

    return int(max(0, min(100, round(score))))


def volume_row(row: dict[str, Any]) -> dict[str, Any]:
    symbol = str(row.get("symbol", "")).upper()
    history = _history(symbol)

    current_volume = safe_float(row.get("volume"))
    market_cap = safe_float(row.get("market_cap"))
    baseline = _baseline(history)
    rvol = current_volume / baseline if baseline and baseline > 0 else None

    change_1h = _period_change(history, 1)
    change_4h = _period_change(history, 4)
    change_12h = _period_change(history, 12)
    turnover = current_volume / market_cap if market_cap > 0 else 0.0
    price_change_24h = safe_float(row.get("change_24h"))
    momentum_score = safe_float(row.get("score") or row.get("attention") or 50)

    activity = _activity_label(rvol)
    interpretation = _price_volume_read(price_change_24h, rvol)
    strength = _strength_score(
        momentum_score,
        rvol,
        change_1h,
        change_4h,
        price_change_24h,
    )

    return {
        **row,
        "volume_24h": current_volume,
        "volume_baseline": baseline,
        "rvol": rvol,
        "volume_change_1h": change_1h,
        "volume_change_4h": change_4h,
        "volume_change_12h": change_12h,
        "turnover_ratio": turnover,
        "volume_activity": activity,
        "price_volume_read": interpretation,
        "market_strength": strength,
        "volume_history_points": len(history),
    }


def build_volume_intelligence(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    record_volume_snapshots(rows)
    result = [volume_row(row) for row in rows]
    result.sort(
        key=lambda row: (
            -safe_float(row.get("market_strength")),
            -(safe_float(row.get("rvol")) if row.get("rvol") is not None else 0),
            -safe_float(row.get("volume_24h")),
        )
    )
    return result
