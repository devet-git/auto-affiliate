"""
Shopee product scraper using Playwright (anti-bot browser automation).
Uses sync_playwright inside Celery workers — avoids async event loop conflicts.

Decision D-01: Playwright chosen for anti-bot capability (reused in Phase 4 Tier-2).
Decision D-02: Only stores image URLs — no local media downloads.
"""
import logging
import time
from typing import Any

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


def scrape_keyword(keyword: str, max_items: int = 50) -> list[dict[str, Any]]:
    """
    Scrape Shopee search results for a given keyword.

    Returns list of dicts with keys:
      - original_url: str (product detail page URL)
      - title: str
      - price: str | None
      - image_urls: list[str]  <- URL strings ONLY, never downloads bytes (D-02)

    Args:
        keyword: Search term to query on shopee.vn
        max_items: Maximum number of products to return (default 50, capped at 100)
    """
    results: list[dict[str, Any]] = []
    max_items = min(max_items, 100)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
            locale="vi-VN",
            extra_http_headers={
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            },
        )

        # Mask automation fingerprint
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        page = context.new_page()

        try:
            url = f"https://shopee.vn/search?keyword={keyword}&sortBy=sales"
            logger.info(f"[Scraper] Navigating: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=45000)

            # Allow JS to render product grid
            page.wait_for_timeout(3000)

            # Scroll down multiple times to trigger lazy-load of product images
            for scroll_step in range(6):
                page.evaluate("window.scrollBy(0, window.innerHeight * 1.5)")
                page.wait_for_timeout(800)

            # Shopee product card selectors (try multiple — UI changes over time)
            selectors = [
                "li.shopee-search-item-result__item",
                "[data-sqe='item']",
                ".shopee-item-card-overlay",
            ]

            items = []
            for sel in selectors:
                items = page.query_selector_all(sel)
                if items:
                    logger.info(f"[Scraper] Using selector '{sel}', found {len(items)} items")
                    break

            if not items:
                logger.warning("[Scraper] No items found — Shopee may have changed its DOM structure")

            for item in items[:max_items]:
                try:
                    # --- Product URL ---
                    link_el = item.query_selector("a[href]")
                    href = link_el.get_attribute("href") if link_el else None
                    if not href:
                        continue
                    if not href.startswith("http"):
                        href = f"https://shopee.vn{href}"
                    # Remove query params to get clean canonical URL
                    href = href.split("?")[0]

                    # --- Title ---
                    title_selectors = [
                        "[data-sqe='name'] span",
                        ".line-clamp-2",
                        ".shopee-item-card__text-name",
                        "[class*='name'] span",
                    ]
                    title = ""
                    for tsel in title_selectors:
                        el = item.query_selector(tsel)
                        if el:
                            title = el.inner_text().strip()
                            break

                    # --- Price ---
                    price_selectors = [
                        ".shopee-price__current",
                        "[class*='price--current']",
                        "[class*='discountedPrice']",
                        "[class*='price'] span",
                    ]
                    price: str | None = None
                    for psel in price_selectors:
                        el = item.query_selector(psel)
                        if el:
                            raw = el.inner_text().strip()
                            if raw:
                                price = raw
                                break

                    # --- Image URLs (strings ONLY — D-02 compliance) ---
                    image_urls: list[str] = []
                    img_els = item.query_selector_all("img")
                    for img in img_els:
                        for attr in ("src", "data-src", "data-original"):
                            src = img.get_attribute(attr) or ""
                            # Filter out placeholder/base64 images
                            if src.startswith("http") and "shopee" in src:
                                image_urls.append(src)
                                break

                    results.append(
                        {
                            "original_url": href,
                            "title": title,
                            "price": price,
                            "image_urls": image_urls,
                        }
                    )

                except Exception as item_err:
                    logger.warning(f"[Scraper] Skipping item due to parse error: {item_err}")
                    continue

        except Exception as e:
            logger.error(f"[Scraper] Fatal error during scrape: {e}")
            raise RuntimeError(f"Shopee scraper failed: {e}") from e
        finally:
            context.close()
            browser.close()

    logger.info(f"[Scraper] Completed — {len(results)} products for keyword='{keyword}'")
    return results
