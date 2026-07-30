from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
from typing import Any

import config

DATABASE_PATH = getattr(config, "HISTORY_DATABASE_PATH", "data/intelligence_history.db")

EVENT_SCHEMA = """
CREATE TABLE IF NOT EXISTS personal_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at TEXT NOT NULL,
    observation_bucket TEXT NOT NULL,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    priority INTEGER NOT NULL,
    price REAL,
    change_1h REAL,
    change_24h REAL,
    change_7d REAL,
    volume REAL,
    volume_ratio REAL,
    attention REAL,
    conviction REAL,
    risk TEXT,
    momentum_state TEXT,
    UNIQUE(observation_bucket, symbol)
);

CREATE INDEX IF NOT EXISTS idx_personal_observations_symbol_time
ON personal_observations(symbol, captured_at DESC);

CREATE TABLE IF NOT EXISTS intelligence_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    detected_at TEXT NOT NULL,
    event_key TEXT NOT NULL UNIQUE,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    title TEXT NOT NULL,
    detail TEXT NOT NULL,
    metric_name TEXT,
    current_value REAL,
    previous_value REAL,
    change_value REAL,
    priority INTEGER NOT NULL,
    acknowledged INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_intelligence_events_time
ON intelligence_events(detected_at DESC);

CREATE INDEX IF NOT EXISTS idx_intelligence_events_symbol
ON intelligence_events(symbol, detected_at DESC);
"""


def _connect() -> sqlite3.Connection:
    path = Path(DATABASE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.executescript(EVENT_SCHEMA)
    return connection


def observation_bucket(captured_at: datetime | None = None, minutes: int = 15) -> str:
    moment = captured_at or datetime.now(timezone.utc)
    minute = (moment.minute // minutes) * minutes
    bucket = moment.replace(minute=minute, second=0, microsecond=0)
    return bucket.isoformat()


def save_observations(rows: list[dict[str, Any]]) -> tuple[str, dict[str, dict[str, Any] | None]]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    captured_at = now.isoformat()
    bucket = observation_bucket(now)
    previous: dict[str, dict[str, Any] | None] = {}

    with _connect() as connection:
        for row in rows:
            if not row.get("available"):
                continue

            symbol = str(row.get("symbol", "")).upper()
            prior = connection.execute(
                """
                SELECT * FROM personal_observations
                WHERE UPPER(symbol) = UPPER(?)
                  AND observation_bucket <> ?
                ORDER BY captured_at DESC
                LIMIT 1
                """,
                (symbol, bucket),
            ).fetchone()
            previous[symbol] = dict(prior) if prior else None

            connection.execute(
                """
                INSERT OR REPLACE INTO personal_observations (
                    captured_at, observation_bucket, symbol, name, priority,
                    price, change_1h, change_24h, change_7d, volume,
                    volume_ratio, attention, conviction, risk, momentum_state
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    captured_at,
                    bucket,
                    symbol,
                    row.get("name", symbol),
                    int(row.get("priority") or 3),
                    row.get("price"),
                    row.get("change_1h"),
                    row.get("change_24h"),
                    row.get("change_7d"),
                    row.get("volume"),
                    row.get("volume_ratio"),
                    row.get("attention"),
                    row.get("conviction") or row.get("score"),
                    row.get("risk"),
                    row.get("momentum_state"),
                ),
            )

    return bucket, previous


def save_events(events: list[dict[str, Any]]) -> int:
    inserted = 0
    with _connect() as connection:
        for event in events:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO intelligence_events (
                    detected_at, event_key, symbol, name, event_type, severity,
                    title, detail, metric_name, current_value, previous_value,
                    change_value, priority
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["detected_at"], event["event_key"], event["symbol"],
                    event["name"], event["event_type"], event["severity"],
                    event["title"], event["detail"], event.get("metric_name"),
                    event.get("current_value"), event.get("previous_value"),
                    event.get("change_value"), int(event.get("priority") or 3),
                ),
            )
            inserted += int(cursor.rowcount > 0)
    return inserted


def recent_events(hours: int = 72, limit: int = 100, symbol: str | None = None,
                  minimum_severity: str | None = None) -> list[dict[str, Any]]:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    clauses = ["detected_at >= ?"]
    params: list[Any] = [cutoff]

    if symbol and symbol != "All":
        clauses.append("UPPER(symbol) = UPPER(?)")
        params.append(symbol)

    severity_rank = {"Informational": 1, "Medium": 2, "High": 3, "Critical": 4}
    if minimum_severity:
        allowed = [label for label, rank in severity_rank.items()
                   if rank >= severity_rank.get(minimum_severity, 1)]
        placeholders = ",".join("?" for _ in allowed)
        clauses.append(f"severity IN ({placeholders})")
        params.extend(allowed)

    params.append(limit)
    query = f"""
        SELECT * FROM intelligence_events
        WHERE {' AND '.join(clauses)}
        ORDER BY
            CASE severity
                WHEN 'Critical' THEN 4
                WHEN 'High' THEN 3
                WHEN 'Medium' THEN 2
                ELSE 1
            END DESC,
            detected_at DESC
        LIMIT ?
    """
    with _connect() as connection:
        rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def event_counts(hours: int = 24) -> dict[str, int]:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    result = {"Critical": 0, "High": 0, "Medium": 0, "Informational": 0, "total": 0}
    with _connect() as connection:
        rows = connection.execute(
            "SELECT severity, COUNT(*) AS count FROM intelligence_events WHERE detected_at >= ? GROUP BY severity",
            (cutoff,),
        ).fetchall()
    for row in rows:
        result[row["severity"]] = int(row["count"])
        result["total"] += int(row["count"])
    return result


def available_event_symbols() -> list[str]:
    with _connect() as connection:
        rows = connection.execute(
            "SELECT DISTINCT symbol FROM intelligence_events ORDER BY symbol"
        ).fetchall()
    return [str(row["symbol"]) for row in rows]
