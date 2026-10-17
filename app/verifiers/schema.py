"""Schema verifier for Cascade.

Validates that model output parses as structured JSON conforming to Reply schema.
Zero-cost verifier.
"""

import json
import re

from pydantic import ValidationError

from app.schemas import Reply, Verdict


def extract_json_from_text(text: str) -> str:
    """Extract JSON object from string, handling markdown fences or preamble."""
    text = text.strip()
    # Check for markdown code blocks
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Check for outermost { and }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1].strip()
    return text


def verify_schema(raw_text: str) -> Verdict:
    """Verify that raw_text is valid JSON matching Reply schema."""
    if not raw_text or not raw_text.strip():
        return Verdict(
            passed=False,
            reason="Reply was empty or missing",
            verifier_name="schema",
            details={"error": "empty_output"},
        )

    json_str = extract_json_from_text(raw_text)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        return Verdict(
            passed=False,
            reason=f"Reply failed JSON parsing: {e.msg}",
            verifier_name="schema",
            details={"raw_sample": raw_text[:120], "error": "json_decode_error"},
        )

    if not isinstance(data, dict):
        return Verdict(
            passed=False,
            reason="Reply parsed but is not a JSON object",
            verifier_name="schema",
            details={"error": "not_a_dict"},
        )

    try:
        reply = Reply(**data)
        # Verify required decision string is non-empty
        if not reply.decision or not reply.decision.strip():
            return Verdict(
                passed=False,
                reason="Reply schema missing required 'decision' field",
                verifier_name="schema",
                details={"error": "missing_decision"},
            )
        if not reply.message or not reply.message.strip():
            return Verdict(
                passed=False,
                reason="Reply schema missing required 'message' field",
                verifier_name="schema",
                details={"error": "missing_message"},
            )
        return Verdict(
            passed=True,
            reason="Schema is valid",
            verifier_name="schema",
            details={"reply": reply},
        )
    except ValidationError as ve:
        first_err = ve.errors()[0]
        field_name = ".".join(str(loc) for loc in first_err.get("loc", []))
        return Verdict(
            passed=False,
            reason=f"Reply schema validation error on field '{field_name}': {first_err.get('msg')}",
            verifier_name="schema",
            details={"validation_errors": ve.errors()},
        )
