"""Unit tests for predict-then-route classifier (app/router.py)."""

import pytest

from app.cascade import run_cascade
from app.router import extract_features, predict_starting_tier
from app.schemas import Task


def test_router_extract_features_easy():
    text = "Hi, can you tell me where order ORD-1001 is right now?"
    feats = extract_features(text)
    assert feats.order_id_count == 1
    assert feats.multi_issue_keyword_count == 0
    tier = predict_starting_tier(text)
    assert tier == "nano"


def test_router_predict_medium_policy():
    text = "I received order ORD-1005 35 days ago and need a return or refund."
    feats = extract_features(text)
    assert feats.policy_keyword_count >= 1
    tier = predict_starting_tier(text)
    assert tier in ("super", "ultra")


def test_router_predict_hard_multi_issue():
    text = (
        "Order ORD-1001 arrived damaged and broken with scratches, "
        "and I was also charged twice on order ORD-1002. This is fraud!"
    )
    feats = extract_features(text)
    assert feats.order_id_count == 2
    assert feats.multi_issue_keyword_count >= 2
    tier = predict_starting_tier(text)
    assert tier == "ultra"


@pytest.mark.asyncio
async def test_cascade_predict_first_strategy_mock():
    # Ticket predicting ultra starting tier should bypass nano and super
    hard_ticket = (
        "Order ORD-1001 was damaged, and order ORD-1002 was charged twice. Fraud!"
    )
    task = Task(task_id="test_pred_001", ticket_text=hard_ticket)
    result = await run_cascade(task, mock=True, strategy="predict_first")
    assert result.task_id == "test_pred_001"
    assert result.tier == "ultra"
    # Starting tier should be ultra, so attempts should only test ultra
    assert result.attempts == 1
    assert len(result.history) == 1
    assert result.history[0].tier == "ultra"
