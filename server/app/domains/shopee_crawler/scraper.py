"""
Shopee product scraper using Playwright (anti-bot browser automation).
Uses sync_playwright inside Celery workers — avoids async event loop conflicts.

Decision D-01: Playwright chosen for anti-bot capability (reused in Phase 4 Tier-2).
Decision D-02: Only stores image URLs — no local media downloads.
"""
import json
import logging
import math
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright

from app.core.config import settings

logger = logging.getLogger(__name__)


def _load_playwright_cookies(state_file: Path) -> list[dict]:
    """
    Load cookies from a session file and return them in Playwright format.

    Supports two input formats:
    - Cookie-Editor (browser extension): JSON array with expirationDate, sameSite as
      'no_restriction', hostOnly, storeId fields.
    - Playwright native: JSON dict with {"cookies": [...], "origins": [...]} shape.

    Raises ValueError if the file appears to contain non-cookie data (e.g., API response).
    """
    data = json.loads(state_file.read_text(encoding="utf-8"))

    # --- Detect Playwright native format ---
    if isinstance(data, dict):
        if "cookies" in data and isinstance(data["cookies"], list):
            return data["cookies"]  # already in Playwright format
        # Looks like something else (e.g. API response body)
        raise ValueError(
            f"{state_file.name} is not a cookies file. "
            "Expected a Cookie-Editor JSON array or Playwright storage_state dict. "
            f"Got a dict with keys: {list(data.keys())[:5]}. "
            "Re-export your Shopee session cookies from Cookie-Editor → Export → JSON."
        )

    if not isinstance(data, list):
        raise ValueError(f"{state_file.name} must be a JSON array or object, got {type(data)}")

    # --- Convert Cookie-Editor array format ---
    same_site_map = {
        "no_restriction": "None",
        "lax": "Lax",
        "strict": "Strict",
        None: "None",
    }

    cookies = []
    for c in data:
        if not isinstance(c, dict) or "name" not in c or "value" not in c:
            continue  # skip malformed entries
        expiry = c.get("expirationDate")
        cookies.append({
            "name": c["name"],
            "value": c["value"],
            "domain": c["domain"],
            "path": c.get("path", "/"),
            "secure": c.get("secure", False),
            "httpOnly": c.get("httpOnly", False),
            "sameSite": same_site_map.get(c.get("sameSite"), "None"),
            # Playwright expects an integer Unix timestamp; -1 means session cookie
            "expires": int(math.floor(expiry)) if expiry else -1,
        })
    return cookies


def scrape_keyword(
    keyword: str,
    max_items: int = 50,
    search_state_file: Path | None = None,
) -> list[dict[str, Any]]:
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
        search_state_file: Path to Cookie-Editor JSON file for logged-in Shopee session.
                           Defaults to shopee_state.json next to the server/ directory.
    """
    results: list[dict[str, Any]] = []
    max_items = min(max_items, 100)

    # Resolve state file: explicit arg → settings → error
    state_path = search_state_file or Path(settings.SHOPEE_SEARCH_STATE_FILE)
    if not state_path.is_absolute():
        # Relative paths are resolved from the server/ directory
        state_path = Path(__file__).parent.parent.parent.parent / state_path
    if not state_path.exists():
        raise FileNotFoundError(
            f"Shopee search session file not found: {state_path}. "
            "Export your logged-in Shopee cookies via Cookie-Editor → JSON, "
            f"then save to: {state_path.resolve()}"
        )

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
        pw_cookies = _load_playwright_cookies(state_path)
        logger.info(f"[Scraper] Loaded {len(pw_cookies)} cookies from {state_path.name}")

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
        context.add_cookies(pw_cookies)

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
                    # Shopee uses hashed class names that change with deployments.
                    # Use JS to find text matching Vietnamese price patterns (₫ or digit·dot).
                    price: str | None = item.evaluate("""el => {
                        const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
                        const priceRe = /[₫đ]|\\d{1,3}(?:\\.\\d{3})+/;
                        let node;
                        while ((node = walker.nextNode())) {
                            const t = node.textContent.trim();
                            if (t && priceRe.test(t) && t.length < 30) return t;
                        }
                        return null;
                    }""")

                    # --- Image URLs (strings ONLY — D-02 compliance) ---
                    # Product thumbnails: https://down-vn.img.susercontent.com/file/...
                    # UI icons to exclude: deo.shopeemobile.com/shopee/modules-federation/...
                    image_urls: list[str] = item.evaluate("""el => {
                        const imgs = el.querySelectorAll('img');
                        const results = [];
                        for (const img of imgs) {
                            const src = img.src || img.dataset.src || img.dataset.original || '';
                            if (!src.startsWith('https://')) continue;
                            if (src.includes('modules-federation')) continue;  // UI icons
                            if (src.endsWith('.svg')) continue;                 // vector icons
                            // Accept susercontent.com (product CDN) or shopee CDN
                            const isProductCdn = src.includes('susercontent.com')
                                              || (src.includes('shopee') && !src.includes('shopeemobile.com'));
                            if (!isProductCdn) continue;
                            // Only include images that actually loaded (naturalWidth > 50px)
                            if (img.naturalWidth > 50) results.push(src);
                        }
                        return results;
                    }""")

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
