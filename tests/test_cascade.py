"""Unit tests for Cascade controller loop.

Verifies:
1. Pass at Nano
2. Escalate once to Super
3. Escalate twice to Ultra
4. Final-tier failure (flagged needs_review=True)
5. Feedback passing in prompts
"""

import pytest

from app.cascade import run_cascade
from app.schemas import ModelResult, Task


@pytest.mark.asyncio
async def test_cascade_pass_at_nano(monkeypatch):
    """Test task passing on first tier (Nano)."""

    async def fake_call_model(tier, messages, **kwargs):
        return ModelResult(
            text='{"decision": "inform_status", "message": "Order ORD-1001 was Delivered on Oct 14.", "order_id": "ORD-1001"}',
            tokens_in=50,
            tokens_out=25,
            cost=0.00001,
            latency=0.3,
        )

    monkeypatch.setattr("app.cascade.call_model", fake_call_model)

    task = Task(
        task_id="t_pass_nano",
        ticket_text="Where is my order ORD-1001?",
        order_id="ORD-1001",
    )
    result = await run_cascade(task)

    assert result.tier == "nano"
    assert result.attempts == 1
    assert result.needs_review is False
    assert len(result.history) == 1
    assert result.history[0].verdict == "pass"


@pytest.mark.asyncio
async def test_cascade_escalate_once(monkeypatch):
    """Test Nano failing schema and Super passing."""
    attempts = []

    async def fake_call_model(tier, messages, **kwargs):
        attempts.append(tier)
        if tier == "nano":
            # Invalid JSON
            return ModelResult(
                text="Sorry I am just a plain text answer with no JSON",
                cost=0.00001,
                latency=0.2,
            )
        else:
            # Super provides valid JSON
            return ModelResult(
                text='{"decision": "inform_status", "message": "Order ORD-1001 was Delivered on Oct 14 via FedEx.", "order_id": "ORD-1001"}',
                cost=0.00005,
                latency=0.5,
            )

    monkeypatch.setattr("app.cascade.call_model", fake_call_model)

    task = Task(
        task_id="t_esc_once",
        ticket_text="Where is my order ORD-1001?",
        order_id="ORD-1001",
    )
    result = await run_cascade(task)

    assert result.tier == "super"
    assert result.attempts == 2
    assert result.needs_review is False
    assert len(result.history) == 2
    assert result.history[0].verdict == "fail"
    assert result.history[1].verdict == "pass"


@pytest.mark.asyncio
async def test_cascade_escalate_twice_to_ultra(monkeypatch):
    """Test Nano and Super failing rules, Ultra passing."""
    call_tiers = []

    async def fake_call_model(tier, messages, **kwargs):
        call_tiers.append(tier)
        if tier == "nano":
            # Policy violation: Approving cash refund for 58-day old order
            return ModelResult(
                text='{"decision": "approve_return_refund", "message": "Refund to your credit card is approved.", "order_id": "ORD-1002"}',
                cost=0.00001,
                latency=0.2,
            )
        elif tier == "super":
            # Grounding violation: Hallucinating wrong tracking
            return ModelResult(
                text='{"decision": "offer_store_credit_only", "message": "Store credit approved with fake TRK99999999.", "order_id": "ORD-1002"}',
                cost=0.00005,
                latency=0.5,
            )
        else:
            # Ultra gets it completely right
            return ModelResult(
                text='{"decision": "offer_store_credit_only", "message": "Delivered 58 days ago on Aug 20. Eligible for store credit only.", "order_id": "ORD-1002"}',
                cost=0.00020,
                latency=1.0,
            )

    monkeypatch.setattr("app.cascade.call_model", fake_call_model)

    task = Task(
        task_id="t_esc_ultra",
        ticket_text="Can I return ORD-1002 for a refund?",
        order_id="ORD-1002",
    )
    result = await run_cascade(task)

    assert result.tier == "ultra"
    assert result.attempts == 3
    assert result.needs_review is False
    assert len(result.history) == 3
    assert result.history[0].verdict == "fail"
    assert result.history[1].verdict == "fail"
    assert result.history[2].verdict == "pass"


@pytest.mark.asyncio
async def test_cascade_final_tier_failure_needs_review(monkeypatch):
    """Test all tiers failing and triggering needs_review=True."""

    async def fake_call_model(tier, messages, **kwargs):
        return ModelResult(text="Corrupt non-json response", cost=0.00001, latency=0.2)

    monkeypatch.setattr("app.cascade.call_model", fake_call_model)

    task = Task(
        task_id="t_fail_all",
        ticket_text="Help with order ORD-1001",
        order_id="ORD-1001",
    )
    result = await run_cascade(task)

    assert result.tier == "ultra"
    assert result.attempts == 3
    assert result.needs_review is True
    assert all(h.verdict == "fail" for h in result.history)


@pytest.mark.asyncio
async def test_cascade_feedback_passing(monkeypatch):
    """Test that failure reason is passed into the next tier prompt."""
    prompts_seen = []

    async def fake_call_model(tier, messages, **kwargs):
        prompts_seen.append((tier, messages[0]["content"]))
        if tier == "nano":
            return ModelResult(
                text='{"decision": "approve_return_refund", "message": "Full refund approved.", "order_id": "ORD-1002"}',
                cost=0.00001,
            )
        return ModelResult(
            text='{"decision": "offer_store_credit_only", "message": "Store credit only.", "order_id": "ORD-1002"}',
            cost=0.00005,
        )

    monkeypatch.setattr("app.cascade.call_model", fake_call_model)

    task = Task(
        task_id="t_feedback", ticket_text="Return ORD-1002", order_id="ORD-1002"
    )
    await run_cascade(task)

    assert len(prompts_seen) == 2
    super_prompt = prompts_seen[1][1]
    assert "CRITICAL ESCALATION FEEDBACK" in super_prompt
    assert "Refund approved outside 30-day window" in super_prompt
