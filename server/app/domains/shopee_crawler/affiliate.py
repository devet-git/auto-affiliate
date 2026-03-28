"""
Shopee Affiliate CMS link converter — "tà đạo" approach (D-03).

Instead of using Shopee's official API (requires whitelist approval),
this module uses Playwright to automate the Shopee Affiliate web portal
with a pre-captured browser session (storage_state JSON).

Usage flow:
  1. Admin logs into https://affiliate.shopee.vn/ manually in their browser.
  2. Admin exports session using a browser extension (e.g., Cookie Editor)
     and saves it as shopee_state.json (path set in SHOPEE_CMS_STATE_FILE).
  3. This module loads that session, navigates to the custom link generator,
     pastes URLs, and extracts the resulting tracking links.
"""
import json
import logging
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

AFFILIATE_CUSTOM_LINK_URL = "https://affiliate.shopee.vn/custom_link"


def convert_affiliate_links(
    urls: list[str],
    state_file: str,
) -> dict[str, str]:
    """
    Convert a list of Shopee product URLs into affiliate tracking links.

    Uses Playwright with a pre-captured Shopee Affiliate CMS session
    (storage_state JSON) to automate the custom_link generator page.

    Args:
        urls: List of original Shopee product URLs to convert.
        state_file: Path to Playwright storage state JSON (exported from browser).

    Returns:
        dict mapping original_url → affiliate_url.
        If a URL fails to convert, it is omitted from the result.

    Raises:
        FileNotFoundError: If state_file does not exist.
        RuntimeError: If the CMS page cannot be reached or session is expired.
    """
    state_path = Path(state_file)
    if not state_path.exists():
        raise FileNotFoundError(
            f"Shopee CMS session file not found: {state_file}\n"
            "Export your logged-in session from the browser and place it at this path.\n"
            "Set SHOPEE_CMS_STATE_FILE in .env to override the default path."
        )

    result: dict[str, str] = {}
    if not urls:
        return result

    logger.info(f"[Affiliate] Converting {len(urls)} URLs using session: {state_file}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(
            storage_state=str(state_path),
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="vi-VN",
        )
        page = context.new_page()

        try:
            logger.info(f"[Affiliate] Navigating to: {AFFILIATE_CUSTOM_LINK_URL}")
            page.goto(AFFILIATE_CUSTOM_LINK_URL, wait_until="networkidle", timeout=30000)

            # Check if session expired (redirected to login page)
            if "login" in page.url or "sign_in" in page.url:
                raise RuntimeError(
                    "Shopee Affiliate session expired. "
                    "Please re-export your session from the browser and update shopee_state.json."
                )

            page.wait_for_timeout(2000)

            # Process URLs in batches of 10 (portal limit per submission)
            batch_size = 10
            for batch_start in range(0, len(urls), batch_size):
                batch = urls[batch_start : batch_start + batch_size]
                batch_text = "\n".join(batch)

                logger.info(f"[Affiliate] Processing batch {batch_start // batch_size + 1} ({len(batch)} URLs)")

                # Find the textarea for custom link input
                # Shopee Affiliate portal uses a textarea for bulk URL input
                textarea_selectors = [
                    "textarea[placeholder*='link']",
                    "textarea[placeholder*='URL']",
                    "textarea[placeholder*='url']",
                    "textarea",
                ]
                textarea = None
                for sel in textarea_selectors:
                    textarea = page.query_selector(sel)
                    if textarea:
                        break

                if not textarea:
                    logger.error("[Affiliate] Could not find URL input textarea on page")
                    break

                # Clear and paste URLs
                textarea.click()
                textarea.fill(batch_text)
                page.wait_for_timeout(500)

                # Click the generate/submit button
                submit_selectors = [
                    "button[type='submit']",
                    "button:has-text('Tạo link')",
                    "button:has-text('Generate')",
                    "button:has-text('Lấy link')",
                    "[class*='submit']",
                    "[class*='generate']",
                ]
                submitted = False
                for btn_sel in submit_selectors:
                    btn = page.query_selector(btn_sel)
                    if btn:
                        btn.click()
                        submitted = True
                        break

                if not submitted:
                    logger.warning("[Affiliate] Could not find submit button — skipping batch")
                    continue

                # Wait for results to appear
                page.wait_for_timeout(3000)

                # Extract the output tracking links
                # The portal typically renders results in a table or list
                result_selectors = [
                    "table tbody tr",
                    "[class*='result'] a",
                    "[class*='link-result']",
                ]
                rows = []
                for rsel in result_selectors:
                    rows = page.query_selector_all(rsel)
                    if rows:
                        break

                for i, row in enumerate(rows):
                    if i >= len(batch):
                        break
                    try:
                        # Extract the generated tracking link from each row
                        link_el = row.query_selector("a[href*='shope.ee'], a[href*='s.shopee']")
                        if not link_el:
                            # Try reading text content that looks like a short URL
                            text = row.inner_text().strip()
                            if "shope.ee" in text or "s.shopee" in text:
                                for part in text.split():
                                    if "shope.ee" in part or "s.shopee" in part:
                                        result[batch[i]] = part.strip()
                                        break
                        else:
                            affiliate_url = link_el.get_attribute("href") or link_el.inner_text().strip()
                            if affiliate_url:
                                result[batch[i]] = affiliate_url
                    except Exception as row_err:
                        logger.warning(f"[Affiliate] Failed to extract row {i}: {row_err}")

                # Reload page between batches to reset form state
                if batch_start + batch_size < len(urls):
                    page.reload(wait_until="networkidle")
                    page.wait_for_timeout(1500)

        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"[Affiliate] CMS automation error: {e}")
            raise RuntimeError(f"Affiliate link conversion failed: {e}") from e
        finally:
            context.close()
            browser.close()

    logger.info(f"[Affiliate] Converted {len(result)}/{len(urls)} links successfully")
    return result
