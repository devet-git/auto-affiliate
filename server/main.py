from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.domains.admin.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DB tables (done in Plan 01-03)
    yield
    # Shutdown: cleanup (if needed)


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


@app.get("/api/v1/health", tags=["system"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "service": "auto-affiliate-api"}
