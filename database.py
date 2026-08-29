import sqlite3
from pathlib import Path
from typing import Any


DATABASE_DIR = Path("database")
DATABASE_PATH = DATABASE_DIR / "netscope.db"


def get_connection() -> sqlite3.Connection:
    """Create a connection to the NetScope SQLite database."""
    DATABASE_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    """Create the diagnostic history table if it does not exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS diagnostics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                results TEXT NOT NULL
            )
            """
        )

        connection.commit()


def save_diagnostic(
    timestamp: str,
    status: str,
    results: str,
) -> int:
    """Save a diagnostic result and return its database ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO diagnostics (timestamp, status, results)
            VALUES (?, ?, ?)
            """,
            (timestamp, status, results),
        )

        connection.commit()

        return cursor.lastrowid


def get_diagnostics(limit: int = 20) -> list[dict[str, Any]]:
    """Return recent diagnostic records."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, timestamp, status, results
            FROM diagnostics
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]