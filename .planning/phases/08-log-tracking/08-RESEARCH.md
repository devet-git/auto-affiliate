# Phase 08: Log Tracking - Research

<objective>
Research how to implement Phase 8: Log Tracking
</objective>

## Domain Knowledge
- **Celery Signals**: Celery exposes signals (`task_prerun`, `task_postrun`, `task_success`, `task_failure`, `task_retry`) that can be hooked to capture the state of every task automatically, rather than modifying every individual task function.
- **Async vs Sync Hooks**: Celery signals are executed synchronouly in the worker process. The database interactions within the signal handlers must use a synchronous SQLModel/SQLAlchemy session (via `Session(engine)`) rather than an `AsyncSession`, as mixing async DB sessions into Celery synchronous signals causes thread-loop issues.
- **Data Table implementation**: The frontend uses `Shadcn UI`. To support advanced filtering (D-03), a data table mapping HTTP React Query state to backend API endpoints with query parameters (`status`, `task_name`, `date_start`) is required.

## Context Analysis & Decisions Path
From `08-CONTEXT.md`:
- **D-01 (Granularity - Log Everything):** 
  - Implementation: Hook `task_prerun` (insert row as `STARTED`).
  - Hook `task_success` (update row to `COMPLETED` and store result).
  - Hook `task_failure` (update row to `FAILED`, store `e.traceback`).
- **D-02 (Data Structure):** Create `TaskLog` model. Use `JSONType` or SQLModel's supported JSON fields for kwargs and result.
- **D-03 (Dashboard UI Filters):** 
  - Backend API: `GET /api/v1/logs?task_name=...&status=...&start_date=...`
  - SQLAlchemy `select().where(...)` for dynamic filters.
- **D-04/D-05 (Configurable Retention):** 
  - Because it needs to be *user-configurable* via the dashboard, using environment variables `.env` is insufficient. We need to store settings in the database.
  - Implement a simple `AppSetting` SQLModel table: `key` (e.g., `log_retention_days`), `value` (e.g., `"7"`).
  - Web UI: Add a small "Settings" panel or config gear in the Logs dashboard to edit this value.
  - Celery Beat: Run `cleanup_old_logs` daily, which queries `AppSetting`, calculates the threshold date, and performs a bulk `DELETE`.

## Implementation Path (What planner needs to know)
1. **Database Schema:** 
   - Add `server/app/domains/logs/models.py` (`TaskLog` table).
   - Add `server/app/domains/settings/models.py` (`AppSetting` table) OR just lump it under a system domains app.
2. **Celery Integrations:** 
   - Add `server/app/domains/logs/celery_signals.py` to register handlers.
   - Import signals in `server/app/core/celery_app.py` to ensure they are loaded at startup.
3. **API Endpoints:** 
   - Create `logs` router for fetching filtered logs. 
   - Create `settings` router for fetching/updating retention days.
4. **Scheduled Task:** 
   - Define `clean_expired_logs_task` in `server/app/domains/sys_worker/tasks.py`. Hook it up to celery beat schedule in `celery_app.py`.
5. **Frontend Application:** 
   - Implement `ExecutionLogs.tsx`. 
   - Add `<DataTable />` component using Shadcn conventions.
   - Add retention-days settings dialog.

## Validation Architecture
- **DB Injection**: Verify signal handlers correctly inject database sessions and persist the `TaskLog` row.
- **Error Tracking Test**: Intentionally throw an exception in a test Celery task and verify `error_traceback` is fully populated.
- **Cleanup Test**: Create a mock log record aged > 30 days, trigger the beat `clean_expired_logs_task`, and verify the database deletes it according to the configurable setting.

## RESEARCH COMPLETE
