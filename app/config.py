"""Application settings, loaded from environment variables or a .env file."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "WhatsApp AI Support Agent"
    environment: str = "development"

    # Database: SQLite by default so it runs anywhere; MySQL in Docker/production.
    database_url: str = "sqlite:///./data.db"

    # WhatsApp Business Cloud API (Meta)
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_verify_token: str = "change-me"
    whatsapp_app_secret: str = ""  # enables webhook signature checking when set
    whatsapp_api_version: str = "v21.0"

    # LLM provider: "anthropic", "openai" or "mock" (no API key needed)
    llm_provider: str = "mock"
    llm_api_key: str = ""
    llm_model: str = ""
    llm_timeout_seconds: float = 20.0

    # HubSpot CRM (optional)
    hubspot_token: str = ""

    # Business details used in the AI prompt
    business_name: str = "Demo Business"
    knowledge_dir: str = "knowledge"

    # Protects the /admin endpoints
    admin_api_key: str = "change-me-admin-key"

    # How many past messages the agent remembers per customer
    history_limit: int = 6


@lru_cache
def get_settings() -> Settings:
    return Settings()
