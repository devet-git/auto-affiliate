# Phase 10: Target Groups Tracker - Research

## Domain Understanding
Goal: Scraping Facebook groups to find high-engagement or keyword-relevant posts, and an admin UI to review these posts before they become targets for automated comments.

## Existing Paradigms
1. **Shopee Crawler Structure**: The auto-affiliate platform already uses an elegant structure for scraping sources:
   - `CrawlerSource` (e.g. KEYWORD, SHOP_URL)
   - `CrawlerConfig` (frequency definition)
   - `ShopeeProduct` (the scraped entities)
   - `crawler_scheduler_tick` (Celery heartbeat task checking config and spawning scrape task)
   - `scrape_shopee_source` (Celery task triggering the internal scraper logic)

2. **Phase 10 Analogue**: We emulate this paradigm for Facebook group scraping:
   - `TargetGroup`: Similar to `CrawlerSource`. Contains the Facebook Group URL/ID and associated Keywords.
   - `TargetGroupConfig`: Similar to `CrawlerConfig`. Contains run frequency for Facebook scraper.
   - `ScrapedPost`: Similar to `ShopeeProduct`. Holds the Facebook post URL, content, author, comments/reactions count, and an approval status (PENDING, APPROVED, REJECTED).
   - `facebook_scheduler_tick`: Heartbeat task for Facebook group scraping.
   - `scrape_facebook_group`: Task to scrape a specific group URL using Playwright (Tiered approach).

## Technical Approach & Stack
- **Database (SQLModel)**: Create models inside `app/domains/target_groups/models.py`. Ensure `TargetGroup`, `TargetGroupConfig`, and `ScrapedPost` tables.
- **Backend API (FastAPI)**: Create `router.py` in `app/domains/target_groups` with endpoints for CRUD TargetGroup, CRUD ScrapedPost, and endpoints to "Approve/Reject" a post.
- **Background Tasks (Celery)**: Scraper tasks located in `app/domains/target_groups/tasks.py`. Using Playwright to access FB DOM elements.
- **Frontend (React/Vite)**: A `TargetGroups.tsx` screen, re-using Shadcn `Table` and generic card structures, similar to `Products.tsx`.

## Risks & Edge Cases
1. **Playwright Facebook Structure changes**: Facebook's DOM changes often. Using robust locators or APIs where possible is essential. We will use `playwright` with a logged-in session (cookies) if authenticated scraping is needed.
2. **Duplicate Scraping**: We must ensure `ScrapedPost.fb_post_url` (or original_url) is globally unique, skipping already-scraped posts automatically. D-02 applies here similarly to Shopee products.
3. **Engagement parsing**: Comments and reactions are localized (e.g., "1.2K", "3 M", "1 bình luận"). We need safe parsing logic to convert string metrics into integer counts to trigger the "High Engagement" logic.

## Validation Architecture
- **Goal-Backward Check**: Can we define a target group, have the backend scrape it to populate a table of pending posts, and approve a post manually?
- **Key Dimensions**:
  1. TargetGroup CRUD operates properly.
  2. ScrapedPost duplicates are ignored.
  3. UI correctly renders posts and approval actions.
  4. Scraper Celery logic completes successfully without hanging.
