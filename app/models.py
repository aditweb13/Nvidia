"""Model client for Nemotron tiers on Token Factory / NVIDIA NIM.

Interface:
    call_model(tier, messages, tools=None) -> ModelResult

Features:
- Token and cost accounting based on configured per-tier prices
- Async execution
- Transient error retry with exponential backoff (503, 429, timeouts)
- Offline mock mode for zero-credit testing
- Optional disk caching for development runs
"""

import asyncio
import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from app.config import get_settings
from app.schemas import ModelResult

logger = logging.getLogger("cascade.models")

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncOpenAI(
            base_url=settings.token_factory_base_url,
            api_key=settings.token_factory_api_key,
        )
    return _client


def _get_cache_key(
    tier: str, messages: list[dict[str, Any]], temperature: float
) -> str:
    raw = json.dumps(
        {"tier": tier, "messages": messages, "temperature": temperature}, sort_keys=True
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _read_cache(cache_key: str, cache_dir: Path) -> ModelResult | None:
    cache_file = cache_dir / f"{cache_key}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ModelResult(**data)
        except (OSError, json.JSONDecodeError, ValueError) as e:
            logger.warning("Failed reading cache: %s", e)
    return None


def _write_cache(cache_key: str, result: ModelResult, cache_dir: Path):
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{cache_key}.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, indent=2)
    except OSError as e:
        logger.warning("Failed writing cache: %s", e)


async def call_model(
    tier: str,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    temperature: float = 0.2,
    max_tokens: int = 600,
    mock: bool = False,
    use_cache: bool | None = None,
) -> ModelResult:
    """Call a model tier (nano, super, ultra) and return a ModelResult with cost accounting."""
    settings = get_settings()
    model_id = settings.get_model_for_tier(tier)
    pricing = settings.get_pricing_for_tier(tier)

    # 1. Offline mock mode
    if (
        mock
        or settings.token_factory_api_key is None
        or settings.token_factory_api_key.startswith("your_")
    ):
        return _mock_call(tier, messages, pricing)

    # 2. Check response cache if enabled
    cache_enabled = settings.response_cache_enabled if use_cache is None else use_cache
    cache_dir = Path(".cache/responses")
    cache_key = _get_cache_key(tier, messages, temperature)
    if cache_enabled:
        cached = _read_cache(cache_key, cache_dir)
        if cached:
            return cached

    # 3. Live call with retries
    client = get_client()
    max_retries = 3
    backoff = 2.0
    start_time = time.perf_counter()

    for attempt in range(1, max_retries + 1):
        try:
            kwargs: dict[str, Any] = {
                "model": model_id,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if tools:
                kwargs["tools"] = tools

            response = await client.chat.completions.create(**kwargs)
            latency = time.perf_counter() - start_time

            choice = response.choices[0]
            reply_text = choice.message.content or ""
            raw_tool_calls = None
            if choice.message.tool_calls:
                raw_tool_calls = [tc.model_dump() for tc in choice.message.tool_calls]

            usage = response.usage
            tokens_in = usage.prompt_tokens if usage else 0
            tokens_out = usage.completion_tokens if usage else 0

            # Calculate cost in USD per 1M tokens
            cost = (tokens_in * (pricing.price_in / 1_000_000.0)) + (
                tokens_out * (pricing.price_out / 1_000_000.0)
            )

            result = ModelResult(
                text=reply_text,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=round(cost, 6),
                latency=round(latency, 3),
                tool_calls=raw_tool_calls,
                raw_response=response.model_dump(),
            )

            if cache_enabled:
                _write_cache(cache_key, result, cache_dir)

            return result

        except Exception as e:
            err_msg = str(e)
            is_transient = any(
                code in err_msg for code in ["503", "429", "timeout", "overloaded"]
            )
            if attempt < max_retries and is_transient:
                logger.warning(
                    "Transient error calling %s (attempt %d/%d): %s. Retrying in %.1fs...",
                    tier,
                    attempt,
                    max_retries,
                    err_msg,
                    backoff,
                )
                await asyncio.sleep(backoff)
                backoff *= 1.5
            else:
                latency = time.perf_counter() - start_time
                logger.error("Error calling %s (%s): %s", tier, model_id, err_msg)
                raise


def _mock_call(tier: str, messages: list[dict[str, Any]], pricing) -> ModelResult:
    """Produce deterministic offline mock replies for testing."""
    last_user_msg = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user_msg = m.get("content", "")
            break

    # Construct mock structured reply
    if "ORD-1001" in last_user_msg:
        mock_reply = {
            "decision": "inform_status",
            "message": "Order ORD-1001 was Delivered on Oct 14 via FedEx (TRK94001230).",
            "order_id": "ORD-1001",
            "action_taken": "Provided tracking details",
        }
    elif "ORD-1002" in last_user_msg:
        mock_reply = {
            "decision": "offer_store_credit_only",
            "message": "Order ORD-1002 was delivered 58 days ago on Aug 20. Under our policy, returns between 31-60 days receive store credit only. No cash refund can be issued.",
            "order_id": "ORD-1002",
            "action_taken": "Offered store credit for return outside 30-day window",
        }
    else:
        mock_reply = {
            "decision": "inform_status",
            "message": "Thank you for contacting ShopEasy. How can I assist you with your order?",
            "order_id": None,
            "action_taken": "Assisted customer",
        }

    text = json.dumps(mock_reply)
    tokens_in = 60
    tokens_out = 45
    cost = (tokens_in * (pricing.price_in / 1_000_000.0)) + (
        tokens_out * (pricing.price_out / 1_000_000.0)
    )

    return ModelResult(
        text=text,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost=round(cost, 6),
        latency=0.05,
    )
