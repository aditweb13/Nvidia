"""SQLite database module for Cascade logging and observability.

Creates and manages:
- tasks table: high-level task resolution records
- calls table: per-tier model execution and verifier calls
Feeds both the Streamlit dashboard and the evaluation benchmark.
"""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.config import get_settings


def get_db_connection(db_path: str | None = None) -> sqlite3.Connection:
    if db_path is None:
        db_path = get_settings().db_path
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | None = None) -> None:
    """Initialize SQLite tables for tasks and calls if they don't exist."""
    conn = get_db_connection(db_path)
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id        TEXT PRIMARY KEY,
                ticket_text    TEXT NOT NULL,
                split          TEXT,               -- dev | test | live
                config         TEXT,               -- nano | super | ultra | cascade
                final_tier     TEXT,
                final_reply    TEXT,
                needs_review   INTEGER DEFAULT 0,
                total_cost     REAL,
                total_latency  REAL,
                correct        INTEGER,            -- set by the grader (1, 0, or NULL)
                created_at     TEXT
            );
            """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS calls (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id        TEXT NOT NULL REFERENCES tasks(task_id),
                attempt        INTEGER,
                tier           TEXT,
                tokens_in      INTEGER,
                tokens_out     INTEGER,
                cost           REAL,
                latency        REAL,
                verifier       TEXT,               -- which verifier produced the verdict
                verdict        TEXT,               -- pass | fail
                reason         TEXT,
                created_at     TEXT
            );
            """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_calls_task ON calls(task_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_split ON tasks(split);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_config ON tasks(config);")
    conn.close()


def log_task(
    task_id: str,
    ticket_text: str,
    split: str,
    config: str,
    final_tier: str,
    final_reply: str,
    needs_review: bool,
    total_cost: float,
    total_latency: float,
    correct: int | None = None,
    created_at: str | None = None,
    db_path: str | None = None,
) -> None:
    """Log or update a task record."""
    if created_at is None:
        created_at = datetime.now(UTC).isoformat()
    conn = get_db_connection(db_path)
    with conn:
        conn.execute(
            """
            INSERT INTO tasks (
                task_id, ticket_text, split, config, final_tier, final_reply,
                needs_review, total_cost, total_latency, correct, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(task_id) DO UPDATE SET
                final_tier=excluded.final_tier,
                final_reply=excluded.final_reply,
                needs_review=excluded.needs_review,
                total_cost=excluded.total_cost,
                total_latency=excluded.total_latency,
                correct=excluded.correct
            """,
            (
                task_id,
                ticket_text,
                split,
                config,
                final_tier,
                final_reply,
                1 if needs_review else 0,
                total_cost,
                total_latency,
                correct,
                created_at,
            ),
        )
    conn.close()


def log_call(
    task_id: str,
    attempt: int,
    tier: str,
    tokens_in: int,
    tokens_out: int,
    cost: float,
    latency: float,
    verifier: str,
    verdict: str,
    reason: str,
    created_at: str | None = None,
    db_path: str | None = None,
) -> None:
    """Log an individual tier attempt and verifier decision."""
    if created_at is None:
        created_at = datetime.now(UTC).isoformat()
    conn = get_db_connection(db_path)
    with conn:
        conn.execute(
            """
            INSERT INTO calls (
                task_id, attempt, tier, tokens_in, tokens_out, cost,
                latency, verifier, verdict, reason, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                attempt,
                tier,
                tokens_in,
                tokens_out,
                cost,
                latency,
                verifier,
                verdict,
                reason,
                created_at,
            ),
        )
    conn.close()


def get_task(task_id: str, db_path: str | None = None) -> dict[str, Any] | None:
    """Retrieve a single task and its call history."""
    conn = get_db_connection(db_path)
    cur = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    task_dict = dict(row)
    cur_calls = conn.execute(
        "SELECT * FROM calls WHERE task_id = ? ORDER BY attempt ASC", (task_id,)
    )
    task_dict["calls"] = [dict(c) for c in cur_calls.fetchall()]
    conn.close()
    return task_dict


def get_all_tasks(
    split: str | None = None,
    config: str | None = None,
    limit: int = 100,
    db_path: str | None = None,
) -> list[dict[str, Any]]:
    """Query recent tasks with optional filtering."""
    conn = get_db_connection(db_path)
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    if split:
        query += " AND split = ?"
        params.append(split)
    if config:
        query += " AND config = ?"
        params.append(config)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    cur = conn.execute(query, tuple(params))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_stats(split: str | None = None, db_path: str | None = None) -> dict[str, Any]:
    """Calculate aggregate stats for live dashboard and benchmarks."""
    conn = get_db_connection(db_path)
    where_clause = ""
    params: list[Any] = []
    if split:
        where_clause = "WHERE split = ?"
        params.append(split)

    cur = conn.execute(
        f"""
        SELECT
            COUNT(*) as total_tasks,
            COALESCE(SUM(total_cost), 0.0) as total_cost,
            COALESCE(AVG(total_latency), 0.0) as avg_latency,
            SUM(CASE WHEN needs_review = 1 THEN 1 ELSE 0 END) as needs_review_count,
            SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as correct_count,
            SUM(CASE WHEN correct IS NOT NULL THEN 1 ELSE 0 END) as evaluated_count
        FROM tasks {where_clause}
        """,
        tuple(params),
    )
    row = cur.fetchone()
    stats = dict(row) if row else {}

    # Tier distribution
    cur_tier = conn.execute(
        f"""
        SELECT final_tier, COUNT(*) as count, COALESCE(SUM(total_cost), 0.0) as cost
        FROM tasks {where_clause}
        GROUP BY final_tier
        """,
        tuple(params),
    )
    tier_counts = {r["final_tier"]: r["count"] for r in cur_tier.fetchall()}
    stats["tier_distribution"] = tier_counts

    # Accuracy percentage
    eval_count = stats.get("evaluated_count", 0)
    if eval_count and eval_count > 0:
        stats["accuracy"] = round((stats.get("correct_count", 0) / eval_count) * 100, 1)
    else:
        stats["accuracy"] = None

    conn.close()
    return stats


def reset_db(db_path: str | None = None) -> None:
    """Clear all records from tasks and calls tables."""
    conn = get_db_connection(db_path)
    with conn:
        conn.execute("DELETE FROM calls;")
        conn.execute("DELETE FROM tasks;")
    conn.close()
