"""Unit tests for configuration loading."""

import pytest

from app.config import Settings, get_yaml_config


def test_settings_default_values():
    settings = Settings()
    assert settings.token_factory_base_url is not None
    assert settings.model_nano is not None
    assert settings.model_super is not None
    assert settings.model_ultra is not None
    assert settings.db_path == "data/cascade.db"


def test_tier_model_lookup():
    settings = Settings(
        MODEL_NANO="custom/nano",
        MODEL_SUPER="custom/super",
        MODEL_ULTRA="custom/ultra",
    )
    assert settings.get_model_for_tier("nano") == "custom/nano"
    assert settings.get_model_for_tier("super") == "custom/super"
    assert settings.get_model_for_tier("ultra") == "custom/ultra"
    with pytest.raises(ValueError):
        settings.get_model_for_tier("invalid_tier")


def test_tier_pricing_lookup():
    settings = Settings(
        PRICE_NANO_IN=0.15,
        PRICE_NANO_OUT=0.30,
        PRICE_SUPER_IN=0.60,
        PRICE_SUPER_OUT=1.80,
        PRICE_ULTRA_IN=2.50,
        PRICE_ULTRA_OUT=7.50,
    )
    nano_pricing = settings.get_pricing_for_tier("nano")
    assert nano_pricing.price_in == 0.15
    assert nano_pricing.price_out == 0.30

    super_pricing = settings.get_pricing_for_tier("super")
    assert super_pricing.price_in == 0.60
    assert super_pricing.price_out == 1.80

    ultra_pricing = settings.get_pricing_for_tier("ultra")
    assert ultra_pricing.price_in == 2.50
    assert ultra_pricing.price_out == 7.50

    with pytest.raises(ValueError):
        settings.get_pricing_for_tier("unknown")


def test_yaml_config_loading():
    config = get_yaml_config()
    assert "routing" in config
    assert "tiers" in config["routing"]
    assert config["routing"]["tiers"] == ["nano", "super", "ultra"]
    assert "verifiers" in config
