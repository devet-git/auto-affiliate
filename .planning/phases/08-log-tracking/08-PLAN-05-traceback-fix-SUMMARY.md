---
phase: 08
plan: 05
status: complete
---

# Plan 05 - Fix Celery Failure Traceback Formatting

## What was built
Fixed `task_failure_handler` in `sys_worker/celery_signals.py` to produce human-readable traceback text instead of the raw object pointer string (`<traceback object at 0x...>`).

### Strategy (priority order):
1. **Celery `einfo`** — Celery passes an `ExceptionInfo` object in `kwargs["einfo"]` which has a pre-formatted, Celery-styled traceback string. Use `str(einfo)` when available.
2. **`traceback_module.format_tb()`** — If only the raw tb object is available, format it using Python's built-in `traceback.format_tb()`, then append the exception type/message.
3. **Fallback** — `str(exception)` as last resort.

Also renamed the stdlib `traceback` import to `traceback_module` to avoid shadowing by the `traceback` parameter in the signal handler signature.

## Self-Check: PASSED
- [x] `einfo` used when Celery provides it
- [x] `traceback_module.format_tb()` used for raw tb objects
- [x] Exception class name and message appended to stack trace
- [x] Import alias avoids name collision
