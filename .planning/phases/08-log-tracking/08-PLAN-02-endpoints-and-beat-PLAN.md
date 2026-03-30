---
wave: 2
depends_on: ["08-PLAN-01-database-signals.md"]
files_modified:
  - server/app/domains/sys_worker/router.py
  - server/app/domains/sys_worker/tasks.py
  - server/app/core/celery_app.py
  - server/main.py
requirements:
  - LOG-01
  - LOG-02
autonomous: true
---

# Plan 02 - Endpoints and Cleanup Beat Task

<objective>
Provide an API to query logs and configure retention, plus a background cleanup task.
</objective>

<verification>
REST endpoints successfully return data. Calling cleanup task deletes old rows.
</verification>

<must_haves>
- Filtering logs by task_name and status must be handled server-side to handle scale.
- Settings endpoint must allow CRUD for settings.
</must_haves>

<tasks>
<task id="08-02-01" description="Logs endpoint">
<read_first>
- server/app/domains/sys_worker/models.py
- server/app/core/database.py
- server/main.py
</read_first>
<action>
1. Create/Update `server/app/domains/sys_worker/router.py` (if it doesn't exist, create it and register in `server/main.py` explicitly).
2. Add `GET /logs` returning a list of `TaskLog`. Accept optional query params `status`, `task_name`, `limit=50`, `offset=0`.
3. Add `GET /settings/{key}` and `POST /settings/` to manage `AppSetting`, especially `log_retention_days`.
4. Expose the router in `server/main.py` via `app.include_router(...)`.
</action>
<acceptance_criteria>
- `server/app/domains/sys_worker/router.py` contains `router.get("/logs")`
- `server/main.py` contains `app.include_router(` referencing the new router
</acceptance_criteria>
</task>

<task id="08-02-02" description="Cleanup Beat Task">
<read_first>
- server/app/domains/sys_worker/tasks.py
- server/app/core/celery_app.py
</read_first>
<action>
1. In `server/app/domains/sys_worker/tasks.py`, implement a new background task `@celery_app.task(name="cleanup_expired_logs")`.
2. It should open a DB session, fetch `log_retention_days` from `AppSetting` (default 7). Calculate threshold date and execute a bulk delete of `TaskLog` where `started_at < threshold`.
3. In `server/app/core/celery_app.py`, configure celery beat schedule: add `from celery.schedules import crontab` and configure `celery_app.conf.beat_schedule` to run `cleanup_expired_logs` daily at midnight.
</action>
<acceptance_criteria>
- `server/app/domains/sys_worker/tasks.py` contains `@celery_app.task(name="cleanup_expired_logs")`
- `server/app/core/celery_app.py` has `beat_schedule` configured for `cleanup_expired_logs`
</acceptance_criteria>
</task>
</tasks>
