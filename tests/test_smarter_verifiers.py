"""Unit tests for Phase 3 smarter verifiers: consistency and judge."""

import pytest

from app.schemas import Reply, Task
from app.verifiers.consistency import verify_consistency
from app.verifiers.judge import verify_judge


@pytest.mark.asyncio
async def test_consistency_verifier_mock():
    task = Task(task_id="t_cons", ticket_text="Where is ORD-1001?", order_id="ORD-1001")
    reply = Reply(decision="inform_status", message="Delivered on Oct 14.")
    v = await verify_consistency(task, [], reply, mock=True)
    assert v.passed is True
    assert v.verifier_name == "consistency"
    assert v.cost > 0


@pytest.mark.asyncio
async def test_judge_verifier_mock_passes():
    task = Task(
        task_id="t_judge",
        ticket_text="Where is my order ORD-1001?",
        order_id="ORD-1001",
    )
    reply = Reply(
        decision="inform_status", message="Order ORD-1001 was delivered on Oct 14."
    )
    v = await verify_judge(task, reply, mock=True)
    assert v.passed is True
    assert v.verifier_name == "judge"
    assert v.cost > 0


@pytest.mark.asyncio
async def test_judge_verifier_mock_detects_missing_issue():
    # Ticket has two issues: charged twice AND when will it ship
    task = Task(
        task_id="t_judge_multi",
        ticket_text="You charged me twice for ORD-1006! Also, when will this coffee set ship?",
        order_id="ORD-1006",
    )
    # Reply only addresses the charge, ignores the shipping question
    reply = Reply(
        decision="refund_duplicate_charge",
        message="I have refunded the duplicate charge of $50.99.",
    )
    v = await verify_judge(task, reply, mock=True)
    assert v.passed is False
    assert "missing_issue" in v.reason
