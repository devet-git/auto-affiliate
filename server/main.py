from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.domains.admin.router import router as auth_router
from app.domains.campaign import models as _campaign_models  # noqa: F401 — registers SQLModel metadata
from app.domains.devices import models as _device_models  # noqa: F401 — registers Device with SQLModel metadata
from app.domains.shopee_crawler.router import router as crawler_router
from app.domains.shopee_crawler import models as _shopee_models  # noqa: F401 — registers ShopeeProduct with SQLModel metadata
from app.domains.sys_worker import models as _sys_worker_models  # noqa: F401 — registers TaskLog and AppSetting
from app.domains.sys_worker.router import router as worker_router
from app.domains.content_sourcing.router import router as sourcing_router
from app.domains.approval.router import router as approval_router
from app.domains.campaign.router import router as campaign_router
from app.domains.devices.router import router as devices_router
from app.domains.notify.bot import bot, DISCORD_BOT_TOKEN
from app.core.database import create_db_and_tables
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DB tables
    create_db_and_tables()
    
    # Start Discord Bot in background
    bot_task = None
    if DISCORD_BOT_TOKEN and DISCORD_BOT_TOKEN != "mock_discord_token":
        bot_task = asyncio.create_task(bot.start(DISCORD_BOT_TOKEN))
            
    yield
    
    # Shutdown: cleanup
    try:
        if bot_task:
            await bot.close()
            bot_task.cancel()
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
app.include_router(devices_router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["system"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "service": "auto-affiliate-api"}
