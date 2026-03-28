"""
Shopee crawler service — orchestrates scraping and DB persistence.
"""
from sqlmodel import Session, select

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
    return session.exec(statement).all()
