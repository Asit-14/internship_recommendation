from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    app_name: str = "FastAPI Auth Service"
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(..., validation_alias="DATABASE_URL")
    jwt_secret_key: str = Field(..., validation_alias="JWT_SECRET_KEY", min_length=32)
    jwt_algorithm: str = Field("HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES", ge=1
    )

    admin_name: str | None = Field(default=None, validation_alias="ADMIN_NAME")
    admin_email: str | None = Field(default=None, validation_alias="ADMIN_EMAIL")
    admin_password: str | None = Field(default=None, validation_alias="ADMIN_PASSWORD")

    smtp_email: str | None = Field(default=None, validation_alias="SMTP_EMAIL")
    smtp_password: str | None = Field(default=None, validation_alias="SMTP_PASSWORD")
    smtp_host: str = Field("smtp.gmail.com", validation_alias="SMTP_HOST")
    smtp_port: int = Field(587, validation_alias="SMTP_PORT")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()