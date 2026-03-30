"""
Shopee crawler management service — CRUD for sources, config, and product listing.
"""
from typing import Optional

from sqlmodel import Session, select

from app.domains.shopee_crawler.models import (
    CrawlerConfig,
    CrawlerConfigUpdate,
    CrawlerSource,
    CrawlerSourceCreate,
    ProductStatus,
    ShopeeProduct,
)


# ---------- CrawlerConfig ----------

def get_or_create_config(session: Session) -> CrawlerConfig:
    """Fetch the singleton CrawlerConfig (id=1), creating it with defaults if absent."""
    config = session.get(CrawlerConfig, 1)
    if config is None:
        config = CrawlerConfig(id=1, frequency_hours=24)
        session.add(config)
        session.commit()
        session.refresh(config)
    return config


def update_config(session: Session, config_update: CrawlerConfigUpdate) -> CrawlerConfig:
    """Patch the CrawlerConfig singleton with provided fields."""
    config = get_or_create_config(session)
    update_data = config_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    session.add(config)
    session.commit()
    session.refresh(config)
    return config


# ---------- CrawlerSource ----------

def get_sources(session: Session) -> list[CrawlerSource]:
    """Return all crawler sources ordered by id."""
    return list(session.exec(select(CrawlerSource).order_by(CrawlerSource.id)).all())


def create_source(session: Session, source_in: CrawlerSourceCreate) -> CrawlerSource:
    """Create a new CrawlerSource entry."""
    source = CrawlerSource(
        source_type=source_in.source_type,
        value=source_in.value.strip(),
        is_active=True,
    )
    session.add(source)
    session.commit()
    session.refresh(source)
    return source


def delete_source(session: Session, source_id: int) -> bool:
    """Delete a CrawlerSource by id. Returns True if deleted, False if not found."""
    source = session.get(CrawlerSource, source_id)
    if source is None:
        return False
    session.delete(source)
    session.commit()
    return True


# ---------- Products ----------

def get_products(
    session: Session,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
) -> list[ShopeeProduct]:
    """Return products with optional status/keyword filtering and pagination."""
    query = select(ShopeeProduct)
    if status:
        try:
            status_enum = ProductStatus(status.upper())
            query = query.where(ShopeeProduct.status == status_enum)
        except ValueError:
            pass  # ignore invalid status values
    if keyword:
        query = query.where(ShopeeProduct.keyword == keyword)
    query = query.order_by(ShopeeProduct.id.desc()).offset(skip).limit(limit)
    return list(session.exec(query).all())
