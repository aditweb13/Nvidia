"""Unit tests for app/db.py SQLite operations."""

from pathlib import Path

from app.db import (
    get_all_tasks,
    get_stats,
    get_task,
    init_db,
    log_call,
    log_task,
    reset_db,
)


def test_db_lifecycle(tmp_path: Path):
    db_file = str(tmp_path / "test_cascade.db")
    init_db(db_file)

    # Log a task
    log_task(
        task_id="t_001",
        ticket_text="Where is my order ORD-1001?",
        split="dev",
        config="cascade",
        final_tier="nano",
        final_reply="Delivered on Oct 14",
        needs_review=False,
        total_cost=0.000025,
        total_latency=1.2,
        correct=1,
        db_path=db_file,
    )

    # Log calls
    log_call(
        task_id="t_001",
        attempt=1,
        tier="nano",
        tokens_in=50,
        tokens_out=30,
        cost=0.000025,
        latency=1.2,
        verifier="schema",
        verdict="pass",
        reason="Valid schema and grounding",
        db_path=db_file,
    )

    # Retrieve task
    task = get_task("t_001", db_path=db_file)
    assert task is not None
    assert task["task_id"] == "t_001"
    assert task["final_tier"] == "nano"
    assert len(task["calls"]) == 1
    assert task["calls"][0]["verdict"] == "pass"

    # Query all tasks
    tasks = get_all_tasks(split="dev", db_path=db_file)
    assert len(tasks) == 1

    # Check stats
    stats = get_stats(split="dev", db_path=db_file)
    assert stats["total_tasks"] == 1
    assert stats["tier_distribution"]["nano"] == 1
    assert stats["accuracy"] == 100.0

    # Reset
    reset_db(db_file)
    assert len(get_all_tasks(db_path=db_file)) == 0
