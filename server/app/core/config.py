from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    # Admin Authentication (personal use — no DB user table needed)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD_HASH: str = ""

    # JWT Configuration
    SECRET_KEY: str = "changethis"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/auto_affiliate"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"

    # Shopee Affiliate CMS — Playwright session state file (D-03)
    # Admin exports logged-in session from browser, places at this path.
    # Playwright uses it to skip login and go directly to custom_link page.
    SHOPEE_CMS_STATE_FILE: str = "shopee_state.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
