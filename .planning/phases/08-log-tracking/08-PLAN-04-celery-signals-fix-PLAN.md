---
wave: 4
depends_on: ["08-PLAN-01-database-signals.md"]
files_modified:
  - server/app/domains/sys_worker/celery_signals.py
requirements:
  - LOG-01
autonomous: true
---

# Plan 04 - Fix Celery Signal Task IDs

<objective>
Fix the Celery task success and task failure hooks to extract the task ID reliably from `sender.request.id`, ensuring database log updates succeed.
</objective>

<verification>
Execute `test_worker_task.apply(args=['hello'])` synchronously and verify that `TaskLog` instances reflect `SUCCESS` status in the DB automatically.
</verification>

<must_haves>
- Uses `sender.request.id` as the source of truth if `task_id` is empty in `kwargs`.
</must_haves>

<tasks>
<task id="08-04-01" description="Extract task ID correctly">
<read_first>
- server/app/domains/sys_worker/celery_signals.py
</read_first>
<action>
1. Edit `server/app/domains/sys_worker/celery_signals.py`.
2. In `task_success_handler`: Add `task_id = sender.request.id if getattr(sender, 'request', None) else kwargs.get("task_id")`. Ensure `where(TaskLog.task_id == task_id)` is invoked properly.
3. In `task_failure_handler`: Extract `task_id = sender.request.id if getattr(sender, 'request', None) else kwargs.get("task_id")`.
</action>
<acceptance_criteria>
- Both hooks properly read `task_id`. Let `task_prerun` as is.
</acceptance_criteria>
</task>
</tasks>
