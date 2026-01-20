from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    log_level: str = "INFO"

    # Supabase
    supabase_url: str
    supabase_anon_key: str | None = None
    supabase_service_key: str | None = None

    # Twilio
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_from: str  # e.g., whatsapp:+14155238886

    # Twilio webhook
    twilio_webhook_url: str | None = None
    twilio_skip_signature: bool = False

    # AI
    openai_api_key: str | None = None
    model: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


