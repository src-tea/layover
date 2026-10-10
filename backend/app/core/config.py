from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LAYOVER"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_issuer: str = ""
    jwt_secret: str = "layover-dev-secret-change-me-long-enough-32-bytes"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    mode: str = "offline"

    @property
    def cors_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
