"""Environment-driven configuration. Every value can be overridden with a SILO_* env var."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_VERSION = "0.1.0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SILO_", env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = "sqlite:///./silo.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Startup behaviour
    auto_migrate: bool = True
    seed_demo_data: bool = True

    # NLP
    nlp_engine: str = Field("auto", description="auto | spacy | rules")
    spacy_model: str = "en_core_web_sm"
    max_text_chars: int = 20_000

    # Article URL ingestion
    url_fetch_enabled: bool = True
    url_fetch_timeout_s: float = 8.0
    url_fetch_max_bytes: int = 1_500_000
    url_fetch_max_redirects: int = 3

    # Abuse protection for POST analysis endpoints (per client IP)
    rate_limit_per_minute: int = 30

    # Live civic-data adapters (optional; the app is fully usable without them)
    live_data_enabled: bool = False
    congress_api_key: str | None = None
    fec_api_key: str | None = None
    congress_api_base: str = "https://api.congress.gov/v3"
    fec_api_base: str = "https://api.open.fec.gov/v1"
    external_timeout_s: float = 10.0
    external_max_retries: int = 2

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
