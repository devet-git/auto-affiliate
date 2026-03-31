# Phase 09: Product Management - Research

## Goal
Implement background crawler for Shopee products (by Admin criteria) and a Web UI to manage the scraped product list.

## Architecture

1.  **Backend Services**:
    *   **Models**: We need an entity to store the target criteria `CrawlerSource` (e.g., keyword="giày nam", shop_url="..."), and an entity for `GlobalSetting` or `CrawlerConfig` to store the frequency. The `ShopeeProduct` model already exists but needs its CRUD operations exposed.
    *   **Celery Beat**: Instead of a dynamic RedBeat scheduler which adds complexity, we simply run a heartbeat task e.g., `@celery.task(name="crawler_scheduler")` every hour. It checks the DB for `CrawlerConfig.next_run`. If due, it spawns `scrape_shopee_task` for each active `CrawlerSource` and updates `next_run`.
    *   **Scraper Engine**: Use `Playwright` to bypass basic Shopee protections (which often block raw requests). We already depend on Playwright. Alternatively, use simple `requests` with valid headers if Shopee API `search/search_items` allows it without login. Playwright is safer for continuous scraping.
    *   **Duplicate Handling**: Upsert logic or skip logic. If `original_url` or `product_id` exists in `shopee_products`, continue without insertion.

2.  **Frontend Interface**:
    *   **Data Table**: Use Shadcn UI `DataTable` and React Query to fetch products from `GET /api/v1/products`.
    *   **Cards/Columns**: Thumbnail image, Title, Price, Status (Pending, Converted), Keyword.
    *   **Config Screen**: A small settings card below or in a separate tab to add new Keywords/Shop URLs and set the "Scrape Frequency".

## Gaps & Risks
- **Shopee Anti-bot**: Shopee frequently has captchas. We must run Playwright in headless mode but with stealth plugins, or accept that occasional runs will fail.
- **Database bloat**: Products table might get huge. Not an immediate issue for v1.1.

## Validation Architecture
- **Criteria**: Create a keyword, force the cron job to run or trigger it manually via the API, and check the DB for new `ShopeeProduct` records.
- **UI**: Ensure the React table loads, paginates, and displays the thumbnails correctly.
