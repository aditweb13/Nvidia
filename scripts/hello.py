"""Script to verify Token Factory access and test all three Nemotron tiers.

Calls Nemotron Nano, Super, and Ultra, and prints the reply and token usage.
Supports --mock flag for offline testing.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings


async def test_tier(client, model_id: str, tier_name: str, mock: bool = False):
    print(f"\n--- Testing Tier: {tier_name.upper()} ({model_id}) ---")
    messages = [
        {"role": "system", "content": "You are a concise customer service assistant."},
        {
            "role": "user",
            "content": "Hello! Can you confirm you are online and tell me what model you are in one sentence?",
        },
    ]

    if mock:
        print("[MOCK MODE] Simulated call to Token Factory.")
        reply = f"Hello! I am Nemotron {tier_name.capitalize()} running in mock mode for offline testing."
        prompt_tokens = 25
        completion_tokens = 18
        print(f"Reply: {reply}")
        print(f"Token usage: {prompt_tokens} input, {completion_tokens} output")
        return True

    try:
        response = await client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=0.2,
            max_tokens=100,
        )
        choice = response.choices[0]
        reply = choice.message.content
        usage = response.usage
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0

        print(f"Reply: {reply.strip()}")
        print(f"Token usage: {prompt_tokens} input, {completion_tokens} output")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"ERROR calling {tier_name} ({model_id}): {e}")
        return False


async def main():
    parser = argparse.ArgumentParser(description="Test Token Factory Nemotron tiers.")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run in mock mode without making real API calls",
    )
    args = parser.parse_args()

    settings = get_settings()

    print("Cascade - Token Factory Hello Test")
    print(f"Base URL: {settings.token_factory_base_url}")
    print(f"Nano Model:  {settings.model_nano}")
    print(f"Super Model: {settings.model_super}")
    print(f"Ultra Model: {settings.model_ultra}")

    if not args.mock and (
        not settings.token_factory_api_key
        or settings.token_factory_api_key.startswith("your_")
    ):
        print("\n" + "=" * 60)
        print("WARNING: TOKEN_FACTORY_API_KEY is not set in .env.")
        print("To run live tests against Nebius Token Factory:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your TOKEN_FACTORY_API_KEY and check model IDs")
        print("To run this test offline right now, run:")
        print("  python scripts/hello.py --mock")
        print("=" * 60 + "\n")
        sys.exit(1)

    client = None
    if not args.mock:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            base_url=settings.token_factory_base_url,
            api_key=settings.token_factory_api_key,
        )

    tiers = [
        ("nano", settings.model_nano),
        ("super", settings.model_super),
        ("ultra", settings.model_ultra),
    ]

    all_passed = True
    for tier_name, model_id in tiers:
        passed = await test_tier(client, model_id, tier_name, mock=args.mock)
        if not passed:
            all_passed = False

    if all_passed:
        print("\nSUCCESS: All three tiers responded successfully.")
    else:
        print("\nFAILURE: One or more tiers failed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
