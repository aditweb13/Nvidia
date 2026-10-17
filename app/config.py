"""Configuration loader for Cascade.

Loads environment variables from .env and settings from config.yaml.
Strictly adheres to rules.md: No hardcoded model IDs or prices.
"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TierPricing(BaseModel):
    price_in: float  # Price in USD per 1M input tokens
    price_out: float  # Price in USD per 1M output tokens


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Token Factory API configuration
    token_factory_base_url: str = Field(
        default="https://api.tokenfactory.nebius.ai/v1",
        alias="TOKEN_FACTORY_BASE_URL",
    )
    token_factory_api_key: str | None = Field(
        default=None,
        alias="TOKEN_FACTORY_API_KEY",
    )

    # Model IDs for Nemotron tiers
    model_nano: str = Field(
        default="nvidia/nemotron-nano-9b-instruct",
        alias="MODEL_NANO",
    )
    model_super: str = Field(
        default="nvidia/nemotron-super-49b-instruct",
        alias="MODEL_SUPER",
    )
    model_ultra: str = Field(
        default="nvidia/nemotron-ultra-340b-instruct",
        alias="MODEL_ULTRA",
    )

    # Per-token pricing in USD per 1M tokens
    price_nano_in: float = Field(default=0.10, alias="PRICE_NANO_IN")
    price_nano_out: float = Field(default=0.20, alias="PRICE_NANO_OUT")
    price_super_in: float = Field(default=0.50, alias="PRICE_SUPER_IN")
    price_super_out: float = Field(default=1.50, alias="PRICE_SUPER_OUT")
    price_ultra_in: float = Field(default=2.00, alias="PRICE_ULTRA_IN")
    price_ultra_out: float = Field(default=6.00, alias="PRICE_ULTRA_OUT")

    # SQLite Database
    db_path: str = Field(default="data/cascade.db", alias="DB_PATH")

    # Feature flags
    enable_consistency_verifier: bool = Field(
        default=False, alias="ENABLE_CONSISTENCY_VERIFIER"
    )
    enable_judge_verifier: bool = Field(default=False, alias="ENABLE_JUDGE_VERIFIER")
    response_cache_enabled: bool = Field(default=True, alias="RESPONSE_CACHE_ENABLED")

    def get_model_for_tier(self, tier: str) -> str:
        tier_lower = tier.lower()
        if tier_lower == "nano":
            return self.model_nano
        elif tier_lower == "super":
            return self.model_super
        elif tier_lower == "ultra":
            return self.model_ultra
        raise ValueError(f"Unknown tier: {tier}. Must be nano, super, or ultra.")

    def get_pricing_for_tier(self, tier: str) -> TierPricing:
        tier_lower = tier.lower()
        if tier_lower == "nano":
            return TierPricing(
                price_in=self.price_nano_in, price_out=self.price_nano_out
            )
        elif tier_lower == "super":
            return TierPricing(
                price_in=self.price_super_in, price_out=self.price_super_out
            )
        elif tier_lower == "ultra":
            return TierPricing(
                price_in=self.price_ultra_in, price_out=self.price_ultra_out
            )
        raise ValueError(f"Unknown tier: {tier}. Must be nano, super, or ultra.")


def load_yaml_config(config_path: str = "config.yaml") -> dict[str, Any]:
    path = Path(config_path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# Global configuration instances
_settings: Settings | None = None
_yaml_config: dict[str, Any] | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def get_yaml_config() -> dict[str, Any]:
    global _yaml_config
    if _yaml_config is None:
        _yaml_config = load_yaml_config()
    return _yaml_config
