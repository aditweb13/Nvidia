"""Benchmark runner for Cascade and single-model baselines.

Evaluates 4 configurations:
1. nano (Nemotron Nano only)
2. super (Nemotron Super only)
3. ultra (Nemotron Ultra only)
4. cascade (Cascade try-cheap-first controller)

Usage:
    python eval/run_eval.py --split dev --config ultra
    python eval/run_eval.py --split dev --config all --mock
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.cascade import run_cascade
from app.db import init_db, log_call, log_task
from app.models import call_model
from app.schemas import Task
from app.tools import get_order_status, get_policy
from eval.grader import grade_reply

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("cascade.eval")

_SYSTEM_PROMPT = """You are a ShopEasy customer service AI.
Your role is to help customers with order tracking, return requests, damaged items, cancellations, and billing.
Always verify facts using the provided tools before making promises.

Return a JSON object with:
{
  "decision": "string (inform_status | approve_return_refund | offer_store_credit_only | deny_return_past_window | cancel_order_approved | deny_cancellation_in_transit | refund_duplicate_charge | approve_damaged_remedy | declare_lost_package | order_not_found)",
  "message": "string (polite customer message with all dates, amounts, and tracking details)",
  "order_id": "string or null",
  "action_taken": "string summary"
}
"""


def _load_tasks(tasks_path: Path, split: str) -> list[dict[str, Any]]:
    tasks = []
    with open(tasks_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                t = json.loads(line)
                if t.get("split") == split:
                    tasks.append(t)
    return tasks


async def run_single_model_task(
    task: dict[str, Any],
    tier: str,
    mock: bool = False,
    use_cache: bool = True,
) -> dict[str, Any]:
    task_id = task["task_id"]
    ticket_text = task["ticket_text"]
    order_id = task.get("order_id")
    gold = task["gold"]

    # Gather tool context if an order ID is present
    tool_context = ""
    if order_id and order_id != "NONE":
        order_info = get_order_status(order_id)
        tool_context += f"\n[Tool Output - Order Status]: {json.dumps(order_info)}"

    # Determine topic and fetch policy context
    topic = "returns"
    if (
        "damage" in ticket_text.lower()
        or "shatter" in ticket_text.lower()
        or "broken" in ticket_text.lower()
    ):
        topic = "damaged"
    elif "twice" in ticket_text.lower() or "duplicate" in ticket_text.lower():
        topic = "duplicate_charge"
    elif "cancel" in ticket_text.lower():
        topic = "cancellation"
    elif "coupon" in ticket_text.lower() or "discount" in ticket_text.lower():
        topic = "coupons"

    policy_info = get_policy(topic)
    tool_context += (
        f"\n[Tool Output - Store Policy]:\n{policy_info.get('content', '')[:1000]}"
    )

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT + tool_context},
        {"role": "user", "content": ticket_text},
    ]

    model_result = await call_model(
        tier=tier,
        messages=messages,
        mock=mock,
        use_cache=use_cache,
    )

    # Parse reply JSON
    reply_decision = None
    reply_message = model_result.text
    try:
        parsed = json.loads(model_result.text)
        if isinstance(parsed, dict):
            reply_decision = parsed.get("decision")
            reply_message = parsed.get("message", model_result.text)
    except (json.JSONDecodeError, TypeError, ValueError):
        logger.debug(
            "Failed parsing structured JSON from model reply: %s",
            model_result.text[:100],
        )

    # Grade
    grade = grade_reply(
        reply_text=reply_message,
        gold=gold,
        reply_decision=reply_decision,
    )

    # Log to SQLite
    log_task(
        task_id=f"{task_id}_{tier}",
        ticket_text=ticket_text,
        split=task.get("split", "dev"),
        config=tier,
        final_tier=tier,
        final_reply=reply_message,
        needs_review=not grade.passed,
        total_cost=model_result.cost,
        total_latency=model_result.latency,
        correct=1 if grade.passed else 0,
    )
    log_call(
        task_id=f"{task_id}_{tier}",
        attempt=1,
        tier=tier,
        tokens_in=model_result.tokens_in,
        tokens_out=model_result.tokens_out,
        cost=model_result.cost,
        latency=model_result.latency,
        verifier="grader",
        verdict="pass" if grade.passed else "fail",
        reason="Deterministic benchmark grading",
    )

    return {
        "task_id": task_id,
        "tier": tier,
        "passed": grade.passed,
        "score": grade.score,
        "cost": model_result.cost,
        "latency": model_result.latency,
        "reply": reply_message,
        "decision": reply_decision,
    }


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def run_evaluation_sync(
    split: str = "dev",
    config: str = "ultra",
    mock: bool = False,
    limit: int | None = None,
):
    asyncio.run(
        _run_evaluation_async(
            split=split,
            config=config,
            mock=mock,
            limit=limit,
        )
    )


async def _run_evaluation_async(
    split: str = "dev",
    config: str = "ultra",
    mock: bool = False,
    limit: int | None = None,
):
    tasks_path = Path(__file__).resolve().parent / "tasks.jsonl"
    tasks = _load_tasks(tasks_path, split)

    if limit:
        tasks = tasks[:limit]

    logger.info(
        "Loaded %d tasks for split=%s (config=%s, mock=%s)",
        len(tasks),
        split,
        config,
        mock,
    )
    init_db()

    configs_to_run = (
        ["nano", "super", "ultra", "cascade"] if config == "all" else [config]
    )
    results_dir = Path(__file__).resolve().parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    summary_records = {}

    for cfg in configs_to_run:
        logger.info("=== Running evaluation for config: %s ===", cfg.upper())
        cfg_results = []
        for i, t in enumerate(tasks, 1):
            try:
                if cfg == "cascade":
                    task_obj = Task(
                        task_id=t["task_id"],
                        ticket_text=t["ticket_text"],
                        order_id=t.get("order_id"),
                        split=split,
                        config="cascade",
                    )
                    c_res = await run_cascade(task_obj, mock=mock)
                    # Grade with gold
                    reply_dec = c_res.reply.decision if c_res.reply else None
                    grade = grade_reply(
                        c_res.answer, t["gold"], reply_decision=reply_dec
                    )
                    res = {
                        "task_id": t["task_id"],
                        "tier": c_res.tier,
                        "attempts": c_res.attempts,
                        "passed": grade.passed,
                        "score": grade.score,
                        "cost": c_res.cost,
                        "latency": c_res.latency,
                        "needs_review": c_res.needs_review,
                        "reply": c_res.answer,
                        "decision": reply_dec,
                    }
                else:
                    res = await run_single_model_task(t, tier=cfg, mock=mock)
            except Exception as e:  # noqa: BLE001
                logger.error("Task %s failed after retries: %s", t["task_id"], e)
                res = {
                    "task_id": t["task_id"],
                    "tier": cfg,
                    "passed": False,
                    "score": 0.0,
                    "cost": 0.0,
                    "latency": 0.0,
                    "reply": f"Model error: {e}",
                    "decision": "model_error",
                }
            cfg_results.append(res)
            logger.info(
                "[%d/%d] %s (%s) -> Passed: %s, Score: %.2f, Cost: $%.6f, Latency: %.2fs",
                i,
                len(tasks),
                t["task_id"],
                cfg,
                res["passed"],
                res["score"],
                res["cost"],
                res["latency"],
            )

        total_tasks = len(cfg_results)
        passed_count = sum(1 for r in cfg_results if r["passed"])
        accuracy = (passed_count / total_tasks * 100) if total_tasks else 0.0
        total_cost = sum(r["cost"] for r in cfg_results)
        avg_latency = (
            (sum(r["latency"] for r in cfg_results) / total_tasks)
            if total_tasks
            else 0.0
        )

        summary = {
            "config": cfg,
            "split": split,
            "total_tasks": total_tasks,
            "passed": passed_count,
            "accuracy": round(accuracy, 2),
            "total_cost": round(total_cost, 6),
            "avg_latency": round(avg_latency, 3),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        summary_records[cfg] = summary
        logger.info(
            "SUMMARY %s: Accuracy=%.1f%%, Total Cost=$%.6f, Avg Latency=%.2fs",
            cfg.upper(),
            accuracy,
            total_cost,
            avg_latency,
        )

        # Save individual run results
        _save_json(
            results_dir / f"{split}_{cfg}.json",
            {"summary": summary, "details": cfg_results},
        )

    # Save summary
    _save_json(results_dir / f"{split}_summary.json", summary_records)


def main():
    parser = argparse.ArgumentParser(description="Cascade evaluation harness")
    parser.add_argument(
        "--split",
        choices=["dev", "test"],
        default="dev",
        help="Dataset split to evaluate",
    )
    parser.add_argument(
        "--config",
        choices=["nano", "super", "ultra", "cascade", "all"],
        default="ultra",
        help="Model config",
    )
    parser.add_argument(
        "--mock", action="store_true", help="Run in mock mode without API calls"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of tasks (for quick testing)",
    )
    args = parser.parse_args()

    if args.split == "test" and not args.mock:
        print(
            "CRITICAL: Per rules.md, the test split is frozen until the final evaluation."
        )
        print("Please run on the dev split during development.")
        sys.exit(1)

    run_evaluation_sync(
        split=args.split, config=args.config, mock=args.mock, limit=args.limit
    )


if __name__ == "__main__":
    main()
