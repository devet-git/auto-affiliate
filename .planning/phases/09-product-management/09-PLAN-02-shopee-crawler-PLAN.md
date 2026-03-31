---
wave: 2
depends_on: [09-PLAN-01-schema-and-api-PLAN.md]
files_modified:
  - server/app/core/celery_app.py
  - server/app/domains/shopee_crawler/tasks.py
autonomous: false
requirements_addressed:
  - PROD-02
---

# Plan 02: Shopee Celery Crawler Setup

<objective>
To implement the background scheduler and the scraping logic using Playwright, safely skipping duplicates.
</objective>

<tasks>

<task>
<description>
Implement Celery Schedule and Dispatcher Task
</description>
<read_first>
- server/app/core/celery_app.py
- .planning/phases/09-product-management/09-CONTEXT.md
</read_first>
<action>
1. In `server/app/core/celery_app.py`, update `celery_app.conf.beat_schedule` to include a new periodic task `crawler_scheduler_tick` every 15 minutes.
2. Create `server/app/domains/shopee_crawler/tasks.py` if not exists.
3. Add `crawler_scheduler_tick` task that checks `CrawlerConfig.next_run_time`. If overdue:
   - Sets a new `next_run_time` = now + `frequency_hours`.
   - Fetches all active `CrawlerSource`s.
   - For each source, spawns `scrape_shopee_source_task.delay(source_id)`.
</action>
<acceptance_criteria>
- `server/app/core/celery_app.py` contains schedule entry for `crawler_scheduler_tick`.
- `server/app/domains/shopee_crawler/tasks.py` contains `@celery_app.task(name="crawler_scheduler_tick")`.
</acceptance_criteria>
</task>

<task>
<description>
Implement Scraper Logic with Playwright
</description>
<read_first>
- server/app/domains/shopee_crawler/tasks.py
</read_first>
<action>
1. In `server/app/domains/shopee_crawler/tasks.py`, implement `scrape_shopee_source_task(source_id: int)`.
2. Extract the source type (Keyword vs Shop URL).
3. Utilize python playwright to navigate to Shopee and parse item cards.
   - For duplicates check: If `original_url` exists in the `shopee_products` table, `continue` the loop and skip creating/updating the DB row.
   - Parse Title, Price, and `image_urls`.
   - Save to DB with status "PENDING".
4. Handle database sessions using isolated connection via SQLModel `Session(engine)`.
</action>
<acceptance_criteria>
- `server/app/domains/shopee_crawler/tasks.py` contains `scrape_shopee_source_task`.
- Contains `from sqlmodel import Session` and checks `session.exec(select(ShopeeProduct).where(ShopeeProduct.original_url == url)).first()`.
</acceptance_criteria>
</task>

</tasks>

<verification>
1. Test by executing `crawler_scheduler_tick.delay()` manually or triggering it via a beat worker `celery -A app.core.celery_app beat`.
2. Ensure no errors in Celery worker log: `celery -A app.core.celery_app worker --loglevel=info`.
</verification>
