from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.domains.admin.router import router as auth_router
from app.domains.campaign import models as _campaign_models  # noqa: F401 — registers SQLModel metadata
from app.domains.shopee_crawler.router import router as crawler_router
from app.domains.shopee_crawler import models as _shopee_models  # noqa: F401 — registers ShopeeProduct with SQLModel metadata
from app.domains.sys_worker.router import router as worker_router
from app.domains.content_sourcing.router import router as sourcing_router
from app.domains.approval.router import router as approval_router
from app.domains.campaign.router import router as campaign_router
from app.domains.notify.bot import router as telegram_router, bot, WEBHOOK_URL, WEBHOOK_SECRET, dp
from app.core.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DB tables
    create_db_and_tables()
    
    # Try to set webhook if configured
    if WEBHOOK_URL and WEBHOOK_URL != "https://my-ngrok.url":
        try:
            url = f"{WEBHOOK_URL}/api/v1/webhook/telegram"
            await bot.set_webhook(url, secret_token=WEBHOOK_SECRET)
        except Exception as e:
            print(f"Error setting Telegram webhook: {e}")
            
    yield
    
    # Shutdown: cleanup (if needed)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.session.close()
    except Exception:
        pass


app = FastAPI(
    title="Auto Affiliate Control Center",
    description="Personal affiliate automation dashboard — Admin only",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(worker_router, prefix="/api/v1")
app.include_router(crawler_router, prefix="/api/v1")
app.include_router(sourcing_router, prefix="/api/v1")
app.include_router(approval_router, prefix="/api/v1")
app.include_router(campaign_router, prefix="/api/v1")
app.include_router(telegram_router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["system"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "service": "auto-affiliate-api"}
