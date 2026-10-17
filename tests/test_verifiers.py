"""Known-good and known-bad unit tests for Cascade free verifiers.

Tests schema, grounding, and rules verifiers.
"""

from app.schemas import Reply, Task
from app.verifiers.grounding import verify_grounding
from app.verifiers.rules import verify_rules
from app.verifiers.schema import verify_schema


# ==========================================
# Schema Verifier Tests
# ==========================================
def test_schema_verifier_known_good():
    valid_json = '{"decision": "inform_status", "message": "Your order ORD-1001 was delivered.", "order_id": "ORD-1001", "action_taken": "Informed customer"}'
    v = verify_schema(valid_json)
    assert v.passed is True
    assert v.verifier_name == "schema"
    assert v.details["reply"].decision == "inform_status"


def test_schema_verifier_with_markdown_fences():
    fenced_json = '```json\n{"decision": "inform_status", "message": "Order delivered.", "order_id": "ORD-1001"}\n```'
    v = verify_schema(fenced_json)
    assert v.passed is True


def test_schema_verifier_known_bad_invalid_json():
    bad_json = "I cannot fulfill this request as JSON."
    v = verify_schema(bad_json)
    assert v.passed is False
    assert "json" in v.reason.lower()


def test_schema_verifier_known_bad_missing_decision():
    missing_dec = '{"message": "Hello there", "order_id": "ORD-1001"}'
    v = verify_schema(missing_dec)
    assert v.passed is False
    assert "decision" in v.reason.lower()


# ==========================================
# Grounding Verifier Tests
# ==========================================
def test_grounding_verifier_known_good():
    task = Task(task_id="t1", ticket_text="Where is ORD-1001?", order_id="ORD-1001")
    reply = Reply(
        decision="inform_status",
        message="Order ORD-1001 was delivered on Oct 14 with tracking TRK94001230 via FedEx. Total was $95.98.",
        order_id="ORD-1001",
    )
    tools = {
        "order_status": {
            "found": True,
            "order": {
                "order_id": "ORD-1001",
                "total_amount": 95.98,
                "tracking": {"tracking_number": "TRK94001230", "carrier": "FedEx"},
            },
        }
    }
    v = verify_grounding(task, reply, tools)
    assert v.passed is True


def test_grounding_verifier_known_bad_hallucinated_amount():
    task = Task(task_id="t1", ticket_text="Where is ORD-1001?", order_id="ORD-1001")
    reply = Reply(
        decision="inform_status",
        message="Your total charge was $499.99 for this item.",
        order_id="ORD-1001",
    )
    tools = {
        "order_status": {
            "found": True,
            "order": {
                "order_id": "ORD-1001",
                "total_amount": 95.98,
            },
        }
    }
    v = verify_grounding(task, reply, tools)
    assert v.passed is False
    assert "499.99" in v.reason


def test_grounding_verifier_known_bad_wrong_carrier():
    task = Task(
        task_id="t1",
        ticket_text="Check shipping carrier for ORD-1001",
        order_id="ORD-1001",
    )
    reply = Reply(
        decision="inform_status",
        message="Your order was shipped using UPS with tracking TRK94001230.",
        order_id="ORD-1001",
    )
    tools = {
        "order_status": {
            "found": True,
            "order": {
                "order_id": "ORD-1001",
                "tracking": {"tracking_number": "TRK94001230", "carrier": "FedEx"},
            },
        }
    }
    v = verify_grounding(task, reply, tools)
    assert v.passed is False
    assert "carrier" in v.reason.lower()


# ==========================================
# Rules Verifier Tests
# ==========================================
def test_rules_verifier_known_good_store_credit_window():
    task = Task(task_id="t2", ticket_text="Can I return ORD-1002?", order_id="ORD-1002")
    reply = Reply(
        decision="offer_store_credit_only",
        message="Because your order was delivered 58 days ago, we can offer you store credit only.",
        order_id="ORD-1002",
    )
    tools = {
        "order_status": {
            "found": True,
            "order": {
                "order_id": "ORD-1002",
                "delivery_date": "2026-08-20",  # 58 days before Oct 17, 2026
                "status": "Delivered",
            },
        }
    }
    v = verify_rules(task, reply, tools)
    assert v.passed is True


def test_rules_verifier_known_bad_refund_outside_30_days():
    task = Task(task_id="t2", ticket_text="Can I return ORD-1002?", order_id="ORD-1002")
    reply = Reply(
        decision="approve_return_refund",
        message="Sure, I have approved a full refund to your original credit card.",
        order_id="ORD-1002",
    )
    tools = {
        "order_status": {
            "found": True,
            "order": {
                "order_id": "ORD-1002",
                "delivery_date": "2026-08-20",  # 58 days ago
                "status": "Delivered",
            },
        }
    }
    v = verify_rules(task, reply, tools)
    assert v.passed is False
    assert "refund approved outside 30-day window" in v.reason.lower()


def test_rules_verifier_known_bad_return_past_60_days():
    task = Task(task_id="t3", ticket_text="Return ORD-1003", order_id="ORD-1003")
    reply = Reply(
        decision="approve_return_refund",
        message="Return approved! Here is your return label.",
        order_id="ORD-1003",
    )
    tools = {
        "order_status": {
            "found": True,
            "order": {
                "order_id": "ORD-1003",
                "delivery_date": "2026-07-06",  # >100 days ago
                "status": "Delivered",
            },
        }
    }
    v = verify_rules(task, reply, tools)
    assert v.passed is False
    assert "outside 60-day limit" in v.reason.lower()


def test_rules_verifier_known_bad_cancel_shipped_order():
    task = Task(task_id="t5", ticket_text="Cancel order ORD-1005", order_id="ORD-1005")
    reply = Reply(
        decision="cancel_order_approved",
        message="Your cancellation is approved and your order has been cancelled.",
        order_id="ORD-1005",
    )
    tools = {
        "order_status": {
            "found": True,
            "order": {
                "order_id": "ORD-1005",
                "status": "In Transit",
            },
        }
    }
    v = verify_rules(task, reply, tools)
    assert v.passed is False
    assert "cannot cancel order" in v.reason.lower()
