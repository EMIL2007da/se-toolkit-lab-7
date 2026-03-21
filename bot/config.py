"""
Configuration loader for the Telegram bot.

Reads secrets from .env.bot.secret using pydantic-settings.
This pattern loads secrets from environment files — never hardcode tokens.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env.bot.secret",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram Bot Token
    bot_token: str = ""

    # LMS API
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = ""

    # LLM API (for Task 3)
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = ""


# Global settings instance
settings = BotSettings()
