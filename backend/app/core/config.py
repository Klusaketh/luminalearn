from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized FastAPI Environment Settings Schema powered by Pydantic BaseSettings.
    Automatically reads environment variables and supplies defaults.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Project Information
    PROJECT_NAME: str = "LuminaLearn AI"
    PROJECT_CODENAME: str = "Project Aurora"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")

    # FastAPI Server
    BACKEND_HOST: str = Field(default="0.0.0.0")
    BACKEND_PORT: int = Field(default=8000)
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    # Security & Tokens
    SECRET_KEY: str = Field(default="DEV_SUPER_SECRET_KEY_CHANGE_IN_PROD_MIN_32_BYTES")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Database Settings (PostgreSQL 16)
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_USER: str = Field(default="lumina_admin")
    POSTGRES_PASSWORD: str = Field(default="lumina_dev_password_2026")
    POSTGRES_DB: str = Field(default="luminalearn_db")

    @property
    def ASYNC_DATABASE_URI(self) -> str:
        """Construct Async SQLAlchemy PostgreSQL Database Connection String."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis Cache & Broker Settings
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_PASSWORD: str = Field(default="")

    # SMTP / Email Service Configuration
    SMTP_HOST: str | None = Field(default=None)
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str | None = Field(default=None)
    SMTP_PASSWORD: str | None = Field(default=None)
    SMTP_TLS: bool = Field(default=True)
    EMAILS_FROM_EMAIL: str | None = Field(default=None)
    EMAILS_FROM_NAME: str = Field(default="LuminaLearn AI")

    # Google OAuth2 Identity Settings
    GOOGLE_CLIENT_ID: str | None = Field(default=None)
    GOOGLE_CLIENT_SECRET: str | None = Field(default=None)

    @property
    def REDIS_URI(self) -> str:
        """Construct Redis Connection String."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"


# Global Instantiated Settings Singleton
settings = Settings()
