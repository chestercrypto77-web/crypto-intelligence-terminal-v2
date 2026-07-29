from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
from typing import Any

from config import HISTORY_DATABASE_PATH


SCHEMA = '''
CREATE TABLE IF NOT EXISTS market_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at TEXT NOT NULL,
    market_regime TEXT NOT NULL,
    market_cap REAL,
    market_change_24h REAL,
    btc_dominance REAL,
    eth_dominance REAL,
    fear_greed INTEGER,
    fear_label TEXT,
    leading_narrative TEXT,
    leading_narrative_change REAL,
    portfolio_score REAL,
    portfolio_risk TEXT
);

CREATE TABLE IF NOT EXISTS asset_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    name TEXT NOT NULL,
    symbol TEXT NOT NULL,
    price REAL,
    change_24h REAL,
    change_7d REAL,
    opportunity_score REAL,
    conviction_score REAL,
    risk TEXT,
    rank INTEGER,
    UNIQUE(captured_at, asset_id)
);
'''


def _connect() -> sqlite3.Connection:
    path = Path(HISTORY_DATABASE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection


def save_snapshot(
    market: dict[str, Any],
    briefing: dict[str, Any],
    sentiment: dict[str, Any] | None,
    categories: dict[str, Any] | None,
    portfolio: dict[str, Any],
    conviction_rows: list[dict[str, Any]],
) -> str:
    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    leader = categories["leaders"][0] if categories and categories.get("leaders") else {}

    with _connect() as connection:
        connection.execute(
            '''
            INSERT INTO market_snapshots (
                captured_at, market_regime, market_cap, market_change_24h,
                btc_dominance, eth_dominance, fear_greed, fear_label,
                leading_narrative, leading_narrative_change,
                portfolio_score, portfolio_risk
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                captured_at,
                briefing.get("regime", "Unknown"),
                market.get("total_market_cap"),
                market.get("market_cap_change_24h"),
                market.get("btc_dominance"),
                market.get("eth_dominance"),
                sentiment.get("value") if sentiment else None,
                sentiment.get("classification") if sentiment else None,
                leader.get("name"),
                leader.get("change_24h"),
                portfolio.get("score"),
                portfolio.get("risk"),
            ),
        )

        connection.executemany(
            '''
            INSERT OR REPLACE INTO asset_snapshots (
                captured_at, asset_id, name, symbol, price, change_24h,
                change_7d, opportunity_score, conviction_score, risk, rank
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            [
                (
                    captured_at,
                    str(row.get("id") or row.get("symbol", "")).lower(),
                    row.get("name", "Unknown"),
                    row.get("symbol", ""),
                    row.get("price"),
                    row.get("change_24h"),
                    row.get("change_7d"),
                    row.get("score"),
                    row.get("conviction"),
                    row.get("risk"),
                    row.get("rank"),
                )
                for row in conviction_rows
            ],
        )

    return captured_at


def market_history(days: int = 30) -> list[dict[str, Any]]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with _connect() as connection:
        rows = connection.execute(
            '''
            SELECT * FROM market_snapshots
            WHERE captured_at >= ?
            ORDER BY captured_at ASC
            ''',
            (cutoff,),
        ).fetchall()
    return [dict(row) for row in rows]


def asset_history(asset_key: str, days: int = 30) -> list[dict[str, Any]]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    key = asset_key.lower()
    with _connect() as connection:
        rows = connection.execute(
            '''
            SELECT * FROM asset_snapshots
            WHERE captured_at >= ?
              AND (LOWER(asset_id) = ? OR LOWER(symbol) = ? OR LOWER(name) = ?)
            ORDER BY captured_at ASC
            ''',
            (cutoff, key, key, key),
        ).fetchall()
    return [dict(row) for row in rows]


def available_assets() -> list[dict[str, str]]:
    with _connect() as connection:
        rows = connection.execute(
            '''
            SELECT symbol, name, MAX(captured_at) AS latest
            FROM asset_snapshots
            GROUP BY symbol, name
            ORDER BY name ASC
            '''
        ).fetchall()
    return [{"symbol": row["symbol"], "name": row["name"]} for row in rows]


def snapshot_count() -> dict[str, int]:
    with _connect() as connection:
        market_count = connection.execute(
            "SELECT COUNT(*) FROM market_snapshots"
        ).fetchone()[0]
        asset_count = connection.execute(
            "SELECT COUNT(*) FROM asset_snapshots"
        ).fetchone()[0]
    return {"market": int(market_count), "assets": int(asset_count)}


def database_bytes() -> bytes:
    path = Path(HISTORY_DATABASE_PATH)
    if not path.exists():
        _connect().close()
    return path.read_bytes()


def restore_database(payload: bytes) -> None:
    path = Path(HISTORY_DATABASE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".restore")
    temporary.write_bytes(payload)

    connection = sqlite3.connect(temporary)
    try:
        result = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise ValueError("The uploaded database failed its integrity check.")
    finally:
        connection.close()

    temporary.replace(path)
