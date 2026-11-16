"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for local development and production deployment."""

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    app_env: str = "development"
    log_level: str = "INFO"
    log_color: bool = True
    recent_history_limit: int = 5

    @property
    def openai_configured(self) -> bool:
        """Return whether a non-placeholder OpenAI key is configured."""
        return bool(self.openai_api_key and not self.openai_api_key.startswith("replace-"))

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
