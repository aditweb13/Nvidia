"""Unit tests for eval/grader.py."""

from eval.grader import grade_reply


def test_grade_reply_passing():
    gold = {
        "decision": "inform_status",
        "required_facts": ["Delivered", "Oct 14", "FedEx", "TRK94001230"],
        "checklist": [
            "State delivery date",
            "Mention tracking number",
            "Confirm delivered",
        ],
    }
    reply = "Hello Alice! Your order ORD-1001 was Delivered on Oct 14 via FedEx with tracking number TRK94001230."
    res = grade_reply(reply, gold, reply_decision="inform_status")
    assert res.passed is True
    assert res.decision_correct is True
    assert len(res.facts_present) == 4
    assert len(res.facts_missing) == 0
    assert res.score >= 0.9


def test_grade_reply_wrong_decision():
    gold = {
        "decision": "deny_return_past_window",
        "required_facts": ["ineligible", "60 days"],
        "checklist": ["Deny return", "Explain over 60 days"],
    }
    reply = "Sure! I have approved your full refund to your original credit card."
    res = grade_reply(reply, gold, reply_decision="approve_return_refund")
    assert res.passed is False
    assert res.decision_correct is False


def test_grade_reply_missing_facts():
    gold = {
        "decision": "inform_status",
        "required_facts": ["Delivered", "Oct 14", "FedEx", "TRK94001230"],
        "checklist": ["State delivery date"],
    }
    reply = "Your order was shipped a while ago."
    res = grade_reply(reply, gold, reply_decision="inform_status")
    assert res.passed is False
    assert len(res.facts_missing) > 1
