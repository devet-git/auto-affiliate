from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.core.database import get_session
from app.domains.admin.dependencies import get_current_admin
from app.domains.shopee_crawler.service import search_and_save

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
async def trigger_shopee_search(
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
