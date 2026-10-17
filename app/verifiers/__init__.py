"""Verifiers package for Cascade.

Layered verification pipeline (cheapest first):
1. schema: Validates JSON format and required Pydantic Reply fields.
2. grounding: Validates that referenced dates, amounts, tracking IDs, and statuses appear in tool outputs.
3. rules: Validates domain store policies (refund window, store credit window, cancellation rules, damaged reporting).
4. consistency (Phase 3): Multi-sample agreement.
5. judge (Phase 3): LLM coverage check.
"""

from app.schemas import Reply, Task, Verdict
from app.verifiers.grounding import verify_grounding
from app.verifiers.rules import verify_rules
from app.verifiers.schema import verify_schema


def run_verifiers(
    task: Task,
    reply: Reply | None,
    tool_outputs: dict,
    raw_text: str = "",
) -> Verdict:
    """Run layered verifiers in order of cost (cheapest first).

    Stops at the first failure.
    """
    # 1. Schema check
    verdict_schema = verify_schema(raw_text)
    if not verdict_schema.passed:
        return verdict_schema

    parsed_reply = reply
    if parsed_reply is None and verdict_schema.details.get("reply"):
        parsed_reply = verdict_schema.details["reply"]

    # 2. Grounding check
    verdict_grounding = verify_grounding(task, parsed_reply, tool_outputs)
    if not verdict_grounding.passed:
        return verdict_grounding

    # 3. Policy rules check
    verdict_rules = verify_rules(task, parsed_reply, tool_outputs)
    if not verdict_rules.passed:
        return verdict_rules

    return Verdict(
        passed=True,
        reason="All deterministic verifications passed",
        verifier_name="pipeline",
    )
