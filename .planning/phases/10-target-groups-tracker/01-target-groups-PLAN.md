---
phase: 10
wave: 1
depends_on: []
files_modified:
  - server/app/domains/target_groups/models.py
  - server/app/domains/target_groups/router.py
  - server/app/domains/target_groups/tasks.py
  - web/src/pages/TargetGroups.tsx
  - web/src/App.tsx
autonomous: false
requirements_addressed: [TARG-01, TARG-02, TARG-03]
---

# Phase 10: Target Groups Tracker

<objective>
Implement the backend models, API, background scraper tasks, and frontend UI for managing target groups and scraped Facebook posts.
</objective>

<must_haves>
- TargetGroup and ScrapedPost models defined in SQLModel
- API endpoints to CRUD groups and patch post statuses
- Celery beat tasks to trigger Facebook scraping via Playwright
- Frontend TargetGroups page with tabs for groups and pending posts
</must_haves>

<task>
<action>
Create the `target_groups` domain in the backend.
1. Create `server/app/domains/target_groups/models.py`.
   - `TargetGroup`: id, url, name, keywords, is_active, created_at.
   - `TargetGroupConfig`: id, frequency_hours, next_run_time.
   - `ScrapedPost`: id, original_url, content, author, comments_count, reactions_count, target_group_id, status (PENDING, APPROVED, REJECTED), created_at.
2. Create `server/app/domains/target_groups/router.py`.
   - `GET /`, `POST /`, `DELETE /{id}` for groups.
   - `GET /posts/` (query by status).
   - `PATCH /posts/{id}/status` (change status to APPROVED/REJECTED).
3. Update `server/app/api/main.py` to include the `target_groups` router under prefix `/target-groups`.
</action>
<read_first>
- server/app/domains/shopee_crawler/models.py
- server/app/domains/shopee_crawler/router.py
</read_first>
<acceptance_criteria>
- `server/app/domains/target_groups/models.py` contains `class TargetGroup(SQLModel, table=True)`
- `server/app/domains/target_groups/router.py` contains `@router.get("/posts/")`
- `server/app/api/main.py` contains `router.include_router(target_groups.router, prefix="/target-groups", tags=["Target Groups"])`
</acceptance_criteria>
</task>

<task>
<action>
Implement Celery tasks for Facebook group scraping.
1. Create `server/app/domains/target_groups/tasks.py`.
2. Add `@celery_app.task(name="app.domains.target_groups.tasks.facebook_scheduler_tick")` to check `TargetGroupConfig` and dispatch scrape tasks.
3. Add `@celery_app.task(name="app.domains.target_groups.tasks.scrape_facebook_group")` to scrape posts using Playwright. Skips posts where `original_url` already exists in `ScrapedPost`.
4. Register the scheduler module so the heartbeat beat runs.
</action>
<read_first>
- server/app/domains/shopee_crawler/tasks.py
- server/app/domains/shopee_crawler/scraper.py
</read_first>
<acceptance_criteria>
- `server/app/domains/target_groups/tasks.py` contains `def facebook_scheduler_tick()`
- `server/app/domains/target_groups/tasks.py` contains `def scrape_facebook_group(self, group_id: int)`
- Duplicate post check uses `session.exec(select(ScrapedPost).where(ScrapedPost.original_url == url)).first()`
</acceptance_criteria>
</task>

<task>
<action>
Implement the React frontend `TargetGroups.tsx`.
1. Create `web/src/pages/TargetGroups.tsx`.
2. Use Shadcn Tabs (`<Tabs defaultValue="groups">`) for "Configured Groups" and "Scraped Posts".
3. Use Shadcn `Table` for both views.
4. "Approve" button triggers `PATCH /api/v1/target-groups/posts/{id}/status` with `{"status": "APPROVED"}`.
5. "Add Group" opens a Shadcn `Dialog` with an `Input` for group URL and keywords.
6. Add "Target Groups" routing path to `web/src/App.tsx`.
</action>
<read_first>
- web/src/pages/Products.tsx
- .planning/phases/10-target-groups-tracker/10-UI-SPEC.md
</read_first>
<acceptance_criteria>
- `web/src/pages/TargetGroups.tsx` contains `<Tabs>` and `Table` from Shadcn components
- Network request for approval uses `PATCH` method with `APPROVED` payload
- Browser page `web/src/App.tsx` contains `<Route path="/targets" element={<TargetGroups />} />`
</acceptance_criteria>
</task>
