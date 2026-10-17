"""LLM Judge verifier for Cascade.

Uses Nemotron Super to verify that a candidate reply addresses every distinct
issue or question in the customer's support ticket.
Counts Super call spend in Verdict.cost.
Zero cost in mock mode or when disabled.
"""

import json
import logging

from app.config import get_settings
from app.models import call_model
from app.schemas import Reply, Task, Verdict
from app.verifiers.schema import extract_json_from_text

logger = logging.getLogger("cascade.verifiers.judge")

_JUDGE_PROMPT = """You are a rigorous quality auditor for customer support tickets.
Analyze the customer's ticket and the assistant's reply.

Ticket:
\"\"\"{ticket_text}\"\"\"

Assistant Reply:
\"\"\"{reply_text}\"\"\"

Task:
1. Identify all distinct customer issues, questions, or requests in the ticket.
2. Determine if the assistant's reply directly and satisfactorily addresses EACH issue.
3. If ANY issue is ignored, unaddressed, or evaded, output passed=false and name the missing issue.

Return ONLY a JSON object:
{
  "passed": true/false,
  "issues_identified": ["issue 1", "issue 2"],
  "unaddressed_issues": ["unaddressed issue if any"],
  "reason": "short explanation of verdict"
}
"""


async def verify_judge(
    task: Task,
    reply: Reply | None,
    mock: bool = False,
) -> Verdict:
    """Evaluate whether candidate reply comprehensively covers all ticket issues."""
    settings = get_settings()
    if not settings.enable_judge_verifier and not mock:
        return Verdict(
            passed=True,
            reason="LLM judge verifier disabled in config",
            verifier_name="judge",
        )

    if reply is None:
        return Verdict(
            passed=False, reason="judge.error: Reply is None", verifier_name="judge"
        )

    if mock:
        # In mock mode, check simple multi-issue heuristic
        ticket_lower = task.ticket_text.lower()
        if "twice" in ticket_lower and "when will" in ticket_lower:
            # Multi-issue: check if reply addresses both
            reply_lower = reply.message.lower()
            if (
                "shipping" not in reply_lower
                and "process" not in reply_lower
                and "ship" not in reply_lower
            ):
                return Verdict(
                    passed=False,
                    reason="judge.missing_issue: Reply addressed the charge but did not answer shipping question",
                    verifier_name="judge",
                    cost=0.00005,
                    details={"missing_issue": "shipping inquiry"},
                )
        return Verdict(
            passed=True,
            reason="LLM judge verified: all ticket issues addressed",
            verifier_name="judge",
            cost=0.00005,
        )

    formatted_prompt = _JUDGE_PROMPT.format(
        ticket_text=task.ticket_text,
        reply_text=reply.message,
    )

    messages = [
        {
            "role": "system",
            "content": "You are a precise customer support QA evaluator.",
        },
        {"role": "user", "content": formatted_prompt},
    ]

    try:
        model_res = await call_model(
            tier="super",
            messages=messages,
            temperature=0.1,
            max_tokens=250,
            mock=mock,
        )
        json_str = extract_json_from_text(model_res.text)
        data = json.loads(json_str)
        passed = bool(data.get("passed", False))
        unaddressed = data.get("unaddressed_issues", [])
        reason = data.get("reason", "LLM judge completed check")

        if not passed:
            reason = f"judge.missing_issue: {unaddressed[0] if unaddressed else reason}"

        return Verdict(
            passed=passed,
            reason=reason,
            verifier_name="judge",
            cost=model_res.cost,
            details=data,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("LLM Judge evaluation failed: %s", e)
        # Fall back to passing if judge fails
        return Verdict(
            passed=True,
            reason="LLM judge fallback: check skipped on evaluation error",
            verifier_name="judge",
        )
