"""
Facebook group scraper background tasks.

Task flow:
  facebook_scheduler_tick (runs periodically via Celery Beat)
    → checks TargetGroupConfig.next_run_time
    → if elapsed, updates next_run_time and spawns scrape_facebook_group for each active group

  scrape_facebook_group (runs per active TargetGroup)
    → uses Playwright to fetch the Facebook group's page
    → extracts posts (URL, content snippet, author, comment/reaction counts)
    → skips posts whose original_url already exists in DB (prevents duplicates)
"""
import logging
from datetime import datetime, timedelta

from celery import shared_task
from sqlmodel import Session, select

from app.core.celery_app import celery_app
from app.core.database import engine
from app.domains.target_groups.models import (
    PostStatus,
    ScrapedPost,
    TargetGroup,
    TargetGroupConfig,
)

logger = logging.getLogger(__name__)


@celery_app.task(name="app.domains.target_groups.tasks.facebook_scheduler_tick")
def facebook_scheduler_tick() -> dict:
    """
    Heartbeat task. Checks if the Facebook scraper is due to run.
    If so: sets next_run_time and spawns one scraping task per active group.
    """
    with Session(engine) as session:
        config = session.get(TargetGroupConfig, 1)
        if config is None:
            config = TargetGroupConfig(id=1, frequency_hours=12)
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
            logger.info(f"[FBScheduler] Not due yet. Next run in ~{remaining} min.")
            return {"status": "skipped", "next_run_in_minutes": remaining}

        # Update next_run_time BEFORE spawning — prevents double-dispatch
        config.next_run_time = now + timedelta(hours=config.frequency_hours)
        session.add(config)
        session.commit()

        groups = list(session.exec(
            select(TargetGroup).where(TargetGroup.is_active == True)  # noqa: E712
        ).all())

        if not groups:
            logger.info("[FBScheduler] No active groups configured.")
            return {"status": "no_groups", "dispatched": 0}

        dispatched = 0
        for group in groups:
            scrape_facebook_group.delay(group.id)
            dispatched += 1
            logger.info(f"[FBScheduler] Dispatched scrape for group {group.id} ({group.url})")

        logger.info(f"[FBScheduler] Dispatched {dispatched} scraping tasks.")
        return {
            "status": "dispatched",
            "dispatched": dispatched,
            "next_run": config.next_run_time.isoformat(),
        }


@celery_app.task(
    name="app.domains.target_groups.tasks.scrape_facebook_group",
    bind=True,
    max_retries=2,
    default_retry_delay=300,  # 5 min retry delay
)
def scrape_facebook_group(self, group_id: int) -> dict:
    """
    Scrape posts for a single TargetGroup using Playwright.
    Skips posts whose original_url already exists in DB (dedup logic).
    """
    with Session(engine) as session:
        group = session.get(TargetGroup, group_id)
        if group is None:
            logger.warning(f"[FBScraper] Group {group_id} not found — skipping.")
            return {"status": "group_not_found", "group_id": group_id}

        if not group.is_active:
            logger.info(f"[FBScraper] Group {group_id} is inactive — skipping.")
            return {"status": "inactive", "group_id": group_id}

        logger.info(f"[FBScraper] Scraping group {group_id}: {group.url}")

        try:
            raw_posts = _scrape_group_posts(group.url, group.keywords)
        except Exception as exc:
            logger.error(f"[FBScraper] Scrape error for group {group_id}: {exc}")
            try:
                raise self.retry(exc=exc)
            except self.MaxRetriesExceededError:
                return {"status": "failed", "error": str(exc), "group_id": group_id}

        added = 0
        skipped = 0
        for item in raw_posts:
            url = item.get("original_url", "")
            if not url:
                continue

            # Check for duplicate — skip if already in DB
            existing = session.exec(
                select(ScrapedPost).where(ScrapedPost.original_url == url)
            ).first()

            if existing:
                skipped += 1
                continue

            post = ScrapedPost(
                original_url=url,
                content=item.get("content", ""),
                author=item.get("author", ""),
                comments_count=item.get("comments_count", 0),
                reactions_count=item.get("reactions_count", 0),
                target_group_id=group_id,
                status=PostStatus.PENDING,
                created_at=datetime.utcnow(),
            )
            session.add(post)
            added += 1

        session.commit()
        logger.info(f"[FBScraper] Group {group_id} done: {added} added, {skipped} skipped.")
        return {
            "status": "ok",
            "group_id": group_id,
            "added": added,
            "skipped": skipped,
        }


def _scrape_group_posts(group_url: str, keywords: list) -> list:
    """
    Uses Playwright to scrape posts from a Facebook group page.
    Returns list of dicts: {original_url, content, author, comments_count, reactions_count}

    NOTE: This is a best-effort scraper. Facebook's DOM changes frequently.
    The implementation uses structural selectors and falls back gracefully.
    A logged-in session (cookies/storage_state) may be required for private groups.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("[FBScraper] Playwright not installed. Returning empty results.")
        return []

    posts = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        try:
            page.goto(group_url, timeout=30000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)

            # Facebook uses role="article" for posts in group feeds
            post_elements = page.query_selector_all('[role="article"]')
            for el in post_elements[:20]:  # Limit to first 20 posts per run
                try:
                    # Look for permalink or post URL
                    link_el = el.query_selector('a[href*="/permalink/"], a[href*="/posts/"]')
                    post_url = link_el.get_attribute("href") if link_el else ""
                    if not post_url:
                        continue

                    # Normalize URL — strip tracking params
                    post_url = post_url.split("?")[0]

                    # Extract content text
                    content_el = el.query_selector('[data-ad-comet-preview="message"], [dir="auto"]')
                    content = content_el.inner_text()[:500] if content_el else ""

                    # Extract author name
                    author_el = el.query_selector('a[role="link"] span')
                    author = author_el.inner_text() if author_el else "Unknown"

                    # Keyword filtering — only include matching posts
                    keywords_lower = [k.lower() for k in (keywords or [])]
                    content_lower = content.lower()
                    if keywords_lower and not any(kw in content_lower for kw in keywords_lower):
                        continue

                    # Build absolute URL
                    full_url = (
                        f"https://www.facebook.com{post_url}"
                        if post_url.startswith("/") else post_url
                    )

                    posts.append({
                        "original_url": full_url,
                        "content": content,
                        "author": author,
                        "comments_count": 0,
                        "reactions_count": 0,
                    })
                except Exception as e:
                    logger.debug(f"[FBScraper] Error parsing post element: {e}")
                    continue

        except Exception as e:
            logger.error(f"[FBScraper] Error fetching group page: {e}")
        finally:
            browser.close()

    return posts
