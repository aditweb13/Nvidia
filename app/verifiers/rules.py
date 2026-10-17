"""Policy rules verifier for Cascade.

Implements deterministic logic checks based on ShopEasy policies:
- refund_window: 0-30 days full refund
- store_credit_window: 31-60 days store credit only; >60 days ineligible
- cancellation: only Pending or Processing can be cancelled
- damaged: reported within 7 days eligible for free replacement/refund with waived return fee
Zero-cost verifier.
"""

from datetime import datetime
from typing import Any

from app.schemas import Reply, Task, Verdict

# Fixed reference date for ShopEasy demo evaluations: Oct 17, 2026
_REFERENCE_DATE = datetime(2026, 10, 17)


def _calculate_days_since(date_str: str) -> int | None:
    """Calculate days between reference date and given ISO date (YYYY-MM-DD)."""
    try:
        dt = datetime.strptime(date_str.split("T")[0].split()[0], "%Y-%m-%d")
        return (_REFERENCE_DATE - dt).days
    except (ValueError, TypeError):
        return None


def verify_rules(
    task: Task,
    reply: Reply | None,
    tool_outputs: dict[str, Any],
) -> Verdict:
    """Validate policy rules against order status and model reply."""
    if reply is None:
        return Verdict(
            passed=False,
            reason="Rules check cannot run: reply is None",
            verifier_name="rules",
        )

    order_data = tool_outputs.get("order_status", {})
    if not order_data.get("found"):
        # Order not found tasks are covered by grounding verifier
        return Verdict(
            passed=True,
            reason="Order not found, no policy rules to violate",
            verifier_name="rules",
        )

    order = order_data.get("order", {})
    delivery_date = order.get("delivery_date")
    status = order.get("status", "")
    decision = reply.decision.lower()
    msg_lower = reply.message.lower()

    # Rule 1: Return & Refund Windows
    if delivery_date:
        days = _calculate_days_since(delivery_date)
        if days is not None:
            # Case A: Delivered > 60 days ago
            if days > 60:
                if any(
                    kw in decision for kw in ["approve", "refund", "credit", "exchange"]
                ) or any(
                    kw in msg_lower
                    for kw in [
                        "refund approved",
                        "store credit approved",
                        "return approved",
                        "here is your return label",
                    ]
                ):
                    return Verdict(
                        passed=False,
                        reason=f"Policy violation: Return or credit approved for item delivered {days} days ago (outside 60-day limit)",
                        verifier_name="rules",
                        details={
                            "rule": "rules.store_credit_window",
                            "days_since_delivery": days,
                        },
                    )

            # Case B: Delivered between 31 and 60 days ago
            elif 30 < days <= 60:
                # Must NOT approve full cash/card refund
                approved_cash_refund = (
                    "approve_return_refund" in decision
                    or "full refund" in msg_lower
                    or "refund to your original" in msg_lower
                    or "refund to your card" in msg_lower
                ) and "store credit only" not in msg_lower
                if approved_cash_refund:
                    return Verdict(
                        passed=False,
                        reason=f"Policy violation: Refund approved outside 30-day window ({days} days since delivery). Must offer store credit only.",
                        verifier_name="rules",
                        details={
                            "rule": "rules.refund_window",
                            "days_since_delivery": days,
                        },
                    )

    # Rule 2: Order Cancellation Eligibility
    if (
        ("cancel" in decision or "cancellation" in msg_lower)
        and status in ["Shipped", "In Transit", "Delivered"]
        and (
            "cancel_order_approved" in decision
            or any(
                w in msg_lower
                for w in [
                    "order has been cancelled",
                    "order is cancelled",
                    "cancellation approved",
                ]
            )
        )
    ):
        return Verdict(
            passed=False,
            reason=f"Policy violation: Cannot cancel order in '{status}' status. Customer must return item after delivery.",
            verifier_name="rules",
            details={"rule": "rules.cancellation", "order_status": status},
        )

    # Rule 3: Damaged Items
    is_damaged_complaint = any(
        kw in task.ticket_text.lower()
        for kw in ["damaged", "broken", "shattered", "defective", "stained"]
    )
    if is_damaged_complaint and delivery_date:
        days = _calculate_days_since(delivery_date)
        if (
            days is not None
            and days <= 7
            and (
                "5.99 return shipping fee will be deducted" in msg_lower
                or "deducting $5.99" in msg_lower
            )
        ):
            return Verdict(
                passed=False,
                reason="Policy violation: Return fee deducted for item reported damaged within 7 days",
                verifier_name="rules",
                details={"rule": "rules.damaged", "days_since_delivery": days},
            )

    # Rule 4: Duplicate Charge handling
    charges = order.get("charges", [])
    if (
        len(charges) > 1
        and "twice" in task.ticket_text.lower()
        and ("deny" in decision or "no record of double charge" in msg_lower)
    ):
        return Verdict(
            passed=False,
            reason="Policy violation: Denied duplicate charge when order has multiple captured charges",
            verifier_name="rules",
            details={
                "rule": "rules.duplicate_charge",
                "charge_count": len(charges),
            },
        )

    return Verdict(
        passed=True, reason="All policy rules satisfied", verifier_name="rules"
    )
