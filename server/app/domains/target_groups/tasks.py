"""
Facebook group scraper background tasks.

Task flow:
  facebook_scheduler_tick (runs periodically via Celery Beat)
    → checks TargetGroupConfig.next_run_time
    → if elapsed, updates next_run_time and spawns scrape_facebook_group for each active group

  scrape_facebook_group (runs per active TargetGroup)
    → uses Playwright + FB session cookies to fetch the Facebook group page
    → extracts posts via a single JS evaluate call (avoids Python↔JS per-element roundtrips)
    → skips posts whose original_url already exists in DB (prevents duplicates)

Session setup:
  Upload FB cookies via POST /api/v1/target-groups/session
  Supported formats:
    1. Playwright storage_state JSON: {"cookies": [...], "origins": [...]}
    2. Cookie-Editor browser extension export: [{"name": ..., "value": ..., ...}]
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

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


# ────────────────────────────────────────────────────────────────────────────────
# Celery tasks
# ────────────────────────────────────────────────────────────────────────────────

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
        is_due = config.next_run_time is None or now >= config.next_run_time

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

        return {
            "status": "dispatched",
            "dispatched": dispatched,
            "next_run": config.next_run_time.isoformat(),
        }


@celery_app.task(
    name="app.domains.target_groups.tasks.scrape_facebook_group",
    bind=True,
    max_retries=2,
    default_retry_delay=300,
)
def scrape_facebook_group(self, group_id: int) -> dict:
    """
    Scrape posts for a single TargetGroup using Playwright + FB session.
    Skips posts whose original_url already exists in DB.
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
        logger.info(f"[FBScraper] Group {group_id}: {added} added, {skipped} skipped.")
        return {"status": "ok", "group_id": group_id, "added": added, "skipped": skipped}


# ────────────────────────────────────────────────────────────────────────────────
# Helper utilities
# ────────────────────────────────────────────────────────────────────────────────

def _load_fb_storage_state() -> Optional[dict]:
    """
    Load Facebook session from FB_SESSION_FILE.
    Supports:
      1. Playwright storage_state:  {"cookies": [...], "origins": [...]}
      2. Cookie-Editor export:      [{"name":..., "value":..., "domain":...}]
    Returns None if file not found or invalid.
    """
    from app.core.config import settings

    session_file = Path(settings.FB_SESSION_FILE)
    if not session_file.exists():
        logger.warning(
            f"[FBScraper] No FB session file at '{session_file}'. "
            "Facebook will show a login wall. "
            "Upload cookies via POST /api/v1/target-groups/session"
        )
        return None

    try:
        raw = json.loads(session_file.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"[FBScraper] Failed reading session file {session_file}: {e}")
        return None

    # Playwright storage_state format
    if isinstance(raw, dict) and "cookies" in raw:
        logger.info(f"[FBScraper] Loaded Playwright session ({len(raw['cookies'])} cookies)")
        return raw

    # Cookie-Editor flat array — convert sameSite to Playwright format
    if isinstance(raw, list):
        same_site_map = {
            "no_restriction": "None",
            "lax": "Lax",
            "strict": "Strict",
            "unspecified": "None",
            "": "None",
        }
        cookies = []
        for c in raw:
            rs = (c.get("sameSite") or "").lower()
            cookie: dict = {
                "name": c.get("name", ""),
                "value": c.get("value", ""),
                "domain": c.get("domain", ".facebook.com"),
                "path": c.get("path", "/"),
                "secure": c.get("secure", True),
                "httpOnly": c.get("httpOnly", False),
                "sameSite": same_site_map.get(rs, "None"),
            }
            if "expirationDate" in c:
                cookie["expires"] = int(c["expirationDate"])
            cookies.append(cookie)
        logger.info(f"[FBScraper] Converted Cookie-Editor session ({len(cookies)} cookies)")
        return {"cookies": cookies, "origins": []}

    logger.error(f"[FBScraper] Unrecognised session file format in {session_file}")
    return None


def _scrape_group_posts(group_url: str, keywords: list) -> list:
    """
    Uses Playwright to scrape posts from a Facebook group page.

    Key design decisions:
    - Strip query params from URL (?locale=vi_VN breaks FB rendering)
    - Single page.evaluate() JS call to extract all post URLs + text at once
      (avoids per-element Python↔JS roundtrips which can hang indefinitely)
    - Keyboard End key scroll (more reliable than scrollTo on FB SPAs)
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("[FBScraper] Playwright not installed. Returning empty results.")
        return []

    storage_state = _load_fb_storage_state()

    # Strip query params — ?locale=vi_VN etc. break FB group rendering
    clean_url = group_url.split("?")[0].rstrip("/")
    if clean_url != group_url:
        logger.info(f"[FBScraper] URL normalized: {group_url} → {clean_url}")

    posts = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context_kwargs: dict = {
            "viewport": {"width": 1280, "height": 900},
        }
        if storage_state:
            context_kwargs["storage_state"] = storage_state

        context = browser.new_context(**context_kwargs)
        page = context.new_page()

        try:
            logger.info(f"[FBScraper] Navigating to {clean_url}")
            page.goto(clean_url, timeout=30000, wait_until="domcontentloaded")
            page.wait_for_timeout(4000)

            # Check for login wall
            current_url = page.url
            if "login" in current_url or "checkpoint" in current_url:
                logger.error(
                    f"[FBScraper] Login wall at {current_url}. "
                    "Upload fresh cookies via POST /api/v1/target-groups/session"
                )
                return []

            logger.info(f"[FBScraper] Page loaded: {current_url}")

            # Scroll down to load more content
            for _ in range(3):
                page.keyboard.press("End")
                page.wait_for_timeout(1500)

            # Expand long posts by clicking "See more" / "Xem thêm"
            page.evaluate("""
                () => {
                    document.querySelectorAll('div[role="button"]').forEach(btn => {
                        if (btn.innerText) {
                            const txt = btn.innerText.toLowerCase();
                            if (txt === "xem thêm" || txt === "see more") {
                                btn.click();
                            }
                        }
                    });
                }
            """)
            page.wait_for_timeout(1500)

            # ── Extract all post URLs + text in a SINGLE JS call ──
            # Never pass element handles as args — that causes hangs.
            raw_data: list = page.evaluate("""
                () => {
                    const posts = [];
                    const messageNodes = document.querySelectorAll(
                        'div[data-ad-comet-preview="message"], div[data-ad-preview="message"], div[dir="auto"][style*="text-align: start;"]'
                    );
                    
                    messageNodes.forEach(node => {
                        const text = node.innerText || '';
                        if (text.length < 10) return;
                        
                        let link = "";
                        let parent = node;
                        for (let i = 0; i < 15; i++) {
                            parent = parent.parentElement;
                            if (!parent) break;
                            
                            const a = parent.querySelector('a[href*="/post"], a[href*="/permalink"]');
                            if (a) {
                                link = a.href || "";
                                break;
                            }
                        }
                        
                        posts.push({ url: link, text: text });
                    });
                    
                    return posts.slice(0, 25);
                }
            """)

            logger.info(f"[FBScraper] JS found {len(raw_data)} post candidates")

            keywords_lower = [k.lower() for k in (keywords or [])]
            seen_urls = set()
            for item in raw_data:
                url = item.get("url", "")
                text = item.get("text", "")
                
                if not url or '/reels/' in url:
                    continue
                    
                url = url.split('?')[0]  # strip URL params AND comment_id
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                
                if keywords_lower and not any(kw in text.lower() for kw in keywords_lower):
                    continue
                if url.startswith("/"):
                    url = f"https://www.facebook.com{url}"
                posts.append({
                    "original_url": url,
                    "content": text[:500],
                    "author": "Unknown",
                    "comments_count": 0,
                    "reactions_count": 0,
                })
                if len(posts) >= 20:
                    break

            logger.info(f"[FBScraper] {len(posts)} posts after keyword filter (keywords={keywords})")

        except Exception as e:
            logger.error(f"[FBScraper] Error scraping {clean_url}: {e}", exc_info=True)
        finally:
            browser.close()

    return posts
