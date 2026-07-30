from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
from typing import Any

import config

DATABASE_PATH = getattr(config, "HISTORY_DATABASE_PATH", "data/intelligence_history.db")
BUCKET_MINUTES = int(getattr(config, "MOMENTUM_SNAPSHOT_MINUTES", 15))

SCHEMA = """
CREATE TABLE IF NOT EXISTS momentum_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at TEXT NOT NULL,
    bucket TEXT NOT NULL,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    price REAL,
    volume REAL,
    market_cap REAL,
    change_1h REAL,
    change_24h REAL,
    change_7d REAL,
    UNIQUE(bucket, symbol)
);
CREATE INDEX IF NOT EXISTS idx_momentum_symbol_time
ON momentum_snapshots(symbol, captured_at DESC);
"""


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _connect() -> sqlite3.Connection:
    path = Path(DATABASE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection


def _bucket(moment: datetime) -> str:
    minute = (moment.minute // BUCKET_MINUTES) * BUCKET_MINUTES
    return moment.replace(minute=minute, second=0, microsecond=0).isoformat()


def record_market(rows: list[dict[str, Any]]) -> int:
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
                INSERT OR IGNORE INTO momentum_snapshots (
                    captured_at, bucket, symbol, name, price, volume, market_cap,
                    change_1h, change_24h, change_7d
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    now.isoformat(), bucket, symbol, row.get("name", symbol),
                    row.get("price"), row.get("volume"), row.get("market_cap"),
                    row.get("change_1h"), row.get("change_24h"), row.get("change_7d"),
                ),
            )
            inserted += int(cursor.rowcount > 0)
    return inserted


def _history(symbol: str, hours: int = 72) -> list[dict[str, Any]]:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT * FROM momentum_snapshots
            WHERE UPPER(symbol) = UPPER(?) AND captured_at >= ?
            ORDER BY captured_at ASC
            """,
            (symbol, cutoff),
        ).fetchall()
    return [dict(row) for row in rows]


def _nearest_change(history: list[dict[str, Any]], hours: float) -> float | None:
    if not history:
        return None
    latest = history[-1]
    latest_price = safe_float(latest.get("price"))
    if latest_price <= 0:
        return None
    latest_time = datetime.fromisoformat(latest["captured_at"])
    target = latest_time - timedelta(hours=hours)
    prior = min(
        history,
        key=lambda row: abs((datetime.fromisoformat(row["captured_at"]) - target).total_seconds()),
    )
    prior_time = datetime.fromisoformat(prior["captured_at"])
    tolerance = max(20 * 60, hours * 3600 * 0.45)
    if abs((prior_time - target).total_seconds()) > tolerance:
        return None
    prior_price = safe_float(prior.get("price"))
    if prior_price <= 0:
        return None
    return (latest_price / prior_price - 1) * 100


def _arrow(value: float | None, flat: float = 0.15) -> str:
    if value is None:
        return "•"
    if value > flat:
        return "▲"
    if value < -flat:
        return "▼"
    return "►"


def _status(values: dict[str, float | None], volume_confirmed: bool) -> str:
    one = values.get("1h")
    four = values.get("4h")
    twelve = values.get("12h")
    twenty_four = values.get("24h")

    if one is not None and four is not None:
        if one > 1.2 and four > 2.5 and volume_confirmed:
            return "Accelerating"
        if one > 0.3 and four > 1.0:
            return "Building"
        if one < -1.2 and four < -2.5:
            return "Rolling over"
        if one < -0.3 and four < -1.0:
            return "Weakening"

    if twenty_four is not None and twenty_four > 5:
        return "Strong"
    if twenty_four is not None and twenty_four < -5:
        return "Under pressure"
    if twelve is not None and abs(twelve) < 1:
        return "Stable"
    return "Mixed"


def _confidence(values: dict[str, float | None], history_count: int, volume_confirmed: bool) -> int:
    available = sum(value is not None for value in values.values())
    score = available * 16
    if history_count >= 8:
        score += 12
    if history_count >= 24:
        score += 10
    if volume_confirmed:
        score += 14
    signs = [
        1 if value and value > 0 else -1 if value and value < 0 else 0
        for value in values.values()
        if value is not None
    ]
    if signs and abs(sum(signs)) == len(signs):
        score += 10
    return max(0, min(100, score))


def momentum_row(row: dict[str, Any]) -> dict[str, Any]:
    symbol = str(row.get("symbol", "")).upper()
    history = _history(symbol)
    values = {
        "15m": _nearest_change(history, 0.25),
        "1h": _nearest_change(history, 1),
        "4h": _nearest_change(history, 4),
        "12h": _nearest_change(history, 12),
        "24h": _nearest_change(history, 24),
    }
    if values["1h"] is None:
        values["1h"] = safe_float(row.get("change_1h"))
    if values["24h"] is None:
        values["24h"] = safe_float(row.get("change_24h"))

    volume = safe_float(row.get("volume"))
    market_cap = safe_float(row.get("market_cap"))
    volume_ratio = volume / market_cap if market_cap else 0
    volume_confirmed = volume_ratio >= 0.08
    status = _status(values, volume_confirmed)
    confidence = _confidence(values, len(history), volume_confirmed)

    acceleration = None
    if values["1h"] is not None and values["4h"] is not None:
        acceleration = values["1h"] - values["4h"] / 4

    return {
        **row,
        "moves": values,
        "arrows": {key: _arrow(value) for key, value in values.items()},
        "status": status,
        "confidence": confidence,
        "acceleration": acceleration,
        "volume_confirmed": volume_confirmed,
        "history_points": len(history),
    }


def build_momentum_radar(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    record_market(rows)
    result = [momentum_row(row) for row in rows]
    rank = {
        "Accelerating": 6, "Building": 5, "Strong": 4, "Stable": 3,
        "Mixed": 2, "Weakening": 1, "Under pressure": 0, "Rolling over": -1,
    }
    result.sort(
        key=lambda row: (
            -rank.get(row["status"], 2),
            -row["confidence"],
            -safe_float(row["moves"].get("1h")),
        )
    )
    return result
