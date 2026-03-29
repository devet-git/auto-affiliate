# Debug Session: web-ui-missing-features

**Created:** 2026-03-29  
**Status:** ROOT CAUSE FOUND  
**Slug:** web-ui-missing-features

## Symptoms

- **Expected:** Full automation control — configure Facebook accounts/phones/Appium, trigger auto-comment, trigger auto-post video, monitor tasks
- **Actual:** Web UI only has Dashboard, Campaigns (create/delete/basic edit), ApprovalQueue — no automation controls
- **Errors:** None — features simply do not exist in UI
- **Timeline:** System built phase-by-phase, automation backend was built but UI integration was never completed
- **Reproduction:** Open web app, navigate to Campaigns — nothing to configure for automation

## Evidence

### Backend Layer — EXISTS (functional)
- `server/app/domains/sys_worker/seeding_tasks.py`: Has `exec_fb_comment`, `exec_fb_batch_comment`, `exec_fb_post_reel`, `notify_admin_discord` Celery tasks
- `server/app/domains/content_sourcing/services/`: Has facebook_seeding service  
- `server/app/domains/content_sourcing/router.py`: Has content sourcing endpoints (7367 bytes — non-trivial)
- Celery workers are configured and running (`appium_phone` queue + default queue)

### Data Layer — INCOMPLETE
- `server/app/domains/campaign/models.py`: Only `id`, `name`, `status`, `created_at`, `updated_at`
- **Missing:** No `Device` model (UDID, label), no `FacebookAccount` model, no campaign automation config fields (post_urls, comment_template, assigned_device)

### API Layer — INCOMPLETE  
- `server/app/domains/sys_worker/router.py`: Only `/worker/test` endpoint — nothing to trigger seeding tasks
- `server/app/domains/campaign/router.py`: Only basic CRUD — no `/campaigns/{id}/run-comment`, `/campaigns/{id}/run-post`
- **Missing:** Device CRUD, Account CRUD, Campaign trigger endpoints

### Frontend Layer — INCOMPLETE
- `web/src/pages/`: Only `Dashboard.tsx`, `Campaigns.tsx`, `ApprovalQueue.tsx`, `Login.tsx`
- `Campaigns.tsx`: Only name + status fields — no automation config UI
- **Missing:** Devices page, Accounts page, Automation config in Campaign detail, Task trigger buttons, Task status monitoring

## Root Cause

The seeding automation backend (Celery tasks + Appium services) was fully built as Phase 3, but was never connected to the management layer: no DB models to store device/account config, no API endpoints to trigger tasks from external callers, and no frontend screens for configuration and task dispatch.

## Fix Plan

See implementation_plan.md for detailed fix plan.
