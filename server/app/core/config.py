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

    # Shopee search session — Cookie-Editor JSON export of a logged-in Shopee account.
    # Used by the scraper to bypass Shopee's login wall when searching products.
    # Export: open shopee.vn in Chrome → Cookie-Editor extension → Export as JSON.
    SHOPEE_SEARCH_STATE_FILE: str = "shopee_search_cookies.json"

    # Shopee Affiliate CMS — Playwright session state file (D-03)
    # Admin exports logged-in Shopee Affiliate portal session, places at this path.
    # Used by /convert to automate affiliate link generation without re-login.
    SHOPEE_CMS_STATE_FILE: str = "shopee_cms_state.json"

    # Appium / Android Device (Phase 3 — Facebook Seeding via real phone)
    # UDID from `adb devices`. Leave empty if device not connected.
    APPIUM_DEVICE_UDID: str = ""
    APPIUM_SERVER_URL: str = "http://127.0.0.1:4723"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
