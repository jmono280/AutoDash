from __future__ import annotations

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = ""

    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: str = "http://localhost:5173"
    UPLOAD_DIR: str = "./uploads"
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str = "nvidia/nemotron-3-super-120b-a12b:free"
    OPENROUTER_MAX_TOKENS_OUT: int = 1024
    OPENROUTER_MAX_HISTORY: int = 10
    OPENROUTER_MAX_CONTEXT_CHARS: int = 4000

    # RingCentral — opcionales, solo requeridos para el script analitycs.py
    RC_APP_CLIENT_ID:     str = ""
    RC_APP_CLIENT_SECRET: str = ""
    RC_SERVER_URL:        str = "https://platform.ringcentral.com"
    RC_USER_JWT:        str = ""
    RC_EXTENSION_IDS:     str = ""

    # IDMS / AutoAnalytix
    IDMS_URL: str = "https://idms.dealersocket.com"
    IDMS_USERNAME: str = ""
    IDMS_PASSWORD: str = ""
    IDMS_DEVICE_KEY: str | None = None
    IDMS_CLIENT_KEY_API: str | None = None

    @property
    def idms_url(self) -> str:
        return self.IDMS_URL

    @property
    def idms_username(self) -> str:
        return self.IDMS_USERNAME

    @property
    def idms_password(self) -> str:
        return self.IDMS_PASSWORD

    @property
    def idms_device_key(self) -> str | None:
        return self.IDMS_DEVICE_KEY

    @property
    def idms_client_key_api(self) -> str | None:
        return self.IDMS_CLIENT_KEY_API

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        if not self.DATABASE_URL:
            if not self.POSTGRES_USER or not self.POSTGRES_PASSWORD or not self.POSTGRES_DB:
                raise ValueError(
                    "Set DATABASE_URL or all of POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB"
                )
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
