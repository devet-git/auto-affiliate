import json
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.domains.admin.dependencies import get_current_admin
from app.domains.shopee_crawler.service import run_batch_affiliate_conversion, search_and_save

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

