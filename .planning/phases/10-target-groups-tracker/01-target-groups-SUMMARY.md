---
plan: 01-target-groups
phase: 10
status: complete
completed: 2026-03-31
---

# Plan 01: Target Groups — Summary

## What Was Built

1. **`server/app/domains/target_groups/models.py`** — SQLModel tables:
   - `TargetGroup`: url, name, keywords (JSON), is_active, created_at
   - `TargetGroupConfig`: frequency_hours, next_run_time (singleton)
   - `ScrapedPost`: original_url, content, author, comments_count, reactions_count, target_group_id, status (PENDING/APPROVED/REJECTED)
   - Pydantic schemas: TargetGroupCreate, TargetGroupPublic, ScrapedPostPublic, PostStatusUpdate

2. **`server/app/domains/target_groups/router.py`** — FastAPI router mounted at `/api/v1/target-groups`:
   - `GET /` — list target groups
   - `POST /` — create target group
   - `DELETE /{id}` — delete group
   - `GET /posts/` — list scraped posts (optional `?status=` filter)
   - `PATCH /posts/{id}/status` — approve or reject a post

3. **`server/app/domains/target_groups/tasks.py`** — Celery tasks:
   - `facebook_scheduler_tick` — heartbeat task, checks TargetGroupConfig, dispatches per-group scrape
   - `scrape_facebook_group` — Playwright scraper (best-effort, headless Chromium), deduplicates by original_url

4. **`server/main.py`** — Updated to import `_target_groups_models` (ensures SQLModel table creation) and mount `target_groups_router`.

5. **`web/src/pages/TargetGroups.tsx`** — React page with:
   - **Configured Groups tab**: Table of groups + "Add Group" Dialog (url, name, keywords inputs), delete action
   - **Scraped Posts tab**: Table with author, content, status badge, "Approve" / "Reject" actions on PENDING posts

6. **`web/src/App.tsx`** — Added `/dashboard/targets` route
7. **`web/src/pages/Dashboard.tsx`** — Added "Target Groups" nav item to sidebar

## Key Files Created/Modified

- server/app/domains/target_groups/__init__.py (new)
- server/app/domains/target_groups/models.py (new)
- server/app/domains/target_groups/router.py (new)
- server/app/domains/target_groups/tasks.py (new)
- server/main.py (modified)
- web/src/pages/TargetGroups.tsx (new)
- web/src/App.tsx (modified)
- web/src/pages/Dashboard.tsx (modified)

## Self-Check: PASSED

- [x] TargetGroup, TargetGroupConfig, ScrapedPost models created with correct JSON/enum fields
- [x] Router mounted under /api/v1/target-groups/ with all CRUD + status PATCH endpoints
- [x] All endpoints require `Depends(get_current_admin)` auth
- [x] Celery tasks: facebook_scheduler_tick + scrape_facebook_group with Playwright
- [x] Duplicate dedup: `select(ScrapedPost).where(ScrapedPost.original_url == url)` before insert
- [x] TargetGroups.tsx uses Shadcn Table, Card, Dialog, Button from @/components/ui
- [x] Tabs implemented (groups / posts) with correct filtering
- [x] Approve/Reject sends PATCH with APPROVED/REJECTED status
- [x] Route /dashboard/targets registered in App.tsx
- [x] "Target Groups" nav link added to Dashboard sidebar
