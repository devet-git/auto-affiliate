"""
Shopee crawler background tasks — scheduler tick and per-source scraping.

Task flow:
  crawler_scheduler_tick (runs every 15 min via Celery Beat)
    → checks CrawlerConfig.next_run_time
    → if elapsed, updates next_run_time and spawns scrape_shopee_source for each active source

  scrape_shopee_source (runs per active CrawlerSource)
    → uses existing scraper.scrape_keyword() for KEYWORD sources
    → skips products whose original_url already exists in DB (D-02 decision: skip duplicates)
"""
import logging
from datetime import datetime, timedelta

from celery import shared_task
from sqlmodel import Session, select

from app.core.celery_app import celery_app
from app.core.database import engine
from app.domains.shopee_crawler.models import (
    CrawlerConfig,
    CrawlerSource,
    ProductStatus,
    ShopeeProduct,
    SourceType,
)

logger = logging.getLogger(__name__)


@celery_app.task(name="app.domains.shopee_crawler.tasks.crawler_scheduler_tick")
def crawler_scheduler_tick() -> dict:
    """
    Heartbeat task (every 15 min). Checks if the crawler is due to run.
    If so: sets next_run_time and spawns one scraping task per active source.
    """
    with Session(engine) as session:
        # Fetch or create singleton config
        config = session.get(CrawlerConfig, 1)
        if config is None:
            config = CrawlerConfig(id=1, frequency_hours=24)
            session.add(config)
            session.commit()
            session.refresh(config)

        now = datetime.utcnow()
        is_due = (
            config.next_run_time is None
            or now >= config.next_run_time
        )

        if not is_due:
            remaining = (config.next_run_time - now).seconds // 60
            logger.info(f"[CrawlerScheduler] Not due yet. Next run in ~{remaining} min.")
            return {"status": "skipped", "next_run_in_minutes": remaining}

        # Update next_run_time BEFORE spawning tasks — prevents double-dispatch
        config.next_run_time = now + timedelta(hours=config.frequency_hours)
        session.add(config)
        session.commit()

        # Fetch all active sources
        sources = list(session.exec(
            select(CrawlerSource).where(CrawlerSource.is_active == True)  # noqa: E712
        ).all())

        if not sources:
            logger.info("[CrawlerScheduler] No active sources configured.")
            return {"status": "no_sources", "dispatched": 0}

        dispatched = 0
        for source in sources:
            scrape_shopee_source.delay(source.id)
            dispatched += 1
            logger.info(f"[CrawlerScheduler] Dispatched scrape for source {source.id} ({source.source_type}: {source.value})")

        logger.info(f"[CrawlerScheduler] Dispatched {dispatched} scraping tasks.")
        return {
            "status": "dispatched",
            "dispatched": dispatched,
            "next_run": config.next_run_time.isoformat(),
        }


@celery_app.task(
    name="app.domains.shopee_crawler.tasks.scrape_shopee_source",
    bind=True,
    max_retries=2,
    default_retry_delay=300,  # 5 min retry delay
)
def scrape_shopee_source(self, source_id: int) -> dict:
    """
    Scrape products for a single CrawlerSource and persist new ones to DB.
    Skips products whose original_url already exists (decision D-02).
    """
    with Session(engine) as session:
        source = session.get(CrawlerSource, source_id)
        if source is None:
            logger.warning(f"[CrawlerScraper] Source {source_id} not found — skipping.")
            return {"status": "source_not_found", "source_id": source_id}

        if not source.is_active:
            logger.info(f"[CrawlerScraper] Source {source_id} is inactive — skipping.")
            return {"status": "inactive", "source_id": source_id}

        logger.info(f"[CrawlerScraper] Starting scrape for source {source_id}: {source.source_type}={source.value}")

        try:
            if source.source_type == SourceType.KEYWORD:
                from app.domains.shopee_crawler.scraper import scrape_keyword
                raw_items = scrape_keyword(keyword=source.value, max_items=50)
            else:
                # SHOP_URL — not yet implemented, log and skip
                logger.warning(f"[CrawlerScraper] SHOP_URL scraping not yet implemented for source {source_id}")
                return {"status": "not_implemented", "source_type": source.source_type}

        except Exception as exc:
            logger.error(f"[CrawlerScraper] Scrape error for source {source_id}: {exc}")
            try:
                raise self.retry(exc=exc)
            except self.MaxRetriesExceededError:
                return {"status": "failed", "error": str(exc), "source_id": source_id}

        # Persist new products — skip duplicates
        added = 0
        skipped = 0
        for item in raw_items:
            url = item.get("original_url", "")
            if not url:
                continue

            # Check duplicate
            existing = session.exec(
                select(ShopeeProduct).where(ShopeeProduct.original_url == url)
            ).first()

            if existing:
                skipped += 1
                continue

            product = ShopeeProduct(
                original_url=url,
                title=item.get("title", ""),
                price=item.get("price"),
                image_urls=item.get("image_urls", []),
                status=ProductStatus.PENDING,
                keyword=source.value if source.source_type == SourceType.KEYWORD else None,
                created_at=datetime.utcnow(),
            )
            session.add(product)
            added += 1

        session.commit()
        logger.info(f"[CrawlerScraper] Source {source_id} done: {added} added, {skipped} skipped.")
        return {
            "status": "ok",
            "source_id": source_id,
            "added": added,
            "skipped": skipped,
        }
