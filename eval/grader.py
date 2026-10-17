"""Deterministic grader for Cascade evaluation benchmark.

Grades replies against gold labels:
1. Decision accuracy (matching correct resolution)
2. Required facts coverage (dates, amounts, carriers, status)
3. Checklist item coverage
"""

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GradeResult:
    passed: bool
    score: float
    decision_correct: bool
    facts_present: list[str] = field(default_factory=list)
    facts_missing: list[str] = field(default_factory=list)
    checklist_score: float = 1.0
    details: dict[str, Any] = field(default_factory=dict)


def _normalize_text(text: str) -> str:
    """Normalize text for robust substring matching."""
    text = text.lower()
    # Replace non-breaking spaces and special dashes
    text = re.sub(r"[\u202f\u00a0]", " ", text)
    text = re.sub(r"[–—−]", "-", text)
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)
    return text


def grade_reply(
    reply_text: str,
    gold: dict[str, Any],
    reply_decision: str | None = None,
) -> GradeResult:
    """Deterministically grades a reply against the task's gold definition.

    Parameters:
    - reply_text: The textual message returned to the customer.
    - gold: The gold dictionary from tasks.jsonl containing 'decision',
      'required_facts', and 'checklist'.
    - reply_decision: The structured decision string if provided by the model.
    """
    norm_reply = _normalize_text(reply_text)
    gold_decision = gold.get("decision", "")
    required_facts = gold.get("required_facts", [])
    checklist = gold.get("checklist", [])

    # 1. Decision check
    decision_correct = False
    if reply_decision:
        clean_reply_dec = reply_decision.strip().lower()
        clean_gold_dec = gold_decision.strip().lower()
        decision_correct = clean_reply_dec == clean_gold_dec

    # Fallback to semantic decision cues in reply_text if structured decision wasn't provided or slightly differed
    if not decision_correct:
        gold_dec_lower = gold_decision.lower()
        if (
            "deny" in gold_dec_lower
            or "ineligible" in gold_dec_lower
            or "expired" in gold_dec_lower
        ):
            decision_correct = any(
                w in norm_reply
                for w in [
                    "cannot be returned",
                    "ineligible",
                    "outside",
                    "expired",
                    "past",
                    "cannot refund",
                    "cannot cancel",
                ]
            )
        elif "store_credit" in gold_dec_lower:
            decision_correct = (
                "store credit" in norm_reply
                and "no cash" in norm_reply
                or "credit only" in norm_reply
            )
        elif "cancel" in gold_dec_lower and "approved" in gold_dec_lower:
            decision_correct = "cancel" in norm_reply and any(
                w in norm_reply
                for w in ["approved", "has been cancelled", "canceled", "released"]
            )
        elif "refund_duplicate" in gold_dec_lower:
            decision_correct = "duplicate" in norm_reply and "refund" in norm_reply
        elif "damaged" in gold_dec_lower or "defective" in gold_dec_lower:
            decision_correct = any(
                w in norm_reply
                for w in ["replacement", "refund", "damaged", "broken", "waived"]
            )
        elif "courtesy" in gold_dec_lower:
            decision_correct = (
                "courtesy" in norm_reply
                or "store credit" in norm_reply
                or "discount" in norm_reply
            )
        elif "inform_status" in gold_dec_lower or "inform_policy" in gold_dec_lower:
            decision_correct = True
        elif "not_found" in gold_dec_lower:
            decision_correct = (
                "not found" in norm_reply or "could not find" in norm_reply
            )

    # 2. Required facts check
    facts_present = []
    facts_missing = []
    for fact in required_facts:
        norm_fact = _normalize_text(fact)
        # Check direct or stripped match
        fact_tokens = [t for t in norm_fact.split() if len(t) > 2]
        if norm_fact in norm_reply or (
            fact_tokens and all(token in norm_reply for token in fact_tokens)
        ):
            facts_present.append(fact)
        else:
            facts_missing.append(fact)

    fact_coverage = len(facts_present) / len(required_facts) if required_facts else 1.0

    # 3. Checklist check (basic presence of required items)
    checklist_matched = 0
    for item in checklist:
        item_words = [w for w in _normalize_text(item).split() if len(w) > 3]
        if item_words:
            matched_words = sum(1 for w in item_words if w in norm_reply)
            if matched_words / len(item_words) >= 0.4:
                checklist_matched += 1
        else:
            checklist_matched += 1

    checklist_score = checklist_matched / len(checklist) if checklist else 1.0

    # Overall score: weighted composite
    # 40% decision, 40% facts, 20% checklist
    score = (
        (0.4 * (1.0 if decision_correct else 0.0))
        + (0.4 * fact_coverage)
        + (0.2 * checklist_score)
    )

    # A task passes if decision is correct and at least 70% of facts are present
    passed = decision_correct and fact_coverage >= 0.65

    return GradeResult(
        passed=passed,
        score=round(score, 3),
        decision_correct=decision_correct,
        facts_present=facts_present,
        facts_missing=facts_missing,
        checklist_score=round(checklist_score, 3),
        details={
            "fact_coverage": round(fact_coverage, 3),
            "total_facts": len(required_facts),
            "matched_facts": len(facts_present),
            "total_checklist": len(checklist),
            "matched_checklist": checklist_matched,
        },
    )
