"""Cascade Controller: Cost-aware model routing state machine.

Interface:
    run_cascade(task) -> CascadeResult

Logic:
1. Starts at cheapest tier (Nemotron Nano by default).
2. Runs layered verifiers (schema -> grounding -> rules) cheapest first.
3. On pass: returns answer immediately.
4. On failure: escalates to Super, then Ultra, passing the failure reason.
5. If final tier fails: returns answer with needs_review=True.
6. Logs every attempt and final task to SQLite.
"""

import json
import logging
import time
from typing import Any

from app.config import get_yaml_config
from app.db import log_call, log_task
from app.models import call_model
from app.schemas import AttemptRecord, CascadeResult, Reply, Task, Verdict
from app.tools import get_order_status, get_policy
from app.verifiers import run_verifiers
from app.verifiers.schema import extract_json_from_text

logger = logging.getLogger("cascade.controller")

_BASE_SYSTEM_PROMPT = """You are a ShopEasy customer service AI.
Your goal is to answer customer questions accurately and resolve tickets adhering strictly to store policies.
Always check provided order and policy details before making promises.

Return your response ONLY as a JSON object formatted as:
{
  "decision": "string (inform_status | approve_return_refund | offer_store_credit_only | deny_return_past_window | cancel_order_approved | deny_cancellation_in_transit | refund_duplicate_charge | approve_damaged_remedy | declare_lost_package | order_not_found)",
  "message": "string (polite, complete customer-facing response)",
  "order_id": "string or null",
  "action_taken": "string summary"
}
"""


def _build_prompt_context(task: Task) -> tuple[str, dict[str, Any]]:
    """Gather tool context and construct system message."""
    tool_outputs: dict[str, Any] = {}
    context_str = ""

    # 1. Fetch order status if order_id is present
    if task.order_id and task.order_id.upper() != "NONE":
        order_info = get_order_status(task.order_id)
        tool_outputs["order_status"] = order_info
        context_str += (
            f"\n\n[Order Status Records]:\n{json.dumps(order_info, indent=2)}"
        )
    else:
        # Check if an order ID is mentioned in ticket text
        import re

        match = re.search(r"\b(ORD-\d{4})\b", task.ticket_text, re.IGNORECASE)
        if match:
            found_id = match.group(1).upper()
            order_info = get_order_status(found_id)
            tool_outputs["order_status"] = order_info
            context_str += (
                f"\n\n[Order Status Records]:\n{json.dumps(order_info, indent=2)}"
            )

    # 2. Fetch relevant policy
    ticket_lower = task.ticket_text.lower()
    topic = "returns"
    if any(
        w in ticket_lower
        for w in ["damage", "broken", "shattered", "stain", "defective"]
    ):
        topic = "damaged"
    elif any(w in ticket_lower for w in ["twice", "double", "duplicate"]):
        topic = "duplicate_charge"
    elif "cancel" in ticket_lower:
        topic = "cancellation"
    elif any(w in ticket_lower for w in ["coupon", "discount", "promo"]):
        topic = "coupons"
    elif any(w in ticket_lower for w in ["shipping", "lost", "delay", "carrier"]):
        topic = "shipping"

    policy_info = get_policy(topic)
    tool_outputs["policy"] = policy_info
    context_str += (
        f"\n\n[Store Policy Guidelines]:\n{policy_info.get('content', '')[:1200]}"
    )

    return context_str, tool_outputs


async def run_cascade(
    task_input: Task | str,
    mock: bool = False,
    use_cache: bool | None = None,
) -> CascadeResult:
    """Execute the Cascade routing state machine for a single task."""
    if isinstance(task_input, str):
        task = Task(task_id=f"live_{int(time.time()*1000)}", ticket_text=task_input)
    else:
        task = task_input

    yaml_config = get_yaml_config()
    tiers: list[str] = yaml_config.get("routing", {}).get(
        "tiers", ["nano", "super", "ultra"]
    )

    context_str, tool_outputs = _build_prompt_context(task)

    history: list[AttemptRecord] = []
    total_cost = 0.0
    total_latency = 0.0
    feedback_reason: str | None = None
    last_reply_text = ""
    last_parsed_reply: Reply | None = None
    last_tier = tiers[0]

    for attempt_idx, tier in enumerate(tiers, 1):
        last_tier = tier
        attempt_start = time.perf_counter()

        # Build prompt with previous failure feedback if escalating
        system_prompt = _BASE_SYSTEM_PROMPT + context_str
        if feedback_reason:
            system_prompt += (
                f"\n\n[CRITICAL ESCALATION FEEDBACK - PREVIOUS TIER REJECTED]:\n"
                f"Your previous tier failed with error: '{feedback_reason}'.\n"
                f"Carefully correct this error and ensure strict adherence to store policy rules."
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task.ticket_text},
        ]

        logger.info(
            "Task %s -> Attempt %d: Calling tier %s (feedback=%s)",
            task.task_id,
            attempt_idx,
            tier.upper(),
            bool(feedback_reason),
        )

        try:
            model_res = await call_model(
                tier=tier,
                messages=messages,
                mock=mock,
                use_cache=use_cache,
            )
            raw_text = model_res.text
            call_cost = model_res.cost
            call_latency = model_res.latency
            tokens_in = model_res.tokens_in
            tokens_out = model_res.tokens_out
        except Exception as e:  # noqa: BLE001
            # Model error after retries: escalate with model_error reason
            logger.warning(
                "Task %s attempt %d on %s failed with model error: %s",
                task.task_id,
                attempt_idx,
                tier,
                e,
            )
            call_latency = time.perf_counter() - attempt_start
            call_cost = 0.0
            tokens_in = 0
            tokens_out = 0
            raw_text = f"Model execution error: {e}"
            verdict = Verdict(
                passed=False,
                reason=f"model_error: {e}",
                verifier_name="system",
            )
            total_latency += call_latency
            log_call(
                task_id=task.task_id,
                attempt=attempt_idx,
                tier=tier,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                latency=call_latency,
                verifier="system",
                verdict="fail",
                reason=verdict.reason,
            )
            history.append(
                AttemptRecord(
                    tier=tier,
                    verdict="fail",
                    reason=verdict.reason,
                    cost=0.0,
                    latency=call_latency,
                    tokens_in=0,
                    tokens_out=0,
                )
            )
            feedback_reason = "model_error"
            continue

        last_reply_text = raw_text
        total_cost += call_cost
        total_latency += call_latency

        # Try parsing reply into Pydantic model
        parsed_reply = None
        try:
            json_str = extract_json_from_text(raw_text)
            data = json.loads(json_str)
            if isinstance(data, dict):
                parsed_reply = Reply(**data)
                last_parsed_reply = parsed_reply
        except (json.JSONDecodeError, TypeError, ValueError) as parse_err:
            logger.debug("Structured reply parse failed on %s: %s", tier, parse_err)

        # Run layered verifiers
        verdict = run_verifiers(
            task=task,
            reply=parsed_reply,
            tool_outputs=tool_outputs,
            raw_text=raw_text,
        )

        # Count extra verifier cost if any
        if verdict.cost > 0:
            total_cost += verdict.cost

        # Log attempt call
        log_call(
            task_id=task.task_id,
            attempt=attempt_idx,
            tier=tier,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost=call_cost + verdict.cost,
            latency=call_latency,
            verifier=verdict.verifier_name,
            verdict="pass" if verdict.passed else "fail",
            reason=verdict.reason,
        )

        history.append(
            AttemptRecord(
                tier=tier,
                verdict="pass" if verdict.passed else "fail",
                reason=verdict.reason,
                cost=round(call_cost + verdict.cost, 6),
                latency=round(call_latency, 3),
                tokens_in=tokens_in,
                tokens_out=tokens_out,
            )
        )

        # Pass condition: return immediately
        if verdict.passed:
            logger.info(
                "Task %s PASSED at tier %s (cost=$%.6f)",
                task.task_id,
                tier.upper(),
                total_cost,
            )
            final_message = parsed_reply.message if parsed_reply else raw_text
            log_task(
                task_id=task.task_id,
                ticket_text=task.ticket_text,
                split=task.split or "live",
                config="cascade",
                final_tier=tier,
                final_reply=final_message,
                needs_review=False,
                total_cost=round(total_cost, 6),
                total_latency=round(total_latency, 3),
            )
            return CascadeResult(
                task_id=task.task_id,
                answer=final_message,
                tier=tier,
                attempts=attempt_idx,
                cost=round(total_cost, 6),
                latency=round(total_latency, 3),
                needs_review=False,
                history=history,
                reply=parsed_reply,
            )

        # Escalation: pass failure reason to next tier
        feedback_reason = verdict.reason
        logger.info(
            "Task %s REJECTED at tier %s: '%s' -> Escalating...",
            task.task_id,
            tier.upper(),
            verdict.reason,
        )

    # If all tiers failed, flag for human review
    logger.warning("Task %s failed all tiers. Flagging for human review.", task.task_id)
    final_message = last_parsed_reply.message if last_parsed_reply else last_reply_text
    log_task(
        task_id=task.task_id,
        ticket_text=task.ticket_text,
        split=task.split or "live",
        config="cascade",
        final_tier=last_tier,
        final_reply=final_message,
        needs_review=True,
        total_cost=round(total_cost, 6),
        total_latency=round(total_latency, 3),
    )
    return CascadeResult(
        task_id=task.task_id,
        answer=final_message,
        tier=last_tier,
        attempts=len(tiers),
        cost=round(total_cost, 6),
        latency=round(total_latency, 3),
        needs_review=True,
        history=history,
        reply=last_parsed_reply,
    )
