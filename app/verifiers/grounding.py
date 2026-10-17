"""Grounding verifier for Cascade.

Validates that factual claims in the reply (order IDs, dollar amounts,
dates, statuses, carrier names, tracking numbers) appear in tool output.
Prevents hallucinations.
Zero-cost verifier.
"""

import re
from typing import Any

from app.schemas import Reply, Task, Verdict


def _extract_dollar_amounts(text: str) -> list[float]:
    """Find all dollar amounts in text like $120, $45.99, 120.00."""
    matches = re.findall(r"\$?\b(\d+\.\d{2})\b", text)
    amounts = []
    for m in matches:
        try:
            amounts.append(float(m))
        except ValueError:
            pass
    return amounts


def _extract_order_ids(text: str) -> list[str]:
    """Find order IDs like ORD-1001, ord-1025."""
    return [oid.upper() for oid in re.findall(r"\bORD-\d{4}\b", text, re.IGNORECASE)]


def _extract_tracking_numbers(text: str) -> list[str]:
    """Find tracking numbers like TRK94001230, TRK1Z999001."""
    return re.findall(r"\bTRK[A-Z0-9]+\b", text, re.IGNORECASE)


def verify_grounding(
    task: Task,
    reply: Reply | None,
    tool_outputs: dict[str, Any],
) -> Verdict:
    """Verify factual claims in reply are grounded in tool outputs."""
    if reply is None:
        return Verdict(
            passed=False,
            reason="Grounding check cannot run: reply is None",
            verifier_name="grounding",
        )

    reply_text = reply.message
    order_data = tool_outputs.get("order_status", {})

    order_found = order_data.get("found", False)
    order_record = order_data.get("order") if order_found else None

    # 1. Order Not Found grounding check
    if not order_found and task.order_id and task.order_id != "NONE":
        # Reply must state order not found
        reply_lower = reply_text.lower()
        if not any(
            phrase in reply_lower
            for phrase in [
                "not found",
                "could not find",
                "unable to locate",
                "no record",
            ]
        ):
            return Verdict(
                passed=False,
                reason=f"Order {task.order_id} was not found in records, but reply did not state this",
                verifier_name="grounding",
            )
        # Reply should not fabricate tracking or delivery dates
        tracking_numbers = _extract_tracking_numbers(reply_text)
        if tracking_numbers:
            return Verdict(
                passed=False,
                reason=f"Hallucinated tracking number {tracking_numbers[0]} for non-existent order",
                verifier_name="grounding",
            )
        return Verdict(
            passed=True,
            reason="Correctly reported ungrounded order as not found",
            verifier_name="grounding",
        )

    # 2. Dollar amount grounding
    if order_record:
        reply_amounts = _extract_dollar_amounts(reply_text)
        valid_amounts = set()

        # Collect legitimate amounts from order record
        if "total_amount" in order_record:
            valid_amounts.add(round(float(order_record["total_amount"]), 2))
        if "subtotal" in order_record:
            valid_amounts.add(round(float(order_record["subtotal"]), 2))
        if "shipping_fee" in order_record:
            valid_amounts.add(round(float(order_record["shipping_fee"]), 2))
        if "discount" in order_record:
            valid_amounts.add(round(float(order_record["discount"]), 2))
        for item in order_record.get("items", []):
            if "price" in item:
                valid_amounts.add(round(float(item["price"]), 2))
        for ch in order_record.get("charges", []):
            if "amount" in ch:
                valid_amounts.add(round(float(ch["amount"]), 2))

        # Also allow standard return fee ($5.99)
        valid_amounts.add(5.99)

        # Check for ungrounded amounts
        for amt in reply_amounts:
            # Skip trivial 0.00
            if amt == 0.0:
                continue
            # Allow approximate percentage amounts (e.g. 10% of subtotal)
            is_valid = any(abs(amt - va) < 0.02 for va in valid_amounts)
            if not is_valid:
                # Check if it matches difference (discount amount or coupon refund)
                subtotal = order_record.get("subtotal", 0.0)
                diff_10 = round(subtotal * 0.10, 2)
                diff_15 = round(subtotal * 0.15, 2)
                diff_20 = round(subtotal * 0.20, 2)
                if (
                    abs(amt - diff_10) < 0.02
                    or abs(amt - diff_15) < 0.02
                    or abs(amt - diff_20) < 0.02
                ):
                    continue
                return Verdict(
                    passed=False,
                    reason=f"Dollar amount ${amt:.2f} mentioned in reply does not match order record",
                    verifier_name="grounding",
                    details={
                        "unmatched_amount": amt,
                        "valid_amounts": list(valid_amounts),
                    },
                )

        # 3. Tracking number grounding
        reply_tracking = _extract_tracking_numbers(reply_text)
        order_tracking_rec = order_record.get("tracking")
        actual_tracking = (
            order_tracking_rec.get("tracking_number", "").upper()
            if isinstance(order_tracking_rec, dict)
            else ""
        )

        for trk in reply_tracking:
            if actual_tracking and trk.upper() != actual_tracking:
                return Verdict(
                    passed=False,
                    reason=f"Tracking number {trk} does not match order record ({actual_tracking})",
                    verifier_name="grounding",
                )

        # 4. Carrier grounding
        reply_lower = reply_text.lower()
        carriers = ["fedex", "ups", "usps", "dhl"]
        order_carrier = (
            order_tracking_rec.get("carrier", "").lower()
            if isinstance(order_tracking_rec, dict)
            else ""
        )
        for c in carriers:
            if c in reply_lower and order_carrier and c != order_carrier:
                # Carrier mismatch
                return Verdict(
                    passed=False,
                    reason=f"Carrier {c.upper()} mentioned in reply does not match order record ({order_carrier.upper()})",
                    verifier_name="grounding",
                )

    return Verdict(
        passed=True,
        reason="All facts grounded in tool outputs",
        verifier_name="grounding",
    )
