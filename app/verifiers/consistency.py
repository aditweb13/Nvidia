"""Self-consistency verifier for Cascade.

Runs 3 parallel temperature-sampled calls on Nemotron Nano using asyncio.gather.
Compares the structured decisions:
- If >= 2 agree: passes with majority decision
- If all 3 disagree: fails with reason 'consistency.disagree'
Counts extra model call spend in Verdict.cost.
"""

import json
import logging
from collections import Counter
from typing import Any

from app.config import get_settings
from app.models import call_model
from app.schemas import Reply, Task, Verdict
from app.verifiers.schema import extract_json_from_text

logger = logging.getLogger("cascade.verifiers.consistency")


async def verify_consistency(
    task: Task,
    messages: list[dict[str, Any]],
    current_reply: Reply | None,
    samples_count: int = 3,
    temperature: float = 0.7,
    mock: bool = False,
) -> Verdict:
    """Run parallel sampling on Nano and verify agreement on decision."""
    settings = get_settings()
    if not settings.enable_consistency_verifier and not mock:
        return Verdict(
            passed=True,
            reason="Consistency verifier disabled in config",
            verifier_name="consistency",
        )

    if mock:
        # In mock mode, simulate consistent agreement
        return Verdict(
            passed=True,
            reason="Self-consistency verified (3/3 samples agreed)",
            verifier_name="consistency",
            cost=0.00003,
            details={"agreement_ratio": 1.0, "samples": 3},
        )

    import asyncio

    coros = [
        call_model(
            tier="nano",
            messages=messages,
            temperature=temperature,
            mock=mock,
        )
        for _ in range(samples_count)
    ]

    results = await asyncio.gather(*coros, return_exceptions=True)

    decisions = []
    total_sample_cost = 0.0

    if current_reply and current_reply.decision:
        decisions.append(current_reply.decision.strip().lower())

    for res in results:
        if isinstance(res, Exception):
            logger.warning("Consistency sample failed: %s", res)
            continue
        total_sample_cost += res.cost
        try:
            json_str = extract_json_from_text(res.text)
            data = json.loads(json_str)
            if isinstance(data, dict) and data.get("decision"):
                decisions.append(str(data["decision"]).strip().lower())
        except (json.JSONDecodeError, TypeError, ValueError) as err:
            logger.debug("Failed parsing consistency decision: %s", err)

    if not decisions:
        return Verdict(
            passed=False,
            reason="consistency.error: Could not extract decisions from consistency samples",
            verifier_name="consistency",
            cost=round(total_sample_cost, 6),
        )

    counter = Counter(decisions)
    most_common_decision, count = counter.most_common(1)[0]
    total_valid = len(decisions)
    ratio = count / total_valid

    # Pass if majority agrees (at least 50%)
    if ratio >= 0.5:
        return Verdict(
            passed=True,
            reason=f"Self-consistency verified ({count}/{total_valid} samples agreed on '{most_common_decision}')",
            verifier_name="consistency",
            cost=round(total_sample_cost, 6),
            details={
                "majority_decision": most_common_decision,
                "ratio": round(ratio, 2),
            },
        )

    return Verdict(
        passed=False,
        reason=f"consistency.disagree: Samples disagreed on decision (distribution: {dict(counter)})",
        verifier_name="consistency",
        cost=round(total_sample_cost, 6),
        details={"distribution": dict(counter)},
    )
