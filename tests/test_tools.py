"""Unit tests for app/tools.py."""

from app.tools import get_order_status, get_policy


def test_get_order_status_found():
    res = get_order_status("ORD-1001")
    assert res["found"] is True
    order = res["order"]
    assert order["order_id"] == "ORD-1001"
    assert order["customer"]["name"] == "Alice Johnson"
    assert order["status"] == "Delivered"
    assert order["total_amount"] == 95.98


def test_get_order_status_case_insensitive():
    res = get_order_status("ord-1002")
    assert res["found"] is True
    assert res["order"]["order_id"] == "ORD-1002"


def test_get_order_status_not_found():
    res = get_order_status("ORD-9999")
    assert res["found"] is False
    assert "not found" in res["error"].lower()


def test_get_policy_returns():
    res = get_policy("returns")
    assert res["found"] is True
    content = res["content"].lower()
    assert "30 days" in content
    assert "store credit" in content


def test_get_policy_damaged():
    res = get_policy("damaged")
    assert res["found"] is True
    content = res["content"].lower()
    assert "damaged" in content
    assert "7 days" in content


def test_get_policy_duplicate_charge():
    res = get_policy("duplicate charges")
    assert res["found"] is True
    content = res["content"].lower()
    assert "duplicate charge" in content or "duplicate" in content
