import json
import os
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.domains.admin.dependencies import get_current_admin
from app.domains.shopee_crawler.service import run_batch_affiliate_conversion, search_and_save
from app.domains.shopee_crawler.crawler_service import (
    get_or_create_config,
    update_config,
    get_sources,
    create_source,
    delete_source,
    get_products,
)
from app.domains.shopee_crawler.models import (
    CrawlerConfigPublic,
    CrawlerConfigUpdate,
    CrawlerSourceCreate,
    CrawlerSourcePublic,
    ShopeeProductPublic,
)
from app.domains.sys_worker.seeding_tasks import notify_admin_discord

router = APIRouter(prefix="/crawler/shopee", tags=["shopee-crawler"])


# ---------- Request / Response schemas ----------


class SearchRequest(BaseModel):
    keyword: str
    count: int = 20


class ProductSummary(BaseModel):
    id: int
    original_url: str
    title: str
    price: str | None
    image_urls: list[str]
    status: str
    keyword: str | None


class SearchResponse(BaseModel):
    scraped: int
    products: list[ProductSummary]


# ---------- Endpoints ----------


@router.post("/search", response_model=SearchResponse)
def trigger_shopee_search(
    body: SearchRequest,
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
) -> SearchResponse:
    """
    Trigger Playwright-based Shopee keyword/category search.

    - Launches headless Chromium to bypass anti-bot measures (D-01).
    - Saves discovered products with image URLs only — no media downloads (D-02).
    - All saved products start with status=PENDING, ready for affiliate conversion.
    - Requires valid admin JWT.
    """
    if not body.keyword.strip():
        raise HTTPException(status_code=422, detail="keyword must not be empty")
    if not (1 <= body.count <= 100):
        raise HTTPException(status_code=422, detail="count must be between 1 and 100")

    try:
        products = search_and_save(
            keyword=body.keyword.strip(),
            count=body.count,
            session=session,
        )
        return SearchResponse(
            scraped=len(products),
            products=[
                ProductSummary(
                    id=p.id,
                    original_url=p.original_url,
                    title=p.title,
                    price=p.price,
                    image_urls=p.image_urls,
                    status=p.status.value,
                    keyword=p.keyword,
                )
                for p in products
            ],
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# ---------- Session Management ----------


class SessionUploadResponse(BaseModel):
    saved_to: str
    message: str


@router.post("/session", response_model=SessionUploadResponse)
async def upload_shopee_session(
    file: UploadFile = File(...),
    _admin: dict = Depends(get_current_admin),
) -> SessionUploadResponse:
    """
    Upload a Playwright storage_state JSON to enable affiliate link generation (/convert).

    ⚠️  This is the **Shopee Affiliate CMS** session — NOT the search cookie file.
    - Search cookies (for /search) → configure SHOPEE_SEARCH_STATE_FILE in .env
    - CMS session (for /convert)  → upload here, saved to SHOPEE_CMS_STATE_FILE

    Export your logged-in Shopee Affiliate portal session using Playwright's
    context.storage_state(), then POST the file here.
    The server saves it to the path configured in SHOPEE_CMS_STATE_FILE (.env).

    Requires valid admin JWT.
    """
    content = await file.read()
    try:
        # Validate it's actual JSON before saving
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("Session file must be a JSON object")
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid JSON: {e}")

    state_path = Path(settings.SHOPEE_CMS_STATE_FILE)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_bytes(content)

    return SessionUploadResponse(
        saved_to=str(state_path.resolve()),
        message="Session saved. You can now trigger /convert to generate affiliate links.",
    )


# ---------- Affiliate Conversion ----------


class ConvertResponse(BaseModel):
    converted: int
    failed: int
    total: int
    message: str


@router.post("/convert", response_model=ConvertResponse)
def trigger_affiliate_conversion(
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
) -> ConvertResponse:
    """
    Convert a batch of PENDING products to affiliate tracking links (D-03).

    Uses Playwright to automate the Shopee Affiliate CMS portal
    with the pre-uploaded session file (via POST /session).
    Processes up to 20 PENDING products per call.

    - PENDING → CONVERTED  (affiliate_url populated)
    - PENDING → FAILED     (conversion error / URL not returned)

    Requires valid admin JWT.
    """
    state_path = Path(settings.SHOPEE_CMS_STATE_FILE)
    if not state_path.exists():
        raise HTTPException(
            status_code=412,
            detail=(
                f"No session file found at '{settings.SHOPEE_CMS_STATE_FILE}'. "
                "Upload your Shopee Affiliate session via POST /session first."
            ),
        )

    try:
        stats = run_batch_affiliate_conversion(session=session)
        
        if stats["converted"] > 0:
            notify_admin_discord.delay(
                f"🎉 **Batch conversion complete!**\n"
                f"Successfully converted {stats['converted']} links.\n"
                f"Failed: {stats['failed']}\n"
                f"Access the Dashboard Approval Queue or run `/approve <id>` to review and post."
            )
            
        return ConvertResponse(
            converted=stats["converted"],
            failed=stats["failed"],
            total=stats["total"],
            message=(
                f"Batch complete: {stats['converted']} converted, "
                f"{stats['failed']} failed out of {stats['total']} processed."
            ),
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# ============================================================
# Product Management — Crawler Config, Sources, Products List
# ============================================================


@router.get("/config", response_model=CrawlerConfigPublic, tags=["product-management"])
def get_crawler_config(
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
) -> CrawlerConfigPublic:
    """Return the current crawler configuration (frequency, next run time)."""
    config = get_or_create_config(session)
    return CrawlerConfigPublic(
        id=config.id,
        frequency_hours=config.frequency_hours,
        next_run_time=config.next_run_time,
    )


@router.patch("/config", response_model=CrawlerConfigPublic, tags=["product-management"])
def patch_crawler_config(
    body: CrawlerConfigUpdate,
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
) -> CrawlerConfigPublic:
    """Update the crawler frequency and/or next run time."""
    config = update_config(session, body)
    return CrawlerConfigPublic(
        id=config.id,
        frequency_hours=config.frequency_hours,
        next_run_time=config.next_run_time,
    )


@router.get("/sources", response_model=List[CrawlerSourcePublic], tags=["product-management"])
def list_crawler_sources(
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
) -> List[CrawlerSourcePublic]:
    """List all configured crawl sources (keywords and shop URLs)."""
    sources = get_sources(session)
    return [
        CrawlerSourcePublic(
            id=s.id,
            source_type=s.source_type,
            value=s.value,
            is_active=s.is_active,
        )
        for s in sources
    ]


@router.post("/sources", response_model=CrawlerSourcePublic, status_code=201, tags=["product-management"])
def add_crawler_source(
    body: CrawlerSourceCreate,
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
) -> CrawlerSourcePublic:
    """Add a new keyword or shop URL as a crawler source."""
    if not body.value.strip():
        raise HTTPException(status_code=422, detail="value must not be empty")
    source = create_source(session, body)
    return CrawlerSourcePublic(
        id=source.id,
        source_type=source.source_type,
        value=source.value,
        is_active=source.is_active,
    )


@router.delete("/sources/{source_id}", status_code=204, tags=["product-management"])
def remove_crawler_source(
    source_id: int,
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
) -> None:
    """Delete a crawler source by ID."""
    deleted = delete_source(session, source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Source {source_id} not found")


@router.get("/products", response_model=List[ShopeeProductPublic], tags=["product-management"])
def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    status: Optional[str] = Query(default=None, description="Filter by status: PENDING, CONVERTED, FAILED"),
    keyword: Optional[str] = Query(default=None, description="Filter by keyword"),
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
) -> List[ShopeeProductPublic]:
    """List scraped Shopee products with optional status/keyword filtering."""
    products = get_products(session, skip=skip, limit=limit, status=status, keyword=keyword)
    return [
        ShopeeProductPublic(
            id=p.id,
            original_url=p.original_url,
            affiliate_url=p.affiliate_url,
            title=p.title,
            price=p.price,
            image_urls=p.image_urls,
            status=p.status,
            keyword=p.keyword,
            created_at=p.created_at,
        )
        for p in products
    ]
