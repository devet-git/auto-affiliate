---
wave: 1
depends_on: []
files_modified:
  - server/app/domains/sys_worker/models.py
  - server/app/domains/sys_worker/celery_signals.py
  - server/app/core/celery_app.py
  - server/main.py
requirements:
  - LOG-01
autonomous: true
---

# Plan 01 - DB Models and Celery Signals

<objective>
Implement TaskLog and AppSetting schema. Wire up Celery signals to log every task execution automatically.
</objective>

<verification>
Automated tests should pass. Start backend and run a dummy Celery task, verify rows appear in TaskLog.
</verification>

<must_haves>
- TaskLog schema must include traceability properties (task_id, err, kwargs).
- Handlers must use synchronous DB sessions.
</must_haves>

<tasks>
<task id="08-01-01" description="Create TaskLog and AppSetting models">
<read_first>
- server/app/core/database.py
- server/main.py
</read_first>
<action>
1. In `server/app/domains/sys_worker/models.py` (create if missing), add `TaskLog` subclassing SQLModel with fields:
   - `id`: int pk
   - `task_id`: str (Celery UUID)
   - `task_name`: str
   - `status`: str
   - `result`: Column(JSON)
   - `error_traceback`: str
   - `kwargs`: Column(JSON)
   - `started_at`: datetime
   - `finished_at`: datetime
2. Also add `AppSetting` model:
   - `key`: str pk
   - `value`: str
3. Ensure these models are imported in `server/main.py` BEFORE `create_db_and_tables()` is called, so tables are created on startup.
</action>
<acceptance_criteria>
- `server/app/domains/sys_worker/models.py` contains `class TaskLog(SQLModel, table=True)`
- `server/main.py` contains `from app.domains.sys_worker.models import TaskLog`
</acceptance_criteria>
</task>

<task id="08-01-02" description="Add Celery signal hooks">
<read_first>
- server/app/domains/sys_worker/models.py
- server/app/core/celery_app.py
</read_first>
<action>
1. Create `server/app/domains/sys_worker/celery_signals.py`.
2. Implement synchronous signal handlers for Celery:
   - `@task_prerun.connect`: Get `engine` from `database.py`, open `Session(engine)`, create a `TaskLog` entry with `status="STARTED"`.
   - `@task_postrun.connect` or `@task_success.connect` and `@task_failure.connect`: Find existing `TaskLog` by `task_id`, update status to `COMPLETED` or `FAILED`, capture `traceback` (for fail) or `retval` (for success). Note: use `.dict()` or JSON serialization.
3. In `server/app/core/celery_app.py`, add `import app.domains.sys_worker.celery_signals` immediately after initializing `celery_app` to register the hooks.
</action>
<acceptance_criteria>
- `server/app/domains/sys_worker/celery_signals.py` defines `@task_prerun.connect` and uses `Session(engine)`
- `server/app/core/celery_app.py` has `import app.domains.sys_worker.celery_signals`
</acceptance_criteria>
</task>
</tasks>
