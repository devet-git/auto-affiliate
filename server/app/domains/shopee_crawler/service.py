"""
Shopee crawler service — orchestrates scraping and DB persistence.
"""
from sqlmodel import Session, select

from app.core.config import settings
from app.domains.shopee_crawler.affiliate import convert_affiliate_links
from app.domains.shopee_crawler.models import ProductStatus, ShopeeProduct
from app.domains.shopee_crawler.scraper import scrape_keyword


def search_and_save(
    keyword: str,
    count: int,
    session: Session,
) -> list[ShopeeProduct]:
    """
    Scrape Shopee products for a keyword and persist to database.
    Only stores image URLs — no local file downloads (per D-02).

    Returns the list of newly created ShopeeProduct records.
    """
    raw_items = scrape_keyword(keyword, max_items=count)

    products: list[ShopeeProduct] = []
    for item in raw_items:
        product = ShopeeProduct(
            original_url=item["original_url"],
            title=item.get("title", ""),
            price=item.get("price"),
            image_urls=item.get("image_urls", []),
            status=ProductStatus.PENDING,
            keyword=keyword,
        )
        session.add(product)
        products.append(product)

    session.commit()
    for p in products:
        session.refresh(p)

    return products


def get_pending_products(session: Session, limit: int = 20) -> list[ShopeeProduct]:
    """Fetch products with PENDING status for affiliate conversion."""
    statement = (
        select(ShopeeProduct)
        .where(ShopeeProduct.status == ProductStatus.PENDING)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def run_batch_affiliate_conversion(
    session: Session,
    batch_size: int = 20,
) -> dict[str, int]:
    """
    Convert a batch of PENDING products to CONVERTED using Playwright CMS automation (D-03).

    Fetches up to `batch_size` PENDING records, calls convert_affiliate_links()
    using the configured CMS session file, then updates DB:
      - On success: affiliate_url = tracking link, status = CONVERTED
      - On failure (URL not in result): status = FAILED

    Returns:
        {"converted": N, "failed": M, "total": T}
    """
    pending = get_pending_products(session, limit=batch_size)
    if not pending:
        return {"converted": 0, "failed": 0, "total": 0}

    urls = [p.original_url for p in pending]
    conversion_map = convert_affiliate_links(
        urls=urls,
        state_file=settings.SHOPEE_CMS_STATE_FILE,
    )

    converted = 0
    failed = 0
    for product in pending:
        affiliate_url = conversion_map.get(product.original_url)
        if affiliate_url:
            product.affiliate_url = affiliate_url
            product.status = ProductStatus.CONVERTED
            converted += 1
        else:
            product.status = ProductStatus.FAILED
            failed += 1
        session.add(product)

    session.commit()
    return {"converted": converted, "failed": failed, "total": len(pending)}

