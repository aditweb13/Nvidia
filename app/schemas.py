"""Pydantic schemas and dataclasses for Cascade.

Strictly follows architecture.md interfaces:
- call_model(tier, messages, tools=None) -> ModelResult
- verify(task, reply, tool_outputs) -> Verdict
- run_cascade(task) -> CascadeResult
"""

from typing import Any

from pydantic import BaseModel, Field


class ModelResult(BaseModel):
    """Result of calling a model tier."""

    text: str
    tokens_in: int = 0
    tokens_out: int = 0
    cost: float = 0.0
    latency: float = 0.0
    raw_response: dict[str, Any] | None = None
    tool_calls: list[dict[str, Any]] | None = None


class Verdict(BaseModel):
    """Verdict returned by a verifier."""

    passed: bool
    reason: str
    cost: float = 0.0
    verifier_name: str = "unknown"
    details: dict[str, Any] = Field(default_factory=dict)


class Reply(BaseModel):
    """Structured customer service reply format."""

    decision: str = Field(
        description="The formal decision (e.g., inform_status, approve_return_refund, offer_store_credit_only, deny_return_past_window, cancel_order_approved, refund_duplicate_charge, approve_damaged_remedy)"
    )
    message: str = Field(
        description="The friendly, complete customer-facing response message"
    )
    order_id: str | None = Field(
        default=None, description="The order ID referenced if applicable"
    )
    action_taken: str | None = Field(
        default=None, description="Summary of action taken"
    )


class Task(BaseModel):
    """Support ticket intake task."""

    task_id: str
    ticket_text: str
    order_id: str | None = None
    customer_id: str | None = None
    difficulty: str | None = "medium"
    split: str | None = "live"
    config: str | None = "cascade"


class AttemptRecord(BaseModel):
    """Record of an individual tier attempt in the cascade."""

    tier: str
    verdict: str  # "pass" | "fail"
    reason: str
    cost: float = 0.0
    latency: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0


class CascadeResult(BaseModel):
    """Final output of the Cascade controller."""

    task_id: str
    answer: str
    tier: str
    attempts: int
    cost: float
    latency: float
    needs_review: bool = False
    history: list[AttemptRecord] = Field(default_factory=list)
    reply: Reply | None = None
