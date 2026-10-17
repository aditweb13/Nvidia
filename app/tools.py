"""Mock tools for ShopEasy customer support scenario.

Tools:
- get_order_status(order_id: str) -> dict
- get_policy(topic: str) -> str
"""

import json
from pathlib import Path
from typing import Any

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_ORDERS_FILE = _DATA_DIR / "orders.json"
_POLICY_FILE = _DATA_DIR / "policy.md"

_orders_cache: dict[str, dict[str, Any]] | None = None
_policy_cache: str | None = None


def _load_orders() -> dict[str, dict[str, Any]]:
    global _orders_cache
    if _orders_cache is None:
        if not _ORDERS_FILE.exists():
            return {}
        with open(_ORDERS_FILE, "r", encoding="utf-8") as f:
            orders_list: list[dict[str, Any]] = json.load(f)
            _orders_cache = {order["order_id"]: order for order in orders_list}
    return _orders_cache


def _load_policy() -> str:
    global _policy_cache
    if _policy_cache is None:
        if not _POLICY_FILE.exists():
            return ""
        with open(_POLICY_FILE, "r", encoding="utf-8") as f:
            _policy_cache = f.read()
    return _policy_cache


def get_order_status(order_id: str) -> dict[str, Any]:
    """Retrieve detailed order information for a given order ID.

    Returns the order dictionary if found, or an error status dictionary
    if not found.
    """
    orders = _load_orders()
    clean_id = order_id.strip().upper()
    if clean_id in orders:
        return {"found": True, "order": orders[clean_id]}
    return {"found": False, "error": f"Order {order_id} not found"}


def get_policy(topic: str) -> dict[str, Any]:
    """Retrieve policy guidelines for a given topic.

    Topics include: 'returns', 'refunds', 'damaged', 'duplicate_charge',
    'cancellation', 'shipping', 'coupons'.
    """
    full_policy = _load_policy()
    topic_lower = topic.strip().lower()

    # Search for section matching topic
    sections = full_policy.split("## ")
    matching_sections = []
    for sec in sections:
        if not sec.strip():
            continue
        first_line = sec.split("\n")[0].lower()
        if any(
            term in first_line or term in sec.lower() for term in topic_lower.split()
        ):
            matching_sections.append("## " + sec.strip())

    if matching_sections:
        return {
            "found": True,
            "topic": topic,
            "content": "\n\n".join(matching_sections),
        }
    return {"found": True, "topic": topic, "content": full_policy}
