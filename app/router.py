"""Predict-then-route upfront classifier for Cascade.

Analyzes ticket text features (length, order IDs, multi-issue keywords) to predict
the optimal starting model tier (nano, super, ultra) rather than always starting at Nano.

Strategies supported:
- 'try_cheap_first': Standard Cascade (Nano -> Super -> Ultra).
- 'predict_first': Routes directly to predicted starting tier, then escalates on verifier failure.
"""

import re
from dataclasses import dataclass

# Keywords indicating complex multi-issue complaints or escalations
_MULTI_ISSUE_KEYWORDS = {
    "also",
    "twice",
    "damaged",
    "broken",
    "duplicate",
    "double",
    "defective",
    "scratched",
    "lawyer",
    "chargeback",
    "unacceptable",
    "dispute",
    "disputing",
    "stolen",
    "fraud",
}

_POLICY_EDGE_KEYWORDS = {
    "return",
    "refund",
    "cancel",
    "cancellation",
    "credit",
    "policy",
    "days ago",
    "exchange",
    "replacement",
}

_ORDER_PATTERN = re.compile(r"\bORD-\d+\b", re.IGNORECASE)


@dataclass
class TicketFeatures:
    text_length: int
    word_count: int
    order_id_count: int
    multi_issue_keyword_count: int
    policy_keyword_count: int


def extract_features(ticket_text: str) -> TicketFeatures:
    """Extract linguistic and structural features from customer ticket."""
    clean_text = ticket_text.lower()
    words = re.findall(r"\b[a-z0-9_-]+\b", clean_text)
    order_matches = _ORDER_PATTERN.findall(ticket_text)

    multi_count = sum(1 for w in words if w in _MULTI_ISSUE_KEYWORDS)
    policy_count = sum(1 for w in words if w in _POLICY_EDGE_KEYWORDS)

    return TicketFeatures(
        text_length=len(ticket_text),
        word_count=len(words),
        order_id_count=len(set(order_matches)),
        multi_issue_keyword_count=multi_count,
        policy_keyword_count=policy_count,
    )


def predict_starting_tier(ticket_text: str) -> str:
    """Predict the most cost-effective starting tier for a support ticket.

    Returns:
        'nano'  -> Simple queries (tracking lookups, general hours, single-order questions)
        'super' -> Medium queries (return window checks, cancellations, standard policy questions)
        'ultra' -> Hard queries (multi-issue complaints, multiple orders, damaged goods + duplicate charges)
    """
    feats = extract_features(ticket_text)

    # Hard threshold: Multi-issue or multiple orders or legal/chargeback keywords
    if feats.order_id_count > 1 or feats.multi_issue_keyword_count >= 2:
        return "ultra"

    # If ticket is long (>250 chars) and contains multiple policy/escalation triggers
    if (
        feats.text_length > 250
        and (feats.multi_issue_keyword_count + feats.policy_keyword_count) >= 3
    ):
        return "ultra"

    # Medium threshold: Policy inquiries (returns, cancellations, store credits)
    if (
        feats.policy_keyword_count >= 1
        or feats.multi_issue_keyword_count == 1
        or feats.text_length > 120
    ):
        return "super"

    # Default to cheapest tier: Nano
    return "nano"
